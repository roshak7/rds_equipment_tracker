import os
import shutil
import sqlite3
from datetime import datetime
import json

def create_backup():
    # Создаем директорию для бэкапов если её нет
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Создаем имя файла бэкапа с текущей датой и временем
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'backup_{timestamp}'
    backup_path = os.path.join(backup_dir, backup_name)
    
    # Создаем директорию для текущего бэкапа
    os.makedirs(backup_path)
    
    # Копируем базу данных
    shutil.copy2('equipment.db', os.path.join(backup_path, 'equipment.db'))
    
    # Копируем все файлы из директории uploads
    if os.path.exists('uploads'):
        shutil.copytree('uploads', os.path.join(backup_path, 'uploads'))
    
    # Создаем файл с информацией о бэкапе
    backup_info = {
        'timestamp': timestamp,
        'files': {
            'database': 'equipment.db',
            'uploads': 'uploads' if os.path.exists('uploads') else None
        },
        'system_info': {
            'python_version': os.sys.version,
            'platform': os.sys.platform
        }
    }
    
    with open(os.path.join(backup_path, 'backup_info.json'), 'w', encoding='utf-8') as f:
        json.dump(backup_info, f, ensure_ascii=False, indent=4)
    
    print(f'Бэкап успешно создан: {backup_path}')
    return backup_path

def restore_backup(backup_path):
    # Проверяем существование директории бэкапа
    if not os.path.exists(backup_path):
        print(f'Ошибка: директория бэкапа {backup_path} не найдена')
        return False
    
    try:
        # Восстанавливаем базу данных
        shutil.copy2(os.path.join(backup_path, 'equipment.db'), 'equipment.db')
        
        # Восстанавливаем файлы из uploads
        if os.path.exists('uploads'):
            shutil.rmtree('uploads')
        if os.path.exists(os.path.join(backup_path, 'uploads')):
            shutil.copytree(os.path.join(backup_path, 'uploads'), 'uploads')
        
        print(f'Бэкап успешно восстановлен из {backup_path}')
        return True
    except Exception as e:
        print(f'Ошибка при восстановлении бэкапа: {str(e)}')
        return False

def list_backups():
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        print('Директория бэкапов не найдена')
        return []
    
    backups = []
    for backup_name in os.listdir(backup_dir):
        backup_path = os.path.join(backup_dir, backup_name)
        if os.path.isdir(backup_path):
            info_file = os.path.join(backup_path, 'backup_info.json')
            if os.path.exists(info_file):
                with open(info_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    backups.append({
                        'name': backup_name,
                        'path': backup_path,
                        'timestamp': info['timestamp']
                    })
    
    return sorted(backups, key=lambda x: x['timestamp'], reverse=True)

if __name__ == '__main__':
    # Создаем бэкап
    backup_path = create_backup()
    
    # Выводим список всех бэкапов
    print('\nСписок доступных бэкапов:')
    backups = list_backups()
    for backup in backups:
        print(f"- {backup['name']} ({backup['timestamp']})") 