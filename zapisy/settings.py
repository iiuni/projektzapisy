# Django settings for fereol project.

import os
import logging

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

RELEASE = False

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

EVENT_MODERATOR_EMAIL = 'zapisy@ii.uni.wroc.pl'

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
 	    'NAME' : os.path.join(PROJECT_PATH, 'database/db.sqlite3'),
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

# For gmail:
#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_HOST_USER = 'youremail@gmail.com'
#EMAIL_HOST_PASSWORD = 'password'
#EMAIL_PORT = 587

#EMAIL_HOST = 'localhost'
#EMAIL_PORT = 1025
#EMAIL_HOST_USER = ''
#EMAIL_HOST_PASSWORD = ''

MASS_MAIL_FROM = 'zapisy@ii.uni.wroc.pl'

EMAIL_COURSE_PREFIX = '[System Zapisow] ' # please don't remove the trailing space

#loggin settings:

LOG_FILE = os.path.join(PROJECT_PATH, "logs/log.log")
LOG_LEVEL = logging.NOTSET
INTERNAL_IPS = ('127.0.0.1',)
logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILE, format = '%(asctime)s | %(levelname)s | %(message)s')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,    
    'formatters': {
        'simple': {
            'format': '%(asctime)s | %(message)s'
        },
    },
    'handlers': {
        'standard_file': {
            'class' : 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'filename': os.path.join(PROJECT_PATH, 'logs/log.log'),
            'maxBytes': 104857600,
            'backupCount': 5,
            'formatter': 'simple'
        },
        'backup_file': {
            'class' : 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',

            'filename': os.path.join(PROJECT_PATH, 'logs/backup.log'),
            'maxBytes': 104857600,
            'backupCount': 5,
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
     },
    'loggers': {
      
        'project.default': {
            'handlers': ['standard_file', 'mail_admins'],
            'level': 'ERROR'
        },
        'project.backup': {
            'handlers': ['backup_file'],
            'level': 'INFO'

        }
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

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = 'site_media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/'

USE_ETAGS = True

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

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

#TEMPLATE_LOADERS = (
#    'django.template.loaders.filesystem.Loader',
#    'django.template.loaders.app_directories.Loader',
##    'django.template.loaders.eggs.load_template_source',
#)

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
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    #'middleware.mobile_detector.mobileDetectionMiddleware',
    #'middleware.mobileMiddleware.SubdomainMiddleware',
    'middleware.error_handling.ErrorHandlerMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s | %(message)s'
        },
    },
    'handlers': {
        'standard_file': {
            'class' : 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'filename': os.path.join(PROJECT_PATH, 'logs/log.log'),
            'maxBytes': 104857600,
            'backupCount': 5,
            'formatter': 'simple'
        },
        'root': {
            'class' : 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'filename': os.path.join(PROJECT_PATH, 'logs/root.log'),
            'maxBytes': 104857600,
            'backupCount': 5,
            'formatter': 'simple'
        },
        'backup_file': {
            'class' : 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',

            'filename': os.path.join(PROJECT_PATH, 'logs/backup.log'),
            'maxBytes': 104857600,
            'backupCount': 5,
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
     },
    
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins',],
            'level': 'ERROR',
            'propagate': True,
        },
        'project.default': {
            'handlers': ['standard_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True
        },
        'project.backup': {
            'handlers': ['backup_file'],
            'level': 'INFO'

        }
    }
}


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',

    'modeltranslation',

    'apps.users',

    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mailer',
    'south',
    'pipeline',
    'apps.enrollment.courses',
    'apps.enrollment.records',
    'apps.statistics',
    'apps.news',
    'apps.offer.preferences',
    'apps.offer.proposal',
    'apps.offer.vote',
    'apps.offer.desiderata',

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

    'testapp'
)

AUTHENTICATION_BACKENDS = (
    'apps.users.auth_backend.BetterBackend',
)

AUTH_PROFILE_MODULE = 'users.UserProfile'

FIXTURE_DIRS = (
    os.path.join(PROJECT_PATH, 'offer/proposal/fixtures'),
)

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/users/'

SKIP_SOUTH_TESTS = True # wylacza wbudowane testy south
SOUTH_TESTS_MIGRATE = False

#TODO: udokumentowac zaleznosci!
#TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.run_tests'
#TEST_OUTPUT_VERBOSE = True
#TEST_OUTPUT_DESCRIPTIONS = True
#TEST_OUTPUT_DIR = 'xmlrunner'

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

SESSION_EXPIRE_AT_BROWSER_CLOSE	= True

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
#        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 86400,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

if os.path.isfile(os.path.join(PROJECT_PATH, 'pipeline.py')):
    execfile(os.path.join(PROJECT_PATH, 'pipeline.py'))

PIPELINE = True
PIPELINE_AUTO = False
PIPELINE_VERSION = True
PIPELINE_YUI_BINARY = 'java -jar libs/yuicompressor-2.4.7.jar'
#PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.jsmin.JSMinCompressor'
#PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.csstidy.CSSTidyCompressor'

STATIC_URL = '/static/'
STATIC_ROOT =  os.path.join(PROJECT_PATH, 'static')
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'
PIPELINE_STORAGE = 'pipeline.storage.PipelineFinderStorage'
PIPELINE_VERSIONING = 'pipeline.versioning.hash.MD5Versioning'
STATICFILES_FINDERS = (
  'pipeline.finders.PipelineFinder',
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)

STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'site_media'),
)

local_settings_file = os.path.join(PROJECT_PATH, 'settings_local.py')
if os.path.isfile(local_settings_file):
    execfile(local_settings_file)


