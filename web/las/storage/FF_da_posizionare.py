#!/usr/bin/python
# Set up the Django Environment
import sys
sys.path.append('/srv/www/storage')
from django.core.management import setup_environ 
import settings,os
setup_environ(settings)
import datetime,urllib2,json
from django.core.mail import send_mail, EmailMultiAlternatives
from archive.models import *
from django.template.loader import render_to_string
from django.template.context import RequestContext
from dateutil.relativedelta import *
from django.contrib.sites.models import Site
from global_request_middleware import *

def ContainerFF():
    try:
        diz={}
        tipocont=ContainerType.objects.get(name='FF')
        listafin=Container.objects.filter(idContainerType=tipocont,idFatherContainer=None,present=1)
        print 'lung',len(listafin)
        #ho la lista dei container e adesso ho bisogno di avere il genid del campione
        #contenuto
        barc=''
        lis_pezzi_url=[]
        lis_gen=[]
        for bloc in listafin:
            barc+=bloc.barcode+'&&,'
            #2000 e' il numero di caratteri scelto per fare in modo che la url
            #della api non sia troppo lunga
            if len(barc)>2000:
                #cancello la virgola alla fine della stringa
                lu=len(barc)-1
                strbarc=barc[:lu]
                print 'strbarc',strbarc
                
                lis_pezzi_url.append(strbarc)
                barc=''
        #cancello la virgola alla fine della stringa
        lu=len(barc)-1
        strbarc=barc[:lu]
        print 'strbarc',strbarc
        if strbarc!='':
            lis_pezzi_url.append(strbarc)
        print 'lis pezzi url',lis_pezzi_url
        print 'len',len(lis_pezzi_url)
        if len(lis_pezzi_url)!=0:
            indir=Urls.objects.get(default=1).url
            #print 'indir',indir
            for elementi in lis_pezzi_url:
                elementi=elementi.replace('#','%23')
                print 'elementi',elementi
                req = urllib2.Request(indir+"/api/tubes/"+elementi, headers={"workingGroups" : 'admin'})
                u = urllib2.urlopen(req)
                #u = urllib2.urlopen(indir+"/api/tubes/"+elementi+ "?workingGroups="+get_WG_string())
                #in data ho i genid di tutti i blocchi di quel cassetto
                data = json.loads(u.read())
                print 'data',data
                for pezzi in data['data']:
                    lis_gen.append(pezzi)
            print 'lis_gen',lis_gen
            stringa='Genealogy id\tBarcode\tOperator\tCreation date\n'
            for elem in lis_gen:
                val=elem.split(',')
                #in val[0] ho il barcode del blocchetto, in val[3] ho il genid
                if len(val)==7:
                    print 'gen',val[3]
                    #se non c'e' il gen vuol dire che il blocchetto e' ancora vuoto
                    diz[val[3]]=val[0]
                    stringa+=val[3]+'\t'+val[0]+'\t'+val[5]+'\t'+val[6]+'\n'
        print 'stringa',stringa
        f2=open(os.path.join(os.path.dirname(__file__),'archive_media/Historical/FF_to_position.csv'),'w')
        f2.write(stringa)
        f2.close()
    except Exception,e:
        print 'err',e
    return

if __name__=='__main__':
    ContainerFF()
    