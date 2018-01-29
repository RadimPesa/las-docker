from django.db import models
from django.contrib.auth.models import User, Permission
import datetime
import fingerprinting.settings as settings

# Create your models here.
class Member(models.Model):
    class Meta:
        permissions = (
            ("can_view_FPM_upload_request", "Upload request"),
            ("can_view_FPM_validate_aliquots", "Validate aliquots"),
            ("can_view_FPM_run_experiment", "Run experiment"),
            ("can_view_FPM_define_experiment", "Define experiment"),
            ("can_view_FPM_filter_results", "Filter results")
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
    description = models.CharField(max_length=100, blank=True, null=True)
    owner = models.CharField(max_length=100)
    pending = models.BooleanField(default=True)
    timechecked = models.DateTimeField(blank=True, null=True,db_column='time_checked')
    time_executed = models.DateTimeField(blank=True, null=True, db_column='time_execution')

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
    plate = models.CharField(max_length=50, blank=True, null=True)
    well = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural='Aliquot_has_Request'
        db_table = 'aliquot_has_request'

    def __unicode__(self):
        return u"%s of request: %s" % (self.aliquot_id, self.request_id)


class Sample (models.Model):
    time_creation = models.DateTimeField()
    idAliquot_has_Request = models.ForeignKey('Aliquot_has_Request', db_column='aliquot_has_request_id')
    idExperiment = models.ForeignKey('Experiment', db_column='experiment_id')
    probe = models.CharField(max_length=100)
    
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
    idOperator = models.ForeignKey(User, db_column='id_user')
    analysis_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name_plural='Analysis'
        db_table = 'analysis'


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
    _url = models.CharField(max_length = 255, unique=True, db_column='url')
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
            return settings.DOMAIN_NAME+self._url


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