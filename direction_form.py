from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from database import Database  # Импортируйте ваш класс Database


class AddDirectionForm(QDialog):
    direction_added = pyqtSignal()

    def __init__(self, company_id, mode="add", direction_id=None):
        super().__init__()
        self.company_id = company_id
        self.mode = mode
        self.direction_id = direction_id

        if self.mode == "add":
            self.setWindowTitle("Добавление направления")
        elif self.mode == "edit":
            self.setWindowTitle("Редактирование направления")

        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        title_label = QLabel("Направление")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-family: Impact;")
        layout.addWidget(title_label)

        name_label = QLabel("Название")
        name_label.setStyleSheet("font-family: Impact; font-size: 20px;")
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setStyleSheet("font-family: Impact; font-size: 18px;")
        layout.addWidget(self.name_input)

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
            self.delete_button.clicked.connect(self.delete_direction)

        self.delete_button.setStyleSheet("font-family: Impact; font-size: 20px;")
        button_layout.addWidget(self.delete_button)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_direction)
        self.save_button.setStyleSheet("font-family: Impact; font-size: 20px;")

        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        if self.mode == "edit" and self.direction_id is not None:
            self.load_direction_data()

    def load_direction_data(self):
        db = Database()
        query = "SELECT direction_name, direction_description FROM directions WHERE direction_id = %s"
        record = db.fetch_one(query, (self.direction_id,))

        if record:
            self.name_input.setText(record[0])
            self.description_input.setPlainText(record[1])
        else:
            QMessageBox.warning(self, "Ошибка", "Данные направления не найдены.")
            self.reject()

    def save_direction(self):
        direction_name = self.name_input.text()
        direction_description = self.description_input.toPlainText()

        if not direction_name:
            QMessageBox.warning(self, "Ошибка", "Название направления не может быть пустым.")
            return

        db = Database()
        if self.mode == "add":
            query = "INSERT INTO directions (direction_name, direction_description, company_id) VALUES (%s, %s, %s)"
            db.execute_query(query, (direction_name, direction_description, self.company_id))
        elif self.mode == "edit":
            query = "UPDATE directions SET direction_name = %s, direction_description = %s WHERE direction_id = %s"
            db.execute_query(query, (direction_name, direction_description, self.direction_id))

        self.direction_added.emit()  # Emit signal to notify that a direction has been added
        self.accept()  # Close the form

    def delete_direction(self):
        confirmation = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить это направление?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            db = Database()
            query = "DELETE FROM directions WHERE direction_id = %s"
            db.execute_query(query, (self.direction_id,))
            QMessageBox.information(self, "Успех", "Направление успешно удалено.")
            self.accept()  # Закрываем форму после успешного удаления