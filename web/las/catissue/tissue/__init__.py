from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.contrib import auth
from django.template.context import RequestContext
from catissue.tissue.forms import *
from catissue.tissue.models import *
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import string,cStringIO,csv,os,ast,re,datetime,math,xlwt,time,shutil
import operator,random,requests,tarfile
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.conf import settings
from catissue.tissue.mw import threadlocals
from catissue.tissue.genealogyID import *
from catissue.LASAuth.decorators import laslogin_required
from django.contrib.auth.decorators import user_passes_test
from itertools import chain
from django.core.mail import send_mail, EmailMultiAlternatives
from catissue.apisecurity.decorators import *
from catissue.global_request_middleware import *
from genomicAnalysis import *
from lasEmail import *
import django.utils.html as duh
from django.utils import timezone
#import ho.pisa as pisa
from xhtml2pdf import pisa

class ErrorDerived(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class ErrorTypeDerived(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class ErrorDerivedAliquotPresent(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class ErrorFloatValue(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ErrorRevalue(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ErrorPositionStoredPlate(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class ErrorVolumePresent(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class ErrorVolumeQuantit(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class ErrorHistoric(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

#per creare il PDF
def PDFMaker(request, nameFile, template, list_report):
    file_data = render_to_string(template, {'list_report': list_report,}, RequestContext(request))
    myfile = cStringIO.StringIO()
    pisa.CreatePDF(file_data, myfile)
    myfile.seek(0)
    response =  HttpResponse(myfile, mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + nameFile
    return response
