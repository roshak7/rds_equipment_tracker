import sqlite3
from datetime import datetime, timedelta
import json
from icalendar import Calendar, Event
import pytz
import icalendar
import os

class CalendarManager:
    def __init__(self, db_path='equipment.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Создаем таблицу для событий календаря
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS события_календаря (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    тип TEXT NOT NULL,
                    заголовок TEXT NOT NULL,
                    описание TEXT,
                    дата_начала TIMESTAMP NOT NULL,
                    дата_окончания TIMESTAMP,
                    повторяемость TEXT,
                    связанная_запись_тип TEXT,
                    связанная_запись_id INTEGER,
                    цвет TEXT DEFAULT '#007bff',
                    создатель TEXT,
                    дата_создания TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def add_event(self, event_type, title, description, start_date, end_date=None, 
                  recurrence=None, related_record_type=None, related_record_id=None,
                  color='#007bff', creator=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO события_календаря 
                (тип, заголовок, описание, дата_начала, дата_окончания, 
                 повторяемость, связанная_запись_тип, связанная_запись_id, 
                 цвет, создатель)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event_type,
                title,
                description,
                start_date,
                end_date,
                recurrence,
                related_record_type,
                related_record_id,
                color,
                creator
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_events(self, start_date=None, end_date=None, event_type=None, 
                   related_record_type=None, related_record_id=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = 'SELECT * FROM события_календаря WHERE 1=1'
            params = []
            
            if start_date:
                query += ' AND дата_начала >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND дата_начала <= ?'
                params.append(end_date)
            
            if event_type:
                query += ' AND тип = ?'
                params.append(event_type)
            
            if related_record_type:
                query += ' AND связанная_запись_тип = ?'
                params.append(related_record_type)
            
            if related_record_id:
                query += ' AND связанная_запись_id = ?'
                params.append(related_record_id)
            
            query += ' ORDER BY дата_начала'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                events.append({
                    'id': row[0],
                    'тип': row[1],
                    'заголовок': row[2],
                    'описание': row[3],
                    'дата_начала': row[4],
                    'дата_окончания': row[5],
                    'повторяемость': row[6],
                    'связанная_запись_тип': row[7],
                    'связанная_запись_id': row[8],
                    'цвет': row[9],
                    'создатель': row[10],
                    'дата_создания': row[11]
                })
            
            return events
    
    def update_event(self, event_id, **kwargs):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            set_clause = ', '.join([f'{k} = ?' for k in kwargs.keys()])
            query = f'UPDATE события_календаря SET {set_clause} WHERE id = ?'
            
            params = list(kwargs.values())
            params.append(event_id)
            
            cursor.execute(query, params)
            conn.commit()
    
    def delete_event(self, event_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM события_календаря WHERE id = ?', (event_id,))
            conn.commit()
    
    def get_upcoming_events(self, days=7):
        end_date = datetime.now() + timedelta(days=days)
        return self.get_events(
            start_date=datetime.now().isoformat(),
            end_date=end_date.isoformat()
        )
    
    def generate_ical(self, events):
        cal = Calendar()
        cal.add('prodid', '-//Equipment Tracker Calendar//example.com//')
        cal.add('version', '2.0')
        
        for event_data in events:
            event = Event()
            event.add('summary', event_data['заголовок'])
            event.add('description', event_data['описание'])
            event.add('dtstart', datetime.fromisoformat(event_data['дата_начала']))
            if event_data['дата_окончания']:
                event.add('dtend', datetime.fromisoformat(event_data['дата_окончания']))
            event.add('uid', f'event-{event_data["id"]}@example.com')
            
            cal.add_component(event)
        
        return cal.to_ical()
    
    def add_maintenance_event(self, equipment_id, title, description, start_date, 
                            maintenance_period, creator=None):
        """Добавляет событие обслуживания с повторяемостью"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Получаем информацию о технике
            cursor.execute('''
                SELECT название, модель
                FROM техника
                WHERE id = ?
            ''', (equipment_id,))
            
            equipment = cursor.fetchone()
            if not equipment:
                return None, 'Техника не найдена'
            
            name, model = equipment
            
            # Создаем событие
            event_id = self.add_event(
                event_type='maintenance',
                title=f'Обслуживание: {name} ({model})',
                description=description,
                start_date=start_date,
                recurrence=f'FREQ=YEARLY;INTERVAL={maintenance_period}',
                related_record_type='техника',
                related_record_id=equipment_id,
                color='#ffc107',
                creator=creator
            )
            
            return event_id, None
    
    def add_warranty_event(self, equipment_id, title, description, warranty_end, creator=None):
        """Добавляет событие окончания гарантии"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Получаем информацию о технике
            cursor.execute('''
                SELECT название, модель
                FROM техника
                WHERE id = ?
            ''', (equipment_id,))
            
            equipment = cursor.fetchone()
            if not equipment:
                return None, 'Техника не найдена'
            
            name, model = equipment
            
            # Создаем событие
            event_id = self.add_event(
                event_type='warranty',
                title=f'Окончание гарантии: {name} ({model})',
                description=description,
                start_date=warranty_end,
                related_record_type='техника',
                related_record_id=equipment_id,
                color='#dc3545',
                creator=creator
            )
            
            return event_id, None
    
    def get_events_by_type(self, event_type, limit=50):
        return self.get_events(event_type=event_type, limit=limit)
    
    def get_events_by_record(self, record_type, record_id, limit=50):
        return self.get_events(
            related_record_type=record_type,
            related_record_id=record_id,
            limit=limit
        )

    def add_event_to_calendar(self, event_type, table, record_id, start_date, end_date=None, description=None):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO календарь (
                тип_события, таблица, запись_id, дата_начала, 
                дата_окончания, описание
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (event_type, table, record_id, start_date, end_date, description))
        conn.commit()
        conn.close()

    def get_events_from_calendar(self, start_date=None, end_date=None, event_type=None):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM календарь WHERE статус = "активное"'
        params = []
        
        if start_date:
            query += ' AND дата_начала >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND дата_начала <= ?'
            params.append(end_date)
        
        if event_type:
            query += ' AND тип_события = ?'
            params.append(event_type)
        
        query += ' ORDER BY дата_начала'
        
        cursor.execute(query, params)
        events = cursor.fetchall()
        conn.close()
        return events

    def update_event_in_calendar(self, event_id, **kwargs):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        allowed_fields = ['дата_начала', 'дата_окончания', 'описание', 'статус']
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f'{field} = ?')
                params.append(value)
        
        if updates:
            params.append(event_id)
            query = f'''
                UPDATE календарь 
                SET {', '.join(updates)}
                WHERE id = ?
            '''
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()

    def delete_event_from_calendar(self, event_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM календарь WHERE id = ?', (event_id,))
        conn.commit()
        conn.close()

    def generate_ical_from_calendar(self, events):
        cal = icalendar.Calendar()
        cal.add('prodid', '-//Система учета техники//mxm.dk//')
        cal.add('version', '2.0')
        
        for event in events:
            ical_event = icalendar.Event()
            ical_event.add('summary', f'{event["тип_события"]}: {event["описание"] or "Событие"}')
            ical_event.add('dtstart', datetime.strptime(event['дата_начала'], '%Y-%m-%d').date())
            
            if event['дата_окончания']:
                ical_event.add('dtend', datetime.strptime(event['дата_окончания'], '%Y-%m-%d').date())
            
            cal.add_component(ical_event)
        
        return cal.to_ical()

    def add_maintenance_event_to_calendar(self, equipment_id, start_date, description=None):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Получаем информацию о технике
        cursor.execute('SELECT название, модель FROM техника WHERE id = ?', (equipment_id,))
        equipment = cursor.fetchone()
        
        if equipment:
            event_description = f'Обслуживание: {equipment["название"]} ({equipment["модель"]})'
            if description:
                event_description += f' - {description}'
            
            self.add_event_to_calendar(
                'обслуживание',
                'техника',
                equipment_id,
                start_date,
                description=event_description
            )
        
        conn.close()

    def add_warranty_event_to_calendar(self, equipment_id, start_date, description=None):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Получаем информацию о технике
        cursor.execute('SELECT название, модель FROM техника WHERE id = ?', (equipment_id,))
        equipment = cursor.fetchone()
        
        if equipment:
            event_description = f'Гарантия: {equipment["название"]} ({equipment["модель"]})'
            if description:
                event_description += f' - {description}'
            
            self.add_event_to_calendar(
                'гарантия',
                'техника',
                equipment_id,
                start_date,
                description=event_description
            )
        
        conn.close()

    def get_events_by_type_from_calendar(self, event_type):
        return self.get_events_from_calendar(event_type=event_type)

    def get_events_by_record_from_calendar(self, table, record_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM календарь
            WHERE таблица = ? AND запись_id = ?
            ORDER BY дата_начала
        ''', (table, record_id))
        events = cursor.fetchall()
        conn.close()
        return events 