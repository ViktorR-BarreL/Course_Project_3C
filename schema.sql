-- Таблица компаний
CREATE TABLE IF NOT EXISTS companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL
);

-- Таблица персон
CREATE TABLE IF NOT EXISTS persons (
    person_id INT AUTO_INCREMENT PRIMARY KEY,
    person_name VARCHAR(50) NOT NULL,
    person_surname VARCHAR(50) NOT NULL,
    person_patron VARCHAR(50),
    company_id INT NOT NULL,
    CONSTRAINT fk_person_company FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Таблица контактов
CREATE TABLE IF NOT EXISTS contacts (
    contact_id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    contact_type VARCHAR(100) NOT NULL,
    contact_state VARCHAR(150),
    CONSTRAINT fk_contact_person FOREIGN KEY (person_id)
        REFERENCES persons(person_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Таблица администраторов
CREATE TABLE IF NOT EXISTS admins (
    company_id INT NOT NULL,
    admin_login VARCHAR(100) NOT NULL,
    admin_password VARCHAR(18) NOT NULL,
    PRIMARY KEY (company_id, admin_login),
    CONSTRAINT fk_admin_company FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Таблица направлений
CREATE TABLE IF NOT EXISTS directions (
    direction_id INT AUTO_INCREMENT PRIMARY KEY,
    direction_name VARCHAR(150) NOT NULL,
    direction_description VARCHAR(1024),
    company_id INT NOT NULL,
    CONSTRAINT fk_direction_company FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Таблица учителей
CREATE TABLE IF NOT EXISTS teachers (
    teacher_id INT PRIMARY KEY,
    direction_id INT,
    teacher_login VARCHAR(100) NOT NULL,
    teacher_password VARCHAR(18) NOT NULL,
    CONSTRAINT fk_teacher_person FOREIGN KEY (teacher_id)
        REFERENCES persons(person_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_teacher_direction FOREIGN KEY (direction_id)
        REFERENCES directions(direction_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Таблица групп
CREATE TABLE IF NOT EXISTS groupss (
    group_id INT AUTO_INCREMENT PRIMARY KEY,
    direction_id INT NOT NULL,
    group_number VARCHAR(50) NOT NULL,  -- Изменено с INT на VARCHAR(50)
    lower_age_limit INT,
    upper_age_limit INT,
    classes_duration TIME,
    teacher_id INT NOT NULL,
    company_id INT NOT NULL,
    CONSTRAINT fk_group_direction FOREIGN KEY (direction_id)
        REFERENCES directions(direction_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_group_teacher FOREIGN KEY (teacher_id)
        REFERENCES teachers(teacher_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_group_company FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Таблица студентов
CREATE TABLE IF NOT EXISTS students (
    student_id INT PRIMARY KEY,
    birth_date DATE NOT NULL,
    CONSTRAINT fk_student_person FOREIGN KEY (student_id)
        REFERENCES persons(person_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Таблица связи студентов и групп
CREATE TABLE IF NOT EXISTS student_group (
    student_id INT NOT NULL,
    group_id INT NOT NULL,
    PRIMARY KEY (student_id, group_id),
    CONSTRAINT fk_studentgroup_student FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_studentgroup_group FOREIGN KEY (group_id)
        REFERENCES groupss(group_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Таблица аудиторий
CREATE TABLE IF NOT EXISTS rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(50) NOT NULL,
    room_description VARCHAR(1024),
    company_id INT NOT NULL,
    CONSTRAINT fk_room_company FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Таблица расписания
CREATE TABLE IF NOT EXISTS rasp (
    rasp_id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    group_id INT NOT NULL,
    room_id INT NOT NULL,
    start_time TIME,
    company_id INT NOT NULL,
    CONSTRAINT fk_rasp_group FOREIGN KEY (group_id)
        REFERENCES groupss(group_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_rasp_room FOREIGN KEY (room_id)
        REFERENCES rooms(room_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_rasp_company FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- Таблица учета посещений
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    rasp_id INT NOT NULL,
    attend BOOLEAN NOT NULL,
    CONSTRAINT fk_attendance_student FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_attendance_rasp FOREIGN KEY (rasp_id)
        REFERENCES rasp(rasp_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);
