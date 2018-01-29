#!/usr/bin/python

# Set up the Django Enviroment
import sys
sys.path.append('/srv/www/caquery/')
from django.core.management import setup_environ 
import settings 
setup_environ(settings)

import urllib, urllib2
from _caQuery.models import Button
from django.core.mail import EmailMessage
import json 
from _caQuery.genealogyID import *
import os
from datetime import datetime
from datetime import timedelta

def ghostmice_experimental():

    period_start = datetime.strftime(datetime.now() - timedelta(days=21), '%Y-%m-%d')

    url_mice = Button.objects.get(name="Mice").query_api_url
    url_qual = Button.objects.get(name="Qual. Measures").query_api_url
    url_quant = Button.objects.get(name="Quant. Measures").query_api_url
    url_implants = Button.objects.get(name="Implants").query_api_url

    print ":----------------------------------------:"
    print ": Ghost mice (experimental)              :"
    print ":----------------------------------------:"

    # retrieve implants performed in last period
    print "Retrieving implants performed after %s" % period_start
    values_to_send = {'predecessor': 'start', 'parameter': 'Date', 'list': '', 'values': '>_' + period_start, 'successor': 'Mice'}
    data = urllib.urlencode(values_to_send)
    try:
        u = urllib2.urlopen(url_implants, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url_implants)   
    res = u.read()
    young_implants = json.loads(res)

    print len(young_implants['id']), "implants"

    # retrieve corresponding mice
    print "Retrieving corresponding mice"

    values_to_send = {'predecessor': 'Implants', 'parameter': 'Status', 'list': {'id': young_implants['id']}, 'values': 'Implanted|Ready For Explant|toSacrifice|waste', 'successor': 'Mice'}
    data = urllib.urlencode(values_to_send)
    try:
        u = urllib2.urlopen(url_mice, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url_mice)   
    res = u.read()
    young_mice = json.loads(res)
    
    print len(young_mice['id']), "mice"

    # retrieve all mice with status in (implanted, ready for explant, to sacrifice)
    print "Retrieving all mice with status implanted, ready for explant or to sacrifice"
    values_to_send = {'predecessor': 'start', 'parameter': 'Status', 'list': '', 'values': 'Implanted|Ready For Explant|toSacrifice|waste', 'successor': 'Mice'}
    data = urllib.urlencode(values_to_send)
    try:
        u = urllib2.urlopen(url_mice, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url_mice)   
    res = u.read()
    mice_with_status = json.loads(res)
    
    print len(mice_with_status['id']), "mice"

    # retrieve qual. measures in last period
    print "Retrieving qual. measures after %s" % period_start
    values_to_send = {'predecessor': 'start', 'parameter': 'Date', 'list': '', 'values': '>_' + period_start, 'successor': 'Mice'}
    data = urllib.urlencode(values_to_send)
    try:
        u = urllib2.urlopen(url_qual, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url_qual)   
    res = u.read()
    qual_measures = json.loads(res)
    print len(qual_measures['id']), "qual. measures"

    # retrieve corresponding mice
    print "Retrieving corresponding mice"
    values_to_send = {'predecessor': 'Qual. Measures', 'parameter': '', 'list': {'id': qual_measures['id']}, 'values': '', 'successor': 'Mice'}
    data = urllib.urlencode(values_to_send)
    try:
        u = urllib2.urlopen(url_mice, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url_mice)   
    res = u.read()
    qual_mice = json.loads(res)
    print len(qual_mice['id']), "mice with qual. measures"

    # retrieve quant. measures in last period
    print "Retrieving quant. measures after %s" % period_start
    values_to_send = {'predecessor': 'start', 'parameter': 'Date', 'list': '', 'values': '>_' + period_start, 'successor': 'Mice'}
    data = urllib.urlencode(values_to_send)
    try:
        u = urllib2.urlopen(url_quant, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url_quant)   
    res = u.read()
    quant_measures = json.loads(res)
    print len(quant_measures['id']), "quant. measures"    

    # retrieve corresponding mice
    print "Retrieving corresponding mice"
    values_to_send = {'predecessor': 'Quant. Measures', 'parameter': '', 'list': {'id': quant_measures['id']}, 'values': '', 'successor': 'Mice'}
    data = urllib.urlencode(values_to_send)
    try:
        u = urllib2.urlopen(url_mice, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url_mice)   
    res = u.read()
    quant_mice = json.loads(res)
    print len(quant_mice['id']), "mice with quant. measures"

    mice_to_exclude = set(qual_mice['id'] + quant_mice['id'] + young_mice['id'])

    mice_ids = list(set(mice_with_status['id']).difference(mice_to_exclude))

    print ""
    print len(mice_ids), "ghost mice (experimental) found"
    print ""
    
    if len(mice_ids) > 0:
        # retrieve mice data
        print "Retrieving additional mice data"
        
        # mice (genid, barcode, exp. group, status)
        values_to_send = {'predecessor': 'Mice', 'parameter': '', 'list': {'id': mice_ids}, 'values': '', 'successor': 'End'}
        data = urllib.urlencode(values_to_send)
        try:
            u = urllib2.urlopen(url_mice, data)
        except:
            print "An error occurred while trying to retrieve data from "+str(url_mice)   
        res = u.read()

        mice = json.loads(res)['objects']
        
        ghostmice = []
        for x in mice:
            genid = x['id_genealogy']
            barcode = x['phys_mouse_id']
            exp_group = x['id_group']
            status = x['status']
            
            # implant (date)
            values_to_send = {'predecessor': 'Mice', 'parameter': '', 'list': {'id': [x['id']]}, 'values': '', 'successor': 'End'}
            data = urllib.urlencode(values_to_send)
            try:
                u = urllib2.urlopen(url_implants, data)
            except:
                print "An error occurred while trying to retrieve data from "+str(url_implants)   
            res = u.read()
            
            implant_date = json.loads(res)['objects'][0]['date']

            # qual. measures
            values_to_send = {'predecessor': 'Mice', 'parameter': '', 'list': {'id': [x['id']]}, 'values': '', 'successor': 'End'}
            data = urllib.urlencode(values_to_send)
            try:
                u = urllib2.urlopen(url_qual, data)
            except:
                print "An error occurred while trying to retrieve data from "+str(url_qual)   
            res = u.read()
            try:
                qual_measures = json.loads(res)['objects']
            except:
                qual_measures = []

            if len(qual_measures) > 0:
                max_qual_date = max([y['date'] for y in qual_measures])
            else:
                max_qual_date = ''

            # quant. measures
            values_to_send = {'predecessor': 'Mice', 'parameter': '', 'list': {'id': [x['id']]}, 'values': '', 'successor': 'End'}
            data = urllib.urlencode(values_to_send)
            try:
                u = urllib2.urlopen(url_quant, data)
            except:
                print "An error occurred while trying to retrieve data from "+str(url_quant)   
            res = u.read()
            try:
                quant_measures = json.loads(res)['objects']
            except:
                quant_measures = []
            
            if len(quant_measures) > 0:
                max_quant_date = max([y['date'] for y in quant_measures])
            else:
                max_quant_date = ''

            if max_qual_date > max_quant_date:
                last_measure_date = max_qual_date
                last_measure_type = 'Qualitative'
            else:
                last_measure_date = max_quant_date
                last_measure_type = 'Quantitative'

            ghostmice.append((genid, barcode, status, implant_date, exp_group, last_measure_date, last_measure_type))

        headers = ('Genealogy ID', 'Barcode', 'Status', 'Implant date', 'Exp. group', 'Last meas. date', 'Last meas. type')
        return headers, ghostmice

    return (), []

def ghostmice_naive():

    headers = ('Barcode', 'Available date')
    twomonthsago = datetime.strftime(datetime.now() - timedelta(days=60), '%Y-%m-%d')

    url_ghost = Button.objects.get(name="Mice").query_api_url.replace("mice", "ghostmicenaive")

    print ":----------------------------------------:"
    print ": Ghost mice (naive)                     :"
    print ":----------------------------------------:"

    # retrieve mice with status = experimental
    print "Retrieving mice with status experimental and availability date < %s" % twomonthsago
    values_to_send = {'startdate': twomonthsago}
    data = urllib.urlencode(values_to_send)
    try:
        u = urllib2.urlopen(url_ghost, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url_ghost)   
    res = u.read()
    try:
        mice = json.loads(res)['objects']
    except Exception as e:
        print "no mice"
        return headers, []
    try:
        print len(mice), "ghost mice"
        ghostmice = []
        for x in mice:
            barcode = x['barcode']
            avl_date = x['available_date']

            ghostmice.append((barcode, avl_date))

        return headers, ghostmice
    except Exception as e:
        print "Exception: ", str(e)
        return headers, []


          
if __name__=='__main__':
    
    group_list = [(ghostmice_experimental, 'Ghost mice (experimental)', 'Ghost mice - experimental'), (ghostmice_naive, 'Ghost mice (naive)', 'Ghost mice - naive')]
    
    mail_to = []
    mail_bcc = []
    mail_from = ''
    
    for f, subj, firstline in group_list:
        head, data = f()
        body = "\n".join(["\t".join(x) for x in data])
        mail_subject = subj
        mail_body = "%s (%d):\n\n" % (firstline, len(data))
        mail_body = mail_body + body
    
        e = EmailMessage(subject=mail_subject, body=mail_body, from_email=mail_from, to=mail_to, bcc=mail_bcc)
        e.attach(filename=subj + ".las", mimetype = "text/plain", content = '\t'.join(head) + '\n' + body)
        e.send()
        print ""
        print "%s: email sent" % subj
        print ""
    
