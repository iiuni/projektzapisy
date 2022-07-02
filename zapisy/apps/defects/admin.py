from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Defect, DefectManager, Image

# Register your models here.
admin.site.register(DefectManager)
# admin.site.register(Defect)


class ImageInline(admin.TabularInline):
    model = Image


class DefectInline(admin.TabularInline):
    model = Defect


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "defect_field")
    readonly_fields = ("defect_field",)

    def defect_field(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse('admin:%s_%s_change' % (obj.defect._meta.app_label, obj.defect._meta.model_name), args=[obj.defect.id]),
            obj.defect.name
        ))
    defect_field.short_description = "Defect"


@admin.register(Defect)
class DefectAdmin(admin.ModelAdmin):
    list_display = ("name", "reporter", "state", "place", "creation_date", "last_modification")
    inlines = [ImageInline]
