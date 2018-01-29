from django.db import models
from django.contrib.auth.models import User,Permission
import datetime
from django.conf import settings

# Create your models here.
class Member(models.Model):
    class Meta:
        permissions = (
            ("can_view_AM_randomize_groups", "Randomize Groups"),
            ("can_view_AM_write_formulas", "Write Formulas"),
        )


class Element(models.Model):
    name = models.CharField(max_length=100)
    alias = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'elements'
        db_table = 'element'

    def __unicode__(self):
        return self.name


class Formula(models.Model):
    name = models.CharField(max_length=100)
    expression = models.CharField(max_length=1000)

    class Meta:
        verbose_name_plural = 'formulas'
        db_table = 'formula'

    def __unicode__(self):
        return self.expression


class FormulaHasElement(models.Model):
    element_id = models.ForeignKey(Element, db_column='element_id')
    formula_id = models.ForeignKey(Formula, db_column='formula_id')

    class Meta:
        verbose_name_plural = 'formula_has_elements'
        db_table = 'formula_has_element'

    def __unicode__(self):
        return u"%s - %s" % (self.element_id, self.formula_id)

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

