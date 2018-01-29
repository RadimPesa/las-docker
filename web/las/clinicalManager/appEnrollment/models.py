from django.db import models
from django.contrib.auth.models import User, Permission

# Create your models here.

class Entity (models.Model):
    identifier      =   models.CharField(max_length=32 )#<<<<<<<<<
    belongingCore   =   models.CharField(max_length=15)#, primary_key=True)<<<<<<<<<


class Feature (models.Model):
    identifier      =   models.CharField(max_length=30)
    dataType        =   models.CharField(max_length=40, null=True, blank=True)
    belongingCore   =   models.CharField(max_length=15, null = True)#, primary_key=True)<<<<<<<<<
    fatherFeatureId =   models.ForeignKey('self', null=True, blank=True)

class UPhaseEntity (models.Model):
    entity              =   models.ForeignKey(Entity)
    uPhase              =   models.CharField(max_length=15)
    startTimestamp      =   models.DateTimeField()
    startNotes          =   models.TextField(null = True)
    startOperator       =   models.ForeignKey(User,null = True ,related_name='startOperator')
    endTimestamp        =   models.DateTimeField(null = True)
    endNotes            =   models.TextField(null = True)
    endOperator         =   models.ForeignKey(User,null = True,related_name='endOperator')
    fatherUPhaseEntity  =   models.ForeignKey('self', null=True, blank=True)
    #identifier      =   models.CharField(max_length=30,)
    #patient         =   models.CharField(max_length=30, null = True)
    #trial           =   models.CharField(max_length=30, null = True)
    #patientTrialCode=   models.CharField(max_length=30, null = True)



class UPhaseEntityFeature (models.Model):
    uPhaseEntity=models.ForeignKey(UPhaseEntity)
    feature=models.ForeignKey(Feature)
    value =   models.CharField(max_length=100)





#WG MANAGEMENT
class Member(models.Model):
    class Meta:
        permissions=(
                     ('can_view_institutional_collection','Institutional Collection'),)

class WG(models.Model):
    name= models.CharField(max_length=40)
    users = models.ManyToManyField(User, through="WG_User")
    owner= models.ForeignKey(User,related_name="owner_wg_set")

class WG_User(models.Model):
    WG=models.ForeignKey(WG)
    user=models.ForeignKey(User)
    permission=models.ForeignKey(Permission,blank=True, null=True)
    class Meta:
        unique_together = ("WG","user","permission")


class AppEnrollmentUserWG(models.Model):
    user=models.ForeignKey(User)
    projectID=models.CharField(max_length=30)
    WG=models.ForeignKey(WG)
    class Meta:
        unique_together = ("user","projectID")
