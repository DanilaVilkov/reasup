# tickets/signals.py

from django.conf import settings
from django.core.mail import EmailMessage
from email.utils import make_msgid
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Ticket

@receiver(pre_save, sender=Ticket)
def ticket_presave(sender, instance, **kwargs):
    """
    Сохраняем старые значения done_by и status перед сохранением,
    чтобы в post_save понять, что поменялось.
    """
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._old_done_by = old.done_by
            instance._old_status  = old.status
        except sender.DoesNotExist:
            instance._old_done_by = None
            instance._old_status  = None
    else:
        instance._old_done_by = None
        instance._old_status  = None

@receiver(post_save, sender=Ticket)
def ticket_postsave(sender, instance, created, **kwargs):
    """
    Отправка email при трёх событиях:
      1) создание заявки;
      2) назначение исполнителя;
      3) закрытие заявки.
    """
    if kwargs.get('raw', False):
        return

    ticket_id = instance.pk
    to_email= instance.email
    from_email = settings.DEFAULT_FROM_EMAIL
    base_subject = f"Заявка №{ticket_id} успешно создана"
    base_headers = {}
    if instance.email_message_id:
        base_headers = {
            'In-Reply-To': instance.email_message_id,
            'References': instance.email_message_id,
        }

    # 1) Новая заявка
    if created:
        subject = base_subject
        message = (
            f"Заявка №{ticket_id} успешно создана!\n"
            "Ваша заявка принята и будет обработана в ближайшее время."
        )
        msg_id = make_msgid()
        email = EmailMessage(
            subject,
            message,
            from_email,
            [to_email],
            headers={'Message-ID': msg_id},
        )
        email.send()
        Ticket.objects.filter(pk=ticket_id).update(email_message_id=msg_id)
        return

    # 2) Назначен исполнитель
    old_exec = getattr(instance, '_old_done_by', None)
    new_exec = instance.done_by
    if old_exec is None and new_exec is not None:
        exec_name = new_exec.get_full_name() or new_exec.username
        subject = f"Re: {base_subject}"
        message = (
            f"По вашей заявке №{ticket_id} назначен исполнитель: {exec_name}.\n"
            "Ожидайте выполнения."
        )
        email = EmailMessage(
            subject,
            message,
            from_email,
            [to_email],
            headers=base_headers,
        )
        email.send()

    # 3) Закрытие заявки
    old_status = getattr(instance, '_old_status', None)
    if old_status != instance.status and instance.status == 'closed':
        subject = f"Re: {base_subject}"
        message = (
            f"Заявка №{ticket_id} выполнена и закрыта.\n"
            "Спасибо за обращение!"
        )
        email = EmailMessage(
            subject,
            message,
            from_email,
            [to_email],
            headers=base_headers,
        )
        email.send()
