# Generated by Django 5.1.6 on 2025-06-06 10:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0005_ticket_computer_name_alter_ticket_done_by_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticket',
            options={'verbose_name': 'Заявка', 'verbose_name_plural': 'Заявки'},
        ),
        migrations.AlterModelOptions(
            name='ticketimage',
            options={'verbose_name': 'Фото заявки', 'verbose_name_plural': 'Фото заявки'},
        ),
    ]
