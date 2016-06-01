#!/usr/bin/env python
from django.core.management import execute_manager

try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

import os
os.environ["DJANGO_SETTINGS_MODULE"] = 'settings'
if __name__ == "__main__":
    from django.contrib.auth.models import Permission
    # Patch the field width to allow for our long model names
    Permission._meta.get_field('name').max_length=200
    Permission._meta.get_field('codename').max_length=200
    execute_manager(settings)

