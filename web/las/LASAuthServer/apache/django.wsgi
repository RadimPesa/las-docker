"""
WSGI config for loginman project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os, sys, site

site.addsitedir('/virtualenvs/venvdj1.4/local/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/srv/www/LASAuthServer/')

path = '/srv/www'
if path not in sys.path:
    sys.path.insert(0, '/srv/www')
os.environ['DJANGO_SETTINGS_MODULE'] = 'LASAuthServer.settings'

# Activate your virtual env
activate_env=os.path.expanduser("/virtualenvs/venvdj1.4/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))



# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
#from django.core.wsgi import get_wsgi_application
#application = get_wsgi_application()

import LASAuthServer.settings
import django.core.handlers.wsgi
_application = django.core.handlers.wsgi.WSGIHandler()
def application(environ, start_response):
        LASAuthServer.settings.BASE_URL = environ['SCRIPT_NAME']
        LASAuthServer.settings.LOGIN_URL = environ['SCRIPT_NAME'] + '/laslogin'
        return _application(environ, start_response)


# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
