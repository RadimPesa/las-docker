from django import forms
from django.contrib.admin import widgets 
from time import strptime, strftime
from django.forms import fields
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField
from xenopatients.models import *
from datetime import date, timedelta
import datetime

class InputFile(forms.Form):
    fileName = forms.FileField(label='File',required = True)

class GroupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['date'] = forms.DateField(widget = widgets.AdminDateWidget())
        self.fields['protocol'] = forms.ModelChoiceField(queryset = Protocols.objects.all(), initial=0, required=False)
        #forms.ModelChoiceField(queryset = Protocols.objects.all(), initial=0, required=False)
    
class DetailsGroupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DetailsGroupForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(widget=forms.TextInput(attrs={"onPaste":"return false","onkeypress":"validate(event)"}))
        self.fields['protocol'] = forms.ModelChoiceField(queryset = Protocols.objects.all(), initial=0, required=False, label="Expected Protocol")
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.PasswordInput()

class WritingMiceForm (forms.Form):
    gender = forms.TypedChoiceField(coerce=bool, choices=((0, 'Male'), (1, 'Female')), widget=forms.RadioSelect, initial=0 )

class FirstStartMiceForm(forms.Form):
    def __init__(self, name, *args, **kwargs):
        super(FirstStartMiceForm, self).__init__(*args, **kwargs)
        self.fields['arrival_date'] = forms.DateField(widget = widgets.AdminDateWidget(), initial=date.today())
        self.fields['age_in_weeks'] = forms.IntegerField()
        self.fields['source'] = forms.ModelChoiceField(queryset = Source.objects.all())
        self.fields['mouse_strain'] = forms.ModelChoiceField(queryset = Mouse_strain.objects.all())
        self.fields['status'] = forms.ModelChoiceField(queryset = Status.objects.filter(default = '1'), initial = 2 )
    def clean_arrival_date(self):
        if self.cleaned_data['arrival_date'] > date.today():
            raise forms.ValidationError("Time travel are we?")
        return date
        
 
class ChangeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ChangeForm, self).__init__(*args, **kwargs)
        list_status = []
        langs = ChangeStatus.objects.values('to_status').distinct()
        for lang in langs:
            list_status.append( Status.objects.get(id = lang['to_status']))
        STATUS = [(s, s) for s in list_status]
        self.fields['target_status'] = forms.MultipleChoiceField(choices = STATUS, widget=forms.Select())

class CustomForm(forms.Form):
    def __init__(self, status_name, *args, **kwargs):
        super(CustomForm, self).__init__(*args, **kwargs)
        fields = Status_info_has_status.objects.filter(id_status__name = status_name)
        if fields:
            for f in fields:
                if f.id_info.description == "Text":
                    self.fields['notes'] = forms.CharField(max_length=45, widget=forms.TextInput(attrs={"onPaste":"return false","onkeypress":"validate(event)"}))
                if f.id_info.description == "Date":
                    self.fields['death_date'] = forms.DateField(widget = widgets.AdminDateWidget(), initial=date.today())
    def clean_death_date(self):
        if self.cleaned_data['death_date'] > date.today():
            raise forms.ValidationError("Time travel are we?")
        return date

class ScopeForm (forms.Form):
    scope_detail = forms.ModelChoiceField(queryset = Scope_details.objects.all(), initial=1)

class ExisistingProtocolsForm (forms.Form):
    def __init__(self, *args, **kwargs):
        super(ExisistingProtocolsForm, self).__init__(*args, **kwargs)
        self.fields['list_protocols'] = forms.ModelChoiceField(queryset = Protocols.objects.all().order_by('name'), widget=forms.RadioSelect( attrs={'onclick':'loadArms()'}), initial=99999)

class ExisistingTreatmentsForm (forms.Form):
    list_treatments = forms.ModelChoiceField(queryset = Arms.objects.all().order_by('name'), widget=forms.RadioSelect, initial=1)

class DateForTreatmentsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DateForTreatmentsForm, self).__init__(*args, **kwargs)
        self.fields['start_date'] = forms.DateTimeField(widget = widgets.AdminDateWidget(), initial = datetime.date.today() + datetime.timedelta(days=1) )
        self.fields['start_time'] = forms.DateTimeField(widget = widgets.AdminTimeWidget(), initial = datetime.datetime.now()) #format = '%H:%M',

class CreateTreatmentForm (forms.Form):
    name = forms.CharField(max_length=45, widget=forms.TextInput(attrs={"onPaste":"return false","onkeypress":"validate(event)"}))
    description = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"onPaste":"return false","onkeypress":"validate(event)"}))
    duration = forms.IntegerField()
    type_of_time = forms.TypedChoiceField(choices=((0, 'minutes'), (1, 'hours'), (2, 'days'), (3, 'months')), initial=2)
    forces_explant = forms.BooleanField()

class DetailsTreatmentForm (forms.Form):
    drug = forms.ModelChoiceField(queryset = Drugs.objects.all().order_by('name'), initial=1)
    via = forms.ModelChoiceField(queryset = Via_mode.objects.all().order_by('description'), initial=1)
    dose = forms.FloatField(label="Weight in milligrams of one dose of the drug", widget = forms.TextInput( attrs={'title':'Dose: weight in milligrams of one dose of the drug'}) )
    schedule = forms.IntegerField( label="Number of time to give the drug in the selected unit of time",widget = forms.TextInput( attrs={'title':'Schedule: number of time to give the drug in the selected unit of time'}), initial = 1 )

class StartImplantForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StartImplantForm, self).__init__(*args, **kwargs)
        self.fields['date'] = forms.DateField(widget = widgets.AdminDateWidget(), initial=date.today())
        self.fields['scope_detail'] = forms.ModelChoiceField(queryset = Protocols.objects.all(), initial=0, required=False, label="Expected Protocol")
        self.fields['notes'] = forms.CharField(max_length=45, required=False, widget=forms.TextInput(attrs={"onPaste":"return false","onkeypress":"validate(event)"}))

SITECHOICE = [(s.shortName,s.longName) for s in Site.objects.all()]
class ImplantForm (forms.Form):
    barcode_of_mouse = forms.CharField(max_length=15, label='Mouse barcode', widget = forms.TextInput(attrs={'title':'Insert the barcode of the mouse.', 'onKeyup':"checkKey(event)"}))
    site = forms.ChoiceField(choices = SITECHOICE)#, initial=1)
    bad_quality_flag = forms.BooleanField()

class SiteForm (forms.Form):
    site = forms.ChoiceField(choices = SITECHOICE)#, initial=1)

class CollectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CollectionForm, self).__init__(*args, **kwargs)
        self.fields['date'] = forms.DateField(widget = widgets.AdminDateWidget(), initial=date.today())

CASI = [(t.id,t.abbreviation) for t in TissueType.objects.all()]
class TissueForm(forms.Form):
    tissue = forms.MultipleChoiceField( choices=CASI, label='Tissue to be obtained', required=True, widget=forms.CheckboxSelectMultiple() )

class ProgrammedExplantForm(forms.Form):
    #uso il metodo init per fare in modo che l'elenco degli espianti programmati sia sempre dinamicamente aggiornato (altrimenti, si aggiorno solo una volta ad ogni riavvio del server......)
    def __init__(self, *args, **kwargs):
        super(ProgrammedExplantForm, self).__init__(*args, **kwargs)
        CHOOSE = [( m.id_mouse.id_genealogy,  str(m.id_mouse.id_genealogy) + ' [' + str(m.id_mouse.id_group.name) + ']'+ ' - ' + str(m.id_scope) + ' - ' + m.scopeNotes) for m in Programmed_explant.objects.filter(done = '0')]
        self.fields['notes'] = forms.CharField(max_length=45, required=False, widget=forms.TextInput(attrs={"onPaste":"return false","onkeypress":"validate(event)"}))
        self.fields['mice']  = forms.MultipleChoiceField(choices=CHOOSE,label='Mice to be explanted', required=False,widget=forms.CheckboxSelectMultiple())

QUALCHOICE = [(q.value,q.value) for q in Qualitative_values.objects.all() if q.value != 'N.D.']
class QualMeasureForm (forms.Form):
    value = forms.ChoiceField(choices = QUALCHOICE, label='', widget = forms.RadioSelect(), initial='None')

class SiteForm (forms.Form):
    site = forms.ChoiceField(choices = SITECHOICE)#, initial=1)
