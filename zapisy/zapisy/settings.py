import os

import environ
from django.contrib.messages import constants as messages
from django.core.exceptions import PermissionDenied
from django.http import Http404

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()

environ.Env.read_env(os.path.join(BASE_DIR, os.pardir, 'env', '.env'))

DEBUG = env.bool('DEBUG')
RELEASE = env.bool('RELEASE')

# With DEBUG = False Django will refuse to serve requests to hosts different than this one.
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Virtualbox default for the host machine as seen from the guest.
INTERNAL_IPS = ('10.0.2.2',)

EMAIL_BACKEND = env.str('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EVENT_MODERATOR_EMAIL = 'zapisy@cs.uni.wroc.pl'
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', default='webmaster@localhost')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)
EMAIL_HOST = env.str('EMAIL_HOST', default='')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=25)
SERVER_EMAIL = env.str('SERVER_EMAIL', default='root@localhost')
EMAIL_THROTTLE_SECONDS = env.int('EMAIL_THROTTLE_SECONDS', default=0)

# django-environ doesn't support nested arrays, but decoding json objects works fine
ARRAY_VALS = env.json('ARRAY_VALS', {})
ADMINS = ARRAY_VALS['ADMINS'] if ARRAY_VALS else []

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env.str('DATABASE_NAME'),
        'PORT': env.str('DATABASE_PORT'),
        'USER': env.str('DATABASE_USER'),
        'PASSWORD': env.str('DATABASE_PASSWORD'),
        'HOST': 'localhost',
        'CHARSET': 'utf8',
        'USE_UNICODE': True,
    }
}

# django-rq is a task queue. It can be used to run asynchronous tasks. The tasks
# should be implemented so, that setting RUN_ASYNC to False would run them
# eagerly.
RUN_ASYNC = env.bool('RUN_ASYNC', True)
RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'PASSWORD': '',
        'DEFAULT_TIMEOUT': 360,
        'ASYNC': RUN_ASYNC,
    },
    'dispatch-notifications': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'ASYNC': RUN_ASYNC,
    },
}

# mass-mail account
# You can test sending with:
# $ python -m smtpd -n -c DebuggingServer localhost:1025

MASS_MAIL_FROM = 'zapisy@cs.uni.wroc.pl'
EMAIL_COURSE_PREFIX = '[System Zapisow] '  # please don't remove the trailing space

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # keep Django's default loggers
    'formatters': {
        'timestampthread': {
            'format': "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(name)-20.20s]  %(message)s",
        },
    },
    'handlers': {
        'logfile': {
            'level': 'INFO',  # INFO or higher goes to the log file. DEBUG polluted the logs way too much.
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/djangoproject.log',
            'maxBytes': 50 * 1024 * 1024,  # will 50 MB do?
            'backupCount': 5,  # keep this many extra historical files
            'formatter': 'timestampthread'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
        },
        'rq_logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'timestampthread',
            'filename': 'logs/rqworker.log',
            'encoding': 'UTF-8',
            'maxBytes': 50 * 1024 * 1024,  # 50 MB
            'backupCount': 5,  # keep this many extra historical files
        },
    },
    'loggers': {
        'django': {  # configure all of Django's loggers
            'handlers': ['logfile', 'console'] if DEBUG else ['logfile'],
            'level': 'DEBUG',  # set to debug to see e.g. database queries
            'propagate': False,
        },
        'apps': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'rq.worker': {
            'handlers': ['rq_logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['logfile'],
        'level': 'DEBUG'
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Warsaw'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pl-pl'

# Available languages for using the service. The first one is the default.


LANGUAGES = (
    ('pl', 'Polish'),
    ('en', 'English'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = env.str('SECRET_KEY', default='N3MUBVRQXkhuqzsZ8QMepRaZwHDXwhp4rTcVQF5bmckB2c293V')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'OPTIONS': {
            'debug': env.bool('TEMPLATE_DEBUG'),
            'context_processors': [
                'django.contrib.messages.context_processors.messages',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'apps.users.context_processors.roles',
            ],
        },
    },
]

# Be careful with the order! SessionMiddleware
# and Authentication both must come before LocalePref which
# must precede LocaleMiddleware, and Common must go afterwards.
MIDDLEWARE = [
    'zapisy.middleware.report_limiter.RollbarOnly404Limited',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'rollbar.contrib.django.middleware.RollbarNotifierMiddlewareExcluding404',
]

ROOT_URLCONF = 'zapisy.urls'

INSTALLED_APPS = (
    'rest_framework',
    'rest_framework.authtoken',

    # needed from 1.7 onwards to prevent Django from trying to apply
    # migrations when testing (slows down DB setup _a lot_)
    'test_without_migrations',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',

    'apps.users',

    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mailer',
    'apps.enrollment.courses',
    'apps.enrollment.records',
    'apps.enrollment.timetable',
    'apps.statistics',
    'apps.news',
    'apps.offer.preferences',
    'apps.offer.proposal',
    'apps.offer.vote',
    'apps.offer.desiderata',
    'apps.offer.assignments',

    'apps.common',
    'apps.schedule',
    # 'debug_toolbar',
    'apps.grade.poll',
    'apps.grade.ticket_create',
    'apps.schedulersync',
    'apps.theses',
    'apps.effects',
    'django_extensions',
    'django_filters',
    'bootstrap_pagination',
    'crispy_forms',
    'apps.notifications',
    'django_cas_ng',
    'django_rq',
    'webpack_loader',
    'pagedown.apps.PagedownConfig',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas_ng.backends.CASBackend',
)

TIME_FORMAT = "H:i"
DATETIME_FORMAT = "j N Y, H:i"

CAS_SERVER_URL = 'https://login.usos.uwr.edu.pl/cas/'
CAS_CREATE_USER = False
CAS_LOGIN_MSG = 'Sukces! Zalogowano przez USOS (login: %s).'
CAS_LOGOUT_COMPLETELY = False

# References pull request #655: https://github.com/iiuni/projektzapisy/pull/655
# Force django_cas_ng to use protocol version 3 instead of 2 (the default).
# This setting can be enabled as soon as the University's CAS is upgraded to a
# newer version. Temporary workaround: users.views.cas_logout()
# CAS_VERSION = '3'

# URL where user will be redirected to after logging out if there is
# no referrer and no next page set.
LOGOUT_REDIRECT_URL = '/'
CAS_REDIRECT_URL = LOGOUT_REDIRECT_URL

# This chceck has to be disabled as long as we are using an incorrect Nginx
# configuration which rewrites HTTPS to HTTP.
CAS_CHECK_NEXT = lambda _: True  # noqa: E731

LOGIN_REDIRECT_URL = '/users/'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Settings for enrollment.
# Bonus minutes per one ECTS credit. This setting affects T0 times computation.
ECTS_BONUS = 2
# Limits concerning the amount of ECTS points a student can sign up to in a
# semester. For the first part of enrollment cycle, the INITIAL_LIMIT holds.
# Then, after abolition time, students can enroll into some additional courses.
ECTS_INITIAL_LIMIT = 35
ECTS_FINAL_LIMIT = 45

VOTE_LIMIT = 60

SESSION_COOKIE_PATH = '/;HttpOnly'
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Attach X-XSS-Protection header to all outgoing HTTP responses.
# It tells conformant browsers to activate their built-in
# XSS (cross-site scripting attack) detection filter.
SECURE_BROWSER_XSS_FILTER = True

# Attach X-Content-Type-Options header with a value of nosniff
# to all outgoing HTTP responses.
# What it does is preventing the browser from trying to guess
# a file type by 'sniffing' (applying some heuristic algorithms to) it.
# Such feature can be abused in surprising ways, e.g. by disguising
# JavaScript code in a text/plain file.
SECURE_CONTENT_TYPE_NOSNIFF = True

# How long should our site be remembered to be HTTPS-only
# by browsers.
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365

# Manifest the will to be included in so-called browser preload list,
# physically distributed with browsers (Chrome for instance) to
# basically do what HSTS would do, but even when a specific site
# has never been seen before.
SECURE_HSTS_PRELOAD = True

DEBUG_TOOLBAR_ALLOWED_USERS = env.list('DEBUG_TOOLBAR_ALLOWED_USERS', default=[])
DEBUG_TOOLBAR_PANELS = env.list('DEBUG_TOOLBAR_PANELS', default=[])

ROLLBAR = {
    'access_token': env.str('ROLLBAR_TOKEN', default=''),
    'environment': env.str('ROLLBAR_ENV', default=''),
    'branch': env.str('ROLLBAR_BRANCH', default=''),
    'root': BASE_DIR,
    'exception_level_filters': [
        (PermissionDenied, 'warning'),
        (Http404, 'warning')
    ]
}

# Message classes set to be compatible with Bootstrap 5 alerts.
MESSAGE_TAGS = {
    messages.ERROR: 'danger error',
    messages.DEBUG: 'dark',
}


def show_toolbar(request):
    if request.user and request.user.username in DEBUG_TOOLBAR_ALLOWED_USERS:
        return True
    return False


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
    'INTERCEPT_REDIRECTS': False,
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 300,
    }
}

NEWS_PER_PAGE = 15

CRISPY_TEMPLATE_PACK = 'bootstrap4'

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "compiled_assets"),
)

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        # This setting is badly named, it's the bundle dir relative
        # to whatever you have in your STATICFILES_DIRS
        'BUNDLE_DIR_NAME': '',
        'STATS_FILE': os.path.join(BASE_DIR, "webpack_resources", 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    # Throttles are used to control the rate of requests that clients can make to an API.
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        # Limit the number of rest calls made by unauthenticated users.
        'anon': '100/day',
    },
    # default filter backends for views - enables querying/filtering after
    # specifying `filterset_fields` in a view
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',)
}
