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
from catissue.tissue.genealogyID import *
from django.contrib.sites.models import Site

#Analizza tutte le vitali con vettore diverso da H o X ancora disponibili nel LAS e va a prendere quelle che hanno genid uguale al barcode, che sono
#quelle create per gli esperimenti dal modulo delle linee. Avverte l'utente che quei campioni sono ancora disponibili nel LAS.
def getCellLine():
    try:
        enable_graph()
        disable_graph()
        print '[BBM] Sending mail to operator for temporary frozen cell lines still available'    
        
        indirizzo=Site.objects.get(name='LASDomain')
        print 'indir',indirizzo
        url=indirizzo.domain
        url+='/biobank/revalue/insert/'
        print 'url',url
        
        oggi=timezone.localtime(timezone.now())
        print 'oggi',oggi
        #prendo i campioni creati da almeno 25 giorni
        passato=oggi-timezone.timedelta(days = 25)
        datapassato=datetime.date(passato.year,passato.month,passato.day)
        #prendo le aliquote vitali ancora disponibili che non siano X o H
        viable=AliquotType.objects.get(abbreviation='VT')
        lisal=Aliquot.objects.filter(idAliquotType=viable,availability=1, timesUsed=0)
        print 'len(lisal)',len(lisal)
        stringat=''        
        for al in lisal:
            gen=GenealogyID(al.uniqueGenealogyID)
            vettore=gen.getSampleVector()
            operatore=al.idSamplingEvent.idSerie.operator
            data=al.idSamplingEvent.samplingDate
            #tolgo la Cancelliere perche' non e' interessata
            if (vettore=='A' or vettore=='S' or vettore=='O') and (operatore!='carlotta.cancelliere') and (data<datapassato):
                stringat+=gen.getGenID()+'&'
        stringtotale=stringat[:-1]
        #stringtotale='CRC1239LMO0B03006001VT0700&CRC1344LMO0A03007001VT0100&CRC0327LMO0B01003001VT0700&CRC1336LMO0A01004001VT0200&CRC0152LMO0C01003001VT1000'
        dizgen=AllAliquotsContainer(stringtotale)
        print 'dizgen',dizgen
        #chiave il nome utente e valore la lista di campioni con anche la posizione
        dizutenti={}
        lgen=''
        lis_pezzi_url=[]
        diznick={}
        listagentot=[]
        for al in lisal:
            gen=al.uniqueGenealogyID
            if gen in dizgen:
                listatemp=dizgen[gen]
                for val in listatemp:
                    ch=val.split('|')
                    barc=ch[1]
                    pos=ch[2]                
                    #e' un campione da prendere
                    if barc.strip()==gen.strip():
                        operatore=al.idSamplingEvent.idSerie.operator
                        if operatore in dizutenti:
                            listemp=dizutenti[operatore]
                        else:
                            listemp=[]                        
                        listemp.append({'genealogy':gen,'barcode':barc,'pos':pos,'data':str(al.idSamplingEvent.samplingDate)})
                        dizutenti[operatore]=listemp
                        listagentot.append(gen)
                        lgen+=gen+'&'
                        if len(lgen)>2000:
                        #cancello la & alla fine della stringa
                            lis_pezzi_url.append(lgen[:-1])
                            lgen=''
        print 'dizutenti prima',dizutenti
        strgen=lgen[:-1]
        print 'strgen',strgen
        if strgen!='':
            lis_pezzi_url.append(strgen)                
        if len(lis_pezzi_url)!=0:
            #celllinethawing o celllinegeneration e' lo stesso, mi da' sempre la stessa url
            webserv=WebService.objects.get(name='CellLineThawing')
            indir=Urls.objects.get(idWebService=webserv).url
            for elementi in lis_pezzi_url:                
                req = urllib2.Request(indir+"/api/getNickName/"+elementi, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                data = u.read()
                diz=json.loads(data)['data']
                print 'diz',diz
                if diz=='errore':
                    raise Exception
                diznick = dict(diznick.items() + diz.items())
        print 'diznick',diznick
        #vado a vedere le procedure in cui sono stati coinvolti quei campioni
        val1={'lista':json.dumps(listagentot)}
        data = urllib.urlencode(val1)
        indir=settings.DOMAIN_URL+'/biobank'
        req = urllib2.Request(indir+"/api/return/container/",data=data, headers={"workingGroups" : 'admin'})
        u = urllib2.urlopen(req)
        #chiave il gen e val la procedura e la data
        dizproc =  json.loads(json.loads(u.read())['data'])
        print 'dizproc',dizproc
        #scandisco dizutenti per aggiungere la info del nickname e dell'ultima eventuale procedura che ha subito il campione        
        for k,lisdati in dizutenti.items():
            print 'lisdati',lisdati
            lisfinale=[]
            for diz in lisdati:
                print 'diz',diz
                gen=diz['genealogy']
                nick=''
                if gen in diznick:
                    nick=diznick[gen]
                proc=''
                data=''
                procplan=''
                if gen in dizproc:
                    proc=dizproc[gen]['procedure']
                    data=dizproc[gen]['data']                    
                    procplan=dizproc[gen]['procplan']                        
                diz['nick']=nick
                diz['proc']=proc
                diz['dataproc']=data
                #se vedo che procplan non e' null vuol dire che il campione e' stato pianificato per una qualche procedura e allora
                #non ha senso che lo faccia comparire nell'email
                print 'procplan',procplan
                if procplan=='':
                    lisfinale.append(diz)
            dizutenti[k]=lisfinale
        print 'dizutenti dopo',dizutenti
        #scandisco di nuovo il dizionario utenti per cancellare le liste che a seguito dell'eventuale cancellazione di prima risultano vuote 
        for k,lisdati in dizutenti.items():
            print 'len lisdati',len(lisdati)
            if len(lisdati)==0:
                del dizutenti[k]
                
        leto=User.objects.get(username='Simonetta')
        for k,lisdati in dizutenti.items():
            file_data = render_to_string('tissue2/report_cell_line.html', {'lista':lisdati,'perc':url})
            loperator = User.objects.filter(username = k)
            print 'loperator',loperator
            if len(loperator)!=0:
                mailOperator = loperator[0].email
                print 'mail',mailOperator
                if mailOperator!='':
                    subject, from_email = '[LAS] Cell lines still available - '+loperator[0].username, settings.EMAIL_HOST_USER
                    text_content = 'This is an important message.'
                    html_content = file_data
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [mailOperator,leto.email])
                    msg.attach_alternative(html_content, "text/html")
                    print 'msg',msg
                    msg.send()
    except Exception,e:
        print 'err',e
    return
if __name__=='__main__':
    getCellLine()
    
