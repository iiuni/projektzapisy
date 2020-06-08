from django.apps import AppConfig


class PollAppConfig(AppConfig):
    name = "apps.grade.poll"
    verbose_name = "Ocena zajęć"

    def ready(self):
        import apps.grade.poll.signals  # noqa
