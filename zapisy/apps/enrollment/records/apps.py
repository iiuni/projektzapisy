"""Django app config for enrollment.records.

(See https://docs.djangoproject.com/en/2.0/ref/applications/).
"""

from django.apps import AppConfig


class RecordsAppConfig(AppConfig):
    name = 'apps.enrollment.records'

    def ready(self):
        import apps.enrollment.records.signals  # noqa
        import apps.enrollment.records.tasks  # noqa
