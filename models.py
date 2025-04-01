import sqlite3
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash  # Добавляем check_password_hash
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

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password, method='pbkdf2:sha256')

    @staticmethod
    def check_password(hashed_password, password):
        return check_password_hash(hashed_password, password)

    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

# Инициализация базы данных
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Создаем таблицу пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS пользователи (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # Создаем таблицу сотрудников
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS сотрудники (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            фамилия TEXT NOT NULL,
            имя TEXT NOT NULL,
            отчество TEXT,
            должность TEXT,
            отдел TEXT,
            email TEXT,
            телефон TEXT,
            дата_приема DATE DEFAULT CURRENT_DATE
        )
    ''')
    
    # Создаем таблицу техники
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS техника (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            название TEXT NOT NULL,
            модель TEXT,
            производитель TEXT,
            серийный_номер TEXT UNIQUE,
            дата_приобретения DATE,
            гарантийный_срок DATE,
            состояние TEXT DEFAULT 'рабочее',
            статус TEXT DEFAULT 'свободна',
            текущий_владелец_id INTEGER,
            дата_последнего_назначения DATE,
            дата_следующего_обслуживания DATE,
            FOREIGN KEY (текущий_владелец_id) REFERENCES сотрудники (id)
        )
    ''')
    
    # Создаем таблицу назначений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS назначения (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            сотрудник_id INTEGER NOT NULL,
            техника_id INTEGER NOT NULL,
            дата_назначения DATE NOT NULL,
            дата_возврата DATE,
            статус TEXT DEFAULT 'активное',
            причина_возврата TEXT,
            FOREIGN KEY (сотрудник_id) REFERENCES сотрудники (id),
            FOREIGN KEY (техника_id) REFERENCES техника (id)
        )
    ''')
    
    # Создаем таблицу обслуживания
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS обслуживание (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            техника_id INTEGER NOT NULL,
            тип_обслуживания TEXT NOT NULL,
            описание TEXT,
            исполнитель TEXT,
            дата_начала DATE NOT NULL,
            дата_завершения DATE,
            статус TEXT DEFAULT 'в процессе',
            FOREIGN KEY (техника_id) REFERENCES техника (id)
        )
    ''')
    
    # Создаем таблицу истории изменений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS история_изменений (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            таблица TEXT NOT NULL,
            запись_id INTEGER NOT NULL,
            тип_изменения TEXT NOT NULL,
            пользователь_id INTEGER NOT NULL,
            дата_изменения TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            старые_данные TEXT,
            новые_данные TEXT,
            FOREIGN KEY (пользователь_id) REFERENCES пользователи (id)
        )
    ''')
    
    # Создаем таблицу уведомлений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS уведомления (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            тип TEXT NOT NULL,
            сообщение TEXT NOT NULL,
            дата_создания TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            дата_прочтения TIMESTAMP,
            статус TEXT DEFAULT 'непрочитанное'
        )
    ''')
    
    # Создаем таблицу файлов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS файлы (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            таблица TEXT NOT NULL,
            запись_id INTEGER NOT NULL,
            имя_файла TEXT NOT NULL,
            путь_к_файлу TEXT NOT NULL,
            тип_файла TEXT,
            размер INTEGER,
            дата_загрузки TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            загрузил_id INTEGER NOT NULL,
            FOREIGN KEY (загрузил_id) REFERENCES пользователи (id)
        )
    ''')
    
    # Создаем таблицу календаря
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS календарь (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            тип_события TEXT NOT NULL,
            таблица TEXT NOT NULL,
            запись_id INTEGER NOT NULL,
            дата_начала DATE NOT NULL,
            дата_окончания DATE,
            описание TEXT,
            статус TEXT DEFAULT 'активное'
        )
    ''')
    
    # Создаем администратора по умолчанию
    cursor.execute('SELECT COUNT(*) FROM пользователи WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO пользователи (username, password, role)
            VALUES (?, ?, ?)
        ''', ('admin', generate_password_hash('admin'), 'admin'))
    
    conn.commit()
    conn.close()

# Функция для записи логов
def запись_лога(пользователь_id, действие):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO история_изменений (таблица, запись_id, тип_изменения, пользователь_id, новые_данные)
        VALUES (?, ?, ?, ?, ?)
    ''', ('система', 0, 'действие', пользователь_id, действие))
    conn.commit()
    conn.close()