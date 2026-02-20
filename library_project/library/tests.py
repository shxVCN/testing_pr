"""
Юнит-тесты библиотеки: книги, выдача и возврат.
"""
from django.test import TestCase

from library.models import Book, Reader, BookLoan
from library.services import add_book, delete_book, issue_book, return_book


class AddBookTests(TestCase):
    """Тесты добавления книг."""

    def test_add_book_creates_record(self):
        """Добавление книги создаёт запись в БД."""
        book = add_book(title='Война и мир', author='Л. Толстой')
        self.assertIsNotNone(book.pk)
        self.assertEqual(book.title, 'Война и мир')
        self.assertEqual(book.author, 'Л. Толстой')
        self.assertEqual(Book.objects.count(), 1)

    def test_add_book_with_isbn_and_year(self):
        """Добавление книги с ISBN и годом."""
        book = add_book(
            title='Мастер и Маргарита',
            author='М. Булгаков',
            isbn='978-5-17-090831-2',
            year=1967,
        )
        self.assertEqual(book.isbn, '978-5-17-090831-2')
        self.assertEqual(book.year, 1967)

    def test_add_book_without_optional_fields(self):
        """Добавление книги без необязательных полей."""
        book = add_book(title='Книга', author='Автор')
        self.assertEqual(book.isbn, '')
        self.assertIsNone(book.year)

    def test_add_multiple_books(self):
        """Можно добавить несколько книг."""
        add_book(title='Книга 1', author='Автор 1')
        add_book(title='Книга 2', author='Автор 2')
        self.assertEqual(Book.objects.count(), 2)


class DeleteBookTests(TestCase):
    """Тесты удаления книг."""

    def test_delete_book_removes_record(self):
        """Удаление книги по id убирает запись из БД."""
        book = add_book(title='Удаляемая книга', author='Автор')
        pk = book.pk
        result = delete_book(pk)
        self.assertTrue(result)
        self.assertEqual(Book.objects.count(), 0)
        self.assertFalse(Book.objects.filter(pk=pk).exists())

    def test_delete_book_nonexistent_returns_false(self):
        """Удаление несуществующей книги возвращает False."""
        result = delete_book(99999)
        self.assertFalse(result)

    def test_delete_book_idempotent_after_delete(self):
        """Повторное удаление того же id возвращает False (книги уже нет)."""
        book = add_book(title='Книга', author='Автор')
        pk = book.pk
        delete_book(pk)
        result = delete_book(pk)
        self.assertFalse(result)


class IssueBookTests(TestCase):
    """Тесты выдачи книг."""

    def setUp(self):
        self.book = Book.objects.create(title='Книга', author='Автор')
        self.reader = Reader.objects.create(
            first_name='Иван',
            last_name='Иванов',
            email='ivan@example.com',
        )

    def test_issue_book_creates_loan(self):
        """Выдача книги создаёт запись выдачи."""
        loan = issue_book(self.book.pk, self.reader.pk)
        self.assertIsNotNone(loan)
        self.assertEqual(loan.book_id, self.book.pk)
        self.assertEqual(loan.reader_id, self.reader.pk)
        self.assertIsNone(loan.returned_at)
        self.assertTrue(BookLoan.objects.filter(book=self.book, reader=self.reader).exists())

    def test_issue_book_nonexistent_book_returns_none(self):
        """Выдача несуществующей книги возвращает None."""
        loan = issue_book(99999, self.reader.pk)
        self.assertIsNone(loan)
        self.assertEqual(BookLoan.objects.count(), 0)

    def test_issue_book_nonexistent_reader_returns_none(self):
        """Выдача книги несуществующему читателю возвращает None."""
        loan = issue_book(self.book.pk, 99999)
        self.assertIsNone(loan)
        self.assertEqual(BookLoan.objects.count(), 0)

    def test_issue_book_twice_same_book_returns_none(self):
        """Нельзя выдать одну и ту же книгу дважды, пока она не возвращена."""
        issue_book(self.book.pk, self.reader.pk)
        second_loan = issue_book(self.book.pk, self.reader.pk)
        self.assertIsNone(second_loan)
        self.assertEqual(BookLoan.objects.filter(book=self.book, returned_at__isnull=True).count(), 1)


class ReturnBookTests(TestCase):
    """Тесты возврата книг."""

    def setUp(self):
        self.book = Book.objects.create(title='Книга', author='Автор')
        self.reader = Reader.objects.create(
            first_name='Петр',
            last_name='Петров',
            email='petr@example.com',
        )

    def test_return_book_by_loan_id(self):
        """Возврат по id выдачи проставляет returned_at."""
        loan = BookLoan.objects.create(book=self.book, reader=self.reader)
        self.assertIsNone(loan.returned_at)
        result = return_book(loan_id=loan.pk)
        self.assertTrue(result)
        loan.refresh_from_db()
        self.assertIsNotNone(loan.returned_at)

    def test_return_book_by_book_and_reader(self):
        """Возврат по book_id и reader_id находит активную выдачу и возвращает книгу."""
        loan = BookLoan.objects.create(book=self.book, reader=self.reader)
        result = return_book(book_id=self.book.pk, reader_id=self.reader.pk)
        self.assertTrue(result)
        loan.refresh_from_db()
        self.assertIsNotNone(loan.returned_at)

    def test_return_nonexistent_loan_returns_false(self):
        """Возврат по несуществующему loan_id возвращает False."""
        result = return_book(loan_id=99999)
        self.assertFalse(result)

    def test_return_already_returned_loan_returns_false(self):
        """Возврат уже возвращённой выдачи возвращает False (нет активной выдачи)."""
        loan = BookLoan.objects.create(book=self.book, reader=self.reader)
        return_book(loan_id=loan.pk)
        result = return_book(loan_id=loan.pk)
        self.assertFalse(result)

    def test_return_without_params_returns_false(self):
        """Вызов return_book без loan_id и без (book_id, reader_id) возвращает False."""
        result = return_book()
        self.assertFalse(result)
