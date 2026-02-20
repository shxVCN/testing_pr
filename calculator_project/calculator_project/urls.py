"""
URL configuration for calculator_project.
"""
from django.urls import path, include

urlpatterns = [
    path('', include('calculator.urls')),
]
