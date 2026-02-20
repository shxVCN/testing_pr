"""
Модели системы управления книгами: книги, читатели, выдача/возврат.
"""
from django.db import models


class Book(models.Model):
    """Книга в библиотеке."""
    title = models.CharField('Название', max_length=200)
    author = models.CharField('Автор', max_length=200)
    isbn = models.CharField('ISBN', max_length=20, blank=True)
    year = models.PositiveIntegerField('Год издания', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['title']

    def __str__(self):
        return f'{self.title} ({self.author})'


class Reader(models.Model):
    """Читатель библиотеки."""
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Читатель'
        verbose_name_plural = 'Читатели'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class BookLoan(models.Model):
    """Выдача книги читателю (выдача и возврат)."""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans', verbose_name='Книга')
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name='loans', verbose_name='Читатель')
    issued_at = models.DateTimeField('Дата выдачи', auto_now_add=True)
    returned_at = models.DateTimeField('Дата возврата', null=True, blank=True)

    class Meta:
        verbose_name = 'Выдача книги'
        verbose_name_plural = 'Выдачи книг'
        ordering = ['-issued_at']

    def __str__(self):
        status = 'возвращена' if self.returned_at else 'на руках'
        return f'{self.book} — {self.reader} ({status})'

    @property
    def is_returned(self):
        return self.returned_at is not None
