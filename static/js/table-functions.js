document.addEventListener('DOMContentLoaded', () => {
    // Добавление строки
    document.getElementById('add-row').addEventListener('click', () => {
        const tableBody = document.querySelector('table tbody');
        const headers = document.querySelectorAll('table thead th');
        const newRow = document.createElement('tr');

        // Добавляем ячейки только для столбцов данных (исключаем столбец действий)
        for (let i = 0; i < headers.length - 1; i++) {
            const cell = document.createElement('td');
            cell.contentEditable = 'true';
            cell.textContent = ''; // Пустая ячейка
            newRow.appendChild(cell);
        }

        // Создаем ячейку для действий
        const actionsCell = document.createElement('td');
        actionsCell.innerHTML = `
            <button type="button" class="btn btn-sm btn-danger delete-row">🗑️ Удалить</button>
            <button type="button" class="btn btn-sm btn-secondary move-up">↑</button>
            <button type="button" class="btn btn-sm btn-secondary move-down">↓</button>`;
        newRow.appendChild(actionsCell);

        tableBody.appendChild(newRow);
    });

    // Обработчик удаления, перемещения вверх и вниз
    document.querySelector('table tbody').addEventListener('click', (e) => {
        if (e.target.classList.contains('delete-row')) {
            e.target.closest('tr').remove();
        } else if (e.target.classList.contains('move-up')) {
            const currentRow = e.target.closest('tr');
            const previousRow = currentRow.previousElementSibling;
            if (previousRow) {
                currentRow.parentNode.insertBefore(currentRow, previousRow);
            }
        } else if (e.target.classList.contains('move-down')) {
            const currentRow = e.target.closest('tr');
            const nextRow = currentRow.nextElementSibling;
            if (nextRow) {
                currentRow.parentNode.insertBefore(nextRow, currentRow);
            }
        }
    });

    // Отправка данных через fetch
    document.getElementById('table-form').addEventListener('submit', function (e) {
        e.preventDefault();

        const tableRows = document.querySelectorAll('table tbody tr');
        const tableData = [];

        // Сбор заголовков (исключаем последний столбец "Действия")
        const headers = Array.from(document.querySelectorAll('table thead th'))
            .slice(0, -1)
            .map(th => th.textContent.trim());
        tableData.push(headers);

        // Сбор данных строк
        tableRows.forEach(row => {
            const rowData = Array.from(row.querySelectorAll('td'))
                .slice(0, -1) // Исключаем последний столбец "Действия"
                .map(td => td.textContent.trim());
            if (rowData.length === headers.length) {
                tableData.push(rowData);
            }
        });

        // Отправка данных через fetch
        fetch(this.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ table_data: tableData })
        }).then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Таблица успешно сохранена!');
                } else {
                    alert('Ошибка: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Ошибка при сохранении таблицы:', error);
                alert('Произошла ошибка при сохранении.');
            });
    });
    // Преобразование времени в локальное
    document.querySelectorAll('.text-muted').forEach(element => {
        const utcTime = element.textContent.match(/Дата создания: (.+)/);
        if (utcTime && utcTime[1]) {
            const localTime = new Date(utcTime[1]).toLocaleString();
            element.textContent = `Дата создания: ${localTime}`;
        }
    });
});