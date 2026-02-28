"""
URL-маршруты приложения polls.
"""
from django.urls import path
from . import views

app_name = 'polls'

urlpatterns = [
    path('', views.poll_list, name='poll_list'),
    path('poll/create/', views.poll_create, name='poll_create'),
    path('poll/<int:pk>/', views.poll_detail, name='poll_detail'),
    path('poll/<int:pk>/results/', views.poll_results, name='poll_results'),
]
