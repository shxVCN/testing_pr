"""
Контекстные процессоры для шаблонов.
"""
from .services import get_upcoming_events, get_events_needing_notification


def upcoming_events(request):
    """
    Добавляет в контекст предстоящие события и события, требующие уведомления.
    """
    context = {
        'upcoming_events': [],
        'notification_events': [],
    }

    if request.user.is_authenticated:
        context['upcoming_events'] = get_upcoming_events(request.user, minutes_ahead=60)
        context['notification_events'] = get_events_needing_notification(request.user)

    return context
