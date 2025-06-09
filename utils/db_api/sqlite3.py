import sqlite3
import uuid


def generate_user_uuid():
    return str(uuid.uuid4())


class Database:
    def __init__(self, path_to_db="main.db"):
        self.connection = sqlite3.connect(path_to_db)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        self.connection.set_trace_callback(logger)  # logni yoqish
        self.cursor.execute(sql, parameters)
        data = None
        if commit:
            self.connection.commit()
        if fetchone:
            data = self.cursor.fetchone()
        if fetchall:
            data = self.cursor.fetchall()
        return data

    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
            user_id int NOT NULL,
            full_name varchar(255) NOT NULL,
            username varchar(255),
            PRIMARY KEY (user_id)
            );
"""
        self.execute(sql, commit=True)

    def create_uuid_to_user_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS UUIDToUser (
            uuid TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL UNIQUE
        );
        """
        self.execute(sql, commit=True)

    def create_table_status(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Status (
            active int,
            block int
            );
"""
        self.execute(sql, commit=True)

    def create_referrals_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_uuid TEXT NOT NULL,
            sender_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL
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
        sql = """
        INSERT OR IGNORE INTO Users(user_id, full_name, username)
        VALUES (?, ?, ?)
        """
        self.execute(sql, (user_id, full_name, username), commit=True)

    def select_all_users(self):
        sql = """
        SELECT * FROM Users
        """
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return self.execute(sql, parameters=parameters, fetchone=True)

    def get_user_id_by_uuid(self, uuid_str: str):
        sql = "SELECT user_id FROM UUIDToUser WHERE uuid = ?"
        result = self.cursor.execute(sql, (uuid_str,)).fetchone()
        return result['user_id'] if result else None

    def insert_uuid_for_user(self, user_id: int, uuid_str: str):
        sql = "INSERT INTO UUIDToUser (user_id, uuid) VALUES (?, ?)"
        try:
            self.cursor.execute(sql, (user_id, uuid_str))
            self.connection.commit()
            print(f"[UUID] {uuid_str} for user {user_id} inserted successfully.")
        except sqlite3.IntegrityError as e:
            print(f"[DB ERROR] Insert failed: {e}")

    def insert_referral(self, referrer_uuid: str, sender_id: int):
        sql = """
        INSERT INTO Referrals (referrer_uuid, sender_id, timestamp)
        VALUES (?, ?, datetime('now'))
        """
        self.execute(sql, parameters=(referrer_uuid, sender_id), commit=True)

    def get_user_uuid(self, user_id: int):
        sql = "SELECT uuid FROM UUIDToUser WHERE user_id = ?"
        result = self.cursor.execute(sql, (user_id,)).fetchone()
        return result[0] if result else None

    def get_referral_senders(self, referrer_uuid: str):
        sql = "SELECT sender_id FROM Referrals WHERE referrer_uuid = ?"
        result = self.cursor.execute(sql, (referrer_uuid,)).fetchall()
        return [row[0] for row in result] if result else []

    def count_referral_senders(self, referrer_uuid: str):
        sql = "SELECT COUNT(*) FROM Referrals WHERE referrer_uuid = ?"
        result = self.cursor.execute(sql, (referrer_uuid,)).fetchone()
        return result[0] if result else 0

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
