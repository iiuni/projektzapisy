from django.contrib import admin

from apps.theses.forms import RemarkFormAdmin, ThesisFormAdmin, VoteFormAdmin
from apps.theses.models import Remark, ThesesSystemSettings, Thesis, Vote


class ThesisAdmin(admin.ModelAdmin):
    autocomplete_fields = []
    list_display = ('title', 'kind', 'status', 'added')
    form = ThesisFormAdmin


class RemarkAdmin(admin.ModelAdmin):
    autocomplete_fields = []
    form = RemarkFormAdmin


class VoteAdmin(admin.ModelAdmin):
    autocomplete_fields = []
    form = VoteFormAdmin


class ThesesSystemSettingsAdmin(admin.ModelAdmin):
    """Theses system settings admin.

    Exactly one instance of ThesesSystemSettings is created when applying
    migrations, and users should only be permitted to modify that one instance,
    not create new ones or delete existing ones
    """
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Thesis, ThesisAdmin)
admin.site.register(Remark, RemarkAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(ThesesSystemSettings, ThesesSystemSettingsAdmin)
