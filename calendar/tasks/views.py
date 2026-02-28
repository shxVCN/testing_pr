"""
Представления для управления событиями.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from .models import Event
from .forms import EventForm


def register_view(request):
    """Регистрация нового пользователя."""
    if request.user.is_authenticated:
        return redirect('tasks:event_list')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('tasks:event_list')
    else:
        form = UserCreationForm()

    return render(request, 'tasks/register.html', {'form': form})


@login_required
def event_list(request):
    """Список всех событий пользователя."""
    events = Event.objects.filter(user=request.user).order_by('date', 'time')
    return render(request, 'tasks/event_list.html', {'events': events})


@login_required
def event_create(request):
    """Создание нового события."""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            messages.success(request, 'Событие успешно создано!')
            return redirect('tasks:event_list')
    else:
        form = EventForm()

    return render(request, 'tasks/event_form.html', {
        'form': form,
        'title': 'Создать событие',
    })


@login_required
def event_edit(request, pk):
    """Редактирование события."""
    event = get_object_or_404(Event, pk=pk, user=request.user)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Событие успешно обновлено!')
            return redirect('tasks:event_list')
    else:
        form = EventForm(instance=event)

    return render(request, 'tasks/event_form.html', {
        'form': form,
        'event': event,
        'title': 'Редактировать событие',
    })


@login_required
def event_delete(request, pk):
    """Удаление события."""
    event = get_object_or_404(Event, pk=pk, user=request.user)

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Событие удалено.')
        return redirect('tasks:event_list')

    return render(request, 'tasks/event_confirm_delete.html', {'event': event})


@login_required
def event_detail(request, pk):
    """Детальный просмотр события."""
    event = get_object_or_404(Event, pk=pk, user=request.user)
    return render(request, 'tasks/event_detail.html', {'event': event})
