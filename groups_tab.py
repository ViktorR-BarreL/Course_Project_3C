from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QTableWidget,
    QTableWidgetItem, QSizePolicy, QSpacerItem, QListWidgetItem, QMessageBox, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database import Database
from student_form import AddStudentForm  # Импортируем форму для добавления нового ученика


class GroupsTab(QWidget):
    def __init__(self, company_id, is_admin, teacher_id=None):
        super().__init__()
        self.company_id = company_id
        self.teacher_id = teacher_id
        self.is_admin = is_admin
        self.db = Database()

        # Основной макет
        main_layout = QHBoxLayout(self)

        # Левый виджет: список групп
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)

        self.groups_label = QLabel("Список групп")
        self.groups_label.setStyleSheet("font-size: 24px; font-family: Impact;")
        self.left_layout.addWidget(self.groups_label)

        self.groups_list = QTableWidget()
        self.groups_list.setColumnCount(2)
        self.groups_list.setHorizontalHeaderLabels(["Номер группы", "Возрастной\nдиапазон"])
        self.groups_list.horizontalHeader().setStretchLastSection(True)
        self.groups_list.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Отключить редактирование
        self.groups_list.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # Выбор строк
        self.groups_list.cellClicked.connect(self.load_group_details)
        self.groups_list.setStyleSheet("font-family: Impact; font-size: 20px;")  # Установка шрифта для таблицы
        self.left_layout.addWidget(self.groups_list)

        main_layout.addWidget(self.left_widget, 2)

        # Правый виджет: информация о группе
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)

        header_layout = QHBoxLayout()
        self.group_number_label = QLabel("Список группы <Номер группы>")
        self.group_number_label.setStyleSheet("font-size: 24px; font-family: Impact;")
        header_layout.addWidget(self.group_number_label)

        if is_admin:
            self.add_student_button = QPushButton("Добавить ученика")
            self.add_student_button.clicked.connect(self.show_add_student_dialog)
            self.add_student_button.setStyleSheet("font-family: Impact; font-size: 20px;")
            header_layout.addWidget(self.add_student_button)

        self.right_layout.addLayout(header_layout)

        self.teacher_label = QLabel("Преподаватель: <ФИО>")
        self.teacher_label.setStyleSheet("font-family: Impact; font-size: 20px;")
        self.right_layout.addWidget(self.teacher_label)

        self.students_list = QListWidget()
        self.students_list.setStyleSheet("font-family: Impact; font-size: 18px;")
        self.right_layout.addWidget(self.students_list)

        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.right_layout.addItem(spacer)

        main_layout.addWidget(self.right_widget, 3)

        self.setLayout(main_layout)
        self.load_groups()

    def load_groups(self):
        """Загружает список групп, фильтруя по teacher_id если админ."""
        self.db = Database()  # Пересоздание подключения
        query = """
            SELECT group_number, 
                   CONCAT(lower_age_limit, '-', upper_age_limit) AS age_range
            FROM groupss
            WHERE company_id = %s
        """
        params = [self.company_id]
        if not self.is_admin and self.teacher_id:
            query += " AND teacher_id = %s"
            params.append(self.teacher_id)

        records = self.db.fetch_all(query, tuple(params))
        self.groups_list.setRowCount(0)  # Очищаем перед добавлением новых данных
        self.groups_list.setRowCount(len(records))
        for row, (group_number, age_range) in enumerate(records):
            self.groups_list.setItem(row, 0, QTableWidgetItem(str(group_number)))
            self.groups_list.setItem(row, 1, QTableWidgetItem(age_range))
        self.groups_list.resizeColumnsToContents()

        # Установка фиксированной ширины колонок
        self.groups_list.setColumnWidth(0, 200)

        if not records:
            QMessageBox.warning(self, "Внимание", "Группы не найдены.")

    def load_group_details(self, row, column):
        """Загружает детали выбранной группы."""
        self.current_group_number = self.groups_list.item(row, 0).text()  # Сохраняем текущий номер группы
        self.group_number_label.setText(f"Список группы {self.current_group_number}")

        # Загружаем данные о преподавателе
        query_teacher = """
            SELECT CONCAT(p.person_surname, ' ', p.person_name, ' ', p.person_patron) AS teacher_name
            FROM teachers t
            JOIN persons p ON t.teacher_id = p.person_id
            JOIN groupss g ON t.teacher_id = g.teacher_id
            WHERE g.group_number = %s AND g.company_id = %s
        """
        teacher = self.db.fetch_one(query_teacher, (self.current_group_number, self.company_id))
        self.teacher_label.setText(f"Преподаватель: {teacher[0] if teacher else 'Не назначен'}")

        # Загружаем список учеников
        query_students = """
            SELECT s.student_id, CONCAT(p.person_surname, ' ', p.person_name, ' ', p.person_patron) AS student_name
            FROM student_group sg
            JOIN students s ON sg.student_id = s.student_id
            JOIN persons p ON s.student_id = p.person_id
            WHERE sg.group_id = (
                SELECT group_id
                FROM groupss
                WHERE group_number = %s AND company_id = %s
            )
        """
        students = self.db.fetch_all(query_students, (self.current_group_number, self.company_id))
        self.students_list.clear()

        for student_id, student_name in students:
            self.add_student_to_list(self.is_admin, student_id, student_name)

    def add_student_to_list(self, is_admin, student_id, student_name):
        """Добавляет ученика в список с кнопкой удаления."""
        student_widget = QWidget()
        layout = QHBoxLayout(student_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(student_name)
        layout.addWidget(label)

        # Проверяем, является ли пользователь администратором
        if is_admin:
            delete_button = QPushButton("❌")
            delete_button.setFixedSize(30, 30)
            delete_button.clicked.connect(lambda: self.confirm_remove_student(student_id))
            layout.addWidget(delete_button)
            layout.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignRight)

        student_widget.setLayout(layout)
        list_item = QListWidgetItem()
        list_item.setSizeHint(student_widget.sizeHint())
        self.students_list.addItem(list_item)
        self.students_list.setItemWidget(list_item, student_widget)

    def confirm_remove_student(self, student_id):
        """Подтверждение перед удалением ученика."""
        reply = QMessageBox.question(
            self,
            "Удаление ученика",
            "Вы уверены, что хотите удалить этого ученика из группы?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.remove_student(student_id)

    def remove_student(self, student_id):
        """Удаляет ученика из группы."""
        query = """
            DELETE FROM student_group
            WHERE student_id = %s AND group_id = (
                SELECT group_id
                FROM groupss
                WHERE group_number = %s AND company_id = %s
                LIMIT 1
            )
        """
        try:
            self.db.execute_query(query, (student_id, self.current_group_number, self.company_id))
            self.load_group_details(self.groups_list.currentRow(), 0)  # Обновляем список
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить ученика: {e}")

    def show_add_student_dialog(self):
        """Показывает диалоговое окно для добавления ученика."""
        selected_row = self.groups_list.currentRow()
        if selected_row == -1:  # Если строка не выбрана
            QMessageBox.warning(
                self,
                "Группа не выбрана",
                "Пожалуйста, выберите группу перед добавлением ученика."
            )
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить ученика")

        layout = QVBoxLayout(dialog)

        font = QFont("Impact", 18)

        add_existing_button = QPushButton("Добавить из существующего списка")
        add_existing_button.setFont(font)
        add_existing_button.clicked.connect(lambda: self.add_existing_student(dialog))
        layout.addWidget(add_existing_button)

        create_new_button = QPushButton("Создать нового")
        create_new_button.setFont(font)
        create_new_button.clicked.connect(lambda: self.create_new_student(dialog))
        layout.addWidget(create_new_button)

        cancel_button = QPushButton("Отмена")
        cancel_button.setFont(font)
        cancel_button.clicked.connect(dialog.reject)
        layout.addWidget(cancel_button)

        dialog.setLayout(layout)
        dialog.exec()

    def add_existing_student(self, parent_dialog):
        """Открывает окно выбора существующих учеников."""
        parent_dialog.accept()

        dialog = QDialog(self)
        dialog.setWindowTitle("Выбор ученика из списка")

        layout = QVBoxLayout(dialog)

        students_list_widget = QListWidget()
        available_students = self.load_students_by_age()

        for student_id, student_name in available_students:
            item = QListWidgetItem(student_name)
            item.setData(Qt.ItemDataRole.UserRole, student_id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            students_list_widget.addItem(item)

        layout.addWidget(students_list_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(lambda: self.add_selected_students(dialog, students_list_widget))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)
        dialog.exec()

    def load_students_by_age(self):
        """Загружает список учеников по возрасту."""
        query = """
            SELECT s.student_id, CONCAT(p.person_surname, ' ', p.person_name, ' ', p.person_patron) AS student_name
            FROM students s
            JOIN persons p ON s.student_id = p.person_id
            WHERE NOT EXISTS (
                SELECT 1 FROM student_group sg
                JOIN groupss g ON sg.group_id = g.group_id
                WHERE sg.student_id = s.student_id AND g.group_number = %s AND g.company_id = %s
            )
        """
        return self.db.fetch_all(query, (self.current_group_number, self.company_id))

    def add_selected_students(self, dialog, students_list_widget):
        """Добавляет выбранных учеников в группу."""
        selected_students = []

        for i in range(students_list_widget.count()):
            item = students_list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_students.append(item.data(Qt.ItemDataRole.UserRole))

        for student_id in selected_students:
            query = """
                INSERT INTO student_group (student_id, group_id)
                VALUES (%s, (
                    SELECT group_id FROM groupss WHERE group_number = %s AND company_id = %s
                ))
            """
            self.db.execute_query(query, (student_id, self.current_group_number, self.company_id))

        self.load_group_details(self.groups_list.currentRow(), 0)
        dialog.accept()

    def create_new_student(self, parent_dialog):
        """Открывает форму создания нового ученика."""
        parent_dialog.accept()

        form = AddStudentForm(self.company_id)
        form.student_added.connect(lambda: self.load_group_details(self.groups_list.currentRow(), 0))
        form.exec()
