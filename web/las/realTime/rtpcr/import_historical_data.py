import sys
import site
import os
sys.path.append('..')
site.addsitedir('~/.virtualenvs/venvdj1.4/local/lib/python2.7/site-packages')
path = '/srv/www'
if path not in sys.path:
    sys.path.insert(0, '/srv/www')
os.environ['DJANGO_SETTINGS_MODULE'] = 'realTime.settings'
# Activate your virtual env
activate_env=os.path.expanduser("~/.virtualenvs/venvdj1.4/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

from django.core.management import setup_environ
from realTime import settings
setup_environ(settings)
from rtpcr.models import *
from django.contrib.auth.models import User
from py2neo import neo4j
from django.utils import timezone
import argparse
from django.db import transaction

neo4j._add_header('X-Stream', 'true;format=pretty')

gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)

query_human_DNA = neo4j.CypherQuery(gdb, "match (c:Collection {identifier: { caseCode } +'0000000000000000000'})-[:hasSuffix]->(tissue:Genid {identifier: { caseCode } + { tissue } + '00000000000000000'})-[:hasSuffix]->(vector:Genid {identifier: { caseCode } + { tissue } + 'H0000000000000000'})-[:hasInstance]->(x:Aliquot:DNA) return x.identifier order by x.identifier limit 1")

query_xeno_1stpassage_DNA = neo4j.CypherQuery(gdb, "match (c:Collection {identifier: { caseCode } + '0000000000000000000'})-[:hasSuffix]->(tissue:Genid {identifier: { caseCode } + { tissue } + '00000000000000000'})-[:hasSuffix]->(vector:Genid {identifier: { caseCode } + { tissue } + 'X0000000000000000'})-[:hasSuffix]->(lineage:Genid)-[:hasSuffix]->(passage:Genid)-[:hasSuffix*1..]->()-[:hasInstance]->(x:Aliquot:DNA) where substring(passage.identifier, 12, 2) = '01' return x.identifier order by x.identifier limit 1")

query_xeno_2ndpassage_DNA = neo4j.CypherQuery(gdb, "match (c:Collection {identifier: { caseCode } + '0000000000000000000'})-[:hasSuffix]->(tissue:Genid {identifier: { caseCode } + { tissue } + '00000000000000000'})-[:hasSuffix]->(vector:Genid {identifier: { caseCode } + { tissue } + 'X0000000000000000'})-[:hasSuffix]->(lineage:Genid)-[:hasSuffix]->(passage:Genid)-[:hasSuffix*1..]->()-[:hasInstance]->(x:Aliquot:DNA) where substring(passage.identifier, 12, 2) = '02' return x.identifier order by x.identifier limit 1")

def parseTSV(filename):
    cases = []
    with open(filename, "r") as f:
        header_line = f.readline()
        genes = header_line.strip().split('\t')[2:]
        for line in f:
            if line.startswith('#') or line.strip() == '':
                continue
            case, aliquot, gcns = line.strip().split('\t', 2)
            if aliquot == '-':
                vector = 'X'
                tissue = 'LM'
                if vector == 'H':
                    res = query_human_DNA.execute(caseCode=case, tissue=tissue)
                elif vector == 'X':
                    res = query_xeno_1stpassage_DNA.execute(caseCode=case, tissue=tissue)
                    if len(res) == 0:
                        res = query_xeno_2ndpassage_DNA.execute(caseCode=case, tissue=tissue)
                else:
                    raise Exception("Unknow vector '%s'" % vector)
                aliquot = res[0][0] if len(res) else None
            cases.append({'case': case, 'genid': aliquot, 'gcns': gcns.split('\t')})
    return genes, cases

def setUpDatabaseEntries(case_aliquot_gcns, reqTitle, reqDescription, username):
    aliquots = [v['genid'] for v in case_aliquot_gcns if v['genid'] is not None]
    try:
        user = User.objects.get(username=username)
    except Exception as e:
        print "User %s not found, terminating" % username
        return

    with transaction.commit_on_success():
        r = Request()
        r.idOperator = user
        r.timestamp = timezone.now()
        r.title = reqTitle
        r.description = reqDescription
        r.owner = user
        r.pending = False
        r.timechecked = timezone.now()
        r.time_executed = None
        r.save()

        print "Request created"

        # N.B. aliquots can't be bulk-created because bulk_create does not set the pk, which is needed to create ahr
        ahr_objects = []
        for a_genid in aliquots:
            try:
                a = Aliquot.objects.get(genId=a_genid)
            except:
                a = Aliquot()
                a.genId = a_genid
                a.exhausted = False
                a.save()
            ahr = Aliquot_has_Request()
            ahr.aliquot_id = a
            ahr.request_id = r
            ahr_objects.append(ahr)
        Aliquot_has_Request.objects.bulk_create(ahr_objects)

    print "Aliquots added"

def generateResultFile(srcfilename, genes, case_aliquot_gcns):
    outfilename = '.'.join(srcfilename.split('.')[:-1])+'_results.tsv'
    headers = ['Sample'] + genes
    with open(outfilename, "w") as f:
        f.write('\t'.join(headers) + '\n')
        for case_data in case_aliquot_gcns:
            if case_data['genid'] is None:
                continue
            f.write('\t'.join([case_data['genid']] + case_data['gcns']) + '\n')
    print "Results file created in %s" % outfilename
    return outfilename
    
def loadHistoricalGCN(filename, reqTitle, reqDescription, username):
    genes, case_aliquot_gcns = parseTSV(filename)
    not_found = [k['case'] for k in case_aliquot_gcns if k['genid'] is None]
    if len(not_found):
        print "Warning: no DNA aliquot found for the following cases:\n", '\n'.join(sorted(not_found))
    setUpDatabaseEntries(case_aliquot_gcns, reqTitle, reqDescription, username)
    name = generateResultFile(filename, genes, case_aliquot_gcns)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Build reference graph')
    parser.add_argument('sourceFile', metavar='sourceFile', type=str, help='Case/mutation source file')
    parser.add_argument('username', metavar='username', type=str, help='Username making the request')
    parser.add_argument('reqTitle', metavar='reqTitle', type=str, help='Request title')
    parser.add_argument('reqDescription', metavar='reqDescription', type=str, nargs='?', help='Request description')
    args = parser.parse_args()
    loadHistoricalGCN(args.sourceFile, args.reqTitle, args.reqDescription, args.username)
