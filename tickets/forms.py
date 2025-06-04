from django import forms
from .models import Ticket
from django.utils.translation import gettext as _

class TicketForm(forms.ModelForm):
    computer_name = forms.CharField(
        label=_("Имя ПК"),
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('Введите имя компьютера'),
            'class': 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 focus:border-primary focus:ring-primary'
        })
    )

    internal_phone = forms.CharField(
        label=_("Внутренний телефон"),
        required=True,  # <-- теперь обязательно
        widget=forms.TextInput(attrs={
            'placeholder': _('Введите внутренний номер'),
            'class': 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 focus:border-primary focus:ring-primary phone-mask'
        })
    )

    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'phone-mask',
            'placeholder': _('Введите номер телефона')
        }),
        label=_('Телефон')
    )

    class Meta:
        model = Ticket
        fields = [
            'full_name',
            'email',
            'phone',
            'internal_phone',   # обязательно
            'building',
            'office',
            'error_description',
            'computer_name',    # необязательно
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'error_description' in self.fields:
            self.fields['error_description'].widget.attrs['rows'] = 2

        # Общие Tailwind-классы для полей ввода
        common_attrs = {
            'class': (
                'mt-1 block w-full px-3 py-2 border rounded-md '  
                'focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary '  
                'dark:bg-gray-700 dark:border-gray-600 dark:focus:ring-secondary'
            )
        }
        # Плейсхолдеры по умолчанию (если не заданы в виджетах)
        placeholders = {
            'full_name': _('Введите ФИО'),
            'email': _('Введите email'),
            'building': _('Укажите корпус'),
            'office': _('Укажите кабинет'),
            'error_description': _('Опишите проблему'),
        }
        for name, field in self.fields.items():
            # Добавляем плейсхолдер, если требуется
            if name in placeholders and not field.widget.attrs.get('placeholder'):
                field.widget.attrs['placeholder'] = placeholders[name]
            # Объединяем классы
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' ' + common_attrs['class']).strip()