# Django settings for storage project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DB_NAME='storage'
DB_USERNAME='storageusr'
DB_PASSWORD='storagepwd2012'
DB_HOST='localhost'

DATABASES = {
    'default': {
        'ENGINE' : 'django.db.backends.mysql',
        'NAME' : DB_NAME,
        'USER' : DB_USERNAME,
        'PASSWORD' : DB_PASSWORD,
        'HOST' : DB_HOST,
        'PORT' : '3306',
        'OPTIONS' : {"init_command": "SET storage_engine=INNODB"},
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

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/archive_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
STATIC_URL = '/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'rv270(n5nmfur58z(rc&tsm03wrvl3762i0^so+z)$k()t!f7b'

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
    'django.contrib.messages.middleware.MessageMiddleware',
    'api.middleware.XsSharingMiddleware',
    'api.middleware.ContentTypeMiddleware',
    'archive.middleware.AjaxRedirect',
    'archive.mw.threadlocals.ThreadLocals', 
    'global_request_middleware.GlobalRequestMiddleware', 
)

ROOT_URLCONF = 'storage.urls'

TEMPLATE_DIRS = (
    '/srv/www/storage/archive/template',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'archive.context_processor.custom_context_processor',
    "django.core.context_processors.request",
    )

#LAS_URL = 'https://devircc.polito.it/lasauth/'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'archive',
    'piston',
    'LASAuth',
    'editpermission',
    'clientHUB',
    'global_request_middleware',
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

LOGIN_URL='/auth/startlogin'
#LAS_AUTH_SERVER_URL ='https://devircc.polito.it/lasauth/laslogin/'
LAS_AUTH_USE_HTTPS=False
THIS_APP_SHORTNAME='SMM'
AUTH_SECRET_KEY ='jJ3Er+Vs`+YRi+dl_@o_]rX>P4]-1,f@S2C#T38fp&!K=Y=~6~-E=?Luj]mMNxcm'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

HOST_URL= '/storage'
HUB_URL=''

API_SHARED_KEY ='u8Hk;GVTbW|siLN0([_gryt2/c)]G7@g$l}.@t?A+Sq/=2l||2ZVkV@w)9+uLQE('

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

CSRF_COOKIE_PATH = '/storage'
SESSION_COOKIE_PATH = '/storage'
#SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 14400

#SYNC_PERMISSIONS_URL='https://devircc.polito.it/lasauth/syncPermissions/'
APPNAME='archive'
USE_GRAPH_DB = False
GRAPH_DB_URL=''

from utils import getLASUrl
DOMAIN_URL=getLASUrl()
SYNC_PERMISSIONS_URL=DOMAIN_URL+'/lasauth/syncPermissions/'
LAS_URL = DOMAIN_URL+'/lasauth/'
LAS_AUTH_SERVER_URL =DOMAIN_URL+'/lasauth/laslogin/'
