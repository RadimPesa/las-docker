#!/usr/bin/python

# Set up the Django Enviroment
import sys
import site
import os
site.addsitedir('~/.virtualenvs/venvdj1.4/local/lib/python2.7/site-packages')

sys.path.append('/srv/www/caquery/')

activate_env=os.path.expanduser("~/.virtualenvs/venvdj1.4/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

from django.core.management import setup_environ 
import settings 
setup_environ(settings)

import urllib, urllib2
from django.core.mail import EmailMessage
import json 
from _caQuery.genealogyID import *
import os
from datetime import datetime
from datetime import timedelta

GHOST_MICE_EXPERIMENTAL_TEMPLATE_ID = 22
GHOST_MICE_NAIVE_TEMPLATE_ID = 23

def ghostmice_experimental():

    period_start = datetime.strftime(datetime.now() - timedelta(days=21), '%Y-%m-%d')

    url = settings.DOMAIN_URL +  '/mdam/api/runtemplate/'

    print ":----------------------------------------:"
    print ": Ghost mice (experimental)              :"
    print ":----------------------------------------:"

    values_to_send = {'template_id': GHOST_MICE_EXPERIMENTAL_TEMPLATE_ID, 'parameters':json.dumps([{'id':'0', 'values':['Bertotti_WG']},{'id':'1', 'values':['>'+period_start]},{'id':'2', 'values':['>'+period_start]},{'id':'3', 'values':['>'+period_start]}])}
    data = urllib.urlencode(values_to_send)

    try:
        u = urllib2.urlopen(url, data)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from "+str(url)   

    res = u.read()
    result = json.loads(res)

    print ""
    print len(result['body']), "ghost mice (experimental) found"
    print ""
    
    headers = ('Genealogy ID', 'Barcode', 'Status', 'Implant date', 'Exp. group', 'Last meas. date', 'Last meas. type')
    ghostmice = []
    for x in result['body']:
        genid = x[1]
        barcode = x[5]
        exp_group = x[2]
        status = x[9]
        implant_date = x[-1][0][0][5]

        # qual. measures
        if len(x[-1][1]) > 0:
            max_qual_date = max([y[3] for y in x[-1][1]])
        else:
            max_qual_date = ''

        # quant. measures
        if len(x[-1][2]) > 0:
            max_quant_date = max([y[3] for y in x[-1][2]])
        else:
            max_quant_date = ''

        if max_qual_date > max_quant_date:
            last_measure_date = max_qual_date
            last_measure_type = 'Qualitative'
        else:
            last_measure_date = max_quant_date
            last_measure_type = 'Quantitative'

        ghostmice.append((genid, barcode, status, implant_date, exp_group, last_measure_date, last_measure_type))
    
    return headers, ghostmice

def ghostmice_naive():

    twomonthsago = datetime.strftime(datetime.now() - timedelta(days=60), '%Y-%m-%d')

    url = settings.DOMAIN_URL +  '/mdam/api/runtemplate/'

    print ":----------------------------------------:"
    print ": Ghost mice (naive)                     :"
    print ":----------------------------------------:"

    values_to_send = {'template_id': GHOST_MICE_NAIVE_TEMPLATE_ID, 'parameters':json.dumps([{'id':'1', 'values':['<'+twomonthsago]}, {'id':'0', 'values':['Bertotti_WG']}])}
    data = urllib.urlencode(values_to_send)

    try:
        u = urllib2.urlopen(url, data)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from "+str(url)   

    res = u.read()
    result = json.loads(res)

    print ""
    print len(result['body']), "ghost mice (naive) found"
    print ""
    
    headers = ('Barcode', 'Available date')
    ghostmice = []

    for x in result['body']:
        barcode = x[4]
        avl_date = x[3]

        ghostmice.append((barcode, avl_date))

    return headers, ghostmice

          
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
    
