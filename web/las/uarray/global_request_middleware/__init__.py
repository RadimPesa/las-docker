from threading import currentThread
from django.conf import settings


_requests = {}

class GlobalRequestMiddlewareException(Exception):
    pass


def get_request():
    t = currentThread()
    if not t in _requests:
        raise GlobalRequestMiddlewareException
    return _requests[t]



class userInfo(object):
    user=""
    WG=""
    functionality=''

def get_WG_string():
    if settings.USE_GRAPH_DB==True:
        t = currentThread()
        if not t in _requests:
            raise GlobalRequestMiddlewareException
        if _requests[t].WG is not None:
            wgString= ",".join(_requests[t].WG)
            return wgString
        else:
            return ''
    else:
        return ''

def set_WG_string(wgString):
    if settings.USE_GRAPH_DB == True:
        global _requests    
        t = currentThread()
        if not t in _requests:
            raise GlobalRequestMiddlewareException
        wgList=wgString.split(',')
        wgSet=set()
        for wg in wgList:
            wgSet.add(wg)
        _requests[t].WG =wgSet
    return

def get_user():
    t = currentThread()
    if not t in _requests:
        raise GlobalRequestMiddlewareException
    return _requests[t].user


def set_WG(WG):
    if settings.USE_GRAPH_DB == True:
        global _requests
        t = currentThread()
        if not t in _requests:
            raise GlobalRequestMiddlewareException
        _requests[t].WG=WG
    return

def get_WG():
    if settings.USE_GRAPH_DB == True:
        global _requests
        t = currentThread()
        if not t in _requests:
            x= userInfo()
            x.user=''
            _requests[t]=x
            _requests[t].WG=set()
        return _requests[t].WG
    else:
        return set()

    
def set_functionality(codename):
    if settings.USE_GRAPH_DB == True:
        global _requests
        t = currentThread()
        if not t in _requests:
            raise GlobalRequestMiddlewareException
        _requests[t].functionality=codename
        print "settato", _requests[t].functionality
    return

def get_functionality():
    if settings.USE_GRAPH_DB == True:
        global _requests
        t = currentThread()
        if not t in _requests:
            x= userInfo()
            x.user=''
            _requests[t]=x
            _requests[t].functionality=''
        return _requests[t].functionality
    else:
        return ''

def disable_graph():
    if settings.USE_GRAPH_DB == True:
        global _requests
        t = currentThread()
        if not t in _requests:
            raise GlobalRequestMiddlewareException
        wgSet=_requests[t].WG
        if 'admin' not in wgSet:
            wgSet.add('admin')
            _requests[t].WG=wgSet
    return

def enable_graph():
    if settings.USE_GRAPH_DB == True:
        global _requests
        t = currentThread()
        if not t in _requests:
            x= userInfo()
            x.user=''
            _requests[t]=x
            _requests[t].WG=set()
            _requests[t].functionality=''
        wgSet=_requests[t].WG
        if 'admin' in wgSet:
            wgSet.remove('admin')
            _requests[t].WG=wgSet
    return


class GlobalRequestMiddleware(object):
    def process_request(self, request):
        try:
            global _requests
            t = currentThread()
            x= userInfo()
            x.user=request.user
            _requests[currentThread()]=x
            _requests[currentThread()].WG=set()
            _requests[currentThread()].functionality=''
            if 'REQUEST_URI' in request.META:
                if '/admin/' in request.META['REQUEST_URI']:
                    _requests[currentThread()].WG.add('admin')
        except Exception,e:
            print e


    def process_response(self, request, response):
        global _requests
        t=currentThread()
        if t in _requests:
            del _requests[t]
        return response
