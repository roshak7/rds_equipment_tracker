// Функции для работы с уведомлениями
function showNotification(message, type = 'success', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.body.appendChild(notification);
    
    if (duration > 0) {
        setTimeout(() => {
            notification.remove();
        }, duration);
    }
}

// Функция для подтверждения действий
function confirmAction(message = 'Вы уверены, что хотите выполнить это действие?') {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Подтверждение</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
                        <button type="button" class="btn btn-primary" id="confirmBtn">Подтвердить</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
        
        document.getElementById('confirmBtn').addEventListener('click', () => {
            modalInstance.hide();
            resolve(true);
        });
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
            resolve(false);
        });
    });
}

// Функция для отображения индикатора загрузки
function showLoading(message = 'Загрузка...') {
    const loading = document.createElement('div');
    loading.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center';
    loading.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    loading.style.zIndex = '9999';
    loading.innerHTML = `
        <div class="text-center text-white">
            <div class="spinner-border mb-3" role="status">
                <span class="visually-hidden">Загрузка...</span>
            </div>
            <div>${message}</div>
        </div>
    `;
    document.body.appendChild(loading);
    return loading;
}

// Функция для работы с таблицами
class TableManager {
    constructor(tableId, options = {}) {
        this.table = document.getElementById(tableId);
        this.options = {
            pageSize: 10,
            ...options
        };
        this.currentPage = 1;
        this.data = [];
        this.filteredData = [];
        this.sortConfig = {
            column: null,
            direction: 'asc'
        };
        
        this.init();
    }
    
    init() {
        // Добавляем пагинацию
        this.addPagination();
        
        // Добавляем сортировку
        this.addSorting();
        
        // Добавляем поиск
        this.addSearch();
        
        // Инициализируем данные
        this.loadData();
    }
    
    loadData() {
        const rows = Array.from(this.table.querySelectorAll('tbody tr'));
        this.data = rows.map(row => ({
            element: row,
            data: Array.from(row.cells).map(cell => cell.textContent.trim())
        }));
        this.filteredData = [...this.data];
        this.updateTable();
    }
    
    updateTable() {
        const start = (this.currentPage - 1) * this.options.pageSize;
        const end = start + this.options.pageSize;
        const pageData = this.filteredData.slice(start, end);
        
        // Скрываем все строки
        this.data.forEach(item => item.element.style.display = 'none');
        
        // Показываем строки текущей страницы
        pageData.forEach(item => item.element.style.display = '');
        
        this.updatePagination();
    }
    
    addPagination() {
        const pagination = document.createElement('div');
        pagination.className = 'd-flex justify-content-between align-items-center mt-3';
        pagination.innerHTML = `
            <div class="btn-group">
                <button class="btn btn-outline-secondary" id="prevPage">Назад</button>
                <button class="btn btn-outline-secondary" id="nextPage">Вперед</button>
            </div>
            <div>
                <span id="pageInfo"></span>
            </div>
        `;
        this.table.parentNode.appendChild(pagination);
        
        document.getElementById('prevPage').addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.updateTable();
            }
        });
        
        document.getElementById('nextPage').addEventListener('click', () => {
            const maxPage = Math.ceil(this.filteredData.length / this.options.pageSize);
            if (this.currentPage < maxPage) {
                this.currentPage++;
                this.updateTable();
            }
        });
    }
    
    updatePagination() {
        const maxPage = Math.ceil(this.filteredData.length / this.options.pageSize);
        document.getElementById('pageInfo').textContent = 
            `Страница ${this.currentPage} из ${maxPage}`;
    }
    
    addSorting() {
        const headers = this.table.querySelectorAll('thead th');
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => this.sort(index));
        });
    }
    
    sort(column) {
        if (this.sortConfig.column === column) {
            this.sortConfig.direction = this.sortConfig.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortConfig.column = column;
            this.sortConfig.direction = 'asc';
        }
        
        this.filteredData.sort((a, b) => {
            const aValue = a.data[column];
            const bValue = b.data[column];
            
            if (this.sortConfig.direction === 'asc') {
                return aValue.localeCompare(bValue);
            } else {
                return bValue.localeCompare(aValue);
            }
        });
        
        this.currentPage = 1;
        this.updateTable();
    }
    
    addSearch() {
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control mb-3';
        searchInput.placeholder = 'Поиск...';
        this.table.parentNode.insertBefore(searchInput, this.table);
        
        searchInput.addEventListener('input', (e) => {
            const searchText = e.target.value.toLowerCase();
            this.filteredData = this.data.filter(item => 
                item.data.some(cell => cell.toLowerCase().includes(searchText))
            );
            this.currentPage = 1;
            this.updateTable();
        });
    }
}

// Функция для работы с кэшем
const cache = {
    data: new Map(),
    
    set(key, value, ttl = 3600) {
        const item = {
            value,
            expiry: Date.now() + ttl * 1000
        };
        this.data.set(key, item);
    },
    
    get(key) {
        const item = this.data.get(key);
        if (!item) return null;
        
        if (Date.now() > item.expiry) {
            this.data.delete(key);
            return null;
        }
        
        return item.value;
    },
    
    clear() {
        this.data.clear();
    }
};

// Функция для работы с фильтрами
function saveFilters(filters, key) {
    localStorage.setItem(`filters_${key}`, JSON.stringify(filters));
}

function loadFilters(key) {
    const saved = localStorage.getItem(`filters_${key}`);
    return saved ? JSON.parse(saved) : null;
}

// Функция для работы с файлами
function handleFileUpload(file, onSuccess, onError) {
    const formData = new FormData();
    formData.append('file', file);
    
    return fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            onSuccess(data);
        } else {
            onError(data.error);
        }
    })
    .catch(error => {
        onError(error.message);
    });
}

// Функция для работы с QR-кодами
function generateQRCode(text, size = 128) {
    const qr = new QRCode(document.createElement('div'), {
        text: text,
        width: size,
        height: size
    });
    return qr;
}

// Функция для работы с push-уведомлениями
async function requestNotificationPermission() {
    if (!('Notification' in window)) {
        console.log('Push-уведомления не поддерживаются');
        return false;
    }
    
    if (Notification.permission === 'granted') {
        return true;
    }
    
    const permission = await Notification.requestPermission();
    return permission === 'granted';
}

// Функция для работы с регулярными выражениями
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function createRegexFromSearch(searchText) {
    try {
        return new RegExp(searchText, 'i');
    } catch (e) {
        return new RegExp(escapeRegExp(searchText), 'i');
    }
}

// Функция для работы с датами
function formatDate(date) {
    return new Date(date).toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatDateTime(date) {
    return new Date(date).toLocaleString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Функция для работы с мобильным интерфейсом
function isMobile() {
    return window.innerWidth <= 768;
}

function adaptForMobile() {
    if (isMobile()) {
        document.body.classList.add('mobile');
        // Добавьте здесь дополнительную адаптацию для мобильных устройств
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    // Адаптация для мобильных устройств
    adaptForMobile();
    
    // Добавление tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Инициализация таблиц
    document.querySelectorAll('table[data-sortable]').forEach(table => {
        new TableManager(table.id, {
            pageSize: parseInt(table.dataset.pageSize) || 10
        });
    });
}); 