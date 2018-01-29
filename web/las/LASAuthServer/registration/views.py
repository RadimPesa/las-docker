
#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""
Class based views for django-inspectional-registration


CLASSES:

    RegistrationCompleteView
        Class based registracion complete view

    RegistrationClosedView
        Class based registration closed view which
        is called when REGISTRATION_OPEN is ``False``

    ActivationCompleteView
        Class based activation complete view

    ActivationView
        Class based activation view. GET for displaying activation form and
        POST for activation

    RegistrationView
        Class based registration view. GET for displaying

AUTHOR:
    lambdalisue[Ali su ae] (lambdalisue@hashnote.net)

Copyright:
    Copyright 2011 Alisue allright reserved.

License:
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unliss required by applicable law or agreed to in writing, software
    distributed under the License is distrubuted on an "AS IS" BASICS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
__AUTHOR__ = "lambdalisue (lambdalisue@hashnote.net)"
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView
from django.views.generic.edit import FormMixin
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.utils.text import ugettext_lazy as _

from backends import get_backend
from models import RegistrationProfile, RegistrationSession


from django.shortcuts import render_to_response
from django.template import RequestContext
from loginmanager.models import *
from django.http import HttpResponse, HttpResponseRedirect
import json
from django.contrib.auth.models import User
from loginmanager.models import PiTemporaryRegistration, WG
from loginmanager.models import LASModule
#from django.core.mail import EmailMessage
from emails import *
from django.conf import settings
from django.db import transaction
from django.utils import simplejson

from py2neo import *
import urllib, urllib2
from django.contrib.auth.decorators import login_required

import string, random # password generation
from registration.forms import CaptchaForm

from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url


class RegistrationCompleteView(TemplateView):
    """A simple template view for registration complete"""
    template_name = r'registration/registration_complete.html'
    def render_to_response(self, context, **response_kwargs):
        reg_session_id = self.request.COOKIES.get('reg_session', None)
        if reg_session_id is not None:
            RegistrationSession.objects.get(captcha_key=reg_session_id).delete()
        response = super(RegistrationCompleteView, self).render_to_response(context, **response_kwargs)
        response.delete_cookie("reg_session")
        return response

class RegistrationClosedView(TemplateView):
    """A simple template view for registraion closed

    This view is called when user accessed to RegistrationView
    with REGISTRATION_OPEN = False
    """
    template_name = r'registration/registration_closed.html'

class ActivationCompleteView(TemplateView):
    """A simple template view for activation complete"""
    template_name = r'registration/activation_complete.html'

class RegistrationErrorView(TemplateView):
    """A simple template view for registration errors"""
    template_name = r'registration/registration_error.html'

class ActivationView(TemplateResponseMixin, FormMixin, SingleObjectMixin, ProcessFormView):
    """A complex view for activation

    GET:
        Display an ActivationForm which has ``password1`` and ``password2``
        for activation user who has ``activation_key``
        ``password1`` and ``password2`` should be equal to prepend typo

    POST:
        Activate the user who has ``activation_key`` with passed ``password1``
    """
    template_name = r'registration/activation_form.html'
    model = RegistrationProfile

    def __init__(self, *args, **kwargs):
        self.backend = get_backend()
        super(ActivationView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        """get ``RegistrationProfile`` queryset which status is 'accepted'"""
        return self.model.objects.filter(_status='accepted')

    def get_object(self, queryset=None):
        """get ``RegistrationProfile`` instance by ``activation_key``

        ``activation_key`` should be passed by URL
        """
        queryset = queryset or self.get_queryset()
        try:
            obj = queryset.get(activation_key=self.kwargs['activation_key'])
            if obj.activation_key_expired():
                raise Http404(_('Activation key has expired'))
        except self.model.DoesNotExist:
            raise Http404(_('An invalid activation key has passed'))
        return obj

    def get_success_url(self):
        """get activation complete url via backend"""
        return self.backend.get_activation_complete_url(self.activated_user)

    def get_form_class(self):
        """get activation form class via backend"""
        return self.backend.get_activation_form_class()

    def form_valid(self, form):
        """activate user who has ``activation_key`` with ``password1``

        this method is called when form validation has successed.
        """
        profile = self.get_object()
        password = form.cleaned_data['password1']
        self.activated_user = self.backend.activate(
                profile.activation_key, self.request, password=password)
        return super(ActivationView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        # self.object have to be set
        self.object = self.get_object()
        return super(ActivationView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # self.object have to be set
        self.object = self.get_object()
        return super(ActivationView, self).post(request, *args, **kwargs)



#@transaction.commit_on_success()
#def ExternalProjectRegistration(request,projectName):
#    print projectName
#    affiliation_list=Affiliation.objects.all().values('id','companyName','state','department')
#    return render_to_response('registration/registration_form.html', {'affiliation_list':affiliation_list}, RequestContext(request))


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@transaction.commit_on_success
def LASRegistration(request,projectName=None):
    backend=get_backend()
    if request.method=='POST':
        reg_session_id = request.COOKIES.get('reg_session', None)
        if request.POST.get('step') not in ['data_check', 'demo_register']:
            print "verifying cookie"
            try:
                reg_session = RegistrationSession.objects.get(captcha_key=reg_session_id)
                print "reg_session = ", reg_session.captcha_key
                print "reg_session.is_valid()=", reg_session.is_valid(get_client_ip(request))
                if reg_session.is_valid(get_client_ip(request)) == False:
                    # when the session is not valid, no data will be disclosed, because the next "if ...('step') == ..." statements are not evaluated
                    # the client redirects to an error page
                    # a malicious user may circumvent this, but he will still not be able to proceed
                    return_dict = {"critical_error": 'true'}
                    return HttpResponse(json.dumps(return_dict),mimetype='application/json')
                else:
                    reg_session.reset_expiration()
            except Exception as e:
                print "exception:", str(e)
                return_dict = {"critical_error": 'true'}
                return HttpResponse(json.dumps(return_dict),mimetype='application/json')
        if request.POST.get('step')=='demo_register':
            import urllib, urllib2
            username= request.POST.get('username')
            firstname = request.POST.get('firstname')
            lastname = request.POST.get('lastname')
            email = request.POST.get('email1')
            try:
                new_user = backend.register(username, email , request)
            except Exception,e:
                print e
                transaction.rollback()
                return_dict = {"result": 'mail_error'}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')

            u = User.objects.get(username=username)
            u.first_name=firstname
            u.last_name=lastname
            u.is_active=1
            u.save()
            luser=LASUser(id=u.id,first_name=u.first_name,last_name=u.last_name, username=u.username,email=u.email,is_active=u.is_active)
            luser.save()
            wg=WG(name=u.username+'_WG',owner=luser)
            wg.save()
            if settings.USE_GRAPH_DB==True:
                gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
                if gdb.get_indexed_node('node_auto_index','identifier',str(wg.name)):
                    print "nodo WG esistente"
                else:
                    print "aggiungo WG al grafo"
                    new_node,=gdb.create({"identifier":str(wg.name)})
                    new_node.add_labels("Social","WG")
            wgDemo=WG.objects.get(name='LASDemo_WG')
            for permission in LASPermission.objects.all():
                try:
                    wg_user=WG_lasuser.objects.get(WG=wg,lasuser=luser,laspermission=permission)
                except:
                    wg_user=WG_lasuser(WG=wg,lasuser=luser,laspermission=permission)
                    wg_user.save()
                if permission.codename !='can_view_LAS_manage_working_groups':
                    try:
                        wg_user=WG_lasuser.objects.get(WG=wgDemo,lasuser=luser,laspermission=permission)
                    except:
                        wg_user=WG_lasuser(WG=wgDemo,lasuser=luser,laspermission=permission)
                        wg_user.save()

                #INVIARE A TUTTI I MOD--API CREATE WG
                perm=Permission.objects.get(codename=permission.codename)
                user=User.objects.get(username=luser.username)
                if (user.has_perm("loginmanager."+perm.codename)==False):
                    user.user_permissions.add(perm)
            for act in Activity.objects.all():
                try:
                    lasuserAct=WG_lasuser_activities.objects.get(WG=wg,lasuser=luser,activity=act)
                except Exception,e:
                    lasuserAct=WG_lasuser_activities(WG=wg,lasuser=luser,activity=act)
                    lasuserAct.save()

            for lasmodule in LASModule.objects.all():
                if lasmodule.name!='LASAuthServer':
                    address=lasmodule.home_url
                    url = address+"permission/addDemoUser/"
                    #t = getApiKey()
                    print url
                    values = {'wg':wg.name,'api_key':'','user':luser.username,'firstname':luser.first_name,'last_name':luser.last_name,'email':luser.email}
                    data = urllib.urlencode(values,True)
                    try:
                        resp=urllib2.urlopen(url, data)
                        res1 =  resp.read()
                    except Exception, e:
                        print 'Eccezione in salvataggio DEMO USER 1)',e
                        transaction.rollback()
                        return False
                lm=LASUser_modules(lasuser=luser,lasmodule=lasmodule)
                lm.save()
            #FARE API AI MODULI MODIFICATA.
            profile= RegistrationProfile.objects.get(user_id=luser.id)
            backend.accept(profile, request=request)
            return_dict = {"result": 'end'}
            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json')

        elif request.POST.get('step')=='data_check':

            #controllo dati
            #USERNAME,MAIL CON REGEX,NOME COGNOME ECC CON REGEX NON VUOTI
            error=False
            error_string='Error!'
            username= request.POST.get('username')
            email=request.POST.get('email1')
            firstname = request.POST.get('firstname')
            lastname = request.POST.get('lastname')

            # validate captcha
            captcha_data = {'captcha_0': request.POST.get('captcha_0'), 'captcha_1': request.POST.get('captcha_1')}
            print "captcha_data: ", captcha_data
            cform = CaptchaForm(captcha_data)
            if cform.is_valid():
                rs = RegistrationSession(captcha_key=captcha_data['captcha_0'],source_ip=get_client_ip(request))
                rs.save()
            else:
                error_string += "\nCaptcha challenge failed, try again"
                error = True
                return_dict = {"critical_error": 'true', "error_string": error_string}
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')

            import re
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError

            try:
                validate_email(email)
            except ValidationError:
                error_string+="\nInvalid mail address!"
                error = True
            if User.objects.filter(username=username).count()>0:
                error=True
                error_string+="\nUsername and/or email are not valid"
            if User.objects.filter(email=email).count()>0:
                error=True
                error_string+="\nUsername and/or email are not valid"
            if error==True:
                return_dict = {"critical_error": 'true', "error_string":error_string}
            else:
                return_dict = {"critical_error": 'false', 'regsession': request.POST.get('captcha_0')}

            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json')

        elif request.POST.get('step')=='search_affiliation':
            if request.POST.get('userType') == 'pi':
                try:
                    if request.POST.get('aff_name')=='' and request.POST.get('aff_state') == '' and request.POST.get('aff_department') == '':
                        affiliations=Affiliation.objects.all()
                    else:
                        if request.POST.get('aff_name') != '':
                            affiliations_name=Affiliation.objects.filter(companyName__icontains=request.POST.get('aff_name'))
                        else:
                            affiliations_name=Affiliation.objects.none()
                        if request.POST.get('aff_state') != '':
                            affiliations_state= Affiliation.objects.filter(state__icontains=request.POST.get('aff_state'))
                        else:
                            affiliations_state=Affiliation.objects.none()
                        if request.POST.get('aff_department') != '':
                            affiliations_department=Affiliation.objects.filter(department__icontains=request.POST.get('aff_department'))
                        else:
                            affiliations_department=Affiliation.objects.none()
                        affiliations=affiliations_name | affiliations_state | affiliations_department
                    affiliationList= list()

                    for a in affiliations:
                        aff={}
                        aff['name']=a.companyName
                        aff['state']=a.state
                        aff['department']=a.department
                        aff['id']=a.id
                        aff['validated']=a.validated
                        affiliationList.append(aff)

                    if affiliations.count()>0:
                        return_dict = {"affiliations": affiliationList}
                    else:
                        return_dict = {"affiliations":"none"}
                except Exception,e:
                    print e
                    return_dict = {"affiliations":"none"}

            elif request.POST.get('userType') == 'user':
                #TROVARE PI
                if request.POST.get('aff_pi_name')=='' and request.POST.get('aff_pi_lastname') == '' and request.POST.get('aff_pi_mail') == '' and request.POST.get('aff_name') == '' and request.POST.get('aff_state') == '' and request.POST.get('aff_department') =='':
                    pi_list=LASUser_affiliation.objects.filter(is_principal_investigator=1)
                else:
                    if request.POST.get('aff_pi_name') != '':
                        pi_list_name=LASUser_affiliation.objects.filter(lasuser__first_name__icontains=request.POST.get('aff_pi_name'),is_principal_investigator=1,lasuser__is_active=1)
                    else:
                        pi_list_name=LASUser_affiliation.objects.none()
                    if request.POST.get('aff_pi_lastname') != '':
                        pi_list_lastname=LASUser_affiliation.objects.filter(lasuser__last_name__icontains=request.POST.get('aff_pi_lastname'),is_principal_investigator=1,lasuser__is_active=1)
                    else:
                        pi_list_lastname=LASUser_affiliation.objects.none()
                    if request.POST.get('aff_pi_mail') != '':
                        pi_list_mail=LASUser_affiliation.objects.filter(lasuser__email__icontains=request.POST.get('aff_pi_mail'),is_principal_investigator=1,lasuser__is_active=1)
                    else:
                        pi_list_mail=LASUser_affiliation.objects.none()
                    if request.POST.get('aff_name') != '':
                        pi_list_companyName=LASUser_affiliation.objects.filter(affiliation__companyName__icontains=request.POST.get('aff_name'),is_principal_investigator=1,lasuser__is_active=1)
                    else:
                        pi_list_companyName=LASUser_affiliation.objects.none()
                    if request.POST.get('aff_state') != '':
                        pi_list_state=LASUser_affiliation.objects.filter(affiliation__state__icontains=request.POST.get('aff_state'),is_principal_investigator=1,lasuser__is_active=1)
                    else:
                        pi_list_state=LASUser_affiliation.objects.none()
                    if request.POST.get('aff_department') != '':
                        pi_list_dept=LASUser_affiliation.objects.filter(affiliation__department__icontains=request.POST.get('aff_department'),is_principal_investigator=1,lasuser__is_active=1)
                    else:
                        pi_list_dept=LASUser_affiliation.objects.none()
                    pi_list= pi_list_name | pi_list_lastname | pi_list_mail | pi_list_companyName | pi_list_state | pi_list_dept
                print request.POST
                if 'project' in request.POST:
                    if request.POST.get('project')!='':
                        pi_list=pi_list.filter(lasuser__username=request.POST.get('project'))
                pi_affiliations=list()
                for p in pi_list:
                    found=False
                    for item in pi_affiliations:
                        if item['supervisorID']==p.lasuser.id:
                            found=True
                            break
                    aff=dict()
                    aff['name']=p.affiliation.companyName
                    aff['state']=p.affiliation.state
                    aff['department']=p.affiliation.department
                    if found==False:
                        pi=dict()
                        pi['firstname']=p.lasuser.first_name
                        pi['lastname']=p.lasuser.last_name
                        pi['id']=p.id
                        pi['supervisorID']=p.lasuser.id
                        pi['affiliations']=list()
                        pi['affiliations'].append(aff)
                        pi_affiliations.append(pi)
                    else:
                        for item in pi_affiliations:
                            if item['supervisorID']==p.lasuser.id:
                                item['affiliations'].append(aff)
                if pi_list.count()>0:
                    return_dict = {"affiliations": pi_affiliations}
                else:
                    return_dict = {"affiliations":"none"}

            return_dict["critical_error"] = 'false'
            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json')

        elif request.POST.get('step')=='check_pi_aff':
            name=request.POST.get('new_name_pi_aff')
            state=request.POST.get('new_state_pi_aff')
            department=request.POST.get('new_department_pi_aff')
            if Affiliation.objects.filter(companyName=name,state=state,department=department).count()>0:
                return_dict = {"msg": 'error'}
            else:
                return_dict = {"msg":"ok"}
            return_dict["critical_error"] = 'false'
            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json')

        elif request.POST.get('step')=='check_lasuser_aff':
            name=request.POST.get('new_pi_name_lasuserAff')
            lastname=request.POST.get('new_pi_lastname_lasuserAff')
            email=request.POST.get('new_pi_mail_lasuserAff')
            if LASUser_affiliation.objects.filter(lasuser__first_name=name,lasuser__last_name=lastname).count()>0 or LASUser_affiliation.objects.filter(lasuser__email=email).count()>0:
                return_dict = {"msg": 'error'}
            else:
                return_dict = {"msg":"ok"}

            return_dict["critical_error"] = 'false'
            json_response = json.dumps(return_dict)
            return HttpResponse(json_response,mimetype='application/json')

        elif request.POST.get('step')=='phase_two':
            if request.POST.get('userType')=='pi':
                if request.POST.get('new_name')!='':
                    new_name = request.POST.get('new_name')
                    new_department = request.POST.get('new_department')
                    new_state = request.POST.get('new_state')
                catlist=list()
                for father_act in Activity.objects.filter(father_activity__isnull=True):
                    cat={}
                    cat['name']=father_act.name
                    cat['id']=father_act.id
                    cat['activities']= list()
                    for act in Activity.objects.filter(father_activity=father_act):
                        activity=dict()
                        activity['name']=act.name
                        activity['id']=act.id
                        cat['activities'].append(activity)
                    catlist.append(cat)
                affiliations=request.POST.getlist('affiliation[]')
                invalid_flag=False
                for a in affiliations:
                    if a=='new_aff':
                        invalid_flag=True
                    else:
                        aff=Affiliation.objects.get(id=a)
                        if aff.validated==False:
                            invalid_flag=True
                #return_dict = {"categories": catlist}
                #json_response = json.dumps(return_dict)
                return render_to_response('registration/registration_form_step2.html', {"categories": catlist,'userType':'pi','username':request.POST.get('username'),'invalid_flag':invalid_flag}, RequestContext(request))
            else:
                if request.POST.get('new_pi_name')!='':
                    new_pi_name = request.POST.get('new_pi_name')
                    new_pi_lastname = request.POST.get('new_pi_lastname')
                    new_pi_mail = request.POST.get('new_pi_mail')
                idList=list()
                supList=list()
                roleList=list()
                affIdList=list()
                supervisorsSet=set()
                for i in request.POST.getlist('affiliation[]'):
                    if i!='new_aff':
                        idList.append(i)
                affiliationsSupervisor=LASUser_affiliation.objects.filter(id__in=idList,is_principal_investigator=1)
                for a in affiliationsSupervisor:
                    if a.lasuser.is_active==1:
                        supervisorsSet.add(a.lasuser)
                roles=Role.objects.all()
                for item in supervisorsSet:
                    sup={}
                    sup['name']=item.lasuser.first_name
                    sup['lastname']= item.lasuser.last_name
                    sup['id']=item.lasuser.id
                    sup['affiliations']=list()
                    print Role_potential_activities.objects.filter(potential_activities_id__in=WG_lasuser_activities.objects.filter(lasuser=item).values_list('activity',flat=True)).values_list('role',flat=True)
                    roles=roles.filter(id__in=Role_potential_activities.objects.filter(potential_activities_id__in=WG_lasuser_activities.objects.filter(lasuser=item).values_list('activity',flat=True)).values_list('role',flat=True)).distinct()
                    print ' filtrato',roles
                    for x in Affiliation.objects.filter(id__in=LASUser_affiliation.objects.filter(lasuser=item,is_principal_investigator=1).values_list('affiliation', flat=True)).distinct():
                        aff={}
                        aff['name']=x.companyName
                        aff['state']=x.state
                        aff['department']=x.department
                        aff['id']=x.id
                        sup['affiliations'].append(aff)
                    supList.append(sup)
                print roles
                for r in roles:
                    rol={}
                    rol['name']=r.name
                    rol['id']=r.id
                    roleList.append(rol)
                if request.POST.get('new_pi_name')!='':
                    sup={}
                    sup['name']=new_pi_name
                    sup['lastname']=new_pi_lastname
                    sup['affiliation']="-"
                    sup['affiliationID']=0
                    sup['affiliationSupervisorID']=0
                    sup['id']=0
                    sup['valid']=False
                    supList.append(sup)
                return render_to_response('registration/registration_form_step2.html', {'supervisor':supList,'roles':roleList,'userType':'user','username':request.POST.get('username')}, RequestContext(request))

        elif request.POST.get('step') == 'register':
            try:
                username= request.POST.get('username')
                firstname = request.POST.get('firstname')
                lastname = request.POST.get('lastname')
                email = request.POST.get('email1')
                if 'wgName' in request.POST:
                    if WG.objects.filter(name=request.POST.get('wgName')).count()>0:
                        return_dict = {"result": 'duplicate'}
                        return_dict["critical_error"] = 'false'
                        json_response = json.dumps(return_dict)
                        return HttpResponse(json_response,mimetype='application/json')
                try:
                    new_user = backend.register(username, email , request)
                except Exception,e:
                    print e
                    transaction.rollback()
                    return_dict = {"result": 'mail_error'}
                    return_dict["critical_error"] = 'false'
                    json_response = json.dumps(return_dict)
                    return HttpResponse(json_response,mimetype='application/json')

                u = User.objects.get(username=username)
                u.first_name=firstname
                u.last_name=lastname
                u.is_active=0
                if settings.DEMO or request.POST.get('project')!='':
                    u.is_active=1
                u.save()
                luser=LASUser(id=u.id,first_name=u.first_name,last_name=u.last_name, username=u.username,email=u.email,is_active=u.is_active)
                luser.save()
                if request.POST.get('userType')=='pi':
                    temp=PiTemporaryRegistration(user=u)
                    temp.save()
                    try:
                        for a in request.POST.getlist('activities[]'):
                            activity=Activity.objects.get(id=a)
                            m2mtemp=PiTemporaryRegistration_Activities(piTemporaryRegistration=temp,activity=activity)
                            m2mtemp.save()
                            #FARE VARIANTE CON SELEZIONE DEI MODULI
                            if WG.objects.filter(name=request.POST.get('wgName'),owner=luser).count()==0:
                                workingGroup=WG(name=request.POST.get('wgName'),owner=luser)
                                workingGroup.save()
                                if settings.USE_GRAPH_DB==True:
                                    gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
                                    if gdb.get_indexed_node('node_auto_index','identifier',str(request.POST.get('wgName'))):
                                        print "nodo WG esistente"
                                    else:
                                        print "aggiungo WG al grafo"
                                        new_node,=gdb.create({"identifier":str(request.POST.get('wgName'))})
                                        new_node.add_labels("Social","WG")

                            '''CARICO PERMESSI ASSOCIATI ALL'UTENTE NELLA TERNA WG-USER-PERM
                            EVENTUALMENTE GLI DO ANCHE IL PERMESSO SULLA SCHERMATA, SE NON CE L'AVEVA
                            (PREVEDERE CHE IN CASO DI REJECT DELLA REGISTRAZIONE SI CANCELLI, SE NON HO PERMESSO PER NESSUN WG!!)'''
                            for activity_permission in Activities_LASPermissions.objects.filter(activity=activity):
                                try:
                                    wg_user=WG_lasuser.objects.get(WG=workingGroup,lasuser=luser,laspermission=activity_permission.laspermission)
                                except:
                                    wg_user=WG_lasuser(WG=workingGroup,lasuser=luser,laspermission=activity_permission.laspermission)
                                    wg_user.save()
                                #INVIARE A TUTTI I MOD--API CREATE WG
                                perm=Permission.objects.get(codename=activity_permission.laspermission.codename)
                                user=User.objects.get(username=luser.username)
                                if (user.has_perm("loginmanager."+perm.codename)==False):
                                    user.user_permissions.add(perm)
                        #LASDEMO
                        if settings.DEMO:

                            result=LASDemo(u,request)
                            if result:
                                return_dict = {"result": 'ok'}
                                return_dict["critical_error"] = 'false'
                                json_response = json.dumps(return_dict)
                                return HttpResponse(json_response,mimetype='application/json')
                            else:
                                return HttpResponse('ERROR DEMO REG')

                    except Exception, e:
                        print e
                        u = User.objects.get(username=username)
                        u.delete()
                        transaction.rollback()
                        return_dict = {"result": 'error'}
                        return_dict["critical_error"] = 'false'
                        json_response = json.dumps(return_dict)
                        return HttpResponse(json_response,mimetype='application/json')
                        #ERRORE DI QUALCHE TIPO, RESTITUISCO ERROR E CANCELLO USER, CHE SI PORTA APPRESSO TUTTI I TEMP RECORD
                    for aff in request.POST.getlist('affiliation[]'):
                        if aff =='new_aff':
                            companyName=request.POST.get('new_aff_name')
                            state=request.POST.get('new_aff_state')
                            department=request.POST.get('new_aff_department')
                            aff=Affiliation(companyName=companyName,department=department,state=state,validated=False)
                            aff.save()
                            user_aff=LASUser_affiliation(lasuser=LASUser.objects.get(username=username),affiliation=aff,is_principal_investigator=True)
                            user_aff.save()
                        else:
                            user_aff=LASUser_affiliation(lasuser=LASUser.objects.get(username=username),affiliation=Affiliation.objects.get(id=aff),is_principal_investigator=True)
                            user_aff.save()
                else:
                    try:
                        #if settings.DEMO:
                        #    result=LASDemo(u,request)
                        #    if result:
                        #        return_dict = {"result": 'ok'}
                        #        json_response = json.dumps(return_dict)
                        #        return HttpResponse(json_response,mimetype='application/json')
                        #    else:
                        #        return HttpResponse('ERROR DEMO REG')


                        supList=request.POST.getlist('supervisors[]')
                        print 'supList',supList
                        roleIDList=list()
                        roles=Role.objects.all()
                        #rolesID = request.POST.getlist("roles["+s+"][]")
                        for r in roles:
                            roleIDList.append(r.id)


                        temp=LASUserTemporaryRegistration(user=u)
                        temp.save()
                        for s in supList:
                            print 's',s
                            if (int(s)!=0):
                                supervisor=LASUser.objects.get(id=s)
                                print 'supervisor',supervisor.username
                                #supAff=LASUser_affiliation.objects.get(id=s)
                                #subReg=LASUserTempRegSupervisors(lasUserTemporaryRegistration=temp,supervisor=supAff.lasuser)
                                subReg=LASUserTempRegSupervisors(lasUserTemporaryRegistration=temp,supervisor=supervisor)
                                subReg.save()
                                subject="New LAS Registration for your Working Groups!"
                                message="Dear "+supervisor.first_name+",\n there is a new pending registration for your working groups in LAS.\nPlease inspect the request as soon as possible"
                                message=message.encode('utf-8')
                                toList=list()
                                toList.append(supervisor.email)
                                #try:
                                #    email = EmailMessage(subject,message,"",toList,"","","","","")
                                #    email.send(fail_silently=False)
                                #    print "email sent"
                                #except Exception,e:
                                #    print e,'MAIL TO SUPERVISOR FAIL'

                                affiliationsList= request.POST.getlist("affiliations["+s+"][]")
                                for affID in affiliationsList:
                                    affiliation=Affiliation.objects.get(id=affID)
                                    if LASUser_affiliation.objects.filter(lasuser=LASUser.objects.get(username=username),affiliation=affiliation,is_principal_investigator=False).count()==0:
                                        aff=LASUser_affiliation(lasuser=LASUser.objects.get(username=username),affiliation=affiliation,is_principal_investigator=False)
                                        aff.save()
                                rolesID = request.POST.getlist("roles["+s+"][]")
                                for item in rolesID:
                                    role=Role.objects.get(id=item)
                                    subReg.roles.add(role)
                                    #subject="New LAS Registration for your Working Group!"
                                    #message="Dear "+supervisor.first_name+",\nthere is a new pending registration for your Working Group.\n\n\nUser information:\n\nName: " + u.first_name + "\nLast Name: " + u.last_name +"\nMail Address: "+u.email
                                    #message=message.encode('utf-8')
                                    #toList=list()
                                    #toList.append(supervisor.email)
                                    #email = EmailMessage(subject,message,"",toList,"","","","","")
                                    #email.send(fail_silently=False)
                                try:
                                    print 'tolist',toList
                                    email = EmailMessage(subject,message,"",toList,"","","","","")
                                    email.send(fail_silently=False)
                                    print "email sent"
                                except Exception,e:
                                    print e,'MAIL TO SUPERVISOR FAIL'
                                if request.POST.get('project')!='':
                                    result=LASProject(u,request,subReg)
                                    if result:
                                        return_dict = {"result": 'ok'}
                                        return_dict["critical_error"] = 'false'
                                        json_response = json.dumps(return_dict)
                                        return HttpResponse(json_response,mimetype='application/json')
                                    else:
                                        return HttpResponse('ERROR PROJECT REG')

                            else:
                                new_pi_name=request.POST.get('new_pi_name')
                                new_pi_lastname=request.POST.get('new_pi_lastname')
                                new_pi_mail=request.POST.get('new_pi_mail')
                                ps=PotentialSupervisor(firstname=new_pi_name,lastname=new_pi_lastname,email=new_pi_mail)
                                ps.save()
                                subReg=LASUserTempRegPotSupervisors(lasUserTemporaryRegistration=temp,potentialSupervisor=ps)
                                subReg.save()
                                rolesID = request.POST.getlist("roles["+s+"][]")
                                for item in rolesID:
                                    role=Role.objects.get(id=item)
                                    subReg.roles.add(role)
                                if (LASUser.objects.filter(email=new_pi_mail).count()==0):
                                    #invio mail solo se lasuser non esisite, se esiste, non potevo dire all'utente che gia esisteva ma non era PI.La registrazione andra a morire
                                    subject="Join LAS!"
                                    message="Dear "+new_pi_name+",\nyou are invited to join LAS.\nPlease use the following link to join the platform.\n%s/las/accounts/register/" % settings.DOMAIN_URL
                                    message=message.encode('utf-8')
                                    toList=list()
                                    toList.append(new_pi_mail)
                                    email = EmailMessage(subject,message,"",toList,"","","","","")
                                    email.send(fail_silently=False)
                    except Exception,e:
                        print e
                        u = User.objects.get(username=username)
                        u.delete()
                        transaction.rollback()
                        return_dict = {"result": 'error'}
                        return_dict["critical_error"] = 'false'
                        json_response = json.dumps(return_dict)
                        return HttpResponse(json_response,mimetype='application/json')
                        #ERRORE DI QUALCHE TIPO, RESTITUISCO ERROR E CANCELLO USER, CHE SI PORTA APPRESSO TUTTI I TEMP RECORD

                return_dict = {"result": 'ok'}
                return_dict["critical_error"] = 'false'
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')
            except Exception,e:
                print e
                transaction.rollback()
                return_dict = {"result": 'error'}
                return_dict["critical_error"] = 'false'
                json_response = json.dumps(return_dict)
                return HttpResponse(json_response,mimetype='application/json')

    else:
        if 'refreshCaptcha' in request.GET:
            to_json_response = dict()
            to_json_response['status'] = 0
            to_json_response['new_cptch_key'] = CaptchaStore.generate_key()
            to_json_response['new_cptch_image'] = captcha_image_url(to_json_response['new_cptch_key'])
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        else:
            if projectName is not None:
                return render_to_response('registration/registration_form.html', {'project':projectName}, RequestContext(request))

            affiliation_list=Affiliation.objects.all().values('id','companyName','state','department')
            context = RequestContext(request)
            context['cf'] = CaptchaForm()
            return render_to_response('registration/registration_form.html', {'affiliation_list':affiliation_list}, context)



def LASProject(user,request,tempRecord):
    import urllib, urllib2
    wg=WG.objects.get(owner=LASUser.objects.get(username=request.POST.get('project')))
    modulesToAdd=set()
    try:
        backend = get_backend()
        profile= RegistrationProfile.objects.get(user_id=user.id)
    except Exception,e:
        print "fail",e
        return False
    if profile is not None and profile.status=='untreated':
        backend.accept(profile, request=request)

    luser=LASUser.objects.get(id=user.id)
    modulesSet=set()
    permsList=list()
    userDict={}
    actList=Activity.objects.filter(father_activity__isnull=False,id__in=Role_potential_activities.objects.filter(role__in=tempRecord.roles.all()).values_list('potential_activities', flat=True)).values_list('id',flat=True)

    try:
        for a in actList:
            if WG_lasuser_activities.objects.filter(lasuser=luser,WG=wg,activity=Activity.objects.get(id=a)).count()==0:
                item=WG_lasuser_activities(lasuser=luser,WG=wg,activity=Activity.objects.get(id=a))
                item.save()
        permList= Activities_LASPermissions.objects.filter(activity__id__in=actList).values_list('laspermission',flat=True).distinct()
        perms=dict()
        for perm in permList:
            laspermission=LASPermission.objects.get(id=perm)
            modulesSet.add(laspermission.lasmodule.shortname)
            try:
                WG_lasuser.objects.get(WG=wg,lasuser=luser,laspermission=laspermission)
            except:
                wg_lasuser=WG_lasuser(WG=wg,lasuser=luser,laspermission=laspermission)
                wg_lasuser.save()
            perm=Permission.objects.get(codename=laspermission.codename)
            if (user.has_perm("loginmanager."+perm.codename)==False):
                user.user_permissions.add(perm)
            if not laspermission.lasmodule.shortname in perms:
                perms[laspermission.lasmodule.shortname]=""
            perms[laspermission.lasmodule.shortname]+=perm.codename+","

            userDict['username']=user.username
            userDict['first_name']=user.first_name
            userDict['last_name']=user.last_name
            userDict['email']=user.email
            userDict['permissions']=perms
            permsList.append(userDict)
    except Exception,e:
        print e
    for m in modulesSet:
        lasmodule=LASModule.objects.get(shortname=m)
        address=lasmodule.home_url
        url = address+"permission/addToWG/"
        print url
        values = {'wg':wg.name,'permsList[]':permsList,'api_key':'','wgOwner':request.user.username}
        data = urllib.urlencode(values,True)
        try:
            resp=urllib2.urlopen(url, data)
            res1 =  resp.read()
        except Exception, e:
            print e
            user.delete()
            if str(e.code)== '403':
                print "fail api"
            return False
        if LASUser_modules.objects.filter(lasuser=luser,lasmodule=lasmodule,is_superuser=0).count()==0:
            rel= LASUser_modules(lasuser=luser,lasmodule=lasmodule,is_superuser=0)
            rel.save()
    tempRecord.delete()
    return True


def LASDemo(user,request):
    import urllib,urllib2
    #from apisecurity.apykey import *
    try:
        backend = get_backend()
        try:
            profile= RegistrationProfile.objects.get(user_id=user.id)
        except:
            profile=None
            return False
        try:
            if profile is not None and profile.status=='untreated':
                backend.accept(profile, request=request)
                user=User.objects.get(pk=profile.user_id)
                temp=PiTemporaryRegistration.objects.get(user=user)
                luser=LASUser.objects.get(pk=profile.user_id)
                wg=WG.objects.get(owner=luser)
                wgDemo=WG.objects.get(owner=LASUser.objects.get(username='LASDemo'))
                errore=False
                errorString=""
                modulesSet=set()
                permsList=list()
                perms=dict()
                userDict={}
                laspermissions=LASPermission.objects.filter(id__in=Activities_LASPermissions.objects.filter(activity_id__in=PiTemporaryRegistration_Activities.objects.filter(piTemporaryRegistration__id=temp.id).values_list('activity',flat='True')).values_list('laspermission',flat='True'))
                for laspermission in laspermissions:
                    modulesSet.add(laspermission.lasmodule.shortname)
                    try:
                        WG_lasuser.objects.get(WG=wg,lasuser=luser,laspermission=laspermission)
                    except:
                        wg_lasuser=WG_lasuser(WG=wg,lasuser=luser,laspermission=laspermission)
                        wg_lasuser.save()
                    try:
                        WG_lasuser.objects.get(WG=wgDemo,lasuser=luser,laspermission=laspermission)
                    except:
                        wg_lasuser=WG_lasuser(WG=wgDemo,lasuser=luser,laspermission=laspermission)
                        wg_lasuser.save()

                    perm=Permission.objects.get(codename=laspermission.codename)
                    if (user.has_perm("loginmanager."+perm.codename)==False):
                        user.user_permissions.add(perm)
                    if not laspermission.lasmodule.shortname in perms:
                        perms[laspermission.lasmodule.shortname]=""
                    perms[laspermission.lasmodule.shortname]+=perm.codename+","

                    userDict['username']=user.username
                    userDict['first_name']=user.first_name
                    userDict['last_name']=user.last_name
                    userDict['email']=user.email
                    userDict['permissions']=perms
                    permsList.append(userDict)
                for m in modulesSet:
                    lasmodule=LASModule.objects.get(shortname=m)
                    if lasmodule.name!='LASAuthServer':
                        address=lasmodule.home_url
                        url = address+"permission/addToWG/"
                        #t = getApiKey()
                        print url
                        values = {'wg':wg.name,'permsList[]':permsList,'api_key':'','wgOwner':wg.owner.username}
                        data = urllib.urlencode(values,True)
                        try:
                            resp=urllib2.urlopen(url, data)
                            res1 =  resp.read()
                        except Exception, e:
                            print 'Eccezione in salvataggio PI 1)',e
                            transaction.rollback()
                            return False
                    if LASUser_modules.objects.filter(lasuser=luser,lasmodule=lasmodule,is_superuser=0).count()==0:
                        rel= LASUser_modules(lasuser=luser,lasmodule=lasmodule,is_superuser=0)
                        rel.save()
                activityList=Activity.objects.filter(id__in=PiTemporaryRegistration_Activities.objects.filter(piTemporaryRegistration__id=temp.id).values_list('activity',flat='True'))
                for act in activityList:
                    try:
                        lasuserAct=WG_lasuser_activities.objects.get(WG=wg,lasuser=luser,activity=act)
                    except Exception,e:
                        lasuserAct=WG_lasuser_activities(WG=wg,lasuser=luser,activity=act)
                        lasuserAct.save()
                for m in modulesSet:
                    lasmodule=LASModule.objects.get(shortname=m)
                    if lasmodule.name!='LASAuthServer':
                        address=lasmodule.home_url
                        url = address+"permission/addToWG/"
                        #t = getApiKey()
                        print url
                        values = {'wg':wgDemo.name,'permsList[]':permsList,'api_key':'','wgOwner':wgDemo.owner.username}
                        data = urllib.urlencode(values,True)
                        try:
                            resp=urllib2.urlopen(url, data)
                            res1 =  resp.read()
                        except Exception, e:
                            print 'Eccezione in salvataggio PI 1)',e
                            transaction.rollback()
                            return False
                    if LASUser_modules.objects.filter(lasuser=luser,lasmodule=lasmodule,is_superuser=0).count()==0:
                        rel= LASUser_modules(lasuser=luser,lasmodule=lasmodule,is_superuser=0)
                        rel.save()
                activityList=Activity.objects.filter(id__in=PiTemporaryRegistration_Activities.objects.filter(piTemporaryRegistration__id=temp.id).values_list('activity',flat='True'))
                for act in activityList:
                    try:
                        lasuserAct=WG_lasuser_activities.objects.get(WG=wgDemo,lasuser=luser,activity=act)
                    except Exception,e:
                        lasuserAct=WG_lasuser_activities(WG=wgDemo,lasuser=luser,activity=act)
                        lasuserAct.save()

                try:
                    potSup=PotentialSupervisor.objects.get(email=luser.email)
                    for item in LASUserTempRegPotSupervisors.objects.filter(potentialSupervisor=potSup):
                        tempReg=LASUserTempRegSupervisors(lasUserTemporaryRegistration=item.lasUserTemporaryRegistration,supervisor=luser)
                        tempReg.save()
                        tempReg.roles=item.roles.all()
                        item.delete()
                    potSup.delete()
                except Exception,e:
                    print 'Eccezione in salvataggio PI 2(PREVISTA))',e
        except Exception,e:
            print 'Eccezione in salvataggio PI 3)',e
            transaction.rollback()
            user=User.objects.get(pk=profile.user_id)
            user.delete()
            return False
        temporaryReg=PiTemporaryRegistration.objects.get(user=user)
        temporaryReg.delete()
        return True
    except Exception, e:
        transaction.rollback()
        return False

def LASDemoOLD(user,request):
    import urllib, urllib2
    wg=WG.objects.get(name='Bertotti_WG')
    modulesToAdd=set()
    try:
        backend = get_backend()
        profile= RegistrationProfile.objects.get(user_id=user.id)
    except Exception,e:
        print "fail",e
        return False
    if profile is not None and profile.status=='untreated':
        backend.accept(profile, request=request)

    luser=LASUser.objects.get(id=user.id)

    modulesSet=set()
    permsList=list()
    userDict={}
    actList=Activity.objects.all().values_list('id',flat=True)
    try:
        for a in actList:
            if WG_lasuser_activities.objects.filter(lasuser=luser,WG=wg,activity=Activity.objects.get(id=a)).count()==0:
                item=WG_lasuser_activities(lasuser=luser,WG=wg,activity=Activity.objects.get(id=a))
                item.save()
        permList= Activities_LASPermissions.objects.filter(activity__id__in=actList).values_list('laspermission',flat=True).distinct()
        perms=dict()
        for perm in permList:
            laspermission=LASPermission.objects.get(id=perm)
            modulesSet.add(laspermission.lasmodule.shortname)
            try:
                WG_lasuser.objects.get(WG=wg,lasuser=luser,laspermission=laspermission)
            except:
                wg_lasuser=WG_lasuser(WG=wg,lasuser=luser,laspermission=laspermission)
                wg_lasuser.save()
            perm=Permission.objects.get(codename=laspermission.codename)
            if (user.has_perm("loginmanager."+perm.codename)==False):
                user.user_permissions.add(perm)
            if not laspermission.lasmodule.shortname in perms:
                perms[laspermission.lasmodule.shortname]=""
            perms[laspermission.lasmodule.shortname]+=perm.codename+","

            userDict['username']=user.username
            userDict['first_name']=user.first_name
            userDict['last_name']=user.last_name
            userDict['email']=user.email
            userDict['permissions']=perms
            permsList.append(userDict)
    except Exception,e:
        print e
    for m in modulesSet:
        lasmodule=LASModule.objects.get(shortname=m)
        address=lasmodule.home_url
        url = address+"permission/addToWG/"
        print url
        values = {'wg':wg.name,'permsList[]':permsList,'api_key':'','wgOwner':request.user.username}
        data = urllib.urlencode(values,True)
        try:
            resp=urllib2.urlopen(url, data)
            res1 =  resp.read()
        except Exception, e:
            print e
            user.delete()
            if str(e.code)== '403':
                print "fail api"
            return False
        if LASUser_modules.objects.filter(lasuser=luser,lasmodule=lasmodule,is_superuser=0).count()==0:
            rel= LASUser_modules(lasuser=luser,lasmodule=lasmodule,is_superuser=0)
            rel.save()


    return True





class RegistrationView(FormMixin, TemplateResponseMixin, ProcessFormView):
    """A complex view for registration

    GET:
        Display an RegistrationForm which has ``username``, ``email1`` and ``email2``
        for registration.
        ``email1`` and ``email2`` should be equal to prepend typo.

        ``form`` and ``supplement_form`` is in context to display these form.

    POST:
        Register the user with passed ``username`` and ``email1``
    """
    template_name = r'registration/registration_form.html'

    def __init__(self, *args, **kwargs):
        self.backend = get_backend()
        super(RegistrationView, self).__init__(*args, **kwargs)

    def get_success_url(self):
        """get registration complete url via backend"""
        return self.backend.get_registration_complete_url(self.new_user)

    def get_disallowed_url(self):
        """get registration closed url via backend"""
        return self.backend.get_registration_closed_url()

    def get_form_class(self):
        """get registration form class via backend"""
        return self.backend.get_registration_form_class()

    def get_supplement_form_class(self):
        """get registration supplement form class via backend"""
        return self.backend.get_supplement_form_class()

    def get_supplement_form(self, supplement_form_class):
        """get registration supplement form instance"""
        if not supplement_form_class:
            return None
        return supplement_form_class(**self.get_form_kwargs())

    def form_valid(self, form, supplement_form=None):
        """register user with ``username`` and ``email1``

        this method is called when form validation has successed.
        """
        username = form.cleaned_data['username']
        email = form.cleaned_data['email1']
        first_name= form.cleaned_data['first_name']
        last_name= form.cleaned_data['last_name']
        modules=form.cleaned_data['modules']
        note=form.cleaned_data['note']


        #raise Exception('prova')
        self.new_user = self.backend.register(username, email, self.request)


        #AGGIUNGO I CAMPI NOME E COGNOME ALL'USER NEL DB
        from django.contrib.auth.models import User
        u = User.objects.get(username=username)
        u.first_name=first_name
        u.last_name=last_name
        u.save()

        #MEMORIZZI MODULI TEMPORANEI
        from loginmanager.models import TemporaryModules
        from loginmanager.models import LASModule
        tempModules=TemporaryModules(note=note)
        tempModules.user=u
        tempModules.save()

        t= TemporaryModules.objects.get(id=tempModules.id)
        for x in modules:
            module= LASModule.objects.get(id=x)
            t.modules.add(module)

        if supplement_form:
            profile = self.new_user.registration_profile
            supplement = supplement_form.save(commit=False)
            supplement.registration_profile = profile
            supplement.save()

        return super(RegistrationView, self).form_valid(form)


    def form_invalid(self, form, supplement_form=None):
        context = self.get_context_data(
                form=form, supplement_form=supplement_form)
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        supplement_form_class = self.get_supplement_form_class()
        supplement_form = self.get_supplement_form(supplement_form_class)
        context = self.get_context_data(
                form=form, supplement_form=supplement_form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        supplement_form_class = self.get_supplement_form_class()
        supplement_form = self.get_supplement_form(supplement_form_class)
        if form.is_valid() and (not supplement_form or supplement_form.is_valid()):
            return self.form_valid(form, supplement_form)
        else:
            return self.form_invalid(form, supplement_form)


    def dispatch(self, request, *args, **kwargs):
        if not self.backend.registration_allowed():
            # registraion has closed
            return redirect(self.get_disallowed_url())
        return super(RegistrationView, self).dispatch(request, *args, **kwargs)

@login_required
@transaction.commit_manually
def AdminCreate(request,projectName=None):
    #backend=get_backend()
    try:
        pis = User.objects.filter(id__in=WG.objects.all().values('owner')).order_by('last_name', 'first_name')
        if request.method == 'GET':
            transaction.commit()
            return render_to_response('registration/adminCreate.html', {'pis':pis, 'message':''}, RequestContext(request))
        else:

            print request.POST
            first_name = request.POST.get("first_name", "")
            last_name = request.POST.get("last_name", "")
            username = request.POST.get("username", "")
            email = request.POST.get("email", "")
            pi = request.POST.get("pi", "")
            is_pi = request.POST.get("is_pi", False)

            if first_name == '' or last_name == '' or username == '' or email == '':
                return render_to_response('registration/adminCreate.html',  {'pis':pis, 'message': 'Complete all fields', 'status':'error'}, RequestContext(request))


            new_user =User(username=username, first_name = first_name, last_name = last_name, email=email, is_active=True)
            new_user.save()


            luser=LASUser(id=new_user.id,first_name=new_user.first_name,last_name=new_user.last_name, username=new_user.username,email=new_user.email,is_active=new_user.is_active)
            luser.save()

            aff = Affiliation.objects.get(pk=1)
            user_aff=LASUser_affiliation(lasuser=luser,affiliation=aff,is_principal_investigator=False)

            defaultPerm =['Patient Management', 'Funnel']

            if is_pi:
                user_aff.is_principal_investigator = True
                wg=WG(name=new_user.username+'_WG',owner=luser)
                wg.save()
                print "WG ->", wg.name
                if settings.USE_GRAPH_DB==True:
                    gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
                    if gdb.get_indexed_node('node_auto_index','identifier',str(wg.name)):
                        print "nodo WG esistente"
                    else:
                        print "aggiungo WG al grafo"
                        new_node,=gdb.create({"identifier":str(wg.name)})
                        new_node.add_labels("Social","WG")
                defaultPerm.append('WG Management')
            else:
                print 'Pi setted'
                print pi
                piUser = LASUser.objects.get(id=pi)
                print piUser
                wg = WG.objects.get(owner=piUser)
                print wg
            user_aff.save()


            for act in Activity.objects.filter(name__in = defaultPerm):
                try:
                    lasuserAct=WG_lasuser_activities.objects.get(WG=wg,lasuser=luser,activity=act)
                except Exception,e:
                    lasuserAct=WG_lasuser_activities(WG=wg,lasuser=luser,activity=act)
                    lasuserAct.save()

            permList= Activities_LASPermissions.objects.filter(activity__in=Activity.objects.filter(name__in = defaultPerm)).values_list('laspermission',flat=True).distinct()
            permsList=list()
            perms=dict()
            modulesSet= set()
            for perm in permList:
                laspermission=LASPermission.objects.get(id=perm)
                modulesSet.add(laspermission.lasmodule.shortname)
                try:
                    WG_lasuser.objects.get(WG=wg,lasuser=luser,laspermission=laspermission)
                except:
                    wg_lasuser=WG_lasuser(WG=wg,lasuser=luser,laspermission=laspermission)
                    wg_lasuser.save()
                perm=Permission.objects.get(codename=laspermission.codename)
                if (new_user.has_perm("loginmanager."+perm.codename)==False):
                    new_user.user_permissions.add(perm)
                if not laspermission.lasmodule.shortname in perms:
                    perms[laspermission.lasmodule.shortname]=""
                perms[laspermission.lasmodule.shortname]+=perm.codename+","
                userDict = {}
                userDict['username']=new_user.username
                userDict['first_name']=new_user.first_name
                userDict['last_name']=new_user.last_name
                userDict['email']=new_user.email
                userDict['permissions']=perms
                permsList.append(userDict)

            for m in modulesSet:
                lasmodule=LASModule.objects.get(shortname=m)
                if lasmodule.name!='LASAuthServer':
                    address=lasmodule.home_url
                    url = address+"permission/addToWG/"
                    #t = getApiKey()
                    print url
                    values = {'wg':wg.name,'permsList[]':permsList,'api_key':'','wgOwner':wg.owner.username}
                    print values
                    data = urllib.urlencode(values,True)
                    try:
                        resp=urllib2.urlopen(url, data)
                        res1 =  resp.read()
                    except Exception, e:
                        print 'exception for url:', url, ' : ', e
                        user.delete()
                        if str(e.code)== '403':
                            print "fail api"
                            return_dict = {"message": "API error"}
                        else:
                            return_dict = {"message": "error"}
                        json_response = json.dumps(return_dict)
                        return HttpResponse(json_response,mimetype='application/json')
                if LASUser_modules.objects.filter(lasuser=luser,lasmodule=lasmodule,is_superuser=0).count()==0:
                    rel= LASUser_modules(lasuser=luser,lasmodule=lasmodule,is_superuser=0)
                    rel.save()

            print 'create node user'
            gdb=neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
            q=neo4j.CypherQuery(gdb,"CREATE (n:Social:User {identifier:'"  + new_user.username + "'}) return n")
            r=q.execute()
            q=neo4j.CypherQuery(gdb,"MATCH (n:User),(wg:WG) where n.identifier='"+ new_user.username + "' and wg.identifier='"+ wg.name + "' CREATE UNIQUE (n)-[:belongs]->(wg) return n.identifier")
            r=q.execute()

            # generate Password

            chars = string.letters + string.digits # Just alphanumeric characters
            pwdSize = 10 # pwd size
            pwd = ''.join((random.choice(chars)) for x in range(pwdSize))

            subject="LAS Registration"
            message="Dear "+luser.first_name +" " + luser.last_name +",\n\n\tyou are now registered in the LAS platform. Your account is the following:\n\n\t\tUsername: " + luser.username + "\n\t\tPassword: " + pwd + "\n\nNow you can visit %s/las/laslogin/ and try to sign-in. Please change your password as soon as possible.\n\nBest regards,\n\n--\nLAS staff" % settings.DOMAIN_URL
            message=message.encode('utf-8')

            new_user.set_password(pwd)
            print new_user.password,'random pass: {0}'.format(pwd)
            new_user.save()
            print new_user.password
            u = User.objects.get(username=username)
            print u.password
            print "sending mail..."
            email = EmailMessage(subject,message,"",[luser.email],"","","","","")
            email.send(fail_silently=False)
            print "mail sent..."
            transaction.commit()
            return render_to_response('registration/adminCreate.html',  {'pis':pis, 'message': 'User created', 'status': 'ok'}, RequestContext(request))
    except Exception, e:
        print e
        transaction.rollback()
        return render_to_response('registration/adminCreate.html',  {'pis':pis, 'message': 'Something went wrong', 'status':'error'}, RequestContext(request))
    finally:
        transaction.rollback()
