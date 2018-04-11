# Django settings for prova project.
import os.path
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DB_NAME='biobanca'
DB_USERNAME='biobankusr'
DB_PASSWORD='biobankpwd2012'
DB_HOST='192.168.122.9'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DB_NAME,                      # Or path to database file if using sqlite3.
        'USER': DB_USERNAME,                      # Not used with sqlite3.
        'PASSWORD': DB_PASSWORD,                  # Not used with sqlite3.
        'HOST': DB_HOST,                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
	'OPTIONS' : {'init_command': 'SET storage_engine=INNODB'},
    }
}

EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_HOST_USER = os.environ['EMAIL_ADMIN_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_ADMIN_PASSWORD']
EMAIL_USE_TLS = os.environ['EMAIL_USE_TLS']

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

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/tissue_media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strinigs here, like "/home/html/static" or "C:/www/django/static".
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
SECRET_KEY = '@!bkk7!zi7(jw10f1yhs47&95+!7e@yxf6-j!kf2-ng9ypb1bc'

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
    'catissue.tissue.mw.threadlocals.ThreadLocals',
    'catissue.api.middleware.XsSharingMiddleware',
    'catissue.api.middleware.ContentTypeMiddleware',
    'catissue.global_request_middleware.GlobalRequestMiddleware',
    'catissue.cookieMiddleware.ExtendUserSession',
)

ROOT_URLCONF = 'catissue.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/srv/www/catissue/tissue/Templates',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'tissue.context_processor.custom_context_processor',
    "django.core.context_processors.request",
    )

#LAS_URL = 'https://lasircc.polito.it/las/'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'tissue',
    'piston',
    'LASAuth',
    'clientHUB',
    'editpermission',
    'global_request_middleware',
    'cookieMiddleware',
    'mercuric'
)

#TEMPLATE_CONTEXT_PROCESSORS = (
#"django.contrib.auth.context_processors.auth",
#"django.core.context_processors.debug",
#"django.core.context_processors.i18n",
#"django.core.context_processors.media",
#"django.core.context_processors.static",
#"django.contrib.messages.context_processors.messages",
#)

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

BASEDIR = os.path.dirname(__file__)
TEMP_URL = os.path.join(BASEDIR,'tissue/tissue_media/temp/')

AUTHENTICATION_BACKENDS = (
    'LASAuth.auth.LASAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL='/auth/startlogin'
#LAS_AUTH_SERVER_URL ='https://lasircc.polito.it/las/laslogin/'
LAS_AUTH_USE_HTTPS=True
THIS_APP_SHORTNAME='BBM'
AUTH_SECRET_KEY ='qvF`Z.+p}<rmZMMD#oe#_fT85v`UvkW2dxN(Z-&+ifQb]F -b4|C)D7|Sa}zeD,J'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

HOST_URL= '/biobank'
#HUB_URL='https://lasircc.polito.it/lashub'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

CSRF_COOKIE_PATH = '/biobank'
SESSION_COOKIE_PATH = '/biobank'
#SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 14400
API_SHARED_KEY ='u8Hk;GVTbW|siLN0([_gryt2/c)]G7@g$l}.@t?A+Sq/=2l||2ZVkV@w)9+uLQE('
#SYNC_PERMISSIONS_URL='https://lasircc.polito.it/las/syncPermissions/'
APPNAME='tissue'
USE_GRAPH_DB = True
GRAPH_DB_URL='http://'+DB_HOST+':7474/db/data/'

from utils import getLASUrl
DOMAIN_URL=getLASUrl()
SYNC_PERMISSIONS_URL=DOMAIN_URL+'/las/syncPermissions/'
LAS_URL = DOMAIN_URL+'/las/'
LAS_AUTH_SERVER_URL =DOMAIN_URL+'/las/laslogin/'
HUB_URL='' #DOMAIN_URL+'/lashub'
