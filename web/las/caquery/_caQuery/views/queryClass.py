from __init__ import *

class Query(object):
    def __init__(self):
        self.qe = None
        self.ds = None
        self.sel = []
        self.fro = []
        self.jwhr = []
        self.fwhr = []
        self.oj = []
        self.gid_list = []
        #self.gid_field = None
        self.gby = []
        self.hvg = []
        self.lim = None
        self.offset = None
        self.sec_type = None
        self.sec_attr = []
        self.sec_src = None
        self.apply_genid = False
        self.distinct = False
        self.sesskey = None
        #self.jt = []
        self.tables = []
        self.outputs = []
        self.keep_group_pk = False
        self.group_pk_name = None
        self.other_outputs = []
        self.num_prev_other_outputs = 0

class QTNode(object):
    def __init__(self):
        self.left = None
        self.right = None
        self.qe = None
        self.ds = None
        self.type = None
        self.params = []
        self.outputs = []
        self.query_path_id = None
        self.genid = []
        self.hvg = []
        self.subflt = []
        self.extend = []
        self.isLast = False
        self.src_table_name = None
        self.src_pk_name = None
        self.translators = []

class QTree(object):
    def __init__(self):
        self.root = None
        self.cleanupdata = {}
        self.sesskey = ''
        self.view_count = 0
        self.quid = os.urandom(3).encode("hex")

    def __parse_node(self, g, index):
        if index == 'start':
            return None

        curr = g[index]
        n = QTNode()

        if curr['w_out'][0] == 'end':
            n.isLast = True

        if curr['button_cat'] == 'qent':
            n.qe = QueryableEntity.objects.get(pk=curr['button_id'])
            n.ds = n.qe.dsTable.dataSource
            n.type = QE
            n.params = [(x['f_id'], x['values'], x['subflt'] if 'subflt' in x else []) for x in curr['parameters']]
            n.outputs = [x for x in curr['outputs'] if x is not None]
            print "[parse] ", n.outputs
            n.query_path_id = curr['query_path_id'][0]
            if 'w_in' in curr:
                n.left = self.__parse_node(g, curr['w_in'][0])

        elif curr['button_cat'] == 'op':
            op_id = curr['button_id']
            if op_id == 1:
                n.type = OR
            elif op_id == 2:
                n.type = AND
            elif op_id == 3:
                n.type = NOTIN
            elif op_id == 4:
                n.type = GB
                n.qe = QueryableEntity.objects.get(pk=curr['gb_entity'])
                n.query_path_id = curr['query_path_id'][0]
                n.hvg = curr['parameters']
                n.outputs = [x for x in curr['outputs'] if x is not None]
            elif op_id == 5:
                n.type = GENID
                n.genid = [x.replace('-', '_') for x in curr['parameters'][0]['values']]
            elif op_id == 7:
                n.type = EXTEND
                n.qe = QueryableEntity.objects.get(pk=curr['output_type_id'])
                if n.isLast:
                    # if this is an extend and it is the last node, filter out outputs from previous entity
                    n.outputs = [x[1:] for x in  curr['outputs'] if x is not None and x[0] == 'e']
                    n.extend = [x for x in curr['parameters'] if x['query_path_id'] != 'self']
                else:
                    # otherwise keep everything (including those outputs)
                    n.outputs = [x[1:] for x in  curr['outputs'] if x is not None]
                    n.extend = curr['parameters']
            elif op_id == 8:
                # TODO: add BASKET op to database
                n.type = BASKET
                n.qe = QueryableEntity.objects.get(pk=curr['output_type_id'])
                n.src_table_name = curr['src_table_name']
                n.src_pk_name = curr['src_pk_name']


            if 'w_in' in curr:
                n.left = self.__parse_node(g, curr['w_in'][0])
                if len(curr['w_in']) > 1:
                    n.right = self.__parse_node(g, curr['w_in'][1])

        return n

    def parse_query_graph(self, g):
        # parse templates first
        print "Parsing template nodes"
        g = self.parseTemplateNodes(g)
        print "Final query graph"
        print g

        self.root = self.__parse_node(g, g['end']['w_in'][0])
        self.root.translators = g['end']['translators']

        return g[g['end']['w_in'][0]]['output_type_id']
 

    def parseTemplateNodes(self, g):
        try:
            from Queue import Queue
            templNodeIdList = Queue()
            offset = 0
            # initially add templates nodes
            for nodeId, node in g.items():
                if nodeId not in ('start', 'end') and node['button_cat'] == 'op' and node['button_id'] == 6:
                    templNodeIdList.put(nodeId)

            while not templNodeIdList.empty():
                nodeId = templNodeIdList.get()
                node = g[nodeId]
                baseQuery = self.fillTemplateBaseQuery(node)
                m, baseQuery = self.explodeTemplate(g, nodeId, baseQuery, offset)
                offset += len(baseQuery)
                # if template is last block, copy its output translators to the query end block (and remove duplicates)
                if g[nodeId]['w_out'][0] == 'end':
                    g['end']['translators'].extend(json.loads(QueryTemplate.objects.get(pk=g[nodeId]['template_id']).outputTranslatorsList))
                    g['end']['translators'] = list(set(g['end']['translators']))
                print 'del d nodeId'
                del g[nodeId]
                
                g.update(baseQuery)
                # check if any of the nodes in base query is itself a template
                # if so, add it to the queue
                
                for i, n in baseQuery.items():
                    if n['button_cat'] == 'op' and n['button_id'] == 6:
                        templNodeIdList.put(i)
            return g
        except Exception, e:
            print 'Exception parseTemplate node ', e
            return g

    def fillTemplateBaseQuery(self, templNode):
        templId = templNode['template_id']
        t = QueryTemplate.objects.get(pk=templId)
        baseQuery = json.loads(t.baseQuery)
        conf = json.loads(t.configuration)
        parameters = json.loads(t.parameters)
        subvalMap = json.loads(t.valueSubfilterMapping)
        nodeParameters = templNode['parameters']
        for nodeP in nodeParameters:
            par_index = int(nodeP['f_id'])
            par = parameters[par_index]
            src_block_id = par['src_block_id']
            bq_par_id = par['bq_par_id']
            opt = conf[src_block_id]['parameters'][str(bq_par_id)]['opt']
            if opt == '2':
                # MODIFICA PER RIMEDIARE ALLA 'u' INSERITA DAL BLOCCO TEMPLATE NEI PARAMETRI TESTUALI
                # E CHE NON VA BENE PER IL BLOCCO GENID
                #if baseQuery[src_block_id]['button_cat'] == 'op' and baseQuery[src_block_id]['button_id'] == 5:
                #    baseQuery[src_block_id]['parameters'][bq_par_id]['values'] = [z[1:] for z in nodeP['values']]
                #else:
                baseQuery[src_block_id]['parameters'][bq_par_id]['values'] = nodeP['values']
            if 'subvalues' in nodeP: # this can happen with both opt==2 and opt==3
                if baseQuery[src_block_id]['button_cat'] == 'op' and baseQuery[src_block_id]['button_id'] == 6:
                    # template, subvalues field is used
                    baseQuery[src_block_id]['parameters'][bq_par_id]['subvalues'] = nodeP['subvalues']
                else:
                    # entity, subflt field is used
                    subflt = []
                    for i, s in enumerate(nodeP['subvalues']):
                        if s == None:
                            subflt.append(None)
                        else:
                            v = nodeP['values'][i]
                            subflt_id = subvalMap[par['src_f_id']][v]
                            subflt.append({'f_id': subflt_id, 'values': s})
                    baseQuery[src_block_id]['parameters'][bq_par_id]['subflt'] = subflt

        toDelete = {}
        for i,n in baseQuery.items():
            for j,x in enumerate(n['parameters']):
                if len(x['values']) == 0:
                    if not toDelete.has_key(i):
                        toDelete[i] = []
                    toDelete[i].append(j)

        for x, iX in toDelete.items():
            baseQuery[x]['parameters'] = [ baseQuery[x]['parameters'][elI] for elI in range(len(baseQuery[x]['parameters'])) if elI not in iX]

        return baseQuery


    def explodeTemplate(self, queryGraph, templNodeId, baseQuery, offset=0):
        # compute max block id in current base query
        m = offset + max([int(x) for x in queryGraph.keys() if x not in ('start', 'end')])

        # load template from DB
        templId = queryGraph[templNodeId]['template_id']
        t = QueryTemplate.objects.get(pk=templId)
        
        ### update node id references in template base query by adding m
        bq = {}
        for idNode, node in baseQuery.items():
            node['w_in'] = [str(int(x) + m) if x != 'start' else x for x in node['w_in']]
            v = node['w_out'][0].split(".")
            node['w_out'] = [str(int(v[0]) + m) + "." + v[1] if v[0] != 'end' else v[0]]
            bq[str(int(idNode) + m)] = node
        
        ### update references to template node in the rest of the query graph
        ### also update references within base query to nodes in rest of graph 
        # load template input mappings from DB
        inputs = t.querytemplate_has_input_set.all()
        # update nodes connected to template inputs
        for x in queryGraph[templNodeId]['w_in']:
            # look for output connected to template
            # (it is always output #0 except for start block, which allows multiple outputs)
            for index_toTemplBlock in range(0, len(queryGraph[x]['w_out'])):
                v = queryGraph[x]['w_out'][index_toTemplBlock].split(".")
                if v[0] == templNodeId:
                    break
            thisInput = inputs.get(no=v[1])
            blockId = str(thisInput.blockId + m)
            queryGraph[x]['w_out'][index_toTemplBlock] = blockId + "." + str(thisInput.inputId)
            bq[blockId]['w_in'][thisInput.inputId] = x
        # update node connected to template output and bq's output node
        x = queryGraph[templNodeId]['w_out'][0]
        bq[str(t.outputBlockId + m)]['w_out'] = [x]
        if x != 'end':
            nn, ii = x.split(".")
            queryGraph[nn]['w_in'][int(ii)] = str(t.outputBlockId + m)
        else:
            queryGraph['end']['w_in'][0] = str(t.outputBlockId + m)

        # map input query paths and outputs specified in template block's configuration
        # onto the corresponding physical nodes
        inputPaths = queryGraph[templNodeId]['query_path_id']
        for j, x in enumerate(inputPaths):
            if x != None:
                # if user didn't specify an input path, use the one embedded in the underlying block (if any)
                thisInput = inputs.get(no=j)
                blockId = str(thisInput.blockId + m)
                inputId = thisInput.inputId
                bq[blockId]['query_path_id'][inputId] = x
        
        if bq[str(t.outputBlockId + m)]['button_cat'] == 'qent' or bq[str(t.outputBlockId + m)]['button_cat'] == 'op' and bq[str(t.outputBlockId + m)]['button_id'] == 6:
            # if last block in template is an entity or a template, simply copy the contents of the 'outputs' fields onto the block field; this is because both entities and templates whose last block is an entity store output database ids in their outputs fields. templates whose last block is a template store indices
            bq[str(t.outputBlockId + m)]['outputs'] = queryGraph[templNodeId]['outputs']
        else:
            # else, if last block is something else (group by, extend), we move outputs from last block that have not been used in the template to the end of the array (so we do not need to remap indices used to reference such outputs in the next blocks)
            bq[str(t.outputBlockId + m)]['outputs'] = [z for k,z in enumerate(bq[str(t.outputBlockId + m)]['outputs']) if k in [int(i) for i in queryGraph[templNodeId]['outputs']]] + [z for k,z in enumerate(bq[str(t.outputBlockId + m)]['outputs']) if k not in [int(i) for i in queryGraph[templNodeId]['outputs']]]
            # in addition, if the block is the extend op, we also delete the corresponding 'parameters' entry for each unused output
            if bq[str(t.outputBlockId + m)]['button_cat'] == 'op' and bq[str(t.outputBlockId + m)]['button_id'] == 7:
                bq[str(t.outputBlockId + m)]['parameters'] = [z for k,z in enumerate(bq[str(t.outputBlockId + m)]['parameters']) if k in [int(i) for i in queryGraph[templNodeId]['outputs']]]

        return m, bq


    def traverse_tree(self):
        q = self.__traverse_tree(self.root)
        
        #fill select statement with output attributes
        print "Preparing last query..."
        print "[ q ]", q.__dict__
        columns = []
        attrs = []
        
        fns = []
        params = []
        translate = []
        qeoutputs = q.qe.output_set.all()
        q.distinct = True

        if len(self.root.translators) > 0:
            save_pk = True
            # select primary key in last query to save it in a separate table
            attrs.append((q.qe.dsTable.name, q.qe.dsTable.primaryKey))
            translate.append(None)
            columns.append("pk")
            fns.append(None)
            params.append( ( attrs.index( (q.qe.dsTable.name, q.qe.dsTable.primaryKey)), ) )
        else:
            save_pk = False

        for x in qeoutputs:
            columns.append(x.name)
            s = json.loads(x.summary)
            if x.fnName and x.fnName.strip() != '':
                m, n = x.fnName.split('.')
                m = __import__(OUT_FMT_PATH + '.' + m, globals(), locals(), [m], -1)
                f = getattr(m, n)
            else:
                f = None
            fns.append(f)
            l = []
            for y in s:
                if ((y[0], y[1])) not in attrs:
                    attrs.append((y[0], y[1]))
                    if y[3] != None:
                        values = {vv.value: vv.valueForDisplay for vv in JTAValue.objects.filter(jtAttr_id=y[3])}
                        translate.append(values)
                    else:
                        translate.append(None)
                l.append(attrs.index((y[0], y[1])))
                if len(y[2]) > 0:
                    for z in y[2]:
                        if z[2] not in q.fro and (z[0], z[1], '=', z[2], z[3]) not in q.oj:
                            q.oj.append((z[0], z[1], '=', z[2], z[3]))
                            q.jwhr.append((z[0], z[1], '=', z[2], z[3], None, None, None, None, True))


            params.append(l)

        if len(q.other_outputs) > 0:
            print "there are group by outputs:", q.other_outputs
            composite_outputs = {}
            for j, out in enumerate(q.other_outputs):
                attrs.append((self.getLastView(), "attr_" + str(j)))
                trans_values = None
                fn = None
                
                if out.get('remap_attr_id', None) is not None:
                    # attribute must be remapped
                    trans_values = {vv.value: vv.valueForDisplay for vv in JTAValue.objects.filter(jtAttr_id=out['remap_attr_id'])}
                    
                if out.get('composite_id', None) is not None:
                    # attribute is part of a composite attribute
                    if out['composite_id'] not in composite_outputs:
                        if out['composite_fnname'] is not None:
                            m, n = out['composite_fnname'].split('.')
                            m = __import__(OUT_FMT_PATH + '.' + m, globals(), locals(), [m], -1)
                            f = getattr(m, n)
                        else:
                            f = None
                        composite_outputs[out['composite_id']] = {'params': {}, 'index': len(columns)}
                        columns.append(out['composite_name'])
                        params.append( [ ] ) # params will be filled out at the end
                        fns.append(f)

                    composite_outputs[out['composite_id']]['params'][out['composite_rank']] = j
                    translate.append(trans_values)

                else:
                    columns.append(out['name'])
                    params.append( ( attrs.index( (self.getLastView(), "attr_" + str(j))), ) )
                    translate.append(trans_values)
                    fns.append(None)

            # fill out parameters
            for i, cout in composite_outputs.iteritems():
                params[cout['index']] = [attrs.index( ( self.getLastView(), "attr_" + str(cout['params'][k]) ) ) for k in sorted(cout['params']) ]


        if q.keep_group_pk == True:
            print "keep group primary key"
            #attrs.append((self.getLastView(), "attr_" + str(len(q.other_outputs))))
            attrs.append((self.getLastView(), "attr_" + str(len(q.other_outputs) + q.num_prev_other_outputs)))
            columns.append("group_pk")
            translate.append(None)
            fns.append(None)
            params.append( ( attrs.index( (self.getLastView(), "attr_" + str(len(q.other_outputs) + q.num_prev_other_outputs))), ) )

        q.sel.extend(attrs)
        print "translate:", translate

        print "about to submit last query"

        rows = self.compile_and_send_query(q, save_pk=save_pk)

        print "last query submitted"

        print "columns:", columns
        print "rows[:5]", rows[:5]

        if len(self.root.translators) > 0:
            trans_data = {x[0]:{z:[] for z in self.root.translators} for x in rows}
        else:
            trans_data = None

        formatted_rows = []
        fp = zip(fns, params)
        for x in rows:
            # translate predefined values
            for id, val in enumerate(x):
                if translate[id] and x[id] != None:
                    try:
                        x[id] = translate[id][str(x[id])]
                    except:
                        # value cannot be translated
                        pass

            r = []
            for f, p in fp:
                if f:
                    v = f([x[i] for i in p])
                else:
                    v = ''.join([str(x[i]) for i in p])
                r.append(v)
            formatted_rows.append(r)
        print formatted_rows[:5]

        
        trans_meta = {}
        for x in self.root.translators:
            print "Running translator", x, "..."
            t = QueryTemplate.objects.get(pk=x)
            # instantiate the translator graph
            translatorGraph = deepcopy(TRANSLATOR_BASE_QUERY)
            # configure BASKET block
            translatorGraph["1"]["output_type_id"] = q.qe.id
            translatorGraph["1"]["src_table_name"] = self.getLastView()
            # new table's pk is named after current table's pk
            translatorGraph["1"]["src_pk_name"] = q.qe.dsTable.primaryKey
            translatorGraph["2"]["template_id"] = x
            translatorGraph["2"]["output_type_id"] = t.outputEntity_id
            from views_query import run_query
            h, b, dummy, dummy, dummy = run_query(translatorGraph, self.getNextView())
            trans_meta[x] = {'title':  t.name, 'headers': h[:-1]} # ignore last field (primary key)
            for r in b:
                trans_data[int(r[-1])][x].append(r[:-1])

        if len(self.root.translators) > 0:
            return columns, formatted_rows, trans_meta, trans_data
        else:
            return columns, formatted_rows, None, None


    def __traverse_tree(self, curr):
        if not curr:
            return None
        print "[ NODE ]", curr.__dict__
        q1 = self.__traverse_tree(curr.left)
        q2 = self.__traverse_tree(curr.right)

        for i,z in enumerate([q1, q2]):
            if z:
                print "[ q%d ]" % (i+1), z.__dict__
            else:
                print "[ q%d ]" % (i+1), "None"

        print "Curr.outputs:", curr.outputs

        if q2:
            #2 inputs
            assert q1.qe == q2.qe
            
            if curr.type == AND:
                #select primary key in second query
                q2.sel.append((q2.qe.dsTable.name, q2.qe.dsTable.primaryKey))
                #submit and get handle
                h2 = self.compile_and_send_query(q2,get_handle=True)
                #add handle in first query
                q1.fro.append(h2[0])
                #add join condition
                q1.jwhr.append((q1.qe.dsTable.name, q1.qe.dsTable.primaryKey, '=', h2[0], HANDLE_KEY_ATTR, None, None, None, None, False))

                return q1

            elif curr.type == NOTIN:
                #select primary key in second query
                q2.sel.append((q2.qe.dsTable.name, q2.qe.dsTable.primaryKey))
                #submit and get handle
                h2 = self.compile_and_send_query(q2,get_handle=True)
                #add NOT IN clause in first query

                if q1.sec_type == NOTIN:
                    # q1 already contains a NOT IN
                    # which must be resolved before we add this one
                    q1.sel.append((q1.qe.dsTable.name, q1.qe.dsTable.primaryKey))
                    h1 = self.compile_and_send_query(q1,get_handle=True)
                    q_next = Query()
                    q_next.qe = q1.qe
                    q_next.ds = q1.ds
                    q_next.fro.append(q1.qe.dsTable.name)
                    q_next.fro.append(h1[0])
                    #add join condition
                    q_next.jwhr.append((q_next.qe.dsTable.name, q_next.qe.dsTable.primaryKey, '=', h1[0], HANDLE_KEY_ATTR, None, None, None, None, False))
                    q1 = q_next
                
                q1.sec_type = NOTIN
                q1.sec_attr = (q1.qe.dsTable.name, q1.qe.dsTable.primaryKey)
                q1.sec_src = h2[0]

                return q1

            elif curr.type == OR:
                #select primary key in second query
                q2.sel.append((q2.qe.dsTable.name, q2.qe.dsTable.primaryKey))
                #submit and get handle
                h2 = self.compile_and_send_query(q2,get_handle=True)
                #select primary key in first query
                q1.sel.append((q1.qe.dsTable.name, q1.qe.dsTable.primaryKey))
                #add OR clause in first query
                q1.sec_type = OR
                q1.sec_src = h2[0]
                #submit and get handle
                h1 = self.compile_and_send_query(q1,get_handle=True)
                #start new query with same entity
                q_next = Query()
                q_next.qe = q1.qe
                q_next.ds = q1.ds
                q_next.fro.append(q1.qe.dsTable.name)
                #add handle to from clause
                q_next.fro.append(h1[0])
                #add join condition
                q_next.jwhr.append((q_next.qe.dsTable.name, q_next.qe.dsTable.primaryKey, '=', h1[0], HANDLE_KEY_ATTR, None, None, None, None, False))

                return q_next

        else:
            # only 1 input
            
            if curr.type in [QE, GB, EXTEND, BASKET]:

                q_next = Query()
                q_next.qe = curr.qe
                q_next.ds = curr.qe.dsTable.dataSource
                q_next.fro.append(curr.qe.dsTable.name)

                if curr.type not in [GB, EXTEND]:
                    q_next.outputs = curr.outputs# save in query in order to add to select clause when statement is submitted in next recursion level, but only if current node is not a group by or extend (if it is a group by, outputs are added to the select statement in the current recursion level). only the number of outputs (from which the attribute names can be reconstructed) is inserted into a special "num_gby_outputs" field, because these attributes need to be selected in the next view from the current view
                #elif curr.type == GB:
                #    q_next.num_gby_outputs = len(curr.outputs) # il numero di attributi selezionati qui e' = al numero di output
                #    print "NUM_GBY_OUTPUTS", len(curr.outputs)
                #elif curr.type == EXTEND:
                #    pass # ma qui invece no, perche' un output puo' corrispondere a piu' attributi

                print "parameters: ", curr.params

                if len(curr.params) > 0:
                    for x in curr.params:
                        f = Filter.objects.get(pk=x[0])
                        jta = f.jtAttr
                        jt = jta.jndTable
                        self.addJoinedTable(q_next, jt)
                        f_type = jta.attrType_id

                        print "filter type: ", f_type
                        if f_type in [2, 3]: # date and numeric ranges must be handled separately
                            for y in x[1]:
                                # second character is '>', '=' or '<'
                                op = "=" if y[1] == "=" else ">=" if y[1] == ">" else "<="
                                # first character is either 'u' (uncorrelated) or 'c' (correlated)
                                if y[0] == 'u':
                                    q_next.fwhr.append((jt.toDSTable.name, jta.attrName, op, [y[2:]], None, None, None))
                                else:
                                    r = re.compile('[ _+]+')
                                    # recupero l'output associato all'attributo correlato
                                    # b = block_id, oid = output id, val = valore da aggiungere o sottrarre
                                    b, oid, val = r.split(y[2:])
                                    
                                    #####if oid not in outputs:
                                    #####    outputs.append(oid)
                                    
                                    # quindi aggiungo un jwhr tra attributo corrente e attributo correlato
                                    # insieme ai valori di range
                                    # per le date
                                    if f_type == 2:
                                        q_next.jwhr.append((jt.toDSTable.name, jta.attrName, op, self.getNextView(), "attr_" + str(oid), None, None, "adddate(", ", '" + val + "')", False))
                                    # per valori numerici
                                    else:
                                        q_next.jwhr.append((jt.toDSTable.name, jta.attrName, op, self.getNextView(), "attr_" + str(oid), None, None, None, "+ '" + val + "'", False))

                        elif f_type in [1, 6 , 7]: # predefined lists, workingGroups and booleans have no correlated attributes
                            # parse subfilters
                            subflt = []
                            print "subfilters: ", x[2]
                            for y in x[2]:
                                if y == None:
                                    subflt.append(None)
                                    continue
                                f1 = Filter.objects.get(pk=y['f_id'])
                                jta1 = f1.jtAttr
                                jt1 = jta1.jndTable
                                self.addJoinedTable(q_next, jt1)
                                f_type1 = jta1.attrType_id

                                if f_type1 in [2, 3]: # date and numeric ranges must be handled separately
                                    s = ''
                                    for z in y['values']:
                                        print "subfilter value:", z
                                        op1 = "=" if z[1] == "=" else ">=" if z[1] == ">" else "<="

                                        if z[0] == 'u':
                                            s = s + " and `%s`.`%s` %s '%s'" % (jt1.toDSTable.name, jta1.attrName, op1, z[2:])
                                        else:
                                            r = re.compile('[ _+]+')
                                            # recupero l'output associato all'attributo correlato
                                            b, oid, val = r.split(z[2:])
                                            
                                            #####if oid not in outputs:
                                            #####    outputs.append(oid)

                                            # quindi aggiungo un jwhr tra attributo corrente e attributo correlato
                                            # insieme ai valori di range
                                            # per le date
                                            if f_type1 == 2:
                                                s = s + " and `%s`.`%s` %s adddate(`%s`.`attr_%d`, %s)" % (jt.toDSTable.name, jta.attrName, op, self.getNextView(), oid, val)
                                            # per valori numerici
                                            else:
                                                s = s + " and `%s`.`%s` %s `%s`.`attr_%d` + %s" % (jt.toDSTable.name, jta.attrName, op, self.getNextView(), oid, val)

                                    subflt.append(s)

                                elif f_type1 == 6: #boolean
                                    subflt.append(" and `%s`.`%s` %s '%s'" % (jt1.toDSTable.name, jta1.attrName, "=", y['values'][0]))
                                # sono arrivato qui
                                # ho fatto i sottocasi 2/3 e 6, bisogna fare il terzo
                                # e poi proseguire con il group by e gli output da aggiungere nella select
                                else: # text and text w/ autocomplete
                                    if y['values'][0][0] == 'u': # uncorrelated, only one value possible since it's a subfilter
                                        vals = [y['values'][0][1:]]
                                        subflt.append(" and `%s`.`%s` %s '%s'" % (jt1.toDSTable.name, jta1.attrName, "=", y['values'][0][1:]))
                                    else: # correlated, only one value possible, use as join condition
                                        r = re.compile('[ _]+')
                                        b, oid = r.split(y['values'][0][1:])
                                        #####if oid not in outputs:
                                        #####    outputs.append(oid)
                                        subflt.append(" and `%s`.`%s` %s `%s`.`attr_%d`" % (jt1.toDSTable.name, jta1.attrName, "=", self.getNextView(), oid))

                            # add all predefined list values with their respective extra conditions (subfilters), if any
                            q_next.fwhr.append((jt.toDSTable.name, jta.attrName, "=", x[1], None, None, subflt if len(subflt) else None))
                        
                        elif f_type == 4:
                            print x
                            vals = [v .replace('-', '_') for v in x[1]]
                            q_next.fwhr.append((jt.toDSTable.name, jta.attrName, "like", vals, None, None, None))
                        else: # text and text w/ autocomplete
                            if x[1][0][0] == 'u': # uncorrelated, multiple values possible
                                vals = [v[1:] for v in x[1]]
                                q_next.fwhr.append((jt.toDSTable.name, jta.attrName, "=", vals, None, None, None))
                            else: # correlated, only one value possible, use as join condition
                                print "correlated attribute"
                                r = re.compile('[ _]+')
                                b, oid = r.split(x[1][0][1:])
                                #####if oid not in outputs:
                                #####    outputs.append(oid)
                                q_next.jwhr.append((jt.toDSTable.name, jta.attrName, "=", self.getNextView(), "attr_" + str(oid), None, None, None, None, False))
                                
                if q1:
                    q_next.keep_group_pk = q1.keep_group_pk

                    if q1.apply_genid == True:
                        q_next.fwhr.append((curr.qe.dsTable.name, curr.qe.dsTable.genId, "like", q1.gid_list, None, None, None))

                    same_ds = q1.qe != None and q1.ds == q_next.ds

                    if same_ds:
                        print "same ds"
                        if q1.qe != q_next.qe or (q1.qe == q_next.qe and curr.query_path_id != None): # this is to allow matching an entity to itself through a non-standard (i.e. non-pk->pk) path (e.g., recursive relationships)
                            #try:
                            # if a query path has been specified, use it
                            if curr.query_path_id != None:
                                qp = QueryPath.objects.get(pk=curr.query_path_id)
                            # else use the default one
                            else:
                                qp = QueryPath.objects.get(fromQEntity=q1.qe,toQEntity=q_next.qe,isDefault=True)
                            lsub = json.loads(qp.leftPath.summary)
                                                        
                            self.addJoinedTable(q1, lsub, True)
                            
                            q1.sel.append((lsub[-1][0], lsub[-1][1]))
                            
                            if curr.type != GB:
                                print "curr.type is not GB"
                                print "Outputs: ", q1.outputs
                                # not a group by query, outputs are simple attributes
                                if len(q1.other_outputs) > 0:
                                    print "outputs from previous GB/EXTEND"
                                    #either from the previous group by (so they are aggregate functions) or extend (so they are attributes from a related entity)
                                    for j in xrange(0, len(q1.other_outputs)):
                                        q1.sel.append((self.getLastView(), "attr_" + str(j)))
                                else:
                                    #or from an entity (so they are attributes)
                                    print "outputs from previous entity"
                                    if curr.type != EXTEND or curr.isLast == False:
                                        for oid in q1.outputs:
                                            o = Output.objects.get(pk=oid)
                                            summ = json.loads(o.summary)
                                            for j,x in enumerate(summ):
                                                q1.sel.append((x[0], x[1]))
                                                self.addJoinedTable(q1, x[2])
                                    else:
                                        print "skip entity output because current block is extend and it is the last block"
                                
                            else: #curr.type == GB:
                                print "curr.type is GB"
                                if len(q1.other_outputs) > 0:
                                    print "there are outputs from previous GB/EXTEND -- only considering outputs from previous groupby"
                                    #from the previous group by
                                    for j,out in enumerate(q1.other_outputs):
                                        if out['src'] == 'G':
                                            q1.sel.append((self.getLastView(), "attr_" + str(j)))
                                q1.gby.append((lsub[-1][0], lsub[-1][1]))
                                for x in curr.hvg:
                                    
                                    if x['op'] in ['COUNT', 'SUM', 'MIN', 'MAX', 'AVG']:
                                        aggr_op = x['op']
                                    else:
                                        print "Invalid operator"
                                        return
                                    
                                    for y in x['values']:
                                        # first character is 'u' (always uncorrelated), skip it
                                        op = "=" if y[1] == "=" else ">=" if y[1] == ">" else "<="
                                        
                                        if x['attr'] == '-1':
                                            t = (aggr_op, STAR, None, None, None, op, y[2:])
                                        
                                        elif x['attr'][0] == 'c':
                                            # correlated attribute: previous block was a group by, this is one of its outputs
                                            # recupero l'output associato all'attributo correlato
                                            # b = block_id, oid = output id
                                            b, oid = x['attr'].split('_')
                                            t = (aggr_op, None, DISTINCT if aggr_op == 'COUNT' else None, self.getLastView(), "attr_" + str(oid), op, y[2:])

                                        else:
                                            o = Output.objects.get(pk=x['attr'])
                                            summ = json.loads(o.summary)
                                            self.addJoinedTable(q1, summ[0][2])
                                            t = (aggr_op, None, DISTINCT if aggr_op == 'COUNT' else None, summ[0][0], summ[0][1], op, y[2:])

                                        q1.hvg.append(t)

                                # add outputs to select statement (outputs are aggregate functions)
                                for x in curr.outputs:
                                    if x['op'] in ['COUNT', 'SUM', 'MIN', 'MAX', 'AVG']:
                                        aggr_op = x['op']
                                    else:
                                        print "Invalid operator"
                                        return
                                    
                                    if x['attr'] == '-1':
                                        t = aggr_op + "(*)"

                                    elif x['attr'][0] == 'c':
                                        # correlated attribute: previous block was a group by, this is one of its outputs
                                        # recupero l'output associato all'attributo correlato
                                        # b = block_id, oid = output id
                                        b, oid = x['attr'][1:].split('_')
                                        t = aggr_op + "(" + ("DISTINCT" if aggr_op == 'COUNT' else "")+ "`" + self.getLastView() + "`.`" + "attr_" + str(oid) + "`)"

                                    else:
                                        o = Output.objects.get(pk=x['attr'])
                                        summ = json.loads(o.summary)
                                        self.addJoinedTable(q1, summ[0][2])
                                        t = aggr_op + "(" + ("DISTINCT" if aggr_op == 'COUNT' else "")+ "`" + summ[0][0] + "`.`" + summ[0][1] + "`)"
                                    q1.sel.append((t,))
                                    # save output names in case they need to be displayed in the final result
                                    
                                    output_name = x['name']
                                    # save output types (needed if block following group by is from a different data source, so the data from the current data source must be sent to the next one by creating a temporary table - hence we need to know column types)
                                    if aggr_op == 'COUNT':
                                        output_type = 3
                                    else:
                                        if x['attr'][0] == 'c':
                                            output_type = q1.other_outputs[int(oid)]['type']
                                        else:
                                            output_type = o.output_has_jtattribute_set.all()[0].jtAttr.attrType.id
                                    
                                    q_next.other_outputs.append({'src': 'G', 'type': output_type, 'name': output_name})

                            if q1.keep_group_pk == True:
                                if q1.group_pk_name == None:
                                    # q1's entity is the entity whose pk we want to keep
                                    group_pk_name = (q1.qe.dsTable.name, q1.qe.dsTable.primaryKey)
                                else:
                                    # q1 has a different entity, the name of the field holding the pk is in group_pk_name
                                    group_pk_name = q1.group_pk_name
                                    
                                if curr.type == GB:
                                    # current block is group by, we need to group by each attribute we select
                                    q1.gby.append(group_pk_name)
                                q1.sel.append(group_pk_name)
                                q_next.group_pk_name = (self.getNextView(), "attr_" + str(len(q1.sel)-2))

                            h1 = self.compile_and_send_query(q1,get_handle=True)

                            q_next.fro.append(h1[0])
                            q_next.jwhr.append((curr.qe.dsTable.name, lsub[-1][3], '=', h1[0], HANDLE_KEY_ATTR, None, None, None, None, False))

                        else:
                            print "same qe"
                            q1.sel.append((q1.qe.dsTable.name, q1.qe.dsTable.primaryKey))
                            print "Outputs: ", q1.outputs
                            # add outputs
                            print "q1.other_outputs=", q1.other_outputs
                            if len(q1.other_outputs) > 0:
                                print "outputs from previous GB/extend/entity through extend"
                                #from a previous GB/extend/entity through extend
                                for j in xrange(0, len(q1.other_outputs)):
                                    q1.sel.append((self.getLastView(), "attr_" + str(j)))
                            else:
                                #from the previous entity
                                print "outputs from previous entity"
                                if curr.type != EXTEND or curr.isLast == False:
                                    for oid in q1.outputs:
                                        o = Output.objects.get(pk=oid)
                                        summ = json.loads(o.summary)
                                        for j,x in enumerate(summ):
                                            q1.sel.append((x[0], x[1]))
                                            self.addJoinedTable(q1, x[2])
                                else:
                                    print "skip entity outputs because current block is extend and it is the last block"

                            h1 = self.compile_and_send_query(q1,get_handle=True)
                            q_next.fro.append(h1[0])
                            q_next.jwhr.append((curr.qe.dsTable.name, curr.qe.dsTable.primaryKey, '=', h1[0], HANDLE_KEY_ATTR, None, None, None, None, False))
                            
                            if curr.type == EXTEND:
                                print "EXTEND operator:", curr.extend
                                q_next.sel.append((q_next.qe.dsTable.name, q_next.qe.dsTable.primaryKey))
                                
                                # propagate prev. entity's outputs only if this is not the last block

                                #if curr.isLast == False:
                                #    for i,oid in enumerate(q1.outputs):
                                #        o = Output.objects.get(pk=oid)
                                #        summ = json.loads(o.summary)
                                #        for j,x in enumerate(summ):
                                #            jta = o.output_has_jtattribute_set.get(no=j).jtAttr
                                #            q_next.other_outputs.append({'src': 'O', 'type': jta.attrType.id, 'name': "%s.%s" % (o.name, jta.name)})

                                if len(q1.other_outputs) > 0:
                                    print "outputs from previous GB/EXTEND -- only considering outputs from GB because EXTEND blocks can (and should) not be chained"
                                    #from the previous group by (so they are aggregate functions)
                                    for j,out in enumerate(q1.other_outputs):
                                        if out['src'] == 'G':
                                            q_next.sel.append((self.getLastView(), "attr_" + str(j)))
                                            q_next.other_outputs.append(out)

                                cnt_composite_attrs = 0
                                for ext in curr.extend:
                                    if ext['query_path_id'] == 'self':
                                        print "extend: self"
                                        if curr.isLast == False:
                                            o = Output.objects.get(pk=q1.outputs[ext['out_id']])
                                            summ = json.loads(o.summary)
                                            for j,x in enumerate(summ):
                                                jta = o.output_has_jtattribute_set.get(no=j).jtAttr
                                                q_next.sel.append((h1[0], 'attr_' + str(j)))
                                                q_next.other_outputs.append({'src': 'O', 'type': jta.attrType.id, 'name': "%s - %s" % (o.qe.name, o.name if len(summ) == 1 else "%s.%s" % (o.name, jta.name))})
                                        else:
                                            print "skip because this is last block"
                                    else:
                                        print "extend: external"
                                        qp = QueryPath.objects.get(pk=ext['query_path_id'])
                                        lsub = json.loads(qp.leftPath.summary)
                                        o = Output.objects.get(pk=ext['out_id'])
                                        print o.name
                                        #print lsub
                                        #print 'This is last: ', curr.isLast
                                        #print q_next.fro
                                        #print q_next.jwhr
                                        if curr.isLast == True:
                                            # perform left outer join
                                            z = lsub[0]
                                            if z[2] not in q_next.fro and (z[0], z[1], '=', z[2], z[3]) not in q_next.oj:
                                                q_next.oj.append((z[0], z[1], '=', z[2], z[3]))
                                                q_next.jwhr.append((z[0], z[1], '=', z[2], z[3], None, None, None, None, True))
                                            self.addJoinedTable(q_next, lsub[1:], outerJn=True)
                                        else:
                                            # perform inner join
                                            self.addJoinedTable(q_next, lsub)
                                        summ = json.loads(o.summary)
                                        print "summary:", summ
                                        if len(summ) == 1:
                                            # single attribute
                                            x = summ[0]
                                            print "%d: %s" % (0, str(x))
                                            if (x[0], x[1]) not in q_next.sel:
                                                print "add joined table"
                                                self.addJoinedTable(q_next, x[2], outerJn=True)
                                            q_next.sel.append((x[0], x[1]))
                                            jta = o.output_has_jtattribute_set.get(no=0).jtAttr
                                            if x[3] is not None:
                                                # attribute must be remapped
                                                q_next.other_outputs.append({'src': 'E', 'type': jta.attrType.id, 'name': "%s - %s" % (o.qe.name, o.name), 'remap_attr_id': jta.id})
                                            else:
                                                q_next.other_outputs.append({'src': 'E', 'type': jta.attrType.id, 'name': "%s - %s" % (o.qe.name, o.name)})
                                        
                                        else:
                                            # composite attribute
                                            for j,x in enumerate(summ):
                                                print "%d: %s" % (j, str(x))
                                                if (x[0], x[1]) not in q_next.sel:
                                                    print "add joined table"
                                                    self.addJoinedTable(q_next, x[2], outerJn=True)
                                                q_next.sel.append((x[0], x[1]))
                                                jta = o.output_has_jtattribute_set.get(no=j).jtAttr
                                                if x[3] is not None:
                                                    # attribute must be remapped
                                                    q_next.other_outputs.append({'src': 'E', 'type': jta.attrType.id, 'name': "%s-%s.%s" % (o.qe.name, o.name, jta.name), 'remap_attr_id': jta.id, 'composite_id': cnt_composite_attrs, 'composite_rank': j, 'composite_fnname': o.fnName, 'composite_name': "%s_%s" % (o.qe.name, o.name)})
                                                else:
                                                    q_next.other_outputs.append({'src': 'E', 'type': jta.attrType.id, 'name': "%s-%s.%s" % (o.qe.name, o.name, jta.name), 'composite_id': cnt_composite_attrs, 'composite_rank': j, 'composite_fnname': o.fnName, 'composite_name': "%s_%s" % (o.qe.name, o.name)})
                                            cnt_composite_attrs += 1
                                print q_next.sel
                                            

                                print "[ q1 ]", q1.__dict__
                                
                                h2 = self.compile_and_send_query(q_next,get_handle=True)

                                q1 = q_next

                                q_next = Query()
                                q_next.qe = curr.qe
                                q_next.ds = curr.qe.dsTable.dataSource
                                q_next.fro.append(curr.qe.dsTable.name)
                                q_next.fro.append(h2[0])
                                q_next.other_outputs = q1.other_outputs
                                q_next.keep_group_pk = q1.keep_group_pk

                                q_next.jwhr.append((curr.qe.dsTable.name, curr.qe.dsTable.primaryKey, '=', h2[0], HANDLE_KEY_ATTR, None, None, None, None, False))


                    elif q1.qe:
                        print "not same ds"
                        #different data source
                        # if a query path has been specified, use it
                        if curr.query_path_id != None:
                            qp = QueryPath.objects.get(pk=curr.query_path_id)
                        # otherwise use the default one
                        else:
                            qp = QueryPath.objects.get(fromQEntity=q1.qe,toQEntity=q_next.qe,isDefault=True)
                        lsub = json.loads(qp.leftPath.summary)
                        bsub = json.loads(qp.bridgeSummary)
                        rsub = json.loads(qp.rightPath.summary)
                        
                        self.addJoinedTable(q1, lsub, False)

                        if bsub[4]:
                            # condition on genid (truncate at appropriate length)
                            q1.sel.append(("rpad(substring(`" + bsub[0] + '`.`' + bsub[1] + "`,1," + str(bsub[4]) + "),26,'_'))")) 
                        else:
                            q1.sel.append((bsub[0], bsub[1]))

                        if curr.type != GB:
                            if len(q1.other_outputs) > 0:
                                column_types = []
                                #outputs from the previous group by (so they are aggregate functions)
                                for j,out in enumerate(q1.other_outputs):
                                    q1.sel.append((self.getLastView(), "attr_" + str(j)))
                                    column_types.append(out['type'])
                            else:
                                column_types = []
                                for oid in q1.outputs:
                                    o = Output.objects.get(pk=oid)
                                    summ = json.loads(o.summary)
                                    column_types.append(o.output_has_jtattribute_set.all()[0].jtAttr.attrType.id)
                                    for x in summ:
                                        q1.sel.append((x[0], x[1]))
                                        self.addJoinedTable(q1, x[2])

                        if q1.keep_group_pk == True:
                            if q1.group_pk_name == None:
                                # q1's entity is the entity whose pk we want to keep
                                group_pk_name = (q1.qe.dsTable.name, q1.qe.dsTable.primaryKey)
                            else:
                                # q1 has a different entity, the name of the field holding the pk is in group_pk_name
                                group_pk_name = q1.group_pk_name
                                
                            if curr.type == GB:
                                # current block is group by, we need to group by each attribute we select
                                q1.gby.append(group_pk_name)
                            q1.sel.append(group_pk_name)

                            # append pk's type to column_types
                            column_types.append(PK_TYPE)

                        # send query to data source 1; select clause contains genid and possibly other attributes needed for correlation
                        r = self.compile_and_send_query(q1)
                        print "RESULT FROM PREVIOUS QUERY:", r

                        #EDIT: reverse right subpath and add it now before bridge to preserve order necessary for correctly generating INNER JOINS
                        # should be fixed
                        rsub.reverse()
                        self.addJoinedTable(q_next, rsub)
                        
                        # we need to discriminate whether we are only joining the data sources based on the genid, or there are other attributes (correlation)
                        if len(q1.outputs) + len(q1.other_outputs) == 0 and q1.keep_group_pk == False:
                            #only genid
                            r = [x[0] for x in r]
                            q_next.fwhr.append((bsub[2], bsub[3], "=", r, None, None, None))
                        else:
                            #genid + other attributes
                            #prepare table to send
                            t = {}
                            t['name'] = self.getNextView()
                            tot_num_columns = len(q1.outputs) + len(q1.other_outputs) + (1 if q1.keep_group_pk == True else 0)
                            column_names = ['attr_%d' % i for i in xrange(0, tot_num_columns)]
                            t['columns'] = [{'name': 'x', 'type': 4}] + [{'name': nn, 'type': tt} for nn,tt in zip(column_names, column_types)]
                            t['data'] = r
                            t['indexed_column'] = 'x'
                            q_next.fro.append(self.getNextView())
                            q_next.tables.append(t)
                            q_next.jwhr.append((bsub[2], bsub[3], "=", self.getNextView(), 'x', None, None, None, None, False))
                            
                            if q1.keep_group_pk == True:
                                q_next.group_pk_name = (self.getNextView(), "attr_" + str(len(q1.sel)-2))

                            self.makeNewView() # make new view because the next one is used as the name of the datatable

                        if curr.type == GB: # n.b. group by should be done in a separate query if the output
                        # for the last block (i.e., the entity corresponding to the grouping attribute)
                        # comprises other entities that are in a many-to-many (or many-to-one) relationship
                            q_next.gby.append((rsub[-1][2], rsub[-1][3]))

                            for x in curr.hvg:
                                
                                if x['op'] in ['COUNT', 'SUM', 'MIN', 'MAX', 'AVG']:
                                    aggr_op = x['op']
                                else:
                                    print "Invalid operator"
                                    return
                                
                                for y in x['values']:
                                    # first character is 'u' (always uncorrelated), skip it
                                    op = "=" if y[1] == "=" else ">=" if y[1] == ">" else "<="
                                    
                                    if x['attr'] == '-1':
                                        t = (aggr_op, STAR, None, None, None, op, y[2:])

                                    elif x['attr'][0] == 'c':
                                        # correlated attribute: previous block was a group by, this is one of its outputs
                                        # recupero l'output associato all'attributo correlato
                                        # b = block_id, oid = output id
                                        b, oid = x['attr'].split('_')
                                        t = (aggr_op, None, DISTINCT if aggr_op == 'COUNT' else None, self.getLastView(), "attr_" + str(oid), op, y[2:])

                                    else:
                                        o = Output.objects.get(pk=x['attr'])
                                        summ = json.loads(o.summary)
                                        self.addJoinedTable(q1, summ[0][2])
                                        t = (aggr_op, None, DISTINCT if aggr_op == 'COUNT' else None, summ[0][0], summ[0][1], op, y[2:])

                                    q_next.hvg.append(t)

                                # add outputs to select statement (outputs are aggregate functions)
                            q_next_gby_output_names = []
                            q_next_gby_output_types = []
                            for x in curr.outputs:
                                if x['op'] in ['COUNT', 'SUM', 'MIN', 'MAX', 'AVG']:
                                    aggr_op = x['op']
                                else:
                                    print "Invalid operator"
                                    return
                                if x['attr'] == '-1':
                                    t = aggr_op + "(*)"

                                elif x['attr'][0] == 'c':
                                    # correlated attribute: previous block was a group by, this is one of its outputs
                                    # recupero l'output associato all'attributo correlato
                                    # b = block_id, oid = output id
                                    b, oid = x['attr'].split('_')
                                    t = aggr_op + "(" + ("DISTINCT" if aggr_op == 'COUNT' else "")+ "`" + self.getNextView() + "`.`" + "attr_" + str(oid) + "`)"

                                else:
                                    o = Output.objects.get(pk=x['attr'])
                                    summ = json.loads(o.summary)
                                    self.addJoinedTable(q1, summ[0][2])
                                    t = aggr_op + "(" + ("DISTINCT" if aggr_op == 'COUNT' else "")+ "`" + summ[0][0] + "`.`" + summ[0][1] + "`)"
                                q_next.sel.append((t,))
                                # save output names in case they need to be displayed in the final result
                                output_name = x['name']
                                # save output types (needed if block following group by is from a different data source, so the data from the current data source must be sent to the next one by creating a temporary table - hence we need to know column types)
                                if aggr_op == 'COUNT':
                                    output_type = 3
                                else:
                                    if x['attr'][0] == 'c':
                                        output_type = q1.other_outputs[int(oid)]['type']
                                    else:
                                        output_type = o.output_has_jtattribute_set.all()[0].jtAttr.attrType.id
                                q_next.other_outputs.append({'src': 'G', 'type': output_type, 'name': output_name})

                            q_next.sel.append((rsub[-1][2], rsub[-1][3]));

                            if q_next.keep_group_pk == True:
                                q_next.gby.append(q_next.group_pk_name)
                                q_next.sel.append(q_next.group_pk_name)
                                q_next_group_pk_name = (self.getNextView(), "attr_" + str(len(q_next.sel)-2))

                            h = self.compile_and_send_query(q_next,get_handle=True)

                            q_old = q_next
                            q_next = Query()
                            q_next.qe = curr.qe
                            q_next.ds = curr.qe.dsTable.dataSource
                            q_next.fro.append(curr.qe.dsTable.name)
                            q_next.fro.append(h[0])
                            q_next.jwhr.append((curr.qe.dsTable.name, curr.qe.dsTable.primaryKey, '=', h[0], HANDLE_KEY_ATTR, None, None, None, None, False))
                            q_next.gby_output_names = q_next_gby_output_names
                            q_next.gby_output_types = q_next_gby_output_types
                            
                            q_next.keep_group_pk = q1.keep_group_pk
                            if q_next.keep_group_pk == True:
                                q_next.group_pk_name = q_next_group_pk_name

                            q1 = q_old
                
                if curr.type == BASKET:
                    # TODO: implement case in which basket items are passed directly
                    if curr.src_table_name != None:
                        # name of table in which basket items are stored is known (e.g., for translators)
                        q_next.fro.append(curr.src_table_name)
                        q_next.jwhr.append((q_next.qe.dsTable.name, q_next.qe.dsTable.primaryKey, '=', curr.src_table_name, curr.src_pk_name, None, None, None, None, False))
                        q_next.keep_group_pk = True

                if q1 is not None:
                    q_next.num_prev_other_outputs = len(q1.other_outputs)
                return q_next
            
            elif curr.type == GENID:
                if q1:
                    q_next = q1
                else:
                    q_next = Query()
                q_next.gid_list.extend(curr.genid)
                q_next.apply_genid = True
                return q_next


    def addJoinedTable(self, q, jt, skipLast=False, outerJn=False):
        s = jt if type(jt) == list else json.loads(jt.summary)
        l = s[:-1] if skipLast else s
        for z in l:
            q.fro.append(z[0])
            q.fro.append(z[2])
            q.jwhr.append((z[0], z[1], '=', z[2], z[3], None, None, None, None, outerJn))
        oj_tables = set([x[3] for x in q.oj])
        # following is to remove duplicates in q.fro but maintaining order
        dset = set()
        q.fro = [x for x in q.fro if x not in dset and x not in oj_tables and not dset.add(x)]
        dset = set()
        q.jwhr = [x for x in q.jwhr if x not in dset and not dset.add(x)]

    def compile_and_send_query(self, q, get_handle=False, save_pk=False):
        url = q.ds.url + RUNQUERY_API
        data = {'s': q.sel,
                'f': q.fro,
                'jw': q.jwhr,
                'fw': q.fwhr,
                'oj': q.oj,
                'gb': q.gby,
                'h': q.hvg,
                'geth': get_handle,
                'sec_type' : q.sec_type,
                'sec_attr' : q.sec_attr,
                'sec_src' : q.sec_src,
                'distinct': q.distinct,
                'l': q.lim,
                'offset': q.offset,
                'viewname': self.getNextView(),
                'tables': q.tables,
                'save_pk': save_pk}
        print "Request: ", url
        #print "size: ", len(json.dumps(data)), " size (compressed): ", len(zlib.compress(json.dumps(data)))
        #print "size(compressed): ", len(zlib.compress(json.dumps(data)))
        #print "size(uncompressed): ", len(json.dumps(data))

        print data
        r = requests.post(url, data=zlib.compress(json.dumps(data)), verify=False, headers={'Content-Type': 'application/octet-stream'})
        #r = requests.post(url, data=json.dumps(data), verify=False, headers={'Content-Type': 'application/octet-stream'})
        print "Response received", r.status_code
        if r.status_code != 200:
            print "(error) response = ", r.content
        self.makeNewView()
        #print "size: ", len(r.text), " size (compressed): ", len(zlib.compress(r.text))
        if get_handle == False:
            try:
                x = json.loads(zlib.decompress(r.content))
            except:
                print "An error occurred"
                return []
            if save_pk == True:
                if q.ds.url not in self.cleanupdata.keys():
                    self.cleanupdata[q.ds.url] = {'handles': [], 'temptables': []}
                self.cleanupdata[q.ds.url]['temptables'].append(self.getLastView())
        else:
            x = r.json()
            if q.ds.url not in self.cleanupdata.keys():
                self.cleanupdata[q.ds.url] = {'handles': [], 'temptables': []}
            self.cleanupdata[q.ds.url]['handles'].append(x[0])
            self.cleanupdata[q.ds.url]['temptables'].extend(x[1:])

        return x
    
    def getLastView(self):
        return "_" + self.sesskey + '_' + self.quid + '_' + str(self.view_count - 1)

    def getNextView(self):
        return "_" + self.sesskey + '_' + self.quid + '_' + str(self.view_count)

    def makeNewView(self):
        self.view_count += 1

    def cleanup(self):
        for url, data in self.cleanupdata.items():
            try:
                r = requests.post(url + CLEANUP_API, data= {'handles' : data['handles'], 'temptables': data['temptables']}, verify=False)
            except Exception,e:
                print str(e)
