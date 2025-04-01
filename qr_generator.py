import qrcode
import io
from flask import send_file
from models import get_db_connection

class QRGenerator:
    @staticmethod
    def generate_equipment_qr(equipment_id):
        conn = get_db_connection()
        equipment = conn.execute('''
            SELECT название, модель, серийный_номер, состояние, статус
            FROM техника
            WHERE id = ?
        ''', (equipment_id,)).fetchone()
        conn.close()
        
        if not equipment:
            return None
            
        # Создаем данные для QR-кода
        qr_data = f"""
        Название: {equipment['название']}
        Модель: {equipment['модель']}
        Серийный номер: {equipment['серийный_номер']}
        Состояние: {equipment['состояние']}
        Статус: {equipment['статус']}
        """
        
        # Генерируем QR-код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Создаем изображение
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Сохраняем изображение в буфер
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer
        
    @staticmethod
    def generate_batch_qr(equipment_ids):
        conn = get_db_connection()
        equipment_list = conn.execute('''
            SELECT id, название, модель, серийный_номер
            FROM техника
            WHERE id IN ({})
        '''.format(','.join('?' * len(equipment_ids))), equipment_ids).fetchall()
        conn.close()
        
        if not equipment_list:
            return None
            
        # Создаем PDF с QR-кодами
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Добавляем QR-коды на страницу
        x, y = 1*inch, 7.5*inch
        for equipment in equipment_list:
            # Генерируем QR-код для каждого оборудования
            qr_buffer = QRGenerator.generate_equipment_qr(equipment['id'])
            if qr_buffer:
                # Добавляем QR-код на страницу
                c.drawImage(qr_buffer, x, y, width=1.5*inch, height=1.5*inch)
                
                # Добавляем текст
                c.setFont("Helvetica", 10)
                c.drawString(x, y-0.2*inch, f"{equipment['название']} ({equipment['серийный_номер']})")
                
                # Переходим к следующей позиции
                x += 2*inch
                if x > 7*inch:  # Если достигли конца строки
                    x = 1*inch
                    y -= 2*inch
                    if y < 1*inch:  # Если достигли конца страницы
                        c.showPage()
                        y = 7.5*inch
        
        c.save()
        buffer.seek(0)
        return buffer 