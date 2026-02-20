"""
Сервисный слой: добавление/удаление книг, выдача и возврат.
"""
from django.db import transaction
from django.utils import timezone

from .models import Book, Reader, BookLoan


def add_book(title: str, author: str, isbn: str = '', year: int = None) -> Book:
    """Добавить книгу в библиотеку."""
    return Book.objects.create(title=title, author=author, isbn=isbn or '', year=year)


def delete_book(book_id: int) -> bool:
    """Удалить книгу по id. Возвращает True если удалена."""
    try:
        book = Book.objects.get(pk=book_id)
        book.delete()
        return True
    except Book.DoesNotExist:
        return False


def issue_book(book_id: int, reader_id: int) -> BookLoan | None:
    """Выдать книгу читателю. Возвращает BookLoan или None при ошибке."""
    try:
        book = Book.objects.get(pk=book_id)
        reader = Reader.objects.get(pk=reader_id)
        if BookLoan.objects.filter(book=book, returned_at__isnull=True).exists():
            return None  # книга уже на руках
        with transaction.atomic():
            return BookLoan.objects.create(book=book, reader=reader)
    except (Book.DoesNotExist, Reader.DoesNotExist):
        return None


def return_book(loan_id: int = None, book_id: int = None, reader_id: int = None):
    """
    Вернуть книгу. Можно указать loan_id либо (book_id + reader_id) для активной выдачи.
    Возвращает True если возврат выполнен, False иначе.
    """
    if loan_id:
        try:
            loan = BookLoan.objects.get(pk=loan_id, returned_at__isnull=True)
            loan.returned_at = timezone.now()
            loan.save()
            return True
        except BookLoan.DoesNotExist:
            return False
    if book_id is not None and reader_id is not None:
        try:
            loan = BookLoan.objects.get(book_id=book_id, reader_id=reader_id, returned_at__isnull=True)
            loan.returned_at = timezone.now()
            loan.save()
            return True
        except BookLoan.DoesNotExist:
            return False
    return False
