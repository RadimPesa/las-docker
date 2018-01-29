from __init__ import *
from basic import *
from py2neo import neo4j
import re

ID_TEMPLATE_MICE_FROM_GENID_WITH_T_TREATMENT_T_IMPLANTS_T_EXPLANTS = 72 # 70
ID_TEMPLATE_ALIQUOTS_FROM_GENID = 10
RUNTEMPLATE_API_NAME = "runtemplate-api"

def getChildren(mice, m):
    children = []
    for x, info in mice.iteritems():
        if info['parentAliquot'] is not None and GenealogyID(info['parentAliquot']).zeroOutFieldsAfter('mouse').setImplantSite('SCR').getGenID() == m:
            children.append(x)
    return children

def checkVitalAliquots(aliquots_list):
    for a in aliquots_list:
        if GenealogyID(a).getArchivedMaterial() == 'VT':
            return True
    return False

def getXenoData(case, user, toExclude=[], missingRels=[], removeIsolated=False):
    # validate case genid (e.g. CRC0096)
    if len(case) != 7:
        raise Exception("Invalid case %s" % case)

    if user is None:
        raise Exception("No user specified for data access permission")

    # validate toExclude
    for g in toExclude:
        if len(g) != 26:
            raise Exception("toExclude: invalid genid %s" % g)

    # validate missingRels
    for rel in missingRels:
        for i in xrange(0,1):
            if len(rel[i]) != 26:
                raise Exception("missingRels: invalid genid %s" % rel[i])

    # run query against graph: get father-child relationships
    gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
    case_id = case + ".*"
    query_text = "match (x:Biomouse) where x.identifier =~ { case_id } and not (x.identifier in { to_exclude } ) optional match (x)<-[:generates]-(n) return x.identifier, n.identifier"
    query = neo4j.CypherQuery(gdb, query_text)
    res = query.execute(case_id=case_id,to_exclude=toExclude)

    mice = {r[0]: {'historical': False, 'parentAliquot': r[1] if r[1] and GenealogyID(r[1]).getSampleVector() == 'X' else None, 'parentMouse': GenealogyID(r[1]).zeroOutFieldsAfter('mouse').setImplantSite('SCR').getGenID() if r[1] and GenealogyID(r[1]).getSampleVector() == 'X' else None, 'treatments': [], 'aliquots': [], 'vital': None, 'implantDate': None, 'explantDate': None} for r in res}

    if len(mice) == 0:
        # no mice found -- case probably doesn't exist
        return mice

    # load missing father-child relationships from list (if any)
    for rel in missingRels:
        try:
            if GenealogyID(rel[1]).isAliquot():
                mice[rel[0]]['parentAliquot'] = rel[1]
                mice[rel[0]]['parentMouse'] = GenealogyID(rel[1]).zeroOutFieldsAfter('mouse').setImplantSite('SCR').getGenID()
            else:
                mice[rel[0]]['parentMouse'] = rel[1]
        except:
            print "Warning: %s not found" % rel[0]
            pass

    # create missing parents
    toAdd = {}
    for m,info in mice.iteritems():
        if info['parentMouse'] and info['parentMouse'] not in mice:
            toAdd[info['parentMouse']] = {'historical': True, 'parentAliquot': None, 'parentMouse': None, 'treatments': [], 'aliquots': [], 'vital': None}
    mice.update(toAdd)

    
    # run query against graph: retrieve orphaned aliquots
    collection_id = case[:7] + '0' * 19
    query_text = "match (c:Collection)-->(a:Aliquot) where c.identifier = { collection_id } return a.identifier"
    query = neo4j.CypherQuery(gdb, query_text)
    res = query.execute(collection_id=collection_id)

    # check availability for orphaned aliquots
    ###

    old_mice = {}
    for r in res:
        mouse_genid = GenealogyID(r[0]).zeroOutFieldsAfter('mouse').setImplantSite('SCR')
        if mouse_genid.getSampleVector() != 'X':
            continue
        else:
            mouse_genid = mouse_genid.getGenID()
        if mouse_genid not in mice:
            if mouse_genid not in old_mice:
                old_mice[mouse_genid] = []
            old_mice[mouse_genid].append(r[0])
    for m, a in old_mice.iteritems():
        mice[m] = {'historical': True, 'parentAliquot': None, 'parentMouse': None, 'treatments': [], 'aliquots': [], 'vital': None, 'implantDate': None, 'explantDate': None} # check if any of the aliquots are vital
    
    # run query against MDAM: mice with treatments, implants and explants
    # N.B. this query also enforces data ownership checks except when admin is in the working group list
    wg_list = set(map(lambda x: x.WG.name, user.wg_user_set.all()))
    if "admin" not in wg_list:
        wg_list = list(wg_list)
        params = {'parameters': '[{"values":' + json.dumps(wg_list) + ', "id": 1}, {"values":' + json.dumps(mice.keys()) + ' , "id": 0}]', 'template_id': ID_TEMPLATE_MICE_FROM_GENID_WITH_T_TREATMENT_T_IMPLANTS_T_EXPLANTS}
    else:
        params = {'parameters': '[{"values":' + json.dumps(mice.keys()) + ' , "id": 0}]', 'template_id': ID_TEMPLATE_MICE_FROM_GENID_WITH_T_TREATMENT_T_IMPLANTS_T_EXPLANTS}
    url = settings.DOMAIN_URL + reverse(RUNTEMPLATE_API_NAME)
    r = requests.post(url, data=params, verify=False)
    resp = json.loads(r.text)

    #saved_record = resp['body'][0]
    #print "saved_record:", saved_record
    print "resp", resp
    for r in resp['body']:

        mice[r[1]]['vital'] = r[9] == 'implanted'
        mice[r[1]]['deathDate'] = r[7]
        for t in r[-1][1]:
            mice[r[1]]['treatments'].append(t[1])
        if len(r[-1][0]) > 0:
            mice[r[1]]['implantDate'] = r[-1][0][0][5]
        if len(r[-1][2]) > 0:
            mice[r[1]]['explantDate'] = r[-1][2][0][3]

    # run query against MDAM: aliquots
    params = {'parameters': '[{"values":' + json.dumps([GenealogyID(x).clearFieldsAfter('mouse').getGenID() for x in mice.keys()]) + ' , "id": 0}]', 'template_id': ID_TEMPLATE_ALIQUOTS_FROM_GENID}
    r = requests.post(url, data=params, verify=False)
    resp = json.loads(r.text)

    # store info about aliquots and vital yes/no
    for r in resp['body']:
        if r[1] == 'True':
            aliq_genid = GenealogyID(r[0])
            mouse_genid = GenealogyID(r[0]).zeroOutFieldsAfter('mouse').setImplantSite('SCR').getGenID()
            mice[mouse_genid]['aliquots'].append(r[0])
            mice[mouse_genid]['vital'] = mice[mouse_genid]['vital'] or aliq_genid.getArchivedMaterial() == 'VT'

    # prune mice that are orphan and have no children nor treatment
    if removeIsolated == True:
        print "%d mice before removal" % len(mice)
        to_delete = []
        for m,info in mice.iteritems():
            if info['parentAliquot'] is None and info['parentMouse'] is None and len(getChildren(mice, m)) == 0 and len(info['treatments']) == 0:
                to_delete.append(m)
        for x in to_delete:
            del mice[x]
        print "%d mice after removal" % len(mice)

    
    return mice

@laslogin_required
@login_required
def plotXenoTree(request):
    if request.method == 'GET':
        if 'case' in request.GET:

            case_id = request.GET['case'].upper()
            removeIsolated = True if request.GET.get('removeisolated', None) else False
            
            import time
            start = time.time()
            data = getXenoData(case=case_id, removeIsolated=removeIsolated, user=request.user)
            print "time: ", time.time() - start
            
            if data == {}:
                notFound = True
            else:
                notFound = False

            try:
                info = GenealogyTreeInfo.objects.get(user=request.user.id,case=case_id)
                parents = info.parents
            except:
                parents = {}

            print "notFound: ", notFound
            return render_to_response('genealogytree.html', {'mice': data, 'plot': True, 'case_id': case_id, 'removeIsolated': removeIsolated, 'notFound': notFound, 'parents': parents}, RequestContext(request)) # , 'missing': missing
        
        else:
            
            return render_to_response('genealogytree.html', {'plot': False}, RequestContext(request))

    elif request.method == 'POST':
        if 'case' in request.POST and 'parents' in request.POST:

            case_id = request.POST['case'].upper()
            parents = json.loads(request.POST['parents'])

            try:
                info = GenealogyTreeInfo.objects.get(user=request.user.id,case=case_id)
            except:
                info = GenealogyTreeInfo()
                info.user = request.user.id
                info.case = case_id

            info.timestamp = datetime.datetime.now()
            info.parents.update(parents)

            info.save()

            return HttpResponse("ok")

        else:
            return HttpResponseServerError("Invalid format")

    else:
        return render_to_response('genealogytree.html', {'plot': False}, RequestContext(request))

