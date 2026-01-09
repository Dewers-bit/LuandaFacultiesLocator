import sqlite3
import os

class Database:
    def __init__(self, db_file="faculties.db"):
        self.db_file = db_file
        self.conn = None
        self._create_tables()

    def get_connection(self):
        """Creates a database connection."""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """Creates tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Users Table with Email
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Institutions Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS institutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL, -- University, Faculty, Institute
                    latitude REAL,
                    longitude REAL,
                    details TEXT,
                    website TEXT,
                    ranking TEXT,
                    courses TEXT
                )
            ''')

            # Login Logs Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS login_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            
            conn.commit()
        except Exception as e:
            print(f"Error creating tables: {e}")
        finally:
            conn.close()

    def query(self, query, params=(), one=False):
        """Executes a SELECT query."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor = conn.execute(query, params)
            rv = cursor.fetchall()
            return (rv[0] if rv else None) if one else rv
        finally:
            conn.close()

    def execute(self, query, params=()):
        """Executes an INSERT, UPDATE, DELETE query."""
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
