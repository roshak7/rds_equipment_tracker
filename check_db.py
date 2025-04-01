import sqlite3
from config import Config

def check_database():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    # Проверяем таблицы
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Таблицы в базе данных:")
    for table in tables:
        print(f"- {table[0]}")
        # Проверяем количество записей в каждой таблице
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  Количество записей: {count}")
        
        # Выводим первые 5 записей
        cursor.execute(f"SELECT * FROM {table[0]} LIMIT 5")
        rows = cursor.fetchall()
        if rows:
            print("  Примеры записей:")
            for row in rows:
                print(f"    {row}")
        print()
    
    conn.close()

if __name__ == '__main__':
    check_database() 