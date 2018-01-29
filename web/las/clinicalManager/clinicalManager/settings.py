# Django settings for CliniaclManager project.
DB_NAME = 'clinical'
DB_USERNAME = 'clinicalusr'
DB_PASSWORD = 'clinicalpwd2013'
DB_HOST='lasmysql'

from os import path
import os
from utils_settings import getLASUrl
DOMAIN_URL=getLASUrl()
#DOMAIN_URL = 'https://lastest.polito.it'
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS
BASEDIR = path.dirname(path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME' : DB_NAME,
        'USER' : DB_USERNAME,
        'PASSWORD' : DB_PASSWORD,
        'HOST' : DB_HOST,
        'PORT': '3306',
        'OPTIONS' : {"init_command": "SET default_storage_engine=INNODB"},
    }
}

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

SITE_ID = 2

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = '/home/piero/Documenti/fixingCellLine/trunk/cell_media'
#print BASEDIR.rpartition('/')[0]
MEDIA_ROOT = path.join(BASEDIR.rpartition('/')[0], 'clinical_media/')
TEMP_URL = path.join(BASEDIR.rpartition('/')[0],'clinical_media/tempFiles/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/clinical_media/'

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
SECRET_KEY = '5#y86p9_kzxpy=tp394tohi&z3*$88qe@f8u6wg8u7av4m%o51'

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
    #'patient.middleware.AjaxRedirect',
    #'api.middleware.AjaxRedirect',
    #'api.middleware.ContentTypeMiddleware',
    #'api.middleware.XsSharingMiddleware',
    'global_request_middleware.GlobalRequestMiddleware',
    'cookieMiddleware.ExtendUserSession',
    #'catissue.global_request_middleware.GlobalRequestMiddleware',

)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    #'clinical.context_processor.custom_context_processor',
    'django.core.context_processors.request',
)

EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_HOST_USER = os.environ['EMAIL_ADMIN_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_ADMIN_PASSWORD']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_USE_TLS = os.environ['EMAIL_USE_TLS']

ROOT_URLCONF = 'clinicalManager.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'clinicalManager.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/srv/www/clinicalManager/templates/",
)

INSTALLED_APPS = (
    'django.contrib.auth', # an authentication system
    'django.contrib.contenttypes', # a framework fro content types
    'django.contrib.sessions', # a session framework
    'django.contrib.sites', # a framework for managing multiple sites with one Django installation
    'django.contrib.messages', # a messaging framework
    'django.contrib.staticfiles', # a framework for managing static files
    'django.contrib.admin',
    'django.contrib.admindocs',
    'rest_framework', # new framework for APIs
    #'rest_framework_swagger', # APIs docs
    'LASAuth', # for login manager
    'editpermission',
    'global_request_middleware',
    'cookieMiddleware',
    'corePatient',
    # 'coreOncoPath', brand new module
    'coreProject',
    'coreInstitution',
    'appEnrollment',
    'appPathologyManagement',
    'appUtils',

)


# FOR LOGIN MANAGER
AUTHENTICATION_BACKENDS = (
    'LASAuth.auth.LASAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

SESSION_ENGINE = 'django.contrib.sessions.backends.db' # _non deve essere_ django.contrib.sessions.backends.file!

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

LOGIN_URL = '/clinical/auth/startlogin/'
LAS_AUTH_SERVER_URL = DOMAIN_URL + '/las/laslogin/'
LAS_AUTH_USE_HTTPS=True
THIS_APP_SHORTNAME = 'CMM' # 'nome_breve_del_modulo' # e.g., XMM, BBMM
AUTH_SECRET_KEY = '+{Qy`+($C$8|k^O&%yT!t#iDM^4Gd,(q(x+4d7-w%9I& _a|atgg~@]_>-|T>nbm'
LAS_URL = DOMAIN_URL + '/las/'
USE_GRAPH_DB = True
APPNAME = 'clinical'
APPNAME_FOR_DECORATORS = 'clinicalManager'
GRAPH_DB = 'lasneo4j'
GRAPH_DB_URL= 'http://'+GRAPH_DB+':7474/db/data'

# Per generare una chiave segreta casuale:
# define('AUTH_KEY',        '+{Qy`+($C$8|k^O&%yT!t#iDM^4Gd,(q(x+4d7-w%9I& _a|atgg~@]_>-|T>nbm');
# define('SECURE_AUTH_KEY', 'COIJktB/K+bk)3- @_3`HaHH{!MJQ}-g-Cad+_l-D)PSoR?NlAg`2LA^iZ9@>Kv2');
# define('LOGGED_IN_KEY',   '{ZhUmog/p21}t.),4`8ZwTF@4a,nKdPsC6C|zYU5LVfM+AFP+Xj*>VzNr*.4kZT+');
# define('NONCE_KEY',       '!99@O.^T;fTDl|Y.>fQos?-t~{g:ed^RRaV`-boeo=b) VJ6fKX+};:{QiK<-Sj|');

HOST_URL= '/clinical'
#HUB_URL='https://lasircc.polito.it/lashub'


CSRF_COOKIE_PATH = '/clinical'
SESSION_COOKIE_PATH = '/clinical'
#SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 14400
API_SHARED_KEY ='u8Hk;GVTbW|siLN0([_gryt2/c)]G7@g$l}.@t?A+Sq/=2l||2ZVkV@w)9+uLQE('
SYNC_PERMISSIONS_URL= DOMAIN_URL + '/las/syncPermissions/'

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
            '()': 'django.utils.log.RequireDebugFalse'
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

CORE_PATIENT_URL=DOMAIN_URL+'/clinical/corePatient/'


REST_FRAMEWORK = {
    #'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'PAGINATE_BY': 10,
    'PAGINATE_BY_PARAM': 'page_size'  # Allow client to override, using `?page_size=xxx`
}


SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
