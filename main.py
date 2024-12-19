import sys
import mysql.connector
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QMessageBox, QStackedWidget, QTableWidget,
    QTableWidgetItem, QListWidget, QFrame
)
from PyQt6.QtCore import Qt


# Класс подключения к БД
class Database:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host='YOURHOST',
                user='YOURUSERNAME',
                password='YOURPASSWORD',
                database='YOURDBNAME'
            )
            self.cursor = self.conn.cursor()
            print("Database connection successful")
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            QMessageBox.critical(None, 'Database Error', f"Cannot connect to database: {err}")
            sys.exit(1)

    def execute_query(self, query, params=None):
        try:
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
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Fetch error: {err}")
            QMessageBox.critical(None, 'Query Error', f"Error fetching data: {err}")
            return []


# Окно входа
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle('Вход')
        self.setGeometry(500, 200, 400, 200)
        self.layout = QVBoxLayout()

        # Поля ввода
        self.login_input = QLineEdit(self)
        self.login_input.setPlaceholderText("Введите логин")
        self.login_input.setFixedWidth(250)  # Устанавливаем фиксированную ширину
        self.layout.addWidget(self.login_input, alignment=Qt.AlignmentFlag.AlignRight)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedWidth(250)  # Устанавливаем фиксированную ширину
        self.layout.addWidget(self.password_input, alignment=Qt.AlignmentFlag.AlignRight)

        # Макет для кнопок
        button_layout = QHBoxLayout()

        # Кнопка регистрации
        self.register_button = QPushButton('Регистрация', self)
        self.register_button.clicked.connect(self.show_registration_window)
        button_layout.addWidget(self.register_button)

        # Кнопка входа
        self.login_button = QPushButton('Вход', self)
        self.login_button.clicked.connect(self.login)
        button_layout.addWidget(self.login_button)

        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

    def login(self):
        login = self.login_input.text()
        password = self.password_input.text()

        if login and password:
            try:
                # Проверка логина администратора
                query = "SELECT company_id FROM admins WHERE admin_login = %s AND admin_password = %s"
                result = self.db.fetch_one(query, (login, password))
                if result:
                    company_id = result[0]
                    query = "SELECT company_name FROM companies WHERE company_id = %s"
                    company_name = self.db.fetch_one(query, (company_id,))[0]
                    QMessageBox.information(self, 'Success', f'Вошли как Администратор.\n Компания: {company_name}')
                    self.close()
                    self.main_window = MainWindow(company_name, is_admin=True, company_id=company_id)
                    self.main_window.show()
                    return

                # Проверка логина преподавателя
                query = """
                    SELECT p.company_id FROM teachers t
                    JOIN persons p ON t.teacher_id = p.person_id
                    WHERE t.teacher_login = %s AND t.teacher_password = %s
                """
                result = self.db.fetch_one(query, (login, password))
                if result:
                    company_id = result[0]
                    query = "SELECT company_name FROM companies WHERE company_id = %s"
                    company_name = self.db.fetch_one(query, (company_id,))[0]
                    QMessageBox.information(self, 'Success', f'Вошли как Преподаватель.\nКомпания: {company_name}')
                    self.close()
                    self.main_window = MainWindow(company_name, is_admin=False, company_id=company_id)
                    self.main_window.show()
                    return

                QMessageBox.warning(self, 'Error', 'Неверный логин или пароль!')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f"Ошибка при входе: {e}")
        else:
            QMessageBox.warning(self, 'Input Error', 'Все поля обязательны для заполнения!')

    def show_registration_window(self):
        self.close()
        self.registration_window = RegistrationWindow()
        self.registration_window.show()


# Окно регистрации
class RegistrationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Регистрация для администратора")
        self.setGeometry(500, 200, 400, 250)

        # Главный макет
        layout = QVBoxLayout()

        # Поле "НАЗВАНИЕ ЗАВЕДЕНИЯ"
        self.center_name_input = QLineEdit()
        self.center_name_input.setPlaceholderText("Название заведения")
        self.center_name_input.setFixedWidth(250)
        layout.addWidget(self.center_name_input, alignment=Qt.AlignmentFlag.AlignRight)

        # Поле "ЛОГИН АДМИНА"
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин админа (автоматически)")
        self.login_input.setReadOnly(True)
        self.login_input.setFixedWidth(250)
        layout.addWidget(self.login_input, alignment=Qt.AlignmentFlag.AlignRight)

        # Поле "ПАРОЛЬ АДМИНА"
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль админа")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedWidth(250)
        layout.addWidget(self.password_input, alignment=Qt.AlignmentFlag.AlignRight)

        # Макет для кнопок
        button_layout = QHBoxLayout()

        # Кнопка "ВХОД"
        self.login_button = QPushButton("Вход")
        self.login_button.clicked.connect(self.show_login_window)
        button_layout.addWidget(self.login_button)

        # Кнопка "РЕГИСТРАЦИЯ"
        self.register_button = QPushButton("Регистрация")
        self.register_button.clicked.connect(self.register)
        button_layout.addWidget(self.register_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Привязка генерации логина к изменению названия
        self.center_name_input.textChanged.connect(self.generate_admin_login)

    def generate_admin_login(self):
        """Генерация логина администратора на основе названия заведения."""
        center_name = self.center_name_input.text().strip()
        if center_name:
            base_login = center_name.lower().replace(" ", "_") + "_admin"
            login = base_login

            # Проверка на уникальность логина
            query = "SELECT admin_login FROM admins WHERE admin_login = %s"
            i = 1
            while True:
                if i > 1:
                    login = f"{base_login}{i}"
                else:
                    login = base_login
                result = self.db.fetch_one(query, (login,))
                if not result:
                    break
                i += 1
            self.login_input.setText(login)
        else:
            self.login_input.clear()

    def register(self):
        center_name = self.center_name_input.text().strip()
        admin_login = self.login_input.text().strip()
        admin_password = self.password_input.text(). strip()

        if center_name and admin_login and admin_password:
            try:
                # Вставка данных в таблицу компаний
                query = "INSERT INTO companies (company_name) VALUES (%s)"
                self.db.execute_query(query, (center_name,))
                company_id = self.db.cursor.lastrowid

                # Вставка данных администратора
                query = "INSERT INTO admins (company_id, admin_login, admin_password) VALUES (%s, %s, %s)"
                self.db.execute_query(query, (company_id, admin_login, admin_password))

                QMessageBox.information(self, "Success", "Регистрация завершена!")
                self.close()
                self.login_window = LoginWindow()
                self.login_window.show()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Ошибка регистрации: {e}")
        else:
            QMessageBox.warning(self, "Input Error", "Все поля обязательны для заполнения!")

    def show_login_window(self):
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()


# Основное окно с панелью управления
class MainWindow(QWidget):
    def __init__(self, company_name, is_admin, company_id):
        super().__init__()
        self.company_id = company_id  # Сохраняем company_id
        self.db = Database()
        self.layout = QHBoxLayout()

        # Устанавливаем статус пользователя (админ или препод)
        self.status = "Администратор" if is_admin else "Преподаватель"

        # Обновляем заголовок окна
        self.setWindowTitle(f"{company_name} - {self.status}")

        self.setGeometry(500, 200, 1000, 600)

        # Панель навигации с кнопками (sidebar)
        self.nav_panel = QVBoxLayout()

        if is_admin:  # Добавляем проверку на права администратора
            self.management_button = QPushButton("Управление", self)
            self.management_button.setFixedHeight(50)
            self.management_button.clicked.connect(self.display_management)
            self.nav_panel.addWidget(self.management_button)

        self.layout.addLayout(self.nav_panel)

        # Контент вкладок (содержимое будет отображаться справа)
        self.content_area = QStackedWidget(self)
        self.layout.addWidget(self.content_area)

        self.setLayout(self.layout)

    def display_management(self):
        """Отображаем раздел управления для администратора."""
        management_widget = QWidget()
        management_layout = QHBoxLayout()

        # Левая панель с элементами управления
        left_panel = QFrame()
        left_panel.setFixedWidth(150)
        left_layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.addItem("Ученики")
        self.list_widget.addItem("Преподаватели")
        self.list_widget.addItem("Направления")
        self.list_widget.addItem("Группы")
        self.list_widget.addItem("Помещения")
        self.list_widget.clicked.connect(self.change_content)  # Событие при выборе элемента

        left_layout.addWidget(self.list_widget)
        left_panel.setLayout(left_layout)

        # Правая панель для отображения записей
        self.right_panel = QWidget()
        right_layout = QVBoxLayout()

        # Кнопки для добавления, редактирования и удаления
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_item)
        button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.edit_item)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_item)
        button_layout.addWidget(self.delete_button)

        # Добавляем кнопки над таблицей
        right_layout.addLayout(button_layout)

        # Таблица для отображения данных
        self.table_widget = QTableWidget(0, 2)  # Начальный размер таблицы (без колонки №)
        self.table_widget.setHorizontalHeaderLabels(["Название", "Описание"])
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Запрещаем редактировать таблицу

        right_layout.addWidget(self.table_widget)

        self.right_panel.setLayout(right_layout)

        management_layout.addWidget(left_panel)
        management_layout.addWidget(self.right_panel)

        management_widget.setLayout(management_layout)

        self.content_area.addWidget(management_widget)
        self.content_area.setCurrentWidget(management_widget)

        # Устанавливаем обработчик для щелчка
        self.table_widget.cellClicked.connect(self.handle_click)
        self.table_widget.cellDoubleClicked.connect(self.edit_item)  # Обработка двойного щелчка

    def change_content(self):
        """Изменение содержимого правой панели в зависимости от выбранного элемента управления."""
        selected_item = self.list_widget.currentItem().text()

        if selected_item == "Ученики":
            self.load_students()
        elif selected_item == "Преподаватели":
            self.load_teachers()
        elif selected_item == "Направления":
            self.load_directions()
        elif selected_item == "Группы":
            self.load_groups()
        elif selected_item == "Помещения":
            self.load_rooms()

    def load_students(self):
        """Загружаем список учеников в таблицу."""
        query = """
            SELECT s.student_id, p.person_name, p.person_surname, s.birth_date
            FROM students s
            JOIN persons p ON s.student_id = p.person_id
            WHERE p.company_id = %s
        """
        records = self.db.fetch_all(query, (self.company_id,))
        self.update_table(records, ["ФИО", "Дата рождения"])

    def load_teachers(self):
        """Загружаем список преподавателей в таблицу."""
        query = """
            SELECT 
                CONCAT(p.person_surname, ' ', p.person_name, ' ', p.person_patron) AS full_name, 
                IFNULL(d.direction_name, '') AS direction_name
            FROM teachers t
            JOIN persons p ON t.teacher_id = p.person_id
            LEFT JOIN directions d ON t.direction_id = d.direction_id
            WHERE p.company_id = %s
        """
        records = self.db.fetch_all(query, (self.company_id,))
        self.update_table(records, ["ФИО", "Направление"])

    def load_directions(self):
        """Загружаем список направлений в таблицу."""
        query = """
            SELECT direction_name, direction_description
            FROM directions
            WHERE company_id = %s
        """
        records = self.db.fetch_all(query, (self.company_id,))
        self.update_table(records, ["Название направления", "Описание"])

    def load_groups(self):
        """Загружаем список групп в таблицу."""
        query = """
            SELECT g.group_id, g.group_number, d.direction_name
            FROM groupss g
            JOIN directions d ON g.direction_id = d.direction_id
            WHERE g.company_id = %s
        """
        records = self.db.fetch_all(query, (self.company_id,))
        self.update_table(records, ["Номер группы", "Направление"])

    def load_rooms(self):
        """Загружаем список помещений в таблицу."""
        query = """
            SELECT room_id, room_number
            FROM rooms
            WHERE company_id = %s
        """
        records = self.db.fetch_all(query, (self.company_id,))
        self.update_table(records, ["Название помещения"])

    def update_table(self, records, column_names):
        """Обновляем таблицу с новыми данными."""
        self.table_widget.setRowCount(len(records))
        self.table_widget.setColumnCount(len(column_names))
        for row, record in enumerate(records):
            for col, value in enumerate(record):
                self.table_widget.setItem(row, col, QTableWidgetItem(str(value)))

        # Обновляем заголовки столбцов
        self.table_widget.setHorizontalHeaderLabels(column_names)

    def handle_click(self, row, column):
        """Обработка щелчка на записи."""
        self.selected_row = row  # Сохраняем индекс выбранной строки

    def edit_item(self):
        """Обработка редактирования записи."""
        if hasattr(self, 'selected_row'):
            selected_data = [
                self.table_widget.item(self.selected_row, col).text() if self.table_widget.item(self.selected_row, col) else ""
                for col in range(self.table_widget.columnCount())
            ]
            QMessageBox.information(self, "Редактировать",
                                    f"Редактирование записи: {selected_data}\n(функционал на стадии разработки).")
        else:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите запись для редактирования.")

    def add_item(self):
        """Обработка добавления новой записи."""
        QMessageBox.information(self, "Добавить", "Добавление новой записи (функционал на стадии разработки).")

    def delete_item(self):
        """Обработка удаления записи."""
        QMessageBox.information(self, "Удалить", "Удаление записи (функционал на стадии разработки).")


# Запуск приложения
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
