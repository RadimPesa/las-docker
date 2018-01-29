from django.db import models
from django.contrib.auth.models import User,Permission
import datetime
from django.conf import settings

# Create your models here.
class Member(models.Model):
    class Meta:
        permissions = (
            ("can_view_LBM_upload_request", "Upload request"),
            ("can_view_LBM_validate_aliquots", "Validate aliquots"),
            ("can_view_LBM_run_experiment", "Run experiment"),
            ("can_view_LBM_define_experiment", "Define experiment"),
            ("can_view_LBM_filter_results", "Filter results")
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

    class Meta:
        verbose_name_plural='Experiment'
        db_table = 'experiment'
    def __unicode__(self):
        return u"%s with %s performed by %s" % (self.time_creation, self.idInstrument, self.idOperator)


class Region (models.Model):
    code = models.CharField(max_length=30)
    
    class Meta:
        verbose_name_plural='Regions'
        db_table = 'region'
    def __unicode__(self):
        return u"%s" % (self.code )

class AliasRegion (models.Model):
    name = models.CharField(max_length=30)
    idRegion = models.ForeignKey('Region', db_column='region_id')

    class Meta:
        verbose_name_plural='AliasRegions'
        db_table = 'aliasregion'
    def __unicode__(self):
        return u"%s" % (self.name)



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
    idMeasure = models.ForeignKey('Measure', db_column='measure_id')
    region = models.ForeignKey('Region', db_column='region')
    lasmeasureId = models.CharField(max_length=100, db_column='lasmeasureid')

    class Meta:
        verbose_name_plural='MeasureTypes'
        db_table = 'measure_type'
    def __unicode__(self):
        return u"%s @ %s" % (self.name, self.region)


class Measure (models.Model):
    name = models.CharField(max_length=100)
    unity_measure = models.CharField(max_length=100, blank=True, null=True)    

    class Meta:
        verbose_name_plural='Measures'
        db_table = 'measure'
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.unity_measure)

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

