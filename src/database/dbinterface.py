import sys
import logging
import psycopg2


class DBInterface():
    def _connect(self):
        try:
            self._conn = psycopg2.connect(
                database=self._db_name,
                user=self._db_user,
                password=self._db_password,
                host=self._db_host,
                port=self._db_port
            )
        except psycopg2.Error as err:
            self._logger.critical("Can not connect to postgres.", exc_info=err)
            sys.exit(1)
        self._cur = self._conn.cursor()
        self._logger.info("Database connection established.")

    def _check_connection(self):
        if hasattr(self, "_conn"):
            i = self._conn.closed
        else:
            i = -1
        if i != 0:
            self._connect()
        return i

    def execute(self, *args, **kwargs):
        self._check_connection()
        try:
            self._cur.execute(*args, **kwargs)
            return True
        except psycopg2.Error as err:
            self._logger.error("Could not execute SQL-Query.", exc_info=err)
            self.rollback()
            return False

    def fetchall(self):
        self._check_connection()
        try:
            return self._cur.fetchall()
        except psycopg2.Error as err:
            self.rollback()
            self._logger.error("Could not fetch.", exc_info=err)
            return None

    def rollback(self):
        if self._check_connection() != 0:
            self._logger.error("Database connection unexpectetly closed.")
        self._conn.rollback()

    def commit(self):
        if self._check_connection() != 0:
            self._logger.error("Database connection unexpectetly closed. Data may be lost.")
            self.rollback()
            return False
        self._conn.commit()
        return True

    def close(self):
        if hasattr(self, "_conn") and self._conn.closed == 0:
            self._conn.close()

    def __init__(self, cfg):
        self._logger      = logging.getLogger('sqlbot.dbinterface')
        self._db_name     = cfg.db_name
        self._db_user     = cfg.db_user
        self._db_password = cfg.db_password
        self._db_host     = cfg.db_host
        self._db_port     = cfg.db_port
        self._connect()

    def __del__(self):
        self.close()
        self._logger.info("Database connection closed.")
