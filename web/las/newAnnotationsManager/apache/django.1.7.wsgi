import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('~/.virtualenvs/venvdj1.7/local/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/srv/www/annotationsManager/')

path = '/srv/www'
if path not in sys.path:
    sys.path.insert(0, '/srv/www')

os.environ['DJANGO_SETTINGS_MODULE'] = 'annotationsManager.settings'

# Activate your virtual env
activate_env=os.path.expanduser("~/.virtualenvs/venvdj1.7/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

import annotationsManager.settings
#import django.core.handlers.wsgi
#_application = django.core.handlers.wsgi.WSGIHandler()

from django.core.wsgi import get_wsgi_application
_application = get_wsgi_application()

def application(environ, start_response):
        if not annotationsManager.settings.LOGIN_URL.startswith(environ['SCRIPT_NAME']):
            annotationsManager.settings.LOGIN_URL = environ['SCRIPT_NAME'] + annotationsManager.settings.LOGIN_URL
        annotationsManager.settings.BASE_URL = environ['SCRIPT_NAME']
        annotationsManager.settings.MEDIA_URL = environ['SCRIPT_NAME'] + annotationsManager.settings.MEDIA_URL
        return _application(environ, start_response)
