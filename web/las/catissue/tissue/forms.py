import re,urllib2,json
from django import forms
from django.contrib.auth.models import User
from catissue.tissue.models import *
from django.contrib.admin import widgets
from time import strptime, strftime
from datetime import date
from django.db.models import Q
from urllib2 import HTTPError

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.PasswordInput()
    
class KitTypeForm(forms.Form):
    name=forms.CharField(label='Kit Name',max_length=30)
    producer=forms.CharField(label='Producer',max_length=50)
    capacity=forms.IntegerField(max_value=1000,label='Capacity')
    catalogue=forms.CharField(label='Catalogue Number',max_length=30)
    instruction=forms.FileField(label='Kit instructions',required=False)
    
class SingleKitForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SingleKitForm, self).__init__(*args, **kwargs)
        self.fields['kit_Type']=forms.ModelChoiceField(label='Kit Type',queryset=KitType.objects.all())
        #barcode=forms.CharField(label='kit Barcode',max_length=30)
        self.fields['expiration_Date']=forms.CharField(label='Expiration Date')
        self.fields['lot']=forms.CharField(label='Lot Number',max_length=30)

#ALIQDERIVATE=[(a.id,a.longName) for a in AliquotType.objects.filter(type='Derived')]

class ProtocolForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ProtocolForm, self).__init__(*args, **kwargs)
        ALIQ=[(a.id,a.longName) for a in AliquotType.objects.all().order_by('longName')]
        self.fields['name']=forms.CharField(label='Protocol name',max_length=50)
        self.fields['source']=forms.MultipleChoiceField(label='Source Type (multiple selection is allowed)',choices=ALIQ,widget=forms.SelectMultiple())
        #result=forms.ChoiceField(label='Result',choices=ALIQDERIVATE,widget=forms.Select(),required=False)
        self.fields['result']=forms.ModelChoiceField(label='Derivative',queryset=AliquotType.objects.filter(type='Derived').order_by('longName'))
        self.fields['load_Quantity']=forms.FloatField(label='Input')
        self.fields['unity_measure']=forms.ChoiceField(choices=[(0,'mg'),(1,'ul')],label='',required=False)
        self.fields['max_Volume']=forms.FloatField(label='Max volume (ul)',required=False)
        self.fields['l_quant']=forms.FloatField(label='Reaction volume (ul)',required=False)
        self.fields['exp_Volume']=forms.FloatField(label='Outcome volume (ul)')
        self.fields['num_Aliq']=forms.IntegerField(max_value=50,label='Derived aliquots number (less than 50)')
        self.fields['vol_Aliq']=forms.FloatField(label='Derived aliquots volume (ul)')
        self.fields['conc_Aliq']=forms.FloatField(label='Derived aliquots concentration (ng/ul)')
        self.fields['kit']=forms.ModelChoiceField(queryset=KitType.objects.all().order_by('name'),required=False)
        self.fields['robot']=forms.CharField(label='Is robot used?',widget=forms.CheckboxInput(),required=False)
    
class PlaceForm(forms.Form):
    hospital=forms.CharField(label='Hospital name:', max_length=45)
    address=forms.CharField(label='Address', max_length=45)
    notes=forms.CharField(label='Notes (optional)',max_length=150, required=False)

CHO=[('select1','select 1'),
         ('select2','select 2')]

#serve per passare al form delle collezioni la lista degli ospedali presi dal modulo clinico
def carica_posti_collez(nome):
    try:
        #devo fare la chiamata al modulo clinico per avere la lista degli ospedali
        servizio=WebService.objects.get(name='Clinical')
        urlclin=Urls.objects.get(idWebService=servizio).url
        #faccio la get al modulo dandogli la lista con dentro i dizionari
        indir=urlclin+'/coreInstitution/api/institution/'+nome
        #print 'indir',indir
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
        if nome!='Funnel' and nome!='Mercuric':                
            lissource=Source.objects.filter(type='Hospital')
        else:
            lissource=Source.objects.filter(type__startswith=nome)
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
        return lisfin
    
#serve per passare al form delle collezioni la lista dei protocolli di collezionamento presi dal modulo clinico
def carica_protocolli_collez():
    try:
        #devo fare la chiamata al modulo clinico per avere la lista degli ospedali
        servizio=WebService.objects.get(name='Clinical')
        urlclin=Urls.objects.get(idWebService=servizio).url
        #faccio la get al modulo dandogli la lista con dentro i dizionari
        indir=urlclin+'/coreProject/api/project/'
        print 'indir',indir
    
        req = urllib2.Request(indir, headers={"workingGroups" : get_WG_string()})
        u = urllib2.urlopen(req)
        lista = json.loads(u.read())
        print 'lista',lista
        #qui ho la lista di dizionari che rappresentano ciascuno un protocollo ed hanno delle chiavi
        #con le varie informazioni
        #lista=[{'identifier':'Funnel','name':'Funnel'}]
        lisprot=CollectionProtocol.objects.all().exclude(project='Internal')
        lisfin=[('','---------')]
        for val in lista:
            nomeesteso=val['name']
            nomeinterno=val['identifier']
            #grazie al nome interno vado a prendere il valore dell'id dalla mia tabella
            for s in lisprot:
                if s.project==nomeinterno:
                    lisfin.append([str(s.id),nomeesteso])
        #print 'lisfin',lisfin
        return lisfin
    except Exception,e:
        print 'err',e
        return []

class CollectionForm(forms.Form):  
    def __init__(self, *args, **kwargs):
        super(CollectionForm, self).__init__(*args, **kwargs)
        
        lisprot=carica_protocolli_collez()
        self.fields['Tumor_Type'] = forms.ModelChoiceField(queryset = CollectionType.objects.all().exclude(type='Internal').order_by('longName'))        
        #self.fields['protocol']=forms.ModelChoiceField(label='Study protocol',queryset = CollectionProtocol.objects.all().order_by('name'))
        self.fields['protocol']=forms.ChoiceField(label='Study protocol',choices=lisprot)
        #'initial' per impostare la data di oggi al caricamento della pagina
        self.fields['date']=forms.CharField(label='Date',max_length=10)
        self.fields['barcode']=forms.CharField(label='Informed consent', max_length=30)
        self.fields['patient']=forms.CharField(label='Patient code', max_length=30,required=False)
        #self.fields['Place'] = forms.ModelChoiceField(label='Hospital',queryset = Source.objects.filter(type='Hospital').order_by('name'))
        self.fields['Place'] = forms.CharField(widget=forms.Select(),label='Hospital',required=False)
        self.fields['randomize'] = forms.BooleanField(label='Random code',required=False)
class TissueForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(TissueForm, self).__init__(*args, **kwargs)
        CASI=[(t.id,t.abbreviation) for t in TissueType.objects.all().exclude(type='Internal')]
        self.fields['tissue']=forms.MultipleChoiceField(choices=CASI,label='Tissue collected', required=True,widget=forms.CheckboxSelectMultiple())

#UTENTI=[(t.id,t.first_name+' '+t.last_name) for t in User.objects.filter(~Q(username='admin')&~Q(first_name='')).order_by('last_name')]

class DerivedInit(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DerivedInit, self).__init__(*args, **kwargs)
        UTENTI=[(t.id,t.last_name+' '+t.first_name) for t in User.objects.filter(~Q(username='admin')&~Q(first_name='')).filter(id__in=WG_User.objects.filter(user__is_active=1,WG__name__in=list(get_WG()),permission__codename=get_functionality()).values_list("user",flat=True)).order_by('last_name')]
        aliqderivate=AliquotType.objects.filter(type='Derived').order_by('longName')
        plasma=AliquotType.objects.filter(longName='Plasma')
        pbmc=AliquotType.objects.filter(longName='Viable')
        aliqtot=aliqderivate | plasma | pbmc
        TIPIALIQ=[(a.id,a.longName) for a in aliqtot]
        TIPIALIQ.insert(0,('','---------'))
        self.fields['result']=forms.ChoiceField(choices=TIPIALIQ, label='Result', required=False)
        self.fields['utente']=forms.ChoiceField(choices=UTENTI,label='Assign to',required=False)
        self.fields['notes']=forms.CharField(widget=forms.Textarea(attrs={'rows':5, 'cols':55,'maxlength':150}),label='Description (optional)', required=False)
        self.fields['aliquot']=forms.CharField(label='Genealogy ID or container barcode',required=False,max_length=45)
        #self.fields['file']=forms.FileField(label='Aliquots file',required=False)
    
class RevaluateForm(forms.Form):
    aliquot=forms.CharField(label='Genealogy ID  or tube barcode',required=False,max_length=30)
    file=forms.FileField(label='Aliquots file',required=False)
    
class PositionForm(forms.Form):
    notes=forms.CharField(widget=forms.Textarea(attrs={'rows':5, 'cols':55,'maxlength':150}),label='Description (optional)', required=False)
    aliquot=forms.CharField(label='Genealogy ID or container barcode',required=False,max_length=30)
    #file=forms.FileField(label='Aliquots file',required=False)

T=(
    (0, 'New collection event'),
    (1, 'Assign to existing collection'),
)

class ExternFormInit(forms.Form):
    tipi=forms.ChoiceField(choices=T,label='Choose the action', required=True)

'''VETTORE=[('','---------'),
         ('H','Human'),
         ('X','Xeno'),
         ('S','Spheroid'),
         ('A','Adherent Line'),
         ('O','Organoid')]'''
VETTORE=[(a.abbreviation,a.name) for a in AliquotVector.objects.all()]
VETTORE.insert(0,('','---------'))

class ExternFormExistingCollection(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ExternFormExistingCollection, self).__init__(*args, **kwargs)
        self.fields['Tumor_Type'] = forms.ModelChoiceField(queryset=CollectionType.objects.all().exclude(type='Internal').order_by('longName'))
        #faccio un'interrogazione fittizia in modo che mi dia una selezione vuota che poi riempio con javascript
        self.fields['case'] = forms.ChoiceField(choices=(('','---------'),(' ','')),required=False,label='Case')
        self.fields['date']=forms.CharField(label='Date',max_length=10)
        #self.fields['Hospital']=forms.ModelChoiceField(queryset = Source.objects.filter(type='Hospital'))
        self.fields['Tissue_Type']=forms.ModelChoiceField(queryset=TissueType.objects.all().exclude(type='Internal').order_by('longName'),label='Tissue type')
        self.fields['vector']=forms.ChoiceField(choices=VETTORE,label='Vector',required=False)
        self.fields['lineage']=forms.CharField(label='Lineage',max_length=2,required=False)
        self.fields['passage']=forms.CharField(label='Passage', max_length=2,required=False)
        self.fields['mouse']=forms.CharField(label='Mouse', max_length=3,required=False)
        self.fields['tissueMouse']=forms.ModelChoiceField(queryset=MouseTissueType.objects.all().order_by('longName'),label='Mouse tissue', required=False)
        self.fields['lincell']=forms.CharField(label='Lineage',max_length=2,required=False)
        self.fields['scongcell']=forms.CharField(label='Thawing cycles', max_length=2,required=False)
        self.fields['passagecell']=forms.CharField(label='Passage', max_length=3,required=False)
        self.fields['Aliquot_Type']=forms.ModelChoiceField(queryset=AliquotType.objects.all().order_by('longName'))
        self.fields['Pieces']=forms.IntegerField(max_value=50,label='N. of pieces',required=False)
        self.fields['Barc']=forms.CharField(label='Tube barcode', max_length=45,required=False)
    
class ExternFormNewCollectionPart1(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ExternFormNewCollectionPart1, self).__init__(*args, **kwargs)
        
        lisprot=carica_protocolli_collez()
        self.fields['Tumor_Type'] = forms.ModelChoiceField(queryset=CollectionType.objects.all().exclude(type='Internal').order_by('longName'))
        #self.fields['protocol']=forms.ModelChoiceField(queryset = CollectionProtocol.objects.all().order_by('name'),label='Study protocol')
        self.fields['protocol']=forms.ChoiceField(label='Study protocol',choices=lisprot)
        self.fields['date']=forms.CharField(label='Date',max_length=10)
        self.fields['barcode_Operation']=forms.CharField(label='Informed consent', max_length=45)
        self.fields['patient']=forms.CharField(label='Patient Code', max_length=30,required=False)
        #self.fields['Hospital']=forms.ModelChoiceField(queryset = Source.objects.filter(type='Hospital').order_by('name'))
        self.fields['Hospital'] = forms.CharField(widget=forms.Select(),required=False)        
        self.fields['randomize'] = forms.BooleanField(label='Random Code',required=False)
        
class ExternFormNewCollectionPart2(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ExternFormNewCollectionPart2, self).__init__(*args, **kwargs)
        self.fields['Tissue_Type']=forms.ModelChoiceField(queryset=TissueType.objects.all().exclude(type='Internal').order_by('longName'),label='Tissue type')
        self.fields['vector']= forms.ChoiceField(choices=VETTORE,required=False,label='Vector')
        self.fields['lineage']=forms.CharField(label='Lineage',max_length=2,required=False)
        self.fields['passage']=forms.CharField(label='Passage', max_length=2,required=False)
        self.fields['mouse']=forms.CharField(label='Mouse', max_length=3,required=False)
        self.fields['tissueMouse']=forms.ModelChoiceField(queryset=MouseTissueType.objects.all().order_by('longName'),label='Mouse tissue', required=False)
        self.fields['lincell']=forms.CharField(label='Lineage',max_length=2,required=False)
        self.fields['scongcell']=forms.CharField(label='Thawing cycles', max_length=2,required=False)
        self.fields['passagecell']=forms.CharField(label='Passage', max_length=3,required=False)
        self.fields['Aliquot_Type']=forms.ModelChoiceField(queryset=AliquotType.objects.all().order_by('longName'))
        self.fields['Pieces']=forms.IntegerField(max_value=50,label='N. of pieces',required=False)
        self.fields['Barc']=forms.CharField(label='Tube barcode', max_length=45,required=False) 

class HistoricForm(forms.Form):
    file=forms.FileField(label='File')
    
class VolumeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        UTENTI=[(t.id,t.last_name+' '+t.first_name) for t in User.objects.filter(~Q(username='admin')&~Q(first_name='')).filter(id__in=WG_User.objects.filter(user__is_active=1,WG__name__in=list(get_WG()),permission__codename=get_functionality()).values_list("user",flat=True)).order_by('last_name')]
        super(VolumeForm, self).__init__(*args, **kwargs)  
        self.fields['date']=forms.CharField(label='Date',required=False)
        self.fields['experiment'] = forms.ModelChoiceField(queryset=Experiment.objects.all().order_by('name'), required=False)
        self.fields['utente']=forms.ChoiceField(choices=UTENTI,label='Assign to',required=False)
        self.fields['notes']=forms.CharField(widget=forms.Textarea(attrs={'rows':5, 'cols':30,'maxlength':150}),label='Description (optional)', required=False)
        #self.fields['volu']=forms.FloatField(label='Taken Volume (uL)')
        #self.fields['Aliquot_Exhausted']=forms.BooleanField(required=False)
        
class PatientForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        lisprot=carica_protocolli_collez()
        #self.fields['utente']=forms.ModelChoiceField(queryset=User.objects.filter(~Q(username='admin')&~Q(first_name='')).order_by('last_name'),label='Operator',required=False)
        self.fields['protocol']=forms.ChoiceField(label='Study protocol',choices=lisprot)
        self.fields['place'] = forms.ModelChoiceField(label='Source',queryset = Source.objects.filter(type='Hospital').order_by('name'),required=False)
        self.fields['infconsent']=forms.CharField(label='Informed consent', max_length=30)
        self.fields['coll_type'] = forms.ModelChoiceField(label='Collection type',queryset = CollectionType.objects.all().exclude(type='Internal').order_by('longName'),required=False)
        self.fields['aliq_type']=forms.ModelChoiceField(queryset=AliquotType.objects.all().order_by('longName'),required=False)
        
class PatientForm2(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PatientForm2, self).__init__(*args, **kwargs)
        #self.fields['aliq_type']=forms.ModelChoiceField(queryset=AliquotType.objects.all(),required=False)
        self.fields['tissue_type'] = forms.ModelChoiceField(label='Tissue type',queryset = TissueType.objects.all().exclude(type='Internal').order_by('longName'),required=False)
        self.fields['vector'] = forms.ChoiceField(choices=VETTORE,required=False)

#UTENTI2=[(t.id,t.first_name+' '+t.last_name) for t in User.objects.filter(~Q(username='admin')&~Q(first_name='')).order_by('last_name')]
#UTENTI2.insert(0,('','---------'))
  
class TransferForm1(forms.Form):
    def __init__(self, *args, **kwargs):
        UTENTI=[(t.id,t.last_name+' '+t.first_name) for t in User.objects.filter(~Q(username='admin')&~Q(first_name='')).filter(id__in=WG_User.objects.filter(user__is_active=1,WG__name__in=list(get_WG()),permission__codename=get_functionality()).values_list("user",flat=True)).order_by('last_name')]
        UTENTI2=[(t.id,t.last_name+' '+t.first_name) for t in User.objects.filter(~Q(username='admin')&~Q(first_name='')).filter(id__in=WG_User.objects.filter(user__is_active=1,WG__name__in=list(get_WG()),permission__codename=get_functionality()).values_list("user",flat=True)).order_by('last_name')]
        UTENTI2.insert(0,('','---------'))
        super(TransferForm1, self).__init__(*args, **kwargs)
        self.fields['executor']=forms.ChoiceField(choices=UTENTI2,label='Assign to',required=False)
        self.fields['date']=forms.CharField(label='Planned shipment date (optional)',required=False)
        self.fields['dest']=forms.ChoiceField(choices=UTENTI,label='Address to',required=False)
        self.fields['aliquot']=forms.CharField(label='Genealogy ID or container barcode',required=False,max_length=45)
        #self.fields['file']=forms.FileField(label='Aliquots file',required=False)
        
class CellLineNewCollectionPart1(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CellLineNewCollectionPart1, self).__init__(*args, **kwargs)
        self.fields['Tumor_Type'] = forms.ModelChoiceField(label='Collection type',queryset=CollectionType.objects.all().exclude(type='Internal').order_by('longName'))
        self.fields['name'] = forms.CharField(label='Cell line name:')
        self.fields['date']=forms.CharField(label='Date:')
        self.fields['mta'] = forms.CharField(label='MTA:',required=False)
        self.fields['lot'] = forms.CharField(label='Lot number:',required=False)
        self.fields['randomize'] = forms.BooleanField(label='Random Code',required=False)

class CellLineNewCollectionPart2(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CellLineNewCollectionPart2, self).__init__(*args, **kwargs)
        lissorg=carica_posti_collez('CellLines')
        self.fields['source']=forms.ChoiceField(label='Source',choices=lissorg)
        #self.fields['source']=forms.ModelChoiceField(queryset = Source.objects.filter(type='Hospital').order_by('name'))
        self.fields['Tissue_Type']=forms.ModelChoiceField(queryset=TissueType.objects.all().exclude(type='Internal').order_by('longName'),label='Tissue type')
        self.fields['vector']=forms.ChoiceField(choices=(('-','---------'),('A','Adherent'),('S','Suspension')),label='Vector')
        self.fields['scong']=forms.CharField(label='Thawing cycles', max_length=2)
        self.fields['passage']=forms.CharField(label='Passage', max_length=3)
        self.fields['volume']=forms.CharField(label='Volume (ul)',required=False)
        self.fields['conta']=forms.CharField(label='Count (cell/ml)',required=False)
        self.fields['barc']=forms.CharField(label='Tube barcode', max_length=45,required=False)      

class SlideInsertForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SlideInsertForm, self).__init__(*args, **kwargs)
        UTENTI=[(t.id,t.last_name+' '+t.first_name) for t in User.objects.filter(~Q(username='admin')&~Q(first_name='')).filter(id__in=WG_User.objects.filter(user__is_active=1,WG__name__in=list(get_WG()),permission__codename=get_functionality()).values_list("user",flat=True)).order_by('last_name')]
        print UTENTI
        #UTENTI=[(t.id,t.first_name+' '+t.last_name) for t in User.objects.filter(~Q(username='admin')&~Q(first_name='')).order_by('last_name')]
        self.fields['utente']=forms.ChoiceField(choices=UTENTI,label='Assign to',required=False)        
        self.fields['notes']=forms.CharField(widget=forms.Textarea(attrs={'rows':5, 'cols':55,'maxlength':150}),label='Description (optional)', required=False)
        self.fields['aliquot']=forms.CharField(label='Genealogy ID or container barcode',required=False,max_length=45)
 
opz=(
    (0, 'Fresh tissue'),
    (1, 'Archive samples'),
)

class BatchFormInit(forms.Form):
    tipi=forms.ChoiceField(choices=opz,label='Choose the action', required=True)

class MarkerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(MarkerForm, self).__init__(*args, **kwargs)
        #self.fields['Marker_Type']=forms.ModelChoiceField(queryset=LabelFeature.objects.filter(type='Marker').order_by('name'),label='Marker type')
        #self.fields['name']=forms.CharField(label='Marker Name',max_length=30)
        self.fields['producer']=forms.CharField(label='Producer',max_length=30, required=False)
        self.fields['catalogue']=forms.CharField(label='Catalogue Number',max_length=30, required=False)
        self.fields['dilution']=forms.CharField(label='Dilution factor',max_length=10, required=False)
        self.fields['time']=forms.CharField(label='Time',max_length=30, required=False)
        self.fields['temperature']=forms.CharField(label='Temperature',max_length=30, required=False)
