# tickets/admin.py

from django.contrib import admin, messages
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.safestring import mark_safe
from html import escape as html_escape  # для экранирования пользовательских данных
from django.forms.models import ModelChoiceField
from django.contrib.auth import get_user_model

from .models import Ticket, TicketImage
from .telegram_utils import send_new_ticket_notification

User = get_user_model()


class TicketImageInline(admin.TabularInline):
    model = TicketImage
    extra = 0
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" style="max-width:200px; max-height:200px;"/>'
                '</a>',
                obj.image.url
            )
        return ""
    image_tag.short_description = 'Фото'


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    change_list_template = "admin/tickets/ticket/change_list.html"

    exclude = ('created_by',)  # скрываем поле "Кто оформил заявку"

    list_display = (
        'ticket_number', 'created_at_formatted', 'location', 'task_summary', 'contact_info',
        'status', 'computer_name', 'done_by', 'has_images', 'send_to_telegram'
    )
    list_editable = ('done_by', 'status')
    list_filter = ('status', 'building', 'done_by')
    search_fields = ('full_name', 'email', 'computer_name', 'phone', 'office')
    ordering = ('-created_at',)
    inlines = [TicketImageInline]
    list_select_related = ('done_by',)

    def ticket_number(self, obj):
        return obj.pk
    ticket_number.short_description = 'Номер'

    def created_at_formatted(self, obj):
        return format_html(
            "<div>{}</div><div style='font-size:90%; color:#555;'>{}</div>",
            obj.created_at.strftime("%d.%m.%Y"),
            obj.created_at.strftime("%H:%M")
        )
    created_at_formatted.short_description = "Дата создания"

    def location(self, obj):
        return format_html(
            "<div>{}</div><div style='font-size:90%; color:#555;'>{}</div>",
            obj.building,
            obj.office
        )
    location.short_description = "Расположение"

    def task_summary(self, obj):
        text = obj.error_description or ""
        return text if len(text) < 50 else text[:47] + "..."
    task_summary.short_description = "Суть задачи"

    def contact_info(self, obj):
        phones = obj.phone
        if obj.internal_phone:
            phones += f" / {obj.internal_phone}"
        return format_html(
            "<div>{}</div><div style='font-size:90%; color:#555;'>{}</div>",
            html_escape(phones),
            html_escape(obj.full_name)
        )
    contact_info.short_description = "Контакт"

    def done_by(self, obj):
        if obj.done_by:
            last = obj.done_by.last_name or ''
            first = obj.done_by.first_name or ''
            if first:
                return f"{last} {first[0]}."
            return last
        return "Не указано"
    done_by.short_description = 'Исполнитель'

    def has_images(self, obj):
        if obj.images.exists():
            url = reverse('admin:tickets_ticket_images', args=[obj.pk])
            svg_img = mark_safe('''
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 40 40">
                  <path fill="#fff" d="M1.5 4.5H38.5V35.5H1.5z"></path>
                  <path fill="#788b9c" d="M38,5v30H2V5H38 M39,4H1v32h38V4L39,4z"></path>
                  <path fill="#b5deff" d="M6 9H34V26.875H6z"></path>
                  <path fill="#d9f6ff" d="M6 19H34V27H6z"></path>
                  <path fill="#7aadf0" d="M6 27H34V31H6z"></path>
                  <path fill="#d9f6ff" d="M14.75 15A3.5 3.143 0 1 0 14.75 21.286A3.5 3.143 0 1 0 14.75 15Z"></path>
                </svg>
            ''')
            return format_html('<a href="{}">{}</a>', url, svg_img)
        return format_html('<span style="color: red;">Нет</span>')
    has_images.short_description = 'Фото'

    def send_to_telegram(self, obj):
        url = reverse('admin:tickets_send_to_telegram', args=[obj.pk])
        svg_icon = mark_safe('''
            <svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px"
                 width="24" height="24" viewBox="0 0 48 48">
              <path fill="#29b6f6" d="M24 4A20 20 0 1 0 24 44A20 20 0 1 0 24 4Z"></path>
              <path fill="#fff" d="M33.95,15l-3.746,19.126c0,0-0.161,0.874-1.245,0.874
                  c-0.576,0-0.873-0.274-0.873-0.274l-8.114-6.733
                  l-3.97-2.001l-5.095-1.355c0,0-0.907-0.262-0.907-1.012
                  c0-0.625,0.933-0.923,0.933-0.923l21.316-8.468
                  c-0.001-0.001,0.651-0.235,1.126-0.234
                  C33.667,14,34,14.125,34,14.5C34,14.75,33.95,15,33.95,15z">
              </path>
            </svg>
        ''')
        return format_html('<a class="btn btn-telegram" href="{}">{}</a>', url, svg_icon)
    send_to_telegram.short_description = 'TG'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'done_by':
            qs = User.objects.all()
            class ExecutorChoiceField(ModelChoiceField):
                def label_from_instance(self, obj):
                    last = obj.last_name or ''
                    first = obj.first_name or ''
                    if first:
                        return f"{last} {first[0]}."
                    return last
            return ExecutorChoiceField(queryset=qs, required=not db_field.blank)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.done_by and obj.status == 'new':
            obj.status = 'in_progress'
        super().save_model(request, obj, form, change)

    def send_to_telegram_view(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        success, error = send_new_ticket_notification(ticket, request)
        if success:
            messages.success(request, "Уведомление отправлено в Telegram!")
        else:
            messages.error(request, f"Ошибка отправки в Telegram: {error}")
        return redirect(request.META.get('HTTP_REFERER', 'admin:index'))

    def ticket_images_view(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        images = ticket.images.all()
        context = {
            **self.admin_site.each_context(request),
            'ticket': ticket,
            'images': images,
            'opts': self.model._meta,
        }
        return render(request, 'admin/tickets/ticket/ticket_images.html', context)

    def set_status_view(self, request, ticket_id):
        from django.http import JsonResponse
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        new_status = request.POST.get('status')
        if new_status in dict(Ticket.STATUS_CHOICES):
            ticket.status = new_status
            ticket.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False}, status=400)

    def set_executor_view(self, request, ticket_id):
        from django.http import JsonResponse
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        user_id = request.POST.get('executor')
        try:
            user = User.objects.get(pk=user_id)
            ticket.done_by = user
            if ticket.status == 'new':
                ticket.status = 'in_progress'
            ticket.save()
            return JsonResponse({'success': True})
        except Exception:
            return JsonResponse({'success': False}, status=400)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('<int:ticket_id>/images/', self.admin_site.admin_view(self.ticket_images_view), name='tickets_ticket_images'),
            path('<int:ticket_id>/send_to_telegram/', self.admin_site.admin_view(self.send_to_telegram_view), name='tickets_send_to_telegram'),
            path('<int:ticket_id>/set_status/', self.admin_site.admin_view(self.set_status_view), name='tickets_set_status'),
            path('<int:ticket_id>/set_executor/', self.admin_site.admin_view(self.set_executor_view), name='tickets_set_executor'),
        ]
        return custom + urls

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('images')

    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request)
        stats = {
            'new':        {'label': 'Новая',     'count': qs.filter(status='new').count(),        'color': '#ffe0e0'},
            'in_progress':{'label': 'В работе',  'count': qs.filter(status='in_progress').count(), 'color': '#faffc3'},
            'closed':     {'label': 'Выполнено', 'count': qs.filter(status='closed').count(),     'color': '#e0ffe0'},
            'denied':     {'label': 'Отклонена', 'count': qs.filter(status='denied').count(),     'color': '#a7d7ff'},
        }
        extra_context = extra_context or {}
        extra_context['ticket_stats'] = stats
        return super().changelist_view(request, extra_context=extra_context)

    class Media:
        js = ('tickets/js/ticket_admin.js',)
        css = {'all': ('tickets/css/ticket_admin.css',)}
