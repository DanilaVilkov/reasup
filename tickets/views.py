# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import TicketForm
from .models import Ticket, TicketImage
from .telegram_utils import send_new_ticket_notification

def create_ticket(request):
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        image_files = request.FILES.getlist('image')

        if len(image_files) > 10:
            original_count = len(image_files)
            image_files = image_files[:10]
            messages.warning(
                request,
                f"Вы загрузили {original_count} изображений — будут сохранены только первые 10."
            )

        if ticket_form.is_valid():
            ticket = ticket_form.save(commit=False)
            if request.user.is_authenticated:
                ticket.created_by = request.user
            ticket.save()

            for image_file in image_files:
                TicketImage.objects.create(ticket=ticket, image=image_file)

            send_new_ticket_notification(ticket, request)
            # Теперь редиректим на URL с параметром ticket_id
            return redirect('ticket_success', ticket_id=ticket.pk)
    else:
        ticket_form = TicketForm()

    return render(request, 'tickets/create_ticket.html', {
        'ticket_form': ticket_form,
    })


def ticket_success(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    return render(request, 'tickets/ticket_success.html', {
        'ticket_number': ticket.pk
    })


def ticket_display(request):
    tickets = Ticket.objects.select_related('done_by')\
                            .prefetch_related('images')\
                            .order_by('-created_at')
    stats = {
        'new': tickets.filter(status__iexact='new').count(),
        'in_progress': tickets.filter(status__iexact='in_progress').count(),
        'closed': tickets.filter(status__iexact='closed').count(),
        'denied': tickets.filter(status__iexact='denied').count(),
    }
    for t in tickets:
        parts = t.full_name.split()
        if len(parts) == 3:
            t.name_line1 = f"{parts[0]} {parts[1]}"
            t.name_line2 = parts[2]
        else:
            t.name_line1 = t.full_name
            t.name_line2 = ""
    return render(request, 'tickets/ticket_display.html', {
        'tickets': tickets,
        'stats': stats,
    })


def ticket_list_partial(request):
    tickets = Ticket.objects.select_related('done_by')\
                            .prefetch_related('images')\
                            .order_by('-created_at')
    for t in tickets:
        parts = t.full_name.split()
        if len(parts) == 3:
            t.name_line1 = f"{parts[0]} {parts[1]}"
            t.name_line2 = parts[2]
        else:
            t.name_line1 = t.full_name
            t.name_line2 = ""
    return render(request, 'tickets/ticket_list_partial.html', {'tickets': tickets})


def public_ticket_images(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    images = ticket.images.all()
    return render(request, 'tickets/public_ticket_images.html', {
        'ticket': ticket,
        'images': images,
    })
