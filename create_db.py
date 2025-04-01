import sqlite3
from config import Config
from werkzeug.security import generate_password_hash

def init_db():
    conn = sqlite3.connect(Config.DATABASE_PATH)
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

if __name__ == '__main__':
    print("Инициализация базы данных...")
    init_db()
    print("База данных успешно инициализирована!") 