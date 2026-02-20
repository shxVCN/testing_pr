"""
Представления калькулятора: API и страница с формой.
"""
import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from .logic import calculate, CalculatorError


def index(request):
    """Главная страница с формой калькулятора."""
    return render(request, 'calculator/index.html')


@require_GET
def api_calculate(request):
    """
    API: GET /api/calculate/?a=1&b=2&op=add
    Возвращает JSON: {"result": 3} или {"error": "..."}.
    """
    try:
        a = float(request.GET.get('a', 0))
        b = float(request.GET.get('b', 0))
        op = request.GET.get('op', 'add').strip().lower()
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Некорректные числа a или b'}, status=400)

    try:
        result = calculate(op, a, b)
        return JsonResponse({'result': result})
    except CalculatorError as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
@csrf_exempt
def api_calculate_post(request):
    """
    API: POST с JSON {"a": 1, "b": 2, "op": "add"}
    или form-data a, b, op.
    """
    if request.content_type and 'application/json' in request.content_type:
        try:
            data = json.loads(request.body)
            a = float(data.get('a', 0))
            b = float(data.get('b', 0))
            op = str(data.get('op', 'add')).strip().lower()
        except (json.JSONDecodeError, TypeError, ValueError):
            return JsonResponse({'error': 'Некорректный JSON или числа'}, status=400)
    else:
        try:
            a = float(request.POST.get('a', 0))
            b = float(request.POST.get('b', 0))
            op = request.POST.get('op', 'add').strip().lower()
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Некорректные числа a или b'}, status=400)

    try:
        result = calculate(op, a, b)
        return JsonResponse({'result': result})
    except CalculatorError as e:
        return JsonResponse({'error': str(e)}, status=400)
