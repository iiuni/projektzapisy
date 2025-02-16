from django.core.management.base import BaseCommand, CommandParser, CommandError
from django.contrib.sites.models import Site
from django.conf import settings


class Command(BaseCommand):
    help = "Updates the default Site object"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--domain",
            type=str,
            help="Specify the site domain, otherwise, loads from .env file."
        )
        parser.add_argument(
            "--name",
            type=str,
            help="Specify the site name, otherwise, loads from .env file.",
        )

    def handle(self, *args, **options):
        site_id: int | None = getattr(settings, "SITE_ID", None)

        if not site_id:
            raise CommandError("SITE_ID is not defined in settings.")

        domain: str = options["domain"] or getattr(settings, "SITE_DOMAIN", '').strip()
        name: str = options["name"] or getattr(settings, "SITE_NAME", '').strip()

        if not domain or not name:
            raise CommandError("Domain and name value muse be provided either as arguments or in .env file")

        try:
            site = Site.objects.get(pk=site_id)
        except Site.DoesNotExist:
            raise CommandError(f"Failed to fetch site object with pk={site_id}.")

        site.domain = domain
        site.name = name
        site.save()
        self.stdout.write(self.style.SUCCESS("Site object updated successfully."))
