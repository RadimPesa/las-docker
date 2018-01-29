from django.db import models
from django.utils.translation import ugettext_lazy as _
from random import randrange
from django.contrib.sessions.models import Session
import hashlib
import os
from datetime import time
from django.conf import settings

MAX_SESSION_KEY = 18446744073709551616L     # 2 << 63

class LASAuthSession(models.Model):
    session_key = models.CharField(max_length=40,primary_key=True,db_column='session_key')
    django_session_key = models.ForeignKey(Session,null=True,db_column='django_session_key')
    login_expire_date = models.DateTimeField(db_index=True,db_column='login_expire_date')
    next_url = models.TextField(db_column='next_url')
    session_open = models.BooleanField(db_column='session_open')


    class Meta:
        db_table = 'las_auth_session'
        verbose_name = 'las_auth_session'
        verbose_name_plural = 'las_auth_sessions'
   
    def generateSessionKey(self):
        try:
            pid = os.getpid()
        except AttributeError:
            # No getpid() in Jython, for example
            pid = 1
        while True:
            session_key = hashlib.md5("%s%s%s%s" % (randrange(0, MAX_SESSION_KEY), pid, time(), settings.SECRET_KEY)).hexdigest()
            try:
                LASAuthSession.objects.get(session_key=session_key)
            except LASAuthSession.DoesNotExist:
                break
        self.session_key = session_key
    
    def __unicode__(self):
        return self.session_key

