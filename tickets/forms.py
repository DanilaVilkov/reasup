from django import forms
from .models import Ticket
from django.utils.translation import gettext as _


class TicketForm(forms.ModelForm):
    # Поле "Имя ПК" - необязательное
    computer_name = forms.CharField(
        label=_("Имя ПК"),  # Локализованная метка
        required=False,  # Необязательное поле
        widget=forms.TextInput(attrs={
            'placeholder': _('Введите имя компьютера'),
            'class': 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 focus:border-primary focus:ring-primary'
        })
    )

    # Поле "Внутренний телефон" - обязательное
    internal_phone = forms.CharField(
        label=_("Внутренний телефон"),
        required=True,  # Обязательное поле
        widget=forms.TextInput(attrs={
            'placeholder': _('Введите внутренний номер'),
            'class': 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 focus:border-primary focus:ring-primary phone-mask'
        })
    )

    # Поле "Телефон" с маской ввода
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'phone-mask',  # Класс для маски телефона
            'placeholder': _('Введите номер телефона')
        }),
        label=_('Телефон')
    )

    class Meta:
        model = Ticket
        # Поля, которые будут отображаться в форме
        fields = [
            'full_name',  # ФИО
            'email',  # Email
            'phone',  # Телефон
            'internal_phone',  # Внутренний телефон (обязательно)
            'building',  # Корпус
            'office',  # Кабинет
            'error_description',  # Описание проблемы
            'computer_name',  # Имя ПК (необязательно)
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Настройка текстового поля для описания проблемы
        if 'error_description' in self.fields:
            self.fields['error_description'].widget.attrs['rows'] = 2  # Высота текстового поля

        # Общие стили Tailwind для всех полей ввода
        common_attrs = {
            'class': (
                'mt-1 block w-full px-3 py-2 border rounded-md '
                'focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary '
                'dark:bg-gray-700 dark:border-gray-600 dark:focus:ring-secondary'
            )
        }

        # Стандартные плейсхолдеры для полей
        placeholders = {
            'full_name': _('Введите ФИО'),
            'email': _('Введите email'),
            'building': _('Укажите корпус'),
            'office': _('Укажите кабинет'),
            'error_description': _('Опишите проблему'),
        }

        # Применение стилей и плейсхолдеров ко всем полям
        for name, field in self.fields.items():
            # Установка плейсхолдера, если он не задан явно
            if name in placeholders and not field.widget.attrs.get('placeholder'):
                field.widget.attrs['placeholder'] = placeholders[name]

            # Объединение существующих классов с общими стилями
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' ' + common_attrs['class']).strip()