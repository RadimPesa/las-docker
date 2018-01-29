from django.db import models
from django.contrib.auth.models import User, Permission
import datetime
import settings
# Create your models here.

class Member(models.Model):
    class Meta:
        permissions = (
            ("can_view_MMM_upload_request", "Upload request"),
            ("can_view_MMM_insert_chip","Insert chip"),
            ("can_view_MMM_insert_chip_type", "Insert chip type"),
            ("can_view_MMM_plan_hybridization","Plan hybridization"),
            ("can_view_MMM_validate_hybridization","Validate hybridization"),
            ("can_view_MMM_hybridize","Hybridize"),
            ("can_view_MMM_scan","Scan"),
            ("can_view_MMM_scanqc","Scan qc"),
            ("can_view_MMM_hybridization_protocol","Hybridization protocol"),
            ("can_view_MMM_scan_protocol","Scan protocol"),
            ("can_view_MMM_explore_scan", "Explore scan"),
            ("can_view_MMM_experiment","Define experiment")
        )


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

class Aliquot(models.Model):
    sample_identifier = models.CharField(max_length=100, blank=True, null=True)
    genId = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(blank=True, null = True)
    owner = models.CharField(max_length=100, blank=True, null=True)
    exhausted = models.BooleanField()
    volume = models.FloatField()
    concentration = models.FloatField()
    
    class Meta:
        verbose_name_plural='Aliquots'
        db_table = 'aliquot'
    def __unicode__(self):
        if self.genId:
            return u"GenID: %s" % (self.genId)
        else:
            return u"SmpID: %s" % (self.sample_identifier)

class Request(models.Model):
    idOperator = models.ForeignKey(User, db_column='Operator_id', blank=True, null=True)
    timestamp = models.DateTimeField()
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)
    pending = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural='Requests'
        db_table = 'request'
    def __unicode__(self):
        return u"%s" % (self.id)



class Aliquot_has_Request(models.Model):
    aliquot_id = models.ForeignKey('Aliquot', db_column='aliquot_id') 
    request_id = models.ForeignKey('Request', db_column='request_id')
    sample_features = models.CharField(max_length=100, blank=True, null=True)
    exp_group = models.CharField(max_length=100,blank=True, null=True)
    tech_replicates = models.BooleanField(default=False)
    idHybPlan = models.ForeignKey('HybridPlan', db_column='hybridplan_id', blank=True, null=True, on_delete=models.SET_NULL)
    virtual_chip = models.IntegerField(blank=True, null=True)
    virtual_order = models.IntegerField(blank=True, null=True)


    class Meta:
        db_table = 'aliquot_has_request'
    def __unicode__(self):
        return u"%s Req: (%s) (%s)" % (self.aliquot_id, self.exp_group, self.request_id.timestamp)


class HybridPlan(models.Model):
    idOperator = models.ForeignKey(User, db_column='operator', blank=True, null=True)
    timeplan = models.DateTimeField()
    timecheck = models.DateTimeField()
    timehybrid = models.DateTimeField()
    idHybProtocol = models.ForeignKey('HybProtocol', db_column='hybprotocol_id')
    idInstrument = models.ForeignKey('Instrument', db_column='instrument_id')

    class Meta:
        db_table = 'hybridplan'
    def __unicode__(self):
        return u"Planed by %s at  %s" % (self.idOperator, self.timeplan)

class Geometry(models.Model):
    rules = models.CharField(max_length=1000)
    npos = models.IntegerField()
    class Meta:
        verbose_name_plural='Geometries'
        #Table's name in db
        db_table='geometry'
    def __unicode__(self):
        return u"%s" % (self.rules)

class ChipType(models.Model):
    title = models.CharField(max_length=100)
    manufacter = models.CharField(max_length=100)
    organism = models.CharField(max_length=100)
    probesNumber = models.CharField(max_length=100)
    GeoPlatformId = models.CharField(max_length=100)
    manifestFile = models.CharField(max_length=100)
    notes = models.CharField(max_length=100)
    layout = models.ForeignKey('Geometry', db_column='layout')
    class Meta:
        verbose_name_plural='ChipTypes'
        db_table='chiptype'
    def __unicode__(self):
        return (self.title)



class Software(models.Model):
    name = models.CharField(max_length=100)
    release = models.CharField(max_length=100)
    notes = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'Softwares'
        db_table = 'software'
    def __unicode__(self):
        return self.name

class Project(models.Model):
    title = models.CharField(max_length=100) 
    description = models.CharField(max_length=100, blank= True) 
    
    class Meta:
        db_table = 'project'
    def __unicode__(self):
        return u"%s %s" % (self.title, self.description)

class Instrument(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    scan = models.BooleanField()
    positions = models.CharField(max_length=2, null=True, blank=True)
    
    class Meta:
        verbose_name_plural='Instruments'
        db_table='instrument'
    def __unicode__(self):
        return self.name



class HybProtocol(models.Model):
    name = models.CharField(max_length=100, unique=True)
    loadQuantity = models.FloatField()
    hybBuffer = models.IntegerField()
    hybridTemp = models.IntegerField()
    totalVolume = models.IntegerField()
    hybTime = models.CharField(max_length=20)
    denTemp = models.IntegerField()
    denTime = models.IntegerField()
    notes = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name_plural = 'Hyb Protocols'
        db_table = 'hybprotocol'
    def __unicode__(self):
        return self.name

class Chip(models.Model):
    idChipType = models.ForeignKey('ChipType', db_column='chiptype_id')
    barcode = models.CharField(max_length=100)
    expirationDate = models.DateField()
    dmapFile = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)
    batchNumber = models.CharField(max_length=100)
    idHybevent = models.ForeignKey('HybridPlan', db_column='hybevent_id')
    notes = models.CharField(max_length=100, null=True, blank=True)
    class Meta:
        verbose_name_plural='Chips'
        #Table's name in db
        db_table='chip'
    def __unicode__(self):
        return u"%s %s" % (self.id, self.barcode)
    

class Assignment(models.Model):
    idChip = models.ForeignKey('Chip', db_column='chip_id')
    position = models.IntegerField(db_column='position')
    idAliquot_has_Request = models.ForeignKey('Aliquot_has_Request', db_column='aliquot_has_request_id')


    class Meta:
        verbose_name_plural='Assignments'
        db_table='assignment'
    def __unicode__(self):
        return u"chip: %s | pos: %s | aliquot: %s" % (self.idChip, self.position, self.idAliquot_has_Request.aliquot_id.id)


class ScanProtocol(models.Model):
    name = models.CharField(max_length=100)
    idSoftware = models.ForeignKey('Software', db_column='software_id')
    idInstrument = models.ForeignKey('Instrument', db_column='id_instrument')
    tobevalidated = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural='Scan Protocols'
        db_table='scanprotocol'
    def __unicode__(self):
        return self.name



class ScanEvent(models.Model):
    startScanTime = models.DateTimeField() 
    endScanTime = models.DateTimeField(blank = True, null = True) 
    idProtocol = models.ForeignKey('ScanProtocol', db_column='protocol_id')
    idOperator = models.ForeignKey(User, db_column='operator', blank=True, null=True)
    notes = models.CharField(max_length=100, blank = True, null = True)
    validated = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural='ScanEvents'
        db_table = 'scanevent'
    def __unicode__(self):
        return u"Protocol: %s, Date: %s Operator: %s" % (self.idProtocol, self.startScanTime, self.idOperator)


class Assignment_has_Scan(models.Model):
    idAssignment = models.ForeignKey('Assignment', db_column='assignment_id')
    idScanEvent = models.ForeignKey('ScanEvent', db_column='scanevent_id')
    qc = models.NullBooleanField(blank = True, null = True)
    link = models.CharField(max_length=100, blank = True, null = True)
    
    class Meta:
        verbose_name_plural='Assignments_has_Scan'
        db_table='assignment_has_scan'


class Chip_has_Scan(models.Model):
    idChip = models.ForeignKey('Chip', db_column='chip_id')
    idScanEvent = models.ForeignKey('ScanEvent', db_column='scanevent_id')
    link = models.CharField(max_length=100, blank = True, null = True)
    posonscanner = models.IntegerField()
    

    class Meta:
        verbose_name_plural='Chip_has_Scan'
        db_table = 'chip_has_scan'
    def __unicode__(self):
        return u"Chip: %s, Scan: %s, on scanner @ %s Link: %s" % (self.idChip, self.idScanEvent, self.posonscanner, self.link)

  
class Parameter(models.Model):
    name = models.CharField(max_length=100)
    default_value = models.CharField(max_length=100)
    unity_measure = models.CharField(max_length=100)
    idInstrument = models.ForeignKey('Instrument', db_column='id_instrument')
    
    class Meta:
        verbose_name_plural='Parameters'
        db_table='parameter'
    def __unicode__(self):
        return self.name
    
class Protocol_has_Parameter_value(models.Model):
    idProtocol = models.ForeignKey('ScanProtocol', db_column='id_protocol')
    idParameter = models.ForeignKey('Parameter', db_column='id_parameter')
    value = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural='Parameters Values'
        db_table='parameter_values'
    def __unicode__(self):
        return u"parameter: %s | value:%s" % (self.idParameter, self.value)

 

##### Expriments

class Experiment(models.Model):
    title = models.CharField(max_length=100) 
    description = models.CharField(max_length=255, blank= True) 
    link = models.CharField(max_length=100, blank = True, null = True)

    class Meta:
        db_table = 'experiment'
    def __unicode__(self):
        return u"%s %s" % (self.title, self.description)

class SampleExperiment (models.Model):
    idExperiment = models.ForeignKey ('Experiment', db_column='experiment_id')
    idSample = models.ForeignKey ('Assignment_has_Scan', db_column='sampleexp_id')
    replicates = models.IntegerField()

    class Meta:
        db_table = 'sample_experiment'
    


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


