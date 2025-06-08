import sqlite3
import uuid


def generate_user_uuid():
    return str(uuid.uuid4())


class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
            user_id int NOT NULL,
            full_name varchar(255) NOT NULL,
            username varchar(255),
            referred_by INTEGER,
            uuid TEXT UNIQUE,
            PRIMARY KEY (user_id)
            );
"""
        self.execute(sql, commit=True)

    def create_table_active_replies(self):
        sql = """
        CREATE TABLE IF NOT EXISTS ActiveReplies (
            user_id INTEGER PRIMARY KEY,
            replying_to INTEGER
        );
        """
        self.execute(sql, commit=True)

    def create_replies_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Replies (
            sender_id INTEGER PRIMARY KEY,
            receiver_id INTEGER NOT NULL
        );
        """
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()

    def create_uuid_to_user_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS UUIDToUser (
            uuid TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL
        );
        """
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()

    def add_reply(self, sender_id, receiver_id):
        sql = "INSERT OR REPLACE INTO Replies (sender_id, receiver_id) VALUES (?, ?)"
        cursor = self.connection.cursor()
        cursor.execute(sql, (sender_id, receiver_id))
        self.connection.commit()

    def set_replying_to(self, sender_id: int, receiver_id: int):
        sql = "INSERT OR REPLACE INTO Replies (sender_id, receiver_id) VALUES (?, ?)"
        cursor = self.connection.cursor()
        cursor.execute(sql, (sender_id, receiver_id))
        self.connection.commit()

    def get_replying_to(self, sender_id):
        sql = "SELECT receiver_id FROM Replies WHERE sender_id = ?"
        cursor = self.connection.cursor()
        result = cursor.execute(sql, (sender_id,)).fetchone()
        return result[0] if result else None

    def delete_replying(self, sender_id: int):
        sql = "DELETE FROM Replies WHERE sender_id = ?"
        cursor = self.connection.cursor()
        cursor.execute(sql, (sender_id,))
        self.connection.commit()

    def create_table_status(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Status (
            active int,
            block int
            );
"""
        self.execute(sql, commit=True)


    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, user_id, full_name, username=None, referred_by=None):
        user_uuid = generate_user_uuid()  # UUID yaratamiz
        sql = """
        INSERT OR IGNORE INTO Users(user_id, full_name, username, referred_by, uuid)
        VALUES (?, ?, ?, ?, ?)
        """
        self.execute(sql, (user_id, full_name, username, referred_by, user_uuid), commit=True)
        return user_uuid

    def select_all_users(self):
        sql = """
        SELECT * FROM Users
        """
        return self.execute(sql, fetchall=True)

    def get_referrer(self, user_id: int):
        sql = "SELECT referred_by FROM Users WHERE user_id = ?"
        result = self.execute(sql, parameters=(user_id,), fetchone=True)
        return result[0] if result else None

    def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return self.execute(sql, parameters=parameters, fetchone=True)

    def get_user_uuid(self, user_id):
        sql = "SELECT uuid FROM users WHERE user_id = ?"
        result = self.cursor.execute(sql, (user_id,)).fetchone()
        return result[0] if result else None

    def get_user_id_by_uuid(self, uuid_str):
        sql = "SELECT user_id FROM Users WHERE uuid = ?"
        result = self.execute(sql, (uuid_str,), fetchone=True)
        return result[0] if result else None

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)

    def delete_users(self):
        self.execute("DELETE FROM Users WHERE TRUE", commit=True)

    def add_status(self, active: int = 0, block: int = 0):
        sql = """
        INSERT INTO Status(active, block) VALUES(?, ?)
        """
        self.execute(sql, parameters=(active, block), commit=True)

    def select_block(self):
        return self.execute(f"SELECT block FROM Status", fetchone=True)

    def select_active(self):
        return self.execute(f"SELECT active FROM Status", fetchone=True)

    def update_block(self, block):
        sql = f"""
        UPDATE Status SET block=?
        """
        return self.execute(sql, parameters=(block,), commit=True)

    def update_active(self, active):
        sql = f"""
        UPDATE Status SET active=?
        """
        return self.execute(sql, parameters=(active,), commit=True)

def logger(statement):
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")