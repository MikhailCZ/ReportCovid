""" SQL -SQLite and NoSQL - MongoDb """

from abc import ABC, abstractmethod
import sqlite3
from datetime import date
from app.utils.config_setup import config_init

class Database(ABC):

    @abstractmethod
    def create_connection(self):
        pass

    @abstractmethod
    def insert_into_babis_newspaper(self, input_data):
        pass

    @abstractmethod
    def select_from_babis_newspaper(self):
        pass


class SqlDatabase(Database):

    def __init__(self):
        self.cfg = config_init()
        self._sql_db = self.cfg['VARIABLES']['DB_SQL']
        self._connection = self.create_connection()
        self.from_babis = 'fromBabisNewspapers'
        self.insert_babis_qry = self.cfg['SQL_QUERIES']['DML']['INSERT_BABIS']
        self.input_json = None

    @property
    def sql_db_name(self):
        return self._sql_db

    def create_connection(self):
        #conn = None
        try:
            conn = sqlite3.connect(self._sql_db)
        except sqlite3.Error as ex:
            raise ex
        else:
            return conn

    def _get_data_from_babis(self, input_json) -> list:
        from_babis_json = input_json[self.from_babis]
        print(from_babis_json)
        from_babis = list(from_babis_json.values())
        return from_babis

    def insert_into_babis_newspaper(self, input_json):
        cursor = self._connection.cursor()
        lst_babis = self._get_data_from_babis(input_json)
        try:
            cursor.execute(self.insert_babis_qry.format(date.today(), lst_babis[0], lst_babis[1], lst_babis[2], lst_babis[3]))
        except sqlite3.Error as ex:
            raise ex
        else:
            self._connection.commit()
            print('Succesfully inserted')
        finally:
            if self._connection:
                self._connection.close()

    def select_from_babis_newspaper(self):
        cursor = self._connection.cursor()
        qry = """ SELECT * FROM fromBabisNewspapers"""
        try:
            cursor.execute(qry)
            data = cursor.fetchall()
        except Exception as ex:
            raise ex
        else:
            return data

