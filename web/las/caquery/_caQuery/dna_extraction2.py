#!/usr/bin/python -u
import sys
import site
import os
site.addsitedir('~/.virtualenvs/venvdj1.4/local/lib/python2.7/site-packages')

sys.path.append('/srv/www/caquery')

activate_env=os.path.expanduser("~/.virtualenvs/venvdj1.4/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

from py2neo import *
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

#settings.GRAPH_DB_URL = "http://localhost:17474/db/data/"
#settings.DOMAIN_URL = "https://lasircc.polito.it"

TREATED_MICE_TEMPLATE_ID = 25
AVAILABLE_ALIQUOTS_TEMPLATE_ID = 26
ALIQUOTS_WITH_TRANSF_EVT_TEMPLATE_ID = 31

gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)

wg_name = "Bertotti_WG"
start_date = datetime(2008, 1, 1)


human_dna_query = neo4j.CypherQuery(gdb,
    "start n = node({ node_id }) match (n)-[:hasInstance]->(a:DNA) match (a)<-[r:OwnsData]-(:WG {identifier: { wg_name }}) where not(has(r.endDate)) return id(a), a.identifier, r.startDate")
xeno_dna_query = neo4j.CypherQuery(gdb,
    "start n = node({ node_id }) match (n)-[:hasSuffix]->(semanticAliquot)-[:hasInstance]->(a:DNA) match (a)<-[rr:OwnsData]-(:WG {identifier: { wg_name }}) where not(has(rr.endDate)) return id(a), a.identifier, rr.startDate")

human_rl_query = neo4j.CypherQuery(gdb,
    "start n = node({ node_id }) match (n)-[:hasInstance]->(a:RNALater) match (a)<-[r:OwnsData]-(:WG {identifier: { wg_name }}) where not(has(r.endDate)) return id(a), a.identifier, r.startDate order by a.identifier")
xeno_rl_query = neo4j.CypherQuery(gdb,
    "start n = node({ node_id }) match (n)-[:hasSuffix]->(semanticAliquot)-[:hasInstance]->(a:RNALater) match (a)<-[r:OwnsData]-(:WG {identifier: { wg_name }}) where not(has(r.endDate)) return id(a), a.identifier, r.startDate order by a.identifier")


days_recent = 10

rl_aliquots = set()
no_rl = set()
mice_to_exclude = set()

MICE_TO_EXCLUDE_FILE='/srv/www/caquery/_caQuery/mice_to_exclude.txt'

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

    from_mdam = [GenealogyID(x[0]).zeroOutFieldsAfter('mouse').getGenID() for x in result['body']]

    
    from_file = []
    try:
        with open(MICE_TO_EXCLUDE_FILE, "r") as f:
            for line in f:
                try:
                    line = line.strip()
                    if len(line) == 0:
                        continue
                    from_file.append(GenealogyID(line).zeroOutFieldsAfter('mouse').getGenID())
                except:
                    pass
    except:
        print "%s not found" % MICE_TO_EXCLUDE_FILE

    mice = from_mdam + from_file
    mice = [x[:17] for x in mice]
    return mice


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
    print result

    genids = set([x[1] for x in result['body']])
    missing = [x for x in al if x not in genids]
    if len(missing) > 0:
        print "Cannot find aliquots in biobank: ", missing

    for x in result['body']:
        al_genid = x[1]
        #if al_genid[14] == '2': #discard historical aliquots
        #    print al_genid, ": discarding historical aliquot"
        #    continue

        skip = False
        # data from Translator: Transf. event as mother
        for y in x[-1][0]:
            if y[0] != 'None':
                continue
            if y[1].lower() in ['no', 'false']: #executed
                print "%s : aliquot currently under derivation, skipping" % al_genid
                skip = True
                break
            elif y[4].lower() in ['no', 'false']: #failed
                print "%s : aliquot already derived successfully, skipping" % al_genid
                skip = True
                break
            elif y[3].lower() in ['yes', 'true']: #exhausted
                print "%s : aliquot exhausted, skipping" % al_genid
                skip = True
                break
        if skip:
            continue

        # data from Translator: Container
        if len(x[-1][1]) > 0:
            barcode = x[-1][1][0][0]
        else:
            barcode = ''

        '''
        # retrieve barcode of corresponding mouse (if it's a mouse)
        genid = GenealogyID(al_genid)
        if genid.getSampleVector() == 'X':
            values_to_send = {  'template_id': MICE_TEMPLATE_ID,
                                'parameters': json.dumps([{'id': 0, 'values': [genid.clearFieldsAfter('mouse').getGenID()]}])}
            data = urllib.urlencode(values_to_send)

            try:
                u = urllib2.urlopen(url, data)
            except Exception, e:
                print e
                print "An error occurred while trying to retrieve data from "+str(url)   

            res = u.read()
            result = json.loads(res)['body']
            if len(result) > 0:
                barcode = result[0][4]
            else:
                barcode = ''
        else:
            barcode = ''
        '''
            
        #sampling date
        sdate = datetime.strptime(x[3], '%Y-%m-%d')
        #archival date
        adate = datetime.strptime(x[5], '%Y-%m-%d') if x[5] != 'None' else datetime.strptime("1909-04-22", "%Y-%m-%d") 
        if sdate >= lastweek_start:
            al_recent.append((al_genid, sdate, adate, barcode))
        else:
            al_old.append((al_genid, sdate, adate, barcode))

    al_recent.sort(lambda x,y: (y[1] - x[1]).days)
    al_old.sort(lambda x,y: (y[2] - x[2]).days)

    al_recent = [(x[0], x[3]) for x in al_recent]
    al_old = [(x[0], x[3]) for x in al_old]

    return al_recent, al_old


def check_dna(id, genid):
    print "---check DNA: ", genid, genid[:17] in mice_to_exclude
    if genid[:17] in mice_to_exclude:
        print "Excluding treated mice:", genid
        return False
    
    vector = GenealogyID(genid).getSampleVector()
    
    if vector == 'X':
        res = xeno_dna_query.execute(node_id=id, wg_name=wg_name)
    elif vector == 'H':
        res = human_dna_query.execute(node_id=id, wg_name=wg_name)
    
    return len(res) > 0


def get_RL(id, genid):
    print "---check RL: ", genid, genid[:17] in mice_to_exclude
    if genid[:17] in mice_to_exclude:
        print "Excluding treated mice:", genid
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


def check_case(case_id, case_gid):
    Hq = "start n = node({ id }) match (n)-[:hasSuffix]->(c) where c.identifier =~ '.{9}H.*' return id(c), c.identifier"
    Xq = "start n = node({ id }) match (n)-[:hasSuffix]->(c) where c.identifier =~ '.{9}X.*' return id(c), c.identifier"
    hcq = neo4j.CypherQuery(gdb,Hq)
    xcq = neo4j.CypherQuery(gdb,Xq)
    h = hcq.execute(id=case_id)
    x = xcq.execute(id=case_id)
    human_case_id, human_case_gid = (h[0][0], h[0][1]) if len(h) > 0 else (None, None)
    xeno_case_id, xeno_case_gid = (x[0][0], x[0][1]) if len(x) > 0 else (None, None)

    # human aliquots
    print "HUMAN:"
    if human_case_id != None:
        print "  [P0]"
        if not check_dna(human_case_id, human_case_gid):
            rl = get_RL(human_case_id, human_case_gid)
            if len(rl) > 0:
                rl_aliquots.add(rl[0])
                print("     chosen: %s" % rl[0])
            else:
                print "     %s has no DNA or RL" % human_case_gid
                no_rl.add(human_case_gid)
        else:
            print "     %s has DNA" % human_case_gid
    else:
        print "Case has no human aliquots"
    
    # xeno aliquots
    print "XENO:"
    if xeno_case_id != None:

        # iterate over lineages
        lineage_q = "start n = node({ id }) match (n)-[:hasSuffix]->(l) return id(l), l.identifier order by l.identifier"
        lcq = neo4j.CypherQuery(gdb,lineage_q)
        lineages = lcq.execute(id=xeno_case_id)

        for l in lineages:

            print "[L%s]" % GenealogyID(l[1]).getLineage()

            # iterate over passages
            passage_q = "start n = node({ id }) match (n)-[:hasSuffix]->(p) return id(p), p.identifier order by p.identifier"
            pcq = neo4j.CypherQuery(gdb,passage_q)
            passages = pcq.execute(id=l[0])

            fatherHasDna = {}

            for p in passages:
                pp = int(GenealogyID(p[1]).getSamplePassage())
                print "  [P%d]" % pp
                
                if pp == 1:
                    # get all semantic mice
                    passage1mice_q = "start n = node({ id }) match (n)-[:hasSuffix]->(semanticMouse) return id(semanticMouse), semanticMouse.identifier"
                    p1q = neo4j.CypherQuery(gdb,passage1mice_q)
                    mice = p1q.execute(id=p[0])
                    
                    # a DNA aliquot must exist or be scheduled for extraction for each mouse
                    for m in mice:

                        mouse_id = m[0]
                        mouse_gid = m[1]
                        if not check_dna(mouse_id, mouse_gid):
                            rl = get_RL(mouse_id, mouse_gid)
                            if len(rl) > 0:
                                rl_aliquots.add(rl[0])
                                print("     chosen: %s" % rl[0])
                            else:
                                print "     %s has no DNA or RL" % mouse_gid
                                no_rl.add(mouse_gid)
                        else:
                            print "     %s has DNA" % mouse_gid

                elif pp >= 2:
                    # a DNA aliquot must exist for each group of siblings if parent has no DNA, else group will be skipped
                    # get passage mice, grouped by father mouse (if any), where mice within each group are sorted by increasing number of children (if any)
                    passage2mice_q =    """start n = node({ passage_node_id })
                                        match (n)-[:hasSuffix]->(semanticMouse)-[:hasInstance]->(x)
                                        match (x)<-[o:OwnsData]-(:WG {identifier: { wg_name }})
                                        where not(has(o.endDate)) 
                                        optional match (semanticMouse)-[:hasSuffix]->(semanticAliquot)-[:hasInstance]->(:Viable)-[:generates {app:'implant'}]->(mm:Biomouse)<-[oo:OwnsData]-(:WG {identifier: { wg_name }})
                                        where not(has(oo.endDate)) 
                                        with semanticMouse, x, count(mm) as childrenCount order by childrenCount, x.identifier
                                        optional match (semanticFather:Genid)-[:hasSuffix]->(:Genid)-[:hasInstance]->(vt:Viable)-[:generates]->(x), (vt)<-[o:OwnsData]-(:WG {identifier: { wg_name }})
                                        where not(has(o.endDate)) 
                                        return id(semanticFather), collect(id(semanticMouse)), collect(semanticMouse.identifier), collect(childrenCount), semanticFather.identifier"""

                    p2q = neo4j.CypherQuery(gdb,passage2mice_q)
                    groups = p2q.execute(passage_node_id=p[0], wg_name=wg_name)
                    childHasDna = {}

                    for g in groups:
                        father_id = g[0]
                        father_gid = g[4]
                        children = zip(g[1], g[2], g[3])

                        # if there is a procedural father, only one mouse from the current group will be selected for DNA extraction
                        # conversely, if the current group has no procedural father, then all mice in the group must be selected
                        if father_id == None:
                            print "     Group_father: None, mice_in_group: %d" % len(children)
                            print "         Skipping group"
                            for m in children:
                                childHasDna[m[0]] = check_dna(m[0], m[1])
                            
                            '''for m in children:
                                if not check_dna(m[0], m[1]):
                                    rl = get_RL(m[0], m[1])
                                    if len(rl) > 0:
                                        rl_aliquots.add(rl[0])
                                        cprint("     chosen: %s" % rl[0], "green")
                                    else:
                                        print "     %s has no DNA or RL" % m[1]
                                else:
                                    print "     %s has DNA" % m[1]
                            '''
                        
                        else:
                            print "     Group_father: %s, has_dna: %s, mice_in_group: %d" % (father_gid, fatherHasDna.get(father_id, False), len(children))
                            if not fatherHasDna.get(father_id, False):
                                dna = False
                                chosen = None
                                for m in children:
                                    hasDna = check_dna(m[0], m[1])
                                    childHasDna[m[0]] = hasDna
                                    if hasDna:
                                        dna = True
                                        chosen = m[1]
                                if not dna:
                                    for m in children:
                                        rl = get_RL(m[0], m[1])
                                        if len(rl) > 0:
                                            rl_aliquots.add(rl[0])
                                            chosen = rl[0]
                                            childHasDna[m[0]] = True
                                            break
                                if not chosen:
                                    print "         no RL available for group"
                                else:
                                    if not dna:
                                        print("         chosen: %s" % chosen)
                                    else:
                                        print "         %s has DNA" % chosen

                            else:
                                print "         Skipping group"
                                for m in children:
                                    childHasDna[m[0]] = check_dna(m[0], m[1])

                        print "\n"

                    fatherHasDna = childHasDna
                    

                else:
                    "Incorrect passage number: ", pp

    else:
        print "Case has no xeno aliquots"
    return


def dna_extraction():
    print "Retrieving mice to exclude from aliquot extraction..."
    global mice_to_exclude
    mice_to_exclude = set(find_mice_to_exclude())
    print len(mice_to_exclude), "mice to exclude found"
    print "Retrieving cases..."
    # N.B.  (1) Devo partire anche dai casi X (=~ '.{9}X.*') per tenere conto di aliquote per cui non esiste la parte H?
    #       (2) Devo inserire la relazione con il WG anche qui?
    q = "match (:Genid:Collection)-[:hasSuffix]->(caso) return id(caso), caso.identifier"
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
        text_content = text_content + '\t'.join(a) + '\n'

    text_content = text_content + "\nOlder aliquots: " + str(len(al_old)) + "\n"

    for a in al_old:
        #urlimg = ' http://lasircc.polito.it/tree_images/'+ a[:9] +'00000000000000000.png'        
        #text_content = text_content + a + urlimg + '\n'            
        text_content = text_content + '\t'.join(a) + '\n'            

    print ""
    print "Sending email"
    print "Recipients: ", ", ".join(recipients)
    print "Content:"
    cprint(text_content, 'cyan')

    try:
        headers = '\t'.join(['Aliquot GenealogyID', 'Aliquot barcode'])
        e = EmailMessage(subject=subject, body=text_content, from_email=sender, to=recipients)
        e.attach(filename="Recent_aliquots.las", mimetype = "text/plain", content = '\n'.join([headers] + ['\t'.join(a) for a in al_recent]))
        e.attach(filename="Old_aliquots.las", mimetype = "text/plain", content = '\n'.join([headers] + ['\t'.join(a) for a in al_old]))
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
