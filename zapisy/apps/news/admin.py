from django.contrib import admin
from django.db import models
from pagedown.widgets import AdminPagedownWidget

from apps.news.models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """
        News admin manager
    """
    fields = ('title', 'body', 'author', 'category')
    list_display = ('title', 'date')
    list_filter = ['date']
    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget},
    }

    def get_changeform_initial_data(self, request):
        return {'author': request.user}
