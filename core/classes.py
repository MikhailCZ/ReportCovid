import requests
from requests.exceptions import HTTPError
from abc import ABC, abstractmethod
import sqlite3
from core.setup_config import config_init
from datetime import date
import json

cfg = config_init()

class ApiData:

    def __init__(self, url):
        self._url = url

    def __str__(self):
        return str('The class gets a json string from Api')

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        if not isinstance(value, str):
            raise TypeError('Url must be string')
        self._url = value

    @property
    def get_content_from_api(self) -> json:
        response = requests.get(self.url)
        if response.status_code == 200:
            #logger.info(f'OK - request success status: {response.status_code}')
            print(f'OK - request success status: {response.status_code}')
        else:
            #logger.error(f'NOK - request was not succesfull status: {response.status_code}. Description: {response.json()}')
            raise HTTPError
        return response.json()


class Parser:

    def __init__(self, content):
        self.content = content

    def __str__(self):
        return str('The class parse is defined to parse json string and get atributes')

    def get_fromBabisNewspapers(self) -> tuple:
        fromBabisNewspapers = self.content['fromBabisNewspapers']
        fromBabisNewspapers = tuple(fromBabisNewspapers.values())
        return fromBabisNewspapers

    def get_totalPositiveTests(self) -> list:
        totalPositiveTests = self.content['totalPositiveTests']
        values = [v['value'] for v in totalPositiveTests]
        date = [d['date'][:10] for d in totalPositiveTests]
        totalPositiveTests = list(zip(date, values))
        return totalPositiveTests

    def get_infectedByRegion(self) -> tuple:
        infectedByRegion = self.content['infectedByRegion']
        values = [v['value'] for v in infectedByRegion]
        values.insert(0, str(date.today()))
        values = tuple(values)
        return values



class DbConnection(ABC):

    def __init__(self, connection):
        self.connection = connection

    def __str__(self):
        return str('Abstract class for creation of various databases')

    @abstractmethod
    def insert_fromBabisNewspapers(self, data):
        pass

    @abstractmethod
    def insert_totalPositiveTests(self, data):
        pass

    @abstractmethod
    def insert_infectedByRegion(self, data):
        pass


class DbConnectionSql(DbConnection):

    def __init__(self, db_sql):
        connection = sqlite3.connect(db_sql)
        super().__init__(connection)

    def __str__(self):
        return str(f'Class for SQL databse')

    def insert_fromBabisNewspapers(self, data):
        cursor = self.connection.cursor()
        try:
            cursor.execute(cfg['SQL_QUERIES']['DML']['INSERT_BABIS'].format(date.today(), data[0], data[1], data[2], data[3]))
        except sqlite3.Error as ex:
            raise Exception (f'{ex}')
        else:
            self.connection.commit()


    def insert_totalPositiveTests(self, data):
        cursor = self.connection.cursor()
        try:
            cursor.executemany(cfg['SQL_QUERIES']['DML']['INSERT_POSITIVE_TESTS'], data)
        except sqlite3.Error as ex:
            raise Exception(f'{ex}')
        else:
            self.connection.commit()


    def insert_infectedByRegion(self, data):
        cursor = self.connection.cursor()
        try:
            cursor.executemany(cfg['SQL_QUERIES']['DML']['INSERT_REGION'], (data,))
        except sqlite3.Error as ex:
            raise Exception(f'{ex}')
        else:
            self.connection.commit()



# class DBConnection:
#     instance = None
#
#     def __new__(cls, *args, **kwargs):
#         if cls.instance is None:
#             cls.instance = super().__new__(DBConnection)
#             return cls.instance
#         return cls.instance
#
#     def __init__(self, db_name='you-db-name'):
#         self.name = db_name
#         # connect takes url, dbname, user-id, password
#         self.conn = self.connect(db_name)
#         self.cursor = self.conn.cursor()
#
#     def connect(self):
#         try:
#             return sqlite3.connect(self.name)
#         except sqlite3.Error as e:
#             pass
#
#     def __del__(self):
#         self.cursor.close()
#         self.conn.close()


api = ApiData(cfg['VARIABLES']['URL'])
content_json = api.get_content_from_api
parse = Parser(content_json)

# get data
data_fromBabisNewspapers = parse.get_fromBabisNewspapers()
data_totalPositiveTests = parse.get_totalPositiveTests()
data_infectedByRegion = parse.get_infectedByRegion()

# insert
db = DatabaseSQL(cfg['VARIABLES']['DB_SQL'])
# db.insert_fromBabisNewspapers(data_fromBabisNewspapers)
# db.insert_totalPositiveTests(parse.get_totalPositiveTests())
# db.insert_infectedByRegion(data_infectedByRegion)

import matplotlib.pyplot as plt
import pandas as pd
df = pd.read_sql('SELECT data, totalInfected FROM fromBabisNewspapers', db.connection)
print(df)
df.plot(kind='bar', x='data', y='totalInfected')
plt.show()











