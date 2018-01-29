from django.db import models
from django.contrib.auth.models import User,Permission
from ngs.mw import threadlocals
import datetime, audit
from django.conf import settings

# Create your models here.

class Member(models.Model):
    class Meta:
        permissions = (
            ("can_view_NGS_upload_request", "Upload request"),
            ("can_view_NGS_validate_aliquots", "Validate aliquots"),
            ("can_view_NGS_run_experiment", "Run experiment")
        )

def getUsername(instance):
    return threadlocals.get_current_user()

class Aliquot(models.Model):
    #non metto lo unique nel gen perche' potrei inserire due volte lo stesso campione proveniente dalla biobanca
    genId = models.CharField(max_length=100)
    date = models.DateField(blank=True, null = True)
    owner = models.CharField(max_length=100, blank=True, null=True)
    exhausted = models.BooleanField()
    volume = models.FloatField(blank=True, null=True)
    concentration = models.FloatField(blank=True, null=True)
    label_request = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField( blank=True, null=True)
    
    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername),))

    class Meta:
        verbose_name_plural='Aliquots'
        db_table = 'aliquot'
    def __unicode__(self):
        return u"GenID: %s" % (self.genId)

class Aliquot_has_Experiment (models.Model):    
    aliquot_id= models.ForeignKey('Aliquot', db_column='aliquot_id',verbose_name='Aliquot')
    idExperiment = models.ForeignKey('Experiment', db_column='experiment_id',verbose_name='Experiment')
    feature_id=models.ForeignKey('Feature', db_column='feature_id',verbose_name='Feature', blank=True,null=True)
    value=models.CharField(max_length=100)
    
    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername),))
    
    class Meta:
        verbose_name_plural='Aliquot_has_Experiment'
        db_table = 'aliquot_has_experiment'
    def __unicode__(self):
        return self.aliquot_id.genId+' '+self.feature_id.name+' '+self.value

class Aliquot_has_Request(models.Model):
    aliquot_id = models.ForeignKey('Aliquot', db_column='aliquot_id')
    request_id = models.ForeignKey('Request', db_column='request_id')
    feature_id=models.ForeignKey('Feature', db_column='feature_id',verbose_name='Feature', blank=True,null=True)
    value=models.CharField(max_length=100)

    class Meta:
        verbose_name_plural='Aliquot_has_Request'
        db_table = 'aliquot_has_request'

    def __unicode__(self):
        return u"%s of request: %s" % (self.aliquot_id, self.request_id)

class Experiment (models.Model):
    time_creation = models.DateTimeField(blank=True,null=True)
    time_executed = models.DateTimeField(blank=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField( blank=True, null=True)
    #idInstrument = models.ForeignKey('Instrument', db_column='id_instrument', blank=True, null=True)
    #idAssay = models.ForeignKey('Assay', db_column='id_assay', blank=True, null=True)
    #idKit = models.ForeignKey('Kit', db_column='id_kit', blank=True, null=True)
    idOperator = models.ForeignKey(User, db_column='operator', blank=True, null=True)
    request_id = models.ForeignKey('Request', db_column='request_id', blank=True, null=True)
    
    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername),))
    
    class Meta:
        verbose_name_plural='Experiment'
        db_table = 'experiment'
    def __unicode__(self):
        return u"%s performed by %s" % (self.time_creation, self.idOperator)

class Feature(models.Model):
    name=models.CharField(max_length=30)  
    measureUnit=models.CharField(max_length=20, blank=True)
    class Meta:
        verbose_name_plural='Features'
        db_table='feature'
    def __unicode__(self):
        return self.name+' '+str(self.measureUnit)

class MeasurementEvent (models.Model):
    aliquot_id= models.ForeignKey('Aliquot', db_column='aliquot_id',blank=True,null=True)
    experiment_id = models.ForeignKey('Experiment', db_column='experiment_id',blank=True,null=True)
    namefile = models.CharField(max_length=200)
    link_file = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural='MeasurementEvents'
        db_table = 'measurement_event'
    def __unicode__(self):
        return u"%s: %s" % (self.aliquot_id, self.link_file )

class Request(models.Model):
    idOperator = models.ForeignKey(User, db_column='operator', blank=True, null=True)
    timestamp = models.DateTimeField(null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField( blank=True, null=True)
    owner = models.CharField(max_length=100)
    pending = models.BooleanField(default=True)
    timechecked = models.DateTimeField(null=True, blank = True)
    #per sapere da dove arrivano le richieste, se dalla biobanca o dall'esterno. In quest'ultimo caso l'inserimento dei campioni
    #passa dalla schermata insertSample del modulo stesso
    source = models.CharField(max_length=30, blank=True, null=True)
    
    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername),))
    
    class Meta:
        verbose_name_plural='Requests'
        db_table = 'request'
    def __unicode__(self):
        return u"%s @ %s assigned to %s requested by %s" % (self.title, self.timestamp, self.idOperator, self.owner)
        

######################################
# Items used in NGS
######################################


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

class Assay(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural='Assay'
        db_table='assay'
    def __unicode__(self):
        return self.name

class Kit(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural='Kits'
        db_table='kit'
    def __unicode__(self):
        return self.name



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


'''START WORKING GROUP AREA'''

class WG(models.Model):
    name= models.CharField(max_length=40)
    users = models.ManyToManyField(User, through="WG_User")
    owner= models.ForeignKey(User,related_name="owner_wg_set")
    class Meta:
        db_table = 'ngs_wg'

class WG_User(models.Model):
    WG=models.ForeignKey(WG)
    user=models.ForeignKey(User)
    permission=models.ForeignKey(Permission,blank=True, null=True)
    class Meta:
        unique_together = ("WG","user","permission")
        db_table = 'ngs_wg_user'

'''END WG AREA'''
