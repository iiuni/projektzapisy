"""Test runner adding the `--nomigrations` flag.

Applying all the migrations before every test run takes a lot of time and tells
us nothing about the code under test: the schema they build is the one the
models already describe. With `--nomigrations` Django creates the tables
directly from the models instead.

This used to be provided by the `django-test-without-migrations` package, which
has been unmaintained since 2017.
"""
import multiprocessing

from django.conf import settings
from django.test.runner import DiscoverRunner


class DisableMigrations:
    """Tells Django that no app has any migrations.

    A `MIGRATION_MODULES` mapping every app label to None makes the test
    database creation fall back to `migrate --run-syncdb`, which creates the
    tables straight from the models.
    """

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


class ZapisyTestRunner(DiscoverRunner):
    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '-n', '--nomigrations',
            action='store_true',
            help='Tells Django to NOT use migrations and create all tables directly.')

    def __init__(self, nomigrations=False, **kwargs):
        if nomigrations:
            settings.MIGRATION_MODULES = DisableMigrations()
        # Python 3.14 made `forkserver` the default start method on Linux, but
        # Django's parallel runner only knows how to set the workers up under
        # `fork` and `spawn` - under anything else they die reporting that the
        # app registry is not ready.
        if multiprocessing.get_start_method(allow_none=True) not in ('fork', 'spawn'):
            multiprocessing.set_start_method('spawn', force=True)
        super().__init__(**kwargs)
