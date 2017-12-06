# -*- coding: utf-8 -*-
from django.contrib import admin
from apps.notifications.models import NotificationPreferences

class NotAdmin(admin.ModelAdmin):

    list_display =('user', 'type', 'value')
    list_filter = ('type', 'value')
    list_select_related = True

admin.site.register(NotificationPreferences, NotAdmin)
