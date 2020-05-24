""" Classes for working with API request and single parts of API json  """

import requests
from app.utils.config_setup import config_init
from app.utils.validators import validate_response, validate_json
import pandas as pd
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
import pyspark
from pyspark.sql import SparkSession
import json
from pyspark.sql.window import Window
import pyspark.sql.functions as func


cfg = config_init()


class Api:
    """ Working with APIs """

    def __init__(self):
        self._url = cfg['VARIABLES']['URL']
        self._response = self._send_request()
        self.json = self.get_json()

    @property
    def url(self):
        return self._url

    def _send_request(self):
        """ send request and get row response """
        response = requests.get(self.url)
        validate_response(response)
        return response

    def get_json(self):
        """ convert response to json """
        json_response = self._response.json()
        return json_response


class ReportSpark(Api):
    """ Spark things """

    def __init__(self):
        super().__init__()
        self.spark = self._create_spark_session()
        self.sc = self._create_spark_context()

    def _create_spark_session(self):
        spark = (
            SparkSession
                .builder
                .appName("SparkReportCovid19")
                .master("local[1]")
                .getOrCreate()
        )
        return spark

    def _create_spark_context(self):
        sc = (
            pyspark.SparkContext
                .getOrCreate()
        )
        return sc


class CompeleteInfo(ReportSpark):
    """ Represents complete info about Covid-19 about certain day"""

    def __init__(self, cfg):
        ReportSpark.__init__(self)
        self.args = cfg['VARIABLES']['COMPLETE_INFO']
        self.spark_df_complete_info = self._create_spark_df()
        self.pandas_df_complete_info = self._convert_to_pandas_df()

    def _create_spark_df(self):
        d = {k: v for (k, v) in self.json.items() if k in self.args}
        json_string_for_rdd = json.dumps(d)
        RDD = self.sc.parallelize([json_string_for_rdd])
        df_spark = self.spark.read.json(RDD)
        return df_spark

    def _convert_to_pandas_df(self):
        df_pandas = self._create_spark_df().toPandas()
        return df_pandas

    def show_spark_df(self):
        return self.spark_df_complete_info.show()

    def show_pandas_df(self):
        return print(self.pandas_df_complete_info)


class PositiveTests(ReportSpark):
    """ Positive tested time series """

    def __init__(self, cfg):
        super().__init__()
        self.args = cfg['VARIABLES']['POSITIVE_TESTED']
        self.spark_df_positive_tests = self._create_spark_df()
        self.spark_df_final_positive_tests = self._create_spark_df_final()
        self.pandas_df_positive_tests = self._convert_to_pandas_df()

    def _create_spark_df(self):
        d = {k: v for (k, v) in self.json.items() if k in self.args}[self.args]
        rdd = self.sc.parallelize([d])
        df_spark_without_substring = self.spark.read.json(rdd)
        df_spark = df_spark_without_substring.select(df_spark_without_substring.date.substr(1, 10).alias('date'), df_spark_without_substring.value)
        return df_spark

    def _create_spark_df_final(self):
        """ calculate increments in percentage """

        dfu = self.spark_df_positive_tests.withColumn('user', func.lit('user_test'))
        df_spark_prev_day_value = dfu.withColumn('prev_date_value', func.lag(dfu['value']).over(Window.orderBy('user')))
        df_spark_changes = df_spark_prev_day_value.withColumn\
                                (
                                    'daily_infected',
                                    (df_spark_prev_day_value['value'] - df_spark_prev_day_value['prev_date_value'])/df_spark_prev_day_value['value']
                                )

        df_spark_result = df_spark_changes.select(df_spark_changes['date'],
                                    df_spark_changes['value'],
                                    func.round(df_spark_changes['daily_infected']*100, 2).alias('changes')
                                    )\
                                    .orderBy(df_spark_prev_day_value['date'])
        return df_spark_result

    def _convert_to_pandas_df(self):
        df_pandas = self._create_spark_df_final().toPandas()
        return df_pandas

    def show_spark_df(self):
        return self.spark_df_positive_tests.show()

    def show_pandas_df(self):
        return print(self.pandas_df_positive_tests)

    def show_spark_final_df(self):
        df_spark_result = self._create_spark_df_final()
        return df_spark_result.show()

    def show_report_positive_tests(self):
        self.pandas_df_positive_tests.plot(
            x='date',
            y='value',
            kind='scatter'
        )
        plt.show()



class Report(CompeleteInfo, PositiveTests):
    """ Reports """

    def __init__(self, cfg):
        CompeleteInfo.__init__(self, cfg)
        PositiveTests.__init__(self, cfg)

    def show_report_complete_info(self):
        pass

    def show_report_positive_tests(self):
        self.pandas_df_positive_tests.plot(
            x='date',
            y='value',
            kind='scatter'
        )
        plt.show()




def pandas_report():
    api = Api()
    covid_json = api.get_json()
    df = pd.DataFrame(columns=['value', 'date'])
    # insert into pandas df row by row
    for i, items in enumerate(covid_json['totalPositiveTests']):
        value = items['value']
        date = items['date'][:10]
        set_insert = (value, date)
        df.loc[i] = set_insert

    df.plot(x ='date', y='value', kind='scatter')
    plt.show()

