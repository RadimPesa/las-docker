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
import datetime,urllib,urllib2,json
from django.core.mail import send_mail, EmailMultiAlternatives
from archive.models import *
from django.template.loader import render_to_string
from django.template.context import RequestContext
from dateutil.relativedelta import *
from django.contrib.sites.models import Site
from django.utils import timezone

def ContainerReturn():
    try:
        print '[SMM] Sending mail to operator for returning containers'
        dizutenti={}
        #oggi=datetime.datetime.now()
        oggi=timezone.localtime(timezone.now())
        print 'oggi',oggi
        indirizzo=Site.objects.get(name='LASDomain')
        print 'indir',indirizzo
        url=indirizzo.domain
        url+='/storage/put/start/'
        print 'url',url
        
        #prendo tutti i container ancora da posizionare
        listacont=Container.objects.all().exclude(owner=None).exclude(owner='')
        print 'liscont',listacont
        #lista con dentro tutti i container di cui voglio avere le informazioni
        listatot=[]
        dizdate={}
        #creo una lista con tutti gli utenti di Bertotti_WG
        bertwg=WG.objects.get(name='Bertotti_WG')
        lisutenti=WG_User.objects.filter(WG=bertwg)
        lisnomi=[]
        for ut in lisutenti:
            if ut.user.username not in lisnomi:
                lisnomi.append(ut.user.username)
                
        for cont in listacont:
            #if cont.owner in lisnomi:
            #prendo tutte le righe dell'audit che riguardano quel cont ordinandole in base alla data
            lisaudit=ContainerAudit.objects.filter(id=cont.id).exclude(owner=None).order_by('-_audit_timestamp')
            #nel primo valore della lista audit, ho la data in cui e' stata prelevata l'ultima volta quella provetta
            tempo=lisaudit[0]._audit_timestamp
            #print 'tempo',tempo
            val=oggi-tempo            
            #if tempo<oggi-relativedelta(days=7):
            if tempo<oggi-timezone.timedelta(days = 7):
                #se e' passata piu' di una settimana, allora devo segnalare all'utente di riposizionarlo
                #print 'precedente',val
                if dizutenti.has_key(cont.owner):
                    lista=dizutenti[cont.owner]
                    lista.append(cont)
                else:
                    lista=[]
                    lista.append(cont)
                laliq=Aliquot.objects.filter(idContainer=cont,endTimestamp=None)
                for aliq in laliq:
                    listatot.append(aliq.genealogyID)
                dizdate[cont.barcode]=tempo
                
                dizutenti[cont.owner]=lista
        
        val1={'lista':json.dumps(listatot)}
        data = urllib.urlencode(val1)
        indir=Urls.objects.get(default=1).url
        req = urllib2.Request(indir+"/api/return/container/",data=data, headers={"workingGroups" : 'admin'})
        u = urllib2.urlopen(req)
        diz =  json.loads(json.loads(u.read())['data'])
        print 'diz',diz
        print 'dizdate',dizdate
        
        #le chiavi corrispondono agli utenti a cui mandare le e-mail
        superutente=User.objects.filter(username='andrea.bertotti')
        zanella=User.objects.filter(username='eugenia.zanella')
        for k,val in dizutenti.items():
            print 'k',k
            print 'val',val
            lisdiz=[]
            for cont in val:
                
                laliq=Aliquot.objects.filter(idContainer=cont,endTimestamp=None)   
                for aliq in laliq:
                    diztot={}
                    diztot['cont']=cont                   
                    diztemp=diz[aliq.genealogyID]
                    diztot['gen']=aliq.genealogyID
                    proc=diztemp['procedure']
                    diztot['proc']=proc
                    if proc=='':
                        dd=''
                    else:
                        data=dizdate[cont.barcode]
                        dd=str(data.day).zfill(2)+'-'+str(data.month).zfill(2)+'-'+str(data.year)
                    diztot['data']=dd
                    lisdiz.append(diztot)
                if len(laliq)==0:
                    diztot={}
                    diztot['cont']=cont
                    diztot['gen']=''
                    diztot['proc']=''
                    diztot['data']=''
                    lisdiz.append(diztot)

            print 'lisdiz',lisdiz
            print 'len lisdiz',len(lisdiz)
            file_data = render_to_string('report_alert_return.html', {'listafin':lisdiz,'perc':url})
            loperator = User.objects.filter(username = k)
            if len(loperator)!=0:
                mailOperator = loperator[0].email
                if mailOperator!='' and loperator[0].is_active==1:
                    subject, from_email = 'Container to be returned - '+loperator[0].username, settings.EMAIL_HOST_USER
                    text_content = 'This is an important message.'
                    html_content = file_data
                    if k in lisnomi:
                        #se l'utente fa parte del Bertotti_WG
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [mailOperator,superutente[0].email,zanella[0].email])
                        print 'Bertotti_WG',k
                    else:
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [mailOperator])
                    msg.attach_alternative(html_content, "text/html")
                    print 'msg',msg
                    msg.send()
    except Exception,e:
        print 'err',e
    return

if __name__=='__main__':
    ContainerReturn()
    
