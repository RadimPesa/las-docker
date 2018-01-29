#!/usr/bin/python
# Set up the Django Enviroment
import sys
import site
import os
site.addsitedir('~/.virtualenvs/venvdj1.4/local/lib/python2.7/site-packages')

sys.path.append('/srv/www/caxeno')
activate_env=os.path.expanduser("~/.virtualenvs/venvdj1.4/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

from django.core.management import setup_environ 
import settings 
setup_environ(settings)
from django.db import transaction
import os, urllib, urllib2, cStringIO, string, json
from xenopatients.models import *
#from datetime import date, timedelta
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.http import *
from django.contrib.sessions.middleware import *
from django.contrib.auth.middleware import *
from django.core.mail import send_mail, EmailMultiAlternatives
from global_request_middleware import *

from django.utils import timezone

@transaction.commit_manually
def checkDate():
    enable_graph()
    disable_graph()
    try:
        print 'xeno: start script end treatment'
        print timezone.localtime(timezone.now())
        mailDict = {}
        mha = Mice_has_arms.objects.filter(start_date__isnull = False, end_date__isnull = True)
        startInterval = timezone.localtime(timezone.now()) - timezone.timedelta(minutes = 15)
        force = []
        indexOperators = []
        i = 0
        for m in mha:
            #se la data finale programmata e' compresa nell'ultimo intervallo di scheduling
            #if m.expected_end_date > startInterval and m.expected_end_date <= datetime.datetime.now():
            if m.expected_end_date <= timezone.localtime(timezone.now()):
                print 'stopping one'
                nameT = m.id_protocols_has_arms.id_protocol.name + ' --- ' + m.id_protocols_has_arms.id_arm.name
                operator = m.id_operator
                idGen = m.id_mouse.id_genealogy
                m.end_date = m.expected_end_date
                m.save()
                
                
                operators = []
                quant = Quantitative_measure.objects.filter(id_mouse = m.id_mouse)
                qual = Qualitative_measure.objects.filter(id_mouse = m.id_mouse)
                string = "" 
                if len(quant) > 0:
                    for q in quant:
                        operator = q.id_series.id_operator
                        if operator.email not in operators:
                            operators.append(operator.email)
                    for o in operators:
                        if string == "":
                            string = o
                        else:
                            string = string + '|' + o

                if len(qual) > 0:
                    for q in qual:
                        operator = q.id_series.id_operator
                        if operator.email not in operators:
                            operators.append(operator.email)
                    for o in operators:
                        if string == "":
                            string = o
                        else:
                            string = string + '|' + o
                indexOperators.append(string)
                
                
                if string in mailDict.keys():
                    mailDict[string].append(nameT+'|'+ idGen)
                else:
                    mailDict.update({string:[nameT+'|'+ idGen]})
                i = i + 1
                #se e' acuto ------> espianto!!!
                treatment = Arms.objects.get(pk = m.id_protocols_has_arms.id_arm.id)
                print treatment.forces_explant
                if treatment.forces_explant:
                    force.append(m.id_mouse.id_genealogy)
                    print 'forces explant'
                    mouse = m.id_mouse
                    mouse.id_status = Status.objects.get(name = "ready for explant")
                    try: #se esiste gia', la sovrascrivo
                        print 'try'
                        pe = Programmed_explant.objects.filter(id_mouse = mouse, done=0)[0] #qui va nella except se non esiste un programmed_explant non fatto per quel topo
                        pe.id_scope = Scope_details.objects.get(description = "Archive (end of experiment)")
                        pe.scopeNotes = scopeNotes = "end of acute arm"
                    except: #altrimenti la creo
                        print 'exc'
                        #print mouse.barcode
                        pe = Programmed_explant(id_scope = Scope_details.objects.get(description = "Archive (end of experiment)"), id_mouse = mouse, scopeNotes = "end of acute arm")
                        pass
                    m.save()
                    pe.save()
        try:
            for k in mailDict.keys():
                text_content = 'The following treatment(s) has/have been automatically stopped, because they reached the expected end date:'
                #operator = k
                #mailOperator = operator.email
                index = k
                subject, from_email = 'Finished treatment(s)', settings.EMAIL_HOST_USER
                for t in mailDict[k]:
                    data = t.split('|')
                    print data
                    if data[1] in force:
                        text_content = text_content + '\n' + data[0] + ' on mouse ' + data[1] + ' (forced explant, to be explanted)'
                    else:
                        text_content = text_content + '\n' + data[0] + ' on mouse ' + data[1]
                mails = []
                for o in k.split('|'):
                    u = User.objects.get(email = o)
                    wg = WG.objects.get(id= WG_User.objects.filter(user=u).values_list('WG', flat=True).distinct()[0])
                    mailSupervisor = wg.owner.email
                    mails.append(mailSupervisor)
                    mails.append(o)
                mails = sorted(set(mails))

                msg = EmailMultiAlternatives(subject, text_content, from_email, list(mails))
                msg.send()
                print 'send'
        except Exception, e:
            print e
            print 'xeno: error mail'
            pass
        transaction.commit()
        print 'xeno script: all ok'
    except Exception,e:
        print 'error'
        print e
        transaction.rollback()
    return
if __name__=='__main__':
    checkDate()
