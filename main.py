import sys
from PyQt6.QtWidgets import QApplication
from database import Database
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QMessageBox, QStackedWidget, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from schedule_tab import ScheduleTab
from groups_tab import GroupsTab
from attendance_tab import AttendanceTab
from management_tab import ManagementTab
from reports_tab import ReportsTab


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
        self.login_input.setFixedWidth(250)
        self.login_input.setStyleSheet("font-family: Impact; font-size: 18px;")
        self.layout.addWidget(self.login_input, alignment=Qt.AlignmentFlag.AlignRight)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setFixedWidth(250)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("font-family: Impact; font-size: 18px;")
        self.layout.addWidget(self.password_input, alignment=Qt.AlignmentFlag.AlignRight)

        # Макет для кнопок
        button_layout = QHBoxLayout()

        # Кнопка регистрации
        self.register_button = QPushButton('Регистрация', self)
        self.register_button.setStyleSheet("font-family: Impact; font-size: 20px;")
        self.register_button.clicked.connect(self.show_registration_window)
        button_layout.addWidget(self.register_button)

        # Кнопка входа
        self.login_button = QPushButton('Вход', self)
        self.login_button.setStyleSheet("font-family: Impact; font-size: 20px;")
        self.login_button.clicked.connect(self.login)
        button_layout.addWidget(self.login_button)

        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

    def login(self):
        login = self.login_input.text()
        password = self.password_input.text()

        if login and password:
            try:
                # Проверка для администратора
                query = "SELECT company_id FROM admins WHERE admin_login = %s AND admin_password = %s"
                result = self.db.fetch_one(query, (login, password))
                if result:
                    company_id = result[0]
                    query = "SELECT company_name FROM companies WHERE company_id = %s"
                    company_name = self.db.fetch_one(query, (company_id,))[0]
                    QMessageBox.information(self, 'Success', f'Вошли как Администратор.\n Компания: {company_name}')
                    self.close()
                    self.main_window = MainWindow(company_name, is_admin=True, company_id=company_id, teacher_id=None)
                    self.main_window.show()
                    return

                # Проверка для преподавателя
                query = """
                    SELECT p.company_id, t.teacher_id FROM teachers t
                    JOIN persons p ON t.teacher_id = p.person_id
                    WHERE t.teacher_login = %s AND t.teacher_password = %s
                """
                result = self.db.fetch_one(query, (login, password))
                if result:
                    company_id, teacher_id = result  # Извлекаем company_id и teacher_id
                    query = "SELECT company_name FROM companies WHERE company_id = %s"
                    company_name = self.db.fetch_one(query, (company_id,))[0]
                    QMessageBox.information(self, 'Success', f'Вошли как Преподаватель.\nКомпания: {company_name}')
                    self.close()
                    self.main_window = MainWindow(company_name, is_admin=False, company_id=company_id,
                                                  teacher_id=teacher_id)
                    self.main_window.show()
                    return

                QMessageBox.warning(self, 'Error', 'Неверный логин или пароль!')
            except Exception:
                QMessageBox.critical(self, 'Error', "Ошибка при входе.")
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

        layout = QVBoxLayout()

        # Поле "Название заведения"
        self.center_name_input = QLineEdit()
        self.center_name_input.setPlaceholderText("Введите название заведения")
        self.center_name_input.setFixedWidth(250)
        self.center_name_input.setStyleSheet("font-family: Impact; font-size: 18px;")
        layout.addWidget(self.center_name_input, alignment=Qt.AlignmentFlag.AlignRight)

        # Поле "Логин админа"
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин админа (автоматически)")
        self.login_input.setReadOnly(True)
        self.login_input.setFixedWidth(250)
        self.login_input.setStyleSheet("font-family: Impact; font-size: 18px;")
        layout.addWidget(self.login_input, alignment=Qt.AlignmentFlag.AlignRight)

        # Поле "Пароль админа"
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Придумайте пароль")
        self.password_input.setFixedWidth(250)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("font-family: Impact; font-size: 18px;")
        layout.addWidget(self.password_input, alignment=Qt.AlignmentFlag.AlignRight)

        # Кнопки
        button_layout = QHBoxLayout()

        self.login_button = QPushButton("Вход")
        self.login_button.setStyleSheet("font-family: Impact; font-size: 20px;")
        self.login_button.clicked.connect(self.show_login_window)
        button_layout.addWidget(self.login_button)

        self.register_button = QPushButton("Регистрация")
        self.register_button.setStyleSheet("font-family: Impact; font-size: 20px;")
        self.register_button.clicked.connect(self.register)
        button_layout.addWidget(self.register_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.center_name_input.textChanged.connect(self.generate_admin_login)

    def generate_admin_login(self):
        center_name = self.center_name_input.text().strip()
        if center_name:
            base_login = center_name.lower().replace(" ", "_") + "_admin"
            login = base_login

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
        admin_password = self.password_input.text().strip()

        if center_name and admin_login and admin_password:
            try:
                query = "INSERT INTO companies (company_name) VALUES (%s)"
                self.db.execute_query(query, (center_name,))
                company_id = self.db.cursor.lastrowid

                query = "INSERT INTO admins (company_id, admin_login, admin_password) VALUES (%s, %s, %s)"
                self.db.execute_query(query, (company_id, admin_login, admin_password))

                QMessageBox.information(self, "Success", "Регистрация завершена!")
                self.close()
                self.login_window = LoginWindow()
                self.login_window.show()
            except Exception:
                QMessageBox.critical(self, "Error", "Ошибка регистрации.")
        else:
            QMessageBox.warning(self, "Input Error", "Все поля обязательны для заполнения!")

    def show_login_window(self):
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()


# Основное окно с панелью управления
class MainWindow(QWidget):
    def __init__(self, company_name, is_admin, company_id, teacher_id=None):
        super().__init__()
        self.company_id = company_id
        self.teacher_id = teacher_id
        self.is_admin = is_admin
        self.db = Database()
        self.setGeometry(130, 70, 1280, 720)

        self.company_name = company_name
        self.is_admin = is_admin

        self.setWindowTitle(f"Компания: {company_name}")

        # Основной макет
        layout = QHBoxLayout(self)

        # Виджет для кнопок
        self.button_widget = QWidget()
        self.button_layout = QVBoxLayout(self.button_widget)

        button_font = QFont("Impact", 20)

        # Создание кнопок для вкладок
        self.schedule_button = QPushButton("Расписание")
        self.schedule_button.setFont(button_font)
        self.schedule_button.setFixedHeight(50)
        self.schedule_button.clicked.connect(lambda: self.switch_tab(0))
        self.button_layout.addWidget(self.schedule_button)

        self.groups_button = QPushButton("Группы")
        self.groups_button.setFont(button_font)
        self.groups_button.setFixedHeight(50)
        self.groups_button.clicked.connect(lambda: self.switch_tab(1))
        self.button_layout.addWidget(self.groups_button)

        self.attendance_button = QPushButton("Посещаемость")
        self.attendance_button.setFont(button_font)
        self.attendance_button.setFixedHeight(50)
        self.attendance_button.clicked.connect(lambda: self.switch_tab(2))
        self.button_layout.addWidget(self.attendance_button)

        if self.is_admin:
            self.management_button = QPushButton("Управление")
            self.management_button.setFont(button_font)
            self.management_button.setFixedHeight(50)
            self.management_button.clicked.connect(lambda: self.switch_tab(3))
            self.button_layout.addWidget(self.management_button)

            self.reports_button = QPushButton("Отчеты")
            self.reports_button.setFont(button_font)
            self.reports_button.setFixedHeight(50)
            self.reports_button.clicked.connect(lambda: self.switch_tab(4))
            self.button_layout.addWidget(self.reports_button)

        self.button_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.content_widget = QStackedWidget()
        self.schedule_tab = ScheduleTab(self.company_id, is_admin=self.is_admin, teacher_id=self.teacher_id)
        self.groups_tab = GroupsTab(self.company_id, is_admin=self.is_admin, teacher_id=self.teacher_id)
        self.attendance_tab = AttendanceTab(self.company_id, is_admin=self.is_admin, teacher_id=self.teacher_id)

        self.content_widget.addWidget(self.schedule_tab)
        self.content_widget.addWidget(self.groups_tab)
        self.content_widget.addWidget(self.attendance_tab)

        if self.is_admin:
            self.management_tab = ManagementTab(self.company_id)
            self.reports_tab = ReportsTab(self.company_id)
            self.content_widget.addWidget(self.management_tab)
            self.content_widget.addWidget(self.reports_tab)

        self.content_widget.currentChanged.connect(self.on_tab_changed)

        layout.addWidget(self.button_widget, 1)
        layout.addWidget(self.content_widget, 5)

    def switch_tab(self, index):
        self.content_widget.setCurrentIndex(index)

    def on_tab_changed(self, index):
        if index == 0:
            self.schedule_tab.current_date = QDate.currentDate()
            self.schedule_tab.update_schedule()
            self.schedule_tab.load_data()
        elif index == 1:
            self.groups_tab.groups_list.clearSelection()
            self.groups_tab.load_groups()
        elif index == 2:
            self.attendance_tab.refresh_schedule()
        elif index == 3 and self.is_admin:
            self.management_tab.update_content()
        elif index == 4 and self.is_admin:
            self.reports_tab.clear_report()

    def show_schedule_tab(self):
        self.content_widget.setCurrentIndex(0)

    def show_groups_tab(self):
        self.content_widget.setCurrentIndex(1)

    def show_attendance_tab(self):
        self.content_widget.setCurrentIndex(2)

    def show_management_tab(self):
        self.content_widget.setCurrentIndex(3)

    def show_reports_tab(self):
        self.content_widget.setCurrentIndex(4)


def initialize_database(db, script_path='schema.sql'):
    try:
        with open(script_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()
            for statement in sql_script.split(';'):
                if statement.strip():
                    db.execute_query(statement)
    except FileNotFoundError:
        QMessageBox.critical(None, 'File Error', f"SQL script file not found: {script_path}")
    except Exception:
        QMessageBox.critical(None, 'Initialization Error', "Database initialization failed.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = Database()
    initialize_database(db)
    registration_window = RegistrationWindow()
    registration_window.show()
    sys.exit(app.exec())
