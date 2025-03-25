// Функция для экспорта отчетов в Excel
function exportToExcel() {
    const table = document.getElementById('reportsTable');
    if (!table) {
        alert('Таблица отчетов не найдена.');
        return;
    }

    const rows = table.querySelectorAll('tr');
    let csvContent = "data:text/csv;charset=utf-8,";

    // Преобразуем таблицу в CSV
    rows.forEach(row => {
        const rowData = [];
        row.querySelectorAll('th, td').forEach(cell => {
            rowData.push(cell.innerText.replace(/,/g, ';')); // Заменяем запятые на точки с запятой
        });
        csvContent += rowData.join(",") + "\r\n";
    });

    // Создаем ссылку для скачивания
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "отчет.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}