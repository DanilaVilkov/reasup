# tickets/models.py

from django.db import models
from django.contrib.auth.models import User


class Ticket(models.Model):
    """Модель заявки на техническую поддержку"""

    # Варианты статусов заявки
    STATUS_CHOICES = (
        ('new', 'Новая'),  # Новая, не назначенная заявка
        ('in_progress', 'В работе'),  # Заявка в работе
        ('closed', 'Закрыта'),  # Успешно завершенная заявка
        ('denied', 'Отклонена'),  # Отклоненная заявка
    )

    # Основные поля заявки
    full_name = models.CharField("ФИО", max_length=255)  # ФИО заявителя
    phone = models.CharField("Телефон", max_length=20)  # Контактный телефон
    internal_phone = models.CharField(
        "Внутренний номер",
        max_length=20,
        blank=True,
        null=True
    )  # Внутренний телефонный номер
    building = models.CharField("Корпус", max_length=50)  # Здание/корпус
    office = models.CharField("Кабинет", max_length=20)  # Номер кабинета
    error_description = models.TextField("Суть задачи")  # Описание проблемы

    # Необязательное поле с именем компьютера
    computer_name = models.CharField(
        "Имя ПК",
        max_length=255,
        blank=True,
        null=True
    )

    email = models.EmailField("Email")  # Электронная почта заявителя

    # Статус заявки с выбором из предопределенных вариантов
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )

    # Связь с пользователем, создавшим заявку
    created_by = models.ForeignKey(
        User,
        related_name='tickets_created',  # Обратное имя для связи
        on_delete=models.SET_NULL,  # При удалении пользователя заявка остается
        null=True,
        blank=True,
        verbose_name="Кто оформил заявку"
    )

    # Связь с пользователем-исполнителем
    done_by = models.ForeignKey(
        User,
        related_name='tickets_done',  # Обратное имя для связи
        on_delete=models.SET_NULL,  # При удалении пользователя заявка остается
        null=True,
        blank=True,
        verbose_name="Исполнитель"
    )

    # Дата создания заявки (автоматически устанавливается при создании)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Заявка"  # Название в единственном числе
        verbose_name_plural = "Заявки"  # Название во множественном числе
        ordering = ['-created_at']  # Сортировка по умолчанию (новые сначала)

    def __str__(self):
        """Строковое представление заявки"""
        return f"{self.full_name} - {self.get_status_display()}"  # Формат: "Иванов И.И. - В работе"


class TicketImage(models.Model):
    """Модель для прикрепленных изображений к заявке"""

    # Связь с заявкой (при удалении заявки все изображения удаляются)
    ticket = models.ForeignKey(
        'Ticket',
        on_delete=models.CASCADE,  # Каскадное удаление
        related_name='images'  # Обратное имя для связи
    )

    # Поле для загрузки изображения
    image = models.ImageField(
        "Фото",
        upload_to='ticket_photos/'  # Папка для загрузки
    )

    class Meta:
        verbose_name = "Фото заявки"  # Название в единственном числе
        verbose_name_plural = "Фото заявки"  # Название во множественном числе

    def __str__(self):
        """Строковое представление изображения"""
        return f"Фото для заявки #{self.ticket.id}"