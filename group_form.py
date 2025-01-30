from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from database import Database


class AddGroupForm(QDialog):
    group_added = pyqtSignal()  # Сигнал для уведомления об успешном добавлении группы

    def __init__(self, company_id, mode="add", group_id=None):
        super().__init__()
        self.company_id = company_id
        self.mode = mode
        self.group_id = group_id
        self.setWindowTitle("Добавление группы" if mode == "add" else "Редактирование группы")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        # Заголовок "Группа"
        title_label = QLabel("Группа")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-family: Impact; margin: 10px 0;")
        layout.addWidget(title_label)

        # Поле "Направление"
        direction_layout = QHBoxLayout()
        direction_label = QLabel("Направление")
        direction_label.setFixedWidth(150)
        direction_label.setStyleSheet("font-family: Impact; font-size: 20px;")
        self.direction_combo = QComboBox()
        self.direction_combo.setStyleSheet("font-family: Impact; font-size: 18px;")
        self.direction_combo.currentIndexChanged.connect(self.direction_selected)  # Обновляем преподавателей
        self.load_directions()
        direction_layout.addWidget(direction_label)
        direction_layout.addWidget(self.direction_combo)
        layout.addLayout(direction_layout)

        # Поле "Номер группы"
        group_number_layout = QHBoxLayout()
        group_number_label = QLabel("Номер группы")
        group_number_label.setFixedWidth(150)
        group_number_label.setStyleSheet("font-family: Impact; font-size: 20px;")
        self.group_number_input = QLineEdit()
        self.group_number_input.setStyleSheet("font-family: Impact; font-size: 18px;")
        group_number_layout.addWidget(group_number_label)
        group_number_layout.addWidget(self.group_number_input)
        layout.addLayout(group_number_layout)

        # Поле "Возрастной диапазон"
        age_range_layout = QHBoxLayout()
        age_range_label = QLabel("Возрастной\nдиапазон")
        age_range_label.setFixedWidth(150)
        age_range_label.setStyleSheet("font-family: Impact; font-size: 20px;")
        self.lower_age_input = QLineEdit()
        self.lower_age_input.setStyleSheet("font-family: Impact; font-size: 18px;")
        self.upper_age_input = QLineEdit()
        self.upper_age_input.setStyleSheet("font-family: Impact; font-size: 18px;")
        age_range_layout.addWidget(age_range_label)
        label_from = QLabel("От")
        label_from.setStyleSheet("font-family: Impact; font-size: 20px;")
        age_range_layout.addWidget(label_from)
        age_range_layout.addWidget(self.lower_age_input)
        label_to = QLabel("До")
        label_to.setStyleSheet("font-family: Impact; font-size: 20px;")
        age_range_layout.addWidget(label_to)
        age_range_layout.addWidget(self.upper_age_input)
        layout.addLayout(age_range_layout)

        # Поле "Длительность занятия"
        duration_layout = QHBoxLayout()
        duration_label = QLabel("Длительность\n(чч:мм)")
        duration_label.setFixedWidth(150)
        duration_label.setStyleSheet("font-family: Impact; font-size: 20px;")
        self.duration_input = QLineEdit()
        self.duration_input.setPlaceholderText("чч:мм")
        self.duration_input.setStyleSheet("font-family: Impact; font-size: 18px;")
        self.duration_input.textEdited.connect(self.format_duration_input)  # Автоматическое форматирование
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_input)
        layout.addLayout(duration_layout)

        # Поле "Преподаватель"
        teacher_layout = QHBoxLayout()
        teacher_label = QLabel("Преподаватель")
        teacher_label.setFixedWidth(150)
        teacher_label.setStyleSheet("font-family: Impact; font-size: 20px;")
        self.teacher_combo = QComboBox()
        self.teacher_combo.setStyleSheet("font-family: Impact; font-size: 18px;")
        teacher_layout.addWidget(teacher_label)
        teacher_layout.addWidget(self.teacher_combo)
        layout.addLayout(teacher_layout)

        # Добавляем вертикальный спейсер
        vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(vertical_spacer)

        # Кнопки "Сохранить" и "Отменить"
        button_layout = QHBoxLayout()

        if self.mode == "add":
            self.delete_button = QPushButton("Отмена")
            self.delete_button.clicked.connect(self.reject)
        elif self.mode == "edit":
            self.delete_button = QPushButton("Удалить")
            self.delete_button.clicked.connect(self.delete_group)

        self.delete_button.setStyleSheet("font-family: Impact; font-size: 20px;")
        button_layout.addWidget(self.delete_button)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_group)
        self.save_button.setStyleSheet("font-family: Impact; font-size: 20px;")
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        if self.mode == "edit" and self.group_id is not None:
            self.load_group_data()
        else:
            self.load_teachers()  # Загружаем всех преподавателей при первой инициализации

    def load_directions(self, selected_direction_id=None):
        """Загружает список направлений из базы данных и выбирает текущее при редактировании."""
        db = Database()
        query = "SELECT direction_id, direction_name FROM directions WHERE company_id = %s"
        records = db.fetch_all(query, (self.company_id,))

        self.direction_combo.clear()
        self.direction_combo.addItem("", None)  # Пустой элемент (если создаем новую группу)

        for direction_id, direction_name in records:
            self.direction_combo.addItem(direction_name, direction_id)  # Добавляем данные

        # Если редактирование — выбираем направление
        if selected_direction_id is not None:
            index = self.direction_combo.findData(selected_direction_id)
            if index != -1:
                self.direction_combo.setCurrentIndex(index)
                self.load_teachers(selected_direction_id)  # Авто-загрузка преподавателей

    def direction_selected(self):

        selected_direction_id = self.direction_combo.currentData()
        self.load_teachers(selected_direction_id)

    def load_teachers(self, selected_direction_id=None, selected_teacher_id=None):
        """Загружает список преподавателей, соответствующих направлению."""
        if not hasattr(self, 'teacher_combo'):
            return

        self.teacher_combo.clear()

        if selected_direction_id is None:
            selected_direction_id = self.direction_combo.currentData()  # Получаем текущее значение

        if selected_direction_id is None:
            return

        db = Database()
        query = """
            SELECT t.teacher_id, CONCAT(p.person_surname, ' ', p.person_name)
            FROM teachers t
            JOIN persons p ON t.teacher_id = p.person_id
            WHERE p.company_id = %s AND t.direction_id = %s
        """
        records = db.fetch_all(query, (self.company_id, selected_direction_id))

        for teacher_id, teacher_name in records:
            self.teacher_combo.addItem(teacher_name, teacher_id)

        if selected_teacher_id is not None:
            index = self.teacher_combo.findData(selected_teacher_id)
            if index != -1:
                self.teacher_combo.setCurrentIndex(index)

    def load_group_data(self):
        """Загружает данные группы для редактирования."""
        db = Database()
        query = """
            SELECT direction_id, group_number, lower_age_limit, upper_age_limit, classes_duration, teacher_id
            FROM groupss
            WHERE group_id = %s
        """
        record = db.fetch_one(query, (self.group_id,))

        if record:
            direction_id, group_number, lower_age, upper_age, duration, teacher_id = record

            self.group_number_input.setText(group_number)  # Заполняем номер группы
            self.lower_age_input.setText(str(lower_age))  # Возрастные пределы
            self.upper_age_input.setText(str(upper_age))
            self.duration_input.setText(str(duration))  # Длительность

            # Загружаем направления и преподавателей, подставляя их ID
            self.load_directions(selected_direction_id=direction_id)
            self.load_teachers(selected_direction_id=direction_id, selected_teacher_id=teacher_id)
        else:
            QMessageBox.warning(self, "Ошибка", "Данные группы не найдены.")
            self.reject()

    def save_group(self):
        """Сохраняет данные группы в базу данных."""
        direction_id = self.direction_combo.currentData()
        group_number = self.group_number_input.text()
        lower_age = self.lower_age_input.text()
        upper_age = self.upper_age_input.text()
        duration = self.duration_input.text()
        teacher_id = self.teacher_combo.currentData()

        # Проверка данных
        if not group_number or not lower_age or not upper_age or not duration or not teacher_id:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены.")
            return

        try:
            lower_age = int(lower_age)
            upper_age = int(upper_age)
            hours, minutes = map(int, duration.split(":"))
            if not (0 <= hours < 24 and 0 <= minutes < 60):
                raise ValueError
            duration = f"{hours:02}:{minutes:02}:00"
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверный формат времени (должно быть чч:мм).")
            return

        if lower_age > upper_age:
            QMessageBox.warning(self, "Ошибка", "Нижний возрастной предел не может быть больше верхнего.")
            return

        db = Database()
        if self.mode == "add":
            query = """
                INSERT INTO groupss (direction_id, group_number, lower_age_limit, upper_age_limit, classes_duration, teacher_id, company_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (direction_id, group_number, lower_age, upper_age, duration, teacher_id, self.company_id)
            db.execute_query(query, params)
        elif self.mode == "edit":
            query = """
                UPDATE groupss
                SET direction_id = %s, group_number = %s, lower_age_limit = %s, upper_age_limit = %s, classes_duration = %s, teacher_id = %s
                WHERE group_id = %s
            """
            params = (direction_id, group_number, lower_age, upper_age, duration, teacher_id, self.group_id)
            db.execute_query(query, params)

        QMessageBox.information(self, "Успех", "Группа успешно добавлена/обновлена.")
        self.group_added.emit()  # Уведомляем, что группа добавлена
        self.accept()  # Закрываем форму

    def delete_group(self):
        """Удаляет группу из базы данных."""
        confirmation = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить эту группу?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            db = Database()
            try:
                query = "DELETE FROM groupss WHERE group_id = %s"
                db.execute_query(query, (self.group_id,))
                QMessageBox.information(self, "Успех", "Группа успешно удалена.")
                self.accept()  # Закрываем форму после успешного удаления
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить группу: {e}")

    def format_duration_input(self, text):
        """Форматирует поле длительности, оставляя двоеточие всегда видимым."""
        # Убираем всё, кроме чисел, из текста
        clean_text = ''.join(filter(lambda x: x.isdigit(), text))

        # Убираем уже установленное двоеточие
        if len(clean_text) > 4:  # Ограничиваем ввод до 4 цифр
            clean_text = clean_text[:4]

        # Добавляем двоеточие автоматически
        if len(clean_text) >= 2:
            formatted_text = clean_text[:2] + ":" + clean_text[2:]
        else:
            formatted_text = clean_text  # Если меньше двух цифр, не добавляем двоеточие

        self.duration_input.setText(formatted_text)
        # Перемещаем курсор в конец
        self.duration_input.setCursorPosition(len(formatted_text))