from datetime import timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton, QFrame, QGridLayout,
    QSpacerItem, QSizePolicy, QScrollArea, QDialog, QTimeEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, QLocale, QTime, pyqtSignal

from database import Database


class AddEventDialog(QDialog):
    def __init__(self, rooms, time=None, selected_room=None):
        super().__init__()
        self.setWindowTitle("Добавить/Редактировать событие")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout(self)

        # Поле для выбора времени
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(time if time else QTime.currentTime())
        time_label = QLabel("Выберите время:")
        time_label.setStyleSheet("font-family: Impact; font-size: 20px;")
        layout.addWidget(time_label)
        layout.addWidget(self.time_edit)

        # Устанавливаем стиль для поля выбора времени
        self.time_edit.setStyleSheet("font-family: Impact; font-size: 18px;")

        # Поле для выбора кабинета
        self.room_selector = QComboBox()
        self.room_selector.addItems(rooms)
        if selected_room:
            index = self.room_selector.findText(selected_room)
            if index >= 0:
                self.room_selector.setCurrentIndex(index)
        room_label = QLabel("Выберите кабинет:")
        room_label.setStyleSheet("font-family: Impact; font-size: 20px;")
        layout.addWidget(room_label)
        layout.addWidget(self.room_selector)

        # Устанавливаем стиль для комбобокса выбора кабинета
        self.room_selector.setStyleSheet("font-family: Impact; font-size: 18px;")

        # Кнопки сохранения и отмены
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.save_button)

        # Устанавливаем стиль для кнопки "Сохранить"
        self.save_button.setStyleSheet("font-family: Impact; font-size: 20px;")

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        # Устанавливаем стиль для кнопки "Отмена"
        self.cancel_button.setStyleSheet("font-family: Impact; font-size: 20px;")

        layout.addLayout(button_layout)

    def get_event_data(self):
        return self.time_edit.time().toString("HH:mm"), self.room_selector.currentText()


class ScheduleTab(QWidget):
    event_added = pyqtSignal()

    def __init__(self, company_id, is_admin, teacher_id=None):
        super().__init__()
        self.company_id = company_id
        self.teacher_id = teacher_id
        self.is_admin = is_admin
        self.current_date = QDate.currentDate()

        self.database = Database()
        self.rooms = []
        self.groups = []
        self.init_ui()

    def init_ui(self):
        locale = QLocale(QLocale.Language.Russian, QLocale.Country.Russia)
        QLocale.setDefault(locale)

        main_layout = QVBoxLayout(self)

        self.top_widget = QWidget()
        top_layout = QHBoxLayout(self.top_widget)

        self.group_selector = QComboBox()
        self.group_selector.setFixedWidth(200)
        self.group_selector.currentIndexChanged.connect(self.update_schedule)
        top_layout.addWidget(self.group_selector)

        # Устанавливаем стиль для комбобокса выбора группы
        self.group_selector.setStyleSheet("font-family: Impact; font-size: 18px;")

        self.prev_week_button = QPushButton("←")
        self.prev_week_button.setFixedSize(40, 40)
        self.prev_week_button.clicked.connect(self.previous_week)
        top_layout.addWidget(self.prev_week_button)

        # Устанавливаем стиль для кнопки "Предыдущая неделя"
        self.prev_week_button.setStyleSheet("font-family: Impact; font-size: 18px;")

        self.week_label = QLabel(self.get_current_week())
        self.week_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(self.week_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Устанавливаем стиль для метки недели
        self.week_label.setStyleSheet("font-family: Impact; font-size: 20px;")

        self.next_week_button = QPushButton("→")
        self.next_week_button.setFixedSize(40, 40)
        self.next_week_button.clicked.connect(self.next_week)
        top_layout.addWidget(self.next_week_button)

        # Устанавливаем стиль для кнопки "Следующая неделя"
        self.next_week_button.setStyleSheet("font-family: Impact; font-size: 18px;")

        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        top_layout.addItem(spacer)

        main_layout.addWidget(self.top_widget)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)

        self.schedule_widget = QFrame()
        self.schedule_layout = QGridLayout(self.schedule_widget)

        self.day_widgets = []
        self.scroll_layout.addWidget(self.schedule_widget)
        scroll_area.setWidget(scroll_content)

        main_layout.addWidget(scroll_area)

        self.load_data()
        self.update_schedule()

        self.current_date = QDate.currentDate()
        self.week_label.setText(self.get_current_week())

        self.setLayout(main_layout)

    def load_data(self):
        self.database = Database()
        try:
            rooms_query = "SELECT room_id, room_number FROM rooms WHERE company_id = %s"
            self.rooms = [f"{row[0]} ({row[1]})" for row in self.database.fetch_all(rooms_query, (self.company_id,))]

            groups_query = "SELECT group_id, group_number FROM groupss WHERE company_id = %s"
            params = [self.company_id]
            if not self.is_admin and self.teacher_id:
                groups_query += " AND teacher_id = %s"
                params.append(self.teacher_id)

            self.groups = [f"{row[0]} ({row[1]})" for row in self.database.fetch_all(groups_query, tuple(params))]

            self.group_selector.addItems(self.groups)

            if self.groups:
                self.group_selector.setCurrentIndex(0)
                self.update_schedule()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки данных", f"Не удалось загрузить данные: {e}")

    def create_day_widget(self, day_name, day_date):
        day_frame = QFrame()
        day_layout = QVBoxLayout(day_frame)
        day_frame.setFrameShape(QFrame.Shape.Box)
        day_frame.setFixedWidth(150)

        locale = QLocale(QLocale.Language.Russian, QLocale.Country.Russia)
        formatted_date = locale.toString(day_date, 'd MMMM').capitalize()
        day_header = QLabel(f"{day_name}\n{formatted_date}")
        day_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        day_layout.addWidget(day_header)

        if self.is_admin:
            button_layout = QHBoxLayout()

            add_button = QPushButton("➕")
            add_button.setFixedSize(30, 30)
            add_button.clicked.connect(lambda: self.add_event(day_layout, day_date))
            button_layout.addWidget(add_button)

            delete_button = QPushButton("❌")
            delete_button.setFixedSize(30, 30)
            delete_button.clicked.connect(lambda: self.delete_selected_event(day_date))
            button_layout.addWidget(delete_button)

            edit_button = QPushButton("✏️")
            edit_button.setFixedSize(30, 30)
            edit_button.clicked.connect(lambda: self.edit_selected_event(day_date))
            button_layout.addWidget(edit_button)

            day_layout.addLayout(button_layout)

        spacer_item = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        day_layout.addItem(spacer_item)

        # Устанавливаем стиль для всех элементов в day_widget
        day_frame.setStyleSheet("font-family: Impact; font-size: 20px;")
        return day_frame

    def delete_selected_event(self, day_date):
        selected_event = self.get_selected_event()
        if not selected_event:
            QMessageBox.warning(self, "Удаление события", "Выберите событие для удаления.")
            return

        event_id = selected_event.property("event_id")
        reply = QMessageBox.question(
            self,
            "Удаление события",
            "Вы уверены, что хотите удалить это событие?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                query = "DELETE FROM rasp WHERE rasp_id = %s"
                self.database.execute_query(query, (event_id,))
                QMessageBox.information(self, "Удаление", "Событие успешно удалено.")
                self.update_schedule()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить событие: {e}")

    def edit_selected_event(self, day_date):
        selected_event = self.get_selected_event()
        if not selected_event:
            QMessageBox.warning(self, "Редактирование события", "Выберите событие для редактирования.")
            return

        event_id = selected_event.property("event_id")
        self.edit_event(event_id)

    def get_selected_event(self):
        for day_widget in self.day_widgets:
            for i in range(day_widget.layout().count()):
                widget = day_widget.layout().itemAt(i).widget()
                if widget and widget.property("selected"):
                    return widget
        return None

    def update_schedule(self):
        for i in reversed(range(self.schedule_layout.count())):
            self.schedule_layout.itemAt(i).widget().deleteLater()

        if not self.groups:
            return

        group_id = int(self.group_selector.currentText().split(' ')[0])

        self.day_widgets = []
        start_of_week = self.current_date.addDays(-(self.current_date.dayOfWeek() - 1))
        for i, day_name in enumerate(
                ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]):
            day_date = start_of_week.addDays(i)
            day_widget = self.create_day_widget(day_name, day_date)

            try:
                self.db = Database()
                query = """
                       SELECT rasp_id, start_time, room_id
                       FROM rasp
                       WHERE company_id = %s AND group_id = %s AND date = %s
                   """
                events = self.db.fetch_all(query, (self.company_id, group_id, day_date.toString("yyyy-MM-dd")))

                events = sorted(events, key=lambda x: QTime.fromString(str(x[1]), "H:mm"))

                for event_id, start_time, room_id in events:
                    room_query = "SELECT room_number FROM rooms WHERE room_id = %s"
                    room_number = self.database.fetch_one(room_query, (room_id,))[0]
                    event_label = QLabel(f"{start_time} - {room_number}")
                    event_label.setStyleSheet("padding: 5px; border: 1px solid gray; text-align: center;")
                    event_label.setProperty("event_id", event_id)
                    event_label.setProperty("selected", False)
                    event_label.mousePressEvent = lambda event, el=event_label: self.select_event(el)
                    day_widget.layout().insertWidget(day_widget.layout().count() - 1, event_label)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить события: {e}")

            self.schedule_layout.addWidget(day_widget, 0, i)
            self.day_widgets.append(day_widget)

        self.schedule_layout.setHorizontalSpacing(10)

        self.week_label.setText(self.get_current_week())

    def select_event(self, event_label):
        for day_widget in self.day_widgets:
            for i in range(day_widget.layout().count()):
                widget = day_widget.layout().itemAt(i).widget()
                if widget:
                    widget.setProperty("selected", False)
                    widget.setStyleSheet("padding: 5px; border: 1px solid gray; text-align: center;")

        event_label.setProperty("selected", True)
        event_label.setStyleSheet("padding: 5px; border: 2px solid blue; text-align: center;")

    def get_current_week(self):
        start_of_week = self.current_date.addDays(-(self.current_date.dayOfWeek() - 1))
        end_of_week = start_of_week.addDays(6)
        return f"{start_of_week.toString('dd.MM.yyyy')} - {end_of_week.toString('dd.MM.yyyy')}"

    def previous_week(self):
        self.current_date = self.current_date.addDays(-7)
        self.update_schedule()

    def next_week(self):
        self.current_date = self.current_date.addDays(7)
        self.update_schedule()

    def add_event(self, day_layout, day_date):
        dialog = AddEventDialog(self.rooms)
        if dialog.exec():
            time, room = dialog.get_event_data()

            try:
                room_id = int(room.split(' ')[0])
                group_id = int(self.group_selector.currentText().split(' ')[0])

                query = """
                    INSERT INTO rasp (company_id, date, start_time, room_id, group_id)
                    VALUES (%s, %s, %s, %s, %s)
                """
                self.database.execute_query(
                    query,
                    (self.company_id, day_date.toString("yyyy-MM-dd"), time, room_id, group_id)
                )

                self.update_schedule()
                self.event_added.emit()

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить событие: {e}")

    def edit_event(self, event_id):
        try:
            query = "SELECT start_time, room_id FROM rasp WHERE rasp_id = %s"
            event_data = self.database.fetch_one(query, (event_id,))
            if not event_data:
                QMessageBox.critical(self, "Ошибка", "Событие не найдено.")
                return

            start_time, room_id = event_data

            if isinstance(start_time, timedelta):
                total_seconds = start_time.total_seconds()
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                start_time_str = f"{hours:02}:{minutes:02}"
            else:
                start_time_str = start_time

            room_query = "SELECT room_number FROM rooms WHERE room_id = %s"
            room_number = self.database.fetch_one(room_query, (room_id,))[0]
            room_display = f"{room_id} ({room_number})"

            dialog = AddEventDialog(self.rooms, QTime.fromString(start_time_str, "HH:mm"), room_display)

            if dialog.exec():
                new_time, new_room = dialog.get_event_data()
                new_room_id = int(new_room.split(' ')[0])

                update_query = """
                    UPDATE rasp
                    SET start_time = %s, room_id = %s
                    WHERE rasp_id = %s
                """
                self.database.execute_query(update_query, (new_time, new_room_id, event_id))
                QMessageBox.information(self, "Обновление", "Событие успешно обновлено.")
                self.update_schedule()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось редактировать событие: {e}")