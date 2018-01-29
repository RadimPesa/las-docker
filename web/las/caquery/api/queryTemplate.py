from piston.handler import BaseHandler
import json

#debugging
import sys, os


from _caQuery.models import *
from _caQuery.views import run_query

class ListTemplates(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        res = [(x.id, x.name, x.description) for x in QueryTemplate.objects.all().order_by('id')]
        return res

class DescribeTemplate(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        if 'template_id' not in request.GET:
            return "Mandatory parameter 'template_id'"
        template_id = request.GET['template_id']
        res = {}
        try:
            t = QueryTemplate.objects.get(pk=template_id)
            par = json.loads(t.parameters)
        except:
            return "No such template"
        try:
            res['id'] = template_id
            res['name'] = t.name
            res['description'] = t.description
            if len(par) > 0:
                res['parameters'] = []
            for i,p in enumerate(par):
                x = {}
                x['id'] = i
                x['name'] = p['name']
                x['description'] = p['description']
                x['type'] = p['type']
                if p['type'] == 1:
                    f = Filter.objects.get(pk=p['src_f_id'])
                    if 'src_main_flt_values' in p:
                        x['values'] = [
                        {
                            'id': y.id,
                            'value': y.valueForDisplay,
                            'subvalues': [
                            {
                                'name': s.jtAttr.name,
                                'description': s.jtAttr.description,
                                'type': s.jtAttr.attrType_id
                            } for s in y.filter_set.all()]
                        } for y in f.jtAttr.jtavalue_set.all()]
                    else:
                        x['values'] = [{'id': y.id, 'value': y.valueForDisplay} for y in f.jtAttr.jtavalue_set.all()]
                if p['type'] == 5:
                    f = Filter.objects.get(pk=p['src_f_id'])
                    x['api_id'] = f.autocomplete_api_id
                res['parameters'].append(x)
            return res
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return (exc_type, fname, exc_tb.tb_lineno, str(e))


class RunTemplate(BaseHandler):
    allowed_methods = ('POST')
    def create(self, request):
        try:
            print "Request: ", request.POST
            template_id = json.loads(request.POST['template_id'])
        except:
            return 'Request must include at least a "template_id" parameter.'
        try:
            t = QueryTemplate.objects.get(pk=template_id)
            template_parameters = json.loads(t.parameters)
            try:
                parameters = json.loads(request.POST['parameters'])
            except:
                parameters = []
    
            import random, string
            N = 32
            query_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))

            query_dict = {
            "1":
                {
                    "button_id":6,
                    "parameters": [], # fill
                    "outputs":[],
                    "query_path_id":[None],
                    "w_in":[],# fill
                    "w_out":["end"],
                    "button_cat":"op",
                    "output_type_id":None, # fill
                    "offsetX":300,
                    "offsetY":120,
                    "template_id":None # fill
                },
            "start":
                {
                    "parameters":None,
                    "query_path_id":[None],
                    "w_out":[], # fill
                    "offsetX":0,
                    "offsetY":0
                },
            "end":
                {
                    "parameters":None,
                    "query_path_id":[None],
                    "w_in":["1"],
                    "offsetX":0,
                    "offsetY":0,
                    "translators": []
                }
            }
            res = {}

            if len(template_parameters) == 0 and len(parameters) != 0:
                res['warning'] = "Template " + str(template_id) + " has no parameters, ignoring parameters"
            else:
                for p in parameters:
                    pp = {}
                    pp['f_id'] = str(p['id'])

                    try:
                        thisParam = template_parameters[int(p['id'])]
                    except:
                        return "Invalid parameter id: " + str(p['id'])
                    print thisParam
                    if thisParam['type'] not in [1,4,7] :
                        # prepend 'u' ('uncorrelated') to parameter values, except if parameter type is predefined list (for which correlation is not allowed)
                        pp['values'] = ['u' + v for v in p['values']]
                    elif thisParam['type'] == 4:
                        pp['values'] = [v for v in p['values']]
                    else:
                        pp['values'] = []
                        for v in p['values']:
                            try:
                                jtValue = JTAValue.objects.get(jtAttr_id= Filter.objects.get(id=thisParam['src_f_id']).jtAttr_id , valueForDisplay=v)
                                pp['values'].append(jtValue.value)
                            except Exception as e:
                                print e
				pass
                    if 'subvalues' in p:
                        pp['subvalues'] = [['u' + x for x in sv]for sv in p['subvalues']]
                    query_dict['1']['parameters'].append(pp)
            
            query_dict['1']['output_type_id'] = t.outputEntity_id
            query_dict['1']['template_id'] = str(template_id)
            query_dict['start']['w_out'] = ["1." + str(i) for i in xrange(t.querytemplate_has_input_set.count())]
            query_dict['1']['w_in'] = ["start" for i in xrange(t.querytemplate_has_input_set.count())]

            print "RunTemplate API: query submitted"
            print "Query dict:", query_dict
            print "Query id:", query_id
            h, b, trans_meta, trans_data, out_e = run_query(query_dict, query_id)
            print "Results: "
            print len(b), "records"

            res['header'] = h
            if trans_meta != None:
                res['body'] = [x + [ [trans_data[int(x[0])][k] for k in sorted(trans_data[int(x[0])])] ] for x in b]
                res['trans_meta'] = [trans_meta[k] for k in sorted(trans_meta)]
            else:
                res['body'] = b
            return res
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return (exc_type, fname, exc_tb.tb_lineno)
            #return str(e)

