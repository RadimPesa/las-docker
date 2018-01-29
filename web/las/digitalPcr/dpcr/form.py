# -*- coding: latin-1 -*-

from dpcr.models import *
from django import forms
from django.forms.models import modelformset_factory
from django.forms.extras import SelectDateWidget


class UploadFileForm(forms.Form): 
    file  = forms.FileField()