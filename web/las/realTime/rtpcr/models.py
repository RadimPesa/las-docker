from django.db import models
from django.contrib.auth.models import User,Permission
import datetime
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from time import strptime, strftime
from django.core.exceptions import ValidationError
from django.conf import settings
from mongoengine import *

class Member(models.Model):
    class Meta:
        permissions = (
            ("can_view_LBM_upload_request", "Upload request"),
            ("can_view_LBM_validate_aliquots", "Validate aliquots"),
            ("can_view_LBM_run_experiment", "Run experiment")
        )

def getUsername(instance):
    return threadlocals.get_current_user()

class Aliquot(models.Model):
    genId = models.CharField(max_length=100, unique=True)
    date = models.DateField(blank=True, null = True)
    owner = models.CharField(max_length=100, blank=True, null=True)
    exhausted = models.BooleanField()
    volume = models.FloatField()
    concentration = models.FloatField()
    
    class Meta:
        verbose_name_plural='Aliquots'
        db_table = 'aliquot'
    def __unicode__(self):
        return u"GenID: %s" % (self.genId)

class Request(models.Model):
    idOperator = models.ForeignKey(User, db_column='operator', blank=True, null=True)
    timestamp = models.DateTimeField(null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    owner = models.CharField(max_length=100)
    pending = models.BooleanField(default=True)
    timechecked = models.DateTimeField(null=True, blank = True)
    time_executed = models.DateTimeField(null=True, blank = True)

    class Meta:
        verbose_name_plural='Requests'
        db_table = 'request'
    def __unicode__(self):
        return u"%s @ %s assigned to %s requested by %s" % (self.title, self.timestamp, self.idOperator, self.owner)

class Aliquot_has_Request(models.Model):
    aliquot_id = models.ForeignKey('Aliquot', db_column='aliquot_id') 
    request_id = models.ForeignKey('Request', db_column='request_id')
    sample_features = models.CharField(max_length=100, blank=True, null=True)
    volumetaken = models.FloatField()

    class Meta:
        verbose_name_plural='Aliquot_has_Request'
        db_table = 'aliquot_has_request'

    def __unicode__(self):
        return u"%s of request: %s" % (self.aliquot_id, self.request_id)

class Sample(models.Model):
    time_creation = models.DateTimeField()
    idAliquot_has_Request = models.ForeignKey(Aliquot_has_Request, db_column='aliquot_has_request_id')
    idExperiment = models.ForeignKey('Experiment', db_column='experiment_id')
    probe = models.CharField(max_length=100)
    value = models.FloatField(null=True)
    

    class Meta:
        verbose_name_plural='Samples'
        db_table = 'sample'
    
    def __unicode__(self):
        return u"%s of %s" % (self.pk, self.idExperiment)

class Instrument(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural='Instruments'
        db_table='instrument'
    def __unicode__(self):
        return self.name

class Experiment (models.Model):
    time_creation = models.DateTimeField()
    time_executed = models.DateTimeField(null=True)
    idInstrument = models.ForeignKey('Instrument', db_column='id_instrument', blank=True, null=True)
    idOperator = models.ForeignKey(User, db_column='operator')
    raw_id = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural='Experiment'
        db_table = 'experiment'
    def __unicode__(self):
        return u"%s with %s performed by %s" % (self.time_creation, self.idInstrument, self.idOperator)

class Analysis(models.Model):
    time_executed = models.DateTimeField(db_column='timestamp')
    id_experiment = models.ForeignKey(Experiment, db_column='id_experiment')
    description = models.CharField(max_length=200)
    idOperator = models.ForeignKey(User, db_column='id_user')
    analysis_id = models.CharField(max_length=100, null=True, blank=True) # UUID of graph node
    analysisType_id = models.ForeignKey('AnalysisType', db_column='id_analysis_type')
    description_id = models.CharField(max_length=32,null=True,blank=True) # UUID of description doc

    class Meta:
        verbose_name_plural='Analysis'
        db_table = 'analysis'

class Formula(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300,null=True,blank=True)
    expression = models.TextField()
    variables = models.TextField()
    analysisType = models.ForeignKey('AnalysisType', db_column='id_analysis_type')
    valueType = models.CharField(max_length=32)

    class Meta:
        verbose_name_plural='Formula'
        db_table = 'formula'

class AnalysisType(models.Model):
    value = models.CharField(max_length=180)
    name = models.CharField(max_length=180)

    class Meta:
        verbose_name_plural='AnalysisType'
        db_table = 'analysis_type'

######################################
# Web services for the other modules
######################################


class WebService(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = 'webservice'
        db_table = 'webservice'

    def __unicode__(self):
        return self.name

class Urls(models.Model):
    _url = models.CharField(max_length = 255, unique=True, db_column = 'url')
    available = models.BooleanField()
    id_webservice = models.ForeignKey(WebService, db_column='id_webservice')
    class Meta:
        verbose_name_plural = 'urls'
        db_table = 'url'
    def __unicode__(self):
        return self.url
    @property
    def url(self):
        if str(self._url).startswith('http'):
            return self._url
        else:
            return settings.DOMAIN_URL+self._url


''' ASSAY '''

class Assay(models.Model):
    WG=models.ForeignKey('WG')
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'assays'
        db_table = 'assay'

    def __unicode__(self):
        return self.name

class Assay_has_Probe(models.Model):
    probe = models.CharField(max_length=255)
    id_assay = models.ForeignKey('Assay', db_column='id_assay')

    class Meta:
        verbose_name_plural = 'assay_has_probe'
        db_table = 'assay_has_probe'

    def __unicode__(self):
        return self.probe

'''START WORKING GROUP AREA'''

class WG(models.Model):
    name= models.CharField(max_length=40)
    users = models.ManyToManyField(User, through="WG_User")
    owner= models.ForeignKey(User,related_name="owner_wg_set")
    class Meta:
        db_table = 'wg'

class WG_User(models.Model):
    WG=models.ForeignKey(WG)
    user=models.ForeignKey(User)
    permission=models.ForeignKey(Permission,blank=True, null=True)
    class Meta:
        unique_together = ("WG","user","permission")
        db_table = 'wg_user'

'''END WG AREA'''

#######################
# Non-relation models #
#######################

class AnalysisOutput(Document):
    analysis_id = IntField()
    value = FloatField() # if null => N/A
    variables = DictField()
    test_probe = StringField()
    ref_probes = ListField(StringField())

    def getVariableValues(self):
        return {k:self.convertToValues(v) for k,v in self.variables.iteritems()}

    @staticmethod
    def convertToValues(data):
        if not isinstance(data, list):
            data = [data]
        out = []
        for x in data:
            if isinstance(x, list):
                out.append(convertToValues(x))
            else:
                s = Sample.objects.get(pk=x)
                out.append({'id': x, 'probe_uuid': s.probe, 'value': s.value})
        return out

    def getSampleGenid(self):
        for v in self.variables.values():
            while True:
                if not isinstance(v, list):
                    try:
                        return Sample.objects.get(pk=v).idAliquot_has_Request.aliquot_id.genId
                    except:
                        return None
                else:
                    if len(v) == 0:
                        break
                    else:
                        v = v[0]


class AnalysisDescription(Document):
    analysis_id = IntField()
    formula_id = IntField() #DictField()
    probe_var_mapping = DictField()
    aggregation_criteria = DictField()

