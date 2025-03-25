// Функция для отправки данных формы добавления техники
function submitAddEquipment() {
    const formData = $('#addEquipmentForm').serializeArray().reduce((obj, item) => {
        obj[item.name] = item.value;
        return obj;
    }, {});

    sendRequest('/добавить_технику', 'POST', formData)
        .then(response => {
            if (response && response.status === 'success') {
                location.reload();
            } else {
                alert('Ошибка при добавлении техники: ' + (response?.message || 'Неизвестная ошибка'));
            }
        });
}

// Функция для загрузки данных техники в форму редактирования
function loadEquipmentData(id, name, model, manufacturer, serialNumber, purchaseDate, cost, condition) {
    $('#editEquipmentId').val(id);
    $('#editName').val(name);
    $('#editModel').val(model);
    $('#editManufacturer').val(manufacturer);
    $('#editSerialNumber').val(serialNumber);
    $('#editPurchaseDate').val(purchaseDate);
    $('#editCost').val(cost);
    $('#editCondition').val(condition);
}

// Функция для отправки данных формы редактирования техники
function submitEditEquipment() {
    const formData = $('#editEquipmentForm').serializeArray().reduce((obj, item) => {
        obj[item.name] = item.value;
        return obj;
    }, {});
    const equipmentId = $('#editEquipmentId').val();

    sendRequest(`/редактировать_технику/${equipmentId}`, 'POST', formData)
        .then(response => {
            if (response && response.status === 'success') {
                location.reload();
            } else {
                alert('Ошибка: ' + (response?.message || 'Неизвестная ошибка'));
            }
        });
}

// Функция для удаления техники
function deleteEquipment(equipmentId) {
    if (confirm("Вы уверены, что хотите удалить эту технику?")) {
        sendRequest(`/удалить_технику/${equipmentId}`, 'DELETE')
            .then(response => {
                if (response && response.status === 'success') {
                    location.reload();
                } else {
                    alert('Ошибка при удалении техники');
                }
            });
    }
}