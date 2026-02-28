# Патч для совместимости Django с Python 3.14:
# BaseContext.__copy__ использует copy(super()), что в 3.14 ломается.
# Создаём копию вручную: object.__new__ + копирование всех атрибутов (dicts, template, render_context и т.д.).
import copy as _copy

import django.template.context as _django_context


def _patched_base_context_copy(self):
    duplicate = object.__new__(self.__class__)
    duplicate.dicts = self.dicts[:]
    for key, value in self.__dict__.items():
        if key == "dicts":
            continue
        try:
            setattr(duplicate, key, _copy.copy(value))
        except (TypeError, AttributeError):
            setattr(duplicate, key, value)
    return duplicate


_django_context.BaseContext.__copy__ = _patched_base_context_copy
