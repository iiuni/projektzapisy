# Django settings for fereol project.

import os
import logging
import environ

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()

environ.Env.read_env(os.path.join(BASE_DIR, os.pardir, 'env', '.env'))

DEBUG = env.bool('DEBUG')
RELEASE = env.bool('RELEASE')

# With DEBUG = False Django will refuse to serve requests to hosts different than this one.
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

EMAIL_BACKEND = env.str('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EVENT_MODERATOR_EMAIL = 'zapisy@cs.uni.wroc.pl'
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', default='webmaster@localhost')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)
EMAIL_HOST = env.str('EMAIL_HOST', default='')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=25)
SERVER_EMAIL = env.str('SERVER_EMAIL', default='root@localhost')


# django-environ doesn't support nested arrays, but decoding json objects works fine
ARRAY_VALS = env.json('ARRAY_VALS', {})
ADMINS = ARRAY_VALS['ADMINS'] if ARRAY_VALS else []

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env.str('DATABASE_NAME', default='fereol'),
        'PORT': env.str('DATABASE_PORT', default='5432'),
        'USER': env.str('DATABASE_USER', default='fereol'),
        'PASSWORD': env.str('DATABASE_PASSWORD'),
        'HOST': 'localhost',
        'CHARSET': 'utf8',
        'USE_UNICODE': True,
    }
}

# mass-mail account
# You can test sending with:
# $ python -m smtpd -n -c DebuggingServer localhost:1025

MASS_MAIL_FROM = 'zapisy@cs.uni.wroc.pl'
EMAIL_COURSE_PREFIX = '[System Zapisow] ' # please don't remove the trailing space

LOGGING = {
        'version': 1,
        'disable_existing_loggers': False, # keep Django's default loggers
        'formatters': {
                'timestampthread': {
                        'format': "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(name)-20.20s]  %(message)s",
                },
        },
        'handlers': {
                'logfile': {
                        # optionally raise to INFO to not fill the log file too quickly
                        'level': 'DEBUG', # DEBUG or higher goes to the log file
                        'class':'logging.handlers.RotatingFileHandler',
                        # IMPORTANT: replace with your desired logfile name!
                        'filename': 'logs/djangoproject.log',
                        'maxBytes': 50 * 10**6, # will 50 MB do?
                        'backupCount': 3, # keep this many extra historical files
                        'formatter': 'timestampthread'
                },
        },
        'loggers': {
                'django': { # configure all of Django's loggers
                        'handlers': ['logfile'],
                        'level': 'DEBUG', # set to debug to see e.g. database queries
                },
                'apps': {
                        'handlers': ['logfile'],
                        'level': 'DEBUG',
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
ugettext = lambda s: s
LANGUAGES = (
    ('pl', ugettext('Polish')),
    ('en', ugettext('English')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_ETAGS = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = '6$u2ggeh-!^hxep3s4h$3z&2-+3c@sy7-sy8349+l-1m)9r0fn'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'OPTIONS': {
            "debug": env.bool('TEMPLATE_DEBUG'),
            'context_processors': [
                'django.contrib.messages.context_processors.messages',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                    'django.template.loaders.eggs.Loader',
                ]),
            ]
        },
    },
]


# Be careful with the order! SessionMiddleware
# and Authentication both must come before LocalePref which
# must precede LocaleMiddleware, and Common must go afterwards.
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'middleware.localePrefMiddleware.LocalePrefMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'middleware.error_handling.ErrorHandlerMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',
    'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
]

ROOT_URLCONF = 'zapisy.urls'

INSTALLED_APPS = (
    'modeltranslation', # needs to be before django.contrib.admin

    'rest_framework',
    
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
    'pipeline',
    'apps.enrollment.courses',
    'apps.enrollment.records',
    'apps.statistics',
    'apps.news',
    'apps.offer.preferences',
    'apps.offer.proposal',
    'apps.offer.vote',
    'apps.offer.desiderata',

    'apps.utils',
    'apps.schedule',
    #'debug_toolbar',
    'apps.grade.poll',
    'apps.grade.ticket_create',
    #'apps.mobile',
    'apps.email_change',
    'apps.schedulersync',
    'django_extensions',
    'django_filters',
    'autoslug',
    'el_pagination',
    'apps.notifications',
    'django_cas_ng',

    'test_app',
    'webpack_loader',
)

MODELTRANSLATION_FALLBACK_LANGUAGES = ('pl',)

AUTHENTICATION_BACKENDS = (
    'apps.users.auth_backend.BetterBackend',
    'django_cas_ng.backends.CASBackend',
)

TIME_FORMAT = "H:i"
DATETIME_FORMAT = "j N Y, H:i"

CAS_SERVER_URL = 'https://login.uni.wroc.pl/cas/'
CAS_CREATE_USER = False
CAS_LOGIN_MSG = u'Sukces! Zalogowano przez USOS (login: %s).'

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/users/'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

#settings for enrollment
ECTS_BONUS = 5 # ECTS_BONUS * ECTS = abs(t0-t1); set to 7, if changed, change also get_t0_interval()
ECTS_LIMIT = 35
ECTS_FINAL_LIMIT = 45

VOTE_LIMIT = 60

M_PROGRAM = 1
LETURE_TYPE = '1'
QUEUE_PRIORITY_LIMIT = 5

SESSION_COOKIE_PATH = '/;HttpOnly'
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# Since Django 1.6 the default session serializer is json, which
# doesn't have as many features, in particular it cannot serialize
# custom objects, and we need this behavior.
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

DEBUG_TOOLBAR_ALLOWED_USERS = env.list('DEBUG_TOOLBAR_ALLOWED_USERS', default=[])
DEBUG_TOOLBAR_PANELS = env.list('DEBUG_TOOLBAR_PANELS', default=[])

ROLLBAR = env.dict('ROLLBAR', default={})


def show_toolbar(request):
    if request.user and request.user.username in DEBUG_TOOLBAR_ALLOWED_USERS:
        return True
    return False


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
    'INTERCEPT_REDIRECTS' : False,
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 300,
    }
}

NEWS_PER_PAGE = 15

# The URL to the issue tracker where users
# can submit issues or bug reports. Used in several templates.
ISSUE_TRACKER_URL = "https://tracker-zapisy.ii.uni.wroc.pl"
# As above, but takes the user straight to the "create new issue" page
ISSUE_TRACKER_NEW_ISSUE_URL = "https://tracker-zapisy.ii.uni.wroc.pl/projects/zapisy-tracker/issues/new"

if os.path.isfile(os.path.join(BASE_DIR, 'zapisy', 'pipeline.py')):
    execfile(os.path.join(BASE_DIR, 'zapisy', 'pipeline.py'))

PIPELINE = env.bool('PIPELINE')
PIPELINE_AUTO = False
PIPELINE_VERSION = True
PIPELINE_YUI_BINARY = 'java -jar libs/yuicompressor-2.4.7.jar'
#PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.jsmin.JSMinCompressor'
#PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.csstidy.CSSTidyCompressor'

COMPRESS_OFFLINE = env.bool('COMPRESS_OFFLINE', default=False)
COMPRESS_ENABLED = env.bool('COMPRESS_ENABLED', default=False)
COMPRESS_OFFLINT_TIMEOUT = env.int('COMPRESS_OFFLINT_TIMEOUT', default=0)

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
	os.path.join(BASE_DIR, "compiled_assets"),
)

STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'
PIPELINE_STORAGE = 'pipeline.storage.PipelineFinderStorage'
PIPELINE_VERSIONING = 'pipeline.versioning.hash.MD5Versioning'
STATICFILES_FINDERS = (
  'pipeline.finders.PipelineFinder',
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
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
        'IGNORE': ['.+\.hot-update.js', '.+\.map']
    }
}
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}
