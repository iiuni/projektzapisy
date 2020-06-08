from django.apps import AppConfig


class TicketsAppConfig(AppConfig):
    name = "apps.grade.ticket_create"
    verbose_name = "Tickets"

    def ready(self):
        import apps.grade.ticket_create.signals  # noqa
