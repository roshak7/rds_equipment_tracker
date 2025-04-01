import pandas as pd
from datetime import datetime
from models import get_db_connection
import io

class ExcelHandler:
    @staticmethod
    def export_employees():
        conn = get_db_connection()
        df = pd.read_sql_query('SELECT * FROM сотрудники', conn)
        conn.close()
        
        # Форматируем данные
        df.columns = ['ID', 'Фамилия', 'Имя', 'Отчество', 'Должность', 'Отдел', 'Email', 'Телефон']
        
        # Создаем Excel файл
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Сотрудники', index=False)
            
            # Получаем объект workbook и worksheet
            workbook = writer.book
            worksheet = writer.sheets['Сотрудники']
            
            # Форматы
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4B0082',
                'font_color': 'white',
                'border': 1
            })
            
            # Применяем форматы
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 15)
        
        output.seek(0)
        return output

    @staticmethod
    def export_equipment():
        conn = get_db_connection()
        df = pd.read_sql_query('''
            SELECT т.*, с.фамилия || ' ' || с.имя || ' ' || с.отчество as текущий_владелец
            FROM техника т
            LEFT JOIN сотрудники с ON т.текущий_владелец_id = с.id
        ''', conn)
        conn.close()
        
        # Форматируем данные
        df.columns = ['ID', 'Название', 'Модель', 'Производитель', 'Серийный номер', 
                     'Дата приобретения', 'Гарантийный срок', 'Состояние', 'Статус',
                     'Текущий владелец ID', 'Дата последнего назначения', 
                     'Дата следующего обслуживания', 'Текущий владелец']
        
        # Создаем Excel файл
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Техника', index=False)
            
            # Получаем объект workbook и worksheet
            workbook = writer.book
            worksheet = writer.sheets['Техника']
            
            # Форматы
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4B0082',
                'font_color': 'white',
                'border': 1
            })
            
            # Применяем форматы
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 15)
        
        output.seek(0)
        return output

    @staticmethod
    def export_assignments():
        conn = get_db_connection()
        df = pd.read_sql_query('''
            SELECT н.*, 
                   с.фамилия || ' ' || с.имя || ' ' || с.отчество as сотрудник,
                   т.название as техника,
                   т.модель,
                   т.серийный_номер
            FROM назначения н
            JOIN сотрудники с ON н.сотрудник_id = с.id
            JOIN техника т ON н.техника_id = т.id
        ''', conn)
        conn.close()
        
        # Форматируем данные
        df.columns = ['ID', 'Сотрудник ID', 'Техника ID', 'Дата назначения', 
                     'Дата возврата', 'Статус', 'Причина возврата', 'Сотрудник',
                     'Техника', 'Модель', 'Серийный номер']
        
        # Создаем Excel файл
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Назначения', index=False)
            
            # Получаем объект workbook и worksheet
            workbook = writer.book
            worksheet = writer.sheets['Назначения']
            
            # Форматы
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4B0082',
                'font_color': 'white',
                'border': 1
            })
            
            # Применяем форматы
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 15)
        
        output.seek(0)
        return output

    @staticmethod
    def import_employees(file):
        try:
            df = pd.read_excel(file)
            conn = get_db_connection()
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO сотрудники (фамилия, имя, отчество, должность, отдел, email, телефон)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['Фамилия'],
                    row['Имя'],
                    row['Отчество'],
                    row['Должность'],
                    row['Отдел'],
                    row['Email'],
                    row['Телефон']
                ))
            
            conn.commit()
            conn.close()
            return True, "Данные успешно импортированы"
        except Exception as e:
            return False, f"Ошибка при импорте: {str(e)}"

    @staticmethod
    def import_equipment(file):
        try:
            df = pd.read_excel(file)
            conn = get_db_connection()
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO техника (
                        название, модель, производитель, серийный_номер,
                        дата_приобретения, гарантийный_срок, состояние, статус
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['Название'],
                    row['Модель'],
                    row['Производитель'],
                    row['Серийный номер'],
                    row['Дата приобретения'],
                    row['Гарантийный срок'],
                    row['Состояние'],
                    row['Статус']
                ))
            
            conn.commit()
            conn.close()
            return True, "Данные успешно импортированы"
        except Exception as e:
            return False, f"Ошибка при импорте: {str(e)}"

    @staticmethod
    def import_assignments(file):
        try:
            df = pd.read_excel(file)
            conn = get_db_connection()
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO назначения (
                        сотрудник_id, техника_id, дата_назначения,
                        дата_возврата, статус, причина_возврата
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    row['Сотрудник ID'],
                    row['Техника ID'],
                    row['Дата назначения'],
                    row['Дата возврата'],
                    row['Статус'],
                    row['Причина возврата']
                ))
            
            conn.commit()
            conn.close()
            return True, "Данные успешно импортированы"
        except Exception as e:
            return False, f"Ошибка при импорте: {str(e)}"

    @staticmethod
    def import_warehouse_data(file):
        """Импорт данных из файла склад.xls по категориям"""
        try:
            # Читаем Excel файл
            df = pd.read_excel(file)
            
            # Проверяем наличие необходимых колонок
            required_columns = ['Категория', 'Название', 'Модель', 'Производитель', 'Серийный номер', 
                              'Дата приобретения', 'Гарантийный срок', 'Состояние']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return False, f'Отсутствуют обязательные колонки: {", ".join(missing_columns)}'
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Счетчики для статистики
            stats = {
                'total': 0,
                'success': 0,
                'failed': 0,
                'categories': {}
            }
            
            # Группируем данные по категориям
            for category, group in df.groupby('Категория'):
                stats['categories'][category] = {
                    'total': len(group),
                    'success': 0,
                    'failed': 0
                }
                
                for _, row in group.iterrows():
                    stats['total'] += 1
                    try:
                        # Проверяем, существует ли уже техника с таким серийным номером
                        cursor.execute('SELECT id FROM техника WHERE серийный_номер = ?', (row['Серийный номер'],))
                        if cursor.fetchone():
                            stats['categories'][category]['failed'] += 1
                            stats['failed'] += 1
                            continue
                        
                        # Добавляем новую технику
                        cursor.execute('''
                            INSERT INTO техника (
                                название, модель, производитель, серийный_номер,
                                дата_приобретения, гарантийный_срок, состояние, статус
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            row['Название'],
                            row['Модель'],
                            row['Производитель'],
                            row['Серийный номер'],
                            row['Дата приобретения'],
                            row['Гарантийный срок'],
                            row['Состояние'],
                            'свободна'
                        ))
                        
                        stats['categories'][category]['success'] += 1
                        stats['success'] += 1
                        
                    except Exception as e:
                        stats['categories'][category]['failed'] += 1
                        stats['failed'] += 1
                        print(f"Ошибка при импорте записи: {str(e)}")
            
            conn.commit()
            conn.close()
            
            # Формируем сообщение о результатах
            message = f"Импорт завершен. Всего записей: {stats['total']}, "
            message += f"успешно: {stats['success']}, с ошибками: {stats['failed']}\n\n"
            message += "По категориям:\n"
            
            for category, cat_stats in stats['categories'].items():
                message += f"\n{category}:\n"
                message += f"- Всего: {cat_stats['total']}\n"
                message += f"- Успешно: {cat_stats['success']}\n"
                message += f"- С ошибками: {cat_stats['failed']}\n"
            
            return True, message
            
        except Exception as e:
            return False, f'Ошибка при импорте данных: {str(e)}' 