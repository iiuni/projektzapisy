from django.contrib import admin

from . import models
from .forms import ThesisForm


class ThesisAdmin(admin.ModelAdmin):
    autocomplete_fields = ['advisor', 'supporting_advisor']
    form = ThesisForm


admin.site.register(models.Thesis, ThesisAdmin)


class ThesesSystemSettingsAdmin(admin.ModelAdmin):
    """Exactly one instance of ThesesSystemSettings is created
    when applying migrations, and users should only be permitted
    to modify that one instance, not create new ones or delete existing ones
    """
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(models.ThesesSystemSettings, ThesesSystemSettingsAdmin)
