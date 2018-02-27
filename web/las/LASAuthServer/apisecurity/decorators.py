from functools import wraps
from django.http import HttpResponse
from django.conf import settings
import hmac
import hashlib
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from apisecurity.apikey import *
from django.core.urlresolvers import reverse

def required_parameters(parameters):
    
    def inner_decorator(fn):
        def wrapped(request, *args, **kwargs):
            try:
                # check if the user api_key matches
                http_method=request.method
                
                if parameters not in getattr(request, http_method):
                    return HttpResponseRedirect(reverse("django.views.defaults.permission_denied"))
                #return json_response({'success': False, 'errors': 'Please use the Web API correctly and supply the parameter: '+parameter})
                else:
	            #print request.POST
                    if http_method=='POST':
                        received= request.POST.get('api_key')
			#print received
                    elif http_method=='GET':
                        received= request.GET.get('api_key')
                    else:
                        return HttpResponseRedirect(reverse("django.views.defaults.permission_denied"))
                    try:
                        import ast
                        key= ast.literal_eval(received)
                        if checkApiKey(key['digest'],key['timestamp'])==False:
                            #NO ACCESSO                         
                            return HttpResponseRedirect(reverse("django.views.defaults.permission_denied"))
                        else:
                            print "Permesso accordato"
                    except Exception,e:
                        print e
                        return HttpResponseRedirect(reverse("django.views.defaults.permission_denied"))
	    except Exception,e:
		print e
		return HttpResponseRedirect(reverse("django.views.defaults.permission_denied"))
            # Proceed like normally with the request
            return fn(request, *args, **kwargs)
        return wraps(fn)(wrapped)
    return inner_decorator
