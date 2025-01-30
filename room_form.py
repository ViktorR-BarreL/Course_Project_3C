from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from database import Database  # Import your Database class


class AddRoomForm(QDialog):
    room_added = pyqtSignal()

    def __init__(self, company_id, mode="add", room_id=None):
        super().__init__()
        self.company_id = company_id  # Store the company ID
        self.mode = mode
        self.room_id = room_id  # ID of the room for editing
        self.setWindowTitle("Добавление помещения" if mode == "add" else "Редактирование помещения")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        title_label = QLabel("Помещение")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-family: Impact; font-size: 24px;")
        layout.addWidget(title_label)

        # Поле "Номер"
        number_layout = QHBoxLayout()
        number_label = QLabel("Номер")
        number_label.setFixedWidth(100)
        number_label.setStyleSheet("font-family: Impact; font-size: 20px;")
        self.number_input = QLineEdit()
        self.number_input.setStyleSheet("font-family: Impact; font-size: 18px;")
        number_layout.addWidget(number_label)
        number_layout.addWidget(self.number_input)
        layout.addLayout(number_layout)

        # Поле "Описание"
        description_label = QLabel("Описание")
        description_label.setStyleSheet("font-family: Impact; font-size: 20px;")
        layout.addWidget(description_label)
        self.description_input = QTextEdit()
        self.description_input.setStyleSheet("font-family: Impact; font-size: 18px;")
        layout.addWidget(self.description_input)

        # Кнопки "Сохранить" и "Удалить/Отменить"
        button_layout = QHBoxLayout()
        if self.mode == "add":
            self.delete_button = QPushButton("Отмена")
            self.delete_button.clicked.connect(self.reject)
        elif self.mode == "edit":
            self.delete_button = QPushButton("Удалить")
            self.delete_button.clicked.connect(self.delete_room)

        # Установка стиля для кнопок
        self.delete_button.setStyleSheet("font-family: Impact; font-size: 20px;")
        button_layout.addWidget(self.delete_button)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_room)
        self.save_button.setStyleSheet("font-family: Impact; font-size: 20px;")
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        if self.mode == "edit" and self.room_id is not None:
            self.load_room_data()

    def load_room_data(self):
        """Загружает данные помещения для редактирования."""
        db = Database()
        query = "SELECT room_number, room_description FROM rooms WHERE room_id = %s"
        record = db.fetch_one(query, (self.room_id,))

        if record:
            self.number_input.setText(record[0])
            self.description_input.setPlainText(record[1])
        else:
            QMessageBox.warning(self, "Ошибка", "Данные помещения не найдены.")
            self.reject()

    def save_room(self):
        room_number = self.number_input.text()
        room_description = self.description_input.toPlainText()

        # Validate that room number is provided
        if not room_number:
            QMessageBox.warning(self, "Ошибка", "Номер помещения не может быть пустым.")
            return

        db = Database()

        if self.mode == "add":
            # SQL query to insert data into the rooms table
            query = "INSERT INTO rooms (room_number, room_description, company_id) VALUES (%s, %s, %s)"
            params = (room_number, room_description, self.company_id)
            db.execute_query(query, params)
        elif self.mode == "edit":
            # SQL query to update data in the rooms table
            query = "UPDATE rooms SET room_number = %s, room_description = %s WHERE room_id = %s"
            params = (room_number, room_description, self.room_id)
            db.execute_query(query, params)

        # Emit the signal to notify that the room has been added
        self.room_added.emit()  # This triggers the connected function

        self.accept()  # Close the form

    def delete_room(self):
        """Удаляет помещение из базы данных."""
        if self.room_id is None:
            QMessageBox.warning(self, "Ошибка", "Не указан ID помещения для удаления.")
            return

        confirmation = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить это помещение?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            db = Database()
            try:
                query = "DELETE FROM rooms WHERE room_id = %s"
                db.execute_query(query, (self.room_id,))
                QMessageBox.information(self, "Успех", "Помещение успешно удалено.")
                self.accept()  # Закрываем форму после успешного удаления
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить помещение: {e}")
