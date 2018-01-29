from django import forms
from time import strptime, strftime
from django.forms import fields
from archive.models import *
from django.db.models import Q
from django.utils.safestring import mark_safe
import operator


class InputFile(forms.Form):
    file_plate = forms.FileField(label='Plate file',required = True)
    type_plate = forms.CharField(max_length = 2)
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.PasswordInput()

#per selezionare i freezer
def SelectFreezer():
    argument_list=[]
    c=[]
    freezer=GenericContainerType.objects.get(abbreviation='freezer')
    lista=ContainerType.objects.filter(idGenericContainerType=freezer)
    for l in lista:
        argument_list.append( Q(**{'idContainerType': l} ))
    if len(argument_list)!=0:
        c=Container.objects.filter(Q(reduce(operator.or_, argument_list)))
    return c

#per selezionare i tipi di aliquote
def SelectAliquot():
    ali=Feature.objects.get(name='AliquotType')
    listaval=FeatureDefaultValue.objects.filter(idFeature=ali).order_by('idDefaultValue__longName')
    return listaval

#per selezionare i tipi di scopi delle piastre
def SelectPlate():
    ali=Feature.objects.get(name='PlateAim')
    listaval=FeatureDefaultValue.objects.filter(idFeature=ali)
    for l in listaval:
        if l.idDefaultValue.longName=='Operative':
            l.idDefaultValue.longName='Working'
        if l.idDefaultValue.longName=='Stored':
            l.idDefaultValue.longName='Archive'
    return listaval

#per selezionare solo i tipi di container di tipologia 'piastra/box'
def SelectContType():
    tip_pias=GenericContainerType.objects.get(abbreviation='plate')
    lista_cont_type=ContainerType.objects.filter(idGenericContainerType=tip_pias).order_by('actualName')
    return lista_cont_type
   
class PlateInsertForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PlateInsertForm, self).__init__(*args, **kwargs)
        CASI_containerType=[(t.id,t.actualName) for t in SelectContType()]
        CASI_Frezeer=[(t.id,t.barcode) for t in SelectFreezer()]
        CASI_aliq=[(t.idDefaultValue.id,t.idDefaultValue.longName) for t in SelectAliquot()]
        CASI_piastra=[(t.idDefaultValue.id,t.idDefaultValue.longName) for t in SelectPlate()]
        self.fields['aim']=forms.ChoiceField(choices=CASI_piastra,label='Plate aim')
        self.fields['file_plate']=forms.FileField(label='Plate file',required=False)
        self.fields['barcode']=forms.CharField(label='Plate Barcode',max_length=20,required=False)
        self.fields['Aliquot_Type']=forms.ChoiceField(choices=CASI_aliq,label='Aliquot Type', required=True)
        self.fields['cont_tipo']=forms.ChoiceField(label='Container Type',choices=CASI_containerType)
        self.fields['geometry']=forms.ModelChoiceField(label='Geometry',queryset = Geometry.objects.all().order_by('name'))
        self.fields['storage']=forms.ChoiceField(choices=CASI_Frezeer,label='Freezer',required=False)
        self.fields['rack']=forms.CharField(label='Rack',required=False,max_length=30)
        self.fields['position']=forms.CharField(label='Position',required=False,max_length=8)

class PlateChangeForm(forms.Form):
    barcode=forms.CharField(label='Plate Barcode',max_length=30)

class PlateChangeForm2(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PlateChangeForm2, self).__init__(*args, **kwargs)
        CASI_Frezeer=[(t.id,t.barcode) for t in SelectFreezer()]
        CASI_aliq=[(t.idDefaultValue.id,t.idDefaultValue.longName) for t in SelectAliquot()]
        CASI_piastra=[(t.idDefaultValue.id,t.idDefaultValue.longName) for t in SelectPlate()]
        self.fields['aim']=forms.ChoiceField(choices=CASI_piastra,label='Plate aim')
        self.fields['Aliquot_Type']=forms.ChoiceField(choices=CASI_aliq,label='Aliquot Type')
        self.fields['storage']=forms.ChoiceField(choices=CASI_Frezeer,label='Freeezer',required=False)
        self.fields['rack']=forms.CharField(label='Rack',required=False,max_length=30)
        self.fields['position']=forms.CharField(label='Position',required=False,max_length=8)
    
TIPI=(
    ('0', 'Within one container'),
    ('1', 'Among more containers')
)

TIPIARCHIVI=(
            ('0','Archive content (aliquot)'),
            ('1','Archive (structured) container'),
            ('2','Archive free containers')
)

class StoreForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StoreForm, self).__init__(*args, **kwargs)
        self.fields['tipi']=forms.ChoiceField(choices=TIPIARCHIVI,label='Choose operation you want to perform', required=True)

class MoveForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(MoveForm, self).__init__(*args, **kwargs)
        CASI_cont=[(t.id,t.name) for t in GenericContainerType.objects.filter(~Q(abbreviation='freezer')&~Q(abbreviation='cellplate'))]
        self.fields['tipi']=forms.ChoiceField(choices=TIPI,label='Choose how you want to move the containers', required=True)
        self.fields['generic']=forms.ChoiceField(choices=CASI_cont, label='Choose container type', required=True)
        #self.fields['aliquote']=forms.ChoiceField(choices=CASI_aliq,label='Choose aliquot type', required=True)

class ContainerTypeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ContainerTypeForm, self).__init__(*args, **kwargs)
        self.fields['name']=forms.CharField(label='Name',max_length=50)
        self.fields['catalog']=forms.CharField(label='Catalogue Number',max_length=50,required=False)
        self.fields['producer']=forms.CharField(label='Producer',max_length=50,required=False)
        #self.fields['lot']=forms.CharField(label='Lot Number',max_length=50,required=False)
        #self.fields['file']=forms.FileField(label='File',required=False)
        #self.fields['geometry']=forms.ModelChoiceField(label='Geometry',queryset = Geometry.objects.all().order_by('name'))
        self.fields['generic']=forms.ModelChoiceField(label='Generic type',queryset = GenericContainerType.objects.all().exclude(abbreviation='cellplate'))
        #self.fields['root'] = forms.BooleanField(label='Is root',required=False)
        #self.fields['multiple'] = forms.BooleanField(label='Can have container in same position',required=False)

class ContainerTypeForm2(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ContainerTypeForm2, self).__init__(*args, **kwargs)
        TIPI_CONT=[(a.id,a.actualName) for a in ContainerType.objects.all().order_by('actualName')]                
        self.fields['contpadri']=forms.MultipleChoiceField(label='Father container (multiple selection is allowed)',choices=TIPI_CONT,widget=forms.SelectMultiple(),required=False)
        self.fields['contfigli']=forms.MultipleChoiceField(label='Child container (multiple selection is allowed)',choices=TIPI_CONT,widget=forms.SelectMultiple(),required=False)
    
class NewContainerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(NewContainerForm, self).__init__(*args, **kwargs)
        CASI_aliq=[(t.idDefaultValue.id,t.idDefaultValue.longName) for t in SelectAliquot()]
        #self.fields['barcode']=forms.CharField(label='Barcode',max_length=50,required=False)
        self.fields['generic']=forms.ModelChoiceField(label='Generic type',queryset = GenericContainerType.objects.all().exclude(abbreviation='cellplate'),required=False)
        self.fields['tipi']=forms.ModelChoiceField(label='Container type',queryset = ContainerType.objects.all(),required=False)
        #self.fields['geometry']=forms.ModelChoiceField(label='Geometry',queryset = Geometry.objects.all())
        self.fields['Aliquot_Type']=forms.MultipleChoiceField(label=mark_safe('Allowed biological content<br>(multiple selection is permitted)'),choices=CASI_aliq,widget=forms.SelectMultiple(),required=False)

class ChangeContainerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ChangeContainerForm, self).__init__(*args, **kwargs)        
        self.fields['generic']=forms.ModelChoiceField(label='Generic type',queryset = GenericContainerType.objects.all().exclude(abbreviation='cellplate'),required=False)
        self.fields['tipi']=forms.ModelChoiceField(label='Container type',queryset = ContainerType.objects.all(),required=False)
    
class NewGeometryForm(forms.Form):
    x=forms.IntegerField(label='Rows number',max_value=40)
    y=forms.IntegerField(label='Columns number')
    
class HistoricForm(forms.Form):
    file=forms.FileField(label='File')
        
