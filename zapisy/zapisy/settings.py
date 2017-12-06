# Django settings for fereol project.

import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = False
RELEASE = False
TEMPLATE_DEBUG = False

# With DEBUG = False Django will refuse to serve requests to hosts different
# than this one.
ALLOWED_HOSTS = ['zapisy.ii.uni.wroc.pl']
EVENT_MODERATOR_EMAIL = 'zapisy@cs.uni.wroc.pl'

"""
DATABASES = {
     'default' : {
        'ENGINE' : 'postgresql_psycopg2',
        'NAME' : 'fereol',
        'PORT' : '',
        'USER' : 'fereol',
        'PASSWORD' : 'fereol',
        'HOST' : '',
        'CHARSET' : 'utf8',
        'USE_UNICODE' : True,
        },

     'fereol2012' : {
        'ENGINE' : 'postgresql_psycopg2',
        'NAME' : 'fereol2012',
        'PORT' : '',
        'USER' : 'fereol',
        'PASSWORD' : 'fereol',
        'HOST' : '',
        'CHARSET' : 'utf8',
        'USE_UNICODE' : True,
        }
 }
"""


DATABASES = {
     'default' : {
        'ENGINE' : 'django.db.backends.sqlite3',
        'NAME' : os.path.join(BASE_DIR, 'database/db.sqlite3'),
        'PORT' : '',
        'USER' : '',
        'PASSWORD' : '',
        'HOST' : '',
        'CHARSET' : 'utf8',
        'USE_UNICODE' : True,
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

# List of callables that know how to import templates from various sources.

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
        'django.template.loaders.eggs.Loader',
    )),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.messages.context_processors.messages',
    'django.contrib.auth.context_processors.auth',
    "django.core.context_processors.request",
)


# Be careful with the order! I'm aware that SessionMiddleware
# and Authentication both must come before LocalePref which
# must precede LocaleMiddleware, and Common must go afterwards.
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'middleware.localePrefMiddleware.LocalePrefMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    #'middleware.mobile_detector.mobileDetectionMiddleware',
    #'middleware.mobileMiddleware.SubdomainMiddleware',
    'middleware.error_handling.ErrorHandlerMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',
    'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
)

ROOT_URLCONF = 'zapisy.urls'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

INSTALLED_APPS = (
    'modeltranslation', # needs to be before django.contrib.admin
    
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
    'django_extensions',
    'django_filters',
    'autoslug',
    'endless_pagination',
    'apps.notifications',
    'django_cas_ng',

    'test_app'
)

MODELTRANSLATION_FALLBACK_LANGUAGES = ('pl',)

AUTHENTICATION_BACKENDS = (
    'apps.users.auth_backend.BetterBackend',
    'django_cas_ng.backends.CASBackend',
)

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

# that's only the example of settings_local.py file contents:
#SESSION_COOKIE_DOMAIN = '.localhost.localhost' # without port number!
#SESSION_COOKIE_DOMAIN = '.localhost.localhost' # without port number!
SESSION_COOKIE_PATH = '/;HttpOnly'
#DEBUG = False
#TEMPLATE_DEBUG = DEBUG

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# Since Django 1.6 the default session serializer is json, which
# doesn't have as many features, in particular it cannot serialize
# custom objects, and we need this behavior.
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

DEBUG_TOOLBAR_ALLOWED_USERS = [
    "209067", # Tomasz Wasilczyk
    "209138", # Arkadiusz Flinik
    "208934",
    "gosia", "stanislaw"
]

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
        'TIMEOUT': 86400,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}
        
NEWS_PER_PAGE = 15

# The URL to the issue tracker where users
# can submit issues or bug reports. Used in several templates.
ISSUE_TRACKER_URL = "https://tracker-zapisy.ii.uni.wroc.pl"
# As above, but takes the user straight to the "create new issue" page
ISSUE_TRACKER_NEW_ISSUE_URL = "https://tracker-zapisy.ii.uni.wroc.pl/projects/zapisy-tracker/issues/new"

if os.path.isfile(os.path.join(BASE_DIR, 'zapisy', 'pipeline.py')):
    exec(open(os.path.join(BASE_DIR, 'zapisy', 'pipeline.py')).read())

PIPELINE = True
PIPELINE_AUTO = False
PIPELINE_VERSION = True
PIPELINE_YUI_BINARY = 'java -jar libs/yuicompressor-2.4.7.jar'
#PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.jsmin.JSMinCompressor'
#PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.csstidy.CSSTidyCompressor'

STATIC_URL = '/static/'
STATIC_ROOT =  os.path.join(BASE_DIR, 'site_media')
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'
PIPELINE_STORAGE = 'pipeline.storage.PipelineFinderStorage'
PIPELINE_VERSIONING = 'pipeline.versioning.hash.MD5Versioning'
STATICFILES_FINDERS = (
  'pipeline.finders.PipelineFinder',
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)

LOCAL_SETTINGS = os.path.join(BASE_DIR, 'zapisy', 'settings_local.py')
if os.path.isfile(LOCAL_SETTINGS):
    print("Running local settings file {0}".format(LOCAL_SETTINGS))
    exec(open(LOCAL_SETTINGS).read())
