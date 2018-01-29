#!/usr/bin/python
# Set up the Django Environment
import sys
import site
import os
site.addsitedir('~/.virtualenvs/venvdj1.4/local/lib/python2.7/site-packages')

sys.path.append('/srv/www/biobank')

activate_env=os.path.expanduser("~/.virtualenvs/venvdj1.4/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

from django.core.management import setup_environ 
import settings
setup_environ(settings)
import datetime
from django.core.mail import send_mail, EmailMultiAlternatives
from catissue.tissue.models import *
from catissue.tissue.utils import *
from django.template.loader import render_to_string
from django.template.context import RequestContext

def getTransfer():
    try:
        enable_graph()
        disable_graph()
        print '[BBM] Sending mail to operator for transferring aliquots'
        lisaliq=[]
        lisbarc=[]
        lispos=[]
        #prendo tutti i trasferimenti ancora da spedire che abbiano come data di partenza programmata 
        #uguale ad oggi e un operatore che deve eseguirli
        oggi=datetime.datetime.now()
        print 'oggi',oggi
        listransf=Transfer.objects.filter(departureExecuted=0,plannedDepartureDate=oggi,deleteTimestamp=None,deleteOperator=None).exclude(operator=None)
        print 'listransf',listransf
        for trasf in listransf:
            listal=AliquotTransferSchedule.objects.filter(idTransfer=trasf)
            print 'listal',listal
            stringa=''
            for al in listal:
                stringa+=al.idAliquot.uniqueGenealogyID+'&'
            stringtot=stringa[:-1]
            diz=AllAliquotsContainer(stringtot)
                 
            for gen in diz:
                lista=diz[gen]
                for val in lista:
                    ch=val.split('|')
                    lisaliq.append(ch[0])
                    lisbarc.append(ch[1])
                    lispos.append(ch[2])
                    
            #prendo gli altri valori dal primo oggetto in lista, tanto sono uguali anche per tutti gli altri campioni
            esec=listal[0].idTransfer.operator
            data=listal[0].idTransfer.plannedDepartureDate
            addr=listal[0].idTransfer.addressTo
            assigner=listal[0].idTransfer.idTransferSchedule.operator
            #mando l'e-mail all'esecutore per dirgli che deve trasferire quei campioni
            file_data = render_to_string('tissue2/transfer/report_transfer.html', {'mail':True,'listafin':zip(lisaliq,lisbarc,lispos),'assigner':assigner,'data':data,'addr':addr})
            operator = User.objects.get(id = esec.id)
            mailOperator = operator.email
            subject, from_email = 'Scheduled transfer aliquots', settings.EMAIL_HOST_USER
            text_content = 'This is an important message.'
            html_content = file_data
            msg = EmailMultiAlternatives(subject, text_content, from_email, [mailOperator])
            msg.attach_alternative(html_content, "text/html")
            print 'msg',msg
            msg.send()
    except Exception,e:
        print 'err',e
    return
if __name__=='__main__':
    getTransfer()
    
