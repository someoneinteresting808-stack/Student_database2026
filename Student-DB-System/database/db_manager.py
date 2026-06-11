import pymysql
from pymysql import Error
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

    def __init__(self, host=None, user=None, password=None, database=None):
        if self._initialized:
            return
        db_config = self.load_config()
        self.config = {
            "host": host or db_config.get("host", "localhost"),
            "user": user or db_config.get("user", "root"),
            "password": password if password is not None else db_config.get("password", ""),
            "database": database or db_config.get("database", "student_db"),
            "port": int(db_config.get("port", 3306))
        }
        self.db_lock = threading.Lock()
        self._initialized = True

    @classmethod
    def get_config_path(cls):
        import os
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "db_config.json")

    @classmethod
    def load_config(cls):
        import os
        import json
        path = cls.get_config_path()
        defaults = {
            "host": "localhost",
            "user": "root",
            "password": "",
            "database": "student_db",
            "port": 3306
        }
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    for k, v in defaults.items():
                        if k not in config:
                            config[k] = v
                    return config
            except Exception as e:
                print(f"Error reading config: {e}")
                return defaults
        else:
            cls.save_config(defaults)
            return defaults

    @classmethod
    def save_config(cls, config):
        import os
        import json
        path = cls.get_config_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def update_config(self, host, user, password, database):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": 3306
        }
        self.save_config(self.config)

    def get_connection(self):
        # We reuse a single connection to avoid opening a new TCP handshake
        # on every single query (which causes massive lag over the internet).
        config_with_timeout = self.config.copy()
        config_with_timeout["connect_timeout"] = 3
        
        if hasattr(self, "_conn") and self._conn and self._conn.open:
            try:
                self._conn.ping(reconnect=True)
                return self._conn
            except Exception:
                pass
        
        self._conn = pymysql.connect(**config_with_timeout)
        return self._conn

    def check_and_setup(self):
        """
        Attempts to connect and initialize the database.
        Returns (True, None) if successful.
        Returns (False, err) if connection fails.
        """
        try:
            conn = None
            try:
                conn = self.get_connection()
                # Connected successfully! Check if tables exist
                cursor = conn.cursor()
                cursor.execute("SHOW TABLES")
                tables = [t[0].lower() for t in cursor.fetchall()]
                required_tables = ["users", "students", "grades", "departments", "subjects"]
                all_exist = all(rt in tables for rt in required_tables)
                
                if all_exist:
                    # Verify subjects table has dept_name column
                    cursor.execute("SHOW COLUMNS FROM subjects")
                    columns = [col[0].lower() for col in cursor.fetchall()]
                    if "dept_name" not in columns:
                        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                        cursor.execute("DROP TABLE IF EXISTS subjects")
                        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                        all_exist = False
                
                cursor.close()
                if not all_exist:
                    # Initialize database schema
                    self.initialize_database()
                return True, None
            except pymysql.Error as e:
                # If database does not exist, let's try to create it
                if e.args[0] == 1049: # ER_BAD_DB_ERROR
                    self.initialize_database()
                    return True, None
                else:
                    raise e
        except Exception as e:
            return False, str(e)

    def initialize_database(self):
        """Runs the schema.sql script to initialize databases and tables."""
        import os
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"schema.sql not found at {schema_path}")

        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        # Connect to database directly
        conn_has_db = True
        try:
            conn = self.get_connection()
        except pymysql.Error as e:
            # If database does not exist (e.g. locally), connect without database
            if e.args[0] == 1049:
                config_no_db = self.config.copy()
                if "database" in config_no_db:
                    del config_no_db["database"]
                config_no_db["connect_timeout"] = 3
                conn = pymysql.connect(**config_no_db)
                conn_has_db = False
            else:
                raise e

        cursor = conn.cursor()
        
        # We need to run each statement in schema.sql.
        statements = schema_sql.split(";")
        for statement in statements:
            statement = statement.strip()
            if not statement:
                continue
            # If we already connected to a specific database, skip CREATE DATABASE/USE statements
            if conn_has_db:
                stmt_upper = statement.upper()
                if stmt_upper.startswith("CREATE DATABASE") or stmt_upper.startswith("USE "):
                    continue
            cursor.execute(statement)
        conn.commit()
        cursor.close()
        # If we connected to config_no_db, we should close it as it was a temp connection
        if not conn_has_db:
            conn.close()

    def execute_query(self, query, params=None):
        import pymysql.cursors
        with self.db_lock:
            conn = None
            cursor = None
            result = None
            try:
                conn = self.get_connection()
                cursor = conn.cursor(pymysql.cursors.DictCursor)
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
            return success

    def execute_transaction(self, operations):
        with self.db_lock:
            conn = None
            cursor = None
            success = False
            try:
                conn = self.get_connection()
                conn.autocommit(False)
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
            return success
