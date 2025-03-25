from flask import Blueprint, render_template
from models import get_db_connection

main_bp = Blueprint('main', __name__)


from flask import Blueprint, jsonify, request
from models import get_db_connection
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/вернуть_технику/<int:назначение_id>', methods=['POST'])
def вернуть_технику(назначение_id):
    conn = get_db_connection()
    try:
        # Получаем информацию о назначении
        назначение = conn.execute('SELECT * FROM назначения WHERE id = ?', (назначение_id,)).fetchone()
        if not назначение:
            return jsonify({'status': 'error', 'message': 'Назначение не найдено'})

        # Обновляем дату возврата
        conn.execute('''
            UPDATE назначения
            SET дата_возврата = ?
            WHERE id = ?
        ''', (datetime.now().strftime('%Y-%m-%d'), назначение_id))

        # Обновляем статус техники на "Доступна"
        conn.execute('''
            UPDATE техника
            SET статус = 'Доступна'
            WHERE id = ?
        ''', (назначение['техника_id'],))
        conn.commit()

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        conn.close()
        
# Маршрут для прикрепления техники к сотруднику
@main_bp.route('/прикрепить_технику', methods=['POST'])
def прикрепить_технику():
    данные = request.get_json()
    сотрудник_id = данные['сотрудник_id']
    техника_id = данные['техника_id']
    дата_назначения = datetime.now().strftime('%Y-%m-%d')

    conn = get_db_connection()
    try:
        # Проверка, что техника доступна
        техника = conn.execute('SELECT * FROM техника WHERE id = ?', (техника_id,)).fetchone()
        if техника['статус'] != 'Доступна':
            return jsonify({'status': 'error', 'message': 'Техника недоступна'})

        # Добавляем запись о назначении
        conn.execute('''
            INSERT INTO назначения (сотрудник_id, техника_id, дата_назначения)
            VALUES (?, ?, ?)
        ''', (сотрудник_id, техника_id, дата_назначения))

        # Обновляем статус техники на "Недоступна"
        conn.execute('''
            UPDATE техника
            SET статус = 'Недоступна'
            WHERE id = ?
        ''', (техника_id,))
        conn.commit()

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        conn.close()

@main_bp.route('/')
def index():
    conn = get_db_connection()
    назначения = conn.execute('''
        SELECT назначения.id, 
               сотрудники.имя || ' ' || сотрудники.фамилия AS сотрудник,
               техника.название || ' (' || техника.серийный_номер || ')' AS техника,
               назначения.дата_назначения, 
               назначения.дата_возврата, 
               техника.состояние, 
               техника.статус
        FROM назначения
        JOIN сотрудники ON назначения.сотрудник_id = сотрудники.id
        JOIN техника ON назначения.техника_id = техника.id
    ''').fetchall()
    
    сотрудники = conn.execute('SELECT * FROM сотрудники').fetchall()
    техника = conn.execute('SELECT * FROM техника').fetchall()
    conn.close()
    
    return render_template('index.html', назначения=назначения, сотрудники=сотрудники, техника=техника)