from piston.handler import BaseHandler
from loginmanager.models import *
from piston.utils import rc
from django.contrib import auth
import json

#Per verificare che username e password corrispondano ad un utente realmente esistente
class CheckLoginHandler(BaseHandler):
    allowed_methods = ('GET','POST')    
    def read(self, request):
        response = rc.ALL_OK
        response.content = json.dumps({'status':'200'})
        print 'response',response
        print 'resp',response.content
        return response
    def create(self, request):
        try:
            print request.POST
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            print 'user',user
            if user is not None:
                if user.is_active:
                    response=rc.ALL_OK
                    response.content=json.dumps({'user':user.username})
                    return response
                else:
                    raise Exception('User not active')
            else:
                raise Exception('User not exists')
        except Exception, e:
            print 'err',e
            response=rc.FORBIDDEN
            response.content=json.dumps({'error':str(e)})
            return response
