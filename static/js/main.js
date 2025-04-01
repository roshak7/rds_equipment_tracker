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

    // Анимация появления элементов при загрузке страницы
    document.querySelectorAll('.card').forEach(card => {
        card.classList.add('fade-in');
    });

    // Анимация для таблиц
    document.querySelectorAll('.table tbody tr').forEach((row, index) => {
        row.style.animation = `fadeIn 0.5s ease-out ${index * 0.1}s`;
    });

    // Инициализация всех подсказок Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Плавная прокрутка для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Анимация для кнопок
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Анимация для карточек статистики
    document.querySelectorAll('.stats-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Автоматическое скрытие уведомлений
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Улучшенная валидация форм
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    
                    // Создаем сообщение об ошибке
                    const feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    feedback.textContent = 'Это поле обязательно для заполнения';
                    field.parentNode.appendChild(feedback);
                } else {
                    field.classList.remove('is-invalid');
                    const feedback = field.parentNode.querySelector('.invalid-feedback');
                    if (feedback) {
                        feedback.remove();
                    }
                }
            });

            if (!isValid) {
                e.preventDefault();
                // Показываем сообщение об ошибке
                const errorAlert = document.createElement('div');
                errorAlert.className = 'alert alert-danger fade-in';
                errorAlert.textContent = 'Пожалуйста, заполните все обязательные поля';
                form.insertBefore(errorAlert, form.firstChild);
                
                // Автоматически скрываем сообщение через 5 секунд
                setTimeout(() => {
                    errorAlert.remove();
                }, 5000);
            }
        });
    });

    // Улучшенная работа с модальными окнами
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            this.classList.add('fade-in');
        });
        
        modal.addEventListener('hide.bs.modal', function() {
            this.classList.remove('fade-in');
        });
    });

    // Анимация для иконок
    document.querySelectorAll('.bi').forEach(icon => {
        icon.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.2)';
        });
        icon.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // Улучшенная работа с таблицами
    document.querySelectorAll('.table').forEach(table => {
        // Добавляем эффект при наведении на строки
        table.querySelectorAll('tbody tr').forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'rgba(74, 144, 226, 0.1)';
            });
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });

        // Добавляем сортировку по клику на заголовки
        table.querySelectorAll('thead th').forEach(header => {
            if (header.dataset.sortable !== 'false') {
                header.style.cursor = 'pointer';
                header.addEventListener('click', function() {
                    const tbody = table.querySelector('tbody');
                    const rows = Array.from(tbody.querySelectorAll('tr'));
                    const index = Array.from(this.parentNode.children).indexOf(this);
                    
                    rows.sort((a, b) => {
                        const aValue = a.children[index].textContent.trim();
                        const bValue = b.children[index].textContent.trim();
                        return aValue.localeCompare(bValue);
                    });
                    
                    rows.forEach(row => tbody.appendChild(row));
                });
            }
        });
    });

    // Управление темной темой
    initTheme();

    // Система уведомлений
    showNotification('Тема изменена', 'success');

    // Инициализация подсказок
    initTooltips();

    // Инициализация фильтров
    initFilters();

    // Инициализация графиков
    initCharts();

    // Добавляем класс page-transition к основному контенту
    document.querySelector('.container-fluid').classList.add('page-transition');
});

// Управление темной темой
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;
    
    // Проверяем сохраненную тему
    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    // Обработчик переключения темы
    themeToggle.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
        
        showNotification('Тема изменена', 'success');
    });
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('#themeToggle i');
    icon.className = theme === 'light' ? 'bi bi-moon-stars' : 'bi bi-sun';
}

// Система уведомлений
function showNotification(message, type = 'info') {
    const container = document.getElementById('notificationContainer');
    const notification = document.createElement('div');
    notification.className = `notification alert alert-${type}`;
    
    notification.innerHTML = `
        <div class="notification-content">
            <i class="bi ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">&times;</button>
    `;
    
    container.appendChild(notification);
    
    // Обработчик закрытия уведомления
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.remove();
    });
    
    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'bi-check-circle',
        error: 'bi-x-circle',
        warning: 'bi-exclamation-triangle',
        info: 'bi-info-circle'
    };
    return icons[type] || icons.info;
}

// Инициализация подсказок
function initTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.dataset.tooltip;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
            tooltip.style.left = rect.left + (rect.width - tooltip.offsetWidth) / 2 + 'px';
        });
        
        element.addEventListener('mouseleave', function() {
            document.querySelector('.tooltip')?.remove();
        });
    });
}

// Инициализация фильтров
function initFilters() {
    document.querySelectorAll('.filter-input').forEach(input => {
        input.addEventListener('input', debounce(function() {
            const filterValue = this.value.toLowerCase();
            const items = document.querySelectorAll('.filterable-item');
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                item.style.display = text.includes(filterValue) ? '' : 'none';
            });
        }, 300));
    });
}

// Инициализация графиков
function initCharts() {
    // График распределения техники
    const equipmentChart = document.getElementById('equipmentChart');
    if (equipmentChart) {
        new Chart(equipmentChart, {
            type: 'doughnut',
            data: {
                labels: ['Свободна', 'Назначена', 'В ремонте'],
                datasets: [{
                    data: [
                        parseInt(equipmentChart.dataset.free) || 0,
                        parseInt(equipmentChart.dataset.assigned) || 0,
                        parseInt(equipmentChart.dataset.maintenance) || 0
                    ],
                    backgroundColor: [
                        '#2ecc71',
                        '#3498db',
                        '#f1c40f'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

// Вспомогательные функции
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}