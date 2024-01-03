from django.apps import AppConfig


class ThesesConfig(AppConfig):
    name = 'apps.theses'
    verbose_name = 'Theses'

    def ready(self):
        from . import signals  # noqa: F401
