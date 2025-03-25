import sqlite3
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash  # Для хэширования пароля
from config import Config  # Импорт конфигурации

# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Выполнение запросов с обработкой ошибок
def execute_query(query, params=()):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return None

# Класс для пользователей
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

# Инициализация базы данных
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS пользователи (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON пользователи(username)')

    # Таблица сотрудников
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS сотрудники (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            имя TEXT NOT NULL,
            фамилия TEXT NOT NULL,
            должность TEXT,
            отдел TEXT,
            email TEXT UNIQUE,
            телефон TEXT,
            статус TEXT DEFAULT 'активный'
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON сотрудники(email)')

    # Таблица техники
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS техника (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            название TEXT NOT NULL,
            модель TEXT,
            производитель TEXT,
            серийный_номер TEXT NOT NULL UNIQUE,
            дата_покупки DATE,
            стоимость REAL,
            состояние TEXT DEFAULT 'рабочее',
            статус TEXT DEFAULT 'доступна'
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_serial_number ON техника(серийный_номер)')

    # Таблица назначений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS назначения (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            сотрудник_id INTEGER,
            техника_id INTEGER,
            дата_назначения TEXT,
            дата_возврата TEXT,
            FOREIGN KEY (сотрудник_id) REFERENCES сотрудники(id),
            FOREIGN KEY (техника_id) REFERENCES техника(id)
        )
    ''')

    # Таблица логов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS логи (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            пользователь_id INTEGER,
            действие TEXT,
            дата TEXT,
            FOREIGN KEY (пользователь_id) REFERENCES пользователи(id)
        )
    ''')
    # Таблица логов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS назначения (
            сотрудник_id INTEGER NOT NULL,
            техника_id INTEGER NOT NULL,
            дата_назначения DATE NOT NULL,
            дата_возврата DATE,
            FOREIGN KEY (сотрудник_id) REFERENCES сотрудники(id),
            FOREIGN KEY (техника_id) REFERENCES техника(id)
        )
    ''')

    # Создание дефолтного суперпользователя
    admin_username = "admin"
    admin_password = "admin"
    admin_role = "admin"

    # Проверяем, существует ли пользователь с логином "admin"
    admin_user = cursor.execute('SELECT * FROM пользователи WHERE username = ?', (admin_username,)).fetchone()

    if not admin_user:
        # Хэшируем пароль "admin"
        hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256')

        # Добавляем дефолтного суперпользователя
        cursor.execute('''
            INSERT INTO пользователи (username, password, role)
            VALUES (?, ?, ?)
        ''', (admin_username, hashed_password, admin_role))
        print("Создан дефолтный суперпользователь: логин=admin, пароль=admin")
    else:
        print("Дефолтный суперпользователь уже существует.")

    conn.commit()
    conn.close()

# Функция для записи логов
def запись_лога(пользователь_id, действие):
    execute_query('''
        INSERT INTO логи (пользователь_id, действие, дата)
        VALUES (?, ?, ?)
    ''', (пользователь_id, действие, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))