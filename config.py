import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')  # Секретный ключ для Flask
    DEBUG = True  # Режим отладки
    DATABASE_PATH = 'database.db'  # Путь к базе данных
    LOG_FILE = 'app.log'  # Файл логов