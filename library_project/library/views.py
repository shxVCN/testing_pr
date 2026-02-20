"""
Представления библиотеки: книги, читатели, выдачи.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods

from .models import Book, Reader, BookLoan
from .services import delete_book, return_book
from .forms import BookForm, ReaderForm


def book_list(request):
    """Список книг."""
    books = Book.objects.all()
    return render(request, 'library/book_list.html', {'books': books})


@require_http_methods(['GET', 'POST'])
def book_add(request):
    """Добавить книгу."""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('library:book_list')
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form})


@require_POST
def book_delete(request, pk):
    """Удалить книгу."""
    delete_book(pk)
    return redirect('library:book_list')


def reader_list(request):
    """Список читателей."""
    readers = Reader.objects.all()
    return render(request, 'library/reader_list.html', {'readers': readers})


@require_http_methods(['GET', 'POST'])
def reader_add(request):
    """Добавить читателя."""
    if request.method == 'POST':
        form = ReaderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('library:reader_list')
    else:
        form = ReaderForm()
    return render(request, 'library/reader_form.html', {'form': form})


def loan_list(request):
    """Список выдач книг."""
    loans = BookLoan.objects.select_related('book', 'reader').all()
    return render(request, 'library/loan_list.html', {'loans': loans})


@require_POST
def loan_return(request, pk):
    """Вернуть книгу (по id выдачи)."""
    return_book(loan_id=pk)
    return redirect('library:loan_list')
