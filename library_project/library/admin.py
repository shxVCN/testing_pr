from django.contrib import admin
from .models import Book, Reader, BookLoan


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'year')
    search_fields = ('title', 'author', 'isbn')


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'phone')
    search_fields = ('last_name', 'first_name', 'email')


@admin.register(BookLoan)
class BookLoanAdmin(admin.ModelAdmin):
    list_display = ('book', 'reader', 'issued_at', 'returned_at')
    list_filter = ('issued_at',)
    raw_id_fields = ('book', 'reader')
