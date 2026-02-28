"""
Формы для создания и редактирования задач.
"""
from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    """Форма для создания и редактирования задачи."""

    class Meta:
        model = Task
        fields = ['title', 'description', 'completed']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название задачи',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание (необязательно)',
                'rows': 3,
            }),
            'completed': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
