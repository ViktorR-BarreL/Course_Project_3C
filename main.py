import mysql.connector

# Параметры подключения
host = 'sql12.freesqldatabase.com'
username = 'your_username'
password = 'your_password'
dbname = 'your_database_name'

# Подключение к базе данных
conn = mysql.connector.connect(
    host=host,
    user=username,
    password=password,
    database=dbname
)

# Проверка соединения
if conn.is_connected():
    print("Connected to the database")
else:
    print("Failed to connect")

# Закрытие соединения
conn.close()
