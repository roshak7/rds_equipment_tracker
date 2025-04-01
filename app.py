from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import init_db, get_db_connection, User, запись_лога
from validators import DataValidator
from scheduler import init_scheduler
from notifications import NotificationSystem
from qr_generator import QRGenerator
from report_generator import ReportGenerator
import io
from datetime import datetime
from excel_handler import ExcelHandler
from stats_manager import StatisticsManager
import os
import base64

app = Flask(__name__)
app.config.from_object(Config)

# Инициализация расширений
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Инициализация базы данных только если она не существует
if not os.path.exists(Config.DATABASE_PATH):
    init_db()

# Инициализация планировщика
scheduler = init_scheduler()

# Функция для загрузки пользователя
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM пользователи WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['role'])
    return None

# Маршрут для главной страницы
@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    
    # Получаем статистику
    stats = {
        'total_equipment': conn.execute('SELECT COUNT(*) as count FROM техника').fetchone()['count'],
        'assigned_equipment': conn.execute('SELECT COUNT(*) as count FROM назначения WHERE статус = "активное"').fetchone()['count'],
        'maintenance_required': conn.execute('SELECT COUNT(*) as count FROM техника WHERE состояние = "требует обслуживания"').fetchone()['count'],
        'faulty_equipment': conn.execute('SELECT COUNT(*) as count FROM техника WHERE состояние = "неисправное"').fetchone()['count'],
        'total_employees': conn.execute('SELECT COUNT(*) as count FROM сотрудники').fetchone()['count']
    }
    
    # Получаем последние назначения
    recent_assignments = conn.execute('''
        SELECT н.*, 
               с.фамилия || ' ' || с.имя || ' ' || с.отчество as employee_name,
               т.название as equipment_name,
               т.модель,
               т.серийный_номер
        FROM назначения н
        JOIN сотрудники с ON н.сотрудник_id = с.id
        JOIN техника т ON н.техника_id = т.id
        ORDER BY н.дата_назначения DESC
        LIMIT 5
    ''').fetchall()
    
    # Получаем технику, требующую обслуживания
    maintenance_required = conn.execute('''
        SELECT название as name, модель as model, состояние as status
        FROM техника
        WHERE состояние = "требует обслуживания"
        LIMIT 5
    ''').fetchall()
    
    # Получаем неисправную технику
    faulty_equipment = conn.execute('''
        SELECT название as name, модель as model, состояние as status
        FROM техника
        WHERE состояние = "неисправное"
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('index.html',
                         stats=stats,
                         recent_assignments=recent_assignments,
                         maintenance_required=maintenance_required,
                         faulty_equipment=faulty_equipment)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM пользователи WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and User.check_password(user['password'], password):
            user_obj = User(user['id'], user['username'], user['role'])
            login_user(user_obj)
            запись_лога(user['id'], 'Вход в систему')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    запись_лога(current_user.id, 'Выход из системы')
    logout_user()
    return redirect(url_for('login'))

@app.route('/employees')
@login_required
def employees():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем список сотрудников
    cursor.execute('SELECT * FROM сотрудники ORDER BY фамилия, имя')
    employees = cursor.fetchall()
    
    # Получаем списки для фильтров
    cursor.execute('SELECT DISTINCT отдел FROM сотрудники ORDER BY отдел')
    departments = [row['отдел'] for row in cursor.fetchall()]
    
    cursor.execute('SELECT DISTINCT должность FROM сотрудники ORDER BY должность')
    positions = [row['должность'] for row in cursor.fetchall()]
    
    conn.close()
    return render_template('employees.html', 
                         employees=employees,
                         departments=departments,
                         positions=positions)

@app.route('/employees', methods=['POST'])
@login_required
def add_employee():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO сотрудники (фамилия, имя, отчество, должность, отдел, email, телефон)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['фамилия'],
            data['имя'],
            data['отчество'],
            data['должность'],
            data['отдел'],
            data['email'],
            data['телефон']
        ))
        conn.commit()
        запись_лога(current_user.id, f"Добавлен сотрудник: {data['фамилия']} {data['имя']}")
        return jsonify({
            'success': True,
            'message': f'Сотрудник {data["фамилия"]} {data["имя"]} успешно добавлен в систему'
        })
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'Ошибка при добавлении сотрудника: {str(e)}'
        })
    finally:
        conn.close()

@app.route('/employees/<int:employee_id>')
@login_required
def get_employee(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM сотрудники WHERE id = ?', (employee_id,))
    employee = cursor.fetchone()
    conn.close()
    
    if employee:
        return jsonify(dict(employee))
    return jsonify({'success': False, 'message': 'Сотрудник не найден'}), 404

@app.route('/employees/<int:employee_id>', methods=['PUT'])
@login_required
def update_employee(employee_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE сотрудники 
            SET фамилия = ?, имя = ?, отчество = ?, должность = ?, отдел = ?, email = ?, телефон = ?
            WHERE id = ?
        ''', (
            data['фамилия'],
            data['имя'],
            data['отчество'],
            data['должность'],
            data['отдел'],
            data['email'],
            data['телефон'],
            employee_id
        ))
        conn.commit()
        запись_лога(current_user.id, f"Обновлен сотрудник: {data['фамилия']} {data['имя']}")
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@app.route('/employees/<int:employee_id>', methods=['DELETE'])
@login_required
def delete_employee(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Проверяем, есть ли активные назначения
        cursor.execute('SELECT COUNT(*) FROM назначения WHERE сотрудник_id = ? AND статус = ?', (employee_id, 'активное'))
        if cursor.fetchone()[0] > 0:
            return jsonify({'success': False, 'message': 'Нельзя удалить сотрудника с активными назначениями'})
        
        cursor.execute('DELETE FROM сотрудники WHERE id = ?', (employee_id,))
        conn.commit()
        запись_лога(current_user.id, f"Удален сотрудник с ID: {employee_id}")
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@app.route('/equipment', methods=['GET', 'POST'])
@login_required
def equipment():
    if request.method == 'POST':
        data = request.form.to_dict()
        validator = DataValidator()
        errors = validator.validate_equipment_data(data)
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('equipment'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO техника (
                    название, модель, производитель, серийный_номер,
                    дата_приобретения, гарантийный_срок, состояние, статус
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['название'],
                data['модель'],
                data['производитель'],
                data['серийный_номер'],
                data['дата_приобретения'],
                data['гарантийный_срок'],
                data['состояние'],
                'свободна'
            ))
            conn.commit()
            запись_лога(current_user.id, f'Добавлена новая техника: {data["название"]}')
            flash(f'Техника "{data["название"]}" успешно добавлена в систему', 'success')
            
        except Exception as e:
            conn.rollback()
            flash(f'Ошибка при добавлении техники: {str(e)}', 'danger')
        finally:
            conn.close()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем список техники с информацией о текущем владельце
    cursor.execute('''
        SELECT т.*, с.фамилия || ' ' || с.имя || ' ' || с.отчество as текущий_владелец
        FROM техника т
        LEFT JOIN сотрудники с ON т.текущий_владелец_id = с.id
        ORDER BY т.название
    ''')
    equipment_list = cursor.fetchall()
    
    # Получаем список производителей для фильтра
    cursor.execute('SELECT DISTINCT производитель FROM техника ORDER BY производитель')
    manufacturers = [row['производитель'] for row in cursor.fetchall()]
    
    conn.close()
    return render_template('equipment.html', 
                         equipment_list=equipment_list,
                         manufacturers=manufacturers)

@app.route('/assignments', methods=['GET', 'POST'])
@login_required
def assignments():
    if request.method == 'POST':
        data = request.form.to_dict()
        validator = DataValidator()
        errors = validator.validate_assignment_data(data)
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('assignments'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Проверяем статус техники
            cursor.execute('SELECT статус, название FROM техника WHERE id = ?', (data['техника_id'],))
            equipment = cursor.fetchone()
            
            if not equipment:
                flash('Техника не найдена', 'danger')
                return redirect(url_for('assignments'))
                
            if equipment['статус'] != 'свободна':
                flash('Невозможно назначить технику, которая не свободна', 'warning')
                return redirect(url_for('assignments'))
            
            # Создаем запись о назначении
            cursor.execute('''
                INSERT INTO назначения (
                    сотрудник_id, техника_id, дата_назначения,
                    дата_возврата, статус, причина_возврата
                ) VALUES (?, ?, CURRENT_DATE, ?, 'активное', NULL)
            ''', (data['сотрудник_id'], data['техника_id'], data.get('дата_возврата')))
            
            # Обновляем статус техники
            cursor.execute('''
                UPDATE техника 
                SET статус = 'назначена',
                    текущий_владелец_id = ?,
                    дата_последнего_назначения = CURRENT_DATE
                WHERE id = ?
            ''', (data['сотрудник_id'], data['техника_id']))
            
            conn.commit()
            запись_лога(current_user.id, f'Техника ID {data["техника_id"]} назначена сотруднику ID {data["сотрудник_id"]}')
            flash(f'Техника "{equipment["название"]}" успешно назначена сотруднику', 'success')
            
        except Exception as e:
            conn.rollback()
            flash(f'Ошибка при назначении техники: {str(e)}', 'danger')
        finally:
            conn.close()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем список назначений с информацией о сотрудниках и технике
    cursor.execute('''
        SELECT н.*, 
               с.фамилия || ' ' || с.имя || ' ' || с.отчество as сотрудник,
               т.название as техника,
               т.модель,
               т.серийный_номер,
               с.отдел
        FROM назначения н
        JOIN сотрудники с ON н.сотрудник_id = с.id
        JOIN техника т ON н.техника_id = т.id
        ORDER BY н.дата_назначения DESC
    ''')
    assignments = cursor.fetchall()
    
    # Получаем списки для фильтров
    cursor.execute('SELECT DISTINCT отдел FROM сотрудники ORDER BY отдел')
    departments = [row['отдел'] for row in cursor.fetchall()]
    
    # Получаем список типов техники для фильтра
    cursor.execute('SELECT DISTINCT название FROM техника ORDER BY название')
    equipment_types = [row['название'] for row in cursor.fetchall()]
    
    # Получаем список свободной техники
    cursor.execute('''
        SELECT * FROM техника 
        WHERE статус = 'свободна' 
        ORDER BY название
    ''')
    available_equipment = cursor.fetchall()
    
    # Получаем список сотрудников
    cursor.execute('SELECT * FROM сотрудники ORDER BY фамилия')
    employees = cursor.fetchall()
    
    conn.close()
    return render_template('assignments.html', 
                         assignments=assignments,
                         available_equipment=available_equipment,
                         employees=employees,
                         departments=departments,
                         equipment_types=equipment_types)

@app.route('/assignments/<int:assignment_id>/return', methods=['POST'])
@login_required
def return_equipment(assignment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Получаем информацию о назначении
        cursor.execute('''
            SELECT н.*, т.id as техника_id
            FROM назначения н
            JOIN техника т ON н.техника_id = т.id
            WHERE н.id = ?
        ''', (assignment_id,))
        assignment = cursor.fetchone()
        
        if not assignment:
            flash('Назначение не найдено')
            return redirect(url_for('assignments'))
            
        if assignment['статус'] != 'активное':
            flash('Невозможно вернуть технику из неактивного назначения')
            return redirect(url_for('assignments'))
        
        # Получаем причину возврата из формы
        причина_возврата = request.form.get('причина_возврата')
        
        # Обновляем запись о назначении
        cursor.execute('''
            UPDATE назначения 
            SET статус = 'завершено',
                дата_возврата = CURRENT_DATE,
                причина_возврата = ?
            WHERE id = ?
        ''', (причина_возврата, assignment_id))
        
        # Обновляем статус техники
        cursor.execute('''
            UPDATE техника 
            SET статус = 'свободна',
                текущий_владелец_id = NULL
            WHERE id = ?
        ''', (assignment['техника_id'],))
        
        conn.commit()
        запись_лога(current_user.id, f'Техника ID {assignment["техника_id"]} возвращена из назначения ID {assignment_id}')
        flash('Техника успешно возвращена')
        
    except Exception as e:
        conn.rollback()
        flash(f'Ошибка при возврате техники: {str(e)}')
    finally:
        conn.close()
    
    return redirect(url_for('assignments'))

@app.route('/equipment/<int:equipment_id>/maintenance', methods=['POST'])
@login_required
def send_to_maintenance(equipment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Проверяем, не назначена ли техника
        cursor.execute('SELECT статус FROM техника WHERE id = ?', (equipment_id,))
        equipment = cursor.fetchone()
        
        if not equipment:
            flash('Техника не найдена')
            return redirect(url_for('equipment'))
            
        if equipment['статус'] != 'свободна':
            flash('Невозможно отправить на обслуживание технику, которая назначена сотруднику')
            return redirect(url_for('equipment'))
        
        # Получаем данные из формы
        тип_обслуживания = request.form.get('тип_обслуживания')
        описание = request.form.get('описание')
        исполнитель = request.form.get('исполнитель')
        
        # Обновляем статус техники
        cursor.execute('''
            UPDATE техника 
            SET статус = 'в ремонте', состояние = 'требует обслуживания'
            WHERE id = ?
        ''', (equipment_id,))
        
        # Создаем запись об обслуживании
        cursor.execute('''
            INSERT INTO обслуживание (техника_id, тип_обслуживания, описание, исполнитель, дата_начала)
            VALUES (?, ?, ?, ?, CURRENT_DATE)
        ''', (equipment_id, тип_обслуживания, описание, исполнитель))
        
        conn.commit()
        запись_лога(current_user.id, f'Техника ID {equipment_id} отправлена на обслуживание')
        flash('Техника успешно отправлена на обслуживание')
        
    except Exception as e:
        conn.rollback()
        flash(f'Ошибка при отправке техники на обслуживание: {str(e)}')
    finally:
        conn.close()
    
    return redirect(url_for('equipment'))

@app.route('/equipment/<int:equipment_id>/complete_maintenance', methods=['POST'])
@login_required
def complete_maintenance(equipment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Проверяем, находится ли техника в ремонте
        cursor.execute('SELECT статус FROM техника WHERE id = ?', (equipment_id,))
        equipment = cursor.fetchone()
        
        if not equipment:
            flash('Техника не найдена')
            return redirect(url_for('equipment'))
            
        if equipment['статус'] != 'в ремонте':
            flash('Невозможно завершить обслуживание техники, которая не находится в ремонте')
            return redirect(url_for('equipment'))
        
        # Получаем следующую дату обслуживания из формы
        следующая_дата_обслуживания = request.form.get('следующая_дата_обслуживания')
        
        # Обновляем статус техники
        cursor.execute('''
            UPDATE техника 
            SET статус = 'свободна', 
                состояние = 'рабочее',
                дата_следующего_обслуживания = ?
            WHERE id = ?
        ''', (следующая_дата_обслуживания, equipment_id))
        
        # Обновляем запись об обслуживании
        cursor.execute('''
            UPDATE обслуживание 
            SET дата_завершения = CURRENT_DATE,
                статус = 'завершено'
            WHERE техника_id = ? AND дата_завершения IS NULL
        ''', (equipment_id,))
        
        conn.commit()
        запись_лога(current_user.id, f'Завершено обслуживание техники ID {equipment_id}')
        flash('Обслуживание техники успешно завершено')
        
    except Exception as e:
        conn.rollback()
        flash(f'Ошибка при завершении обслуживания: {str(e)}')
    finally:
        conn.close()
    
    return redirect(url_for('equipment'))

@app.route('/equipment/<int:equipment_id>/qr')
@login_required
def equipment_qr(equipment_id):
    buffer = QRGenerator.generate_equipment_qr(equipment_id)
    return send_file(
        buffer,
        mimetype='image/png',
        as_attachment=True,
        download_name=f'equipment_{equipment_id}_qr.png'
    )

@app.route('/equipment/batch-qr', methods=['POST'])
@login_required
def batch_qr():
    equipment_ids = request.form.getlist('equipment_ids[]')
    if not equipment_ids:
        flash('Выберите хотя бы одну единицу техники', 'error')
        return redirect(url_for('equipment'))
    
    buffer = QRGenerator.generate_batch_qr(equipment_ids)
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'equipment_qr_codes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )

@app.route('/reports/equipment')
@login_required
def equipment_report():
    buffer = ReportGenerator.generate_equipment_report()
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'equipment_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )

@app.route('/reports/assignments')
@login_required
def assignments_report():
    buffer = ReportGenerator.generate_assignment_report()
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'assignments_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )

@app.route('/equipment/<int:equipment_id>')
@login_required
def get_equipment(equipment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM техника WHERE id = ?', (equipment_id,))
    equipment = cursor.fetchone()
    conn.close()
    
    if equipment:
        return jsonify(dict(equipment))
    return jsonify({'success': False, 'message': 'Техника не найдена'}), 404

@app.route('/export/employees')
@login_required
def export_employees():
    output = ExcelHandler.export_employees()
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'employees_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@app.route('/export/equipment')
@login_required
def export_equipment():
    output = ExcelHandler.export_equipment()
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'equipment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@app.route('/export/assignments')
@login_required
def export_assignments():
    output = ExcelHandler.export_assignments()
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'assignments_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@app.route('/import/employees', methods=['POST'])
@login_required
def import_employees():
    if 'file' not in request.files:
        flash('Файл не выбран')
        return redirect(url_for('employees'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Файл не выбран')
        return redirect(url_for('employees'))
    
    success, message = ExcelHandler.import_employees(file)
    flash(message)
    return redirect(url_for('employees'))

@app.route('/import/equipment', methods=['POST'])
@login_required
def import_equipment():
    if 'file' not in request.files:
        flash('Файл не выбран')
        return redirect(url_for('equipment'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Файл не выбран')
        return redirect(url_for('equipment'))
    
    success, message = ExcelHandler.import_equipment(file)
    flash(message)
    return redirect(url_for('equipment'))

@app.route('/import/assignments', methods=['POST'])
@login_required
def import_assignments():
    if 'file' not in request.files:
        flash('Файл не выбран')
        return redirect(url_for('assignments'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Файл не выбран')
        return redirect(url_for('assignments'))
    
    success, message = ExcelHandler.import_assignments(file)
    flash(message)
    return redirect(url_for('assignments'))

@app.route('/import/warehouse', methods=['POST'])
@login_required
def import_warehouse():
    if 'file' not in request.files:
        flash('Файл не выбран', 'danger')
        return redirect(url_for('equipment'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Файл не выбран', 'danger')
        return redirect(url_for('equipment'))
    
    if not file.filename.endswith('.xls'):
        flash('Пожалуйста, загрузите файл в формате .xls', 'warning')
        return redirect(url_for('equipment'))
    
    success, message = ExcelHandler.import_warehouse_data(file)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('equipment'))

@app.route('/statistics')
@login_required
def statistics():
    stats_manager = StatisticsManager()
    
    # Получаем статистику
    equipment_stats = stats_manager.get_equipment_stats()
    employee_stats = stats_manager.get_employee_stats()
    assignment_stats = stats_manager.get_assignment_stats()
    
    # Генерируем графики
    equipment_chart = stats_manager.generate_equipment_chart()
    employee_chart = stats_manager.generate_employee_chart()
    assignment_chart = stats_manager.generate_assignment_chart()
    manufacturer_chart = stats_manager.generate_manufacturer_chart()
    position_chart = stats_manager.generate_position_chart()
    department_chart = stats_manager.generate_department_chart()
    
    return render_template('statistics.html',
                         equipment_stats=equipment_stats,
                         employee_stats=employee_stats,
                         assignment_stats=assignment_stats,
                         equipment_chart=equipment_chart,
                         employee_chart=employee_chart,
                         assignment_chart=assignment_chart,
                         manufacturer_chart=manufacturer_chart,
                         position_chart=position_chart,
                         department_chart=department_chart)

@app.route('/api/statistics')
@login_required
def get_filtered_statistics():
    period = request.args.get('period', '30')
    department = request.args.get('department', '')
    equipment_type = request.args.get('equipment_type', '')
    
    stats_manager = StatisticsManager()
    
    # Получаем статистику с учетом фильтров
    equipment_stats = stats_manager.get_equipment_stats(period, department, equipment_type)
    employee_stats = stats_manager.get_employee_stats(period, department)
    assignment_stats = stats_manager.get_assignment_stats(period, department)
    
    return jsonify({
        'equipment_stats': equipment_stats,
        'employee_stats': employee_stats,
        'assignment_stats': assignment_stats
    })

@app.route('/api/statistics/efficiency')
@login_required
def get_efficiency_stats():
    """Получение статистики эффективности использования техники"""
    period = request.args.get('period', '30')
    department = request.args.get('department', '')
    
    stats_manager = StatisticsManager()
    efficiency_stats = stats_manager.get_equipment_efficiency(period, department)
    
    return jsonify(efficiency_stats)

@app.route('/api/statistics/costs')
@login_required
def get_cost_stats():
    """Получение статистики стоимости владения техникой"""
    period = request.args.get('period', '30')
    department = request.args.get('department', '')
    
    stats_manager = StatisticsManager()
    cost_stats = stats_manager.get_equipment_cost_analysis(period, department)
    
    return jsonify(cost_stats)

@app.route('/api/statistics/maintenance')
@login_required
def get_maintenance_stats():
    """Получение статистики обслуживания и ремонтов"""
    period = request.args.get('period', '30')
    department = request.args.get('department', '')
    
    stats_manager = StatisticsManager()
    maintenance_stats = stats_manager.get_maintenance_analysis(period, department)
    
    return jsonify(maintenance_stats)

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
    app.run(debug=True, host='0.0.0.0', port=5000)