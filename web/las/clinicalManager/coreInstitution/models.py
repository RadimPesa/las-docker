from django.db import models

# Create your models here.

class Institution (models.Model):
    identifier      =   models.CharField(max_length=30)
    name            =   models.CharField(max_length=50)
    institutionType =   models.CharField(max_length=30)

