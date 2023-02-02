import json
import logging

from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.effects.models import Variant

logger = logging.getLogger()


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ('name', 'program', 'requirements_formatted', 'pdf_link')

    def requirements_formatted(self, obj):
        formatted = json.dumps(
            obj.requirements.get('wymagania'), indent=4, ensure_ascii=False
        ).encode('utf-8').decode().replace('\n', '<br>').replace('    ', '&emsp;')
        return mark_safe(formatted)

    def pdf_link(self, obj):
        url = obj.requirements.get("meta").get("url")
        link = f'<a target="_blank" rel="noopener noreferrer" href={url}>Link</a>'
        return mark_safe(link)

    requirements_formatted.short_description = 'Wymagania'
    pdf_link.short_description = 'Link do PDF'
