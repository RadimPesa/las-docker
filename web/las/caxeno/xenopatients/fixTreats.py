#!/usr/bin/python
# Set up the Django Enviroment
import sys
sys.path.append('/srv/www/caxeno')
#sys.path.append('/home/piero/Documenti/caXeno/trunk/caxeno')
from django.core.management import setup_environ 
#from django.conf import settings 
import settings
setup_environ(settings)
from django.db import transaction
import os, urllib, urllib2, cStringIO, string, json
from xenopatients.models import *
from xenopatients.genealogyID import *
from datetime import date, timedelta
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.http import *
from django.contrib.sessions.middleware import *
from django.contrib.auth.middleware import *
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models import Count

@transaction.commit_manually
def fixTreats():
    try:
        print 'xeno: start fixing treats'
        print datetime.datetime.now()
        mhaList = Mice_has_arms.objects.all().values('id_mouse').annotate(count=Count('id_mouse')).filter(count__gte=2)
        for mha in mhaList:
            treats = Mice_has_arms.objects.filter(id_mouse = Mice.objects.get(id = mha['id_mouse'])).order_by('id')
            if len(treats) == 2:
                if treats[0].end_date != None and treats[1].start_date != None:
                    if treats[0].end_date > treats[1].start_date:
                        print '2'
                        print str(treats[0].end_date), ">", str(treats[1].start_date)
                        treats[0].end_date = treats[1].start_date
                        treats[0].save()
            if len(treats) == 3:
                if treats[0].end_date != None and treats[1].start_date != None and treats[1].end_date != None and treats[2].start_date != None:
                    print '333333', mha['id_mouse']
                    if treats[0].end_date > treats[1].start_date:
                        print str(treats[0].end_date), ">", str(treats[1].start_date)
                        treats[0].end_date = treats[1].start_date
                        treats[0].save()
                    if treats[1].end_date > treats[2].start_date:
                        print str(treats[1].end_date), ">", str(treats[2].start_date)
                        treats[1].end_date = treats[2].start_date
                        treats[1].save()
        transaction.commit()
    except Exception,e:
        print 'error'
        print e
        transaction.rollback()
    return

@transaction.commit_manually
def fixGenID():
    try:
        print 'xeno: start fixing genID'
        print datetime.datetime.now()

        for m in BioMice.objects.all():
            string=' '.join(m.id_genealogy.split())
            #print len(string),m.id_genealogy

            if len(string) == 26:
               gen = GenealogyID(m.id_genealogy)
               #print m.id_genealogy, gen.getTissueType()
               if gen.getTissueType() == '000':
                   if len(Implant_details.objects.filter(id_mouse = m)) > 0:
                       ids = Implant_details.objects.get(id_mouse = m)

                       gen.updateGenID({'tissueType':ids.site.shortName})
                       print string, gen.getGenID()
                       m.id_genealogy = gen.getGenID()
                       m.save()
            transaction.commit()
        print 'ok'
    except Exception,e:
        print 'error'
        print e
        transaction.rollback()
    return


if __name__=='__main__':
    fixGenID()
