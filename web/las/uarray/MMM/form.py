# -*- coding: latin-1 -*-

from MMM.models import *
from django import forms
from django.forms.models import modelformset_factory
from django.forms.extras import SelectDateWidget


class NotesScanForm(forms.Form):
    notes = forms.CharField(widget=forms.Textarea (attrs={'style':'width:500px;height:50px'}), required=False)

class UploadFileForm(forms.Form):
    file  = forms.FileField()


class ManualRequestDefinitionForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput)


class ScanProtocolForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ScanProtocolForm, self).__init__(*args, **kwargs)
        self.fields['Protocol'] = forms.CharField(widget=forms.Select(choices = [(s.pk, s.name) for s in ScanProtocol.objects.all()]))


class HybrProtForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(HybrProtForm, self).__init__(*args, **kwargs)
        self.fields['Hyb_protocol'] = forms.CharField(widget=forms.Select(choices = [(hyb.pk, hyb.name) for hyb in HybProtocol.objects.all()]))
        self.fields['Hyb_instrument'] = forms.CharField(widget=forms.Select(choices=[(hyb.pk, hyb.name) for hyb in Instrument.objects.filter(scan="0")]))


class HybProtForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HybProtForm, self).__init__(*args, **kwargs)
        self.fields['loadQuantity'].label = "Load Quantity (ng)"
        self.fields['hybBuffer'].label = "Hybridization Buffer (ul)"
        self.fields['hybridTemp'].label = "Hybridization Temperature (°C)"
        self.fields['totalVolume'].label = "Total Volume (ul)"
        self.fields['hybTime'].label = "Hybridization Time (hours)"
        self.fields['denTemp'].label = "Denaturation Temperature (°C)"
        self.fields['denTime'].label = "Denaturation Time (minutes)"
    
    class Meta:
        model = HybProtocol

'''
class ExperimentDefinitionForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput)
    description = forms.CharField(widget=forms.Textarea)
    project = forms.CharField(widget=forms.Select(choices = [(Project.pk, Project.title) for Project in Project.objects.all()]))

    def store(self):
        project_ = Project.objects.get(pk=self.cleaned_data['project'])
        try:
            experiment = Experiment.objects.get(title=self.cleaned_data['title'])
        except:
            new_experiment = Experiment(title = self.cleaned_data['title'], 
                               description= self.cleaned_data['description'],
                               idProject = project_)
            new_experiment.save()
            return new_experiment


class NewProjectForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput)
    description = forms.CharField(widget=forms.Textarea)

    def save(self):
        new_project_data = Project(title=self.cleaned_data['title'], description=self.cleaned_data['description'])
        new_project_data.save()
        return new_project_data
'''