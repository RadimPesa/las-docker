from django.db import models

# Create your models here.


class Project(models.Model):
    identifier  =   models.CharField(max_length=30)
    name        =   models.CharField(max_length=45)



class Feature(models.Model):
    identifier      =   models.CharField(max_length=30)
    name            =   models.CharField(max_length=40)
    fatherFeatureId =   models.ForeignKey('self', null=True, blank=True)
    dataType        =   models.CharField(max_length=40, null=True, blank=True)
    belongingCore   =   models.CharField(max_length=15, null = True)#, primary_key=True)<<<<<<<<<

class ProjectFeature(models.Model):
    project         =   models.ForeignKey(Project)
    feature         =   models.ForeignKey(Feature)
    value           =   models.CharField(max_length=200)
    lastUpdate      =   models.DateField()
    module          =   models.CharField(max_length=40)
    uPhase          =   models.CharField(max_length=40)


