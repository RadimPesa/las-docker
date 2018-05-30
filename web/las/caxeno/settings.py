# Django settings for caxeno project.
DB_NAME = 'caxeno'
DB_USERNAME = 'xenousr'
DB_PASSWORD = 'xenopwd2012'
DB_HOST='lasmysql'

from os import path
import os
from utils import getLASUrl
DOMAIN_URL=getLASUrl()

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
)


MANAGERS = ADMINS
BASEDIR = path.dirname(path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE' : 'django.db.backends.mysql',
        'NAME' : DB_NAME,
        'USER' : DB_USERNAME,
        'PASSWORD' : DB_PASSWORD,
        'HOST' : DB_HOST,
        'PORT' : '3306',
        'OPTIONS' : {"init_command": "SET default_storage_engine=INNODB"},
    }
}

EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_HOST_USER = os.environ['EMAIL_ADMIN_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_ADMIN_PASSWORD']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_USE_TLS = os.environ['EMAIL_USE_TLS']
EMAIL_SUBJECT_PREFIX = '[XMM]'


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Rome'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

USE_TZ = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path.join(BASEDIR, 'xenopatients/xeno_media/')
#MEDIA_ROOT = "/home/piero/Scrivania/Documenti/caxeno/xenopatients/xeno_media"

# URL that handles the media served from  MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/xeno_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
STATIC_URL = '/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '((j#x&v-(sdgmzb1f3#m@7znq_$$l=-!9r^*kn)wi1z-*cpy5#'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'xenopatients.middleware.AjaxRedirect',
    'api.middleware.AjaxRedirect',
    'xenopatients.mw.threadlocals.ThreadLocals',
    'api.middleware.XsSharingMiddleware',
    'api.middleware.ContentTypeMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'global_request_middleware.GlobalRequestMiddleware',
    'cookieMiddleware.ExtendUserSession',
)

ROOT_URLCONF = 'caxeno.urls'

TEMPLATE_DIRS = (
    '/srv/www/caxeno/xenopatients/template',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'xenopatients',
    'piston',
    'LASAuth',
    'editpermission',
    'global_request_middleware',
    'cookieMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'xenopatients.context_processor.custom_context_processor',
    'django.core.context_processors.request',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda r: not DEBUG
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

AUTHENTICATION_BACKENDS = (
    'LASAuth.auth.LASAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/auth/startlogin/'
LAS_AUTH_SERVER_URL = DOMAIN_URL + '/las/laslogin/'
LAS_AUTH_USE_HTTPS = True
#LAS_AUTH_SERVER_URL = 'http://lassrv2.polito.it/las/laslogin/'
#LAS_AUTH_SERVER_URL = 'http://dom87.polito.it:8000/laslogin/'
THIS_APP_SHORTNAME='XMM' # e.g., XMM, BBMM
AUTH_SECRET_KEY = 'Q+!8l445{-d#PgQA~m@Mx~sR7%ds&&9)7(Iop,}2S|@i)854,@Rp~lxoqbpkT-_E'
SYNC_PERMISSIONS_URL=DOMAIN_URL + '/las/syncPermissions/'
API_SHARED_KEY ='u8Hk;GVTbW|siLN0([_gryt2/c)]G7@g$l}.@t?A+Sq/=2l||2ZVkV@w)9+uLQE('
LAS_URL = DOMAIN_URL + '/las'

APPNAME = 'xenopatients'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db' # _non deve essere_ django.contrib.sessions.backends.file!
#SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

CSRF_COOKIE_PATH = '/xeno'
SESSION_COOKIE_PATH = '/xeno'
#SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 14400

USE_GRAPH_DB = True
#USE_GRAPH_DB = False
GRAPH_DB = 'lasneo4j'
GRAPH_DB_URL= 'http://'+GRAPH_DB+':7474/db/data'

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
