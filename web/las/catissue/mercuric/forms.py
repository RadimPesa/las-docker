import re,urllib2,json
from django import forms
from django.contrib.auth.models import User
from catissue.tissue.models import *
from django.contrib.admin import widgets
from time import strptime, strftime
from datetime import date
from urllib2 import HTTPError

#serve per passare al form delle collezioni la lista degli ospedali presi dal modulo clinico
def carica_posti_collez(tipo):
    try:
        #prot e' l'id. Devo passare alla API del modulo clinico il nome interno
        protocollo=CollectionProtocol.objects.get(project=tipo)
        #devo fare la chiamata al modulo clinico per avere la lista degli ospedali
        servizio=WebService.objects.get(name='Clinical')
        urlclin=Urls.objects.get(idWebService=servizio).url
        #faccio la get al modulo dandogli la lista con dentro i dizionari
        indir=urlclin+'/coreInstitution/api/institution/'+protocollo.project
        print 'indir',indir
        lisfin=[('','---------')]
        try:
            req = urllib2.Request(indir, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
        except HTTPError,e:
            print 'code',e.code
            if e.code == 409:   
                return lisfin
            
        lista = json.loads(u.read())
        print 'lista',lista
        #qui ho la lista di dizionari che rappresentano ciascuno un posto ed hanno delle chiavi
        #con le varie informazioni
        #lista=[{'identifier':'AA','name':'Istituto di Candiolo'}]
        
        lissource=Source.objects.filter(type__startswith=protocollo.project)
        for val in lista:
            nomeesteso=val['name']
            nomeinterno=val['identifier']
            #grazie al nome interno vado a prendere il valore dell'id dalla mia tabella
            for s in lissource:
                if s.internalName==nomeinterno:
                    lisfin.append([str(s.id),nomeesteso])
        print 'lisfin',lisfin
        return lisfin
    except Exception,e:
        print 'err',e
        return []



class CollectionMercForm(forms.Form):  
    def __init__(self, *args, **kwargs):
        super(CollectionMercForm, self).__init__(*args, **kwargs)
        
        lisposti=carica_posti_collez('Mercuric')
        self.fields['Place'] = forms.ChoiceField(label='Site',choices=lisposti)
        self.fields['date']=forms.CharField()
        self.fields['patient']=forms.CharField(label='Patient code', max_length=30,required=False)
        self.fields['barcode']=forms.CharField(label='Tube barcode',max_length=30)
        self.fields['volume']=forms.CharField(label='Volume (ml)',max_length=30)
