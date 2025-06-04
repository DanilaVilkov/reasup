# tickets/apps.py

from django.apps import AppConfig

class TicketsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tickets"
    verbose_name = "Техническая поддержка"  # Название раздела в админке вместо "Tickets"

    def ready(self):
        # Регистрируем обработчики сигналов
        import tickets.signals
