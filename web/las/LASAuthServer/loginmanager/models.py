from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.contrib.sessions.models import Session
import settings
#from django.db.models.signals import post_save

# Create your models here.

class Report(models.Model):
    subject=models.CharField(max_length=100)
    body=models.TextField()

class MenuCat(models.Model):
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name

class LASModule(models.Model):
    name = models.CharField(max_length=128)
    shortname = models.CharField(max_length=30)
    _home_url = models.CharField(max_length=128,db_column='home_url')
    icon_url = models.CharField(max_length=128)
    _logout_url = models.CharField(max_length=128,db_column='logout_url')
    remote_key = models.CharField(max_length=80)
    is_active= models.BooleanField()
    menucat_id = models.ForeignKey("MenuCat", db_column='menucat_id')

    def __unicode__(self):
        return self.name
    
    @property
    def home_url(self):
        if str(self._home_url).startswith('http'):
            return self._home_url
        else:
            return settings.DOMAIN_URL+self._home_url

    @property
    def logout_url(self):
        if str(self._logout_url).startswith('http'):
            return self._logout_url
        else:
            return settings.DOMAIN_URL+self._logout_url



class LASPermission(Permission):
    lasmodule = models.ForeignKey(LASModule)
    report=models.ForeignKey(Report,null=True)    
    def __unicode__(self):
        return self.name


class Activity(models.Model):
    name= models.CharField(max_length=40)
    father_activity=models.ForeignKey("self", null=True)
    laspermissions=models.ManyToManyField(LASPermission,through='Activities_LASPermissions')
    def __unicode__(self):
        return self.name

class Activities_LASPermissions(models.Model):
    activity=models.ForeignKey(Activity)
    laspermission=models.ForeignKey(LASPermission)


class Role(models.Model):
    name= models.CharField(max_length=40)
    potential_activities= models.ManyToManyField(Activity,blank=True,null=True, through='Role_potential_activities')

class Role_potential_activities(models.Model):
    role= models.ForeignKey(Role)
    potential_activities=models.ForeignKey(Activity)


class Affiliation(models.Model):
    companyName = models.CharField(max_length=40)
    department = models.CharField(max_length=40)
    city = models.CharField(max_length=40)
    state = models.CharField(max_length=40)
    zipCode= models.CharField(max_length=10)
    validated = models.BooleanField(default=False)

class LASUser(User):
    modules = models.ManyToManyField(LASModule, through="LASUser_modules")
    roles=models.ManyToManyField(Role,blank=True,null=True, through='LASUser_roles')
    affiliation=models.ManyToManyField(Affiliation,blank=True,null=True,through="LASUser_affiliation")
    #is_principal_investigator=models.BooleanField(default=False) STA NELLE AFFILIAZIONI
    

    def __unicode__(self):
        #return self.user.username
        return self.username

class LASUser_roles(models.Model):
    lasuser = models.ForeignKey(LASUser)
    roles = models.ForeignKey(Role)

class LASUser_affiliation(models.Model):
    lasuser = models.ForeignKey(LASUser)
    affiliation = models.ForeignKey(Affiliation)
    is_principal_investigator =models.BooleanField(default=False)

class LASUser_modules(models.Model):
    lasuser = models.ForeignKey(LASUser)
    lasmodule = models.ForeignKey(LASModule)
    is_superuser = models.BooleanField()

class LASUser_logged_in_module(models.Model):
    lasuser = models.ForeignKey(LASUser)
    lasmodule = models.ForeignKey(LASModule)
    session_key = models.CharField(max_length=40)
    date_time = models.DateTimeField(auto_now=True)
    father_session_key=models.ForeignKey(Session,blank=True,null=True)

    class Meta:
        unique_together = ("lasuser", "lasmodule","father_session_key")
    ''' 
    def delete(self):
        url = self.lasmodule.logout_url
        print "LASauthServer: logout "+url
        if not url.endswith('/'):
            url += '/'
        k = str(self.lasmodule.remote_key)
        app_name = self.lasmodule.shortname
        h = hmac.new(k, k + app_name + self.session_key, hashlib.sha256).hexdigest()
        data = {APP_FIELD_NAME : app_name, SESSION_KEY_FIELD_NAME : self.session_key, HMAC_FIELD_NAME : h}
        req = urllib2.Request(url, urllib.urlencode(data))
        try:
            res = urllib2.urlopen(req)
            print res.read()
        except Exception, e:
            print e
        #print "sloggato da",self.lasmodule.shortname
        super(LASUser_logged_in_module, self).delete()
    '''

class ModuleRequest(models.Model):
    user = models.ForeignKey(LASUser)
    modules = models.ManyToManyField(LASModule)
    status= models.CharField(max_length=40)
    date_time = models.DateTimeField(auto_now=True)
    
class PermissionRequest(models.Model):
    user = models.ForeignKey(LASUser)
    permissions = models.ManyToManyField(LASPermission)
    status= models.CharField(max_length=40)
    date_time = models.DateTimeField(auto_now=True)
        
class TemporaryModules(models.Model):
    user = models.ForeignKey(User)
    modules = models.ManyToManyField(LASModule,blank=True,null=True)
    note=models.CharField(max_length=200)
    
class TemporaryRegistration(models.Model):
    user = models.ForeignKey(User)
    modules = models.ManyToManyField(LASModule,blank=True,null=True)
    note=models.CharField(max_length=200)
    

class PiTemporaryRegistration(models.Model):
    user = models.ForeignKey(User)
    activities = models.ManyToManyField(Activity,blank=True,null=True,through="PiTemporaryRegistration_Activities")


class PiTemporaryRegistration_Activities(models.Model):
    piTemporaryRegistration = models.ForeignKey(PiTemporaryRegistration)
    activity= models.ForeignKey(Activity)

class PotentialSupervisor(models.Model):
    firstname=models.CharField(max_length=40)
    lastname=models.CharField(max_length=40)
    email=models.CharField(max_length=40)

class LASUserTemporaryRegistration(models.Model):
    user = models.ForeignKey(User)
    supervisors = models.ManyToManyField(LASUser,related_name='las_supervisor',blank=True,null=True,through="LASUserTempRegSupervisors")
    potentialSupervisors = models.ManyToManyField(PotentialSupervisor,blank=True,null=True,through="LASUserTempRegPotSupervisors")

class LASUserTempRegSupervisors(models.Model):
    lasUserTemporaryRegistration=models.ForeignKey(LASUserTemporaryRegistration)
    supervisor=models.ForeignKey(LASUser)
    roles = models.ManyToManyField(Role,blank=True,null=True)

class LASUserTempRegPotSupervisors(models.Model):
    lasUserTemporaryRegistration=models.ForeignKey(LASUserTemporaryRegistration)
    potentialSupervisor=models.ForeignKey(PotentialSupervisor)
    roles = models.ManyToManyField(Role,blank=True,null=True)

class WG(models.Model):
    name= models.CharField(max_length=40)
    users = models.ManyToManyField(LASUser, through="WG_lasuser")
    owner= models.ForeignKey(LASUser,related_name="owned_wg_set")

    class Meta:
        unique_together = ("name", "owner")

class WG_lasuser(models.Model):
    WG=models.ForeignKey(WG)
    lasuser=models.ForeignKey(LASUser)
    laspermission=models.ForeignKey(LASPermission)

    class Meta:
        unique_together = ("WG", "lasuser","laspermission")

class LASUser_activities(models.Model):
    lasuser = models.ForeignKey(LASUser)
    activity =models.ForeignKey(Activity)

class WG_lasuser_activities(models.Model):
    WG=models.ForeignKey(WG)
    lasuser=models.ForeignKey(LASUser)
    activity=models.ForeignKey(Activity)

    class Meta:
        unique_together = ("WG", "lasuser","activity")



class LASUser_invite(models.Model):
    lasuser=models.ForeignKey(LASUser)
    WG=models.ForeignKey(WG)
    role=models.ForeignKey(Role)


    class Meta:
        unique_together = ("lasuser", "WG","role")



class LASVideo(models.Model):
    title=models.CharField(max_length=100)
    description=models.CharField(max_length=5000)
    url=models.CharField(max_length=200)
    rank = models.IntegerField()
    activity=models.ForeignKey(Activity, db_column='activity')

    def __unicode__(self):
        return self.title





class DemoRestore(models.Model):
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(blank=True,null=True)



class RecipientRole(models.Model):
    name=models.CharField(max_length=50)


class WG_lasuser_templateMail(models.Model):
    wg_lasuser=models.ForeignKey(WG_lasuser)
    templateMail=models.TextField() #Forzatura, ma mantengo costraint( qua scrivo solo se sopra c'e')
    

class ActivityRequest(models.Model):
    activity=models.ForeignKey(Activity)
    WG=models.ForeignKey(WG)
    lasuser=models.ForeignKey(LASUser)
    timestamp=models.DateTimeField(auto_now=True)




class RelationalTag(models.Model):
    name=models.CharField(max_length=40)

class WG_lasuser_relationalTag(models.Model):
    wg_lasuser=models.ForeignKey(WG_lasuser)
    relationalTag=models.ForeignKey(RelationalTag)


class WG_lasuser_recipient(models.Model):
    wg_lasuser=models.ForeignKey(WG_lasuser)
    recipientList=models.TextField()


class LASStatus(models.Model):
    status = models.BooleanField()

