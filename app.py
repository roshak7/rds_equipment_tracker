from flask import Flask, render_template
from flask_login import LoginManager, login_required, current_user
from config import Config
from models import init_db, get_db_connection, User  # Импортируем User из models.py

app = Flask(__name__)
app.config.from_object(Config)

# Инициализация расширений
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.auths'

# Функция для загрузки пользователя
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user_data = conn.execute('SELECT * FROM пользователи WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user_data:
        return User(id=user_data['id'], username=user_data['username'], role=user_data['role'])
    return None

# Маршрут для главной страницы
@app.route('/')
def index():
    return render_template('index.html')

# Инициализация базы данных и логирования
init_db()

# Регистрация маршрутов
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.equipment_routes import equipment_bp
from routes.employee_routes import employee_bp
from routes.report_routes import report_bp

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(equipment_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(report_bp)

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)