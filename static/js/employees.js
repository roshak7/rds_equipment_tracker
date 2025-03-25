// Функция для отправки данных формы добавления сотрудника
function submitAddEmployee() {
    const formData = $('#addEmployeeForm').serializeArray().reduce((obj, item) => {
        obj[item.name] = item.value;
        return obj;
    }, {});

    sendRequest('/добавить_сотрудника', 'POST', formData)
        .then(response => {
            if (response && response.status === 'success') {
                location.reload();
            } else {
                alert('Ошибка при добавлении сотрудника: ' + (response?.message || 'Неизвестная ошибка'));
            }
        });
}

// Функция для загрузки данных сотрудника в форму редактирования
function loadEmployeeData(id, firstName, lastName, position, department, email, phone) {
    $('#editEmployeeId').val(id);
    $('#editFirstName').val(firstName);
    $('#editLastName').val(lastName);
    $('#editPosition').val(position || '');
    $('#editDepartment').val(department || '');
    $('#editEmail').val(email || '');
    $('#editPhone').val(phone || '');
}

// Функция для отправки данных формы редактирования сотрудника
function submitEditEmployee() {
    const formData = $('#editEmployeeForm').serializeArray().reduce((obj, item) => {
        obj[item.name] = item.value;
        return obj;
    }, {});
    const employeeId = $('#editEmployeeId').val();

    sendRequest(`/редактировать_сотрудника/${employeeId}`, 'POST', formData)
        .then(response => {
            if (response && response.status === 'success') {
                location.reload();
            } else {
                alert('Ошибка: ' + (response?.message || 'Неизвестная ошибка'));
            }
        });
}

// Функция для удаления сотрудника
function deleteEmployee(employeeId) {
    if (confirm("Вы уверены, что хотите удалить этого сотрудника?")) {
        sendRequest(`/удалить_сотрудника/${employeeId}`, 'DELETE')
            .then(response => {
                if (response && response.status === 'success') {
                    location.reload();
                } else {
                    alert('Ошибка при удалении сотрудника');
                }
            });
    }
}