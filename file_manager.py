import os
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename
import magic
import hashlib

class FileManager:
    def __init__(self, db_path='equipment.db', upload_folder='uploads'):
        self.db_path = db_path
        self.upload_folder = upload_folder
        self.allowed_extensions = {
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png',
            'txt', 'rtf', 'zip', 'rar'
        }
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Создаем папку для загрузок, если она не существует
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
    
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_file(self, file, таблица, запись_id, пользователь_id):
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Добавляем timestamp к имени файла для уникальности
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            
            # Сохраняем файл
            file_path = os.path.join(self.upload_folder, unique_filename)
            file.save(file_path)
            
            # Сохраняем информацию о файле в базе данных
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO файлы (
                    таблица, запись_id, имя_файла, путь_к_файлу,
                    тип_файла, размер, загрузил_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                таблица,
                запись_id,
                filename,
                file_path,
                file.content_type,
                os.path.getsize(file_path),
                пользователь_id
            ))
            conn.commit()
            conn.close()
            
            return True, "Файл успешно загружен"
        return False, "Неподдерживаемый тип файла"
    
    def delete_file(self, file_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Получаем информацию о файле
        cursor.execute('SELECT путь_к_файлу FROM файлы WHERE id = ?', (file_id,))
        file_info = cursor.fetchone()
        
        if file_info:
            # Удаляем физический файл
            try:
                os.remove(file_info['путь_к_файлу'])
            except OSError:
                pass  # Игнорируем ошибку, если файл уже удален
            
            # Удаляем запись из базы данных
            cursor.execute('DELETE FROM файлы WHERE id = ?', (file_id,))
            conn.commit()
            conn.close()
            return True, "Файл успешно удален"
        
        conn.close()
        return False, "Файл не найден"
    
    def get_file_info(self, file_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ф.*, п.username as загрузил_username
            FROM файлы ф
            JOIN пользователи п ON ф.загрузил_id = п.id
            WHERE ф.id = ?
        ''', (file_id,))
        file_info = cursor.fetchone()
        conn.close()
        return file_info
    
    def get_files_by_record(self, таблица, запись_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ф.*, п.username as загрузил_username
            FROM файлы ф
            JOIN пользователи п ON ф.загрузил_id = п.id
            WHERE ф.таблица = ? AND ф.запись_id = ?
            ORDER BY ф.дата_загрузки DESC
        ''', (таблица, запись_id))
        files = cursor.fetchall()
        conn.close()
        return files
    
    def get_file_path(self, file_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT путь_к_файлу FROM файлы WHERE id = ?', (file_id,))
        file_info = cursor.fetchone()
        conn.close()
        return file_info['путь_к_файлу'] if file_info else None
    
    def format_file_size(self, size_in_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.1f} {unit}"
            size_in_bytes /= 1024
        return f"{size_in_bytes:.1f} TB"
    
    def get_file_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def get_file_type(self, file_path):
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path)
    
    def is_allowed_file(self, filename, file_type):
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        return ext in self.allowed_extensions.get(file_type, set())
    
    def save_file(self, file, record_type, record_id, file_type='documents'):
        if not file or not self.is_allowed_file(file.filename, file_type):
            return None, 'Неподдерживаемый тип файла'
        
        if file.content_length > self.max_file_size:
            return None, 'Файл слишком большой'
        
        try:
            # Создаем безопасное имя файла
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            
            # Создаем директорию для записи если её нет
            record_folder = os.path.join(self.upload_folder, record_type, str(record_id))
            os.makedirs(record_folder, exist_ok=True)
            
            # Сохраняем файл
            file_path = os.path.join(record_folder, unique_filename)
            file.save(file_path)
            
            # Получаем информацию о файле
            file_hash = self.get_file_hash(file_path)
            mime_type = self.get_file_type(file_path)
            
            return {
                'filename': unique_filename,
                'original_name': filename,
                'path': file_path,
                'hash': file_hash,
                'mime_type': mime_type,
                'size': file.content_length,
                'upload_date': datetime.now().isoformat()
            }, None
            
        except Exception as e:
            return None, str(e)
    
    def delete_file(self, file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True, None
            return False, 'Файл не найден'
        except Exception as e:
            return False, str(e)
    
    def get_file_info(self, file_path):
        if not os.path.exists(file_path):
            return None, 'Файл не найден'
        
        try:
            return {
                'filename': os.path.basename(file_path),
                'path': file_path,
                'size': os.path.getsize(file_path),
                'hash': self.get_file_hash(file_path),
                'mime_type': self.get_file_type(file_path),
                'modified_date': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            }, None
        except Exception as e:
            return None, str(e)
    
    def get_record_files(self, record_type, record_id):
        record_folder = os.path.join(self.upload_folder, record_type, str(record_id))
        if not os.path.exists(record_folder):
            return []
        
        files = []
        for filename in os.listdir(record_folder):
            file_path = os.path.join(record_folder, filename)
            file_info, error = self.get_file_info(file_path)
            if file_info:
                files.append(file_info)
        
        return sorted(files, key=lambda x: x['modified_date'], reverse=True)
    
    def cleanup_orphaned_files(self):
        """Удаляет файлы, которые не связаны с записями в базе данных"""
        try:
            # Получаем список всех файлов в uploads
            for root, dirs, files in os.walk(self.upload_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Здесь можно добавить проверку связи с базой данных
                    # Если файл не связан с записью, удаляем его
                    # os.remove(file_path)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def get_file_preview(self, file_path):
        """Генерирует превью для изображений"""
        try:
            from PIL import Image
            import io
            
            # Открываем изображение
            img = Image.open(file_path)
            
            # Создаем превью
            img.thumbnail((200, 200))
            
            # Конвертируем в байты
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            return img_byte_arr, None
        except Exception as e:
            return None, str(e)
    
    def compress_file(self, file_path):
        """Сжимает файл для экономии места"""
        try:
            import zipfile
            
            # Создаем имя для архива
            archive_path = file_path + '.zip'
            
            # Создаем ZIP архив
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_path, os.path.basename(file_path))
            
            # Удаляем оригинальный файл
            os.remove(file_path)
            
            return archive_path, None
        except Exception as e:
            return None, str(e) 