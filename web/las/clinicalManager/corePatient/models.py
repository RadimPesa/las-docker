from django.db import models
#from django.contrib.auth.models import User, Permission
from py2neo import *
from django.conf import settings
from global_request_middleware import *

class WgObjectManager(models.Manager):

    def get_query_set(self):
        superWG = set(["Marsoni_WG"])
        # print get_WG()
        if settings.USE_GRAPH_DB==True and 'disabled' not in get_WG() and superWG.issuperset(get_WG())==False:
            groups=get_WG()
            groups = [g.encode('ascii','ignore') for g in groups]
            #groups =['admin','Marsoni_WG']
            graph = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
            query = neo4j.CypherQuery(graph,"MATCH (n:Patient)-[]-(wg:WG) where wg.identifier in "+str(groups)+" return n.identifier")
            r = query.execute()
            idList = list( [str(x[0]) for x in r.data])
            return super(WgObjectManager, self).get_query_set().filter(identifier__in=idList)
        else:
            return super(WgObjectManager, self).get_query_set()


class Patient(models.Model):
    objects=WgObjectManager()
    identifier      =   models.CharField(max_length=32, unique = True)
    firstName       =   models.CharField(max_length=40, null = True)
    lastName        =   models.CharField(max_length=40, null = True)
    fiscalCode      =   models.CharField(max_length=16, null = True)
    birthDate       =   models.DateField(null = True)
    birthPlace      =   models.CharField(max_length=45, null = True, blank=True)
    birthNation     =   models.CharField(max_length=45, null = True, blank=True)
    sex             =   models.CharField(max_length=1,  null = True)
    race            =   models.CharField(max_length=45, null = True)
    residencePlace  =   models.CharField(max_length=45, null = True)
    residenceNation =   models.CharField(max_length=45, null = True)
    vitalStatus     =   models.CharField(max_length=45, null = True)

    def __str__(self):              # __unicode__ on Python 2
        return self.firstName



class MergedPatient(models.Model):
    identifier      =   models.CharField(max_length=32, unique = True)
    firstName       =   models.CharField(max_length=40, null = True)
    lastName        =   models.CharField(max_length=40, null = True)
    fiscalCode      =   models.CharField(max_length=16, null = True)
    birthDate       =   models.DateField(null = True)
    birthPlace      =   models.CharField(max_length=45, null = True, blank=True)
    birthNation     =   models.CharField(max_length=45, null = True, blank=True)
    sex             =   models.CharField(max_length=1,  null = True)
    race            =   models.CharField(max_length=45, null = True)
    residencePlace  =   models.CharField(max_length=45, null = True)
    residenceNation =   models.CharField(max_length=45, null = True)
    vitalStatus     =   models.CharField(max_length=45, null = True)
    patient         =   models.ForeignKey(Patient)
    mergingDate     =   models.DateTimeField(null = True)

    def __str__(self):              # __unicode__ on Python 2
        return self.firstName


# Do not use the following classes

class Feature(models.Model):
    identifier      =   models.CharField(max_length=30)
    name            =   models.CharField(max_length=40)
    fatherFeatureId =   models.ForeignKey('self', null=True, blank=True)
    dataType        =   models.CharField(max_length=40, null=True, blank=True)
    belongingCore   =   models.CharField(max_length=15, null = True)#, primary_key=True)<<<<<<<<<

class PatientFeature(models.Model):
    patient         =   models.ForeignKey(Patient)
    feature         =   models.ForeignKey(Feature)
    value           =   models.CharField(max_length=200)
    lastUpdate      =   models.DateField()
    module          =   models.CharField(max_length=40)
    uPhase          =   models.CharField(max_length=40)
