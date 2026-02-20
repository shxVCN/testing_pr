"""
Формы для книг и читателей.
"""
from django import forms
from .models import Book, Reader


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('title', 'author', 'isbn', 'year')


class ReaderForm(forms.ModelForm):
    class Meta:
        model = Reader
        fields = ('first_name', 'last_name', 'email', 'phone')
