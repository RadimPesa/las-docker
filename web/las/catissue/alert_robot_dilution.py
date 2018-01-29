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
from django.contrib.sites.models import Site

#per prendere tutte le pianificazioni delle diluizioni o delle quantificazioni gia' eseguite dal robot, ma non ancora salvate nel LAS.
#Avverte l'utente che deve andare nell'apposita schermata e confermare
def getPlan():
    try:
        enable_graph()
        disable_graph()
        print '[BBM] Sending mail to operator for robot procedure'        
        lisaliqsched=[]
        indirizzo=Site.objects.get(name='LASDomain')
        print 'indir',indirizzo
        url=indirizzo.domain
        #prendo tutti i plan del robot legati alla diluizione che non abbiano ancora l'alerted impostato
        adesso=timezone.localtime(timezone.now())
        print 'adesso',adesso
        #passato=adesso-timezone.timedelta(minutes = 120)
        lisprotype=ProtocolTypeHamilton.objects.filter(name='dilution').values_list('id',flat=True)
        lisprot=ProtocolHamilton.objects.filter(protocol_type_id__in=lisprotype).values_list('id',flat=True)
        print 'lisprot',lisprot
        lisplanprot=PlanHasProtocolHamilton.objects.filter(protocol_id__in=lisprot).values_list('plan_id',flat=True)
        lisplanhamiltondil=PlanHamilton.objects.filter(id__in=lisplanprot,executed__isnull=False,processed__isnull=True,alerted__isnull=True)
        print 'lisplanhamiltondilution',lisplanhamiltondil        
        if len(lisplanhamiltondil)!=0:
            lisplanfin=[]
            #chiave l'id e valore il nome del plan
            dizplanname={}
            for p in lisplanhamiltondil:
                lisplanfin.append(p.id)
                dizplanname[p.id]=p.name
            print 'lisplanfin',lisplanfin
            featrobot=FeatureDerivation.objects.get(name='Robot')
            lisprotrobot=FeatureDerProtocol.objects.filter(idFeatureDerivation=featrobot).values_list('idDerProtocol',flat=True)
            lisaliqsched=AliquotDerivationSchedule.objects.filter(Q(idPlanDilution__in=lisplanfin)&~Q(idDerivationProtocol=None)&Q(idDerivationProtocol__in=lisprotrobot)&Q(derivationExecuted=1)&Q(deleteTimestamp=None)).order_by('validationTimestamp')
            print 'lisaliqdersched',lisaliqsched
            urlval=url+'/biobank/derived/robot/createderivatives/'
            send_mail(lisaliqsched,'derive',urlval,'dilution',[],dizplanname)                
                
            #se non ho derivazioni collegate a quel piano vuol dire che quel piano e' collegato ad uno split
            lisaliqsched=AliquotSplitSchedule.objects.filter(idPlanRobot__in=lisplanfin).order_by('validationTimestamp')
            urlval=url+'/biobank/split/robot/savedata/'
            print 'lisaliqsplitsched',lisaliqsched
            lissample=SampleHamilton.objects.filter(plan_id__in=lisplanfin).values_list('genid',flat=True)
            print 'lissample',lissample
            lisfallitesplit=[]
            for alsched in lisaliqsched:
                gen=alsched.idAliquot.uniqueGenealogyID
                if gen not in lissample:
                    lisfallitesplit.append(alsched.id)
            send_mail(lisaliqsched,'split',urlval,'dilution',lisfallitesplit,dizplanname)
                
                
            for plan in lisplanhamiltondil:
                plan.alerted=adesso
                plan.save()
                
        #guardo i piani per la quantificazione
        lisprotype=ProtocolTypeHamilton.objects.filter(name__in=['fluo','uv']).values_list('id',flat=True)
        lisprot=ProtocolHamilton.objects.filter(protocol_type_id__in=lisprotype).values_list('id',flat=True)
        print 'lisprot',lisprot
        lisplanprot=PlanHasProtocolHamilton.objects.filter(protocol_id__in=lisprot).values_list('plan_id',flat=True)
        #qui prendo anche i piani di quantificazioni a fini di derivazione, ma tanto dopo quando filtro su alqualsched avro' una lista vuota
        #e non trovero' nessuna procedura, come e' giusto che sia 
        lisplanhamiltonquant=PlanHamilton.objects.filter(id__in=lisplanprot,executed__isnull=False,processed__isnull=True,alerted__isnull=True)
        print 'lisplanhamiltonquant',lisplanhamiltonquant        
        if len(lisplanhamiltonquant)!=0:
            lisplanfin=[]
            #chiave l'id e valore il nome del plan
            dizplanname={}
            for p in lisplanhamiltonquant:
                lisplanfin.append(p.id)
                dizplanname[p.id]=p.name
            print 'lisplanfin',lisplanfin
            lisaliqsched=AliquotQualitySchedule.objects.filter(idPlanRobot__in=lisplanfin).order_by('validationTimestamp')
            urlval=url+'/biobank/revalue/robot/savedata/'
            print 'lisqualsched',lisaliqsched
            send_mail(lisaliqsched,'revalue',urlval,'quantification',[],dizplanname)
            
            for plan in lisplanhamiltonquant:
                plan.alerted=adesso
                plan.save()

    except Exception,e:
        print 'err',e
    return

def send_mail(lisaliqsched,tipoplan,url,action,lisfallitesplit,dizplanname):
    try:
        if len(lisaliqsched)!=0:
            stringat=''
            for alsched in lisaliqsched:
                stringat+=alsched.idAliquot.uniqueGenealogyID+'&'
            stringtotale=stringat[:-1]
            dizpos=AllAliquotsContainer(stringtotale)
            lisaliq=[]
            lisbarc=[]
            lispos=[]
            lisname=[]
            #chiave il nome utente e valore la lista di aliqsched
            dizutenti={}
            for alsched in lisaliqsched:
                operatore=alsched.operator
                if tipoplan=='split' or tipoplan=='revalue':
                    operatore=alsched.operator.username
                #operatore e' l'username    
                if operatore in dizutenti:
                    listemp=dizutenti[operatore]
                else:
                    listemp=[]
                listemp.append(alsched)
                dizutenti[operatore]=listemp
            print 'dizutenti',dizutenti
            for k,lisalsched in dizutenti.items():
                for alsched in lisalsched:
                    listatemp=dizpos[alsched.idAliquot.uniqueGenealogyID]
                    fallito=False
                    plan=alsched.idPlanRobot
                    if tipoplan=='derive':
                        plan=alsched.idPlanDilution
                        if alsched.failed==1:
                            fallito=True
                    if tipoplan=='split':
                        if alsched.id in lisfallitesplit:
                            fallito=True
                    #invece per il revalue non fallisce mai
                    for val in listatemp:
                        ch=val.split('|')
                        lisaliq.append(alsched.idAliquot.uniqueGenealogyID)
                        lisbarc.append(ch[1])
                        lispos.append(ch[2])                        
                        if fallito:
                            lisname.append('Failed')
                        else:
                            lisname.append(dizplanname[plan])
                    #se per caso il campione e' esaurito allora listatemp e' vuota, ma io devo comunque inserire qualcosa nelle liste
                    if len(listatemp)==0:
                        lisaliq.append(alsched.idAliquot.uniqueGenealogyID)
                        lisbarc.append('')
                        lispos.append('')
                        if fallito:
                            lisname.append('Failed')
                        else:
                            lisname.append(dizplanname[plan])
    
                file_data = render_to_string('tissue2/derive_robot/report_dilution.html', {'lista':zip(lisaliq,lisbarc,lispos,lisname),'perc':url,'action':action})
                loperator = User.objects.filter(username = k)
                print 'loperator',loperator
                if len(loperator)!=0:
                    mailOperator = loperator[0].email
                    print 'mail',mailOperator
                    if mailOperator!='':
                        subject, from_email = '[LAS] '+action.capitalize()+' completed', settings.EMAIL_HOST_USER
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
    getPlan()
    
