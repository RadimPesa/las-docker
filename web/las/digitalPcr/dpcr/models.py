from django.db import models
from django.contrib.auth.models import User,Permission
import datetime
from django.conf import settings
import json

# Create your models here.
class Member(models.Model):
    class Meta:
        permissions = (
            ("can_view_DPCR_upload_request", "Upload request"),
            ("can_view_DPCR_validate_aliquots", "Validate aliquots"),
            ("can_view_DPCR_run_experiment", "Run experiment"),
            ("can_view_DPCR_define_experiment", "Define experiment"),
            ("can_view_DPCR_filter_results", "Filter results")
        )


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
    description = models.CharField(max_length=100, blank=True, null=True)
    owner = models.CharField(max_length=100)
    pending = models.BooleanField(default=True)
    timechecked = models.DateTimeField(null=True)
    time_executed = models.DateTimeField(null=True)
    abortTime = models.DateTimeField(null=True, db_column='aborttime')
    abortUser = models.ForeignKey(User, blank=True, null=True, db_column='abortuser', related_name='abort_user')

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


class Sample (models.Model):
    position = models.CharField(max_length=5)
    probe = models.CharField(max_length=100)
    gene = models.CharField(max_length=100)
    wt = models.BooleanField(default=False)
    idAliquot_has_Request = models.ForeignKey('Aliquot_has_Request', db_column='aliquot_has_request_id')
    idExperiment = models.ForeignKey('Experiment', db_column='experiment_id')

    class Meta:
        verbose_name_plural='Samples'
        db_table = 'sample'
    def __unicode__(self):
        return u"%s (position %s) @ %s - %s" % (self.idAliquot_has_Request, self.position, self.probe, self.gene)

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
    plot = models.CharField(max_length=100, blank=True, null=True)
    exp_type = models.ForeignKey('ExperimentType', blank=False, null=False)

    class Meta:
        verbose_name_plural='Experiment'
        db_table = 'experiment'
    def __unicode__(self):
        return u"%s with %s performed by %s" % (self.time_creation, self.idInstrument, self.idOperator)

class ExperimentType(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    class Meta:
        db_table = 'experiment_type'
    def __unicode__(self):
        return name

class MeasurementEvent (models.Model):
    value = models.CharField(max_length=100)
    idSample = models.ForeignKey('Sample', db_column='sample_id')
    idMeasureType = models.ForeignKey('MeasureType', db_column='measuretype_id')
    idExperiment = models.ForeignKey('Experiment', db_column='experiment_id')

    class Meta:
        verbose_name_plural='MeasurmentEvents'
        db_table = 'measurement_event'
    def __unicode__(self):
        return u"%s: %s %s" % (self.idSample, self.value, self.idMeasureType)


class MeasureType (models.Model):
    name = models.CharField(max_length=100)
    lasmeasureId = models.CharField(max_length=100, db_column='lasmeasureid')

    class Meta:
        verbose_name_plural='MeasureTypes'
        db_table = 'measure_type'
    def __unicode__(self):
        return u"%s" % (self.name)


class FilterSession (models.Model):
    timestamp = models.DateTimeField()
    operator = models.ForeignKey(User, db_column='operator')
    features = models.TextField()

    class Meta:
        verbose_name_plural='FilterSessions'
        db_table = 'filter_session'
    def __unicode__(self):
        return u"%s @ %s with filter %s" % (self.operator, self.timestamp, self.features)


class Aliquot_has_Filter (models.Model):
    aliquot_id = models.ForeignKey('Aliquot', db_column='aliquot_id') 
    filter_id = models.ForeignKey('FilterSession', db_column='filter_id')
    values = models.TextField()

    class Meta:
        verbose_name_plural='Aliquots_has_Filter'
        db_table = 'aliquot_has_filter'

    def __unicode__(self):
        return u"%s of filter session: %s" % (self.aliquot_id, self.filter_id)

''' ASSAY '''

class Assay(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'assays'
        db_table = 'assay'

    def __unicode__(self):
        return self.name

    def getAssayMutations(self):
        return map(lambda x: json.loads(x.mut_description), Assay_has_Mutation.objects.filter(id_assay=self))

    def getAssayTypes(self):
        return map(lambda x: x.exp_type.id, Assay_has_ExpType.objects.filter(assay=self))

class Assay_has_ExpType(models.Model):
    assay = models.ForeignKey('Assay', blank=False, null=False)
    exp_type = models.ForeignKey('ExperimentType', blank=False, null=False)

    class Meta:
        db_table = 'assay_has_exptype'

    def __unicode__(self):
        return self.assay.name + u" - " + self.exp_type.name

class Assay_has_Mutation(models.Model):
    id_assay = models.ForeignKey('Assay', db_column='id_assay')
    mut_description = models.CharField(max_length=1024)
    
    class Meta:
        verbose_name_plural = 'assay_has_mutation'
        db_table = 'assay_has_mutation'

    def __unicode__(self):
        return self.mut_description

'''START WORKING GROUP AREA'''

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
    _url = models.CharField(max_length = 255, unique=True,db_column='url')
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



###WG SECTION


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

