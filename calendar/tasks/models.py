"""
Модели приложения управления задачами и событиями.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Event(models.Model):
    """Событие с указанной датой и временем."""
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    date = models.DateField('Дата')
    time = models.TimeField('Время')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='Пользователь'
    )
    notify_minutes_before = models.PositiveIntegerField(
        'Уведомить за (минут)',
        default=15,
        help_text='За сколько минут до события показать уведомление'
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
        ordering = ['date', 'time']

    def __str__(self):
        return f'{self.title} ({self.date} {self.time})'

    def get_datetime(self):
        """Возвращает объединённые дату и время как datetime."""
        from datetime import datetime
        return timezone.make_aware(
            datetime.combine(self.date, self.time),
            timezone.get_current_timezone()
        )

    def is_upcoming(self, minutes_threshold=None):
        """
        Проверяет, является ли событие предстоящим (в пределах порога уведомления).
        Если minutes_threshold не указан, используется notify_minutes_before.
        """
        if minutes_threshold is None:
            minutes_threshold = self.notify_minutes_before

        event_datetime = self.get_datetime()
        now = timezone.now()
        threshold_end = event_datetime
        threshold_start = event_datetime - timezone.timedelta(minutes=minutes_threshold)

        return threshold_start <= now <= threshold_end

    def is_past(self):
        """Проверяет, прошло ли уже событие."""
        return self.get_datetime() < timezone.now()
