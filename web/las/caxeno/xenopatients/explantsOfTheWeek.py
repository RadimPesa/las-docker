#!/usr/bin/python
# Set up the Django Enviroment
import sys
sys.path.append('/srv/www/caxeno')
from django.core.management import setup_environ 
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

def getExplants():
    try:
        print 'xeno: start script for weekly explants mail'
        print datetime.datetime.today()
        today = datetime.datetime.now()
        date = today - timedelta(days = 6) #o 7?
        #print date
        date = datetime.datetime(date.year, date.month, date.day)
        print date
        series = Series.objects.filter(id_type = Type_of_serie.objects.get(description = 'explant'), date__gte = date )
        mice = []
        print len(series)
        for s in series:
            print s
            explants = Explant_details.objects.filter(id_series = s)
	    print explants
            for e in explants:
                print e
                g = GenealogyID(e.id_mouse.id_genealogy)
                print g.getSamplePassagge()
                if g.getSamplePassagge() == '01':
                    mouse = e.id_mouse.id_genealogy + '|' + str(s.date) + '|' + s.id_operator.username
                    #print mouse
                    mice.append(mouse)
        mice = list(set(mice))
        print len(mice), 'sssssssss'
        try:
            text_content = 'Explants P01 made in the last week:'
            print len(mice)
            text_content += '\n' + str(len(mice)) + ' explanted mice in this week.'
            
            subject, from_email = 'Explants of the week', settings.EMAIL_HOST_USER
            for m in mice:
                data = m.split('|')
                #print data
                text_content = text_content + '\n' + 'Mouse:\t' + data[0] + '\tDate:\t' + data[1] + '\tOperator:\t' + data[2]
            mails = []

            uuser = User.objects.get(username = 'andrea.bertotti')
            mails.append(user.email)
            user = User.objects.get(username = 'francesco.galimi')
            mails.append(user.email)
            print mails
	    print text_content
            msg = EmailMultiAlternatives(subject, text_content, from_email, mails)
            msg.send()
            print 'send'
        except Exception, e:
            print e
            print 'xeno: error mail'
            pass
        print 'xeno script: all ok'
    except Exception,e:
        print 'error'
        print e
        #transaction.rollback()
    return
if __name__=='__main__':
    settings.USE_GRAPH_DB= False
    getExplants()
