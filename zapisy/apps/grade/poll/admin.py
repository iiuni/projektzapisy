import json

from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.forms import widgets

from .models import Schema


class PrettyJSONWidget(widgets.Textarea):
    """Formats JSON in a textarea with an indentation."""
    def format_value(self, value):
        try:
            value = json.dumps(json.loads(value), indent=2, ensure_ascii=False)
            # these lines will try to adjust size of TextArea to fit to content
            row_lengths = [len(r) for r in value.split('\n')]
            self.attrs['rows'] = min(max(len(row_lengths) + 2, 10), 30)
            self.attrs['cols'] = min(max(max(row_lengths) + 2, 40), 120)
            return value
        except Exception:
            return super(PrettyJSONWidget, self).format_value(value)


@admin.register(Schema)
class SchemaAdmin(admin.ModelAdmin):
    list_display = ('type',)

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }
