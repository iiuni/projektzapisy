"""Django admin panel for vote."""
from django.contrib import admin

from .models import SystemState

admin.site.register(SystemState)
