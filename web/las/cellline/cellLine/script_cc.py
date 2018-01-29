#!/usr/bin/python
# Set up the Django Enviroment
import sys
#sys.path.append('/srv/www/caxeno')
sys.path.append('/home/piero/Documenti/fixingCellLine/trunk')
from django.core.management import setup_environ 
from cellLineManager import settings
import os, cStringIO, string, json, csv, datetime
setup_environ(settings)
from django.contrib.auth import authenticate, login
from django.db import transaction
from cellLine.models import *
from cellLine.genealogyID import *

#@transaction.commit_manually
def readFile(filePath):
    try:
        print 'start'
        now = datetime.date.now()
        print today
        with open(filePath, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t', quotechar='"')
            for row in reader:
                #if len(row[0]) > 0:
                print '#####new loop#####'
                print row
                name = row[0] #+ name_plate
                media = row[1]
                serum = row[2]
                percSerum = row[3]
                percDMSO = row[4]
                suppl = row[5]
                mgml = row[6]
                ugul = row[7]
                ugml = row[8]
                perc = row[9]
                mM = row[10]
                antibiotics = row[11]
                percAntibiotics = row[12]

                cp = Condition_protocol(protocol_name = name, creation_date_time = now)
                #cp.save()
                cc = Condition_configuration(version = 1, condition_protocol_id = cp)
                #cc.save()
                cf = Conditio_feature.objetcs.get()
                chf = Condition_has_feature(value = , condition_feature_id = cf, condition_configuration_id = cc)
                #chf.save()





class Condition_has_feature(models.Model):
    value = models.CharField(max_length=30, null=True, blank=True)
    condition_feature_id = models.ForeignKey(Condition_feature, db_column='condition_feature_id')
    condition_configuration_id = models.ForeignKey('Condition_configuration', db_column='condition_configuration_id')
    start = models.IntegerField() 
    end = models.IntegerField() 



        #transaction.commit()
        print 'cell script: all ok'
    except Exception,e:
        print 'error'
        #transaction.rollback()
        print e
    return
if __name__=='__main__':
    readFile("terreni.csv")