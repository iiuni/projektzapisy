from django.core.management.base import BaseCommand

from apps.grade.poll.models import PollType, Schema

HEADER = "-- "
MARGIN = "   "
CREATED = " + "


class Command(BaseCommand):
    help = "Creates schemas from fixtures. If an argument is not given, creates for all types."

    def add_arguments(self, parser):
        parser.add_argument("-t", "--type", type=str, help="Type of the schema")

    def handle(self, *args, **kwargs):
        self.stdout.write(f"{HEADER}Initializing")
        poll_type = kwargs["type"]
        created = 0
        types = []
        if poll_type:
            types.append(poll_type)
        else:
            types = PollType.choices

        for schema_type in types:
            schema = Schema(
                questions=Schema.get_schema_from_file(poll_type=schema_type[0]),
                type=schema_type[0],
            )
            schema.save()
            self.stdout.write(f"{CREATED}Created schema for {schema_type}")
            created += 1

        self.stdout.write(f"\n{HEADER}Summary")
        self.stdout.write(f"{MARGIN}Created: {created}")
