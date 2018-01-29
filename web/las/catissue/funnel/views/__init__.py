from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext
from catissue.tissue.models import *
from django.contrib import auth
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings

import urllib,urllib2,json,ast,requests
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from sets import Set
from django.db import transaction, connection
from catissue.LASAuth.decorators import laslogin_required
from multiprocessing import Process, Queue
import csv
import itertools
import urlparse
import re
import os
import sys

import zlib
from django.views.decorators.gzip import gzip_page
from copy import deepcopy 

from catissue.global_request_middleware import *
from catissue.apisecurity.decorators import *

from catissue.funnel.forms import *
from catissue.tissue.utils import *
from catissue.api.handlers import CheckPatientHandler
from views_funnel import *

class ErrorDerived(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)