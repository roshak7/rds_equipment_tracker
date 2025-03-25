from flask import Blueprint, render_template, jsonify
from models import get_db_connection

# Создание Blueprint
report_bp = Blueprint('report', __name__)

# Маршрут для страницы отчетов
@report_bp.route('/reports')
def reports():
    conn = get_db_connection()
    техника = conn.execute('SELECT * FROM техника').fetchall()
    сотрудники = conn.execute('SELECT * FROM сотрудники').fetchall()
    назначения = conn.execute('''
        SELECT назначения.*, сотрудники.имя AS сотрудник_имя, техника.название AS техника_название
        FROM назначения
        JOIN сотрудники ON назначения.сотрудник_id = сотрудники.id
        JOIN техника ON назначения.техника_id = техника.id
    ''').fetchall()
    conn.close()
    return render_template('reports.html', техника=техника, сотрудники=сотрудники, назначения=назначения)

# Маршрут для экспорта отчетов в JSON
@report_bp.route('/export_reports', methods=['GET'])
def export_reports():
    conn = get_db_connection()
    техника = conn.execute('SELECT * FROM техника').fetchall()
    сотрудники = conn.execute('SELECT * FROM сотрудники').fetchall()
    назначения = conn.execute('''
        SELECT назначения.*, сотрудники.имя AS сотрудник_имя, техника.название AS техника_название
        FROM назначения
        JOIN сотрудники ON назначения.сотрудник_id = сотрудники.id
        JOIN техника ON назначения.техника_id = техника.id
    ''').fetchall()
    conn.close()

    # Формируем JSON-ответ
    данные = {
        'техника': [dict(row) for row in техника],
        'сотрудники': [dict(row) for row in сотрудники],
        'назначения': [dict(row) for row in назначения]
    }
    return jsonify(данные)