# Django settings for caQuery project.
DB_NAME = 'query'
DB_USERNAME = 'queryusr'
DB_PASSWORD = 'querypwd2012'
DB_HOST='lasmysql'

from os import path
import os
import mongoengine
from utilsLASUrl import getLASUrl
DOMAIN_URL=getLASUrl()


MONGO_USERNAME=os.environ['MONGO_INITDB_ROOT_USERNAME']
MONGO_PASSWORD=os.environ['MONGO_INITDB_ROOT_PASSWORD']
MONGO_PORT = 27017
MONGO_HOST = 'lasmongodb'


#BASEDIR = path.dirname(path.abspath(__file__))


DEBUG = False

if "DEBUG_LAS" in os.environ:
    if os.environ['DEBUG_LAS'] in ('TRUE', 'True', 'true'):
        DEBUG = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS
BASEDIR = path.dirname(path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DB_NAME, #query',                      # Or path to database file if using sqlite3.
        'USER': DB_USERNAME,                      # Not used with sqlite3.
        'PASSWORD': DB_PASSWORD,                  # Not used with sqlite3.
        'HOST': DB_HOST,                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    },            
   #'annotations': {
   #     'NAME': 'annotations',
   #     'ENGINE': 'django_mongodb_engine',
   #     'USER': '',
   #     'PASSWORD': '',
   #     'HOST': 'localhost',
   #     'PORT': '27017',
   # },
   # 'templates': {
   #     'NAME': 'templates',
   #     'ENGINE': 'django_mongodb_engine',
   #     'USER': '',
   #     'PASSWORD': '',
   #     'HOST': 'localhost',
   #     'PORT': '27017',
   # }
}

#mongoengine.connect('mdam', host=DB_HOST, port=MONGO_PORT, username=MONGO_USERNAME, password=MONGO_PASSWORD)
mongoengine.connect('mdam', host=MONGO_HOST, username=MONGO_USERNAME, password=MONGO_PASSWORD, authentication_source='admin')

GRAPH_DB = 'lasneo4j'
GRAPH_DB_URL= 'http://'+GRAPH_DB+':7474/db/data'

EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_HOST_USER = os.environ['EMAIL_ADMIN_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_ADMIN_PASSWORD']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_USE_TLS = os.environ['EMAIL_USE_TLS']
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_SUBJECT_PREFIX = '[MDAM]'


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

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = path.join(BASEDIR, '/caQuery/src/caQuery/_caQuery/caQuery_media')
#"GET /caQuery_media/css/style.css HTTP/1.1" 404 1786
MEDIA_ROOT = '/srv/www/caquery/_caQuery/caQuery_media'
 
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/caQuery_media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
#ADMIN_MEDIA_PREFIX = '/static/admin/'

TEMP_URL = path.join(BASEDIR,'_caQuery/caQuery_media/tmp/')


# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'voohs7l*y4_3xdc7%c-bi$n!za__7c)58y-4c@k71e(x5$j9*3'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
#    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    '_caQuery.middleware.AjaxRedirect',
    'api.middleware.ContentTypeMiddleware',
    'api.middleware.XsSharingMiddleware',
    'global_request_middleware.GlobalRequestMiddleware',
    'cookieMiddleware.ExtendUserSession',
)

ROOT_URLCONF = 'caquery.urls'

TEMPLATE_DIRS = (
    #"C:/Users/Feffy/Desktop/Feffy/Workspace/caQuery/src/caQuery/_caQuery/templates/"
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
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    '_caQuery',
    'piston',
    'LASAuth',
    'mongoengine',
    'editpermission',
    'global_request_middleware',
    'cookieMiddleware',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
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


TEMPLATE_CONTEXT_PROCESSORS = (
"django.contrib.auth.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"django.core.context_processors.request",
"django.core.context_processors.static",
"django.contrib.messages.context_processors.messages",
"_caQuery.context_processors.custom_context_processor",
)

#mongoengine.connect('MAM_NoSql_db', username='smellai', password='167048')

AUTHENTICATION_BACKENDS = (
    'LASAuth.auth.LASAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/auth/startlogin/'
LAS_AUTH_SERVER_URL = DOMAIN_URL + '/las/laslogin/'
LAS_AUTH_USE_HTTPS = True
#LAS_AUTH_SERVER_URL = 'https://devircc.polito.it/lasauth/laslogin/'
#LAS_AUTH_SERVER_URL = 'http://dom87.polito.it:8000/laslogin/'
THIS_APP_SHORTNAME='MDAM' # e.g., XMM, BBMM
AUTH_SECRET_KEY = 'CW>M=I(_o(momyfsgH{dOE1`}XGV|)pnGBV]O{yYhP^$SGiYn&,6ic~NBE8{<&)-'
API_SHARED_KEY ='u8Hk;GVTbW|siLN0([_gryt2/c)]G7@g$l}.@t?A+Sq/=2l||2ZVkV@w)9+uLQE(' 
SYNC_PERMISSIONS_URL=DOMAIN_URL + '/las/syncPermissions/'
LAS_URL = DOMAIN_URL + '/las'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

CSRF_COOKIE_PATH = '/mdam'
SESSION_COOKIE_PATH = '/mdam'
#SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 14400
#SESSION_COOKIE_HTTPONLY = False


USE_GRAPH_DB= True
APPNAME='_caQuery'

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
