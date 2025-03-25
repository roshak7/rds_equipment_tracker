from flask import Blueprint, flash, redirect, render_template, jsonify, request, url_for
from flask_login import login_required, current_user
from models import get_db_connection
from werkzeug.security import generate_password_hash
from utils import запись_лога

user_bp = Blueprint('users', __name__)

# Маршрут для отображения списка пользователей
@user_bp.route('/users')
@login_required
def users():
    # Проверка роли пользователя
    if current_user.role != 'admin':
        flash('У вас нет прав для просмотра этой страницы.', 'danger')
        return redirect(url_for('index'))
    
    # Получение данных из базы данных
    conn = get_db_connection()
    пользователи = conn.execute('SELECT * FROM пользователи').fetchall()
    conn.close()
    return render_template('users.html', пользователи=пользователи)

# Добавление пользователя
@user_bp.route('/добавить_пользователя', methods=['POST'])
@login_required
def добавить_пользователя():
    if current_user.role != 'admin':
        return jsonify({'status': 'error', 'message': 'Нет прав'})
    данные = request.get_json()
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO пользователи (username, password, role)
            VALUES (?, ?, ?)
        ''', (данные['username'], generate_password_hash(данные['password']), данные['role']))
        conn.commit()
        запись_лога(f"Добавлен пользователь: {данные['username']}", current_user.id)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        conn.close()

# Редактирование пользователя
@user_bp.route('/редактировать_пользователя/<int:user_id>', methods=['POST'])
@login_required
def редактировать_пользователя(user_id):
    if current_user.role != 'admin':
        return jsonify({'status': 'error', 'message': 'Нет прав'})
    данные = request.get_json()
    conn = get_db_connection()
    try:
        # Если пароль не указан, оставляем старый
        if 'password' in данные and данные['password']:
            conn.execute('''
                UPDATE пользователи
                SET username = ?, password = ?, role = ?
                WHERE id = ?
            ''', (данные['username'], generate_password_hash(данные['password']), данные['role'], user_id))
        else:
            conn.execute('''
                UPDATE пользователи
                SET username = ?, role = ?
                WHERE id = ?
            ''', (данные['username'], данные['role'], user_id))
        conn.commit()
        запись_лога(f"Отредактирован пользователь ID={user_id}", current_user.id)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        conn.close()

# Удаление пользователя
@user_bp.route('/удалить_пользователя/<int:user_id>', methods=['DELETE'])
@login_required
def удалить_пользователя(user_id):
    if current_user.role != 'admin':
        return jsonify({'status': 'error', 'message': 'Нет прав'})
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM пользователи WHERE id = ?', (user_id,))
        conn.commit()
        запись_лога(f"Удален пользователь ID={user_id}", current_user.id)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        conn.close()