from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QDateEdit, QTableWidget,
    QTableWidgetItem, QListWidget, QListWidgetItem, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from database import Database


class AddStudentForm(QDialog):
    student_added = pyqtSignal()

    def __init__(self, company_id, mode="add", student_id=None):
        super().__init__()
        self.company_id = company_id
        self.mode = mode
        self.student_id = student_id  # ID студента для редактирования

        if self.mode == "add":
            self.setWindowTitle("Добавление ученика")
        elif self.mode == "edit":
            self.setWindowTitle("Редактирование ученика")

        self.setMinimumSize(400, 500)

        # Основной макет
        layout = QVBoxLayout()

        # Заголовок "Ученик"
        title_label = QLabel("Ученик")
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

        # Поле "Дата рождения"
        dob_layout = QHBoxLayout()
        dob_label = QLabel("Дата рождения")
        dob_label.setFixedWidth(100)
        self.date_of_birth = QDateEdit()
        self.date_of_birth.setCalendarPopup(True)
        self.date_of_birth.setDate(QDate.currentDate())
        dob_layout.addWidget(dob_label)
        dob_layout.addWidget(self.date_of_birth)
        layout.addLayout(dob_layout)

        # Устанавливаем стиль для поля даты рождения
        dob_label.setStyleSheet("font-family: Impact; font-size: 20px;")
        self.date_of_birth.setStyleSheet("font-family: Impact; font-size: 18px;")

        # Поле "Группа" с кнопкой для выбора групп
        group_layout = QHBoxLayout()
        group_label = QLabel("Группа")
        group_label.setFixedWidth(100)
        self.group_combo = QPushButton("Выбрать группы")
        self.group_combo.clicked.connect(self.select_groups)
        group_layout.addWidget(group_label)
        group_layout.addWidget(self.group_combo)
        layout.addLayout(group_layout)

        # Устанавливаем стиль для группы
        group_label.setStyleSheet("font-family: Impact; font-size: 20px;")
        self.group_combo.setStyleSheet("font-family: Impact; font-size: 18px;")

        self.selected_groups = []  # Список выбранных групп

        # Таблица "Контактная информация"
        contact_label = QLabel("Контактная информация:")
        contact_label.setStyleSheet("font-size: 18px; font-family: Impact;")
        layout.addWidget(contact_label)

        self.contact_table = QTableWidget(0, 2)
        self.contact_table.setHorizontalHeaderLabels(["Тип", "Значение"])
        self.contact_table.horizontalHeader().setStretchLastSection(True)
        self.contact_table.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)
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
            self.delete_button.clicked.connect(self.delete_student)

        button_layout.addWidget(self.delete_button)

        # Устанавливаем стиль для кнопки "Удалить" или "Отмена"
        self.delete_button.setStyleSheet("font-family: Impact; font-size: 20px;")

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_student)
        button_layout.addWidget(self.save_button)

        # Устанавливаем стиль для кнопки "Сохранить"
        self.save_button.setStyleSheet("font-family: Impact; font-size: 20px;")

        layout.addLayout(button_layout)
        self.setLayout(layout)

        if self.mode == "edit" and self.student_id is not None:
            self.load_student_data()

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
                    (self.student_id, contact_type, contact_value))
                self.contact_table.removeRow(selected_row)
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите контакт для удаления.")

    def select_groups(self):
        """Открывает окно для выбора групп, фильтруя их по возрасту."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Выбор групп")
        dialog.setMinimumSize(300, 400)

        layout = QVBoxLayout()

        group_list_widget = QListWidget()

        # Загружаем группы из базы данных в зависимости от возраста ученика
        age = self.calculate_age(self.date_of_birth.date())
        available_groups = self.load_groups_by_age(age)

        # Добавляем группы в список
        for group in available_groups:
            item = QListWidgetItem(group)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if group in self.selected_groups else Qt.CheckState.Unchecked)
            group_list_widget.addItem(item)

        layout.addWidget(group_list_widget)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(
            lambda: self.save_selected_groups(dialog, group_list_widget))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)
        dialog.exec()

    def load_groups_by_age(self, age):
        """Загружает группы из базы данных в зависимости от возраста ученика."""
        db = Database()
        query = """
            SELECT group_number FROM groupss 
            WHERE lower_age_limit <= %s AND upper_age_limit >= %s AND company_id = %s
        """
        records = db.fetch_all(query, (age, age, self.company_id))
        return [str(record[0]) for record in records]

    def save_selected_groups(self, dialog, group_list_widget):
        """Сохраняет выбранные группы."""
        self.selected_groups = [
            group_list_widget.item(i).text()
            for i in range(group_list_widget.count())
            if group_list_widget.item(i).checkState() == Qt.CheckState.Checked
        ]
        self.group_combo.setText(", ".join(self.selected_groups))
        dialog.accept()

    def calculate_age(self, birth_date):
        """Вычисляет возраст ученика на основе даты рождения."""
        today = QDate.currentDate()
        return today.year() - birth_date.year() - (
            (today.month(), today.day()) < (birth_date.month(), birth_date.day()))

    def save_student(self):
        """Сохраняет данные ученика в базе данных."""
        surname = self.fields["Фамилия"].text()
        first_name = self.fields["Имя"].text()
        patronymic = self.fields["Отчество"].text()
        birth_date = self.date_of_birth.date().toString("yyyy-MM-dd")

        if not (surname and first_name):
            QMessageBox.warning(
                self, "Ошибка", "Фамилия и Имя обязательны для заполнения.")
            return

        db = Database()

        if self.mode == "add":
            # Добавление нового ученика
            query_person = """
                INSERT INTO persons (person_name, person_surname, person_patron, company_id)
                VALUES (%s, %s, %s, %s)
            """
            db.execute_query(
                query_person, (first_name, surname, patronymic, self.company_id))
            person_id = db.fetch_one("SELECT LAST_INSERT_ID()")[0]

            query_student = """
                INSERT INTO students (student_id, birth_date)
                VALUES (%s, %s)
            """
            db.execute_query(query_student, (person_id, birth_date))
            student_id = person_id

        elif self.mode == "edit" and self.student_id:
            # Обновление существующего ученика
            query_person = """
                UPDATE persons
                SET person_name = %s, person_surname = %s, person_patron = %s
                WHERE person_id = %s
            """
            db.execute_query(
                query_person, (first_name, surname, patronymic, self.student_id))

            query_student = """
                UPDATE students
                SET birth_date = %s
                WHERE student_id = %s
            """
            db.execute_query(query_student, (birth_date, self.student_id))
            student_id = self.student_id
        else:
            QMessageBox.warning(
                self, "Ошибка", "Не удалось определить режим сохранения.")
            return

        # Обновление групп
        db.execute_query(
            "DELETE FROM student_group WHERE student_id = %s", (student_id,))
        for group_name in self.selected_groups:
            group_id = db.fetch_one("""
                SELECT group_id FROM groupss 
                WHERE group_number = %s AND company_id = %s
            """, (group_name, self.company_id))[0]
            db.execute_query("""
                INSERT INTO student_group (student_id, group_id)
                VALUES (%s, %s)
            """, (student_id, group_id))

        # Обновление контактной информации
        db.execute_query(
            "DELETE FROM contacts WHERE person_id = %s", (student_id,))
        for row in range(self.contact_table.rowCount()):
            contact_type = self.contact_table.item(row, 0).text()
            contact_value = self.contact_table.item(row, 1).text()
            if contact_type and contact_value:
                db.execute_query("""
                    INSERT INTO contacts (person_id, contact_type, contact_state) 
                    VALUES (%s, %s, %s)
                """, (student_id, contact_type, contact_value))

        QMessageBox.information(
            self, "Успех", "Данные ученика успешно сохранены!")
        self.student_added.emit()
        self.accept()

    def load_student_data(self):
        """Загружает данные ученика для редактирования."""
        if not self.student_id:
            QMessageBox.warning(
                self, "Ошибка", "Не указан ID студента для редактирования.")
            self.reject()
            return

        query = """
            SELECT p.person_name, p.person_surname, p.person_patron, s.birth_date, p.person_id
            FROM students s
            JOIN persons p ON s.student_id = p.person_id
            WHERE s.student_id = %s
        """
        db = Database()
        record = db.fetch_one(query, (self.student_id,))

        if not record:
            QMessageBox.warning(self, "Ошибка", "Данные студента не найдены.")
            self.reject()
            return

        # Заполняем поля данными
        self.fields["Имя"].setText(record[0])
        self.fields["Фамилия"].setText(record[1])
        self.fields["Отчество"].setText(record[2])
        self.date_of_birth.setDate(QDate.fromString(
            record[3].strftime("%Y-%m-%d"), "yyyy-MM-dd"))

        person_id = record[4]  # person_id

        # Загружаем группы
        groups_query = """
            SELECT g.group_number
            FROM student_group sg
            JOIN groupss g ON sg.group_id = g.group_id
            WHERE sg.student_id = %s
        """
        groups = db.fetch_all(groups_query, (self.student_id,))
        self.selected_groups = [group[0] for group in groups]
        self.group_combo.setText(", ".join(self.selected_groups))

        # Загружаем контакты
        contacts_query = """
            SELECT contact_type, contact_state
            FROM contacts
            WHERE person_id = %s
        """
        contacts = db.fetch_all(contacts_query, (person_id,))
        for contact in contacts:
            self.add_contact_row()
            row = self.contact_table.rowCount() - 1
            self.contact_table.setItem(row, 0, QTableWidgetItem(contact[0]))
            self.contact_table.setItem(row, 1, QTableWidgetItem(contact[1]))
        self.contact_table.resizeRowsToContents()

    def delete_student(self):
        """Удаляет группу из базы данных."""
        confirmation = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить этого ученика?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            db = Database()
            try:
                query = "DELETE FROM students WHERE student_id = %s"
                db.execute_query(query, (self.student_id,))
                QMessageBox.information(self, "Успех", "Ученик успешно удален.")
                self.accept()  # Закрываем форму после успешного удаления
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить ученика: {e}")