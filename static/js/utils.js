// Общая функция для отправки AJAX-запросов
function sendRequest(url, method = 'POST', data = {}) {
    return fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Сетевая ошибка');
            }
            return response.json();
        })
        .catch(error => {
            console.error('Ошибка при выполнении запроса:', error);
            alert('Произошла ошибка при отправке данных.');
        });
}