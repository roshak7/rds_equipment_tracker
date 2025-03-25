from flask import Blueprint, render_template, request, jsonify
from models import get_db_connection

# Создание Blueprint
equipment_bp = Blueprint('equipment', __name__)

# Маршрут для страницы управления техникой
@equipment_bp.route('/equipment_management')
def equipment_management():
    conn = get_db_connection()
    техника = conn.execute('SELECT * FROM техника').fetchall()
    conn.close()
    return render_template('equipment_management.html', техника=техника)

# Маршрут для добавления техники
@equipment_bp.route('/добавить_технику', methods=['POST'])
def добавить_технику():
    данные = request.get_json()
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO техника (название, модель, производитель, серийный_номер, дата_покупки, стоимость, состояние)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            данные['название'],
            данные['модель'],
            данные['производитель'],
            данные['серийный_номер'],
            данные['дата_покупки'],
            данные['стоимость'],
            данные['состояние']
        ))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        conn.close()

# Маршрут для редактирования техники
@equipment_bp.route('/редактировать_технику/<int:equipment_id>', methods=['POST'])
def редактировать_технику(equipment_id):
    данные = request.get_json()
    conn = get_db_connection()
    try:
        conn.execute('''
            UPDATE техника
            SET название = ?, модель = ?, производитель = ?, серийный_номер = ?, дата_покупки = ?, стоимость = ?, состояние = ?
            WHERE id = ?
        ''', (
            данные['название'],
            данные['модель'],
            данные['производитель'],
            данные['серийный_номер'],
            данные['дата_покупки'],
            данные['стоимость'],
            данные['состояние'],
            equipment_id
        ))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        conn.close()

# Маршрут для удаления техники
@equipment_bp.route('/удалить_технику/<int:equipment_id>', methods=['DELETE'])
def удалить_технику(equipment_id):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM техника WHERE id = ?', (equipment_id,))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        conn.close()