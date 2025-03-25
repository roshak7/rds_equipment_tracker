from flask import Blueprint, render_template, request, jsonify
from models import get_db_connection

# Создание Blueprint
employee_bp = Blueprint('employee', __name__)

# Маршрут для страницы управления сотрудниками
@employee_bp.route('/sotrudniki')
def sotrudniki():
    conn = get_db_connection()
    сотрудники = conn.execute('SELECT * FROM сотрудники').fetchall()
    conn.close()
    return render_template('sotrudniki.html', сотрудники=сотрудники)

# Маршрут для добавления сотрудника
@employee_bp.route('/добавить_сотрудника', methods=['POST'])
def добавить_сотрудника():
    данные = request.get_json()
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO сотрудники (имя, фамилия, должность, отдел, email, телефон)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            данные['имя'],
            данные['фамилия'],
            данные['должность'],
            данные['отдел'],
            данные['email'],
            данные['телефон']
        ))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        conn.close()

# Маршрут для редактирования сотрудника
@employee_bp.route('/редактировать_сотрудника/<int:employee_id>', methods=['POST'])
def редактировать_сотрудника(employee_id):
    данные = request.get_json()
    conn = get_db_connection()
    try:
        conn.execute('''
            UPDATE сотрудники
            SET имя = ?, фамилия = ?, должность = ?, отдел = ?, email = ?, телефон = ?
            WHERE id = ?
        ''', (
            данные['имя'],
            данные['фамилия'],
            данные['должность'],
            данные['отдел'],
            данные['email'],
            данные['телефон'],
            employee_id
        ))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        conn.close()

# Маршрут для удаления сотрудника
@employee_bp.route('/удалить_сотрудника/<int:employee_id>', methods=['DELETE'])
def удалить_сотрудника(employee_id):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM сотрудники WHERE id = ?', (employee_id,))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        conn.close()