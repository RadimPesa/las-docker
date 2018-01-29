from django.shortcuts import render_to_response
from loginmanager.forms import *
from loginmanager.models import *
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.template import RequestContext
import urllib
import urllib2
import hashlib
import hmac
import json
from django.contrib.auth.models import User,Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.core.exceptions import PermissionDenied
from apisecurity.decorators import required_parameters
from registration.backends import get_backend
from registration.models import RegistrationProfile
from apisecurity.apikey import *
from django.core.mail import EmailMessage
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from xhtml2pdf import pisa
from django.template.loader import render_to_string
import cStringIO as StringIO
import cgi
import os
import xlwt
from django.forms.models import model_to_dict
from py2neo import *

from views_mercuric import *
