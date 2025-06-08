# tickets/telegram_utils.py

import requests
from requests.exceptions import RequestException
from django.conf import settings
from html import escape

def send_new_ticket_notification(ticket, request=None):
    """
    Отправляет уведомление о заявке в Telegram.
    При миграции чата (400 с migrate_to_chat_id) автоматически перепосылает.
    Возвращает (True, None) при успехе или (False, описание ошибки) при неудаче.
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id   = settings.TELEGRAM_CHAT_ID
    if not bot_token or not chat_id:
        return False, "Не задан TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID"

    # Формируем текст сообщения, включая номер заявки и имя ПК (если есть)
    parts = [
        f"<b>Новая заявка №{ticket.id}</b>",
        f"<b>Дата:</b> {ticket.created_at.strftime('%d.%m.%Y %H:%M')}",
        f"<b>ФИО:</b> {escape(ticket.full_name)}",
        f"<b>Телефон:</b> {escape(ticket.phone)}",
    ]
    if getattr(ticket, 'internal_phone', None):
        parts.append(f"<b>Внутренний:</b> {escape(ticket.internal_phone)}")
    parts += [
        f"<b>Корпус:</b> {escape(ticket.building)}",
        f"<b>Кабинет:</b> {escape(ticket.office)}",
        f"<b>Задача:</b> {escape(ticket.error_description)}",
    ]
    if getattr(ticket, 'computer_name', None):
        parts.append(f"<b>Имя ПК:</b> {escape(ticket.computer_name)}")
    if ticket.images.exists():
        url = request.build_absolute_uri(ticket.images.first().image.url) if request else ticket.images.first().image.url
        parts.append(f"<b>Фото:</b> {escape(url)}")

    text = "\n".join(parts)
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True,
    }
    send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    try:
        resp = requests.post(send_url, data=payload, timeout=5)
    except RequestException as e:
        return False, f"Сетевая ошибка: {e}"

    # Если чат был обновлён до супергруппы — Telegram вернёт 400 + migrate_to_chat_id
    if resp.status_code == 400:
        try:
            err = resp.json()
            params = err.get('parameters', {})
            new_id = params.get('migrate_to_chat_id')
        except ValueError:
            new_id = None

        if new_id:
            # Пробуем перепослать сообщение в новый чат
            payload['chat_id'] = new_id
            try:
                resp2 = requests.post(send_url, data=payload, timeout=5)
            except RequestException as e2:
                return False, f"Сетевая ошибка при повторе: {e2}"
            if resp2.status_code == 200:
                return True, None
            return False, f"Telegram API after migrate {resp2.status_code}: {resp2.text}"

    # Обычная ошибка
    if resp.status_code != 200:
        try:
            detail = resp.json()
        except ValueError:
            detail = resp.text
        return False, f"Telegram API {resp.status_code}: {detail}"

    return True, None
