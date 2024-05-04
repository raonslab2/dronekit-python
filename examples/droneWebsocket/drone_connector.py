import pymysql as db
import logging

class MySQLConnector:
    def __init__(self, host, user, password, database, charset='utf8'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.conn = None

    def connect(self):
        try:
            self.conn = db.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset,
                local_infile=1
            )
            return self.conn
        except Exception as e:
            logging.error(f"MySQL connection error: {e}")

    def close(self):
        try:
            if self.conn:
                self.conn.close()
        except Exception as e:
            logging.error(f"Error while closing MySQL connection: {e}")

    def is_connected(self):
        try:
            return self.conn.ping(reconnect=True)
        except Exception as e:
            logging.error(f"Error while pinging MySQL server: {e}")
            return False
