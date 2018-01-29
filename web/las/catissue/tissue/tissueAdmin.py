from __init__ import *
from django.db.models import get_model
import json

@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_admin')
def start(request):
    print 'BBM VIEW: start tissueadmin.start'
    if request.method == 'POST':
        try:
            req = json.loads(request.POST['d'])
            model = duh.escape(req['model'])
            dataR = req['dataR']
            print 'dataR',dataR
            for key,val in dataR.items():
                vnuovo=duh.escape(val)
                dataR[key]=vnuovo
            print 'data dopo',dataR
            get_model('tissue', model).objects.create(**dataR)
            return HttpResponse('Added new record.')
        except Exception, e:
            print e
            return HttpResponse(e)
    if 'nameT' in request.GET:
        print 'get'
        nameT = request.GET['nameT']
        print "'"+nameT+"'"
        try:
            model_class = get_model('tissue', nameT)
            print 'model_class',model_class
            test = []
            for record in model_class.objects.all():
                #print 'field names',record._meta.fields
                temp = {}
                for field in record._meta.fields:
                    #print 'field',field
                    f =  getattr(record, field.name)
                    #print 'f',f
                    if str(f) == "None":
                        f = ""
                    temp[field.name] = f
                test.append(temp)            
            if len(test)==0:
                print 'model class',model_class
                temp={}
                for field in model_class._meta.fields:
                    temp[field.name] = ''
                test.append(temp)
            print 'test',test
            return HttpResponse(json.dumps(test), content_type="application/json")
        except Exception, e:
            print 'err',e
    tables = {'Collection Type':{'nameT':'CollectionType', 'attrs':{'abbreviation':'string|y|3','longName':'string|y|30'}},
              'Aliquot Type':{'nameT':'AliquotType', 'attrs':{'abbreviation':'string|y|4','longName':'string|y|20','type':'string|y|20'}},
              #'Clinical Feature':{'nameT':'ClinicalFeature', 'attrs':{'name':'string|y|30','measureUnit':'string|n|20','type':'string|n|30'}},
              'Courier':{'nameT':'Courier', 'attrs':{'name':'string|y|50'}},
              'Instrument':{'nameT':'Instrument', 'attrs':{'name':'string|y|45','code':'string|y|45','manufacturer':'string|n|45','description':'text|n|150'}},
              'Mouse Tissue':{'nameT':'MouseTissueType', 'attrs':{'abbreviation':'string|y|3','longName':'string|y|30'}},
              #'Source':{'nameT':'Source', 'attrs':{'name':'string|y|45','type':'string|y|30'}},
              'Tissue Type':{'nameT':'TissueType', 'attrs':{'abbreviation':'string|y|2','longName':'string|y|30'}},
    }
    return render_to_response('tissue2/admin/admin.html',{'tables':tables}, RequestContext(request))
