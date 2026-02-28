"""
Тесты приложения управления задачами и событиями.
Покрывают создание, редактирование, удаление событий и логику уведомлений.
"""
from datetime import date, time, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Event
from .services import get_upcoming_events, get_events_needing_notification


class EventModelTest(TestCase):
    """Тесты модели Event и её методов."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_event_creation(self):
        """Тест создания события с указанной датой и временем."""
        event = Event.objects.create(
            title='Тестовое событие',
            description='Описание',
            date=date(2025, 3, 15),
            time=time(14, 30),
            user=self.user,
            notify_minutes_before=15
        )
        self.assertEqual(event.title, 'Тестовое событие')
        self.assertEqual(event.date, date(2025, 3, 15))
        self.assertEqual(event.time, time(14, 30))
        self.assertEqual(event.user, self.user)
        self.assertEqual(event.notify_minutes_before, 15)

    def test_event_str_representation(self):
        """Тест строкового представления объекта Event."""
        event = Event.objects.create(
            title='Встреча',
            date=date(2025, 2, 20),
            time=time(10, 0),
            user=self.user
        )
        self.assertIn('Встреча', str(event))
        self.assertIn('2025-02-20', str(event))


class EventCRUDTest(TestCase):
    """Тесты создания, редактирования и удаления событий через представления."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_event_create_view(self):
        """Тест создания события через форму."""
        url = reverse('tasks:event_create')
        response = self.client.post(url, {
            'title': 'Новое событие',
            'description': 'Описание события',
            'date': '2025-03-01',
            'time': '12:00',
            'notify_minutes_before': 30
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(title='Новое событие').exists())
        event = Event.objects.get(title='Новое событие')
        self.assertEqual(event.user, self.user)

    def test_event_edit_view(self):
        """Тест редактирования существующего события."""
        event = Event.objects.create(
            title='Старое название',
            date=date(2025, 3, 10),
            time=time(9, 0),
            user=self.user
        )
        url = reverse('tasks:event_edit', kwargs={'pk': event.pk})
        response = self.client.post(url, {
            'title': 'Обновлённое название',
            'description': '',
            'date': '2025-03-11',
            'time': '10:00',
            'notify_minutes_before': 15
        })
        self.assertEqual(response.status_code, 302)
        event.refresh_from_db()
        self.assertEqual(event.title, 'Обновлённое название')
        self.assertEqual(event.date, date(2025, 3, 11))

    def test_event_delete_view(self):
        """Тест удаления события."""
        event = Event.objects.create(
            title='Событие для удаления',
            date=date(2025, 3, 5),
            time=time(14, 0),
            user=self.user
        )
        pk = event.pk
        url = reverse('tasks:event_delete', kwargs={'pk': pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Event.objects.filter(pk=pk).exists())


class NotificationLogicTest(TestCase):
    """Тесты логики уведомлений о предстоящих событиях."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_get_upcoming_events_returns_future_events(self):
        """Тест: get_upcoming_events возвращает события в указанном временном окне."""
        future_date = timezone.now().date() + timedelta(days=1)
        event = Event.objects.create(
            title='Завтрашнее событие',
            date=future_date,
            time=time(12, 0),
            user=self.user
        )
        upcoming = get_upcoming_events(self.user, minutes_ahead=24 * 60)
        self.assertIn(event, upcoming)

    def test_get_events_needing_notification_within_threshold(self):
        """Тест: события в пороге уведомления возвращаются get_events_needing_notification."""
        with timezone.override('UTC'):
            now = timezone.now()
            event_time = now + timedelta(minutes=5)
            event = Event.objects.create(
                title='Скоро',
                date=event_time.date(),
                time=event_time.time(),
                user=self.user,
                notify_minutes_before=15
            )
            needing = get_events_needing_notification(self.user)
            self.assertIn(event, needing)

    def test_past_events_not_in_notification(self):
        """Тест: прошедшие события не попадают в уведомления."""
        local_now = timezone.localtime(timezone.now())
        past_time = local_now - timedelta(hours=1)
        event = Event.objects.create(
            title='Прошедшее',
            date=past_time.date(),
            time=past_time.time(),
            user=self.user,
            notify_minutes_before=15
        )
        needing = get_events_needing_notification(self.user)
        self.assertNotIn(event, needing)


class EventCollectionTest(TestCase):
    """Тесты работы с коллекцией событий пользователя."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_user_events_ordering(self):
        """Тест: события пользователя упорядочены по дате и времени."""
        Event.objects.create(
            title='Второе',
            date=date(2025, 3, 20),
            time=time(15, 0),
            user=self.user
        )
        Event.objects.create(
            title='Первое',
            date=date(2025, 3, 20),
            time=time(10, 0),
            user=self.user
        )
        Event.objects.create(
            title='Третье',
            date=date(2025, 3, 21),
            time=time(9, 0),
            user=self.user
        )
        events = list(Event.objects.filter(user=self.user).order_by('date', 'time'))
        self.assertEqual(events[0].title, 'Первое')
        self.assertEqual(events[1].title, 'Второе')
        self.assertEqual(events[2].title, 'Третье')

    def test_events_isolated_per_user(self):
        """Тест: события изолированы по пользователям."""
        other_user = User.objects.create_user(username='other', password='pass123')
        Event.objects.create(
            title='Моё событие',
            date=date(2025, 3, 15),
            time=time(12, 0),
            user=self.user
        )
        Event.objects.create(
            title='Чужое событие',
            date=date(2025, 3, 15),
            time=time(12, 0),
            user=other_user
        )
        user_events = Event.objects.filter(user=self.user)
        self.assertEqual(user_events.count(), 1)
        self.assertEqual(user_events.first().title, 'Моё событие')
