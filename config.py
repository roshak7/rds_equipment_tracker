import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    DEBUG = True  # Режим отладки
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'equipment.db')
    LOG_FILE = 'app.log'  # Файл логов
    
    # Настройки SMTP-сервера
    SMTP_SERVER = os.environ.get('SMTP_SERVER') or 'smtp.gmail.com'
    SMTP_PORT = int(os.environ.get('SMTP_PORT') or 587)
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME') or 'your-email@gmail.com'
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') or 'your-app-password'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@company.com'