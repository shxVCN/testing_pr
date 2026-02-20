"""
Логика калькулятора: арифметические операции.
"""


class CalculatorError(ValueError):
    """Ошибка вычисления (например, деление на ноль)."""
    pass


def add(a: float, b: float) -> float:
    """Сложение."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Вычитание."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Умножение."""
    return a * b


def divide(a: float, b: float) -> float:
    """Деление. Вызывает CalculatorError при делении на ноль."""
    if b == 0:
        raise CalculatorError('Деление на ноль')
    return a / b


def calculate(operation: str, a: float, b: float) -> float:
    """
    Выполняет операцию по строковому имени.
    Поддерживаются: add, subtract, multiply, divide.
    """
    operations = {
        'add': add,
        'subtract': subtract,
        'multiply': multiply,
        'divide': divide,
    }
    op = operations.get(operation)
    if op is None:
        raise CalculatorError(f'Неизвестная операция: {operation}')
    return op(a, b)
