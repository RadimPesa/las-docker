# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from LASAuth.decorators import laslogin_required
from apisecurity.decorators import permission_decorator

@laslogin_required
@login_required
@permission_decorator('appEnrollment.can_view_CMM_Case_Report_Form')
def crf(request):
    #return HttpResponse("corePatient...")
    variables = RequestContext(request)
    return render_to_response('corePatient/crf.html',variables)

@laslogin_required
@login_required
@permission_decorator('appEnrollment.can_view_CMM_patient_enrollment')
def enrollment(request):
    #return HttpResponse("corePatient...")
    variables = RequestContext(request)
    return render_to_response('corePatient/enrollment.html',variables)

@laslogin_required
@login_required
@permission_decorator('appEnrollment.can_view_CMM_Enrollment_list')
def enrollmentList(request):
    #return HttpResponse("corePatient...")
    variables = RequestContext(request)
    return render_to_response('corePatient/enrollmentList.html',variables)
