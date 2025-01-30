import random
import string
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from database import Database


class AddTeacherForm(QDialog):
    teacher_added = pyqtSignal()

    def __init__(self, company_id, mode="add", teacher_id=None):
        super().__init__()
        self.company_id = company_id
        self.mode = mode
        self.teacher_id = teacher_id

        if self.mode == "add":
            self.setWindowTitle("Добавление преподавателя")
        elif self.mode == "edit":
            self.setWindowTitle("Редактирование преподавателя")

        self.setMinimumSize(400, 500)

        # Основной макет
        layout = QVBoxLayout()

        # Заголовок "Преподаватель"
        title_label = QLabel("Преподаватель")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-family: Impact;")
        layout.addWidget(title_label)

        # Поля ввода для Фамилии, Имени и Отчества
        self.fields = {}
        for field_name in ["Фамилия", "Имя", "Отчество"]:
            field_layout = QHBoxLayout()
            label = QLabel(field_name)
            label.setFixedWidth(100)
            line_edit = QLineEdit()
            field_layout.addWidget(label)
            field_layout.addWidget(line_edit)
            layout.addLayout(field_layout)
            self.fields[field_name] = line_edit

            # Устанавливаем стиль для полей ввода
            label.setStyleSheet("font-family: Impact; font-size: 20px;")
            line_edit.setStyleSheet("font-family: Impact; font-size: 18px;")

        # Поле "Направление"
        direction_layout = QHBoxLayout()
        direction_label = QLabel("Направление")
        direction_label.setFixedWidth(100)
        self.direction_combo = QComboBox()
        self.load_directions()
        direction_layout.addWidget(direction_label)
        direction_layout.addWidget(self.direction_combo)
        layout.addLayout(direction_layout)

        # Устанавливаем стиль для поля направления
        direction_label.setStyleSheet("font-family: Impact; font-size: 20px;")
        self.direction_combo.setStyleSheet("font-family: Impact; font-size: 18px;")

        # Поля для логина и пароля
        for field_name in ["Логин", "Пароль"]:
            field_layout = QHBoxLayout()
            label = QLabel(field_name)
            label.setFixedWidth(100)
            line_edit = QLineEdit()
            if field_name == "Логин":
                line_edit.setReadOnly(True)  # Поле "Логин" нередактируемое
                line_edit.setText(self.generate_login())  # Генерация логина
            elif field_name == "Пароль":
                line_edit.setText(self.generate_password())  # Генерация пароля
            field_layout.addWidget(label)
            field_layout.addWidget(line_edit)
            layout.addLayout(field_layout)
            self.fields[field_name] = line_edit

            # Устанавливаем стиль для логина и пароля
            label.setStyleSheet("font-family: Impact; font-size: 20px;")
            line_edit.setStyleSheet("font-family: Impact; font-size: 18px;")

        # Таблица "Контактная информация"
        contact_label = QLabel("Контактная информация:")
        contact_label.setStyleSheet("font-size: 18px; font-family: Impact;")
        layout.addWidget(contact_label)

        self.contact_table = QTableWidget(0, 2)
        self.contact_table.setHorizontalHeaderLabels(["Тип", "Значение"])
        self.contact_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.contact_table)

        # Устанавливаем стиль для таблицы
        self.contact_table.setStyleSheet("font-family: Impact; font-size: 16px;")

        add_contact_button = QPushButton("Добавить контакт")
        add_contact_button.clicked.connect(self.add_contact_row)
        layout.addWidget(add_contact_button)

        # Устанавливаем стиль для кнопки "Добавить контакт"
        add_contact_button.setStyleSheet("font-family: Impact; font-size: 16px;")

        delete_contact_button = QPushButton("Удалить контакт")
        delete_contact_button.clicked.connect(self.delete_contact_row)
        layout.addWidget(delete_contact_button)

        # Устанавливаем стиль для кнопки "Удалить контакт"
        delete_contact_button.setStyleSheet("font-family: Impact; font-size: 16px;")

        # Кнопки "Сохранить" и "Удалить"
        button_layout = QHBoxLayout()

        if self.mode == "add":
            self.delete_button = QPushButton("Отмена")
            self.delete_button.clicked.connect(self.reject)
        elif self.mode == "edit":
            self.delete_button = QPushButton("Удалить")
            self.delete_button.clicked.connect(self.delete_teacher)

        button_layout.addWidget(self.delete_button)

        # Устанавливаем стиль для кнопки "Удалить" или "Отмена"
        self.delete_button.setStyleSheet("font-family: Impact; font-size: 20px;")

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_teacher)
        button_layout.addWidget(self.save_button)

        # Устанавливаем стиль для кнопки "Сохранить"
        self.save_button.setStyleSheet("font-family: Impact; font-size: 20px;")

        layout.addLayout(button_layout)
        self.setLayout(layout)

        if self.mode == "edit" and self.teacher_id is not None:
            self.load_teacher_data()

    def generate_login(self):
        """Генерирует уникальный логин."""
        base_login = "teacher"
        login_number = 1
        login = f"{base_login}{login_number}"

        db = Database()
        query = "SELECT COUNT(*) FROM teachers WHERE teacher_login = %s"
        while db.fetch_one(query, (login,))[0] > 0:
            login_number += 1
            login = f"{base_login}{login_number}"
        return login

    def generate_password(self):
        """Генерирует случайный пароль."""
        characters = string.ascii_letters + string.digits + "!@#$%^&*()"
        return ''.join(random.choice(characters) for _ in range(8))

    def add_contact_row(self):
        """Добавляет новую строку в таблицу контактной информации."""
        row_position = self.contact_table.rowCount()
        self.contact_table.insertRow(row_position)
        self.contact_table.setItem(row_position, 0, QTableWidgetItem(""))
        self.contact_table.setItem(row_position, 1, QTableWidgetItem(""))

    def delete_contact_row(self):
        """Удаляет выбранную строку из таблицы контактной информации."""
        selected_row = self.contact_table.currentRow()
        if selected_row >= 0:
            confirmation = QMessageBox.question(
                self,
                "Подтверждение удаления",
                "Вы уверены, что хотите удалить этот контакт?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirmation == QMessageBox.StandardButton.Yes:
                contact_type = self.contact_table.item(selected_row, 0).text()
                contact_value = self.contact_table.item(selected_row, 1).text()
                db = Database()
                # Удаление контакта из базы данных
                db.execute_query(
                    "DELETE FROM contacts WHERE person_id = %s AND contact_type = %s AND contact_state = %s",
                    (self.teacher_id, contact_type, contact_value))
                self.contact_table.removeRow(selected_row)
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите контакт для удаления.")

    def load_directions(self):
        """Загружает направления из базы данных."""
        db = Database()
        query = "SELECT direction_id, direction_name FROM directions WHERE company_id = %s"
        directions = db.fetch_all(query, (self.company_id,))
        for direction_id, direction_name in directions:
            self.direction_combo.addItem(direction_name, direction_id)

    def save_teacher(self):
        """Сохраняет данные преподавателя в базе данных."""
        surname = self.fields["Фамилия"].text()
        name = self.fields["Имя"].text()
        patronymic = self.fields["Отчество"].text()
        login = self.fields["Логин"].text()
        password = self.fields["Пароль"].text()
        direction_id = self.direction_combo.currentData()

        if not (surname and name and login and password):
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля.")
            return

        db = Database()

        if self.mode == "add":
            # Добавление нового преподавателя
            query_person = """
                INSERT INTO persons (person_name, person_surname, person_patron, company_id)
                VALUES (%s, %s, %s, %s)
            """
            db.execute_query(query_person, (name, surname, patronymic, self.company_id))
            person_id = db.fetch_one("SELECT LAST_INSERT_ID()")[0]

            query_teacher = """
                INSERT INTO teachers (teacher_id, teacher_login, teacher_password, direction_id)
                VALUES (%s, %s, %s, %s)
            """
            db.execute_query(query_teacher, (person_id, login, password, direction_id))
            self.teacher_id = person_id

        elif self.mode == "edit" and self.teacher_id:
            # Обновление существующего преподавателя
            query_person = """
                UPDATE persons
                SET person_name = %s, person_surname = %s, person_patron = %s
                WHERE person_id = %s
            """
            db.execute_query(query_person, (name, surname, patronymic, self.teacher_id))

            query_teacher = """
                UPDATE teachers
                SET teacher_login = %s, teacher_password = %s, direction_id = %s
                WHERE teacher_id = %s
            """
            db.execute_query(query_teacher, (login, password, direction_id, self.teacher_id))
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось определить режим сохранения.")
            return

        # Обновление контактной информации
        db.execute_query(
            "DELETE FROM contacts WHERE person_id = %s", (self.teacher_id,))
        for row in range(self.contact_table.rowCount()):
            contact_type = self.contact_table.item(row, 0).text()
            contact_value = self.contact_table.item(row, 1).text()
            if contact_type and contact_value:
                db.execute_query("""
                    INSERT INTO contacts (person_id, contact_type, contact_state) 
                    VALUES (%s, %s, %s)
                """, (self.teacher_id, contact_type, contact_value))

        QMessageBox.information(self, "Успех", f"Преподаватель успешно сохранен.\nЛогин: {login}\nПароль: {password}")
        self.teacher_added.emit()
        self.accept()

    def load_teacher_data(self):
        """Загружает данные преподавателя для редактирования."""
        if not self.teacher_id:
            QMessageBox.warning(self, "Ошибка", "Не указан ID преподавателя для редактирования.")
            self.reject()
            return

        query = """
            SELECT p.person_name, p.person_surname, p.person_patron, t.teacher_login, t.teacher_password, t.direction_id
            FROM teachers t
            JOIN persons p ON t.teacher_id = p.person_id
            WHERE t.teacher_id = %s
        """
        db = Database()
        record = db.fetch_one(query, (self.teacher_id,))

        if not record:
            QMessageBox.warning(self, "Ошибка", "Данные преподавателя не найдены.")
            self.reject()
            return

        self.fields["Имя"].setText(record[0])
        self.fields["Фамилия"].setText(record[1])
        self.fields["Отчество"].setText(record[2])
        self.fields["Логин"].setText(record[3])
        self.fields["Пароль"].setText(record[4])
        direction_index = self.direction_combo.findData(record[5])
        if direction_index != -1:
            self.direction_combo.setCurrentIndex(direction_index)

        # Загружаем контакты
        contacts_query = """
            SELECT contact_type, contact_state
            FROM contacts
            WHERE person_id = %s
        """
        contacts = db.fetch_all(contacts_query, (self.teacher_id,))
        for contact in contacts:
            self.add_contact_row()
            row = self.contact_table.rowCount() - 1
            self.contact_table.setItem(row, 0, QTableWidgetItem(contact[0]))
            self.contact_table.setItem(row, 1, QTableWidgetItem(contact[1]))
        self.contact_table.resizeRowsToContents()

    def delete_teacher(self):
        """Удаляет преподавателя из базы данных."""
        confirmation = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить этого преподавателя?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            db = Database()
            try:
                query = "DELETE FROM teachers WHERE teacher_id = %s"
                db.execute_query(query, (self.teacher_id,))
                QMessageBox.information(self, "Успех", "Преподаватель успешно удален.")
                self.accept()  # Закрываем форму после успешного удаления
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить преподавателя: {e}")