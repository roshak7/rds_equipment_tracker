import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Используем бэкенд Agg для работы в неосновном потоке
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import io

class StatisticsManager:
    def __init__(self, db_path='equipment.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def get_db_connection(self):
        return self.conn

    def get_equipment_stats(self, period='30', department='', equipment_type=''):
        # Преобразуем period в число, если он передан
        period = int(period) if period else None
        
        # Базовый SQL запрос для общей статистики
        base_query = '''
                SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN состояние = 'рабочее' THEN 1 ELSE 0 END) as working,
                SUM(CASE WHEN состояние = 'требует обслуживания' THEN 1 ELSE 0 END) as maintenance_required,
                SUM(CASE WHEN состояние = 'неисправное' THEN 1 ELSE 0 END) as faulty
            FROM техника т
        '''
        
        # Добавляем условия WHERE только если они нужны
        where_conditions = []
        params = []
        
        if department:
            base_query += '''
                LEFT JOIN назначения н ON т.id = н.техника_id
                LEFT JOIN сотрудники с ON н.сотрудник_id = с.id
            '''
            where_conditions.append('с.отдел = ?')
            params.append(department)
        
        if equipment_type:
            where_conditions.append('т.название = ?')
            params.append(equipment_type)
        
        if period:
            if department or equipment_type:
                where_conditions.append('н.дата_назначения >= date("now", "-" || ? || " days")')
            else:
                where_conditions.append('т.дата_приобретения >= date("now", "-" || ? || " days")')
            params.append(period)
        
        # Добавляем WHERE только если есть условия
        if where_conditions:
            base_query += ' WHERE ' + ' AND '.join(where_conditions)
        
        # Выполняем запрос только если есть параметры
        if params:
            self.cursor.execute(base_query, params)
        else:
            self.cursor.execute(base_query)
            
        overall_stats = self.cursor.fetchone()
        
        # Преобразуем None в 0 для числовых значений
        overall_stats = {
            'total': overall_stats['total'] or 0,
            'working': overall_stats['working'] or 0,
            'maintenance_required': overall_stats['maintenance_required'] or 0,
            'faulty': overall_stats['faulty'] or 0
        }
            
            # Статистика по производителям
        manufacturer_query = '''
            SELECT производитель, COUNT(*) as count,
                SUM(CASE WHEN состояние = 'рабочее' THEN 1 ELSE 0 END) as working_count
            FROM техника т
        '''
        
        # Сбрасываем условия WHERE и параметры
        where_conditions = []
        params = []
        
        if department:
            manufacturer_query += '''
                LEFT JOIN назначения н ON т.id = н.техника_id
                LEFT JOIN сотрудники с ON н.сотрудник_id = с.id
            '''
            where_conditions.append('с.отдел = ?')
            params.append(department)
        
        if equipment_type:
            where_conditions.append('т.название = ?')
            params.append(equipment_type)
        
        if period:
            if department or equipment_type:
                where_conditions.append('н.дата_назначения >= date("now", "-" || ? || " days")')
            else:
                where_conditions.append('т.дата_приобретения >= date("now", "-" || ? || " days")')
            params.append(period)
        
        # Добавляем WHERE только если есть условия
        if where_conditions:
            manufacturer_query += ' WHERE ' + ' AND '.join(where_conditions)
        
        manufacturer_query += ' GROUP BY производитель ORDER BY count DESC LIMIT 5'
        
        # Выполняем запрос только если есть параметры
        if params:
            self.cursor.execute(manufacturer_query, params)
        else:
            self.cursor.execute(manufacturer_query)
            
        manufacturer_stats = self.cursor.fetchall()
        
        # Статистика по типам техники
        type_query = '''
            SELECT название as тип, COUNT(*) as count
            FROM техника т
        '''
        
        # Сбрасываем условия WHERE и параметры
        where_conditions = []
        params = []
        
        if department:
            type_query += '''
                LEFT JOIN назначения н ON т.id = н.техника_id
                LEFT JOIN сотрудники с ON н.сотрудник_id = с.id
            '''
            where_conditions.append('с.отдел = ?')
            params.append(department)
        
        if equipment_type:
            where_conditions.append('т.название = ?')
            params.append(equipment_type)
        
        if period:
            if department or equipment_type:
                where_conditions.append('н.дата_назначения >= date("now", "-" || ? || " days")')
            else:
                where_conditions.append('т.дата_приобретения >= date("now", "-" || ? || " days")')
            params.append(period)
        
        # Добавляем WHERE только если есть условия
        if where_conditions:
            type_query += ' WHERE ' + ' AND '.join(where_conditions)
        
        type_query += ' GROUP BY название ORDER BY count DESC'
        
        # Выполняем запрос только если есть параметры
        if params:
            self.cursor.execute(type_query, params)
        else:
            self.cursor.execute(type_query)
            
        type_stats = self.cursor.fetchall()
            
            return {
            'overall': overall_stats,
            'manufacturers': [dict(row) for row in manufacturer_stats],
            'types': [dict(row) for row in type_stats]
        }

    def get_employee_stats(self, period='30', department=''):
        # Базовый SQL запрос
        base_query = '''
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT отдел) as departments_count
            FROM сотрудники с
        '''
        
        # Добавляем JOIN с назначениями, если указан период
        if period:
            base_query += '''
                LEFT JOIN назначения н ON с.id = н.сотрудник_id
                WHERE н.дата_назначения >= date("now", "-" || ? || " days")
            '''
        
        # Добавляем фильтр по отделу
        if department:
            if period:
                base_query += ' AND с.отдел = ?'
            else:
                base_query += ' WHERE с.отдел = ?'
        
        # Подготавливаем параметры
        params = []
        if period:
            params.append(period)
        if department:
            params.append(department)
        
        # Выполняем запрос только если есть параметры
        if params:
            self.cursor.execute(base_query, params)
        else:
            self.cursor.execute(base_query)
            
        overall_stats = self.cursor.fetchone()
        
        # Преобразуем None в 0 для числовых значений
        overall_stats = {
            'total': overall_stats['total'] or 0,
            'departments_count': overall_stats['departments_count'] or 0
        }
            
            # Статистика по отделам
        department_query = '''
            SELECT 
                с.отдел,
                COUNT(DISTINCT с.id) as count,
                COUNT(DISTINCT н.техника_id) as equipment_count,
                COUNT(DISTINCT н.id) as assignments_count
            FROM сотрудники с
            LEFT JOIN назначения н ON с.id = н.сотрудник_id
        '''
        
        if period:
            department_query += ' WHERE н.дата_назначения >= date("now", "-" || ? || " days")'
        
        department_query += ' GROUP BY с.отдел ORDER BY count DESC'
        
        # Выполняем запрос только если есть параметры
        if period:
            self.cursor.execute(department_query, [period])
        else:
            self.cursor.execute(department_query)
            
        department_stats = self.cursor.fetchall()
            
            # Статистика по должностям
        position_query = '''
            SELECT должность, COUNT(*) as count
            FROM сотрудники с
        '''
        
        if period:
            position_query += '''
                LEFT JOIN назначения н ON с.id = н.сотрудник_id
                WHERE н.дата_назначения >= date("now", "-" || ? || " days")
            '''
        
        if department:
            if period:
                position_query += ' AND с.отдел = ?'
            else:
                position_query += ' WHERE с.отдел = ?'
        
        position_query += ' GROUP BY должность ORDER BY count DESC'
        
        # Выполняем запрос только если есть параметры
        if params:
            self.cursor.execute(position_query, params)
        else:
            self.cursor.execute(position_query)
            
        position_stats = self.cursor.fetchall()
            
            return {
            'overall': overall_stats,
            'departments': [dict(row) for row in department_stats],
            'positions': [dict(row) for row in position_stats]
        }

    def get_assignment_stats(self, period='30', department=''):
        # Базовый SQL запрос
        base_query = '''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN статус = 'активное' THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN статус = 'завершено' THEN 1 ELSE 0 END) as completed
            FROM назначения н
        '''
        
        # Добавляем JOIN с сотрудниками, если указан отдел
        if department:
            base_query += '''
                JOIN сотрудники с ON н.сотрудник_id = с.id
                WHERE с.отдел = ?
            '''
        
        # Добавляем фильтр по периоду
        if period:
            if department:
                base_query += ' AND н.дата_назначения >= date("now", "-" || ? || " days")'
            else:
                base_query += ' WHERE н.дата_назначения >= date("now", "-" || ? || " days")'
        
        # Подготавливаем параметры
        params = []
        if department:
            params.append(department)
        if period:
            params.append(period)
        
        # Выполняем запрос только если есть параметры
        if params:
            self.cursor.execute(base_query, params)
        else:
            self.cursor.execute(base_query)
            
        overall_stats = self.cursor.fetchone()
        
        # Преобразуем None в 0 для числовых значений
        overall_stats = {
            'total': overall_stats['total'] or 0,
            'active': overall_stats['active'] or 0,
            'completed': overall_stats['completed'] or 0
        }
        
        # Статистика по отделам
        department_query = '''
                SELECT 
                с.отдел,
                COUNT(*) as count
            FROM назначения н
            JOIN сотрудники с ON н.сотрудник_id = с.id
        '''
        
        if period:
            department_query += ' WHERE н.дата_назначения >= date("now", "-" || ? || " days")'
        
        department_query += ' GROUP BY с.отдел ORDER BY count DESC'
        
        # Выполняем запрос только если есть параметры
        if period:
            self.cursor.execute(department_query, [period])
        else:
            self.cursor.execute(department_query)
            
        department_stats = self.cursor.fetchall()
        
        # Статистика по месяцам
        monthly_query = '''
            SELECT 
                strftime('%Y-%m', дата_назначения) as month,
                COUNT(*) as count
                FROM назначения н
        '''
        
        if department:
            monthly_query += '''
                JOIN сотрудники с ON н.сотрудник_id = с.id
                WHERE с.отдел = ?
            '''
        
        if period:
            if department:
                monthly_query += ' AND н.дата_назначения >= date("now", "-" || ? || " days")'
            else:
                monthly_query += ' WHERE н.дата_назначения >= date("now", "-" || ? || " days")'
        
        monthly_query += '''
            GROUP BY month
            ORDER BY month DESC
                LIMIT 12
        '''
        
        # Выполняем запрос только если есть параметры
        if params:
            self.cursor.execute(monthly_query, params)
        else:
            self.cursor.execute(monthly_query)
            
        monthly_stats = self.cursor.fetchall()
            
            return {
            'overall': overall_stats,
            'departments': [dict(row) for row in department_stats],
            'monthly': [dict(row) for row in monthly_stats]
            }
    
    def generate_equipment_chart(self):
        stats = self.get_equipment_stats()
        
        # Очищаем предыдущие графики
        plt.clf()
        
        # Проверяем, есть ли данные для отображения
        total = sum([
            stats['overall']['working'],
            stats['overall']['maintenance_required'],
            stats['overall']['faulty']
        ])
        
        if total == 0:
            # Если данных нет, создаем пустой график с сообщением
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, 'Нет данных для отображения', 
                    ha='center', va='center', fontsize=14)
            plt.axis('off')
        else:
            # Создаем круговую диаграмму состояния техники
        plt.figure(figsize=(10, 6))
        
        values = [
            stats['overall']['working'],
            stats['overall']['maintenance_required'],
            stats['overall']['faulty']
        ]
        labels = ['Рабочее', 'Требует обслуживания', 'Неисправное']
        colors = ['#28a745', '#ffc107', '#dc3545']
        
        plt.pie(values, labels=labels, autopct='%1.1f%%', colors=colors)
        plt.title('Состояние техники')
        
        # Сохраняем график в буфер
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buf.seek(0)
        return buf
    
    def generate_employee_chart(self):
        stats = self.get_employee_stats()
        
        # Очищаем предыдущие графики
        plt.clf()
        
        # Проверяем, есть ли данные для отображения
        if not stats['departments']:
            # Если данных нет, создаем пустой график с сообщением
            plt.figure(figsize=(12, 6))
            plt.text(0.5, 0.5, 'Нет данных для отображения', 
                    ha='center', va='center', fontsize=14)
            plt.axis('off')
        else:
            # Создаем столбчатую диаграмму по отделам
            plt.figure(figsize=(12, 6))
            departments = [row['отдел'] for row in stats['departments']]
            counts = [row['count'] for row in stats['departments']]
            
            sns.barplot(x=departments, y=counts)
            plt.xticks(rotation=45, ha='right')
            plt.title('Распределение сотрудников по отделам')
            plt.xlabel('Отдел')
            plt.ylabel('Количество сотрудников')
            plt.tight_layout()
        
        # Сохраняем график в буфер
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buf.seek(0)
        return buf
    
    def generate_assignment_chart(self):
        stats = self.get_assignment_stats()
        
        # Очищаем предыдущие графики
        plt.clf()
        
        # Проверяем, есть ли данные для отображения
        if not stats['monthly']:
            # Если данных нет, создаем пустой график с сообщением
            plt.figure(figsize=(12, 6))
            plt.text(0.5, 0.5, 'Нет данных для отображения', 
                    ha='center', va='center', fontsize=14)
            plt.axis('off')
        else:
            # Создаем линейный график динамики назначений
        plt.figure(figsize=(12, 6))
            months = [row['month'] for row in stats['monthly']]
            counts = [row['count'] for row in stats['monthly']]
            
            plt.plot(months, counts, marker='o')
            plt.xticks(rotation=45, ha='right')
            plt.title('Динамика назначений по месяцам')
            plt.xlabel('Месяц')
            plt.ylabel('Количество назначений')
            plt.tight_layout()
        
        # Сохраняем график в буфер
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buf.seek(0)
        return buf

    def generate_manufacturer_chart(self):
        stats = self.get_equipment_stats()
        
        # Очищаем предыдущие графики
        plt.clf()
        
        # Проверяем, есть ли данные для отображения
        if not stats['manufacturers']:
            # Если данных нет, создаем пустой график с сообщением
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, 'Нет данных для отображения', 
                    ha='center', va='center', fontsize=14)
            plt.axis('off')
        else:
            # Создаем столбчатую диаграмму производителей
            plt.figure(figsize=(10, 6))
            manufacturers = [row['производитель'] for row in stats['manufacturers']]
            counts = [row['count'] for row in stats['manufacturers']]
            
            sns.barplot(x=manufacturers, y=counts)
            plt.xticks(rotation=45, ha='right')
            plt.title('Топ производителей')
            plt.xlabel('Производитель')
            plt.ylabel('Количество')
            plt.tight_layout()
        
        # Сохраняем график в буфер
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buf.seek(0)
        return buf

    def generate_position_chart(self):
        stats = self.get_employee_stats()
        
        # Очищаем предыдущие графики
        plt.clf()
        
        # Проверяем, есть ли данные для отображения
        if not stats['positions']:
            # Если данных нет, создаем пустой график с сообщением
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, 'Нет данных для отображения', 
                    ha='center', va='center', fontsize=14)
            plt.axis('off')
        else:
            # Создаем круговую диаграмму должностей
            plt.figure(figsize=(10, 6))
            positions = [row['должность'] for row in stats['positions']]
            counts = [row['count'] for row in stats['positions']]
            
            plt.pie(counts, labels=positions, autopct='%1.1f%%')
            plt.title('Распределение по должностям')
        
        # Сохраняем график в буфер
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buf.seek(0)
        return buf

    def generate_department_chart(self):
        stats = self.get_assignment_stats()
        
        # Очищаем предыдущие графики
        plt.clf()
        
        # Проверяем, есть ли данные для отображения
        if not stats['departments']:
            # Если данных нет, создаем пустой график с сообщением
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, 'Нет данных для отображения', 
                    ha='center', va='center', fontsize=14)
            plt.axis('off')
        else:
            # Создаем столбчатую диаграмму по отделам
            plt.figure(figsize=(10, 6))
            departments = [row['отдел'] for row in stats['departments']]
            counts = [row['count'] for row in stats['departments']]
            
            sns.barplot(x=departments, y=counts)
            plt.xticks(rotation=45, ha='right')
            plt.title('Распределение назначений по отделам')
            plt.xlabel('Отдел')
            plt.ylabel('Количество назначений')
            plt.tight_layout()
        
        # Сохраняем график в буфер
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buf.seek(0)
        return buf

    def get_equipment_efficiency(self, period='30', department=''):
        """Анализ эффективности использования техники"""
        # Базовый SQL запрос
        base_query = '''
            SELECT 
                т.id,
                т.наименование,
                т.название,
                т.состояние,
                COUNT(н.id) as total_assignments,
                SUM(CASE WHEN н.статус = 'активное' THEN 1 ELSE 0 END) as active_assignments,
                AVG(JULIANDAY(COALESCE(н.дата_завершения, 'now')) - JULIANDAY(н.дата_назначения)) as avg_usage_days,
                COUNT(DISTINCT н.сотрудник_id) as unique_users
            FROM техника т
            LEFT JOIN назначения н ON т.id = н.техника_id
        '''
        
        # Добавляем JOIN с сотрудниками, если указан отдел
        if department:
            base_query += '''
                LEFT JOIN сотрудники с ON н.сотрудник_id = с.id
                WHERE с.отдел = ?
            '''
        
        # Добавляем фильтр по периоду
        if period:
            if department:
                base_query += ' AND н.дата_назначения >= date("now", "-? days")'
            else:
                base_query += ' WHERE н.дата_назначения >= date("now", "-? days")'
        
        base_query += '''
            GROUP BY т.id
            ORDER BY total_assignments DESC
        '''
        
        # Подготавливаем параметры
        params = []
        if department:
            params.append(department)
        if period:
            params.append(period)
        
        # Выполняем запрос
        self.cursor.execute(base_query, params)
        efficiency_stats = self.cursor.fetchall()
        
        # Добавляем расчет эффективности
        for stat in efficiency_stats:
            # Коэффициент использования (активные назначения / общее количество назначений)
            stat['utilization_rate'] = round(
                (stat['active_assignments'] / stat['total_assignments'] * 100) 
                if stat['total_assignments'] > 0 else 0, 2
            )
            
            # Среднее время использования в днях
            stat['avg_usage_days'] = round(stat['avg_usage_days'] or 0, 1)
            
            # Коэффициент ротации (количество уникальных пользователей / общее количество назначений)
            stat['rotation_rate'] = round(
                (stat['unique_users'] / stat['total_assignments'] * 100) 
                if stat['total_assignments'] > 0 else 0, 2
            )
        
        return [dict(row) for row in efficiency_stats]

    def get_equipment_cost_analysis(self, period='30', department=''):
        """Анализ стоимости владения техникой"""
        # Базовый SQL запрос
        base_query = '''
                SELECT 
                т.id,
                т.наименование,
                т.название,
                т.стоимость,
                т.дата_приобретения,
                COUNT(о.id) as maintenance_count,
                SUM(о.стоимость) as maintenance_cost,
                COUNT(р.id) as repair_count,
                SUM(р.стоимость) as repair_cost,
                COUNT(н.id) as assignment_count,
                AVG(JULIANDAY(COALESCE(н.дата_завершения, 'now')) - JULIANDAY(н.дата_назначения)) as avg_usage_days
            FROM техника т
            LEFT JOIN назначения н ON т.id = н.техника_id
            LEFT JOIN обслуживание о ON т.id = о.техника_id
            LEFT JOIN ремонты р ON т.id = р.техника_id
        '''
        
        # Добавляем JOIN с сотрудниками, если указан отдел
        if department:
            base_query += '''
                LEFT JOIN сотрудники с ON н.сотрудник_id = с.id
                WHERE с.отдел = ?
            '''
        
        # Добавляем фильтр по периоду
        if period:
            if department:
                base_query += ' AND н.дата_назначения >= date("now", "-? days")'
            else:
                base_query += ' WHERE н.дата_назначения >= date("now", "-? days")'
        
        base_query += '''
            GROUP BY т.id
            ORDER BY т.стоимость DESC
        '''
        
        # Подготавливаем параметры
        params = []
        if department:
            params.append(department)
        if period:
            params.append(period)
        
        # Выполняем запрос
        self.cursor.execute(base_query, params)
        cost_stats = self.cursor.fetchall()
        
        # Добавляем расчеты стоимости владения
        for stat in cost_stats:
            # Общая стоимость владения
            stat['total_ownership_cost'] = (
                stat['стоимость'] + 
                (stat['maintenance_cost'] or 0) + 
                (stat['repair_cost'] or 0)
            )
            
            # Средняя стоимость обслуживания в день
            stat['avg_daily_maintenance_cost'] = round(
                ((stat['maintenance_cost'] or 0) / (stat['avg_usage_days'] or 1)), 2
            )
            
            # Средняя стоимость ремонта в день
            stat['avg_daily_repair_cost'] = round(
                ((stat['repair_cost'] or 0) / (stat['avg_usage_days'] or 1)), 2
            )
            
            # Общая стоимость в день
            stat['total_daily_cost'] = round(
                (stat['total_ownership_cost'] / (stat['avg_usage_days'] or 1)), 2
            )
            
            # ROI (Return on Investment)
            stat['roi'] = round(
                ((stat['assignment_count'] * 1000) / stat['total_ownership_cost'] * 100), 2
            )
        
        return [dict(row) for row in cost_stats]

    def get_maintenance_analysis(self, period='30', department=''):
        """Анализ обслуживания и ремонтов"""
        # Базовый SQL запрос
        base_query = '''
            SELECT 
                т.название,
                COUNT(DISTINCT т.id) as total_equipment,
                COUNT(о.id) as maintenance_count,
                SUM(о.стоимость) as maintenance_cost,
                AVG(JULIANDAY(о.дата_завершения) - JULIANDAY(о.дата_начала)) as avg_maintenance_duration,
                COUNT(р.id) as repair_count,
                SUM(р.стоимость) as repair_cost,
                AVG(JULIANDAY(р.дата_завершения) - JULIANDAY(р.дата_начала)) as avg_repair_duration
            FROM техника т
            LEFT JOIN обслуживание о ON т.id = о.техника_id
            LEFT JOIN ремонты р ON т.id = р.техника_id
        '''
        
        # Добавляем JOIN с назначениями и сотрудниками, если указан отдел
        if department:
            base_query += '''
                LEFT JOIN назначения н ON т.id = н.техника_id
                LEFT JOIN сотрудники с ON н.сотрудник_id = с.id
                WHERE с.отдел = ?
            '''
        
        # Добавляем фильтр по периоду
        if period:
            if department:
                base_query += ' AND (о.дата_начала >= date("now", "-? days") OR р.дата_начала >= date("now", "-? days"))'
            else:
                base_query += ' WHERE (о.дата_начала >= date("now", "-? days") OR р.дата_начала >= date("now", "-? days"))'
        
        base_query += '''
            GROUP BY т.название
            ORDER BY maintenance_count DESC
        '''
        
        # Подготавливаем параметры
        params = []
        if department:
            params.append(department)
        if period:
            params.extend([period, period])  # Для обоих условий в WHERE
        
        # Выполняем запрос
        self.cursor.execute(base_query, params)
        maintenance_stats = self.cursor.fetchall()
        
        # Добавляем расчеты
        for stat in maintenance_stats:
            # Средняя стоимость обслуживания на единицу техники
            stat['avg_maintenance_cost'] = round(
                ((stat['maintenance_cost'] or 0) / (stat['total_equipment'] or 1)), 2
            )
            
            # Средняя стоимость ремонта на единицу техники
            stat['avg_repair_cost'] = round(
                ((stat['repair_cost'] or 0) / (stat['total_equipment'] or 1)), 2
            )
            
            # Частота обслуживания (количество обслуживаний на единицу техники)
            stat['maintenance_frequency'] = round(
                ((stat['maintenance_count'] or 0) / (stat['total_equipment'] or 1)), 2
            )
            
            # Частота ремонтов (количество ремонтов на единицу техники)
            stat['repair_frequency'] = round(
                ((stat['repair_count'] or 0) / (stat['total_equipment'] or 1)), 2
            )
            
            # Средняя продолжительность обслуживания в днях
            stat['avg_maintenance_duration'] = round(stat['avg_maintenance_duration'] or 0, 1)
            
            # Средняя продолжительность ремонта в днях
            stat['avg_repair_duration'] = round(stat['avg_repair_duration'] or 0, 1)
        
        return [dict(row) for row in maintenance_stats]

    def get_equipment_utilization(self, days=30):
        # Получаем общее количество техники
        self.cursor.execute('SELECT COUNT(*) as total FROM техника')
        total_equipment = self.cursor.fetchone()['total'] or 0
            
            # Получаем количество техники в активных назначениях
        self.cursor.execute('''
            SELECT COUNT(DISTINCT техника_id) as assigned
                FROM назначения
                WHERE статус = 'активное'
            ''')
        assigned_equipment = self.cursor.fetchone()['assigned'] or 0
        
        if total_equipment > 0:
            utilization_rate = (assigned_equipment / total_equipment) * 100
        else:
            utilization_rate = 0
        
        return {
            'total': total_equipment,
            'assigned': assigned_equipment,
            'rate': round(utilization_rate, 2)
        } 