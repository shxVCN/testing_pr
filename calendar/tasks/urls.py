"""
URL-маршруты приложения tasks.
"""
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='tasks/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('event/create/', views.event_create, name='event_create'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    path('event/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('event/<int:pk>/delete/', views.event_delete, name='event_delete'),
]
