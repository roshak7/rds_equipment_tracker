from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import get_db_connection, User  # Импортируем User из models.py
from werkzeug.security import check_password_hash
from utils import запись_лога

auth_bp = Blueprint('auth', __name__)

# Маршрут для входа
@auth_bp.route('/auths', methods=['GET', 'POST'])
def auths():
    if current_user.is_authenticated:
        # Если пользователь уже авторизован, перенаправляем на главную страницу
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Проверяем данные пользователя в базе данных
        conn = get_db_connection()
        user_data = conn.execute('SELECT * FROM пользователи WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user_data and check_password_hash(user_data['password'], password):
            # Создаем объект User для Flask-Login
            user = User(id=user_data['id'], username=user_data['username'], role=user_data['role'])
            login_user(user)  # Авторизуем пользователя
            запись_лога(f"Вход пользователя: {username}", user.id)
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль', 'danger')

    return render_template('auths.html')

# Маршрут для выхода
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('auth.auths'))