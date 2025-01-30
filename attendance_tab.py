import time
from datetime import timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QDateEdit, QListWidget, QListWidgetItem, QCheckBox, QPushButton, QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont
from database import Database


class AttendanceTab(QWidget):
    def __init__(self, company_id, is_admin, teacher_id=None):
        super().__init__()
        self.company_id = company_id
        self.teacher_id = teacher_id
        self.is_admin = is_admin
        self.db = Database()

        layout = QVBoxLayout()

        # Установка шрифта Impact
        self.setFont(QFont("Impact", 16))

        # Выпадающий список для выбора номера группы
        self.group_selector = QComboBox()
        self.group_selector.setPlaceholderText("Выберите номер группы")
        self.group_selector.currentIndexChanged.connect(self.load_schedule_times)
        layout.addWidget(QLabel("Номер группы:"))
        layout.addWidget(self.group_selector)

        # Поле для выбора даты
        self.date_selector = QDateEdit()
        self.date_selector.setDisplayFormat("dd.MM.yyyy")
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.dateChanged.connect(self.load_schedule_times)
        layout.addWidget(QLabel("Выберите дату:"))
        layout.addWidget(self.date_selector)

        # Выпадающий список для выбора времени
        self.time_selector = QComboBox()
        self.time_selector.setPlaceholderText("Выберите время")
        self.time_selector.currentIndexChanged.connect(self.load_students)
        layout.addWidget(QLabel("Выберите время:"))
        layout.addWidget(self.time_selector)

        # Список учеников с флажками
        self.student_list = QListWidget()
        layout.addWidget(QLabel("Список учеников:"))
        layout.addWidget(self.student_list)

        # Кнопка для сохранения посещений
        self.save_button = QPushButton("Сохранить посещаемость")
        self.save_button.clicked.connect(self.save_attendance)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def load_groups(self):
        query = """
        SELECT group_id, group_number FROM groupss
        WHERE company_id = %s
        """
        if not self.is_admin:
            query += " AND teacher_id = %s"
            groups = self.db.fetch_all(query, (self.company_id, self.teacher_id))
        else:
            groups = self.db.fetch_all(query, (self.company_id,))

        if not groups:
            QMessageBox.warning(self, "Внимание", "Группы не найдены.")
            return

        self.group_selector.clear()
        for group in groups:
            self.group_selector.addItem(group[1], group[0])

    def load_schedule_times(self):
        group_id = self.group_selector.currentData()
        date = self.date_selector.date().toString("yyyy-MM-dd")

        if not group_id:
            QMessageBox.warning(self, "Ошибка", "Выберите группу.")
            return

        query = """
        SELECT rasp_id, start_time
        FROM rasp
        WHERE group_id = %s AND date = %s
        """
        times = self.db.fetch_all(query, (group_id, date))

        self.time_selector.clear()

        if not times:
            QMessageBox.warning(self, "Внимание", "Расписание для выбранной группы и даты не найдено.")
            return

        for rasp_id, start_time in times:
            if isinstance(start_time, timedelta):
                hours, remainder = divmod(start_time.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                time_str = f"{hours:02}:{minutes:02}"
                self. time_selector.addItem(time_str, rasp_id)
            elif isinstance(start_time, time):
                self.time_selector.addItem(start_time.strftime("%H:%M"), rasp_id)

    def load_students(self):
        group_id = self.group_selector.currentData()
        rasp_id = self.time_selector.currentData()

        if not group_id or not rasp_id:
            return

        query_students = """
        SELECT p.person_id, CONCAT(p.person_surname, ' ', p.person_name, ' ', p.person_patron) AS full_name
        FROM persons p
        JOIN student_group sg ON p.person_id = sg.student_id
        WHERE sg.group_id = %s
        """
        students = self.db.fetch_all(query_students, (group_id,))

        query_attendance = """
        SELECT student_id, attend
        FROM attendance
        WHERE rasp_id = %s
        """
        attendance_data = {row[0]: row[1] for row in self.db.fetch_all(query_attendance, (rasp_id,))}

        self.student_list.clear()
        for idx, student in enumerate(students, start=1):
            student_id = student[0]
            full_name = student[1]

            item = QListWidgetItem()
            container_widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)

            name_label = QLabel(f"{idx}. {full_name}")
            name_label.setFont(QFont("Impact", 16))  # Установка шрифта и размера
            layout.addWidget(name_label)

            checkbox = QCheckBox()
            item.setData(Qt.ItemDataRole.UserRole, student_id)
            layout.addWidget(checkbox)

            container_widget.setLayout(layout)
            self.student_list.addItem(item)
            self.student_list.setItemWidget(item, container_widget)

            if student_id in attendance_data:
                checkbox.setChecked(attendance_data[student_id])

    def save_attendance(self):
        rasp_id = self.time_selector.currentData()

        if not rasp_id:
            QMessageBox.warning(self, "Ошибка", "Не выбрано время занятия.")
            return

        for i in range(self.student_list.count()):
            item = self.student_list.item(i)
            container_widget = self.student_list.itemWidget(item)
            if container_widget is None:
                continue

            checkbox = container_widget.findChild(QCheckBox)
            if checkbox is None:
                continue

            student_id = item.data(Qt.ItemDataRole.UserRole)
            attend = checkbox.isChecked()

            check_query = """
            SELECT COUNT(*) FROM attendance
            WHERE student_id = %s AND rasp_id = %s
            """
            record_exists = self.db.fetch_one(check_query, (student_id, rasp_id))[0]

            if record_exists:
                update_query = """
                UPDATE attendance
                SET attend = %s
                WHERE student_id = %s AND rasp_id = %s
                """
                self.db.execute_query(update_query, (attend, student_id, rasp_id))
            else:
                insert_query = """
                INSERT INTO attendance (student_id, rasp_id, attend)
                VALUES (%s, %s, %s)
                """
                self.db.execute_query(insert_query, (student_id, rasp_id, attend))

        QMessageBox.information(self, "Успех", "Посещаемость успешно сохранена!")

    def refresh_schedule(self):
        self.db = Database()
        self.load_groups()
        self.group_selector.setCurrentIndex(-1)
        self.date_selector.setDate(QDate.currentDate())
        self.time_selector.clear()
        self.student_list.clear()