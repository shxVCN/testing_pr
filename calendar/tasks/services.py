"""
Сервисы для логики уведомлений о предстоящих событиях.
"""
from django.utils import timezone
from .models import Event


def get_upcoming_events(user, minutes_ahead=60):
    """
    Возвращает события пользователя, которые начнутся в течение указанных минут.
    Используется для отображения уведомлений.
    """
    now = timezone.now()
    threshold = now + timezone.timedelta(minutes=minutes_ahead)

    events = Event.objects.filter(user=user).order_by('date', 'time')
    upcoming = []

    for event in events:
        event_dt = event.get_datetime()
        if now <= event_dt <= threshold and not event.is_past():
            upcoming.append(event)

    return upcoming


def get_events_needing_notification(user):
    """
    Возвращает события, для которых сейчас активен период уведомления.
    Событие считается требующим уведомления, если текущее время попадает
    в интервал [event_time - notify_minutes_before, event_time].
    """
    events = Event.objects.filter(user=user).order_by('date', 'time')
    return [e for e in events if e.is_upcoming()]
