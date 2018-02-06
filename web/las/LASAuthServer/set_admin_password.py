import sys, os
sys.path.append('/srv/www/LASAuthServer')
from django.core.management import setup_environ 
import settings
setup_environ(settings)
from django.contrib.auth.models import User

if __name__ == '__main__':
    print "Setting password for LAS user `administrator`..."
    u = User.objects.get(username__exact='administrator')
    u.set_password(os.environ['ADMIN_PASSWORD'])
    u.save()
    print "Done!"
