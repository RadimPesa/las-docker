from django.db import models
from django.contrib.auth.models import User


class Entity(models.Model):
    identifier      =   models.CharField(max_length=32)
    belongingCore   =   models.CharField(max_length=15)


class Feature (models.Model):
    identifier      =   models.CharField(max_length=30)
    dataType        =   models.CharField(max_length=40, null=True)
    belongingCore   =   models.CharField(max_length=15, null = True)
    fatherFeatureId =   models.ForeignKey('self', null=True)


class UPhaseEntity (models.Model):
    entity              =   models.ForeignKey(Entity)
    uPhase              =   models.CharField(max_length=15)
    startTimestamp      =   models.DateTimeField()
    startNotes          =   models.TextField(null = True)
    startOperator       =   models.ForeignKey(User, null = True, related_name='appPathologyManagement_startOperator')
    endTimestamp        =   models.DateTimeField(null = True)
    endNotes            =   models.TextField(null = True)
    endOperator         =   models.ForeignKey(User, null = True, related_name='appPathologyManagement_endOperator')
    fatherUPhaseEntity  =   models.ForeignKey('self', null = True)


class UPhaseEntityFeature (models.Model):
    uPhaseEntity=models.ForeignKey(UPhaseEntity)
    feature=models.ForeignKey(Feature)    
    value =   models.CharField(max_length=100)