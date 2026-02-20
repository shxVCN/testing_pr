# Калькулятор (Django)

Простое веб-приложение: форма калькулятора и API для арифметических операций.

## Установка

```bash
pip install -r requirements.txt
python manage.py migrate
```

## Запуск

```bash
python manage.py runserver
```

- Главная: http://127.0.0.1:8000/
- API GET: `/api/calculate/?a=1&b=2&op=add`
- API POST: `/api/calculate/post/` (JSON или form-data: a, b, op)

## Тесты

```bash
python manage.py test calculator
```
