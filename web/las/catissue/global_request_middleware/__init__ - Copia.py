try:
    from threading import currentThread
except:
    # Django 1.2 and older
    from django.utils.thread_support import currentThread 

_requests = {}

class GlobalRequestMiddlewareException(Exception):
    pass

def get_request():
    t = currentThread()
    if not t in _requests:
        raise GlobalRequestMiddlewareException
    return _requests[t] 

def get_request_url():
    t = currentThread()
    if not t in _requests:
        raise GlobalRequestMiddlewareException
    return _requests[t].url


def has_request():
    t = currentThread()
    return t in _requests

class userInfo(object):
    user=""
    groups=list()
    url=""
    functionality=""
    
class GlobalRequestMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        from urlparse import urlparse
        try:
            t = currentThread()
            x= userInfo()
            x.user=request.user
            if not t in _requests:
                if str(type(view_func))!="<type 'function'>":
                    url=request.META['HTTP_REFERER']
                    x.url=url
                    if url is not None:
                        parsed_uri = urlparse(url)
                        domain = '{}://{}/'.format( parsed_uri[ 0 ], parsed_uri[ 1 ] )
                        x.functionality=url.replace(domain, "")
                    else:
                        print"???"
                        return
                else:
                    if view_func.__module__!="django.views.static": 
                        url=request.build_absolute_uri(request.get_full_path())
                        x.url=url
                        parsed_uri = urlparse(url)
                        domain = '{}://{}/'.format( parsed_uri[ 0 ], parsed_uri[ 1 ] )
                        x.functionality=url.replace(domain, "")
                    else:
                        pass
                print x.functionality
                _requests[currentThread()]=x
        except Exception,e:
            print e
            pass


    def process_response(self, request, response):
        t=currentThread()
        if t in _requests:
            del _requests[t]
        return response
    #def process_request(self, request):
    #   try: 
    #       x= userInfo()
    #       x.user=request.user
    #       x.url=""
    #       _requests[currentThread()]=x
    #   except Exception,e:
    #       print e
    #       pass
            
