import logging
from config import Config  # Импорт конфигурации

# Настройка логирования
def setup_logging():
    logging.basicConfig(
        filename=Config.LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

# Запись действия в лог
def запись_лога(действие, пользователь_id=None):
    logging.info(f"Пользователь ID {пользователь_id}: {действие}")