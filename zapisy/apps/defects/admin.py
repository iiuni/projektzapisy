from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .forms import DefectManagerAdminForm
from .models import Defect, DefectManager, DefectImage


class DefectImageInline(admin.TabularInline):
    model = DefectImage


class DefectInline(admin.TabularInline):
    model = Defect


@admin.register(DefectImage)
class DefectImageAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "defect_field")
    # readonly_fields = ("defect_field",)

    def defect_field(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse('admin:%s_%s_change' % (obj.defect._meta.app_label, obj.defect._meta.model_name),
                    args=[obj.defect.id]),
            obj.defect.name
        ))
    defect_field.short_description = "Defect"


@admin.register(Defect)
class DefectAdmin(admin.ModelAdmin):
    list_display = ("name", "reporter", "state", "place", "creation_date", "last_modification")
    inlines = [DefectImageInline]

    def get_queryset(self, request):
        qs = self.model.all_objects.get_queryset()

        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


@admin.register(DefectManager)
class DefectManagerAdmin(admin.ModelAdmin):
    list_display = ("id", "manager_field",)
    form = DefectManagerAdminForm

    def manager_field(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse('admin:%s_%s_change' % (obj.user_id._meta.app_label, obj.user_id._meta.model_name),
                    args=[obj.user_id.id]),
            obj.user_id.first_name + " " + obj.user_id.last_name
        ))
    manager_field.short_description = "User"
