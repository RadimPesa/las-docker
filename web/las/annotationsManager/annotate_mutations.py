#!/usr/bin/python

# Set up the Django Enviroment
import sys
sys.path.append('/home/alberto/Lavoro/Annotations/')
from django.core.management import setup_environ 
from annotationsManager import settings
setup_environ(settings)

from annotations.models import Gene, Transcript, Mutation, GeneAlias

from itertools import chain
from py2neo import neo4j
import urllib, urllib2
import ast
from datetime import datetime

from annotations.genealogyID import GenealogyID

def annotateMutation(geneId, geneStatus, genID, mutId=None, alleleFreq=None, aaMutSyntax=None, cdsInferred=None, aliquotInferred=None):
    
    t = gdb.get_indexed_node('node_auto_index','genid', genID)

    if t is None:
        # se genid non trovato, prova a cercarlo con il 200 storico del topo
        m = int(GenealogyID(genID).getMouse()) + 200
        t = gdb.get_indexed_node('node_auto_index','genid', GenealogyID(genID).setMouse(m).getGenID())

    if t is not None:
        #controlla se esiste gia' la stessa annotazione
        #s = n.get_related_nodes(neo4j.Direction.INCOMING, 'annotates')
        #exists = False
        #for x in s:
        #    if 'mutID' in x.get_properties().keys() and x.get_properties()['mutID'] == mutid:
        #        exists = True
        #        break
        #if exists:
        #    print "Already annotated: " + str(mutid)
        #    return
            
        to_insert = []
        n = {}
        n['annotationType'] = 'mutation'
        n['geneId'] = geneId
        n['geneStatus'] = geneStatus
        if mutId:
            n['mutId'] = mutId
        if alleleFreq:
            n['alleleFreq'] = alleleFreq
        if aaMutSyntax:
            n['aaMutSyntax'] = aaMutSyntax
        if cdsInferred:
            n['cdsInferred'] = cdsInferred
        to_insert.append(n)
        if aliquotInferred == True:
            to_insert.append((0, 'annotates', t, {'aliquotInferred': True}))
        else:
            to_insert.append((0, 'annotates', t))
        gdb.create(*to_insert)
        print "OK (" + (str(mutid) if geneStatus=='mut' else geneStatus) + ")"
    else:
        print "Not found: " + genID


def getAnnotationTarget(vector, case, tissue):
    #print "getAnnotationtarget(%s, %s, %s)" % (vector, case, tissue)
    #se e' presente il tessuto usa quello
    if not tissue.strip():
    #altrimenti assumi liver met (LM)
        tissue = 'LM'
    
    if vector == 'H':
        ############ N.B. potrebbe non esserci la D01 ma un'altra!!!!!!
        q = 'start n=node:node_auto_index("genid:'+case+tissue+'H*") where n.genid =~ "' + case+tissue+'H' + '.{10}D.*" return n'
        data,metadata = neo4j.cypher.execute(gdb, q)
        
        if len(data):
            genid = str(chr(127))
            for x in data:
                if x[0]['genid'] < genid:
                    genid = x[0]['genid']
            return genid
        else:
            return None
        
        #return case.strip() + tissue.strip() + 'H0000000000D01000'
    
    elif vector == 'X':
        #se X, 1a aliquota di DNA del 1o espianto di passaggio 1
        #se X storico, X0{A,B}01001, segnalando che trattasi di inferenza
        q = 'start n=node:node_auto_index("genid:'+case+tissue+'X*") where n.genid =~ "' + case+tissue+'X' + '0.01.{6}D.*" return n'
        data,metadata = neo4j.cypher.execute(gdb, q)
        
        
        if len(data):
            mice_genid_list = []
            for x in data:
                mice_genid_list.append(GenealogyID(x[0]['genid']).zeroOutFieldsAfter('mouse').getGenID())
                mice_genid_list = list(set(mice_genid_list))
                
            #make a query for genealogy id of each mouse
            mouse_explant = []
            for x in mice_genid_list:
                #first, query the mice block to get mice id
                url = 'https://lasircc.polito.it/xeno/api.query.mice'
                vts = {'predecessor': 'Genealogy ID_', 'parameter': '', 'list': {'genID': [x]}, 'values': '', 'successor': u'Explants'}
                dt = urllib.urlencode(vts)
                try:
                    u = urllib2.urlopen(url, dt)
                except:
                    print "An error occurred while trying to retrieve data from "+str(url)   

                res=u.read()
                result=ast.literal_eval(res)
                
                #next, query the explant block to get explant details
                url = 'https://lasircc.polito.it/xeno/api.query.explants'
                vts = {'predecessor': u'Mice', 'parameter': u'', 'list': result, 'values': '', 'successor': u'End'}
                dt = urllib.urlencode(vts)
                try:
                    u = urllib2.urlopen(url, dt)
                except:
                    print "An error occurred while trying to retrieve data from "+str(url)   

                res=u.read()
                result=ast.literal_eval(res)
                    
                #store mouse (genid -> explant date) in a dictionary
                try:
                    mouse_explant.append ((x, datetime.strptime(result['objects'][0]['date'], '%Y-%m-%d')))
                except:
                    pass
                        
            if len(mouse_explant) > 0:
                # se l'espianto e' tracciato nel database, considera quello con data minima e seleziona il topo corrispondente
                mouse_explant.sort(key=lambda t: t[1])
                mouse_genid = mouse_explant[0][0]
                    
                genid = str(chr(127))
                # quindi, tra tutte le aliquote D derivate da quel topo, scegli quella di indice minimo
                for x in data:
                    if mouse_genid == GenealogyID(x[0]['genid']).zeroOutFieldsAfter('mouse').getGenID() and x[0]['genid'] < genid:
                        genid = x[0]['genid']
            
            else:
                # altrimenti, se l'espianto non e' tracciato nel database, seleziona direttamente l'aliquota con genid minimo
                genid = str(chr(127))
                
                for x in data:
                    if x[0]['genid'] < genid:
                        genid = x[0]['genid']
            
                            
            return genid
            
        else:
            return None

def getMutation(mut, gene):
    try:
        return Mutation.objects.filter(id_transcript__in=transcripts[gene],aa_mut_syntax="p."+mut).only('id_mutation').order_by('-frequency_in_studies').only('id_mutation')[0].id_mutation
    except:
        return None


f=open("/srv/www/annotationsManager/dtb_mutations.csv", "r")

fields = ['case', 'tissue', 'genid', 'KRAS', 'NRAS', 'BRAF', 'PIK3CA', 'KRAS', 'NRAS', 'BRAF', 'PIK3CA']
vector = ['', '', '', 'H', 'H', 'H', 'H', 'X', 'X', 'X', 'X']
gene_names = ['KRAS', 'NRAS', 'BRAF', 'PIK3CA']
transcripts = {}
genes = {}

for g in gene_names:
    gene_ids1 = Gene.objects.values_list('id_gene', flat=True).filter(gene_name=g).only('id_gene')
    #gene_ids2 = GeneAlias.objects.values_list('id_gene', flat=True).filter(gene_synonym=g).only('id_gene')
    #gene_ids = list(chain(gene_ids1, gene_ids2))
    gene_ids = gene_ids1
    if len(gene_ids) > 1:
        print "More than one gene found for %s !" % (g)
        genes[g] = None
    else:
        genes[g] = gene_ids[0]
    transcripts[g] = Transcript.objects.values_list('id_transcript', flat=True).filter(id_gene__in=gene_ids).only('id_transcript')
    if len(transcripts[g]) > 1:
        print "More than one transcript found for %s !" % (g)
        transcripts[g] = []
    

gdb = neo4j.GraphDatabaseService(settings.NEO4J_URL)
                
for l in f:
    m = l.strip().split(',')
    
    genid = {}
    
    g = m[2].strip()
    if g:
        genid[GenealogyID(g).getSampleVector()] = g
        inferred = False
    else:
        inferred = True
        for i in xrange(3,11):
            if m[i].strip() and m[i].strip() not in ('-', '?', 'wt ?', 'bad', 'bad seq', 'BAD SEQ'):
                genid[vector[i]] = getAnnotationTarget(vector[i], m[0], m[1])
                break
    
    for i in xrange(3,11):
        if m[i].strip() and m[i].strip() not in ('-', '?', 'wt ?', 'bad', 'bad seq', 'BAD SEQ'):
            if genid[vector[i]]:
                if m[i].strip() == 'wt':
                    print genid[vector[i]] + " " + vector[i] + " " + m[i]
                    annotateMutation(geneId=genes[fields[i]], geneStatus="wt", genID=genid[vector[i]], aliquotInferred=inferred)
                else:
                    mutid = getMutation(m[i], fields[i])
                    if mutid:
                        print genid[vector[i]] + " " + vector[i] + " " + m[i]
                        annotateMutation(geneId=genes[fields[i]], geneStatus="mut", genID=genid[vector[i]], mutId=mutid, aaMutSyntax="p."+m[i], cdsInferred=True, aliquotInferred=inferred)
                    else:
                        print "Mutation not found: %s %s" % (fields[i], m[i])
            else:
                print m[0] + " " + m[1] + " " + vector[i] + " : no aliquot found"
                break

f.close()
