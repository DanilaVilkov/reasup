# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('display/', views.ticket_display, name='ticket_display'),
    path('display/partial/', views.ticket_list_partial, name='ticket_list_partial'),
    path('ticket_images/<int:ticket_id>/', views.public_ticket_images, name='public_ticket_images'),
    path('create/', views.create_ticket, name='create_ticket'),
    # Меняем URL — теперь он принимает ticket_id
    path('success/<int:ticket_id>/', views.ticket_success, name='ticket_success'),
]
