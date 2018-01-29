from django.db import models
from django.contrib.auth.models import User,Permission
from mongoengine import *
import datetime
from django.conf import settings

# Create your models here.


class Member(models.Model):
    class Meta:
        permissions = (
            ("can_view_upload_request", "Can view upload request")
        )


class WebService(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = 'webservice'
        db_table = 'webservice'

    def __unicode__(self):
        return self.name

class Urls(models.Model):
    url = models.CharField(max_length = 255, unique=True,db_column='url')
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


#################################################
# MONGODB                               
#################################################

class RepData(Document):
    name = StringField(max_length=100)
    resource = FileField()
    created = DateTimeField(default=datetime.datetime.now)
    owner = StringField(max_length=100)
    extension = StringField(max_length=20)
    genealogy = StringField(max_length=100)
        
    def __unicode__(self):
        return str(self.name) + ' created at ' + str(self.created) + ' by ' + str(self.owner)
    
    meta = {
        'ordering': ['-created'],
        'allow_inheritance': False,
    }


class UArrayChip(Document):
    barcode = StringField(max_length=100)
    hybevent = StringField(max_length=10)
    scan = StringField(max_length=10)
    sources = ListField(ReferenceField('RepData'))

    meta = {
        'allow_inheritance': False,
        'indexes': ['barcode']
    }    

class UArraySample(Document):
    genid = StringField(max_length=100)
    sources = ListField(ReferenceField('RepData', dbref=False))
    chip = ReferenceField('UArrayChip', dbref=False)
    position = StringField(max_length=100)
    expression = DictField()
    detection = DictField()
    imputed = ListField(StringField(max_length=100))
    
    meta = {
        'allow_inheritance': False,
        'indexes': ['genid']
    }

class Experiment(Document):
    experiment_type = StringField(max_length=100)
    sources = ListField(ReferenceField('RepData',dbref=False))

    meta = {
        'allow_inheritance': False,
    }



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
