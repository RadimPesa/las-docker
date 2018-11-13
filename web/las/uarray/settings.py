# Django settings for uArray local.
DB_NAME = 'uarray'
DB_USERNAME = 'uarrayusr'
DB_PASSWORD = 'uarraypwd2012'
DB_HOST='lasmysql'

from os import path
import os

BASEDIR = path.dirname(path.abspath(__file__))

DEBUG = False

if "DEBUG_LAS" in os.environ:
    if os.environ['DEBUG_LAS'] in ('TRUE', 'True', 'true'):
        DEBUG = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'uarray',                      # Or path to database file if using sqlite3.
        'USER': 'uarrayusr',                      # Not used with sqlite3.
        'PASSWORD': 'uarraypwd2012',                  # Not used with sqlite3.
        'HOST': DB_HOST,                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    }
}

from utils import getLASUrl
DOMAIN_URL=getLASUrl()

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
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

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

USE_TZ = True

#*** AGGIUNTO ***
#DATE_FORMAT = 'j, Y'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = path.join(BASEDIR, 'MMM/uarray_media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/uarray_media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/media/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'



# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
 #   'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'a#9vrkqk^*i--p9o2tscj!e)dm68ntdbz$rsg=%xz4ziyziu!1'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'MMM.middleware.AjaxRedirect',
    'global_request_middleware.GlobalRequestMiddleware',
    'cookieMiddleware.ExtendUserSession',
)

ROOT_URLCONF = 'urls'



INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'MMM',
    'LASAuth',
    'piston',
    'editpermission',
    'global_request_middleware',
    'cookieMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'LASAuth.auth.LASAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

SESSION_ENGINE = 'django.contrib.sessions.backends.db' # _non deve essere_ django.contrib.sessions.backends.file!


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
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

TEMPLATE_CONTEXT_PROCESSORS = ('django.core.context_processors.request',
                                'django.contrib.auth.context_processors.auth',
                                'django.core.context_processors.debug',
                                'django.core.context_processors.i18n',
                                'django.core.context_processors.media',
                                'MMM.context_processor.custom_context_processor',
)

LOGIN_URL = '/auth/startlogin/'
LAS_AUTH_SERVER_URL = DOMAIN_URL + '/las/laslogin/'
LAS_URL = DOMAIN_URL + '/las'
LAS_AUTH_USE_HTTPS = True
THIS_APP_SHORTNAME='MMM'
AUTH_SECRET_KEY = 'Y7~!b$`}=(TX?*ZHhHu )%sQ-.DTcfg#49qpR+o~G:0!-B*r!nE407_+XdF`X3Ro'
API_SHARED_KEY = 'u8Hk;GVTbW|siLN0([_gryt2/c)]G7@g$l}.@t?A+Sq/=2l||2ZVkV@w)9+uLQE('
SYNC_PERMISSIONS_URL=DOMAIN_URL + '/las/syncPermissions/'
APPNAME = 'MMM'
USE_GRAPH_DB = True
GRAPH_DB = 'lasneo4j'
GRAPH_DB_URL= 'http://'+GRAPH_DB+':7474/db/data'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}
                   
CSRF_COOKIE_PATH = '/micro'
SESSION_COOKIE_PATH = '/micro'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 14400
