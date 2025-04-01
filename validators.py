import re
from datetime import datetime

class DataValidator:
    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone):
        pattern = r'^\+?[0-9]{10,15}$'
        return bool(re.match(pattern, phone))

    @staticmethod
    def validate_serial_number(serial_number):
        # Проверяем, что серийный номер не пустой и содержит только допустимые символы
        pattern = r'^[A-Za-z0-9-]+$'
        return bool(re.match(pattern, serial_number)) and len(serial_number) >= 3

    @staticmethod
    def validate_dates(start_date, end_date):
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            return start <= end
        except ValueError:
            return False

    @staticmethod
    def validate_cost(cost):
        try:
            cost = float(cost)
            return cost >= 0
        except ValueError:
            return False

    @staticmethod
    def validate_employee_data(data):
        errors = []
        
        if not data.get('имя') or len(data['имя']) < 2:
            errors.append('Имя должно содержать минимум 2 символа')
            
        if not data.get('фамилия') or len(data['фамилия']) < 2:
            errors.append('Фамилия должна содержать минимум 2 символа')
            
        if data.get('email') and not DataValidator.validate_email(data['email']):
            errors.append('Некорректный email')
            
        if data.get('телефон') and not DataValidator.validate_phone(data['телефон']):
            errors.append('Некорректный номер телефона')
            
        return errors

    @staticmethod
    def validate_equipment_data(data):
        errors = []
        
        if not data.get('название'):
            errors.append('Название техники обязательно')
            
        if not data.get('серийный_номер'):
            errors.append('Серийный номер обязателен')
        elif not DataValidator.validate_serial_number(data['серийный_номер']):
            errors.append('Некорректный серийный номер')
            
        if data.get('стоимость') and not DataValidator.validate_cost(data['стоимость']):
            errors.append('Некорректная стоимость')
            
        if data.get('дата_покупки'):
            try:
                datetime.strptime(data['дата_покупки'], '%Y-%m-%d')
            except ValueError:
                errors.append('Некорректная дата покупки')
                
        return errors

    @staticmethod
    def validate_assignment_data(data):
        errors = []
        
        if not data.get('сотрудник_id'):
            errors.append('ID сотрудника обязателен')
            
        if not data.get('техника_id'):
            errors.append('ID техники обязателен')
            
        if data.get('дата_возврата'):
            try:
                datetime.strptime(data['дата_возврата'], '%Y-%m-%d')
            except ValueError:
                errors.append('Некорректная дата возврата')
                
        return errors 