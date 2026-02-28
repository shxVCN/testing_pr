"""
Модели приложения голосования.
"""
from django.db import models
from django.conf import settings


class Poll(models.Model):
    """Опрос с вариантами ответов."""
    question = models.CharField('Вопрос', max_length=255)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_polls',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'
        ordering = ['-created_at']

    def __str__(self):
        return self.question

    def get_total_votes(self):
        """Общее количество голосов по опросу."""
        return Vote.objects.filter(choice__poll=self).count()

    def user_has_voted(self, user):
        """Проверка, голосовал ли пользователь в этом опросе."""
        if not user.is_authenticated:
            return False
        return Vote.objects.filter(choice__poll=self, user=user).exists()


class Choice(models.Model):
    """Вариант ответа в опросе."""
    text = models.CharField('Текст варианта', max_length=200)
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name='Опрос'
    )

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'
        unique_together = [['poll', 'text']]

    def __str__(self):
        return f'{self.poll.question}: {self.text}'

    def get_votes_count(self):
        """Количество голосов за этот вариант."""
        return self.votes.count()


class Vote(models.Model):
    """Голос пользователя за вариант ответа."""
    voted_at = models.DateTimeField('Время голосования', auto_now_add=True)
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='Вариант'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Голос'
        verbose_name_plural = 'Голоса'
        unique_together = [['choice', 'user']]

    def __str__(self):
        return f'{self.user} -> {self.choice.text}'
