from piston.handler import BaseHandler
from loginmanager.models import *
from piston.utils import rc
from django.contrib import auth
import json,ast

#Per verificare che username e password corrispondano ad un utente realmente esistente
class CheckLoginHandler(BaseHandler):
    allowed_methods = ('POST')
    '''def read(self, request):
        response = rc.ALL_OK
        response.content = json.dumps({'status':'200'})
        print 'response',response
        print 'resp',response.content
        return response'''
    def create(self, request):
        try:
            print 'request.POST',request.POST
            #dictdata=ast.literal_eval(request.raw_post_data)
            #print 'dictdata',dictdata
            raw_data = json.loads(request.raw_post_data)
            print 'raw_data',raw_data
            username = raw_data['username']
            password = raw_data['password']
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
