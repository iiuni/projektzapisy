"""
    Preferences admin
"""

from django.contrib import admin

from .models import PreferencesQuestion, Preference

admin.site.register(PreferencesQuestion)
admin.site.register(Preference)
