"""
Юнит-тесты приложения голосования.

Каждый тест использует Django TestCase с реальной БД (SQLite в тестах)
и bootstrap-сценарий: создание пользователей, опросов, вариантов через ORM.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models import Count

from .models import Poll, Choice, Vote


User = get_user_model()


class PollCreationTest(TestCase):
    """
    Тест создания опроса.
    Сценарий: пользователь создаёт опрос с вариантами ответов через форму.
    Bootstrap: создание пользователя в БД, проверка коллекции choices.
    """

    def setUp(self):
        """Bootstrap: подготовка данных в БД."""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_poll_creation_with_choices(self):
        """Создание опроса создаёт связанные варианты в коллекции choices."""
        response = self.client.post(reverse('polls:poll_create'), {
            'question': 'Какой язык программирования лучше?',
            'choice1': 'Python',
            'choice2': 'JavaScript',
            'choice3': 'Java',
        })
        self.assertEqual(response.status_code, 302)

        poll = Poll.objects.get(question='Какой язык программирования лучше?')
        self.assertEqual(poll.created_by, self.user)

        # Проверка внутренней коллекции choices
        choices = list(poll.choices.all())
        self.assertEqual(len(choices), 3)
        choice_texts = [c.text for c in choices]
        self.assertIn('Python', choice_texts)
        self.assertIn('JavaScript', choice_texts)
        self.assertIn('Java', choice_texts)


class VoteLogicTest(TestCase):
    """
    Тест логики голосования.
    Сценарий: пользователь голосует за вариант; при повторном голосовании
    старый голос заменяется новым (один голос на опрос).
    Bootstrap: опрос, варианты, пользователь в БД.
    """

    def setUp(self):
        """Bootstrap: опрос с вариантами в БД."""
        self.user = User.objects.create_user(username='voter', password='testpass123')
        self.poll = Poll.objects.create(question='Тест?', created_by=self.user)
        self.choice_a = Choice.objects.create(poll=self.poll, text='Вариант A')
        self.choice_b = Choice.objects.create(poll=self.poll, text='Вариант B')
        self.client = Client()
        self.client.login(username='voter', password='testpass123')

    def test_vote_creates_vote_record(self):
        """Голосование создаёт запись Vote и связывает с choice.votes."""
        response = self.client.post(
            reverse('polls:poll_detail', args=[self.poll.pk]),
            {'choice': self.choice_a.pk}
        )
        self.assertEqual(response.status_code, 302)

        # Проверка коллекции votes у choice
        votes = list(self.choice_a.votes.all())
        self.assertEqual(len(votes), 1)
        self.assertEqual(votes[0].user, self.user)

    def test_revote_replaces_previous_vote(self):
        """Повторное голосование заменяет предыдущий голос (один голос на опрос)."""
        Vote.objects.create(choice=self.choice_a, user=self.user)

        # Голосуем за другой вариант
        self.client.post(
            reverse('polls:poll_detail', args=[self.poll.pk]),
            {'choice': self.choice_b.pk}
        )

        # У choice_a не должно быть голосов от этого пользователя
        self.assertFalse(self.choice_a.votes.filter(user=self.user).exists())
        # У choice_b должен быть голос
        self.assertTrue(self.choice_b.votes.filter(user=self.user).exists())


class PollResultsTest(TestCase):
    """
    Тест получения результатов голосования.
    Сценарий: несколько пользователей голосуют; проверка подсчёта.
    Bootstrap: опрос, варианты, несколько Vote в БД.
    """

    def setUp(self):
        """Bootstrap: опрос с голосами."""
        self.creator = User.objects.create_user(username='creator', password='pass')
        self.poll = Poll.objects.create(question='Результаты?', created_by=self.creator)
        self.choice_x = Choice.objects.create(poll=self.poll, text='X')
        self.choice_y = Choice.objects.create(poll=self.poll, text='Y')

        self.user1 = User.objects.create_user(username='u1', password='pass')
        self.user2 = User.objects.create_user(username='u2', password='pass')
        Vote.objects.create(choice=self.choice_x, user=self.user1)
        Vote.objects.create(choice=self.choice_x, user=self.user2)
        Vote.objects.create(choice=self.choice_y, user=User.objects.create_user(username='u3', password='pass'))

    def test_results_show_correct_counts(self):
        """Страница результатов возвращает корректные подсчёты голосов.
        Проверка коллекций votes, get_total_votes и аннотации votes_count."""
        # choice_x: 2 голоса, choice_y: 1 голос (bootstrap из setUp)
        choice_x_votes = self.choice_x.votes.count()
        choice_y_votes = self.choice_y.votes.count()
        self.assertEqual(choice_x_votes, 2)
        self.assertEqual(choice_y_votes, 1)
        self.assertEqual(self.poll.get_total_votes(), 3)

        # Проверка аннотации votes_count (как в представлении результатов)
        choices_with_votes = self.poll.choices.all().annotate(votes_count=Count('votes'))
        total = sum(c.votes_count for c in choices_with_votes)
        self.assertEqual(total, 3)


class PollModelMethodsTest(TestCase):
    """
    Тест методов модели Poll.
    Сценарий: проверка get_total_votes и user_has_voted.
    Bootstrap: опрос, варианты, голоса в БД.
    """

    def setUp(self):
        """Bootstrap: данные для проверки методов."""
        self.user = User.objects.create_user(username='check', password='pass')
        self.poll = Poll.objects.create(question='Методы?', created_by=self.user)
        self.choice = Choice.objects.create(poll=self.poll, text='Да')
        Vote.objects.create(choice=self.choice, user=self.user)

    def test_get_total_votes(self):
        """get_total_votes возвращает общее количество голосов по опросу."""
        total = self.poll.get_total_votes()
        self.assertEqual(total, 1)

        other_user = User.objects.create_user(username='other', password='pass')
        Vote.objects.create(choice=self.choice, user=other_user)
        self.assertEqual(self.poll.get_total_votes(), 2)

    def test_user_has_voted(self):
        """user_has_voted корректно определяет, голосовал ли пользователь."""
        self.assertTrue(self.poll.user_has_voted(self.user))

        anonymous = User.objects.create_user(username='anon', password='pass')
        self.assertFalse(self.poll.user_has_voted(anonymous))


class ChoiceVotesCollectionTest(TestCase):
    """
    Тест коллекции votes у Choice.
    Сценарий: несколько голосов за один вариант; проверка related_name.
    Bootstrap: опрос, choice, несколько Vote.
    """

    def setUp(self):
        """Bootstrap: вариант с несколькими голосами."""
        self.creator = User.objects.create_user(username='c', password='p')
        self.poll = Poll.objects.create(question='Коллекция?', created_by=self.creator)
        self.choice = Choice.objects.create(poll=self.poll, text='Вариант')

    def test_choice_votes_collection(self):
        """Коллекция choice.votes содержит все голоса за этот вариант."""
        users = [
            User.objects.create_user(username=f'u{i}', password='p')
            for i in range(3)
        ]
        for u in users:
            Vote.objects.create(choice=self.choice, user=u)

        votes = list(self.choice.votes.all())
        self.assertEqual(len(votes), 3)
        self.assertEqual(self.choice.get_votes_count(), 3)
