#!/usr/bin/python -u

from py2neo import *

import sys
sys.path.append('/srv/www/caquery')
from django.core.management import setup_environ 
import settings 
setup_environ(settings)

import urllib, urllib2
import ast
import json
from django.core.mail import EmailMessage
from datetime import datetime
from datetime import timedelta
from termcolor import cprint

from _caQuery.genealogyID import *


TREATED_MICE_TEMPLATE_ID = 25
AVAILABLE_ALIQUOTS_TEMPLATE_ID = 26
ALIQUOTS_WITH_TRANSF_EVT_TEMPLATE_ID = 28

gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)

wg_name = "Bertotti_WG"
start_date = datetime(2014, 1, 1)

human_dna_query = neo4j.CypherQuery(gdb,
    "start n = node({ node_id }) match (n)-[:hasInstance]->(a:DNA) match (a)<-[r:OwnsData]-(:WG {identifier: { wg_name }}) return id(a), a.identifier, r.startDate")
xeno_dna_query = neo4j.CypherQuery(gdb,
    "start n = node({ node_id }) match (n)-[r:generates*]->(a:DNA) where all (x in r where x.app <> 'implant') match (a)<-[rr:OwnsData]-(:WG {identifier: { wg_name }}) return id(a), a.identifier, rr.startDate")

human_rl_query = neo4j.CypherQuery(gdb,
    "start n = node({ node_id }) match (n)-[:hasInstance]->(a:RNALater) match (a)<-[r:OwnsData]-(:WG {identifier: { wg_name }}) return id(a), a.identifier, r.startDate order by a.identifier")
xeno_rl_query = neo4j.CypherQuery(gdb,
    "start n = node({ node_id }) match (n)<-[:hasInstance]-(semanticMouse)-[:hasSuffix]->(semanticAliquot)-[:hasInstance]->(a:RNALater) match (a)<-[r:OwnsData]-(:WG {identifier: { wg_name }}) return id(a), a.identifier, r.startDate order by a.identifier")
    #"start n = node({ node_id }) match (n)-[r:generates*]->(a:RNALater) where all (x in r where x.app <> 'implant') match (a)<-[rr:OwnsData]-(:WG {identifier: { wg_name }}) return id(a), a.identifier, rr.startDate order by a.identifier")

passage1_sorted_mouse_query = neo4j.CypherQuery(gdb,
    "start n = node({ node_id }) match (n)-[:hasInstance]->(:Viable)-[:generates {app:'implant'}]->(m:Biomouse) match (m)<-[:OwnsData]-(:WG {identifier: { wg_name }}) optional match (m)<-[:hasInstance]-(semanticMouse)-[:hasSuffix]->(semanticAliquot)-[:hasInstance]->(:Viable)-[:generates {app:'implant'}]->(mm:Biomouse) return id(m), m.identifier, count(mm) as CC order by CC, m.identifier")
    #"start n = node({ node_id }) match (n)-[:hasInstance]->()-[:generates*0.. {app:'split'}]->(:Viable)-[:generates {app:'implant'}]->(m:Biomouse) match (m)<-[r:OwnsData]-(:WG {identifier: { wg_name }}) optional match (m)-[:generates]->()-[:generates*0.. {app:'split'}]->(:Viable)-[:generates {app:'implant'}]->(mm:Biomouse) return id(m), m.identifier, count(mm) as CC, r.startDate order by CC, m.identifier")
sorted_mouse_query = neo4j.CypherQuery(gdb,
    "start n = node({ node_id }) match (n)<-[:hasInstance]-(semanticMouse0)-[:hasSuffix]->(semanticAliquot0)-[:hasInstance]->(:Viable)-[:generates {app:'implant'}]->(m:Biomouse) match (m)<-[:OwnsData]-(:WG {identifier: { wg_name }}) optional match (m)<-[:hasInstance]-(semanticMouse1)-[:hasSuffix]->(semanticAliquot1)-[:hasInstance]->(:Viable)-[:generates {app:'implant'}]->(mm:Biomouse) return id(m), m.identifier, count(mm) as CC order by CC, m.identifier")
    #"start n = node({ node_id }) match (n)-[:generates]->()-[:generates*0.. {app:'split'}]->(:Viable)-[:generates {app:'implant'}]->(m:Biomouse) match (m)<-[r:OwnsData]-(:WG {identifier: { wg_name }}) optional match (m)-[:generates]->()-[:generates*0.. {app:'split'}]->(:Viable)-[:generates {app:'implant'}]->(mm:Biomouse) return id(m), m.identifier, count(mm) as CC, r.startDate order by CC, m.identifier")

days_recent = 7

rl_aliquots = set()
no_rl = set()
mice_to_exclude = set()

def find_mice_to_exclude():
    # topi da escludere perche' parte di un treatment protocol

    url = settings.DOMAIN_URL +  '/mdam/api/runtemplate/'

    values_to_send = {'template_id': TREATED_MICE_TEMPLATE_ID}
    data = urllib.urlencode(values_to_send)

    try:
        u = urllib2.urlopen(url, data)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from "+str(url)   

    res = u.read()
    result = json.loads(res)

    return [GenealogyID(x[0]).zeroOutFieldsAfter('mouse').getGenID() for x in result['body']]

def sortAliquots(al):
    print "Sorting aliquots by date..."

    aliq_dict= {}

    al_recent = []
    al_old = []

    lastweek_start = datetime.now() - timedelta(days=days_recent)
    
    url = settings.DOMAIN_URL +  '/mdam/api/runtemplate/'

    values_to_send = {  'template_id': ALIQUOTS_WITH_TRANSF_EVT_TEMPLATE_ID,
                        'parameters': json.dumps([{'id': 0, 'values': al}])}
    data = urllib.urlencode(values_to_send)

    try:
        u = urllib2.urlopen(url, data)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from "+str(url)   

    res = u.read()
    result = json.loads(res)

    genids = set([x[1] for x in result['body']])
    missing = [x for x in al if x not in genids]
    if len(missing) > 0:
        print "Cannot find aliquots in biobank: ", missing

    for x in result['body']:
        al_genid = x[1]
        if al_genid[14] == '2': #discard historical aliquots
            print al_genid, ": discarding historical aliquot"
            continue

        skip = False
        for y in x[-1][0]:
            if y[0] != 'None':
                continue
            if y[1] == 'No': #executed
                print "%s : aliquot currently under derivation, skipping" % al_genid
                skip = True
                break
            elif y[4] == 'No': #failed
                print "%s : aliquot already derived successfully, skipping" % al_genid
                skip = True
                break
            elif y[3] == 'Yes': #exhausted
                print "%s : aliquot exhausted, skipping" % al_genid
                skip = True
                break
        if skip:
            continue

        #sampling date
        sdate = datetime.strptime(x[3], '%Y-%m-%d')
        #archival date
        adate = datetime.strptime(x[5], '%Y-%m-%d') if x[5] != 'None' else datetime.strptime("1909-04-22", "%Y-%m-%d") 
        if sdate >= lastweek_start:
            al_recent.append((al_genid, sdate, adate))
        else:
            al_old.append((al_genid, sdate, adate))

    al_recent.sort(lambda x,y: (y[1] - x[1]).days)
    al_old.sort(lambda x,y: (y[2] - x[2]).days)

    al_recent = [x[0] for x in al_recent]
    al_old = [x[0] for x in al_old]

    return al_recent, al_old

def check_dna(id, genid):
    if genid in mice_to_exclude:
        return False
    
    vector = GenealogyID(genid).getSampleVector()
    
    if vector == 'X':
        res = xeno_dna_query.execute(node_id=id, wg_name=wg_name)
    elif vector == 'H':
        res = human_dna_query.execute(node_id=id, wg_name=wg_name)
    
    return len(res) > 0

def get_RL(id, genid):
    if genid in mice_to_exclude:
        return []
    
    vector = GenealogyID(genid).getSampleVector()
    
    if vector == 'X':
        res = xeno_rl_query.execute(node_id=id, wg_name=wg_name)
    elif vector == 'H':
        res = human_rl_query.execute(node_id=id, wg_name=wg_name)

    if len(res) > 0:
        r = []
        for x in res.data:
            # take first 19 characters (omit milliseconds)
            if datetime.strptime(x[2][:19], "%Y-%m-%d %H:%M:%S") >= start_date:
                r.append(x[1])
            else:
                print "discarding old aliquot: ", x[1]
        if len(r) == 0:
            return []
    else:
        return []


    # check aliquot availability (i.e., not exhausted) in BioBank
    url = settings.DOMAIN_URL +  '/mdam/api/runtemplate/'

    values_to_send = {'template_id': AVAILABLE_ALIQUOTS_TEMPLATE_ID, 'parameters': json.dumps([{'id': 0, 'values': r}])}
    data = urllib.urlencode(values_to_send)

    try:
        u = urllib2.urlopen(url, data)
    except Exception, e:
        print e
        print "An error occurred while trying to retrieve data from "+str(url)   

    res = u.read()
    result = json.loads(res)

    return [x[0] for x in result['body']]

def visit_subtree(parent_id, parent_gid, parent_has_dna, passage):
    print "[P%d] parent: %s, has_DNA: %s" % (passage, parent_gid, parent_has_dna)
    children = sorted_mouse_query.execute(node_id=parent_id, wg_name=wg_name)
    children = [[x[0], x[1], x[2], False] for x in children]
    if parent_has_dna == True:
        print "     skip passage"
        for m in children:
            m[3] = check_dna(m[0], m[1])
    else:
        dna = False
        chosen = None
        for m in children:
            m[3] = check_dna(m[0], m[1])
            if m[3]:
                dna = True
                chosen = m[1]
        if not dna:
            for m in children:
                rl = get_RL(m[0], m[1])
                if len(rl) > 0:
                    rl_aliquots.add(rl[0])
                    chosen = rl[0]
                    m[3] = True
                    break
        if not chosen:
            print "     no RL available for group"
            no_rl.add(parent_gid)
        else:
            if not dna:
                cprint("     chosen: %s" % chosen, 'green')
            else:
                print "     %s has DNA" % chosen
    for m in children:
        c_id = m[0]
        c_gid = m[1]
        c_num_children = m[2]
        has_dna = m[3]
        if c_num_children > 0:
            visit_subtree(c_id, c_gid, has_dna, passage+1)

def check_case(case_id, case_gid):
    # human aliquots
    print "[P0]"
    if not check_dna(case_id, case_gid):
        rl = get_RL(case_id, case_gid)
        if len(rl) > 0:
            rl_aliquots.add(rl[0])
            cprint("     chosen: %s" % rl[0], "green")
        else:
            print "     %s has no DNA or RL" % case_gid
            no_rl.add(case_gid)
    else:
        print "     %s has DNA" % case_gid
    
    # passage-1 mice
    mice1 = passage1_sorted_mouse_query.execute(node_id=case_id, wg_name=wg_name)
    if len(mice1) == 0:
        return
    print "[P1]"
    for m in mice1:
        mouse_id = m[0]
        mouse_gid = m[1]
        if not check_dna(mouse_id, mouse_gid):
            rl = get_RL(mouse_id, mouse_gid)
            if len(rl) > 0:
                rl_aliquots.add(rl[0])
                cprint("     chosen: %s" % rl[0], "green")
            else:
                print "     %s has no DNA or RL" % mouse_gid
                no_rl.add(mouse_gid)
        else:
            print "     %s has DNA" % mouse_gid

    # passage-2 mice
    # call recursive visit by setting parent_has_dna to False
    # so that a passage-2 mouse is always chosen
    for m in mice1:
        mouse_id = m[0]
        mouse_gid = m[1]
        c_num_children = m[2]
        if c_num_children > 0:
            visit_subtree(mouse_id, mouse_gid, False, 2)

def dna_extraction():
    print "Retrieving mice to exclude from aliquot extraction..."
    mice_to_exclude = set(find_mice_to_exclude())
    print len(mice_to_exclude), "mice to exclude found"
    print "Retrieving cases..."
    # N.B.  (1) Devo partire anche dai casi X (=~ '.{9}X.*') per tenere conto di aliquote per cui non esiste la parte H?
    #       (2) Devo inserire la relazione con il WG anche qui?
    q = "match (:Genid:Collection)-[:hasSuffix]->()-[:hasSuffix]->(caso) where caso.identifier =~ '.{9}H.*' return id(caso), caso.identifier"
    cq = neo4j.CypherQuery(gdb,q)
    cases = cq.execute()
    print len(cases), " case(s) found"

    for c in cases:
        case_id = c[0]
        case_gid = c[1]
        #gid = GenealogyID(case_gid)
        #if gid.getOrigin() == 'CRC' and int(gid.getCaseCode()) <= 430:
        #    continue
        print "===[ Case %s ]====================" % case_gid
        check_case(case_id, case_gid)
        print ""

    print ""
    print "Aliquots for extraction (%d):" % len(rl_aliquots)

    rl = sorted(rl_aliquots)
    al_recent, al_old = sortAliquots(rl)

    recipients = []
    sender = ''
    subject = 'Aliquots for DNA Extraction'
    
    text_content = ""
    #text_content = "Red Node = Aliquot selected for extraction\nBlue Border = DNA already extracted\nBox Shape = RNAlater aliquots present\n\n"
    text_content = text_content + "Recent aliquots (" + (datetime.now() - timedelta(days=days_recent)).strftime("%a, %d %b %Y") + " - " + datetime.now().strftime("%a, %d %b %Y") + "): " + str(len(al_recent)) +"\n"
    
    for a in al_recent:
        #urlimg = ""
        #if aliquots.index(a) != 0:
        #    
        #    if a[:9] == aliquots[aliquots.index(a)-1][:9]:
        #        urlimg = ""
        #    
        #    else:
        #        urlimg = ' http://devircc.polito.it/tree_images/'+ a[:9] +'00000000000000000.png'
        #else:
        #    urlimg = ' http://devircc.polito.it/tree_images/'+ a[:9] +'00000000000000000.png'
        #urlimg = ' http://lasircc.polito.it/tree_images/'+ a[:9] +'00000000000000000.png'

        #text_content = text_content + a + urlimg + '\n'
        text_content = text_content + a + '\n'

    text_content = text_content + "\nOlder aliquots: " + str(len(al_old)) + "\n"

    for a in al_old:
        #urlimg = ' http://lasircc.polito.it/tree_images/'+ a[:9] +'00000000000000000.png'        
        #text_content = text_content + a + urlimg + '\n'            
        text_content = text_content + a + '\n'            

    print ""
    print "Sending email"
    print "Recipients: ", ", ".join(recipients)
    print "Content:"
    cprint(text_content, 'cyan')

    try:
        e = EmailMessage(subject=subject, body=text_content, from_email=sender, to=recipients)
        e.attach(filename="Recent_aliquots.las", mimetype = "text/plain", content = '\n'.join(al_recent))
        e.attach(filename="Old_aliquots.las", mimetype = "text/plain", content = '\n'.join(al_old))
        e.send()
        print
        print 'Email sent'
    except Exception, e:
        print e
        cprint('Error sending email', 'red')

if __name__=='__main__':
    dna_extraction()


# N.B. MODIFICHE DA FARE IN FUTURO
# Al fine di valutare correttamente, nell'ottica del fingerprinting, anche topi/aliquote
# ottenuti tramite condivisione/cessione da parte di altri gruppi di ricerca, occorre
# riconsiderare nel seguente modo il concetto di "passaggio":
# -per ora il "passaggio" considerato per il fingerprinting coincide con il reale "passaggio"
# dell'entita' biologica
# -in futuro, occorre considerare di "passaggio 0" le aliquote o i topi (anche se di passaggio
# reale > 0) che non hanno genitori topi/aliquote all'interno della porzione di albero condiviso
# e.g., nel caso dei topi, sono "veri" passaggi > 0 - allo scopo del fingerprinting - solo quelli
# per cui esiste, risalendo verso la radice dell'albero, una sequenza
# (mouse)<-[:generates {app: 'Implant'}]-(:Viable)<-[:hasInstance]-(semanticAliquot)<-[:hasSuffix]-(semanticFatherMouse)-[:hasInstance]->(fatherMouse)
