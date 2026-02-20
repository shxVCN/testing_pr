"""
URL configuration for library app.
"""
from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_add, name='book_add'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('readers/', views.reader_list, name='reader_list'),
    path('readers/add/', views.reader_add, name='reader_add'),
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/<int:pk>/return/', views.loan_return, name='loan_return'),
]
