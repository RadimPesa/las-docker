from django.http import HttpResponse
import requests
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

#URLHUB = "http://pieruz.polito.it:8000"
URLHUB= settings.HUB_URL

@csrf_exempt
def getAndLock(request):
    try:
        if request.method == 'POST':
            print request.POST
            if URLHUB == '':
                return HttpResponse('not active')
            else:
                #input: randomFlag - case 
                url = URLHUB + '/generateCase/'
                values = {'randomFlag' : request.POST['randomFlag'], 'case': request.POST['case']}
                r = requests.post(url, data=values, verify=False)
                #print 'client', result
                return HttpResponse(r.text)
        else:
            return HttpResponse('This url needs a post request, not a get.')
    except Exception, e:
        print e
        return HttpResponse(e)

@csrf_exempt
def saveAndFinalize(request):
    try:
        if request.method == 'POST':
            print request.POST
            if URLHUB == '':
                return HttpResponse('not active')
            else:
                #input: randomFlag - case 
                url = URLHUB + '/finalizeItems/'
                values = {'typeO' : request.POST['typeO'], 'listO': request.POST['listO']}
                r = requests.post(url, data=values, verify=False)
                #print 'client', result
                return HttpResponse(r.text)
        else:
            return HttpResponse('This url needs a post request, not a get.')
    except Exception, e:
        print e
        return HttpResponse(e)

@csrf_exempt
def checkBarcode(request):
    try:
        if request.method == 'POST':
            print request.POST
            if URLHUB == '':
                return HttpResponse('not active')
            else:
                #input: randomFlag - case 
                url = URLHUB + '/checkBarcode/'
                values = {'barcode' : request.POST['barcode']}
                print values
                r = requests.post(url, data=values, verify=False)
                #print 'client', result
                return HttpResponse(r.text)
        else:
            return HttpResponse('This url needs a post request, not a get.')
    except Exception, e:
        print e
        return HttpResponse(e)