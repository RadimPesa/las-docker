from __init__ import *
from django.views.decorators.csrf import csrf_exempt
from django.core.servers.basehttp import FileWrapper

@csrf_exempt
def retrieveFile(request, link):
    if request.method == "GET":
        repdata = RepData.objects(id=link)[0]
        fout = repdata.resource.read()
        #fout = open ('/home/alessandro/poste_amazon.pdf', "rb")
        response = HttpResponse(fout, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=' + repdata.name
        return response