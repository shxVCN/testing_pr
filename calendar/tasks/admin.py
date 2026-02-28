from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'user', 'notify_minutes_before')
    list_filter = ('date', 'user')
    search_fields = ('title', 'description')
