#from django.core.urlresolvers import reverse
#from django.http import HttpResponse, HttpResponseRedirect
#from django.shortcuts import render_to_response
#from django.template import loader, Context, RequestContext
from piston.handler import BaseHandler
from annotations.models import *
from django.db import models
from api.utils import *
from itertools import chain
from django.conf import settings
from django.db import transaction
#from django.contrib import auth

from py2neo import neo4j
import json
from subprocess import call
import tempfile
import os
import re


class GenesFromSymbol(BaseHandler):
    allowed_methods = ('GET')
    def read (self, request):
        try:
            geneSymbolList = request.GET.getlist('geneSymbol')
            exactMatch = request.GET['exactMatch']
            genes = {}
            if exactMatch.lower() in ['true', 'yes']:
                for geneSymbol in geneSymbolList:
                    gene_ids1 = Gene.objects.values_list('id_gene', flat=True).filter(gene_name=geneSymbol).only('id_gene')
                    gene_ids2 = GeneAlias.objects.values_list('id_gene', flat=True).filter(gene_synonym=geneSymbol).only('id_gene')
                    gene_ids = list(chain(gene_ids1, gene_ids2))
                    gene_objs = Gene.objects.filter(id_gene__in=gene_ids)
                    genes[geneSymbol] = gene_objs
            elif exactMatch.lower() in ['false', 'no']:
                for geneSymbol in geneSymbolList:
                    gene_ids1 = Gene.objects.values_list('id_gene', flat=True).filter(gene_name__icontains=geneSymbol).only('id_gene')
                    gene_ids2 = GeneAlias.objects.values_list('id_gene', flat=True).filter(gene_synonym__icontains=geneSymbol).only('id_gene')
                    gene_ids = list(chain(gene_ids1, gene_ids2))
                    gene_objs = Gene.objects.filter(id_gene__in=gene_ids)
                    genes[geneSymbol] = gene_objs
            else:
                raise Exception

            #gene_list = []
            #for o in gene_objs:
            #    gene_list.append(ClassSimple(o, ['id_gene', 'gene_name', 'chromosome', 'chrom_arm', 'chrom_band']).getAttributes())	
            #return gene_list
            return {k:[ClassSimple(o, ['id_gene', 'gene_name', 'chromosome', 'chrom_arm', 'chrom_band']).getAttributes() for o in v] for k,v in genes.iteritems()}
        except Exception,e:
            print e
            return 'Error: ' + str(e).replace('"','')

class MutationsFromGeneId(BaseHandler):
    allowed_methods = ('GET')
    def read (self, request):
        try:
            geneId = request.GET['geneId']
            transcripts = Transcript.objects.filter(id_gene=geneId).only('id_transcript')
            mut_objs = Mutation.objects.filter(id_transcript__in=transcripts).only('id_mutation', 'cds_mut_syntax', 'aa_mut_syntax')
            mut_list = []
            for o in mut_objs:
                mut_list.append(ClassSimple(o, ['id_mutation', 'cds_mut_syntax', 'aa_mut_syntax']).getAttributes())
            return mut_list
        except Exception,e:
            print e
            return 'Error'

class MutationFromCDSSyntax(BaseHandler):
    allowed_methods = ('GET')
    def read (self, request):
        try:
            geneSymbol = request.GET['geneSymbol']
            cdsMutSyntax = request.GET['cdsMutSyntax']

            gene_ids1 = Gene.objects.values_list('id_gene', flat=True).filter(gene_name=geneSymbol).only('id_gene')
            gene_ids2 = GeneAlias.objects.values_list('id_gene', flat=True).filter(gene_synonym=geneSymbol).only('id_gene')
            gene_ids = list(chain(gene_ids1, gene_ids2))
            
            transcripts = Transcript.objects.filter(id_gene__in=gene_ids).only('id_transcript')

            mut_objs = Mutation.objects.filter(id_transcript__in=transcripts,cds_mut_syntax=cdsMutSyntax).only('id_mutation')
            #mut_objs = Mutation.objects.only('id_mutation', 'cds_mut_syntax').filter(id_transcript__in=Transcript.objects.filter(id_gene__in=Gene.objects.filter(gene_name=geneSymbol)),cds_mut_syntax=cdsMutSyntax)
            mut_list = []
            for o in mut_objs:
                mut_list.append(ClassSimple(o, ['id_mutation']).getAttributes())
            return mut_list
        except Exception,e:
            print e
            return 'Error'

class CreateMutationAnnotation(BaseHandler):
    allowed_methods = ('POST')
    def create (self, request):
        try:
            genid = request.POST['genId']
            geneid = request.POST['geneId']
            genestatus = request.POST['geneStatus']
        except:
            return {'status': 'Error', 'description': 'Bad syntax'}
        
        try:
            g = Gene.objects.filter(pk=geneid).only('id_gene')
        except:
            return {'status': 'Error', 'description': 'Gene not found'}
        
        gdb = neo4j.GraphDatabaseService(settings.NEO4J_URL)
        t = gdb.get_indexed_node('node_auto_index','genid', genid)
        if t is None:
            return {'status': 'Error', 'description': 'GenealogyID not found'}
        
        n = {}
        
        if genestatus == 'mut':
            
            try:
                mutid = request.POST['mutId']
            except:
                return {'status': 'Error', 'description': 'Parameter \'mutId\' missing'}

            try:
                m = Mutation.objects.filter(pk=mutid).only('id_mutation', 'aa_mut_syntax')
                n['mutId'] = int(mutid)
                n['aaMutSyntax'] = m[0].aa_mut_syntax
            except Exception, e:
                return {'status': 'Error', 'description': 'Mutation not found' + str(e)}
            
            if m[0].id_transcript.id_gene.id_gene != int(geneid):
                return {'status': 'Error', 'description': 'Mutation %s does not belong to gene %s' % (mutid, geneid)}
            
            if 'alleleFreq' in request.POST and len(request.POST['alleleFreq']) > 0:
                try:
                    n['alleleFreq'] = float(request.POST['alleleFreq'])
                except:
                    return {'status': 'Error', 'description': 'Invalid value for parameter \'alleleFreq\''}
            if 'cdsInferred' in request.POST and len(request.POST['cdsInferred']) > 0:
                if request.POST['cdsInferred'].lower() in ['true', 'yes']:
                    n['cdsInferred'] = True
                elif request.POST['cdsInferred'].lower() not in ['false', 'no']:
                    return {'status': 'Error', 'description': 'Invalid value for parameter \'cdsInferred\''}
           
        elif genestatus not in ['wt', 'n/a']:
            return {'status': 'Error', 'description': 'Invalid value for parameter \'geneStatus\''}

        n['annotationType'] = 'mutation'
        n['geneId'] = int(geneid)
        n['geneStatus'] = genestatus

        to_insert = []
        to_insert.append(n)
        
        if 'aliquotInferred' in request.POST and len(request.POST['aliquotInferred']) > 0:
            if request.POST['aliquotInferred'].lower() in ['true', 'yes']:
                to_insert.append((0, 'annotates', t, {'aliquotInferred': True}))
            elif request.POST['aliquotInferred'].lower() not in ['false', 'no']:
                return {'status': 'Error', 'description': 'Invalid value for parameter \'aliquotInferred\''}
        else:
            to_insert.append((0, 'annotates', t))
        
        print to_insert

        try:
            gdb.create(*to_insert)
            return {'status': 'Ok'}
        except Exception, e:
            return {'status': 'Error', 'description': str(e)}
        
class TopFreqMutFromAASyntax(BaseHandler):
    allowed_methods = ('GET')
    def read (self, request):
        try:
            geneId = request.GET['geneId']
            aaMutSyntax = request.GET['aaMutSyntax']
        except:
            return {'status': 'Error', 'description': 'Bad syntax'}
        
        mut_list = []
        try:
            transcripts = Transcript.objects.filter(id_gene=geneId).only('id_transcript')
            mut = Mutation.objects.filter(id_transcript__in=transcripts,aa_mut_syntax=aaMutSyntax).order_by('-frequency_in_studies').only('id_mutation')[0]
            mut_list.append(ClassSimple(mut, ['id_mutation']).getAttributes())
        except:
            pass
        return mut_list

class GeneMutNamesFromId(BaseHandler):
    allowed_methods = ('GET')
    def read (self, request):
        try:
            gene_list = json.loads(request.GET['geneList'])
        except:
            gene_list = []
        try:
            mut_list = json.loads(request.GET['mutList'])
        except:
            mut_list = []
        
        if len(gene_list) == 0 and len(mut_list) == 0:
            return {'status': 'Error', 'description': 'Bad syntax'}
        
        ret = {}
            
        if len(gene_list) > 0:
            q = Gene.objects.filter(pk__in=gene_list).only('id_gene', 'gene_name')
            genes = {}
            for x in q:
                genes[x.id_gene] = x.gene_name
            ret['genes'] = genes
            
        if len(mut_list) > 0:
            q = Mutation.objects.filter(pk__in=mut_list).only('id_mutation', 'aa_mut_syntax', 'cds_mut_syntax')
            mutations = {}
            for x in q:
                mutations[x.id_mutation] = (x.aa_mut_syntax, x.cds_mut_syntax)
            ret['mutations'] = mutations
        
        return ret

'''        
class AlignTargetSequence(BaseHandler):
    allowed_methods = ('GET')
    def read (self, request):
        try:
            name = request.GET['name']
            sequence = request.GET['sequence']
        except:
            return {'status': 'Error', 'description': 'Bad syntax'}
        sequence = sequence.strip()
        
        in_f = tempfile.NamedTemporaryFile()
        in_f.delete = False
        in_f_name = in_f.name
        in_f.write(">" + name + "\n")
        in_f.write(sequence + "\n")
        in_f.close()
        
        out_f = tempfile.NamedTemporaryFile()
        out_f.delete = False
        out_f_name = out_f.name
        out_f.close()
        
        ret = call(["/home/alberto/Lavoro/Downloads/blat/build/gfClient", "-minScore="+str(len(sequence)), "-minIdentity=100", "localhost", "1515", "/home/alberto/Lavoro/Downloads/blat/seq/", in_f_name, out_f_name])
        
        out_f = open(out_f_name, "r")
        
        for i in xrange(0,5):
            out_f.readline()
        
        alignments = []
        for l in out_f:
            l = l.split()
            strand = l[8]
            tx = l[13]
            al_start = l[15]
            al_end = l[16]
            try:
                gene = Gene.objects.filter(chromosome=int(tx[3:]),ensembl_genome_start__lte=int(al_start), ensembl_genome_stop__gte=int(al_end))[0].gene_name
            except:
                gene = 'n/a'
            alignments.append((tx, al_start, al_end, strand, gene))
            
        out_f.close()
        
        os.remove(in_f_name)
        os.remove(out_f_name)
        
        return alignments
'''

class SnpFromName(BaseHandler):
    allowed_methods = ('GET')
    def read(self, request):
        try:
            snpName = request.GET['snpName']
            snp = Variation.objects.filter(name=snpName).values("variation_id", "name", "ancestral_allele", "minor_allele", "minor_allele_freq")

            return snp

        except Exception,e:
            
            print e
            return 'Error: ' + str(e).replace('"','')

class CellLineFromName(BaseHandler):
    allowed_methods = ('GET')
    max_results = 10
    print 'api cell'
    def read(self, request):
        try:
            print '1'
            import Levenshtein
            import re
            print '2'
            try:
                clname = request.GET['name'].lower()
                clname = re.sub('[^a-zA-Z0-9]', '', clname)
            except:
                return ['Error', 'Invalid syntax']
            print 'clname',clname
            cla = CellLineAlias.objects.filter(name__icontains=clname).order_by('cellLine')
            cla1 = list(cla)
            cla1.sort(key=lambda x: Levenshtein.distance(clname,x.name.lower()))
            cl = {}
            i = 0
            while len(cl) < self.max_results and i < len(cla1):
                if cla1[i].cellLine not in cl:
                    cl[cla1[i].cellLine] = [cla1[i].name]
                else:
                    cl[cla1[i].cellLine].append(cla1[i].name)
                i += 1

            return [{'id': k.id, 'name': k.name, 'match': v} for k,v in cl.items()]
            if len(cl) < self.max_results:
                clname = re.sub('[^a-zA-Z0-9]', '', clname)
                allcla = set(CellLineAlias.objects.all()).difference(set(cla))
                dist = {}
                for c in allcla:
                    d = Levenshtein.distance(clname, re.sub('[^a-zA-Z0-9]', '', c.name).lower())
                    if c.cellLine not in dist or dist[c.cellLine][0] > d:
                        dist[c.cellLine] = (d, c.name)
            
                return [{'id': k.id, 'name': k.name, 'match': v} for k,v in cl.items()] + [{'id': x.id, 'name': x.name, 'match': [dist[x][1]]} for x in sorted(dist, key=lambda k:dist[k][0])[:self.max_results-len(cl)]]
            else:
                return [{'id': k.id, 'name': k.name, 'match': v} for k,v in cl.items()]
        except Exception,e:
            print 'err',e

class NewCellLine(BaseHandler):
    allowed_methods = ('POST')
    def create(self, request):
        try:
            clname = request.POST['name']
        except:
            return ['Error', 'Invalid syntax']

        try:
            cl = CellLine()
            cl.name = clname
            cl.save()
        except:
            cl = CellLine.objects.get(name=clname)
            return {'id': cl.id, 'warning': 'already in database'}
        
        try:
            cla = CellLineAlias()
            cla.name = re.sub('[^a-zA-Z0-9]', '', clname.strip())
            cla.cellLine = cl
            cla.save()
        except Exception as e:
            return str(e)

        return {'id': cl.id}




