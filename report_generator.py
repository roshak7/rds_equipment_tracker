import pandas as pd
from datetime import datetime
from models import get_db_connection
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

class ReportGenerator:
    @staticmethod
    def generate_equipment_report():
        conn = get_db_connection()
        
        # Получаем данные
        equipment = conn.execute('''
            SELECT название, модель, производитель, серийный_номер, 
                   дата_покупки, стоимость, состояние, статус
            FROM техника
            ORDER BY название
        ''').fetchall()
        
        # Создаем DataFrame
        df = pd.DataFrame(equipment, columns=[
            'Название', 'Модель', 'Производитель', 'Серийный номер',
            'Дата покупки', 'Стоимость', 'Состояние', 'Статус'
        ])
        
        # Создаем PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Добавляем заголовок
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        )
        elements.append(Paragraph("Отчет по технике", title_style))
        
        # Добавляем дату
        date_style = ParagraphStyle(
            'CustomDate',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.gray
        )
        elements.append(Paragraph(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}", date_style))
        elements.append(Spacer(1, 20))
        
        # Создаем таблицу
        table_data = [df.columns.tolist()] + df.values.tolist()
        
        # Стили для таблицы
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        
        table = Table(table_data)
        table.setStyle(style)
        elements.append(table)
        
        # Добавляем статистику
        elements.append(Spacer(1, 20))
        stats_style = ParagraphStyle(
            'CustomStats',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=10
        )
        
        total_equipment = len(equipment)
        assigned_equipment = len([e for e in equipment if e['статус'] == 'назначена'])
        maintenance_required = len([e for e in equipment if e['состояние'] == 'требует обслуживания'])
        
        elements.append(Paragraph(f"Всего техники: {total_equipment}", stats_style))
        elements.append(Paragraph(f"Назначено: {assigned_equipment}", stats_style))
        elements.append(Paragraph(f"Требует обслуживания: {maintenance_required}", stats_style))
        
        # Генерируем PDF
        doc.build(elements)
        buffer.seek(0)
        
        conn.close()
        return buffer
        
    @staticmethod
    def generate_assignment_report():
        conn = get_db_connection()
        
        # Получаем данные
        assignments = conn.execute('''
            SELECT с.имя || ' ' || с.фамилия as сотрудник,
                   т.название as техника,
                   н.дата_назначения,
                   н.дата_возврата,
                   н.статус
            FROM назначения н
            JOIN сотрудники с ON н.сотрудник_id = с.id
            JOIN техника т ON н.техника_id = т.id
            ORDER BY н.дата_назначения DESC
        ''').fetchall()
        
        # Создаем DataFrame
        df = pd.DataFrame(assignments, columns=[
            'Сотрудник', 'Техника', 'Дата назначения',
            'Дата возврата', 'Статус'
        ])
        
        # Создаем PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Добавляем заголовок
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        )
        elements.append(Paragraph("Отчет по назначениям", title_style))
        
        # Добавляем дату
        date_style = ParagraphStyle(
            'CustomDate',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.gray
        )
        elements.append(Paragraph(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}", date_style))
        elements.append(Spacer(1, 20))
        
        # Создаем таблицу
        table_data = [df.columns.tolist()] + df.values.tolist()
        
        # Стили для таблицы
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        
        table = Table(table_data)
        table.setStyle(style)
        elements.append(table)
        
        # Добавляем статистику
        elements.append(Spacer(1, 20))
        stats_style = ParagraphStyle(
            'CustomStats',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=10
        )
        
        total_assignments = len(assignments)
        active_assignments = len([a for a in assignments if a['статус'] == 'активное'])
        
        elements.append(Paragraph(f"Всего назначений: {total_assignments}", stats_style))
        elements.append(Paragraph(f"Активных назначений: {active_assignments}", stats_style))
        
        # Генерируем PDF
        doc.build(elements)
        buffer.seek(0)
        
        conn.close()
        return buffer 