#!/usr/bin/python
# Set up the Django Environment
import sys
import site
import os
site.addsitedir('~/.virtualenvs/venvdj1.4/local/lib/python2.7/site-packages')

sys.path.append('/srv/www/storage')


activate_env=os.path.expanduser("~/.virtualenvs/venvdj1.4/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

from django.core.management import setup_environ 
import settings
setup_environ(settings)
import datetime,urllib2,json
from django.core.mail import send_mail, EmailMultiAlternatives
from archive.models import *
from django.template.loader import render_to_string
from django.template.context import RequestContext
from dateutil.relativedelta import *
from django.contrib.sites.models import Site
from global_request_middleware import *
from django.utils import timezone

def ContainerArchive():
    try:
        print '[SMM] Sending mail to operator for archiving containers'
        #oggi=datetime.datetime.now()
        oggi=timezone.localtime(timezone.now())
        print 'oggi',oggi
        indirizzo=Site.objects.get(name='LASDomain')
        print 'indir',indirizzo
        url=indirizzo.domain
        url+='/storage/archive/'
        print 'url',url
        indir=Urls.objects.get(default=1).url
        #mi restituisce solo i campioni di Bertotti_WG
        req = urllib2.Request(indir+"/api/archivealiquots/", headers={"workingGroups" : 'Bertotti_WG'})
        u = urllib2.urlopen(req)
        data = json.loads(u.read())
        
        #le chiavi corrispondono agli utenti a cui mandare le e-mail
        superutente=User.objects.filter(username='andrea.bertotti')
        zanella=User.objects.filter(username='eugenia.zanella')
        for k,val in data.items():
            print 'k',k
            print 'val',val
            lisgen=[]
            lisdata=[]
            lisfin=[]
            for elem in val:
                v=elem.split('|')         
                laliq=Aliquot.objects.filter(genealogyID=v[0],endTimestamp=None)
                if len(laliq)!=0:
                    piastra=laliq[0].idContainer.barcode
                    if 'diatech' not in piastra.lower(): 
                        lisgen.append(v[0])
                        lisfin.append(laliq[0].idContainer)
                        dat=v[1].split('-')
                        datafin=dat[2]+'-'+dat[1]+'-'+dat[0]
                        lisdata.append(datafin)
            print 'lisfin',lisfin
            print 'lisgen',lisgen
            file_data = render_to_string('report_alert_archive.html', {'listafin':zip(lisgen,lisfin,lisdata),'perc':url})
            loperator = User.objects.filter(username = k)
            if len(loperator)!=0:
                mailOperator = loperator[0].email
                if mailOperator!='' and loperator[0].is_active==1:
                    subject, from_email = 'Container to be archived - '+loperator[0].username, settings.EMAIL_HOST_USER
                    text_content = 'This is an important message.'
                    html_content = file_data
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [mailOperator,superutente[0].email,zanella[0].email])
                    msg.attach_alternative(html_content, "text/html")
                    print 'msg',msg
                    msg.send()
    except Exception,e:
        print 'err',e
    return

if __name__=='__main__':
    ContainerArchive()
    
