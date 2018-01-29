from __init__ import *
from basic import *
from queryClass import Query, QTNode,QTree
from views_query import *


@laslogin_required  
@login_required
@permission_decorator('_caQuery.can_view_MDAM_query_generator')
def createTemplate(request):
    if request.method == 'POST':
        print request.POST
        bq = json.loads(request.POST['base_query'])
        qtid = request.POST['templateid']
        if qtid:
            t = QueryTemplate.objects.get(pk=qtid)
        else:
            t = QueryTemplate()

        t.name = request.POST['title']
        t.description = request.POST['description']
        conf = json.loads(request.POST['configuration'])
        print 'conf', conf
        t.isTranslator = json.loads(request.POST['isTranslator'])
        t.outputTranslatorsList = json.dumps(bq['end']['translators'])
        
        if t.isTranslator == True:
            firstBlockId = bq['start']['w_out'][0].split('.')[0]
            # set translator input type
            t.translatorInputType = QueryableEntity.objects.get(pk=bq[firstBlockId]['button_id'])
            # delete first block
            secondBlockId = bq[firstBlockId]['w_out'][0].split('.')[0]
            bq['start']['w_out'][0] = bq[firstBlockId]['w_out'][0]
            bq[secondBlockId]['w_in'][0] = bq[firstBlockId]['w_in'][0]
            del bq[firstBlockId]
            # copy input conf from first to second block
            conf[secondBlockId]['inputs'] = conf[firstBlockId]['inputs']
            # delete first block's conf
            del conf[firstBlockId]
        bq1 = deepcopy(bq)
        del bq1['start']
        del bq1['end']

        t.baseQuery = json.dumps(bq1)
        t.configuration = json.dumps(conf)

        last_id = bq['end']['w_in'][0]
        t.outputEntity = QueryableEntity.objects.get(pk=bq[last_id]['output_type_id'])
        t.outputBlockId = last_id
        if bq1[last_id]['button_cat'] == 'qent':
            outputsList = json.dumps([])
        elif bq1[last_id]['button_cat'] == 'op':
            if bq1[last_id]['button_id'] == 4: # group by
                outputsList = json.dumps([x['name'] for x in bq1[last_id]['outputs'] if x != None])
            elif bq1[last_id]['button_id'] == 7: # extend
                outputsList = json.dumps([x for x in bq1[last_id]['outputs'] if x != None])
            elif bq1[last_id]['button_id'] == 6: # template
                outputsList = QueryTemplate.objects.get(pk=bq1[last_id]['template_id']).outputsList
            else:
                outputsList = json.dumps([])
        t.outputsList = outputsList
        t.save()
        
        # input entities
        if not qtid:
            for j, x in enumerate(bq['start']['w_out']):
                bid, iid = x.split('.')
                curr_id = bid
                curr_iid = iid
                while 'output_type_id' not in bq[curr_id]:
                    curr_id, curr_iid = bq[curr_id]['w_out'][0].split('.')
                
                qti = QueryTemplate_has_input()
                qti.queryTemplate = t
                if bq[curr_id]['button_cat'] == 'qent':
                    qti.entity = QueryableEntity.objects.get(pk=bq[curr_id]['button_id'])
                elif bq[curr_id]['button_cat'] == 'op' and bq[curr_id]['button_id'] == 6:
                    qti.entity = QueryTemplate_has_input.objects.get(queryTemplate_id=bq[curr_id]['template_id'],no=curr_iid).entity
                qti.no = j
                qti.blockId = bid
                qti.inputId = iid
                qti.name = conf[bid]['inputs'][iid]['name']
                qti.description = conf[bid]['inputs'][iid]['description']
                qti.save()
        
        # save template wg
        wgList = get_WG()
        print wgList
        for wg in wgList:
            templwg=QueryTemplateWG.objects.get_or_create(queryTemplate=t,WG=WG.objects.get(name=wg))

        generate_querygen_json()
        return HttpResponseRedirect(reverse("_caQuery.views.home"))

    elif request.method == 'GET':
        if 'check_template_name' in request.GET:
            tname = request.GET['check_template_name']
            tqid = request.GET['tqid']
            transid = request.GET['transid']
            #print transid, tqid, tname
            
            try:
                q = QueryTemplate.objects.get(name=tname)
                if tqid != 'null':
                    if q.pk == int(tqid):
                        raise Exception('same template')
                if transid != 'null':
                    if q.pk == int(transid):
                        raise Exception('same template')
                return HttpResponse('true')
            except:
                print 'return false'
                return HttpResponse('false')

        else:
            return HttpResponse()

@laslogin_required   
@login_required
@permission_decorator('_caQuery.can_view_MDAM_configuration')
def datasources(request):
    if request.method == 'GET':
        if "dsData" in request.GET:
            ds = request.GET['dsData']
            res = DataSource.objects.filter(pk=ds).values()
            return HttpResponse(json.dumps(res[0]))
        else:
            datasrc = DataSource.objects.all()
            return render_to_response("datasources.html", {'name':request.user.username, 'datasrc': datasrc}, RequestContext(request))

    elif request.method == 'POST':
        print request.POST
        print request.FILES

        with transaction.commit_manually():

            if "dropDs" in request.POST:
                ds = request.POST['dropDs']
                try:
                    DataSource.objects.get(pk=ds).delete()
                except Exception as e:
                    transaction.rollback()
                    #return HttpResponseServerError("DataSource not found")
                    return HttpResponseServerError(str(e))
                else:
                    transaction.commit()
                    return HttpResponse("OK")
                
            elif "newDs" in request.POST:

                print "new data source"
                ds = request.POST['newDs']
                if ds == '':
                    #new ds
                    try:
                        DataSource.objects.get(name=request.POST['name'])
                        return HttpResponseServerError("Data source " + request.POST['name'] + " already exists!")
                    except:
                        pass

                    try:
                        ds = DataSource()
                        ds.name = request.POST['name']
                        ds.description = request.POST['descr']
                        ds.color = request.POST['color']
                        ds.colorHover = request.POST['colorh']
                        ds.colorClicked = request.POST['colorc']
                        url = request.POST['url']
                        if not url.endswith('/'):
                            url = url + '/'
                        ds._url = url

                        f = request.FILES['icon']
                        
                        print "Ricevuto file: ", f.name
 
                        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, 'images', f.name)) == True:
                            i = 0
                            fname, fext = os.path.splitext(f.name)
                            while os.path.isfile(os.path.join(settings.MEDIA_ROOT, 'images', fname + '_' + str(i) + fext)) == True:
                                i += 1
                            dest_file = fname + '_' + str(i) + fext
                        else:
                            dest_file = f.name
                        
                        with open(os.path.join(settings.MEDIA_ROOT, 'images', dest_file), 'wb+') as destination:
                            for chunk in f.chunks():
                                destination.write(chunk)
                                
                        ds.iconUrl = settings.MEDIA_URL + '/images/' + dest_file
                        ds.iconUrl = re.sub("[\/]+", "/", ds.iconUrl)

                        ds.save()
                        generate_datasource_css()

                    except Exception as e:
                        transaction.rollback()
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        return HttpResponseServerError(str((exc_type, fname, exc_tb.tb_lineno, str(e))))

                    else:
                        transaction.commit()
                        
                        return HttpResponse(ds.pk)
                    
                else:
                    #update existing ds
                    try:
                        ds = DataSource.objects.get(pk=ds)
                        ds.name = request.POST['name']
                        ds.description = request.POST['descr']
                        ds.color = request.POST['color']
                        ds.colorHover = request.POST['colorh']
                        ds.colorClicked = request.POST['colorc']
                        url = request.POST['url']
                        if not url.endswith('/'):
                            url = url + '/'
                        ds.url = url
                        
                        if 'icon' in request.FILES:
                            f = request.FILES['icon']
                            if os.path.isfile(os.path.join(settings.MEDIA_ROOT, 'images', f.name)) == True:
                                i = 0
                                fname, fext = os.path.splitext(f.name)
                                while os.path.isfile(os.path.join(settings.MEDIA_ROOT, 'images', fname + '_' + str(i) + fext)) == True:
                                    i += 1
                                dest_file = fname + '_' + str(i) + fext
                            else:
                                dest_file = f.name
                            
                            with open(os.path.join(settings.MEDIA_ROOT, 'images', dest_file), 'wb+') as destination:
                                for chunk in f.chunks():
                                    destination.write(chunk)
                                    
                            ds.iconUrl = settings.MEDIA_URL + 'images/' + dest_file

                        ds.save()

                        generate_datasource_css()

                    except Exception as e:
                        transaction.rollback()
                        return HttpResponseServerError(str(e))
                    else:
                        transaction.commit()
                        
                        return HttpResponse(ds.pk)

            elif "refreshDs" in request.POST:
                #refresh schema of existing ds
                try:
                    ds = request.POST['refreshDs']
                    ds = DataSource.objects.get(pk=ds)
                    url = urlparse.urljoin(ds.url, GETDBSCHEMA_API)
                    print url
                    r = requests.get(url, verify=False)
                    print r
                    dbschema = r.json()
                    ent = dbschema['entities']
                    rel = dbschema['relationships']

                    for k,v in ent.items():
                        try:
                            dst = DSTable.objects.get(name=k,dataSource=ds)
                        except:
                            dst = DSTable()
                            dst.name = k
                        dst.dataSource = ds
                        dst.attrList = json.dumps(v['fields'])
                        dst.primaryKey = v['pkey']
                        dst.save()

                    print "DSTable objects saved"

                    for x in rel:
                        dst_from = DSTable.objects.get(name=x[0],dataSource=ds)
                        dst_to = DSTable.objects.get(name=x[1],dataSource=ds)
                        # forward relationship (one-to-many)
                        try:
                            dsr = DSRelationship.objects.get(fromDSTable=dst_from,toDSTable=dst_to,leftRelatedAttr=x[2])
                        except:
                            dsr = DSRelationship()
                            dsr.fromDSTable = dst_from
                            dsr.toDSTable = dst_to
                            dsr.leftRelatedAttr = x[2]
                        dsr.rightRelatedAttr = x[3]
                        dsr.oneToMany = True
                        dsr.save()
                        # backward relationship (many-to-one)
                        try:
                            dsr = DSRelationship.objects.get(fromDSTable=dst_to,toDSTable=dst_from,leftRelatedAttr=x[3])
                        except:
                            dsr = DSRelationship()
                            dsr.fromDSTable = dst_to
                            dsr.toDSTable = dst_from
                            dsr.leftRelatedAttr = x[3]
                        dsr.rightRelatedAttr = x[2]
                        dsr.oneToMany = False
                        dsr.save()

                    print "DSRelationship objects saved"

                except Exception,e:
                    transaction.rollback()
                    print "exception"
                    print e
                    return HttpResponseServerError(str(e))
                else:
                    transaction.commit()
                    return HttpResponse("OK")

def generate_datasource_css():
    print "Generating CSS..."
    with open(os.path.join(settings.MEDIA_ROOT, 'css', 'ds.css'), 'w') as css:
        template = """.%s {
    background-color: %s;
}
.%s:hover {
    background-color: %s;
}
.%s.clicked {
    background-color: %s;
}
.%s.clicked:hover {
    background-color: %s;
}
p.box.%s {
    background-color: %s;
    background-image: -webkit-gradient(linear, left top, left bottom, from(%s), to(%s)); /* Saf4+, Chrome */
    background-image: -webkit-linear-gradient(top, %s, %s); /* Chrome 10+, Saf5.1+, iOS 5+ */
    background-image:    -moz-linear-gradient(top, %s, %s); /* FF3.6 */
    background-image:     -ms-linear-gradient(top, %s, %s); /* IE10 */
    background-image:      -o-linear-gradient(top, %s, %s); /* Opera 11.10+ */
    background-image:         linear-gradient(top, %s, %s);
    filter: progid:DXImageTransform.Microsoft.gradient(startColorStr='%s', EndColorStr='%s'); /* IE6-IE9 */
}

"""

        ds = DataSource.objects.all()
        for x in ds:
            name = x.name.lower().replace(' ', '_')
            css.write(template % (name, x.color, name, x.colorHover, name, x.colorClicked, name, x.colorClicked, name, x.color, x.color, x.colorHover, x.color, x.colorHover, x.color, x.colorHover, x.color, x.colorHover, x.color, x.colorHover, x.color, x.colorHover, x.color, x.colorHover))
    print css.name + " written"

def generate_querygen_json():
    print "Generating JSON..."
    with open(os.path.join(settings.MEDIA_ROOT, 'js', 'qent.json'), 'w') as js:
        template = '''/******************************************
This file has been automatically generated.
Please do not edit.

Created %s
*******************************************/

var qent = %s;

var ops = %s;

var genid = %s;

var templates = %s;
'''
        
        #Queryable Entities
        qe = {}
        for x in QueryableEntity.objects.filter(enabled=True):
            curr_qe = {}
            
            curr_qe['name'] = x.name
            curr_qe['dslabel'] = x.dsTable.dataSource.name.lower().replace(' ', '_')
            curr_qe['description'] = x.description
            curr_qe['genid_prefilter'] = x.genid_prefilter
            curr_qe['hasWG'] = True if len(x.filter_set.filter(jtAttr__attrType=AttributeType.objects.get(name='Working Group'))) > 0 else False            

            filt = {}
            for y in x.filter_set.filter(parentFilter=None):
                filt[y.id] = {  'name': y.jtAttr.name,
                            'description': y.jtAttr.description,
                            'type': y.jtAttr.attrType_id,
                            'multiValued': y.multiValued,
                            'batchInput': y.batchInput,
                            'fileInput': y.fileInput,
                            'api_id': y.autocomplete_api_id,
                            'genid': [z.relatedGenIDType.name for z in GenIDType_has_Filter.objects.filter(relatedFilter=y) ],
                            'values': []}

                for z in y.jtAttr.jtavalue_set.filter(hasBeenExcluded=False).order_by('valueForDisplay'):
                    try:
                        f_child = Filter.objects.get(parentFilter=y,parentValue=z)
                        f_child_id = f_child.id
                        f_child_name = f_child.jtAttr.name
                        f_child_type = f_child.jtAttr.attrType_id
                    except:
                        f_child_id = None
                        f_child_name = None
                        f_child_type = None
                    filt[y.id]['values'].append((z.value, z.valueForDisplay, f_child_id, f_child_name, f_child_type))
            curr_qe['filters'] = filt
            
            output = {}
            for y in x.output_set.all():
                output[y.id] = {    'name': y.name }
            curr_qe['outputs'] = output
            
            curr_qe['fw_query_paths'] = {}
            for y in QueryPath.objects.filter(fromQEntity=x):
                curr_qe['fw_query_paths'][y.id] = {'toEntity': y.toQEntity.id, 'oneToMany': y.oneToMany, 'name': y.name, 'description': y.description, 'isDefault': y.isDefault}
            
            qe[x.id] = curr_qe

        #Operators
        ops = {}
        for x in Operator.objects.all():
            ops[x.id] = {   'name': x.name,
                            'description': x.description,
                            'numInputs': x.numInputs,
                            'configurable': x.configurable,
                            'outFromIn': x.outTypeDependsOnIn,
                            'outFromConf': x.outTypeDependsOnConf,
                            'canBeFirst': x.canBeFirst,
                            'canBeLast': x.canBeLast}

        # Genealogy ID
        genid = {}
        for x in GenIDType.objects.all().order_by('name'):
            genid[x.name] = {'fields': [{'name': y.name, 'start': y.start, 'end': y.end, 'ftype': y.field_type.id, 'values': [z.value for z in y.genidfieldvalue_set.all().order_by('value')]} for y in x.genidfield_set.all().order_by('start')] } #relatedQE eliminato

        # templates
        templates = {}
        for x in QueryTemplate.objects.all().order_by('name'):
            inputs = [{'qent_id': y.entity_id, 'name': y.name, 'description': y.description} for y in x.querytemplate_has_input_set.all().order_by('no')]
            base_query = json.loads(x.baseQuery)
            conf = json.loads(x.configuration)
            parameters = []
            parameters_small = []
            valSubfltMap = {}
            for block_id, cfg in conf.iteritems():
                # pre-load source template data if block is template
                if base_query[block_id]['button_cat'] == 'op' and base_query[block_id]['button_id'] == 6:
                    src_templ_id = base_query[block_id]['template_id']
                    src_templ = QueryTemplate.objects.get(pk=src_templ_id)
                    src_templ_par = json.loads(src_templ.parameters)
                for i, par in cfg['parameters'].iteritems():
                    i = int(i)
                    if par['opt'] == '2' or par['opt'] == '3':
                        if base_query[block_id]['button_cat'] == 'qent':
                            # block is an entity, parameter is linked to an entity parameter
                            f_id = base_query[block_id]['parameters'][i]['f_id']
                            p = {'bq_par_id': i,
                                'src_block_id': block_id,
                                'src_button_id': base_query[block_id]['button_id'],
                                'src_f_id': f_id,
                                'type': Filter.objects.get(pk=f_id).jtAttr.attrType_id,
                                'name': par['name'],
                                'description': par['description']}
                            p_small = {'src_button_id': base_query[block_id]['button_id'],
                                'src_f_id': f_id,
                                'type': Filter.objects.get(pk=f_id).jtAttr.attrType_id,
                                'name': par['name'],
                                'description': par['description']}
                            if par['opt'] == '3':
                                # main filter is locked, subfilters are free
                                par_flt_values = base_query[block_id]['parameters'][i]['values']
                                p['src_main_flt_values'] = par_flt_values
                                p_small['src_main_flt_values'] = par_flt_values
                                par_flt = Filter.objects.get(pk=f_id)
                                par_flt_val_objects = par_flt.jtAttr.jtavalue_set.filter(value__in=par_flt_values)
                                mapping = {w.parentValue.value : w.id for w in Filter.objects.filter(parentFilter__id=f_id,parentValue__in=par_flt_val_objects)}
                                if len(mapping) > 0:
                                    mapping.update(valSubfltMap.get(f_id, {}))
                                    valSubfltMap[f_id] = mapping
                            elif p['type'] == 1:
                                mapping = {w.parentValue.value : w.id for w in Filter.objects.filter(parentFilter__id=f_id)}
                                if len(mapping) > 0:
                                    mapping.update(valSubfltMap.get(f_id, {}))
                                    valSubfltMap[f_id] = mapping

                        else:
                            # block is an operator
                            if base_query[block_id]['button_id'] == 6:
                                # template
                                # block is a template, current template's parameter is linked to the original block (entity or gb/genid) parameter
                                src_templ_par_id = int(base_query[block_id]['parameters'][i]['f_id'])
                                f_type = src_templ_par[src_templ_par_id]['type']
                                p = {'bq_par_id': i,
                                    'src_block_id': block_id,
                                    'type': f_type,
                                    'name': par['name'],
                                    'description': par['description']}
                                p_small = {'type': f_type,
                                    'name': par['name'],
                                    'description': par['description']}

                                if 'src_f_id' in src_templ_par[src_templ_par_id]:
                                    # original block was an entity
                                    f_id = src_templ_par[src_templ_par_id]['src_f_id']
                                    button_id = src_templ_par[src_templ_par_id]['src_button_id']
                                    p['src_button_id'] = button_id
                                    p['src_f_id'] = f_id
                                    p_small['src_button_id'] = button_id
                                    p_small['src_f_id'] = f_id

                                if par['opt'] == '3':
                                    # main filter is locked, subfilters are free
                                    par_flt_values = base_query[block_id]['parameters'][i]['values']
                                    p['src_main_flt_values'] = par_flt_values
                                    p_small['src_main_flt_values'] = par_flt_values
                                    par_flt = Filter.objects.get(pk=f_id)
                                    par_flt_val_objects = par_flt.jtAttr.jtavalue_set.filter(value__in=par_flt_values)
                                    mapping = {w.parentValue.value : w.id for w in Filter.objects.filter(parentFilter__id=f_id,parentValue__in=par_flt_val_objects)}
                                    if len(mapping) > 0:
                                        mapping.update(valSubfltMap.get(f_id, {}))
                                        valSubfltMap[f_id] = mapping
                                elif p['type'] == 1:
                                    mapping = {w.parentValue.value : w.id for w in Filter.objects.filter(parentFilter__id=f_id)}
                                    if len(mapping) > 0:
                                        mapping.update(valSubfltMap.get(f_id, {}))
                                        valSubfltMap[f_id] = mapping
                            else:
                                # if group by (id == 4), then type is numeric (3), else (genealogy id) it is text (4)
                                p = {'bq_par_id': i,
                                    'src_block_id': block_id,
                                    'type': 3 if base_query[block_id]['button_id'] == 4 else 4,
                                    'name': par['name'],
                                    'description': par['description']}
                                p_small = {'type': 3 if base_query[block_id]['button_id'] == 4 else 4,
                                    'name': par['name'],
                                    'description': par['description']}
                        parameters.append(p)
                        parameters_small.append(p_small)
            
            templwg = [wg for wg in QueryTemplateWG.objects.filter(queryTemplate=x).values_list('WG__name', flat =True)]
            templates[x.id] = {'name': x.name, 'description': x.description, 'inputs': inputs, 'output': x.outputEntity_id, 'parameters': parameters_small, 'outputsList': json.loads(x.outputsList), 'isTranslator': x.isTranslator, 'translatorInputType': x.translatorInputType_id, 'WG': templwg }
            x.parameters = json.dumps(parameters)
            x.valueSubfilterMapping = json.dumps(valSubfltMap)
            x.save()
        
        js.write(template % (datetime.datetime.now(), json.dumps(qe), json.dumps(ops), json.dumps(genid), json.dumps(templates)))

def loadGenIDFields():
    for x in GenIDField.objects.all():
        if x.dsTable != None:
            #retrieve data from remote table
            from queryClass import Query,QTree
            q = Query()
            q.ds = x.dsTable.dataSource
            q.sel.append((x.dsTable.name, x.attrName))
            q.fro.append(x.dsTable.name)
            q.distinct = True
            qt = QTree()
            res = qt.compile_and_send_query(q, get_handle=False)
            field_len = x.end - x.start + 1
            print "Result: ", res
            for y in res:
                if len(y[0]) == field_len:
                    try:
                        v = GenIDFieldValue.objects.get(genid_field=x,value=y[0])
                    except:
                        v = GenIDFieldValue()
                        v.genid_field = x
                        v.value = y[0]
                        v.save()
                else:
                    print "discarding value: ", y[0]

@laslogin_required
@login_required
@permission_decorator('_caQuery.can_view_MDAM_configuration')
def manageqe(request):
    if request.method == 'GET':
        if 'ds' in request.GET:
            ds_id = request.GET['ds']
            ds = DataSource.objects.get(pk=ds_id)
            dst = DSTable.objects.filter(dataSource=ds)
            qe = QueryableEntity.objects.filter(dsTable__in=dst).order_by('name')
            datasrc = DataSource.objects.all().order_by('name')
            return render_to_response("manageqe.html", {'name':request.user.username, 'datasrc': datasrc, 'qe': qe, 'ds': ds}, RequestContext(request))
        else:
            datasrc = DataSource.objects.all().order_by('name')
            return render_to_response("manageqe.html", {'name':request.user.username, 'datasrc': datasrc}, RequestContext(request))
    
    elif request.method == 'POST':
        if 'dropQe' in request.POST:
            qe_id_list = request.POST.getlist('dropQe')

            templates = checkTemplates(None, None, [ int(x) for x in qe_id_list] )
            if len(templates.keys()) == 0:
                for x in qe_id_list:
                    try:
                        #pass
                        QueryableEntity.objects.get(pk=x).delete()
                    except:
                        continue
                generate_querygen_json()
                return HttpResponse("ok")
            else:
                respText = ''
                for tVal in templates.values():
                    respText += '<br>' +tVal['name']
                return HttpResponseServerError("Entity is used by the following templates: " + respText)
            
            
@laslogin_required
@login_required
def newqe(request):
    if request.method == 'GET':
        if "ds" in request.GET:
            print "ds in request"
            ds_id = request.GET['ds']
            ds = DataSource.objects.get(pk=ds_id)
            dst = DSTable.objects.filter(dataSource=ds).order_by('name')
            attrtype = AttributeType.objects.all()
            genidtypes = GenIDType.objects.all()
            if "qe" in request.GET:
                qe_id = request.GET['qe']
                qe = QueryableEntity.objects.get(pk=qe_id)
                return render_to_response("newqe.html", {'name':request.user.username, 'ds': ds, 'dst': dst, 'attrtype': attrtype, 'qe':qe, 'genidtypes': genidtypes}, RequestContext(request))
            else:
                return render_to_response("newqe.html", {'name':request.user.username, 'ds': ds, 'dst': dst, 'attrtype': attrtype, 'genidtypes': genidtypes}, RequestContext(request))



        elif "action" in request.GET:
            action = request.GET['action']

            if action == 'getGenidField':
                dst_id = request.GET['dst']
                dst = DSTable.objects.get(pk=dst_id)
                attrlist = json.loads(dst.attrList)
                res = {'columns': attrlist, 'default': dst.genId}
                return HttpResponse(json.dumps(res))

            elif action == 'reachFromDst':
                
                #return list of tables reachable from current one, structured as follows
                #source table id + name, dest table id + name, relationship id, source table attr, dest table attr, relationship cardinality
                dst_id = request.GET['dst']
                dst = DSTable.objects.get(pk=dst_id)

                all_dst = DSTable.objects.filter(dataSource=dst.dataSource)

                dsr = DSRelationship.objects.filter(fromDSTable=dst, toDSTable__in=all_dst).order_by('toDSTable__name')

                all_paths = []
                for x in dsr:
                    all_paths.append((x.fromDSTable.id, x.fromDSTable.name, x.toDSTable.id, x.toDSTable.name, (x.id, x.leftRelatedAttr,  x.rightRelatedAttr, x.oneToMany)))
                return HttpResponse(json.dumps(all_paths))

            elif action == 'getJndTab':
                dst = request.GET['dst']
                dst_obj = DSTable.objects.get(pk=dst)
                from django.db.models import Count
                jndTab_set = sorted(list(JoinedTable.objects.filter(fromDSTable=dst_obj).exclude(toDSTable=dst_obj)) +
                                list(JoinedTable.objects.filter(fromDSTable=dst_obj,toDSTable=dst_obj).annotate(Count('joinedtable_has_dsrelationship')).filter(joinedtable_has_dsrelationship__count=0)), key=lambda jt:jt.toDSTable.name)
                res = [(j.id, j.toDSTable.name, [(x.dsr.fromDSTable.id, x.dsr.fromDSTable.name, x.dsr.leftRelatedAttr, x.dsr.toDSTable.id, x.dsr.toDSTable.name, x.dsr.rightRelatedAttr, x.dsr.oneToMany) for x in j.joinedtable_has_dsrelationship_set.all()], j.fromDSTable==j.toDSTable) for j in jndTab_set]
                return HttpResponse(json.dumps(res))

            elif action == 'getPath':
                import networkx as nx
                
                from_dst_id = request.GET['fromdst']
                to_dst_id = request.GET['todst']
                to_dst = DSTable.objects.get(pk=to_dst_id)

                if from_dst_id != to_dst_id:
                    from_dst = DSTable.objects.get(pk=from_dst_id)
                    all_dst = DSTable.objects.filter(dataSource=from_dst.dataSource)

                    g = nx.DiGraph()

                    for x in all_dst:
                        g.add_node(x.id, name=x.name)

                    all_dsr = DSRelationship.objects.filter(fromDSTable__in=all_dst, toDSTable__in=all_dst)#, oneToMany=True)
                    
                    for x in all_dsr:
                        g.add_edge(x.fromDSTable.id, x.toDSTable.id, id=x.id, lra=x.leftRelatedAttr, rra=x.rightRelatedAttr, oneToMany=x.oneToMany)
                    
                    try:
                        p = nx.shortest_path(g,source=from_dst.id,target=to_dst.id)
                        path = [(p[i-1], g.node[p[i-1]]['name'], g.edge[p[i-1]][p[i]]['lra'], p[i], g.node[p[i]]['name'], g.edge[p[i-1]][p[i]]['rra'], g.edge[p[i-1]][p[i]]['oneToMany']) for i in xrange(1, len(p))]
                        path_dsr = [g.edge[p[i-1]][p[i]]['id'] for i in xrange(1, len(p))]
                    except Exception as e:
                        path = None
                        path_dsr = None
                else:
                    path = []
                    path_dsr = []

                res = {}
                res['manytoone'] = not all([x[6] for x in path])
                res['path'] = path
                res['dsr'] = path_dsr

                
                return HttpResponse(json.dumps(res))

            elif action == 'getJtAttrs':
                jndTab_id = request.GET['jndTab']

                attrs = [(x.id, "%s (%s)"%(x.name, x.attrType.name), x.attrType.id) for x in JTAttribute.objects.filter(jndTable_id=jndTab_id).order_by('name')]

                return HttpResponse(json.dumps(attrs))

            elif action == 'getAttrs':
                jndTab_id = request.GET['jndTab']

                jndTab = JoinedTable.objects.get(pk=jndTab_id)
                dst = jndTab.toDSTable

                return HttpResponse(dst.attrList)

            elif action == 'getPredefValues':
                jndTab_id = request.GET['jndTab']
                attr = request.GET['attr']
                vocab = request.GET['vocab']

                dst = JoinedTable.objects.get(pk=jndTab_id).toDSTable

                if vocab == 'attr':
                    attr_list = [attr, attr]
                elif vocab == 'tab':
                    dsr = DSRelationship.objects.get(fromDSTable=dst,leftRelatedAttr=attr)
                    dst = dsr.toDSTable
                    attr_list = json.loads(dst.attrList)

                #retrieve data from remote table
                q = Query()
                q.ds = dst.dataSource
                q.sel.extend([(dst.name, x) for x in attr_list])
                q.fro.append(dst.name)
                q.distinct = True
                qt = QTree()
                data = qt.compile_and_send_query(q, get_handle=False)
                res = {'headers': attr_list, 'data': data, 'dst': dst.id}

                return HttpResponse(json.dumps(res))

            elif action == 'getFilters':
                qe_id = request.GET['qe']
                try:
                    f_list = Filter.objects.filter(qe_id=qe_id,parentFilter=None).order_by('jtAttr__name')
                    # the same parent filter cannot have children filters on more than one distinct attribute
                    # this is not enforced by the model (which in fact allows for multiple filters/attributes
                    # for a single parent filter) but it is forbidden at the application level
                    f_list = [(x.id, x.jtAttr.name, x.filter_set.all()[0].jtAttr.name if x.filter_set.count() > 0 else None, [y.id for y in x.filter_set.all()]) for x in f_list]
                    return HttpResponse(json.dumps(f_list))
                except Exception as e:
                    return HttpResponseServerError(str(e))

            elif action == 'getOutputs':
                qe_id = request.GET['qe']
                try:
                    o_list = list(Output.objects.filter(qe_id=qe_id).order_by('name').values_list('id', 'name'))
                    return HttpResponse(json.dumps(o_list))
                except Exception as e:
                    return HttpResponseServerError(str(e))
            
            elif action == 'getShare':
                qe_id = request.GET['qe']
                try:
                    resp = {'shareable': False, 'output': None}
                    q = QueryableEntity.objects.get(pk=qe_id)
                    if q.shareable == True:
                        resp = {'shareable': q.shareable, 'output': q.outputShareable.name}
                    else:
                        resp = {'shareable': False, 'output': None}
                    return HttpResponse(json.dumps(resp))
                except Exception as e:
                    return HttpResponseServerError(str(e))

            elif action == 'getFilterValues':
                f_id = request.GET['flt']
                try:
                    f = Filter.objects.get(pk=f_id)
                    if f.filter_set.count() > 0:
                        return HttpResponseServerError("A subfilter already exists for this filter.")
                    jta = f.jtAttr
                    values = list(jta.jtavalue_set.all().order_by('valueForDisplay').values_list('id', 'valueForDisplay'))
                    return HttpResponse(json.dumps(values))
                except Exception as e:
                    return HttpResponseServerError(str(e))

        else:
            print "no key in request"
            return render_to_response("newqe.html", {'name':request.user.username}, RequestContext(request))

    elif request.method == 'POST':
        if 'action' in request.POST:
            action = request.POST['action']
            
            if action == 'delJndTab':
                jt = JoinedTable.objects.get(pk=request.POST['jndtab'])
                qe = QueryableEntity.objects.get(pk=request.POST['qe'])
                if jt.fromDSTable == jt.toDSTable:
                    return HttpResponseServerError("Cannot delete source table.")
                jtattrs = JTAttribute.objects.filter(jndTable=jt)
                flts = Filter.objects.filter(jtAttr__in=jtattrs, qe=qe)
                outs = Output_has_JTAttribute.objects.filter(jtAttr__in=jtattrs, output__qe=qe)
                if len(flts) == 0 and len(outs) == 0:
                    jt.delete()
                    return HttpResponse("ok")
                else:
                    return HttpResponseServerError("Joined table is in use by other entities.")

            elif action == 'delJTAttr':
                jta = JTAttribute.objects.get(pk=request.POST['jtattr'])
                qe = QueryableEntity.objects.get(pk=request.POST['qe'])

                flts = Filter.objects.filter(jtAttr=jta, qe=qe)
                outs = Output_has_JTAttribute.objects.filter(jtAttr=jta, output__qe=qe)
                print flts
                print outs
                if len(flts) == 0 and len(outs) == 0:
                    jta.delete()
                    return HttpResponse("ok")
                else:
                    return HttpResponseServerError("Attribute is used by other entities.")

            elif action == 'createqe':
                try:
                    print request.POST
                    qe_dst = request.POST['dst']
                    qe_name = request.POST['name']
                    qe_descr = request.POST['descr']
                    qe_genid = True if request.POST['genid'] == 'yes' else False
                    dst_genidfield = request.POST['genidfield']
                
                    dst = DSTable.objects.get(pk=qe_dst)
                    dst.genId = dst_genidfield;
                    dst.save()

                    qe = QueryableEntity()
                    qe.name = qe_name
                    qe.description = qe_descr
                    qe.dsTable = dst
                    qe.genid_prefilter = qe_genid

                    qe.save()

                    from django.db.models import Count
                    jndt_list = JoinedTable.objects.filter(fromDSTable=dst,toDSTable=dst).annotate(Count('joinedtable_has_dsrelationship')).filter(joinedtable_has_dsrelationship__count=0)
                    if len(jndt_list) == 0:
                        jndt = JoinedTable.getOrCreateJTWithPath(dst,dst, [])
                        jndt.fillSummary()
                        jndt.save()
                    else:
                        jndt = jndt_list[0]

                    return HttpResponse(qe.id)

                except Exception as e:
                    return HttpResponseServerError(str(e))

            elif action == 'createJndTab':
                try:
                    fromDst_id = request.POST['fromDst']
                    toDst_id = request.POST['toDst']
                    path = json.loads(request.POST['path'])

                    fromDst = DSTable.objects.get(pk=fromDst_id)
                    toDst = DSTable.objects.get(pk=toDst_id)

                    jndTab = JoinedTable.getOrCreateJTWithPath(fromDst, toDst, path)

                    return HttpResponse(jndTab.id)

                except Exception as e:
                    return HttpResponseServerError(str(e))

            elif action == 'createAttr':
                name = request.POST['name']
                descr = request.POST['descr']
                jndTab_id = request.POST['jndTab']
                attr = request.POST['attr']
                attrtype = int(request.POST['type'])


                jta = JTAttribute()
                jta.name = name
                jta.description = descr
                jta.jndTable = JoinedTable.objects.get(pk=jndTab_id)
                jta.attrName = attr
                jta.attrType = AttributeType.objects.get(pk=attrtype)

                if attrtype == 1 or attrtype == 6:
                    jta.predefList_Dst = DSTable.objects.get(pk=request.POST['predefList_dst'])
                    jta.predefList_Attr = request.POST['predefList_attr']
                

                jta.save()

                return HttpResponse(jta.id)

            elif action == 'createValues':
                with transaction.commit_manually():
                    try:
                        values_list = json.loads(request.POST['list'])
                        jtattr = JTAttribute.objects.get(pk=request.POST['jtattr'])
                        exclude_list = json.loads(request.POST['excludeList'])
                        for x in values_list:
                            jtav = JTAValue()
                            jtav.jtAttr = jtattr
                            jtav.value = x[0]
                            jtav.valueForDisplay = x[1]
                            jtav.save()
                        for x in exclude_list:
                            jtav = JTAValue()
                            jtav.jtAttr = jtattr
                            jtav.value = x
                            jtav.valueForDisplay = None
                            jtav.hasBeenExcluded = True
                            jtav.save()
                        transaction.commit()
                        return HttpResponse("ok")
                    except Exception as e:
                        transaction.rollback()
                        return HttpResponseServerError(str(e))

            elif action == 'createFlt':
                jta_id = request.POST['jta']
                qe_id = request.POST['qe']
                opts = json.loads(request.POST['opts'])

                try:
                    jta = JTAttribute.objects.get(pk=jta_id)
                    qe = QueryableEntity.objects.get(pk=qe_id)
                except Exception as e:
                    print e
                    return HttpResponseServerError(str(e))

                if "list" in request.POST and "parflt" in request.POST:

                    try:
                        val_type = json.loads(request.POST['list'])
                        parflt = Filter.objects.get(pk=request.POST['parflt'])

                        for val_id, type_id in val_type:
                            try:
                                j = JTAttribute.objects.get(jndTable=jta.jndTable,attrName=jta.attrName,attrType_id=type_id)
                            except:
                                j = JTAttribute()
                                j.name = jta.name
                                j.jndTable = jta.jndTable
                                j.attrName = jta.attrName
                                j.attrType_id = type_id
                                j.save()

                            f = Filter()
                            f.jtAttr = j
                            f.qe = qe
                            f.multiValued = True if 'multi' in opts else False
                            f.batchInput = True if 'batch' in opts else False
                            f.fileInput = True if 'file' in opts else False
                            f.parentFilter = parflt
                            f.parentValue_id = val_id
                            f.save()

                        return HttpResponse("ok")

                    except Exception as e:
                        return HttpResponseServerError(str(e))

                else:

                    f = Filter()
                    f.jtAttr = jta
                    f.qe = qe
                    f.multiValued = True if 'multi' in opts else False
                    f.batchInput = True if 'batch' in opts else False
                    f.fileInput = True if 'file' in opts else False

                    if jta.attrType_id == 5: # text with autcomplete
                        try:
                            api = AutoCompleteAPI.objects.get(dsTable=jta.jndTable.toDSTable,attrName=jta.attrName)
                        except:
                            api = AutoCompleteAPI()
                            api.dsTable = jta.jndTable.toDSTable
                            api.attrName = jta.attrName
                            api.fill_attrs()
                            api.save()
                        f.autocomplete_api = api
                    
                    f.save()
                    if jta.attrType_id == 4: #genid 
                        genidopts = json.loads(request.POST['genidtypes'])
                        print 'genidopts', genidopts
                        for gtype in genidopts:
                            print gtype
                            relatedGenIDType= GenIDType.objects.get(pk=gtype)
                            print relatedGenIDType
                            genidtype_filter = GenIDType_has_Filter(relatedGenIDType=relatedGenIDType, relatedFilter=f)
                            genidtype_filter.save()

                    return HttpResponse(f.id)

            elif action == 'createOut':
                qe_id = request.POST['qe']
                outname = request.POST['outname']
                fnname = request.POST['fnname']
                jta_list = json.loads(request.POST['jta'])

                o = Output()
                o.qe = QueryableEntity.objects.get(pk=qe_id)
                o.name = outname
                o.fnName = fnname

                o.save()

                for x in jta_list:
                    ohj = Output_has_JTAttribute()
                    ohj.no = jta_list.index(x)
                    ohj.output = o
                    ohj.jtAttr = JTAttribute.objects.get(pk=x)
                    ohj.save()

                o.fillSummary()
                o.save()

                return HttpResponse(o.id)

            elif action == 'delFilter':
                f_ids = json.loads(request.POST['f'])
                print f_ids
                templates = checkTemplates([int(f) for f in f_ids ], None, None)
                if len(templates.keys()) == 0:
                    for x in f_ids:
                        try:
                            #pass
                            Filter.objects.get(pk=x).delete()
                        except:
                            continue
                    return HttpResponse("ok")
                else:
                    respText = ''
                    for tVal in templates.values():
                        respText += '<br>' +tVal['name']
                    return HttpResponseServerError("Filter is used by the following templates: " + respText)

            elif action == 'delOutput':
                o_ids = json.loads(request.POST['o'])
                print o_ids
                templates = checkTemplates(None, [ int(o) for o in o_ids],None )
                if len(templates.keys()) == 0:
                    for o_id in o_ids:
                        try:
                            #pass
                            o = Output.objects.get(pk=o_id)
                            qe = o.qe
                            qe.shareable = False
                            qe.outputShareable = None
                            qe.save()
                            o.delete()

                            return HttpResponse("ok")
                        except Exception as e:
                            print e
                            continue
                    return HttpResponseServerError(str(e))
                else:
                    respText = ''
                    for tVal in templates.values():
                        respText += '<br>' +tVal['name']
                    return HttpResponseServerError("Output is used by the following templates: "+ respText)

            elif action == 'enableqe':
                qe_id = request.POST['qe']
                print qe_id
                qe = QueryableEntity.objects.get(pk=qe_id)
                qe.name = request.POST['qe_name']
                qe.description = request.POST['qe_description']
                qe.enabled = True
                qe.save()

                generate_querygen_json()

                return HttpResponseRedirect(('%s?ds='+str(qe.dsTable.dataSource.id)) % reverse('_caQuery.views.manageqe'))

            elif action == 'shareOutput':
                o_id = json.loads(request.POST['o'])
                print o_id
                o = Output.objects.get(pk=o_id)
                qe = o.qe
                qe.shareable = True
                qe.outputShareable = o
                qe.save()
                return HttpResponse(o.id)

            elif action == 'unshare':

                qe_id = request.POST['qe']
                qe = QueryableEntity.objects.get(pk=qe_id)
                qe.shareable = False
                qe.outputShareable = None
                qe.save()
                return HttpResponse("ok")

        else:
            return HttpResponseServerError()

@laslogin_required
@login_required
@permission_decorator('_caQuery.can_view_MDAM_configuration')
def updateAllPredefinedLists(request):
    if request.method == 'GET':
        attrs = [{'attribute': a, 'newValues': []} for a in JTAttribute.objects.filter(predefList_Dst__isnull=False).order_by('name')]
        toDelete = []
        for j,attr in enumerate(attrs):
            attr['flt_for_entity'] = list(set([f.qe.name for f in attr['attribute'].filter_set.all()]))
            attr['out_for_entity'] = list(set([oha.output.qe.name for oha in attr['attribute'].output_has_jtattribute_set.all()]))
            if len(attr['flt_for_entity']) == 0 and len(attr['out_for_entity']) == 0:
                toDelete.append(j)
                continue
            newValues = getNewPredefValues(attr['attribute'])

            for x in newValues:
                v = JTAValue()
                v.jtAttr = attr['attribute']
                v.value = x[0]
                v.valueForDisplay = x[1]
                v.hasBeenExcluded = False
                v.save()
                attr['newValues'].append(v)

        for j in toDelete:
            del attrs[j]

        return render_to_response("updatePredefList_report.html", {'attrs': attrs, 'name':request.user.username}, RequestContext(request))
    elif request.method == 'POST':
        try:
            action = request.POST['action']
        except:
            return HttpResponse()
        if action == 'updateval':
            try:
                vid = request.POST['vid']
                valueForDisplay = request.POST['valueForDisplay']
            except:
                return HttpResponse()
            try:
                jtav = JTAValue.objects.get(pk=vid)
                jtav.valueForDisplay = valueForDisplay
                jtav.save()
                return HttpResponse("ok")
            except Exception, e:
                return HttpResponseServerError("An error occurred: " + str(e))
        elif action == 'finish':
            generate_querygen_json()
            try:
                vid_exclude = request.POST['exclude']
                vid_exclude = json.loads(vid_exclude)
                for vid in vid_exclude:
                    jtav = JTAValue.objects.get(pk=vid)
                    jtav.hasBeenExcluded = True
                    jtav.save()
            except:
                return HttpResponse()
            return HttpResponseRedirect(reverse("_caQuery.views.home"))


def getNewPredefValues(jta):
    dst = jta.predefList_Dst
    ds = dst.dataSource
    attr = jta.predefList_Attr
    q = Query()
    q.ds = ds
    if jta.jndTable.toDSTable == dst and jta.attrName == attr:
        # predefined list from column
        sel = [(dst.name, attr), (dst.name, attr)]
    else:
        # predefined list from related table
        sel = [(dst.name, dst.primaryKey), (dst.name, attr)]
    q.sel.extend(sel)
    q.fro.append(dst.name)
    q.distinct = True
    qt = QTree()
    data = qt.compile_and_send_query(q, get_handle=False)

    values = set([x.value for x in jta.jtavalue_set.all()])
    new_values = [x for x in data if str(x[0]) not in values]

    return new_values

@laslogin_required
@login_required
def tablebrowser(request):
    if request.method == 'GET':
        
        if 'dst' in request.GET:
            allds = DataSource.objects.all().order_by('name')
            dst = DSTable.objects.get(pk=request.GET['dst'])
            alldst = DSTable.objects.filter(dataSource=dst.dataSource).order_by('name')
                    
            attrlist = json.loads(dst.attrList)
            details = []

            q = Query()
            q.ds = dst.dataSource
            q.sel = [(dst.name, x) for x in attrlist]
            q.fro.append(dst.name)
            q.lim = 1
            qt = QTree()
            r = qt.compile_and_send_query(q, get_handle=False)
            print "len(r) = ", len(r)
            if len(r) == 0:
                r = ['' for x in attrlist]

            import itertools
            for x,y in itertools.izip(attrlist,r[0]):
                pk = 'yes' if x == dst.primaryKey else ''
                gid = 'yes' if x == dst.genId else ''
                details.append({'name': x, 'pk': pk, 'gid': gid, 'data':y})

            return render_to_response("tablebrowser.html", {'allds': allds, 'alldst': alldst, 'dst': dst, 'data': details, 'name':request.user.username}, RequestContext(request))


        elif 'ds' in request.GET:
            alldst = list(DSTable.objects.filter(dataSource=request.GET['ds']).order_by('name').values_list('id', 'name'))
            return HttpResponse(json.dumps(alldst))
        
        else:
            return render_to_response("tablebrowser.html", {'allds': DataSource.objects.all().order_by('name'), 'name':request.user.username}, RequestContext(request))

@laslogin_required
@login_required
@permission_decorator('_caQuery.can_view_MDAM_configuration')
def qpaths(request):
    if request.method == 'GET':
        if 'ds' in request.GET:
            #return list of queryable entities for data source
            ds_id = request.GET['ds']
            try:
                ds = DataSource.objects.get(pk=ds_id)
                dst = DSTable.objects.filter(dataSource=ds)
                qe = list(QueryableEntity.objects.filter(dsTable__in=dst).order_by('name').values_list('id', 'name', 'dsTable__id', 'dsTable__name'))
                return HttpResponse(json.dumps(qe))
            except:
                return HttpResponse(json.dumps([]))
        
        elif "qe" in request.GET:
            #return table name and table id for queryable entity
            qe_id = request.GET['qe']
            try:
                qe = QueryableEntity.objects.get(pk=qe_id)
                return HttpResponse(json.dumps([qe.dsTable.id,str(qe.dsTable)]))
            except:
                return HttpResponse(None)

        elif "fromqe" in request.GET and "toqe" in request.GET:
            #return shortest path from qe to qe
            import networkx as nx
            
            from_qe_id = request.GET['fromqe']
            to_qe_id = request.GET['toqe']
            
            from_dst = QueryableEntity.objects.get(pk=from_qe_id).dsTable
            to_dst = QueryableEntity.objects.get(pk=to_qe_id).dsTable
            

            all_dst = DSTable.objects.filter(dataSource=from_dst.dataSource)

            g = nx.DiGraph()

            for x in all_dst:
                g.add_node(x.id, name=x.name)

            all_dsr = DSRelationship.objects.filter(fromDSTable__in=all_dst, toDSTable__in=all_dst)
            
            for x in all_dsr:
                g.add_edge(x.fromDSTable.id, x.toDSTable.id, id=x.id, lra=x.leftRelatedAttr, rra=x.rightRelatedAttr, oneToMany=x.oneToMany)
            
            try:
                p = nx.shortest_path(g,source=from_dst.id,target=to_dst.id)
                path = [(p[i-1], g.node[p[i-1]]['name'], g.edge[p[i-1]][p[i]]['lra'], p[i], g.node[p[i]]['name'], g.edge[p[i-1]][p[i]]['rra'], g.edge[p[i-1]][p[i]]['oneToMany']) for i in xrange(1, len(p))]
                path_dsr = [g.edge[p[i-1]][p[i]]['id'] for i in xrange(1, len(p))]
            except Exception as e:
                path = None
                path_dsr = None

            res = {}
            res['path'] = path
            res['dsr'] = path_dsr
            
            return HttpResponse(json.dumps(res))

        elif "fromdst" in request.GET:
            #return list of tables reachable from current one, structured as follows
            #source table id + name, dest table id + name, relationship id, source table attr, dest table attr, relationship cardinality
            dst_id = request.GET['fromdst']
            dst = DSTable.objects.get(pk=dst_id)

            all_dst = DSTable.objects.filter(dataSource=dst.dataSource)

            dsr = DSRelationship.objects.filter(fromDSTable=dst, toDSTable__in=all_dst).order_by('toDSTable__name')

            all_paths = []
            for x in dsr:
                all_paths.append((x.fromDSTable.id, x.fromDSTable.name, x.toDSTable.id, x.toDSTable.name, (x.id, x.leftRelatedAttr,  x.rightRelatedAttr, x.oneToMany)))
            return HttpResponse(json.dumps(all_paths))

        elif "ds_dst_attr" in request.GET:
            #return list of tables with list of attributes for data source
            ds_id = request.GET['ds_dst_attr']

            all_dst = list(DSTable.objects.filter(dataSource=DataSource.objects.get(pk=ds_id)).order_by('name').values_list('id', 'name', 'attrList'))
            all_dst = [(x[0], x[1], json.loads(x[2])) for x in all_dst]
            return HttpResponse(json.dumps(all_dst))

        elif "dst_attr" in request.GET:
            #return list of attributes for table
            dst_id = request.GET['dst_attr']
            return HttpResponse(DSTable.objects.get(pk=dst_id).attrList)


        else:
            all_ds = DataSource.objects.all().order_by('name')
            return render_to_response('qpaths.html', {'name':request.user.username, 'allds': all_ds}, RequestContext(request))

    elif request.method == 'POST':
        if "auto" in request.POST:
            name = request.POST['name']
            descr = request.POST['descr']
            fromqe_id = request.POST['fromqe']
            toqe_id = request.POST['toqe']
            isDefault = request.POST['isdefault']
            path = request.POST['path']

            fromqe = QueryableEntity.objects.get(pk=fromqe_id)
            toqe = QueryableEntity.objects.get(pk=toqe_id)
            path = json.loads(path)

            jt = JoinedTable.getOrCreateJTWithPath(fromqe.dsTable, toqe.dsTable, path)
                
            qp = QueryPath()
            qp.name = name
            qp.descr = descr
            qp.fromQEntity = fromqe
            qp.toQEntity = toqe
            qp.leftPath = jt
            qp.oneToMany = jt.oneToMany
            qp.isDefault = True if isDefault == 'true' else False

            qp.save()

            if "saverev" in request.POST:
                revname = request.POST['revname']
                revdescr = request.POST['revdescr']
                revIsDefault = request.POST['revIsdefault']

                path_rev = []

                for x in path[::-1]:
                    dsr = DSRelationship.objects.get(pk=x)
                    # exclude dsr in case it is a recursive relation from the entity to itself
                    dsr_rev = DSRelationship.objects.filter(fromDSTable=dsr.toDSTable,toDSTable=dsr.fromDSTable).exclude(id=dsr.id)[0]
                    path_rev.append(dsr_rev.id)

                jtr = JoinedTable.getOrCreateJTWithPath(toqe.dsTable, fromqe.dsTable, path_rev)

                qpr = QueryPath()
                qpr.name = revname
                qpr.descr = revdescr
                qpr.fromQEntity = toqe
                qpr.toQEntity = fromqe
                qpr.leftPath = jtr
                qpr.oneToMany = jtr.oneToMany
                qpr.isDefault = True if revIsDefault == 'true' else False

                qpr.save()

            generate_querygen_json()
            return HttpResponse(json.dumps({'forward': qp.id, 'reverse': qpr.id}))

        elif "man" in request.POST:
            print request.POST

            name = request.POST['name']
            descr = request.POST['descr']
            fromqe_id = request.POST['fromqe']
            toqe_id = request.POST['toqe']
            isDefault = request.POST['isdefault']
            left = request.POST['left']
            right = request.POST['right']
            bridge = request.POST['bridge']

            fromqe = QueryableEntity.objects.get(pk=fromqe_id)
            toqe = QueryableEntity.objects.get(pk=toqe_id)
            left = json.loads(left)
            right = json.loads(right)
            bridge = json.loads(bridge)

            if len(left) > 0:
                fromdst = DSRelationship.objects.get(pk=left[0]).fromDSTable
                todst = DSRelationship.objects.get(pk=left[-1]).toDSTable
                jt1 = JoinedTable.getOrCreateJTWithPath(fromdst, todst, left)
            else:
                fromqe_dst = fromqe.dsTable
                jt1 = JoinedTable.getOrCreateJTWithPath(fromqe_dst, fromqe_dst, [])

            if len(right) > 0:
                fromdst = DSRelationship.objects.get(pk=right[0]).fromDSTable
                todst = DSRelationship.objects.get(pk=right[-1]).toDSTable
                jt2 = JoinedTable.getOrCreateJTWithPath(fromdst, todst, right)
            else:
                toqe_dst = toqe.dsTable
                jt2 = JoinedTable.getOrCreateJTWithPath(toqe_dst, toqe_dst, [])

            if len(bridge) > 0:
                try:
                    br = DSRelationship.objects.get(fromDSTable_id=bridge[0], toDSTable_id=bridge[1], leftRelatedAttr=bridge[2])
                except:
                    br = DSRelationship()
                    br.fromDSTable = DSTable.objects.get(pk=bridge[0])
                    br.toDSTable = DSTable.objects.get(pk=bridge[1])
                    br.leftRelatedAttr = bridge[2]
                    br.rightRelatedAttr = bridge[3]
                    br.oneToMany = True if bridge[4] == '1' else False
                    br.save()
            else:
                br = None

            qp = QueryPath()
            qp.name = name
            qp.descr = descr
            qp.fromQEntity = fromqe
            qp.toQEntity = toqe
            qp.leftPath = jt1
            qp.rightPath = jt2 if br else None
            qp.bridgeDsr = br
            qp.oneToMany = (qp.leftPath == None or qp.leftPath.oneToMany) and (qp.rightPath == None or qp.rightPath.oneToMany) and (qp.bridgeDsr == None or qp.bridgeDsr.oneToMany)
            qp.isDefault = True if isDefault == 'true' else False
            qp.save()

            if "saverev" in request.POST:
                revname = request.POST['revname']
                revdescr = request.POST['revdescr']
                revIsDefault = request.POST['revIsdefault']

                left_rev = []
                right_rev = []

                for x in left[::-1]:
                    dsr = DSRelationship.objects.get(pk=x)
                    dsr_rev = DSRelationship.objects.filter(fromDSTable=dsr.toDSTable,toDSTable=dsr.fromDSTable).exclude(id=dsr.id)[0]
                    left_rev.append(dsr_rev.id)
                for x in right[::-1]:
                    dsr = DSRelationship.objects.get(pk=x)
                    dsr_rev = DSRelationship.objects.filter(fromDSTable=dsr.toDSTable,toDSTable=dsr.fromDSTable).exclude(id=dsr.id)[0]
                    right_rev.append(dsr_rev.id)

                if len(right_rev) > 0:
                    fromdst = DSRelationship.objects.get(pk=right_rev[0]).fromDSTable
                    todst = DSRelationship.objects.get(pk=right_rev[-1]).toDSTable
                    jt1 = JoinedTable.getOrCreateJTWithPath(fromdst, todst, right_rev)
                else:
                    toqe_dst = toqe.dsTable
                    jt1 = JoinedTable.getOrCreateJTWithPath(toqe_dst, toqe_dst, [])

                if len(left_rev) > 0:
                    fromdst = DSRelationship.objects.get(pk=left_rev[0]).fromDSTable
                    todst = DSRelationship.objects.get(pk=left_rev[-1]).toDSTable
                    jt2 = JoinedTable.getOrCreateJTWithPath(fromdst, todst, left_rev)
                else:
                    fromqe_dst = fromqe.dsTable
                    jt2 = JoinedTable.getOrCreateJTWithPath(fromqe_dst, fromqe_dst, [])

                if len(bridge) > 0:
                    try:
                        br = DSRelationship.objects.get(fromDSTable_id=bridge[1], toDSTable_id=bridge[0], leftRelatedAttr=bridge[3])
                    except:
                        br = DSRelationship()
                        br.fromDSTable_id = bridge[1]
                        br.toDSTable_id = bridge[0]
                        br.leftRelatedAttr = bridge[3]
                        br.rightRelatedAttr = bridge[2]
                        br.oneToMany = False if bridge[4] == '1' else True
                        br.save()
                else:
                    br = None


                qpr = QueryPath()
                qpr.name = revname
                qpr.descr = revdescr
                qpr.fromQEntity = toqe
                qpr.toQEntity = fromqe
                qpr.leftPath = jt1 if br else jt2
                qpr.rightPath = jt2 if br else None
                qpr.bridgeDsr = br
                qpr.oneToMany = (qpr.leftPath == None or qpr.leftPath.oneToMany) and (qpr.rightPath == None or qpr.rightPath.oneToMany) and (qpr.bridgeDsr == None or qpr.bridgeDsr.oneToMany)
                qpr.isDefault = True if revIsDefault == 'true' else False

                qpr.save()
            else:
                qpr = None
                
            generate_querygen_json()
            return HttpResponse(json.dumps({'forward': qp.id, 'reverse': qpr.id if qpr else None}))
            

        else:
            return HttpResponse()


def checkTemplates(fDel, oDel, qDel):
    templates = {}
    for x in QueryTemplate.objects.all().order_by('name'):
        inputs = [{'qent_id': y.entity_id, 'name': y.name, 'description': y.description} for y in x.querytemplate_has_input_set.all().order_by('no')]
        base_query = json.loads(x.baseQuery)
        conf = json.loads(x.configuration)
        if qDel:
            try:
                for block, blockInfo in base_query.items():
                    if blockInfo.has_key('button_id'):
                        if blockInfo['button_id'] in qDel:
                            raise Exception('Block used')
            except Exception, e:
                print e 
                templates[x.id] = {'name': x.name, 'description': x.description}
                continue



        if fDel:
            try:
                for block_id, cfg in conf.iteritems():
                    # pre-load source template data if block is template
                    if base_query[block_id]['button_cat'] == 'op' and base_query[block_id]['button_id'] == 6:
                        src_templ_id = base_query[block_id]['template_id']
                        src_templ = QueryTemplate.objects.get(pk=src_templ_id)
                        src_templ_par = json.loads(src_templ.parameters)
                    for i, par in cfg['parameters'].iteritems():
                        #print 'fDel', fDel
                        i = int(i)
                        if par['opt'] == '2' or par['opt'] == '3':
                            if base_query[block_id]['button_cat'] == 'qent':
                                # block is an entity, parameter is linked to an entity parameter
                                f_id = int(base_query[block_id]['parameters'][i]['f_id'])
                                #print 'f_id base', f_id
                                if f_id in fDel:
                                    print 'exception base'
                                    raise Exception('Filter used')
                            else:
                                # block is an operator
                                if base_query[block_id]['button_id'] == 6:
                                    # template
                                    # block is a template, current template's parameter is linked to the original block (entity or gb/genid) parameter
                                    src_templ_par_id = int(base_query[block_id]['parameters'][i]['f_id'])
                                    if 'src_f_id' in src_templ_par[src_templ_par_id]:
                                        # original block was an entity
                                        f_id = int(src_templ_par[src_templ_par_id]['src_f_id'])
                                        #print 'f_id block', f_id
                                        if f_id in fDel:
                                            print 'exception block'
                                            raise Exception('Filter in use')

            except Exception, e:
                print e 
                templates[x.id] = {'name': x.name, 'description': x.description}
                continue

        if oDel:
            try:

                for block_id, cfg in  base_query.iteritems():
                    if len(cfg['outputs']):
                        for o in cfg['outputs']:
                            if type(o) is dict:
                                if o.has_key('attr'):
                                    if int(o['attr']) in oDel:
                                        raise Exception('Output used')
                            else:
                                if int(o) in oDel:
                                    raise Exception('Output used')
            except Exception, e:
                print e
                templates[x.id] = {'name': x.name, 'description': x.description}
                continue

    print templates
    return templates

@laslogin_required
@login_required
@permission_decorator('_caQuery.can_view_MDAM_edittemplate')
def editTemplate(request):
    if request.method == 'GET':
        qtemplates = QueryTemplate.objects.filter(isTranslator=False, pk__in= QueryTemplateWG.objects.filter(WG__in = WG.objects.filter(name__in=list( get_WG() ) ) ).values_list('queryTemplate', flat=True) )
        templates = []

        for qt in qtemplates:
            t = {'id':qt.pk, 'title': qt.name, 'description': qt.description, 'output': qt.outputEntity.name, 'translators':[]}
            transList = json.loads(qt.outputTranslatorsList)
            for trans in transList:
                translator = QueryTemplate.objects.get(pk=trans)
                print translator.pk
                t['translators'].append({'id': translator.pk, 'title': translator.name, 'description': translator.description, 'output': translator.outputEntity.name})
            templates.append(t)
        print templates
        return render_to_response("templates.html", {'qt': json.dumps(templates)}, RequestContext(request))
    elif request.method == 'POST':
        if 'action' in request.POST:
            try:
                action = request.POST['action']
                if action == 'delTemplate':
                    qt_id = request.POST['qt']
                    wgList = get_WG()
                    qt = QueryTemplate.objects.get(pk=qt_id)
                    for wg in wgList:
                        QueryTemplateWG.objects.get(queryTemplate=qt, WG=WG.objects.get(name=wg)).delete()
                    
                    qtwg = QueryTemplateWG.objects.filter(queryTemplate=qt)
                    if len(qtwg) == 0:
                        QueryTemplate.objects.get(pk=qt_id).delete()
                        generate_querygen_json()
                    return HttpResponse('ok')
            except Exception, e:
                print e
                HttpResponseServerError('Impossible complete the action') 
        return HttpResponseServerError('no valid action')



@laslogin_required
@login_required
@permission_decorator('_caQuery.can_view_MDAM_edittranslator')
def editTranslator(request):
    if request.method == 'GET':
        qtemplates = QueryTemplate.objects.filter(isTranslator=True, pk__in= QueryTemplateWG.objects.filter(WG__in = WG.objects.filter(name__in=list( get_WG() ) ) ).values_list('queryTemplate', flat=True) )
        templates = []

        for qt in qtemplates:
            t = {'id':qt.pk, 'title': qt.name, 'description': qt.description, 'output': qt.outputEntity.name, 'translators':[]}
            transList = json.loads(qt.outputTranslatorsList)
            for trans in transList:
                translator = QueryTemplate.objects.get(pk=trans)
                print translator.pk
                t['translators'].append({'id': translator.pk, 'title': translator.name, 'description': translator.description, 'output': translator.outputEntity.name})
            templates.append(t)
        print templates
        return render_to_response("translators.html", {'qt': json.dumps(templates)}, RequestContext(request))
    elif request.method == 'POST':
        if 'action' in request.POST:
            try:
                action = request.POST['action']
                if action == 'delTemplate':
                    qt_id = request.POST['qt']
                    wgList = get_WG()
                    qt = QueryTemplate.objects.get(pk=qt_id)
                    for wg in wgList:
                        QueryTemplateWG.objects.get(queryTemplate=qt, WG=WG.objects.get(name=wg)).delete()
                    
                    qtwg = QueryTemplateWG.objects.filter(queryTemplate=qt)
                    if len(qtwg) == 0:
                        QueryTemplate.objects.get(pk=qt_id).delete()
                        generate_querygen_json()
                    return HttpResponse('ok')
            except Exception, e:
                print e
                HttpResponseServerError('Impossible complete the action') 
        return HttpResponseServerError('no valid action')