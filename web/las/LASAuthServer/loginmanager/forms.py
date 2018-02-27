from django import forms
from loginmanager.models import *

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.PasswordInput()


class CreateAffiliation(forms.Form):
    companyName=forms.CharField(label='Company Name',max_length=45)
    department=forms.CharField(label='Department',max_length=45)
    city=forms.CharField(label='City',max_length=45)
    state=forms.CharField(label='State',max_length=45)
    zipCode=forms.CharField(label='Zip Code',max_length=45)

