import mysql.connector
from PyQt6.QtWidgets import QMessageBox
import sys
from mysql.connector.connection import MySQLConnection

# Класс подключения к БД
class Database:
    def __init__(self):
        try:
            self.conn = MySQLConnection(
                host='YOURHOST',
                user='YORUSER',
                password='YOURPASSWORD',
                database='YOURDB'
            )
            self.cursor = self.conn.cursor()
            print("Database connection successful")
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            QMessageBox.critical(None, 'Database Error', f"Cannot connect to database: {err}")
            sys.exit(1)

    def execute_query(self, query, params=None):
        try:
            if not self.conn.is_connected():
                print("Reconnecting to the database...")
                self.connect()

            # Проверяем, если есть незакрытые результаты
            self._clear_unread_results()

            # Выполнение запроса
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()

        except mysql.connector.Error as err:
            print(f"Query execution error: {err}")
            QMessageBox.critical(None, 'Query Error', f"Error executing query: {err}")

    def fetch_one(self, query, params=None):
        try:
            if not self.conn.is_connected():
                print("Reconnecting to the database...")
                self.connect()

            # Проверяем, если есть незакрытые результаты
            self._clear_unread_results()

            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"Fetch error: {err}")
            QMessageBox.critical(None, 'Query Error', f"Error fetching data: {err}")
            return None

    def fetch_all(self, query, params=None):
        try:
            if not self.conn.is_connected():
                print("Reconnecting to the database...")
                self.connect()

            # Проверяем, если есть незакрытые результаты
            self._clear_unread_results()

            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Fetch error: {err}")
            QMessageBox.critical(None, 'Query Error', f"Error fetching data: {err}")
            return []

    def _clear_unread_results(self):
        """Метод для очистки незакрытых результатов (если они есть)."""
        try:
            # Попытка извлечь все результаты, если они были оставлены без внимания
            if self.cursor.nextset():
                while self.cursor.nextset():
                    pass
        except mysql.connector.Error as err:
            print(f"Error clearing unread results: {err}")
