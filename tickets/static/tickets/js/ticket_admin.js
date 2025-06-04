// tickets/static/tickets/js/ticket_admin.js

document.addEventListener('DOMContentLoaded', function() {
  console.log('ticket_admin.js загружен');  // проверяем, что скрипт выполняется

  /** Получить CSRF-токен из куки **/
  function getCSRFToken() {
    const name = 'csrftoken=';
    return document.cookie
      .split(';')
      .map(c => c.trim())
      .filter(c => c.startsWith(name))
      .map(c => decodeURIComponent(c.slice(name.length)))[0] || '';
  }

  /** AJAX-обновление через эндпоинты set_status / set_executor **/
  function ajaxUpdate(ticketId, action, data, onSuccess, onError) {
    let base = window.location.pathname;
    if (!base.endsWith('/')) base += '/';
    const url = base + ticketId + '/' + action + '/';
    console.log('AJAX to', url, 'data=', data);
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCSRFToken()
      },
      body: new URLSearchParams(data)
    })
    .then(res => {
      console.log('Response status:', res.status, 'CT:', res.headers.get('Content-Type'));
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const ct = res.headers.get('Content-Type') || '';
      return ct.includes('application/json')
        ? res.json()
        : res.text().then(t => { throw new Error('Non-JSON response: ' + t); });
    })
    .then(json => {
      if (json.success) return onSuccess();
      throw new Error('Server returned success=false');
    })
    .catch(err => {
      console.error('ajaxUpdate error:', err);
      if (onError) onError(err);
      else alert('Ошибка сохранения: ' + err.message);
    });
  }

  /** Надёжное определение ticketId из строки **/
  function getTicketId(row) {
    // 1) data-object-pk
    if (row.dataset.objectPk) return row.dataset.objectPk;
    // 2) скрытый checkbox в первом столбце
    const cb = row.querySelector('input[type=checkbox][name="_selected_action"]');
    if (cb && cb.value) return cb.value;
    // 3) ячейка с классом field-ticket_number
    const numCell = row.querySelector('td.field-ticket_number, th.field-ticket_number');
    if (numCell) {
      const txt = numCell.textContent.trim();
      if (txt && /^\d+$/.test(txt)) return txt;
    }
    console.warn('ticketId не найден для строки:', row);
    return null;
  }

  /** --- главное: находим все строки таблицы change_list --- **/
  // в админке Django таблица имеет id="result_list"
  let rows = document.querySelectorAll('#result_list tbody tr');
  if (!rows.length) {
    rows = document.querySelectorAll('table.change-list tbody tr');
  }
  if (!rows.length) {
    rows = document.querySelectorAll('tbody tr');
  }

  rows.forEach(row => {
    // 1) раскраска по статусу
    const statusCell = row.querySelector('td.field-status');
    if (statusCell) {
      const sel = statusCell.querySelector('select');
      let txt = sel ? sel.value : statusCell.textContent.trim();
      txt = txt.toLowerCase();
      if (txt === 'new' || txt === 'новая') row.style.backgroundColor = '#ffe0e0';
      else if (txt === 'in_progress' || txt === 'в работе') row.style.backgroundColor = '#faffc3';
      else if (txt === 'closed' || txt === 'закрыта') row.style.backgroundColor = '#e0ffe0';
      else if (txt === 'denied' || txt === 'отклонена') row.style.backgroundColor = '#a7d7ff';
    }
    // общий стиль
    row.style.color = 'black';
    row.querySelectorAll('td, th').forEach(cell => {
      cell.style.verticalAlign = 'middle';
      cell.style.textAlign = 'center';
    });

    // находим ID заявки
    const ticketId = getTicketId(row);
    if (!ticketId) return;

    // 2) автосохранение статуса
    if (statusCell) {
      const sel = statusCell.querySelector('select');
      if (sel) {
        sel.addEventListener('change', function() {
          ajaxUpdate(ticketId, 'set_status', { status: this.value },
            () => location.reload(),
            err => alert('Не удалось сохранить статус:\n' + err.message)
          );
        });
      }
    }

    // 3) автосохранение исполнителя
    const execCell = row.querySelector('td.field-done_by');
    if (execCell) {
      const selExec = execCell.querySelector('select');
      if (selExec) {
        selExec.addEventListener('change', function() {
          ajaxUpdate(ticketId, 'set_executor', { executor: this.value },
            () => location.reload(),
            err => alert('Не удалось сохранить исполнителя:\n' + err.message)
          );
        });
      }
    }
  });
});
