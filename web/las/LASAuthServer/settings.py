# Django settings for loginman project.
import os
print os.environ
DB_NAME = 'lasauthserver'
DB_USERNAME = 'lasauthserver'
DB_PASSWORD = 'lasauthsrvpwd2012'
DB_HOST='lasmysql'

DEBUG = False
if "DEBUG_LAS" in os.environ:
    if os.environ['DEBUG_LAS'] in ('TRUE', 'True', 'true'):
        DEBUG = True
        print "DEBUG is set to True."
    else:
        print "DEBUG is set to False."
else:
    print "DEBUG_LAS is not defined in .env. DEBUG is by default set to False."

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DB_NAME,                      # Or path to database file if using sqlite3.
        'USER': DB_USERNAME,                      # Not used with sqlite3.
        'PASSWORD': DB_PASSWORD,                  # Not used with sqlite3.
        'HOST': DB_HOST,                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
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

SITE_ID = 1

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
MEDIA_ROOT = '/srv/www/LASAuthServer/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/lasauth_media/'

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
SECRET_KEY = '3(8)2bhh2n=t7hd38r-_$m_r2c23!f)3br3jqltys+r)m-s#9@'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cookieMiddleware.ExtendUserSession',
    #'loginapi.middleware.ContentTypeMiddleware',
)

AUTHENTICATION_BACKENDS = (
#    'django_openid_auth.auth.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)
OPENID_CREATE_USERS = True

ROOT_URLCONF = 'LASAuthServer.urls'

# Python dotted path to the WSGI application used by Django's runserver.
#WSGI_APPLICATION = 'loginman.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/srv/www/LASAuthServer/media/templates',
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
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'loginmanager',
    #'piston',
    'registration',
    'mercuric',
    'cookieMiddleware',
    'captcha',
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

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
AUTH_PROFILE_MODULE = 'loginmanager.LASUser'
LOGIN_URL = '/laslogin/'
SESSION_COOKIE_PATH = '/las'
#SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 14400
CSRF_COOKIE_PATH = '/las'

API_SHARED_KEY ='u8Hk;GVTbW|siLN0([_gryt2/c)]G7@g$l}.@t?A+Sq/=2l||2ZVkV@w)9+uLQE('


TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'loginmanager.context_processor.site_processor',
)


EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_HOST_USER = os.environ['EMAIL_ADMIN_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_ADMIN_PASSWORD']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_USE_TLS = os.environ['EMAIL_USE_TLS']
DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']



USE_GRAPH_DB = True
GRAPH_DB = 'lasneo4j'
GRAPH_DB_URL= 'http://'+GRAPH_DB+':7474/db/data'
DEMO = False


from utils import getLASUrl
DOMAIN_URL=getLASUrl()

CENTRAL_MEDIA_URL = 'http://lasircc.polito.it/lasmedia/'

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

REGISTRATION_SESSION_TIMEOUT = 10 # minutes

LOGINAS_REDIRECT_URL = "/las/index/"
LOGINAS_LOGOUT_REDIRECT_URL = "/las/index/"

HELPDESK = os.environ['HELPDESK']
