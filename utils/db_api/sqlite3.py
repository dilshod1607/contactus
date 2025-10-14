import sqlite3


class Database:
    def __init__(self, path_to_db="main.db"):
        # SQLite obyektini boshqa threadlarda ishlatishga ruxsat
        self.connection = sqlite3.connect(path_to_db, check_same_thread=False)
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


    def create_admins_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL UNIQUE
        );
        """
        self.execute(sql, commit=True)

        # Agar hali super admin yo‘q bo‘lsa, avtomatik qo‘shamiz (birinchi qatorda)
        sql_insert = """
        INSERT OR IGNORE INTO Admins (id, admin_id)
        VALUES (1, 5391341271);
        """
        self.execute(sql_insert, commit=True)

    def select_super(self):
        row = self.execute("SELECT admin_id FROM Admins WHERE id = 1", fetchone=True)
        if row:
            return row[0]
        return None

    def add_admin(self, admin_id: int):
        sql = "INSERT OR IGNORE INTO Admins (admin_id) VALUES (?);"
        self.execute(sql, parameters=(admin_id,), commit=True)

    def select_all_admins(self):
        sql = "SELECT admin_id FROM Admins;"
        rows = self.execute(sql, fetchall=True)
        return [row[0] for row in rows] if rows else []

    def delete_admin(self, admin_id: int) -> bool:
        super_admin = self.select_super()
        if admin_id == super_admin:  # super adminni o‘chirmaymiz
            return False
        query = "DELETE FROM Admins WHERE admin_id=?"
        self.execute(query, (admin_id,), commit=True)
        return True

    def create_requests_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'new',  -- status: new, viewed, closed
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.execute(sql, commit=True)

    def add_request(self, fio: str, phone: str, email: str, message: str, status="new"):
        sql = """
        INSERT INTO Requests (fio, phone, email, message, status)
        VALUES (?, ?, ?, ?, ?)
        """
        # execute ishlaydi va self.cursor reference mavjud bo'lsa lastrowid ni qaytaramiz
        self.execute(sql, parameters=(fio, phone, email, message, status), commit=True)
        return self.cursor.lastrowid

    def get_all_requests(self, status=None):
        sql = "SELECT * FROM Requests"
        if status:
            sql += " WHERE status=?"
            return self.execute(sql, parameters=(status,), fetchall=True)
        return self.execute(sql, fetchall=True)

    # Barcha murojaatlarni olish, status bo‘yicha filtrlash mumkin
    def select_request_by_id(self, req_id: int):
        sql = "SELECT id, fio, phone, email, message, status, created_at FROM Requests WHERE id=?"
        row = self.execute(sql, parameters=(req_id,), fetchone=True)
        if row:
            return {
                "id": row[0],
                "fio": row[1],
                "phone": row[2],
                "email": row[3],
                "message": row[4],
                "status": row[5],
                "created_at": row[6]
            }
        return None

    # Database klassida
    def select_all_requests(self, include_closed=False):
        sql = "SELECT id, fio, phone, email, message, status, created_at FROM Requests"
        if not include_closed:
            sql += " WHERE status != 'closed'"
        rows = self.execute(sql, fetchall=True)
        return [
            {
                "id": row[0],
                "fio": row[1],
                "phone": row[2],
                "email": row[3],
                "message": row[4],
                "status": row[5],
                "created_at": row[6]
            } for row in rows
        ] if rows else []

    # Murojaat statusini o‘zgartirish
    def update_request_status(self, req_id, status):
        sql = "UPDATE Requests SET status=? WHERE id=?"
        self.execute(sql, parameters=(status, req_id), commit=True)

    def update_request_status(self, request_id: int, status: str):
        sql = "UPDATE Requests SET status=? WHERE id=?"
        self.execute(sql, parameters=(status, request_id), commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

def logger(statement):
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")
