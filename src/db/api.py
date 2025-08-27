import contextlib
import sqlite3
from queue import Queue
from sqlite3 import Connection
from typing import List

import pandas as pd
import pandas.io.sql as sqlio


class ConnectionPool:
    def __init__(self, db_name: str, pool_size: int = 5):
        self.db_name = db_name
        self.pool_size = pool_size
        self._pool = Queue(maxsize=pool_size)

        # Initialize pool with connections
        for _ in range(pool_size):
            conn = sqlite3.connect(db_name, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            self._pool.put(conn)

    @contextlib.contextmanager
    def get_connection(self):
        conn = self._pool.get()
        try:
            yield conn
        finally:
            self._pool.put(conn)

    def close_all(self):
        while not self._pool.empty():
            conn = self._pool.get()
            conn.close()


class BaseDb(object):
    def __init__(self, db_name):
        self.db_name = db_name
        self._pool = ConnectionPool(db_name)

    def connect(self) -> Connection:
        conn = sqlite3.connect(self.db_name, check_same_thread=False)
        # Optimize SQLite settings
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        return conn

    def execute_sql(
        self, sql, parameters=None, many=False, batch_size: int = 1000
    ) -> None:
        if parameters is None:
            parameters = []

        with self._pool.get_connection() as conn:
            cur = conn.cursor()
            try:
                conn.execute("BEGIN TRANSACTION")
                if not many:
                    cur.execute(sql, parameters)
                else:
                    # Process in batches for better performance
                    if isinstance(parameters, list) and len(parameters) > batch_size:
                        for i in range(0, len(parameters), batch_size):
                            batch = parameters[i : i + batch_size]
                            cur.executemany(sql, batch)
                    else:
                        cur.executemany(sql, parameters)
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cur.close()

    def query_df(self, sql: str, parameters=None) -> pd.DataFrame:
        with self._pool.get_connection() as conn:
            return sqlio.read_sql_query(sql, conn, params=parameters)

    def query_json(self, sql, parameters=None) -> str:
        df = self.query_df(sql, parameters)
        return df.to_json(orient="records")

    def query(self, sql, parameters=None):
        if parameters is None:
            parameters = []
        with self._pool.get_connection() as conn:
            cur = conn.cursor()
            result = list(cur.execute(sql, parameters))
            cur.close()
            return result

    @contextlib.contextmanager
    def query_iterator(self, sql, parameters=None):
        if parameters is None:
            parameters = []
        with self._pool.get_connection() as conn:
            cur = conn.cursor()
            try:
                yield cur.execute(sql, parameters)
            finally:
                cur.close()

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

    def ddl_script(self, filename: str) -> None:
        with open(filename, "r") as f:
            sql = f.read()
            self.execute_sql(sql)

    def insert_list(self, filename: str, values: List, batch_size: int = 1000) -> None:
        with self._pool.get_connection() as conn:
            cur = conn.cursor()
            try:
                with open(filename, "r") as f:
                    sql = f.read()

                conn.execute("BEGIN TRANSACTION")

                # Process in batches for better performance
                if len(values) > batch_size:
                    for i in range(0, len(values), batch_size):
                        batch = values[i : i + batch_size]
                        cur.executemany(sql, batch)
                else:
                    cur.executemany(sql, values)

                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cur.close()
