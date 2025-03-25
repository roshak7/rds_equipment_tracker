// Функция для отправки данных формы добавления пользователя
function submitAddUser() {
    const formData = $('#addUserForm').serializeArray().reduce((obj, item) => {
        obj[item.name] = item.value;
        return obj;
    }, {});

    sendRequest('/добавить_пользователя', 'POST', formData)
        .then(response => {
            if (response && response.status === 'success') {
                location.reload();
            } else {
                alert('Ошибка при добавлении пользователя: ' + (response?.message || 'Неизвестная ошибка'));
            }
        });
}

// Функция для загрузки данных пользователя в форму редактирования
function loadUserData(id, username, role) {
    $('#editUserId').val(id);
    $('#editUsername').val(username);
    $('#editRole').val(role);
}

// Функция для отправки данных формы редактирования пользователя
function submitEditUser() {
    const formData = $('#editUserForm').serializeArray().reduce((obj, item) => {
        obj[item.name] = item.value;
        return obj;
    }, {});
    const userId = $('#editUserId').val();

    sendRequest(`/редактировать_пользователя/${userId}`, 'POST', formData)
        .then(response => {
            if (response && response.status === 'success') {
                location.reload();
            } else {
                alert('Ошибка: ' + (response?.message || 'Неизвестная ошибка'));
            }
        });
}

// Функция для удаления пользователя
function deleteUser(userId) {
    if (confirm("Вы уверены, что хотите удалить этого пользователя?")) {
        sendRequest(`/удалить_пользователя/${userId}`, 'DELETE')
            .then(response => {
                if (response && response.status === 'success') {
                    location.reload();
                } else {
                    alert('Ошибка при удалении пользователя');
                }
            });
    }
}