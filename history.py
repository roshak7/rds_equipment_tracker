import sqlite3
from datetime import datetime
import json

class HistoryManager:
    def __init__(self, db_path='equipment.db'):
        self.db_path = db_path
    
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def add_change(self, таблица, запись_id, тип_изменения, пользователь_id, старые_данные=None, новые_данные=None):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Преобразуем данные в JSON, если они являются словарями
        if isinstance(старые_данные, dict):
            старые_данные = json.dumps(старые_данные, ensure_ascii=False)
        if isinstance(новые_данные, dict):
            новые_данные = json.dumps(новые_данные, ensure_ascii=False)
        
        cursor.execute('''
            INSERT INTO история_изменений (
                таблица, запись_id, тип_изменения, пользователь_id,
                старые_данные, новые_данные
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            таблица,
            запись_id,
            тип_изменения,
            пользователь_id,
            старые_данные,
            новые_данные
        ))
        conn.commit()
        conn.close()
    
    def get_history(self, таблица=None, запись_id=None, тип_изменения=None, limit=50):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT и.*, п.username as пользователь_username
            FROM история_изменений и
            JOIN пользователи п ON и.пользователь_id = п.id
            WHERE 1=1
        '''
        params = []
        
        if таблица:
            query += ' AND и.таблица = ?'
            params.append(таблица)
        
        if запись_id:
            query += ' AND и.запись_id = ?'
            params.append(запись_id)
        
        if тип_изменения:
            query += ' AND и.тип_изменения = ?'
            params.append(тип_изменения)
        
        query += ' ORDER BY и.дата_изменения DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        history = cursor.fetchall()
        conn.close()
        return history
    
    def get_record_history(self, таблица, запись_id):
        return self.get_history(таблица=таблица, запись_id=запись_id)
    
    def get_user_history(self, пользователь_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM история_изменений
            WHERE пользователь_id = ?
            ORDER BY дата_изменения DESC
        ''', (пользователь_id,))
        history = cursor.fetchall()
        conn.close()
        return history
    
    def clear_old_history(self, days=90):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM история_изменений
            WHERE дата_изменения < date('now', ?)
        ''', (f'-{days} days',))
        conn.commit()
        conn.close()
    
    def format_change_data(self, data):
        if not data:
            return None
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data
    
    def get_change_summary(self, change):
        summary = f"{change['тип_изменения']} в таблице {change['таблица']}"
        if change['запись_id']:
            summary += f" (ID: {change['запись_id']})"
        return summary 