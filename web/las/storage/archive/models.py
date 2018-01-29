from django.db import models
from archive.mw import threadlocals
from django.contrib.auth.models import User
import audit
from django.contrib.auth.models import Permission
from django.conf import settings

def getUsername(instance):
    return threadlocals.get_current_user()

class WG(models.Model):
    name= models.CharField(max_length=40)
    users = models.ManyToManyField(User, through="WG_User")
    owner= models.ForeignKey(User,related_name="owner_wg_set")
    class Meta:
        db_table= "storage_wg"

class WG_User(models.Model):
    WG=models.ForeignKey(WG)
    user=models.ForeignKey(User)
    permission=models.ForeignKey(Permission,blank=True, null=True)
    class Meta:
        unique_together = ("WG","user","permission")
        db_table= "storage_wg_user"

class Aliquot (models.Model):
    genealogyID = models.CharField('Genealogy ID',max_length=30)
    idContainer = models.ForeignKey('Container', db_column='idContainer',verbose_name='Container',null=True, blank=True)
    position = models.CharField(max_length = 10,null=True, blank=True)
    startTimestamp=models.DateTimeField('Start Timestamp',blank=True,null=True)
    endTimestamp=models.DateTimeField('End Timestamp',blank=True,null=True)
    startOperator=models.ForeignKey(User, db_column='startOperator',related_name='startOper',verbose_name='Start Operator',blank=True,null=True)
    endOperator=models.ForeignKey(User, db_column='endOperator',related_name='endOper',verbose_name='End Operator',blank=True,null=True)
    
    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername),))
    
    class Meta:
        verbose_name_plural = 'aliquots'
        db_table = 'aliquot'
    def __unicode__(self):
        return self.genealogyID+' is in '+str(self.idContainer)+' '+self.position

class CurrentAliquot (models.Model):
    genealogyID = models.CharField('Genealogy ID',max_length=30)
    idContainer = models.ForeignKey('Container', db_column='idContainer',verbose_name='Container',null=True, blank=True)
    position = models.CharField(max_length = 10,null=True, blank=True)
    startTimestamp=models.DateTimeField('Start Timestamp',blank=True,null=True)
    endTimestamp=models.DateTimeField('End Timestamp',blank=True,null=True)
    startOperator=models.ForeignKey(User, db_column='startOperator',related_name='startOpe',verbose_name='Start Operator',blank=True,null=True)
    endOperator=models.ForeignKey(User, db_column='endOperator',related_name='endOpe',verbose_name='End Operator',blank=True,null=True)

    #history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername),))

    class Meta:
        verbose_name_plural = 'aliquots'
        db_table = 'currentaliquot'
    def __unicode__(self):
        return self.genealogyID+' is in '+str(self.idContainer)+' '+self.position

class Geometry (models.Model):
    name = models.CharField(max_length = 45)
    rules = models.TextField()
    class Meta:
        verbose_name_plural = 'geometry'
        db_table = 'geometry'
    def __unicode__(self):
        return self.name

class ContainerType (models.Model):
    idGenericContainerType = models.ForeignKey('GenericContainerType', db_column='idGenericContainerType', verbose_name='Generic Container Type',blank=True,null=True)
    #nome che viene usato per scopi interni all'applicazione
    name = models.CharField(max_length = 50, unique = True)
    #nome che viene fatto vedere all'utente
    actualName = models.CharField(max_length = 50)
    maxPosition = models.IntegerField('Max Position',null=True,blank=True)
    catalogNumber=models.CharField(max_length = 50,null=True,blank=True)
    producer=models.CharField(max_length = 50,null=True,blank=True)
    #lotNumber=models.CharField(max_length = 50,null=True,blank=True)
    linkFile=models.CharField(max_length = 100,null=True,blank=True)
    idGeometry=models.ForeignKey('Geometry', db_column='idGeometry', verbose_name='Geometry',blank=True,null=True)
    oneUse = models.BooleanField()
    class Meta:
        verbose_name_plural = 'containerType'
        db_table = 'containertype'
    def __unicode__(self):
        return self.actualName

class Container (models.Model):
    idContainerType = models.ForeignKey(ContainerType, db_column='idContainerType',verbose_name='Container Type')
    idFatherContainer = models.ForeignKey('self', db_column='idFatherContainer',verbose_name='Father Container', null = True,blank=True)    
    idGeometry = models.ForeignKey(Geometry, db_column='idGeometry', verbose_name='Geometry',null=True,blank=True)
    position = models.CharField(max_length = 10,null=True, blank=True)
    barcode = models.CharField(max_length = 45, unique=True)
    availability = models.BooleanField()
    full = models.BooleanField(default = False)
    owner = models.CharField(max_length = 45, null=True, blank=True)
    present = models.BooleanField(default = True)
    oneUse = models.BooleanField()
    
    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername),))
    
    class Meta:
        verbose_name_plural = 'container'
        db_table = 'container'
    def __unicode__(self):
        return self.barcode
    
class ContainerAudit (models.Model):
    idContainerType = models.ForeignKey(ContainerType, db_column='idContainerType',verbose_name='Container Type')
    idFatherContainer = models.ForeignKey('self', db_column='idFatherContainer',verbose_name='Father Container', null = True,blank=True)    
    idGeometry = models.ForeignKey(Geometry, db_column='idGeometry', verbose_name='Geometry',null=True,blank=True)
    position = models.CharField(max_length = 10,null=True, blank=True)
    barcode = models.CharField(max_length = 45, unique=True)
    availability = models.BooleanField()
    full = models.BooleanField(default = False)
    owner = models.CharField(max_length = 45, null=True, blank=True)
    present = models.BooleanField(default = True)
    oneUse = models.BooleanField()
    username = models.CharField(blank=True,null=True)
    _audit_timestamp=models.DateTimeField(blank=True,null=True)
    _audit_change_type=models.CharField(blank=True,null=True)
    
    class Meta:
        verbose_name_plural = 'container_audit'
        db_table = 'container_audit'
    def __unicode__(self):
        return self.barcode

class ContTypeHasContType (models.Model):
    idContainer = models.ForeignKey('ContainerType', db_column='idContainer',related_name='id_container', verbose_name='Container', null = True,blank=True)
    idContained = models.ForeignKey('ContainerType', db_column='idContained',related_name='id_contained', verbose_name='Content', null = True,blank=True)
    class Meta:
        verbose_name_plural = 'containerTypeHasContainerType'
        db_table = 'conttypehasconttype'
    def __unicode__(self):
        return str(self.idContained)+' is in '+str(self.idContainer)

class Feature (models.Model):
    name = models.CharField(max_length = 45)
    class Meta:
        verbose_name_plural = 'feature'
        db_table = 'feature'
    def __unicode__(self):
        return self.name

class ContainerFeature (models.Model):
    idFeature = models.ForeignKey(Feature, db_column='idFeature',verbose_name='Feature')
    idContainer = models.ForeignKey(Container, db_column='idContainer',verbose_name='Container')
    value = models.CharField(max_length = 45)
    class Meta:
        verbose_name_plural = 'containerFeature'
        db_table = 'containerfeature'
    def __unicode__(self):
        return self.value

class GenericContainerType (models.Model):
    name = models.CharField(max_length = 45)
    abbreviation = models.CharField(max_length = 10)
    class Meta:
        verbose_name_plural = 'Generic container types'
        db_table = 'genericcontainertype'
    def __unicode__(self):
        return self.name

class Request (models.Model):
    date = models.DateField()
    operator = models.CharField(max_length = 45)
    class Meta:
        verbose_name_plural = 'request'
        db_table = 'request'
    def __unicode__(self):
        return self.value

class ContainerRequest (models.Model):
    idRequest = models.ForeignKey(Request, db_column='idRequest',verbose_name='Request')
    idContainer = models.ForeignKey(Container, db_column='idContainer',verbose_name='Container')
    executed = models.BooleanField()
    class Meta:
        verbose_name_plural = 'containerRequest'
        db_table = 'containerrequest'

class Output (models.Model):
    idRequest = models.ForeignKey(Request, db_column='idRequest',verbose_name='Request')
    date = models.DateField()
    operator = models.CharField(max_length = 45)
    class Meta:
        verbose_name_plural = 'output'
        db_table = 'output'

class ContainerOutput (models.Model):
    idOutput = models.ForeignKey(Output, db_column='idOutput',verbose_name='Output')
    idContainer = models.ForeignKey(Container, db_column='idContainer',verbose_name='Container')
    class Meta:
        verbose_name_plural = 'containerOutput'
        db_table = 'containeroutput'

class Input (models.Model):
    date = models.DateField()
    operator = models.CharField(max_length = 45)
    class Meta:
        verbose_name_plural = 'input'
        db_table = 'input'

class ContainerInput (models.Model):
    idContainer = models.ForeignKey(Container, db_column='idContainer',verbose_name='Container')
    idInput = models.ForeignKey(Input, db_column='idInput',verbose_name='Input')
    class Meta:
        verbose_name_plural = 'containerInput'
        db_table = 'containerinput'

class ContainerTypeFeature (models.Model):
    idFeature = models.ForeignKey(Feature, db_column='idFeature',verbose_name='Feature')
    idContainerType = models.ForeignKey(ContainerType, db_column='idContainerType',verbose_name='Container Type')
    class Meta:
        verbose_name_plural = 'containerTypeFeature'
        db_table = 'containertypefeature'
        
class Urls(models.Model):
    _url = models.CharField(max_length = 60, unique=True,db_column='url')
    default = models.BooleanField()
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
    
class DefaultValue(models.Model):
    abbreviation=models.CharField(max_length=5, blank=True)
    longName=models.CharField(max_length=20,verbose_name='Long Name')
    class Meta:
        verbose_name_plural='Default values'
        db_table='defaultvalue'
    def __unicode__(self):
        return self.longName    
    
class FeatureDefaultValue (models.Model):
    idFeature = models.ForeignKey(Feature, db_column='idFeature',verbose_name='Feature')
    idDefaultValue = models.ForeignKey(DefaultValue, db_column='idDefaultValue',verbose_name='Default Value')
    class Meta:
        verbose_name_plural = 'Feature Default Values'
        db_table = 'featuredefaultvalue'
    def __unicode__(self):
        return str(self.idFeature)+' '+str(self.idDefaultValue)
    
class Member(models.Model):
    class Meta:
        permissions = (
            ("can_view_insert_new_container_type", "Insert New Container Type"),
            ("can_view_insert_new_container_instance", "Insert New Container Instance"),
            ("can_view_change_plate_status", "Change Plate Status"),
            ("can_view_archive_aliquots", "Archive Aliquots"),
            ("can_view_move_aliquots", "Move Aliquots"),
            ("can_view_return_aliquots", "Return Aliquots"),
        )
