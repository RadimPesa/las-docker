from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
import urllib
import urllib2
import hashlib
import hmac
import json
from django.conf import settings
from catissue.apisecurity.apikey import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        #app_label="archive"
        content_type = ContentType.objects.get(model="member")
        permslist=""
        permslistname=""
        for perm in Permission.objects.filter(content_type_id=content_type.id):
            if perm.codename !="add_member" and perm.codename !="change_member" and perm.codename !="delete_member" :
                permslist+=perm.codename+","
                permslistname+=perm.name+","
                print perm.codename
        url=settings.SYNC_PERMISSIONS_URL
        try:
            t = getApiKey()
        except Exception,e:
            print e
        
        values = {'lista' : permslist, 'listanomi':permslistname, 'shortname' :settings.THIS_APP_SHORTNAME, 'api_key':t}
        data = urllib.urlencode(values)
        try:
            resp=urllib2.urlopen(url, data)
            res1 =  resp.read()
            if res1=='ok':
                self.stdout.write('Successfully update')

        except urllib2.HTTPError, e:
            if str(e.code)== '403':
                self.stdout.write('Forbidden Access to API')
            else:
                self.stdout.write("Error: "+str(e.code)+"\n")

    
            