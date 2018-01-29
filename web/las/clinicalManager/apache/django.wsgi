import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/virtualenvs/venvdj1.7/local/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/srv/www/clinicalManager/')


path = '/srv/www'
if path not in sys.path:
    sys.path.insert(0, '/srv/www')

os.environ['DJANGO_SETTINGS_MODULE'] = 'clinicalManager.settings'

# Activate your virtual env
activate_env=os.path.expanduser("/virtualenvs/venvdj1.7/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))


import clinicalManager.settings
from django.core.wsgi import get_wsgi_application
_application = get_wsgi_application()
def application(environ, start_response):
        clinicalManager.settings.LOGIN_URL = environ['SCRIPT_NAME'] + clinicalManager.settings.LOGIN_URL
        clinicalManager.settings.BASE_URL = environ['SCRIPT_NAME']
        return _application(environ, start_response)

#import os
#import sys
#sys.path.append('/srv/www/CellLine/')

#path = '/srv/www'
#if path not in sys.path:
#    sys.path.insert(0, '/srv/www')

#os.environ['DJANGO_SETTINGS_MODULE'] = 'cellLineManager.settings'

#import cellLineManager.settings
#import django.core.handlers.wsgi
#_application = django.core.handlers.wsgi.WSGIHandler()
#def application(environ, start_response):
#        cellLineManager.settings.LOGIN_URL = environ['SCRIPT_NAME'] + cellLineManager.settings.LOGIN_URL
#        cellLineManager.settings.BASE_URL = environ['SCRIPT_NAME'] 
#        return _application(environ, start_response)

