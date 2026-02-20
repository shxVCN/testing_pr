# Система управления книгами (Django)

Приложение для учёта книг, читателей и выдачи/возврата книг.

## Установка

```bash
pip install -r requirements.txt
python manage.py migrate
```

## Запуск

```bash
python manage.py runserver
```

- Книги: http://127.0.0.1:8000/books/
- Читатели: http://127.0.0.1:8000/readers/
- Выдачи: http://127.0.0.1:8000/loans/
- Админка: http://127.0.0.1:8000/admin/ (создайте суперпользователя: `python manage.py createsuperuser`)

## Юнит-тесты

```bash
python manage.py test library
```

Тесты: добавление/удаление книг, выдача и возврат книг.
