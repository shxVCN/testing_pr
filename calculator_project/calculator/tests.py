"""
Тесты калькулятора: логика и API (8 тестов).
"""
from django.test import TestCase, Client
from django.urls import reverse

from calculator.logic import (
    add,
    divide,
    calculate,
    CalculatorError,
)


class CalculatorLogicTest(TestCase):
    """Тесты функций калькулятора в logic.py."""

    def test_add_integers(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-1, 1), 0)

    def test_divide_by_zero_raises(self):
        with self.assertRaises(CalculatorError) as ctx:
            divide(1, 0)
        self.assertIn('ноль', str(ctx.exception).lower())

    def test_calculate_add(self):
        self.assertEqual(calculate('add', 2, 3), 5)


class CalculatorApiGetTest(TestCase):
    """Тесты GET /api/calculate/."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('calculator:api_calculate')

    def test_add(self):
        r = self.client.get(self.url, {'a': '2', 'b': '3', 'op': 'add'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {'result': 5})

    def test_divide_by_zero_returns_400(self):
        r = self.client.get(self.url, {'a': '1', 'b': '0', 'op': 'divide'})
        self.assertEqual(r.status_code, 400)
        self.assertIn('error', r.json())

    def test_invalid_number_returns_400(self):
        r = self.client.get(self.url, {'a': 'x', 'b': '1', 'op': 'add'})
        self.assertEqual(r.status_code, 400)
        self.assertIn('error', r.json())


class CalculatorApiPostTest(TestCase):
    """Тесты POST /api/calculate/post/."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('calculator:api_calculate_post')

    def test_post_json_add(self):
        r = self.client.post(
            self.url,
            data='{"a": 5, "b": 3, "op": "add"}',
            content_type='application/json',
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {'result': 8})


class CalculatorIndexTest(TestCase):
    """Тесты главной страницы калькулятора."""

    def test_index_returns_200(self):
        r = self.client.get(reverse('calculator:index'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('Калькулятор', r.content.decode('utf-8'))
