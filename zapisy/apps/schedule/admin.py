from django import forms
from django.contrib import admin

from .models.term import Term
from .models.event import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created', 'status', 'type', 'description', 'semester')
    list_filter = ('type',)
    ordering = ('type', 'title')

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.save(author_id=request.user.id)
        return instance

class TermAdmin(admin.ModelAdmin):
    list_display = ('event', 'day', 'start', 'end', 'room', 'place')
    list_filter = ('room',)
    search_fields = ('event__title',)
    ordering = ('-day', 'start', 'end')


admin.site.register(Term, TermAdmin)
admin.site.register(Event, EventAdmin)