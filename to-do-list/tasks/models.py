"""
Модель задачи для приложения To-Do List.
"""
from django.db import models


class Task(models.Model):
    """Модель задачи с полями: название, описание, статус выполнения."""
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    completed = models.BooleanField('Выполнено', default=False)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
