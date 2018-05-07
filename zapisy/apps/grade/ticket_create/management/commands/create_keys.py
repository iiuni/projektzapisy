from django.core.management.base import BaseCommand
from apps.grade.ticket_create.utils import generate_keys_for_polls


class Command(BaseCommand):
    args = '<semester( szablon)+>'
    help = 'tworzy ankiety na podstawie szablony'

    def handle(self, *args, **options):
        generate_keys_for_polls()
