from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QTableWidget,
    QListWidgetItem, QTableWidgetItem, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QSize, QDate
from PyQt6.QtGui import QFont
from student_form import AddStudentForm
from teacher_form import AddTeacherForm
from direction_form import AddDirectionForm
from room_form import AddRoomForm
from group_form import AddGroupForm
from database import Database


class ManagementTab(QWidget):
    def __init__(self, company_id):
        super().__init__()
        self.company_id = company_id
        self.db = Database()

        # Основной макет
        management_layout = QHBoxLayout(self)

        # Левая панель (список разделов)
        left_panel = QWidget()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont("Impact", 20))

        for item_text in ["Ученики", "Преподаватели", "Направления", "Группы", "Помещения"]:
            item = QListWidgetItem(item_text)
            item.setSizeHint(QSize(0, 30))
            self.list_widget.addItem(item)

        self.list_widget.currentItemChanged.connect(self.update_content)
        left_layout.addWidget(self.list_widget)
        left_panel.setLayout(left_layout)

        # Правая панель (таблица и кнопки)
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        button_container = QHBoxLayout()
        button_container.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.add_button = QPushButton("➕")
        self.add_button.setFont(QFont("Segoe UI", 16))
        self.add_button.setFixedSize(30, 30)
        self.add_button.clicked.connect(self.handle_add_button)
        button_container.addWidget(self.add_button)

        self.edit_button = QPushButton("✏️")
        self.edit_button.setFont(QFont("Segoe UI", 14))
        self.edit_button.setFixedSize(30, 30)
        self.edit_button.clicked.connect(self.handle_edit_button)
        button_container.addWidget(self.edit_button)

        self.delete_button = QPushButton("❌")
        self.delete_button.setFont(QFont("Segoe UI", 14))
        self.delete_button.setFixedSize(30, 30)
        self.delete_button.clicked.connect(self.handle_delete_button)
        button_container.addWidget(self.delete_button)

        right_layout.addLayout(button_container)

        self.table_widget = QTableWidget(0, 2)
        self.table_widget.setHorizontalHeaderLabels(["", ""])
        self.table_widget.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.table_widget.setFont(QFont("Impact", 18))
        right_layout.addWidget(self.table_widget)

        right_panel.setLayout(right_layout)
        management_layout.addWidget(left_panel)
        management_layout.addWidget(right_panel)

        self.setLayout(management_layout)
        self.add_direction_form = AddDirectionForm(self.company_id)
        self.add_direction_form.direction_added.connect(self.load_directions)

        # self.update_content()

    def update_content(self):
        self.db = Database()  # Пересоздание подключения
        selected_item = self.list_widget.currentItem()
        if selected_item is not None:
            selected_item_text = selected_item.text()
            if selected_item_text == "Ученики":
                self.load_students()
            elif selected_item_text == "Преподаватели":
                self.load_teachers()
            elif selected_item_text == "Направления":
                self.load_directions()
            elif selected_item_text == "Группы":
                self.load_groups()
            elif selected_item_text == "Помещения":
                self.load_rooms()

    def load_students(self):
        query = """
            SELECT student_id, CONCAT(p.person_surname, ' ', p.person_name, ' ', p.person_patron) AS full_name, s.birth_date
            FROM students s
            JOIN persons p ON s.student_id = p.person_id
            WHERE p.company_id = %s
        """
        records = self.db.fetch_all(query, (self.company_id,))
        self.update_table(records, ["ФИО", "Дата рождения"])

    def load_teachers(self):
        query = """
            SELECT teacher_id, CONCAT(p.person_surname, ' ', p.person_name, ' ', p.person_patron) AS full_name, d.direction_name
            FROM teachers t
            JOIN persons p ON t.teacher_id = p.person_id
            JOIN directions d ON t.direction_id = d.direction_id
            WHERE p.company_id = %s
        """
        records = self.db.fetch_all(query, (self.company_id,))
        self.update_table(records, ["ФИО", "Направление"])

    def load_directions(self):
        query = """
            SELECT direction_id, direction_name, direction_description
            FROM directions
            WHERE company_id = %s
        """
        records = self.db.fetch_all(query, (self.company_id,))
        self.update_table(records, ["Название направления", "Описание"])

    def load_groups(self):
        query = """
            SELECT group_id, g.group_number, d.direction_name
            FROM groupss g
            JOIN directions d ON g.direction_id = d.direction_id
            WHERE g.company_id = %s
        """
        records = self.db.fetch_all(query, (self.company_id,))
        self.update_table(records, ["Номер группы", "Направление"])

    def load_rooms(self):
        query = """
            SELECT room_id, room_number, room_description
            FROM rooms
            WHERE company_id = %s
        """
        records = self.db.fetch_all(query, (self.company_id,))
        self.update_table(records, ["Номер помещения", "Описание"])

    def update_table(self, records, column_names):
        self.table_widget.setRowCount(len(records))
        self.table_widget.setColumnCount(len(column_names))
        for row, record in enumerate(records):
            for col, value in enumerate(record[1:]):
                self.table_widget.setItem(
                    row, col, QTableWidgetItem(str(value)))

            self.table_widget.item(row, 0).setData(
                Qt.ItemDataRole.UserRole, record[0])

        self.table_widget.setHorizontalHeaderLabels(column_names)
        for column in range(self.table_widget.columnCount()):
            self.table_widget.resizeColumnToContents(column)

    def handle_add_button(self):
        selected_item = self.list_widget.currentItem()
        if selected_item is not None:
            if selected_item.text() == "Ученики":
                add_student_form = AddStudentForm(self.company_id)
                add_student_form.student_added.connect(self.load_students)
                add_student_form.exec()
            elif selected_item.text() == "Преподаватели":
                add_teacher_form = AddTeacherForm(self.company_id)
                add_teacher_form.teacher_added.connect(self.load_teachers)
                add_teacher_form.exec()
            elif selected_item.text() == "Направления":
                add_direction_form = AddDirectionForm(self.company_id)
                add_direction_form.direction_added.connect(
                    self.load_directions)
                add_direction_form.exec()
            elif selected_item.text() == "Группы":
                add_groups_form = AddGroupForm(self.company_id)
                add_groups_form.group_added.connect(self.load_groups)
                add_groups_form.exec()
            elif selected_item.text() == "Помещения":
                add_room_form = AddRoomForm(self.company_id)
                add_room_form.room_added.connect(self.load_rooms)
                add_room_form.exec()
        self.update_content()

    def handle_delete_button(self):
        selected_row = self.table_widget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(
                self, "Ошибка", "Пожалуйста, выберите запись для удаления.")
            return

        record_id_item = self.table_widget.item(selected_row, 0)
        record_id = record_id_item.data(Qt.ItemDataRole.UserRole)
        if not record_id:
            QMessageBox.warning(
                self, "Ошибка", "Невозможно получить идентификатор записи.")
            return

        confirmation = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить выбранную запись?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            selected_item = self.list_widget.currentItem()
            if selected_item is not None:
                selected_item_text = selected_item.text()
                if selected_item_text == "Ученики":
                    query = "DELETE FROM students WHERE student_id = %s"
                elif selected_item_text == "Преподаватели":
                    query = "DELETE FROM teachers WHERE teacher_id = %s"
                elif selected_item_text == "Направления":
                    query = "DELETE FROM directions WHERE direction_id = %s"
                elif selected_item_text == "Группы":
                    query = "DELETE FROM groupss WHERE group_id = %s"
                elif selected_item_text == "Помещения":
                    query = "DELETE FROM rooms WHERE room_id = %s"
                else:
                    QMessageBox.warning(
                        self, "Ошибка", "Неизвестный тип записи.")
                    return

                try:
                    self.db.execute_query(query, (record_id,))
                    self.update_content()
                    QMessageBox.information(
                        self, "Успех", "Запись успешно удалена.")
                except Exception as e:
                    QMessageBox.critical(
                        self, "Ошибка", f"Ошибка при удалении записи: {e}")

    def handle_edit_button(self):
        selected_row = self.table_widget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(
                self, "Ошибка", "Пожалуйста, выберите запись для редактирования.")
            return

        record_id_item = self.table_widget.item(selected_row, 0)
        record_id = record_id_item.data(Qt.ItemDataRole.UserRole)
        if not record_id:
            QMessageBox.warning(
                self, "Ошибка", "Невозможно получить идентификатор записи.")
            return

        selected_item = self.list_widget.currentItem()
        if selected_item is not None:
            selected_item_text = selected_item.text()
            if selected_item_text == "Ученики":
                self.edit_student(record_id)
            elif selected_item_text == "Преподаватели":
                self.edit_teacher(record_id)
            elif selected_item_text == "Направления":
                self.edit_direction(record_id)
            elif selected_item_text == "Группы":
                self.edit_group(record_id)
            elif selected_item_text == "Помещения":
                self.edit_room(record_id)
        self.update_content()

    def edit_student(self, student_id):
        query = """
            SELECT p.person_name, p.person_surname, p.person_patron, s.birth_date 
            FROM students s
            JOIN persons p ON s.student_id = p.person_id
            WHERE s.student_id = %s
        """
        record = self.db.fetch_one(query, (student_id,))
        if not record:
            QMessageBox.critical(self, "Ошибка", "Данные ученика не найдены.")
            return

        # Создаём форму редактирования
        edit_student_form = AddStudentForm(
            self.company_id, mode='edit', student_id=student_id)
        edit_student_form.fields["Имя"].setText(record[0])
        edit_student_form.fields["Фамилия"].setText(record[1])
        edit_student_form.fields["Отчество"].setText(record[2])

        # Проверяем и преобразуем дату рождения
        from datetime import date
        birth_date = record[3]  # record[3] содержит дату
        if isinstance(birth_date, date):  # Если это объект datetime.date
            birth_date_str = birth_date.strftime(
                "%Y-%m-%d")  # Преобразуем в строку
        else:
            birth_date_str = birth_date  # Если это уже строка

        # Преобразуем строку в QDate
        edit_student_form.date_of_birth.setDate(
            QDate.fromString(birth_date_str, "yyyy-MM-dd"))

        # Загрузка групп студента
        groups_query = """
            SELECT g.group_number 
            FROM student_group sg
            JOIN groupss g ON sg.group_id = g.group_id
            WHERE sg.student_id = %s
        """
        groups = self.db.fetch_all(groups_query, (student_id,))
        edit_student_form.selected_groups = [group[0] for group in groups]
        edit_student_form.group_combo.setText(
            ", ".join(edit_student_form.selected_groups))

        # Сохранение изменений
        edit_student_form.student_added.connect(self.load_students)
        if edit_student_form.exec():
            QMessageBox.information(
                self, "Успех", "Данные ученика успешно обновлены.")

    # В методе `edit_teacher`:
    def edit_teacher(self, teacher_id):
        # Извлечение данных преподавателя
        query = """
            SELECT p.person_name, p.person_surname, p.person_patron, t.teacher_login, t.teacher_password, d.direction_id
            FROM teachers t
            JOIN persons p ON t.teacher_id = p.person_id
            JOIN directions d ON t.direction_id = d.direction_id
            WHERE t.teacher_id = %s
        """
        record = self.db.fetch_one(query, (teacher_id,))
        if not record:
            QMessageBox.critical(self, "Ошибка", "Данные преподавателя не найдены.")
            return

        # Создание формы редактирования
        edit_teacher_form = AddTeacherForm(self.company_id, mode='edit', teacher_id=teacher_id)
        edit_teacher_form.fields["Имя"].setText(record[0])
        edit_teacher_form.fields["Фамилия"].setText(record[1])
        edit_teacher_form.fields["Отчество"].setText(record[2])
        edit_teacher_form.fields["Логин"].setText(record[3])
        edit_teacher_form.fields["Пароль"].setText(record[4])

        # Установка направления
        for i in range(edit_teacher_form.direction_combo.count()):
            if edit_teacher_form.direction_combo.itemData(i) == record[5]:
                edit_teacher_form.direction_combo.setCurrentIndex(i)
                break

        # Сохранение изменений
        edit_teacher_form.teacher_added.connect(self.load_teachers)
        if edit_teacher_form.exec():
            QMessageBox.information(self, "Успех", "Данные преподавателя успешно обновлены.")

    def edit_direction(self, direction_id):
        query = """
            SELECT direction_name, direction_description 
            FROM directions 
            WHERE direction_id = %s
        """
        record = self.db.fetch_one(query, (direction_id,))
        if not record:
            QMessageBox.critical(self, "Ошибка", "Данные направления не найдены.")
            return

        # Создаем форму редактирования
        edit_direction_form = AddDirectionForm(self.company_id, mode='edit', direction_id=direction_id)
        edit_direction_form.name_input.setText(record[0])
        edit_direction_form.description_input.setPlainText(record[1])

        # Сохранение изменений
        edit_direction_form.direction_added.connect(self.load_directions)
        if edit_direction_form.exec():
            QMessageBox.information(self, "Успех", "Данные направления успешно обновлены.")

    def edit_group(self, group_id):
        query = """
            SELECT group_number, lower_age_limit, upper_age_limit, classes_duration, teacher_id
            FROM groupss
            WHERE group_id = %s
        """
        record = self.db.fetch_one(query, (group_id,))
        if not record:
            QMessageBox.critical(self, "Ошибка", "Данные группы не найдены.")
            return

        # Создаем форму редактирования
        edit_group_form = AddGroupForm(self.company_id, mode='edit', group_id=group_id)
        edit_group_form.group_number_input.setText(record[0])
        edit_group_form.lower_age_input.setText(str(record[1]))
        edit_group_form.upper_age_input.setText(str(record[2]))

        # Преобразуем timedelta в строку "чч:мм"
        duration_timedelta = record[3]
        total_seconds = int(duration_timedelta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        duration_str = f"{hours:02}:{minutes:02}"

        # Устанавливаем значение в поле duration_input
        edit_group_form.duration_input.setText(duration_str)

        # Установка преподавателя
        teacher_index = edit_group_form.teacher_combo.findData(record[4])  # teacher_id
        if teacher_index != -1:
            edit_group_form.teacher_combo.setCurrentIndex(teacher_index)
        else:
            edit_group_form.teacher_combo.setCurrentIndex(-1)  # Устанавливаем на -1, если преподаватель не найден

        # Сохранение изменений
        edit_group_form.group_added.connect(self.load_groups)
        if edit_group_form.exec():
            QMessageBox.information(self, "Успех", "Данные группы успешно обновлены.")

    def edit_room(self, room_id):
        query = """
            SELECT room_number, room_description 
            FROM rooms 
            WHERE room_id = %s
        """
        record = self.db.fetch_one(query, (room_id,))
        if not record:
            QMessageBox.critical(self, "Ошибка", "Данные помещения не найдены.")
            return

        # Создаем форму редактирования
        edit_room_form = AddRoomForm(self.company_id, mode='edit', room_id=room_id)
        edit_room_form.number_input.setText(record[0])
        edit_room_form.description_input.setPlainText(record[1])

        # Сохранение изменений
        edit_room_form.room_added.connect(self.load_rooms)
        if edit_room_form.exec():
            QMessageBox.information(self, "Успех", "Данные помещения успешно обновлены.")