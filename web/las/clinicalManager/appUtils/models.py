from django.db import models
from django.conf import settings

class Urls(models.Model):
    _url = models.CharField(max_length = 45,db_column='url')
    idWebService = models.ForeignKey('WebService', db_column='idWebService',null=True,blank=True)
    class Meta:
        verbose_name_plural = 'urls'
        db_table = 'url'
    @property
    def url(self):
        if str(self._url).startswith('http'):
            return self._url
        else:
            return settings.DOMAIN_URL+self._url
    def __unicode__(self):
        return self.url
    
class WebService(models.Model):
    name = models.CharField(max_length=45)
   
    class Meta:
        verbose_name_plural = 'Web Services'
        db_table = 'webService'

    def __unicode__(self):
        return self.name
