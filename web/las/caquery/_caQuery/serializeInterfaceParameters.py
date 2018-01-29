#!/usr/bin/python

# Set up the Django Enviroment
import sys
sys.path.append('/home/alberto/Lavoro/svn/caQuery/caQuery/src/caquery/')
from django.core.management import setup_environ 
import settings 
setup_environ(settings)

import json
import datetime

from _caQuery.models import *


def serializeToJson():
    
    json_texts = {}
    
    rows = Parameter.objects.all()
    d = {}
    for r in rows:
        item = {}
        item['name'] = r.name
        item['userprovided'] = r.userprovided
        item['type_id'] = r.type_id_id
        item['button_id'] = r.button_id_id
        item['api_id'] = r.api_id_id
        d[r.id] = item
    json_texts['Parameter'] = unicode(json.dumps(d))
    
    rows = Value.objects.all()    
    d = {}
    for r in rows:
        item = {}
        item['value'] = r.value
        item['parameter_id'] = r.parameter_id_id
        d[r.id] = item
    json_texts['Value'] = unicode(json.dumps(d))
    
    rows = Button.objects.all()
    d = {}
    for r in rows:
        item = {}
        item['name'] = r.name
        item['category_id'] = r.category_id_id
    #    item['type_id'] = r.type_id
        item['num_inputs'] = r.num_inputs
        item['block_title'] = r.block_title
        item['configurable'] = r.configurable
        d[r.id] = item
    json_texts['Button'] = unicode(json.dumps(d))
    
    rows = button_compatibility.objects.all()
    l = []
    for r in rows:
        item = {}
        item['id1'] = r.id1_id
        item['id2'] = r.id2_id
        l.append(item)
    json_texts['button_compatibility'] = unicode(json.dumps(l))
    
    rows = Type.objects.all()
    d = {}
    for r in rows:
        item = {}
        item['name'] = r.name
        d[r.idtype] = item
    json_texts['Type'] = unicode(json.dumps(d))
    
    rows = API.objects.all()
    d = {}
    for r in rows:
        item = {}
        item['name'] = r.name
        item['service_id'] = r.service_id_id
        d[r.id] = item
    json_texts['API'] = unicode(json.dumps(d))
    
    rows = Service.objects.all()
    d = {}
    for r in rows:
        item = {}
        item['url'] = r.url
        d[r.id] = item
    json_texts['Service'] = unicode(json.dumps(d))
    
    rows = Category.objects.all()
    d = {}
    for r in rows:
        item = {}
        item['name'] = r.name
        d[r.id] = item
    json_texts['Category'] = unicode(json.dumps(d))
    
    for k in json_texts.keys():
        try:
            st = SerializedTable.objects.get(pk=k)
            if st.json_text != json_texts[k]:
                st.delete()
                st = None
        except:
            st = None
        if st is None:
            st = SerializedTable(table_name = k, json_text = json_texts[k], last_modified = datetime.datetime.now())
            st.save()
            print "updating table " + k
        else:
            print "not updating table " + k


if __name__=='__main__':
    serializeToJson()
