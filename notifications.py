from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
import sqlite3
import json

class NotificationSystem:
    def __init__(self, db_path='equipment.db'):
        self.db_path = db_path
    
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def add_notification(self, тип, сообщение):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO уведомления (тип, сообщение)
            VALUES (?, ?)
        ''', (тип, сообщение))
        conn.commit()
        conn.close()
    
    def get_unread_notifications(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM уведомления
            WHERE статус = 'непрочитанное'
            ORDER BY дата_создания DESC
        ''')
        notifications = cursor.fetchall()
        conn.close()
        return notifications
    
    def mark_as_read(self, notification_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE уведомления
            SET статус = 'прочитанное',
                дата_прочтения = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (notification_id,))
        conn.commit()
        conn.close()
    
    def check_maintenance_notifications(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Проверяем технику, требующую обслуживания
        cursor.execute('''
            SELECT название, модель, дата_следующего_обслуживания
            FROM техника
            WHERE дата_следующего_обслуживания <= date('now', '+7 days')
            AND дата_следующего_обслуживания > date('now')
        ''')
        maintenance_required = cursor.fetchall()
        
        for equipment in maintenance_required:
            days_left = (datetime.strptime(equipment['дата_следующего_обслуживания'], '%Y-%m-%d') - datetime.now()).days
            self.add_notification(
                'обслуживание',
                f'Техника {equipment["название"]} ({equipment["модель"]}) требует обслуживания через {days_left} дней'
            )
        
        # Проверяем технику с истекающим гарантийным сроком
        cursor.execute('''
            SELECT название, модель, гарантийный_срок
            FROM техника
            WHERE гарантийный_срок <= date('now', '+30 days')
            AND гарантийный_срок > date('now')
        ''')
        warranty_expiring = cursor.fetchall()
        
        for equipment in warranty_expiring:
            days_left = (datetime.strptime(equipment['гарантийный_срок'], '%Y-%m-%d') - datetime.now()).days
            self.add_notification(
                'гарантия',
                f'Гарантийный срок техники {equipment["название"]} ({equipment["модель"]}) истекает через {days_left} дней'
            )
        
        conn.close()
    
    def clear_old_notifications(self, days=30):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM уведомления
            WHERE дата_создания < date('now', ?)
        ''', (f'-{days} days',))
        conn.commit()
        conn.close()

class NotificationManager:
    def __init__(self, db_path='equipment.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Создаем таблицу для уведомлений
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS уведомления (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    тип TEXT NOT NULL,
                    сообщение TEXT NOT NULL,
                    важность TEXT NOT NULL,
                    статус TEXT DEFAULT 'непрочитанное',
                    дата_создания TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    дата_прочтения TIMESTAMP,
                    пользователь TEXT
                )
            ''')
            
            conn.commit()
    
    def add_notification(self, notification_type, message, importance='info', user=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO уведомления 
                (тип, сообщение, важность, пользователь)
                VALUES (?, ?, ?, ?)
            ''', (notification_type, message, importance, user))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_notifications(self, user=None, status=None, limit=50):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = 'SELECT * FROM уведомления WHERE 1=1'
            params = []
            
            if user:
                query += ' AND пользователь = ?'
                params.append(user)
            
            if status:
                query += ' AND статус = ?'
                params.append(status)
            
            query += ' ORDER BY дата_создания DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            notifications = []
            for row in rows:
                notifications.append({
                    'id': row[0],
                    'тип': row[1],
                    'сообщение': row[2],
                    'важность': row[3],
                    'статус': row[4],
                    'дата_создания': row[5],
                    'дата_прочтения': row[6],
                    'пользователь': row[7]
                })
            
            return notifications
    
    def mark_all_as_read(self, user=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = '''
                UPDATE уведомления 
                SET статус = 'прочитанное', дата_прочтения = CURRENT_TIMESTAMP
                WHERE статус = 'непрочитанное'
            '''
            params = []
            
            if user:
                query += ' AND пользователь = ?'
                params.append(user)
            
            cursor.execute(query, params)
            conn.commit()
    
    def delete_notification(self, notification_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM уведомления WHERE id = ?', (notification_id,))
            conn.commit()
    
    def get_notification_stats(self, days=30):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    тип,
                    важность,
                    статус,
                    COUNT(*) as количество
                FROM уведомления
                WHERE дата_создания >= datetime('now', '-' || ? || ' days')
                GROUP BY тип, важность, статус
                ORDER BY количество DESC
            ''', (days,))
            
            return cursor.fetchall() 