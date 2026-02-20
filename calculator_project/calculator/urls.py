"""
URL configuration for calculator app.
"""
from django.urls import path
from . import views

app_name = 'calculator'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/calculate/', views.api_calculate, name='api_calculate'),
    path('api/calculate/post/', views.api_calculate_post, name='api_calculate_post'),
]
