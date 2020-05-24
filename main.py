from app.models.report import Api, CompeleteInfo, PositiveTests, Report
from app.models.databases import SqlDatabase
from app.utils.config_setup import config_init
#import pytest


def main():

    # init config
    cfg = config_init()

    # report complete
    report_complete = CompeleteInfo(cfg)
    report_complete.show_spark_df()
    report_complete.show_pandas_df()


    # report positive tested
    report_positive_tests = PositiveTests(cfg)
    report_positive_tests.show_spark_df()
    report_positive_tests.show_pandas_df()
    report_positive_tests.show_spark_final_df()
    report_positive_tests.show_report_positive_tests()

    # show report
    report = Report(cfg)
    report.show_report_positive_tests()


if __name__ == '__main__':
    main()