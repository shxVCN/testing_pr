"""
Юнит-тесты для приложения задач.
Покрывают CRUD операции и логику пометки задач как выполненных.
"""
import unittest.mock

from django.test import TestCase, Client
from django.urls import reverse

from .models import Task


def _safe_copy(context):
    """Обход несовместимости Python 3.14 с copy() для Django Context."""
    try:
        from copy import copy
        return copy(context)
    except AttributeError:
        return None


class TaskCRUDTests(TestCase):
    """Тесты CRUD операций и коллекции задач."""

    def setUp(self):
        """Подготовка клиента для тестов."""
        self.client = Client()
        # Патч для совместимости с Python 3.14
        self._copy_patcher = unittest.mock.patch(
            'django.test.client.copy',
            side_effect=_safe_copy
        )
        self._copy_patcher.start()

    def tearDown(self):
        self._copy_patcher.stop()

    def test_task_list_displays_collection(self):
        """Тест: список задач отображает коллекцию (Read - коллекция)."""
        Task.objects.create(title='Задача 1', description='Описание 1')
        Task.objects.create(title='Задача 2', description='Описание 2')
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Задача 1')
        self.assertContains(response, 'Задача 2')
        self.assertEqual(Task.objects.count(), 2)

    def test_task_create_adds_new_task(self):
        """Тест: создание новой задачи (Create)."""
        response = self.client.post(reverse('task_create'), {
            'title': 'Новая задача',
            'description': 'Описание новой задачи',
            'completed': False,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='Новая задача').exists())
        task = Task.objects.get(title='Новая задача')
        self.assertEqual(task.description, 'Описание новой задачи')
        self.assertFalse(task.completed)

    def test_task_detail_displays_single_object(self):
        """Тест: детальный просмотр отображает один объект (Read - объект)."""
        task = Task.objects.create(title='Тестовая задача', description='Детали')
        response = self.client.get(reverse('task_detail', args=[task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая задача')
        self.assertContains(response, 'Детали')

    def test_task_update_modifies_existing_task(self):
        """Тест: редактирование существующей задачи (Update)."""
        task = Task.objects.create(title='Исходная задача', description='Старое описание')
        response = self.client.post(reverse('task_update', args=[task.pk]), {
            'title': 'Обновлённая задача',
            'description': 'Новое описание',
            'completed': False,
        })
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Обновлённая задача')
        self.assertEqual(task.description, 'Новое описание')

    def test_task_delete_removes_task(self):
        """Тест: удаление задачи (Delete)."""
        task = Task.objects.create(title='Задача на удаление')
        self.assertEqual(Task.objects.count(), 1)
        response = self.client.post(reverse('task_delete', args=[task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), 0)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_task_toggle_complete_marks_and_unmarks(self):
        """Тест: пометка задачи как выполненной и снятие пометки (логика toggle)."""
        task = Task.objects.create(title='Задача', completed=False)
        # Пометка как выполненной
        self.client.post(reverse('task_toggle_complete', args=[task.pk]))
        task.refresh_from_db()
        self.assertTrue(task.completed)
        # Снятие пометки
        self.client.post(reverse('task_toggle_complete', args=[task.pk]))
        task.refresh_from_db()
        self.assertFalse(task.completed)
