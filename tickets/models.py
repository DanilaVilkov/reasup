# tickets/models.py

from django.db import models
from django.contrib.auth.models import User

class Ticket(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('closed', 'Закрыта'),
        ('denied', 'Отклонена'),
    )

    full_name = models.CharField("ФИО", max_length=255)
    phone = models.CharField("Телефон", max_length=20)
    internal_phone = models.CharField("Внутренний номер", max_length=20, blank=True, null=True)
    building = models.CharField("Корпус", max_length=50)
    office = models.CharField("Кабинет", max_length=20)
    error_description = models.TextField("Суть задачи")
    computer_name = models.CharField(
        "Имя ПК",
        max_length=255,
        blank=True,
        null=True
    )
    email = models.EmailField("Email")
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='new')
    created_by = models.ForeignKey(
        User,
        related_name='tickets_created',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Кто оформил заявку"
    )
    done_by = models.ForeignKey(
        User,
        related_name='tickets_done',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Исполнитель"
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Заявка"          # для выпадающего списка: "Выберите Заявку для изменения"
        verbose_name_plural = "Заявки"   # для раздела: "Заявки"

    def __str__(self):
        return f"{self.full_name} - {self.get_status_display()}"


class TicketImage(models.Model):
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField("Фото", upload_to='ticket_photos/')

    class Meta:
        verbose_name = "Фото заявки"
        verbose_name_plural = "Фото заявки"

    def __str__(self):
        return f"Фото для заявки #{self.ticket.id}"
