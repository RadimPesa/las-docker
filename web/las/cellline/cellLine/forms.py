import re
from django.contrib.auth.models import User
from django import forms
from django.contrib.admin import widgets 
from time import strptime, strftime
from django.forms import fields
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField
from cellLine.models import *
from datetime import date, timedelta
import datetime

class NewProtocolForm(forms.Form):
    def __init__(self, listPlates, listTypeProtocol, listTypeProcess, *args, **kwargs):
        super(NewProtocolForm, self).__init__(*args, **kwargs)
        self.fields['name_protocol'] = forms.CharField(max_length=255)
        self.fields['description'] = forms.CharField( widget=forms.Textarea ,required = False)
        self.fields['fileName'] = forms.FileField(label='File',required = False)
        self.fields['plate'] = forms.TypedChoiceField(choices=listPlates, initial=0)
        self.fields['type_of_protocol'] = forms.TypedChoiceField(coerce=bool,choices=listTypeProtocol, widget=forms.RadioSelect, initial=0 )
        self.fields['type_process'] = forms.TypedChoiceField(coerce=bool, choices=listTypeProcess, widget=forms.RadioSelect, initial=0 )

    def clean_name_protocol(self):
        print Condition_protocol.objects.filter(protocol_name = self.cleaned_data['name_protocol']).count()
        print self.cleaned_data['name_protocol']
        if Condition_protocol.objects.filter(protocol_name = self.cleaned_data['name_protocol']).count() > 0:
            raise forms.ValidationError("Name already in use.")
        return self.cleaned_data['name_protocol']
        
        
