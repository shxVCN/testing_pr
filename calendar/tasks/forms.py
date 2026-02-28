"""
Формы для создания и редактирования событий.
"""
from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    """Форма создания и редактирования события."""

    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'notify_minutes_before']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название события'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание (необязательно)'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'notify_minutes_before': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': '15'
            }),
        }
