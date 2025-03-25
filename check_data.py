from models import get_db_connection

def check_data():
    # Подключение к базе данных
    conn = get_db_connection()

    try:
        # Проверка таблицы сотрудников
        сотрудники = conn.execute('SELECT * FROM сотрудники').fetchall()
        print("Сотрудники:")
        for сотрудник in сотрудники:
            print(dict(сотрудник))  # Преобразуем sqlite3.Row в словарь

        # Проверка таблицы техники
        техника = conn.execute('SELECT * FROM техника').fetchall()
        print("Техника:")
        for item in техника:
            print(dict(item))  # Преобразуем sqlite3.Row в словарь

    except Exception as e:
        print(f"Ошибка при работе с базой данных: {e}")

    finally:
        # Закрытие соединения
        conn.close()

if __name__ == "__main__":
    check_data()