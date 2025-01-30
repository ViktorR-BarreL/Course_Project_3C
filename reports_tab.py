from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QFileDialog,
    QPushButton, QHBoxLayout, QDateEdit, QGridLayout, QMessageBox, QScrollArea
)
from PyQt6.QtCore import QDate
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os
from database import Database  # Импортируйте ваш класс Database


class ReportsTab(QWidget):
    def __init__(self, company_id):
        super().__init__()
        self.company_id = company_id
        self.db = Database()

        # Главный макет
        layout = QHBoxLayout()

        # Левый виджет для управления параметрами отчетов
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("ОТЧЕТЫ")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; font-family: 'Impact'; font-size: 20px;")
        left_layout.addWidget(title_label)

        # Выбор периода отчета
        period_label = QLabel("Выбор периода отчета:")
        period_label.setStyleSheet("font-family: 'Impact'; font-size: 20px;")
        left_layout.addWidget(period_label)

        self.start_date_selector = QDateEdit()
        self.start_date_selector.setDisplayFormat("dd.MM.yyyy")
        self.start_date_selector.setDate(QDate.currentDate())
        self.start_date_selector.setStyleSheet("font-family: 'Impact'; font-size: 18px;")
        left_layout.addWidget(self.start_date_selector)

        self.end_date_selector = QDateEdit()
        self.end_date_selector.setDisplayFormat("dd.MM.yyyy")
        self.end_date_selector.setDate(QDate.currentDate())
        self.end_date_selector.setStyleSheet("font-family: 'Impact'; font-size: 18px;")
        left_layout.addWidget(self.end_date_selector)

        # Выбор вида отчета
        report_type_label = QLabel("Выберите вид отчета:")
        report_type_label.setStyleSheet("font-family: 'Impact'; font-size: 20px;")
        left_layout.addWidget(report_type_label)

        self.report_type_list = QListWidget()
        self.report_type_list.setStyleSheet("font-family: 'Impact'; font-size: 18px;")
        self.report_type_list.addItems([
            "Посещаемость",
            "Нагрузка преподавателей",
            "Использование помещений",
            "Популярность направлений"
        ])
        left_layout.addWidget(self.report_type_list)

        # Кнопка "Сформировать отчет"
        self.generate_report_button = QPushButton("Сформировать отчет")
        self.generate_report_button.setStyleSheet("font-family: 'Impact'; font-size: 20px;")
        self.generate_report_button.clicked.connect(self.generate_report)
        left_layout.addWidget(self.generate_report_button)

        left_widget.setLayout(left_layout)
        layout.addWidget(left_widget)

        # Правый виджет для отображения отчетов
        self.report_display_widget = QWidget()
        self.report_display_layout = QVBoxLayout()

        # Скроллируемая область для отчетов
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.report_content_widget = QWidget()
        self.report_content_layout = QGridLayout(self.report_content_widget)

        self.scroll_area.setWidget(self.report_content_widget)
        self.report_display_layout.addWidget(self.scroll_area)

        self.export_pdf_button = QPushButton("Экспорт в PDF")
        self.export_pdf_button.setStyleSheet("font-family: 'Impact'; font-size: 20px;")
        self.export_pdf_button.clicked.connect(self.export_to_pdf)
        self.report_display_layout.addWidget(self.export_pdf_button)

        self.report_display_widget.setLayout(self.report_display_layout)
        layout.addWidget(self.report_display_widget)

        self.setLayout(layout)

    def generate_report(self):
        """Формирует отчет в правом поле по выбранному типу и периоду."""
        self.db = Database()  # Пересоздание подключения
        start_date = self.start_date_selector.date()
        end_date = self.end_date_selector.date()

        # Проверка на корректность дат
        if end_date < start_date:
            QMessageBox.warning(self, "Ошибка", "Конечная дата не может быть меньше начальной даты.")
            return  # Выход из метода, если даты некорректны

        # Проверка на выбор типа отчета
        if self.report_type_list.currentItem() is None:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите тип отчета.")
            return  # Выход из метода, если тип отчета не выбран

        start_date_str = start_date.toString("yyyy-MM-dd")
        end_date_str = end_date.toString("yyyy-MM-dd")
        report_type = self.report_type_list.currentItem().text()

        self.clear_report()  # Очищаем отчет перед формированием нового

        if report_type == "Посещаемость":
            attendance_data = self.get_attendance_report(start_date_str, end_date_str)
            self.display_attendance_report(attendance_data)
        elif report_type == "Нагрузка преподавателей":
            teacher_load_data = self.get_teacher_load_report(start_date_str, end_date_str)
            self.display_teacher_load_report(teacher_load_data)
        elif report_type == "Использование помещений":
            room_usage_data = self.get_room_usage_report(start_date_str, end_date_str)
            self.display_room_usage_report(room_usage_data)
        elif report_type == "Популярность направлений":
            self.get_direction_popularity_report(start_date_str, end_date_str)

    def display_attendance_report(self, attendance_data):
        """Отображает отчет о посещаемости."""
        self.clear_report()
        header_labels = ["Группа", "ФИО Студента", "Всего занятий", "Пропуски"]
        for col, label in enumerate(header_labels):
            header_label = QLabel(label)
            header_label.setStyleSheet("font-family: 'Impact'; font-size: 20px;")
            self.report_content_layout.addWidget(header_label, 0, col)

        row = 1
        for group_number, data in attendance_data.items():
            for student in data['students']:
                group_label = QLabel(str(group_number))
                full_name_label = QLabel(student['full_name'])
                total_classes_label = QLabel(str(data['total_classes']))
                absences_label = QLabel(str(student['absences']))

                # Установка шрифта и размера
                for label in [group_label, full_name_label, total_classes_label, absences_label]:
                    label.setStyleSheet("font-family: 'Impact'; font-size: 18px;")

                self.report_content_layout.addWidget(group_label, row, 0)
                self.report_content_layout.addWidget(full_name_label, row, 1)
                self.report_content_layout.addWidget(total_classes_label, row, 2)
                self.report_content_layout.addWidget(absences_label, row, 3)

                row += 1

    def display_teacher_load_report(self, teacher_load_data):
        """Отображает отчет о нагрузке преподавателей."""
        self.clear_report()
        header_labels = ["Направление", "Преподаватель", "Всего занятий"]
        for col, label in enumerate(header_labels):
            header_label = QLabel(label)
            header_label.setStyleSheet("font-family: 'Impact'; font-size: 20px;")
            self.report_content_layout.addWidget(header_label, 0, col)

        row = 1
        for direction_name, teachers in teacher_load_data.items():
            for teacher in teachers:
                direction_label = QLabel(direction_name)
                teacher_name_label = QLabel(teacher['teacher_name'])
                total_classes_label = QLabel(str(teacher['total_classes']))

                # Установка шрифта и размера
                for label in [direction_label, teacher_name_label, total_classes_label]:
                    label.setStyleSheet("font-family: 'Impact'; font-size 18px;")

                self.report_content_layout.addWidget(direction_label, row, 0)
                self.report_content_layout.addWidget(teacher_name_label, row, 1)
                self.report_content_layout.addWidget(total_classes_label, row, 2)

                row += 1

    def display_room_usage_report(self, room_usage_data):
        """Отображает отчет о использовании помещений."""
        self.clear_report()
        header_labels = ["Номер кабинета", "Количество использований"]
        for col, label in enumerate(header_labels):
            header_label = QLabel(label)
            header_label.setStyleSheet("font-family: 'Impact'; font-size: 20px;")
            self.report_content_layout.addWidget(header_label, 0, col)

        row = 1
        for room_number, usage_count in room_usage_data['used_rooms']:
            room_label = QLabel(str(room_number))
            usage_count_label = QLabel(str(usage_count))

            # Установка шрифта и размера
            for label in [room_label, usage_count_label]:
                label.setStyleSheet("font-family: 'Impact'; font-size: 18px;")

            self.report_content_layout.addWidget(room_label, row, 0)
            self.report_content_layout.addWidget(usage_count_label, row, 1)

            row += 1

        if room_usage_data['unused_rooms']:
            unused_label = QLabel("Неиспользуемые помещения:")
            unused_label.setStyleSheet("font-family: 'Impact'; font-size: 20px;")
            self.report_content_layout.addWidget(unused_label, row, 0, 1, 2)
            row += 1

            for room_number in room_usage_data['unused_rooms']:
                unused_room_label = QLabel(str(room_number))
                unused_room_label.setStyleSheet("font-family: 'Impact'; font-size: 18px;")
                self.report_content_layout.addWidget(unused_room_label, row, 0)
                row += 1

    def display_direction_popularity(self, labels, sizes, direction_data, total_students):
        """Отображает данные о популярности направлений в интерфейсе."""
        self.clear_report()  # Очищаем область отчета

        # Сохраняем данные для экспорта в PDF
        self.labels = labels  # Сохраняем labels как атрибут класса
        self.sizes = sizes  # Сохраняем sizes как атрибут класса
        self.total_students = total_students  # Сохраняем общее количество учеников
        self.direction_data = direction_data  # Сохраняем данные по направлениям

        # Создаем фигуру для круговой диаграммы
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')  # Равные оси для круга
        ax.set_title('Популярность направлений')

        # Встраиваем диаграмму в интерфейс
        canvas = FigureCanvas(fig)
        self.report_content_layout.addWidget(canvas, 0, 0, 1, 2)  # Добавляем диаграмму в layout

        # Отображаем список направлений и количество учеников
        row = 1
        for direction_name, student_count in direction_data:
            direction_label = QLabel(f"{direction_name}: {student_count} учеников")
            direction_label.setStyleSheet("font-family: 'Impact'; font-size: 18px;")
            self.report_content_layout.addWidget(direction_label, row, 0)
            row += 1

        # Отображаем общее количество учеников
        total_label = QLabel(f"Общее количество учеников: {total_students}")
        total_label.setStyleSheet("font-family: 'Impact'; font-size: 20px;")
        self.report_content_layout.addWidget(total_label, row, 0)

        # Обновляем интерфейс
        self.report_content_widget.update()

    def get_attendance_report(self, start_date, end_date):
        """Получает отчет о посещаемости с количеством занятий и пропусков по группам."""
        try:
            # Запрос для получения количества занятий и пропусков по группам
            query = """
                SELECT g.group_number, COUNT(r.rasp_id) AS total_classes,
                       p.person_id, CONCAT(p.person_surname, ' ', p.person_name) AS full_name,
                       SUM(CASE WHEN a.attend = 0 THEN 1 ELSE 0 END) AS absences
                FROM groupss g
                LEFT JOIN rasp r ON g.group_id = r.group_id AND r.date BETWEEN %s AND %s
                LEFT JOIN student_group sg ON g.group_id = sg.group_id
                LEFT JOIN students s ON sg.student_id = s.student_id
                LEFT JOIN persons p ON s.student_id = p.person_id
                LEFT JOIN attendance a ON r.rasp_id = a.rasp_id AND s.student_id = a.student_id
                WHERE g.company_id = %s
                GROUP BY g.group_id, p.person_id
                ORDER BY g.group_number, p.person_surname
            """

            # Выполнение запроса
            records = self.db.fetch_all(query, (start_date, end_date, self.company_id))

            # Обработка данных
            report_data = {}
            for group_number, total_classes, person_id, full_name, absences in records:
                if group_number not in report_data:
                    report_data[group_number] = {
                        'total_classes': total_classes,
                        'students': []
                    }
                report_data[group_number]['students'].append({
                    'full_name': full_name,
                    'absences': absences
                })

            return report_data

        except Exception:
            QMessageBox.critical(self, "Ошибка", "Не удалось получить отчет о посещаемости.")
            return {}

    def get_teacher_load_report(self, start_date, end_date):
        """Получает отчет о нагрузке преподавателей за указанный период."""
        try:
            # Запрос для получения количества проведенных занятий по преподавателям и направлениям
            query = """
                    SELECT CONCAT(p.person_surname, ' ', p.person_name) AS teacher_name,
                           d.direction_name,
                           COUNT(r.rasp_id) AS total_classes
                    FROM teachers t
                    JOIN persons p ON t.teacher_id = p.person_id
                    JOIN directions d ON t.direction_id = d.direction_id
                    JOIN groupss g ON t.teacher_id = g.teacher_id
                    JOIN rasp r ON g.group_id = r.group_id
                    WHERE r.date BETWEEN %s AND %s
                    AND d.company_id = %s
                    GROUP BY t.teacher_id, d.direction_id
                    ORDER BY d.direction_name, teacher_name
            """

            # Выполнение запроса
            records = self.db.fetch_all(query, (start_date, end_date, self.company_id))

            # Обработка данных
            report_data = {}
            for teacher_name, direction_name, total_classes in records:
                if direction_name not in report_data:
                    report_data[direction_name] = []
                report_data[direction_name].append({
                    'teacher_name': teacher_name,
                    'total_classes': total_classes
                })

            return report_data

        except Exception:
            QMessageBox.critical(self, "Ошибка", "Не удалось получить отчет о нагрузке преподавателей.")
            return {}

    def get_room_usage_report(self, start_date, end_date):
        """Получает отчет о использовании кабинетов за указанный период."""
        try:
            # Запрос для получения всех кабинетов
            query_rooms = """
                SELECT room_id, room_number
                FROM rooms
                WHERE company_id = %s
            """
            rooms = self.db.fetch_all(query_rooms, (self.company_id,))

            # Словарь для хранения количества использований кабинетов
            room_usage = {room[0]: {'room_number': room[1], 'usage_count': 0} for room in rooms}

            # Запрос для получения количества использований кабинетов
            query_usage = """
                SELECT room_id, COUNT(*) AS usage_count
                FROM rasp
                WHERE date BETWEEN %s AND %s
                GROUP BY room_id
            """
            usage_records = self.db.fetch_all(query_usage, (start_date, end_date))

            # Обновляем словарь с количеством использований
            for room_id, usage_count in usage_records:
                if room_id in room_usage:
                    room_usage[room_id]['usage_count'] += usage_count

            # Списки для отчетов
            used_rooms = []
            unused_rooms = []

            for room_id, data in room_usage.items():
                if data['usage_count'] > 0:
                    used_rooms.append((data['room_number'], data['usage_count']))
                else:
                    unused_rooms.append(data['room_number'])

            return {
                'used_rooms': used_rooms,
                'unused_rooms': unused_rooms
            }

        except Exception:
            QMessageBox.critical(self, "Ошибка", "Не удалось получить отчет о использовании кабинетов.")
            return {}

    def get_direction_popularity_report(self, start_date, end_date):
        """Получает отчет о популярности направлений за указанный период."""
        try:
            # Запрос для получения количества учеников по направлениям
            query = """
                SELECT d.direction_name, COUNT(s.student_id) AS student_count
                FROM directions d
                LEFT JOIN teachers t ON d.direction_id = t.direction_id
                LEFT JOIN groupss g ON t.teacher_id = g.teacher_id
                LEFT JOIN student_group sg ON g.group_id = sg.group_id
                LEFT JOIN students s ON sg.student_id = s.student_id
                WHERE d.company_id = %s
                GROUP BY d.direction_id
                HAVING student_count > 0  -- Исключаем направления с 0 учеников
            """
            direction_data = self.db.fetch_all(query, (self.company_id,))

            # Запрос для получения общего количества учеников
            total_students_query = """
                SELECT COUNT(*) 
                FROM students s
                JOIN student_group sg ON s.student_id = sg.student_id
                JOIN groupss g ON sg.group_id = g.group_id
                JOIN directions d ON g.direction_id = d.direction_id
                WHERE d.company_id = %s
            """
            total_students = self.db.fetch_one(total_students_query, (self.company_id,))[0]

            # Подготовка данных для круговой диаграммы
            labels = []
            sizes = []

            for direction_name, student_count in direction_data:
                labels.append(direction_name)
                percentage = (student_count / total_students) * 100 if total_students > 0 else 0
                sizes.append(percentage)

            # Отображение данных в интерфейсе
            self.display_direction_popularity(labels, sizes, direction_data, total_students)

        except Exception:
            QMessageBox.critical(self, "Ошибка", "Не удалось получить отчет о популярности направлений.")

    def export_to_pdf(self):
        """Экспортирует текущий отчет в PDF."""
        try:
            # Получаем путь к папке "Документы"
            documents_path = os.path.expanduser("~/Documents")

            # Формируем стандартное имя файла
            default_file_name = os.path.join(documents_path, "Отчет.pdf")

            # Открываем диалог сохранения файла с указанием стандартного пути
            pdf_file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить PDF",
                default_file_name,  # Указываем стандартный путь
                "PDF Files (*.pdf)"
            )

            if not pdf_file_path:
                return  # Если пользователь отменил, выходим

            with PdfPages(pdf_file_path) as pdf:
                # Получаем название отчета и период
                report_type = self.report_type_list.currentItem().text()
                start_date = self.start_date_selector.date().toString("dd.MM.yyyy")
                end_date = self.end_date_selector.date().toString("dd.MM.yyyy")
                report_title = f"{report_type} за период с {start_date} по {end_date}"

                # Добавляем отчет о посещаемости
                if report_type == "Посещаемость":
                    attendance_data = self.get_attendance_report(
                        self.start_date_selector.date().toString("yyyy-MM-dd"),
                        self.end_date_selector.date().toString("yyyy-MM-dd")
                    )
                    table_data = self.prepare_attendance_table(attendance_data)

                    # Создаем таблицу для PDF
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.axis('off')  # Отключаем оси
                    ax.set_title(report_title, fontsize=14, pad=20)  # Добавляем заголовок
                    table = ax.table(
                        cellText=table_data,
                        colLabels=["Группа", "ФИО Студента", "Всего занятий", "Пропуски"],
                        cellLoc='center',
                        loc='center'
                    )
                    table.auto_set_font_size(False)
                    table.set_fontsize(10)
                    table.scale(1.2, 1.2)  # Масштабируем таблицу
                    pdf.savefig(fig)
                    plt.close(fig)

                # Добавляем отчет о нагрузке преподавателей
                elif report_type == "Нагрузка преподавателей":
                    teacher_load_data = self.get_teacher_load_report(
                        self.start_date_selector.date().toString("yyyy-MM-dd"),
                        self.end_date_selector.date().toString("yyyy-MM-dd")
                    )
                    table_data = self.prepare_teacher_load_table(teacher_load_data)

                    # Создаем таблицу для PDF
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.axis('off')
                    ax.set_title(report_title, fontsize=14, pad=20)  # Добавляем заголовок
                    table = ax.table(
                        cellText=table_data,
                        colLabels=["Направление", "Преподаватель", "Всего занятий"],
                        cellLoc='center',
                        loc='center'
                    )
                    table.auto_set_font_size(False)
                    table.set_fontsize(10)
                    table.scale(1.2, 1.2)
                    pdf.savefig(fig)
                    plt.close(fig)

                # Добавляем отчет о использовании помещений
                elif report_type == "Использование помещений":
                    room_usage_data = self.get_room_usage_report(
                        self.start_date_selector.date().toString("yyyy-MM-dd"),
                        self.end_date_selector.date().toString("yyyy-MM-dd")
                    )
                    table_data = self.prepare_room_usage_table(room_usage_data)

                    # Создаем таблицу для PDF
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.axis('off')
                    ax.set_title(report_title, fontsize=14, pad=20)  # Добавляем заголовок
                    table = ax.table(
                        cellText=table_data,
                        colLabels=["Номер кабинета", "Количество использований"],
                        cellLoc='center',
                        loc='center'
                    )
                    table.auto_set_font_size(False)
                    table.set_fontsize(10)
                    table.scale(1.2, 1.2)
                    pdf.savefig(fig)
                    plt.close(fig)

                # Добавляем отчет о популярности направлений
                elif report_type == "Популярность направлений":
                    # Создаем фигуру для диаграммы и текста
                    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))  # 2 строки, 1 столбец

                    # Добавляем заголовок
                    fig.suptitle(report_title, fontsize=14, y=1.02)  # Добавляем заголовок

                    # Круговая диаграмма
                    ax1.pie(self.sizes, labels=self.labels, autopct='%1.1f%%', startangle=140)
                    ax1.axis('equal')  # Равные оси для круга
                    ax1.set_title('Популярность направлений')

                    # Текстовая информация
                    text_content = "Общее количество учеников: {}\n\n".format(self.total_students)
                    for direction_name, student_count in self.direction_data:
                        text_content += f"{direction_name}: {student_count} учеников\n"

                    # Добавляем текст на второй subplot
                    ax2.axis('off')  # Отключаем оси для текста
                    ax2.text(0.1, 0.5, text_content, fontsize=12, va='center')

                    # Сохраняем фигуру в PDF
                    pdf.savefig(fig)
                    plt.close(fig)

            QMessageBox.information(self, "Успех", "Отчет успешно экспортирован в PDF!")

        except Exception:
            QMessageBox.critical(self, "Ошибка", "Не удалось экспортировать отчет в PDF.")

    def prepare_attendance_table(self, attendance_data):
        """Подготавливает данные для таблицы посещаемости."""
        table_data = []
        for group_number, data in attendance_data.items():
            for student in data['students']:
                table_data.append([group_number, student['full_name'], data['total_classes'], student['absences']])
        return table_data

    def prepare_teacher_load_table(self, teacher_load_data):
        """Подготавливает данные для таблицы нагрузки преподавателей."""
        table_data = []
        for direction_name, teachers in teacher_load_data.items():
            for teacher in teachers:
                table_data.append([direction_name, teacher['teacher_name'], teacher['total_classes']])
        return table_data

    def prepare_room_usage_table(self, room_usage_data):
        """Подготавливает данные для таблицы использования помещений."""
        table_data = []
        for room_number, usage_count in room_usage_data['used_rooms']:
            table_data.append([room_number, usage_count])
        return table_data

    def clear_report(self):
        """Очищает область для отображения отчета."""
        # Удаляем все виджеты из layout
        for i in reversed(range(self.report_content_layout.count())):
            widget = self.report_content_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
