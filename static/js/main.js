// Импорт всех скриптов
import './utils.js';
import './users.js';
import './employees.js';
import './equipment.js';
import './reports.js';

document.addEventListener('DOMContentLoaded', () => {
    console.log('Все скрипты успешно загружены.');

    // Отладка: вывод данных о сотрудниках и технике в консоль
    console.log('Сотрудники:', {{ сотрудники | tojson }});
    console.log('Техника:', {{ техника | tojson }});

    // Фильтрация таблицы
    const rows = document.querySelectorAll('#analyticsTable tbody tr');
    const filters = document.querySelectorAll('.filter');

    // Добавляем обработчики событий для фильтров
    filters.forEach(filter => {
        filter.addEventListener('change', applyFilters);
        filter.addEventListener('input', applyFilters);
    });

    function applyFilters() {
        const employeeFilter = document.getElementById('filterEmployee').value;
        const equipmentFilter = document.getElementById('filterEquipment').value;
        const assignmentDateFilter = document.getElementById('filterAssignmentDate').value;
        const returnDateFilter = document.getElementById('filterReturnDate').value;
        const conditionFilter = document.getElementById('filterCondition').value;
        const statusFilter = document.getElementById('filterStatus').value;

        rows.forEach(row => {
            const employee = row.dataset.employee;
            const equipment = row.dataset.equipment;
            const assignmentDate = row.dataset.assignmentDate;
            const returnDate = row.dataset.returnDate;
            const condition = row.dataset.condition;
            const status = row.dataset.status;

            const matchesEmployee = !employeeFilter || employee === employeeFilter;
            const matchesEquipment = !equipmentFilter || equipment === equipmentFilter;
            const matchesAssignmentDate = !assignmentDateFilter || assignmentDate === assignmentDateFilter;
            const matchesReturnDate = !returnDateFilter || returnDate === returnDateFilter;
            const matchesCondition = !conditionFilter || condition === conditionFilter;
            const matchesStatus = !statusFilter || status === statusFilter;

            if (matchesEmployee && matchesEquipment && matchesAssignmentDate && matchesReturnDate && matchesCondition && matchesStatus) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    // Прикрепление техники
    document.querySelector('#assignEquipmentModal button[type="button"].btn-primary').addEventListener('click', submitAssignEquipment);

    function submitAssignEquipment() {
        const formData = $('#assignEquipmentForm').serializeArray().reduce((obj, item) => {
            obj[item.name] = item.value;
            return obj;
        }, {});

        fetch('/прикрепить_технику', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Техника успешно прикреплена!');
                    location.reload();
                } else {
                    alert('Ошибка: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Ошибка при отправке запроса:', error);
                alert('Произошла ошибка при отправке данных.');
            });
    }

    // Возврат техники
    document.querySelectorAll('.btn-danger').forEach(button => {
        button.addEventListener('click', event => {
            const назначениеId = event.target.dataset.id; // Убедитесь, что атрибут data-id установлен
            returnEquipment(назначениеId);
        });
    });

    function returnEquipment(назначениеId) {
        if (!confirm('Вы уверены, что хотите вернуть технику?')) return;

        fetch(`/вернуть_технику/${назначениеId}`, {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Техника успешно возвращена!');
                    location.reload();
                } else {
                    alert('Ошибка: ' + data.message);
                }
            });
    }
});