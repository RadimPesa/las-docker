import os
import sys
import site

site.addsitedir('/virtualenvs/venvdj1.4/local/lib/python2.7/site-packages')
sys.path.append('/srv/www/caxeno/')

path = '/srv/www'
if path not in sys.path:
    sys.path.insert(0, '/srv/www')

os.environ['DJANGO_SETTINGS_MODULE'] = 'caxeno.settings'


# Activate your virtual env
activate_env=os.path.expanduser("/virtualenvs/venvdj1.4/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

import caxeno.settings
import django.core.handlers.wsgi
_application = django.core.handlers.wsgi.WSGIHandler()
def application(environ, start_response):
        #if not caxeno.settings.LOGIN_URL.startswith(environ['SCRIPT_NAME']):
        caxeno.settings.LOGIN_URL = environ['SCRIPT_NAME'] + caxeno.settings.LOGIN_URL
        caxeno.settings.BASE_URL = environ['SCRIPT_NAME']
        #caxeno.settings.MEDIA_URL = environ['SCRIPT_NAME'] + caxeno.settings.MEDIA_URL
        return _application(environ, start_response)

