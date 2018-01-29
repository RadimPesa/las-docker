from cellLine.forms import *
from django.http import HttpResponse, Http404
from django.template import Context
from django.template import RequestContext
from django.template.loader import get_template
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from cellLine.models import *
from cellLine.genealogyID import *
import datetime
from django.utils import simplejson
from LASAuth.decorators import laslogin_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
import webbrowser, os.path

@laslogin_required 
@login_required
def experiment_page(request):
    print 'CLM view: start experiment.experiment_page'
    exp_genID_list_gen = []
    exp_genID_list_num = []
    for c in ExperimentInVitro.objects.order_by('genID'):
        exp_genID_list_gen.append(c.genID)
        exp_genID_list_num.append(c.num_plates)
    exp_genID_list = []
    exp_genID_list = zip(exp_genID_list_gen,exp_genID_list_num)
    return render_to_response('cell_line_experiment/cell_line_experiment.html',{'user': request.user,'exp_genID_list': exp_genID_list, }, context_instance=RequestContext(request))