import mysql.connector
from mysql.connector import Error
import threading

class DBManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(DBManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, host="localhost", user="root", password="", database="student_db"):
        if self._initialized:
            return
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database
        }
        self.db_lock = threading.Lock()
        self._initialized = True

    def get_connection(self):
        return mysql.connector.connect(**self.config)

    def execute_query(self, query, params=None):
        with self.db_lock:
            conn = None
            cursor = None
            result = None
            try:
                conn = self.get_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                conn.commit()
            except Error as e:
                print(f"Database Error: {e}")
                if conn:
                    conn.rollback()
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
            return result

    def execute_non_query(self, query, params=None):
        with self.db_lock:
            conn = None
            cursor = None
            success = False
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                conn.commit()
                success = True
            except Error as e:
                print(f"Database Error: {e}")
                if conn:
                    conn.rollback()
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
            return success

    def execute_transaction(self, operations):
        with self.db_lock:
            conn = None
            cursor = None
            success = False
            try:
                conn = self.get_connection()
                conn.autocommit = False
                cursor = conn.cursor()
                for query, params in operations:
                    cursor.execute(query, params or ())
                conn.commit()
                success = True
            except Error as e:
                print(f"Transaction Error: {e}")
                if conn:
                    conn.rollback()
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
            return success
