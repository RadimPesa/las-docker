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
from catissue.tissue.models import *
import json,urllib,urllib2
from django.utils import timezone

def shareAliquots():
    try:
        enable_graph()
        disable_graph()
        print '[BBM] Share aliquots to Marsoni_WG'
        oggi=timezone.localtime(timezone.now())
        print 'oggi',oggi
        wgmarsoni=WG.objects.get(name='Marsoni_WG')
        url = Urls.objects.get(idWebService=WebService.objects.get(name='LASAuthServer')).url + "/shareEntities/"
        print 'urlLASAUTH',url
        marsoni=PrincipalInvestigator.objects.get(name='Silvia',surname='Marsoni')
        lprot=CollectionProtocolInvestigator.objects.filter(idPrincipalInvestigator=marsoni).values_list('idCollectionProtocol',flat=True)
        lcoll=Collection.objects.filter(idCollectionProtocol__in=lprot).values_list('id',flat=True)
        lsample=SamplingEvent.objects.filter(idCollection__in=lcoll).values_list('id',flat=True)
        #prendo tutte le aliquote dei protocolli controllati dalla Marsoni
        laliq=Aliquot.objects.filter(idSamplingEvent__in=lsample).values_list('id',flat=True)
        print 'len aliq',len(laliq)
        #prendo tutte le aliquote gia' condivise con la Marsoni
        lalwg=Aliquot_WG.objects.filter(WG_id=wgmarsoni).values_list('aliquot',flat=True)
        print 'len alwg',len(lalwg)
        lal2=list(set(laliq)-set(lalwg))
        #ottengo solo le aliquote non ancora condivise con la Marsoni
        lalfin=Aliquot.objects.filter(id__in=lal2).values_list('uniqueGenealogyID',flat=True)
        print 'lis da condividere',lalfin
        print 'len lis da condividere',len(lalfin)

        if len(lalfin)!=0:
            listot=[]
            for a in lalfin:
                listot.append(a)
                
            data={'entitiesList':json.dumps(listot),'user':'silvia.marsoni'}
            data = urllib.urlencode(data)
            req = urllib2.Request(url,data=data)
            u = urllib2.urlopen(req)
            
            res =  u.read()
            print 'res',res
        
        print '[BBM] Share aliquots to QCInspector_WG'
        wginspector=WG.objects.get(name='QCInspector_WG')
        wgbertotti=WG.objects.get(name='Bertotti_WG')
        #prendo le aliquote di Bertotti
        lalbertotti=Aliquot_WG.objects.filter(WG_id=wgbertotti).values_list('aliquot',flat=True)
        #prendo le aliquote del qcinspector
        lalinsp=Aliquot_WG.objects.filter(WG_id=wginspector).values_list('aliquot',flat=True)
        lal2=list(set(lalbertotti)-set(lalinsp))
        #ottengo solo le aliquote non ancora condivise con il qcinspector
        lalfin=Aliquot.objects.filter(id__in=lal2).values_list('uniqueGenealogyID',flat=True)
        print 'lis da condividere qci',lalfin
        print 'len lis da condividere qci',len(lalfin)
        
        if len(lalfin)!=0:
            listot=[]
            for a in lalfin:
                listot.append(a)
            data={'entitiesList':json.dumps(listot),'user':'QCInspector'}
            data = urllib.urlencode(data)
            req = urllib2.Request(url,data=data)
            u = urllib2.urlopen(req)
            
            res =  u.read()
            print 'res qci',res
    except Exception,e:
        print 'err',e
    return
if __name__=='__main__':
    shareAliquots()
    
