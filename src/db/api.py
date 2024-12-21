import sqlite3
import contextlib
import numpy as np
import pandas as pd
import pandas.io.sql as sqlio

from sqlite3 import Connection


class BaseDb(object):
    def __init__(self, db_name):
        self.db_name = db_name

    def connect(self) -> Connection:
        return sqlite3.connect(self.db_name, check_same_thread=True)

    def execute_sql(self, sql, parameters=None, many=False) -> None:
        if parameters is None:
            parameters = []
        conn = self.connect()
        cur = conn.cursor()
        if not many:
            cur.execute(sql, parameters)
        else:
            cur.executemany(sql, parameters)
        conn.commit()
        cur.close()
        conn.close()

    def query_df(
        self, sql: str, parameters=None, convert_none: bool = True
    ) -> pd.DataFrame:
        conn = self.connect()
        df = sqlio.read_sql_query(sql, conn, params=parameters)
        if convert_none:
            df.fillna(value=np.nan, inplace=True)
        conn.close()
        return df

    def query(self, sql, parameters=None):
        if parameters is None:
            parameters = []
        conn = self.connect()
        cur = conn.cursor()
        result = list(cur.execute(sql, parameters))
        cur.close()
        conn.close()
        return result

    @contextlib.contextmanager
    def query_iterator(self, sql, parameters=None):
        if parameters is None:
            parameters = []
        conn = self.connect()
        cur = conn.cursor()
        yield cur.execute(sql, parameters)
        cur.close()
        conn.close()

    def query_scalar(self, sql, parameters=None):
        if parameters is None:
            parameters = []
        res = self.query(sql, parameters)
        return res[0][0]

    def table_has_column(self, table: str, column: str) -> str | None:
        sql = "PRAGMA table_info ('{}')".format(table)
        lst = self.query(sql)
        for col in lst:
            if col[1] == column:
                return col
        return None

    def table_exists(self, table_name: str) -> bool:
        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = set([table[0] for table in self.query(sql)])
        return table_name in tables
