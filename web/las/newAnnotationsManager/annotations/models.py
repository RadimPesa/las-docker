from django.db.models import *
try:
    from django.apps import apps
    get_model = apps.get_model
except:
    from django.db.models.loading import get_model

from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q

from annotations.funnel_models import *
from annotations.lib.graph_utils import *
from annotations.lib.genomic_models import *
from annotations.lib.exceptions import *
import annotations.lib.outliers as olib
import annotations.tasks as tasks

from bulk_update.manager import BulkUpdateManager

from array import array
import re
import csv
import vcf
import json
import warnings
import datetime
import numpy
import time
import os
import shutil
import hgvs.parser
hgvsparser = hgvs.parser.Parser()

type_map = {"list": {"python_types": [list], "equal": lambda x,y:set(x)==set(y)}, "scalar": {"python_types": [str, int, long, float, bool], "equal": lambda x,y: x==y}}

class TargetSequence(Model):
    name = CharField(max_length=128, db_column='NAME',unique=True)
    sequence = CharField(max_length=8192, db_column='SEQUENCE',blank=True,null=True)
    uuid = CharField(max_length=32,db_column='uuid')
    class Meta:
        db_table='TARGET_SEQUENCE'
    def getPrimerInstance(self):
        p = Primer()
        p.byUuid(self.uuid)
        return p
    @property
    def genes(self):
        p = self.getPrimerInstance()
        aligns = p.getAlignments()
        return ', '.join(sorted(list(set([a['gene_symbol'] for a in aligns if a['gene_symbol'] is not None]))))

class Chromosome(Model):
    name = CharField(max_length=255, db_column='name')
    chrom = CharField(max_length=10)
    size = IntegerField()
    class Meta:
        db_table = u'CHROMOSOME'

class TSACombination(Model):
    name = CharField(max_length=128, db_column='NAME')
    length = BigIntegerField(null=True, blank=True, db_column='LENGTH')
    uuid = CharField(max_length=32,db_column='uuid')
    class Meta:
        db_table='TSA_COMBINATION'

### Table that supports gene search
class GeneAlias(Model):
    synonym = CharField(max_length=64)
    graph_uuid = CharField(max_length=32,null=False,blank=False)
    class Meta:
        db_table = 'GeneAlias'

class AnnotationFeature(Model):
    name = CharField(max_length=64)
    class_name = CharField(max_length=64)
    allow_manual_insert = BooleanField()
    label_term = ForeignKey('LabelTerm',null=True,blank=True)
    class Meta:
        db_table = u'AnnotationFeature'

'''
class AnnotationFeature_Subtype(Model):
    name = CharField(max_length=64)
    label_term = ForeignKey('LabelTerm',null=True,blank=True)
    annotation_feature = ForeignKey('AnnotationFeature')
    class_subtype_name = CharField(max_length=64)
    class Meta:
        db_table = u'AnnotationFeature_Subtype'
'''

class Source(Model):
    name = CharField(max_length=64)
    url = CharField(max_length=256)
    class_name = CharField(max_length=64)
    class Meta:
        db_table = u'Source'

class AnnotationFeature_has_source(Model):
    annotation_feature = ForeignKey('AnnotationFeature')
    source = ForeignKey('Source')
    class Meta:
        db_table = u'AnnotationFeature_has_source'

class LabelTerm(Model):
    name = CharField(max_length=64)
    displayName = CharField(max_length=64)
    ontology = ForeignKey('Ontology',null=True,blank=True)
    ontology_term = CharField(max_length=64,null=True,blank=True)
    fatherLabel = ForeignKey('LabelTerm', null=True, blank=True)
    lastInsert = DateTimeField(null=True, blank=True)
    annotationModelName = CharField(max_length=256, blank=True, null=True)
    graphModelName = CharField(max_length=256, blank=True, null=True)
    class Meta:
        db_table = u'LabelTerm'
    def __unicode__(self):
        return self.name
    def updateLastInsert(self):
        now = timezone.now()
        self.lastInsert = now
        self.save()
        parent = self.fatherLabel
        while parent is not None:
            parent.lastInsert = now
            parent.save()
            parent = parent.fatherLabel

    def getAnnotationModel(self):
        modelName = self.annotationModelName
        parent = self.fatherLabel
        while modelName is None and parent is not None:
            modelName = parent.annotationModelName
            parent = parent.fatherLabel
        if modelName:
            return get_model('annotations', modelName)
        else:
            return None

    def getGraphModel(self):
        graphModelName = self.graphModelName
        parent = self.fatherLabel
        while graphModelName is None and parent is not None:
            graphModelName = parent.graphModelName
            parent = parent.fatherLabel
        if graphModelName:
            return getattr(annotations.lib.genomic_models, graphModelName)
        else:
            return None

class Ontology(Model):
    name = CharField(max_length=64)
    url = CharField(max_length=255)
    class Meta:
        db_table = u'Ontology'

class Annotation_GeneExpression_Manager(Manager):
    def aggregateForReport(self, records):
        def samplePrefix(genid):
            #return genid[:7]
            return genid

        samples = {}
        for x in records:
            sp = samplePrefix(x.id_sample)
            if sp not in samples:
                samples[sp] = {}
            if x.tx_accession not in samples[sp]:
                samples[sp][x.tx_accession] = []
            samples[sp][x.tx_accession].append(x)
       
        return samples

    def formatForReport(self, aggregates):
        print "aggregates", aggregates
        gg = GenomeGraphUtility()
        tx_acs = {}
        for tx_dict in aggregates.values():
            for t in tx_dict.keys():
                if t not in tx_acs:
                    try:
                        gene_info = gg.getTranscriptInfo(ac=t)[0]
                        tx_acs[t] = gene_info['gene.symbol']
                    except:
                        tx_acs[t] = "Unknown gene"

        headers = []
        row1 = ['']
        row2 = []
        row2.append('Sample')
        for tx_ac in sorted(tx_acs, key=lambda k: tx_acs[k]):
            gene_symbol = tx_acs[tx_ac]
            row1.append(gene_symbol)
            row2.append('(' + tx_ac + ')')
        headers.append(row1)
        headers.append(row2)

        data = []
        for sampleId, tx_dict in aggregates.iteritems():
            row = []
            row.append(sampleId)
            for tx_ac in sorted(tx_dict, key=lambda k: tx_acs[k]):
                annot_list = tx_dict[tx_ac]
                values = []
                for a in annot_list:
                    if a.expression_value is not None:
                        values.append(str(a.expression_value))
                row.append(" | ".join(values))
            data.append(row)
        return headers, data

    def runPostSaveHandlers(self, description=None, analysis_obj=None):
        pass

class Annotation_GeneExpression(Model):
    id_sample = CharField(max_length=26)
    id_experimental_data = CharField(max_length=32)
    id_analysis = ForeignKey('Analysis', db_column='id_analysis')
    ref_graph_uuid = CharField(max_length=32,null=True,blank=True)
    tx_accession = CharField(max_length=64,null=True,blank=True)
    expression_value = FloatField(null=True,blank=True)
    value_type = CharField(max_length=32,null=True,blank=True)
    annot_graph_uuid = CharField(max_length=32,null=True,blank=True,default=None)
    _ref_tx_accession = CharField(max_length=1024,null=True,blank=True,default=None,db_column='ref_tx_accession')
    analysis_output_id = CharField(max_length=32,null=True,blank=True)
    failed = BooleanField(default=False)
    conflict = BooleanField(default=False)
    conflict_info = CharField(max_length=2048,null=True,blank=True)

    @property
    def ref_tx_accession(self):
        return self._ref_tx_accession.split(',')

    @ref_tx_accession.setter
    def ref_tx_accession(self, value):
        self._ref_tx_accession = ",".join(value)

    objects = Annotation_GeneExpression_Manager()

    class Meta:
        db_table = 'Annotation_GeneExpression'

    @staticmethod
    def getFilteringParams(chrom, start, end, gene_uuid, gene_symbol):
        g = GenomeGraphUtility()
        all_tx_info = g.getTranscriptsForGene(gene_uuid)
        return {"tx_accession__in": [x[1] for x in all_tx_info]}

    def setAnnotationContent(self, *args):
        self.ref_graph_uuid = None # hack (mentre abbiamo ancora SA e SGV che usano ref_uuid)
        self.tx_accession = args[1] # partiamo da 1 a differenza di SA e SGV che in [1] hanno ref_uuid
        self.expression_value = args[5]
        self.ref_tx_accession = [x['ref'] for x in args[6]] # accession numbers
        self.value_type = args[7]
        self.analysis_output_id = args[8]
        self.failed = False

   # 0 -> sample_id, 1 -> test_tx_ac, 2 -> start, 3 -> end, 4 -> test_gene_symbol, 5 -> ref_genes_info, 6 -> output_id
    def setFailedContent(self, *args):
        self.ref_graph_uuid = None # hack (mentre abbiamo ancora SA e SGV che usano ref_uuid)
        self.tx_accession = args[1] # partiamo da 1 a differenza di SA e SGV che in [1] hanno ref_uuid
        self.expression_value = None
        self.ref_tx_accession = [x['ref'] for x in args[5]] # accession numbers
        self.value_type = None
        self.analysis_output_id = args[6]
        self.failed = True

class Annotation_SequenceAlteration_Manager(Manager):
    def aggregateForReport(self, records):
        def samplePrefix(genid):
            #return genid[:7]
            return genid

        g = GenomeGraphUtility()
        samples = {}
        for x in records:
            sp = samplePrefix(x.id_sample)
            if sp not in samples:
                samples[sp] = {}
            if not x.gene_symbol:
                res = g.getGenesInRegion(chrom=x.chrom,start=x.start,end=x.end)
                if len(res) > 0:
                    x.gene_symbol = res[0][1]
            if x.gene_symbol not in samples[sp]:
                samples[sp][x.gene_symbol] = []
            samples[sp][x.gene_symbol].append(x)
       
        return samples

    def formatForReport(self, aggregates):
        genes = {}
        for gene_dict in aggregates.values():
            for g, annot_list in gene_dict.iteritems():
                if g not in genes:
                    genes[g] = 0
                genes[g] = max(len(annot_list), genes[g])
        headers = []
        row1 = ['']
        row2 = []
        row2.append('Sample')
        for g, cnt in sorted(genes.iteritems()):
            for i in xrange(1, cnt+1):
                if not g:
                    g_name = 'M' + str(i)
                    row1.extend(['Extra-genic'] * 5)
                else:
                    g_name = g + ' M' + str(i)
                    row1.extend([g] * 5)
                row2.extend([g_name + ' HGVS.g', g_name + ' HGVS.c', g_name + ' HGVS.p', g_name + ' COSMIC', g_name + ' AF'])
        headers.append(row1)
        headers.append(row2)
        data = []
        for sampleId, gene_dict in aggregates.iteritems():
            row = []
            row.append(sampleId)
            for g in sorted(genes):
                gene_muts = []
                annot_list = gene_dict.get(g, [])
                for a in annot_list:
                    sa_obj = a.getSequenceAlterationObj()
                    gene_muts.extend([sa_obj.getHGVS_g(), sa_obj.getHGVS_c(), sa_obj.getHGVS_p_1L(), " ".join([c.cosmic_id for c in sa_obj.getCosmicEntry()]), a.allele_frequency])
                for i in xrange(len(annot_list), genes[g]):
                    gene_muts.extend([''] * 5)
                row.extend(gene_muts)
            data.append(row)
        return headers, data

    def autoAnnotate(self, refObj=None, willExist=None):
        if refObj is not None: # run autoAnnotate for a specific sequence alteration (added/removed)
            if willExist: # sa exists from now on (and it didn't before): create annotations
                print "update1"
                info = refObj.getExtendedInfo()[0]
                for a in Annotation_SequenceAlteration.objects.filter(chrom=info['chrom'], start=info['start'], end=info['end'], num_bases=info['num_bases'], sa_type=info['type'], ref=info['ref'], alt=info['alt'], gene_symbol=info['gene_symbol']):
                    print a.id
                    a.copyToGraph()
            else: # sa will no longer exist (it will be deleted): delete annotations
                print "update2"
                uuid = refObj.getUUID()
                for a in Annotation_SequenceAlteration.objects.filter(ref_graph_uuid=uuid):
                    a.removeFromGraph()
        else: # run autoAnnotate to check and update all annotations (can take a long time)
        # N.B. annotations whose reference exists will be created, but the opposite cannot happen (if a reference doesn't exist, neither can annotations that refer to it)
            print "update3"
            for a in Annotation_SequenceAlteration.objects.filter(annot_graph_uuid=None):
                try:
                    a.autoAnnotate()
                except Exception as e:
                    print e

    def runPostSaveHandlers(self, description=None, analysis_obj=None):
        pass

class Annotation_SequenceAlteration(Model):
    id_sample = CharField(max_length=26)
    id_experimental_data = CharField(max_length=32)
    id_analysis = ForeignKey('Analysis',db_column='id_analysis')
    ref_graph_uuid = CharField(max_length=32,null=True,blank=True)
    allele_frequency = FloatField(null=True,blank=True)
    chrom = CharField(max_length=2, null=True, blank=True)
    start = IntegerField(null=True, blank=True)
    end = IntegerField(null=True, blank=True)
    strand = CharField(max_length=1, null=True, blank=True)
    num_bases = IntegerField(null=True, blank=True)
    sa_type = CharField(max_length=32, null=True, blank=True)
    ref = CharField(max_length=128, null=True, blank=True)
    alt = CharField(max_length=1024, null=True, blank=True)
    gene_symbol = CharField(max_length=64,null=True,blank=True)
    annot_graph_uuid = CharField(max_length=32,null=True,blank=True,default=None)
    failed = BooleanField(default=False)
    conflict = BooleanField(default=False)
    conflict_info = CharField(max_length=2048,null=True,blank=True)

    objects = Annotation_SequenceAlteration_Manager()

    class Meta:
        db_table = 'Annotation_SequenceAlteration'
   
    @staticmethod
    def getFilteringParams(chrom, start, end, gene_uuid, gene_symbol):
        return {'chrom': chrom, 'start__gte': start, 'end__lte': end}

    def setAnnotationContent(self, *args):
        # args[ ... ] -> ...
        # 0 -> genid, 1 -> chrom, 2 -> start, 3 -> end, 4 -> strand, 5 -> ref, 6 -> alt, 7 -> num_bases, 8 -> type, 9 -> gene_symbol, 10 -> val
        self.chrom = args[1]
        self.start = args[2]
        self.end = args[3]
        self.strand = args[4]
        self.ref = args[5] if args[5] != 'None' else None
        self.alt = args[6] if args[6] != 'None' else None
        self.num_bases = args[7] if args[7] != 'None' else None
        self.sa_type = args[8]
        self.gene_symbol = args[9]
        self.allele_frequency = float(args[10])
        self.failed = False

    def setFailedContent(self, *args):
        # args[ ... ] -> ...
        # 0 -> genid, 1 -> ref (chrom), 2 -> start, 3 -> end
        self.chrom = args[1].replace('chr', '')
        self.start = args[2]
        self.end = args[3]
        self.strand = None
        self.ref = None
        self.alt = None
        self.num_bases = None
        self.sa_type = None
        self.gene_symbol = None
        self.allele_frequency = None
        self.failed = True

    def save(self, *args, **kwargs):
        skipAnnotate = kwargs.get('skipAnnotate', False)
        try:
            del kwargs['skipAnnotate']
        except:
            pass
        if self.end is None:
            self.end = SequenceAlteration.getEndCoordinate(self.start, self.ref, self.num_bases)
        #if self.ref_graph_uuid is None:
        #    x = self.getSequenceAlterationObj()
        #    u = x.getUUID()
        #    if u:
        #        self.ref_graph_uuid = u
        super(Annotation_SequenceAlteration, self).save(*args, **kwargs)
        if not skipAnnotate:
            self.autoAnnotate()

    def getSequenceAlterationObj(self):
        data = {'chrom': self.chrom, 'start': self.start, 'num_bases': self.num_bases, 'type': self.sa_type, 'ref': self.ref, 'alt': self.alt}
        if self.gene_symbol:
            data['gene_symbol'] = self.gene_symbol
        sa = SequenceAlteration()
        sa.set(**data)
        sa.exists()
        return sa

    def copyToGraph(self):
        if self.annot_graph_uuid is not None:
            warnings.warn("Already in graph", RuntimeWarning)
            return
        # create reference node on graph
        data = {'chrom': self.chrom, 'start': self.start, 'num_bases': self.num_bases, 'type': self.sa_type, 'ref': self.ref, 'alt': self.alt, 'gene_symbol': self.gene_symbol}
        sa = SequenceAlteration()
        sa.set(**data)
        if sa.isWildType():
            return
        if not sa.exists():
            sa.save()
            l = sa.getCosmicEntry()
            u = sa.getUUID()
            for x in l:
                x.las_graph_id = u
                x.save()
        else:
            u = sa.getUUID()
        # create annotation
        ggu = GenomeGraphUtility()
        self.annot_graph_uuid = ggu.annotateNode(src_genid=self.id_sample,ref_uuid=u,analysis_uuid=self.id_analysis.graph_uuid,db_model=self._meta.object_name,db_id=self.id,data={"allele_frequency": self.allele_frequency})
        # update reference if necessary
        if self.ref_graph_uuid != u:
            self.ref_graph_uuid = u
        super(Annotation_SequenceAlteration, self).save()

    def removeFromGraph(self):
        if self.annot_graph_uuid is None:
            warnings.warn("Not in graph", RuntimeWarning)
            return
        # delete annotation
        ggu = GenomeGraphUtility()
        ggu.deleteAnnotation(self.annot_graph_uuid)
        # clear annot_graph_uuid
        self.ref_graph_uuid = None
        self.annot_graph_uuid = None
        super(Annotation_SequenceAlteration, self).save()

    def getDataForExport(self):
        return {
            'id': self.id,
            'id_sample': self.id_sample,
        }

    def autoAnnotate(self):
        saObj = self.getSequenceAlterationObj()
        # auto annotate if reference exists or is in Cosmic
        if saObj.exists():
            print "[Annotation_SequenceAlteration (id=%d)] auto-annotate: yes (in refgraph)" % self.id
            self.copyToGraph()
        #elif len(saObj.getCosmicEntry()) > 0:
        #    print "[Annotation_SequenceAlteration (id=%d)] auto-annotate: yes (in Cosmic)" % self.id
        #    self.copyToGraph()
        else:
            print "[Annotation_SequenceAlteration (id=%d)] auto-annotate: skip" % self.id

    def runPostSaveHandlers(self, description=None, analysis_obj=None):
        # put here code that must be MANUALLY run after saving one or MORE objects
        # (called by api.newapi.submitResults)
        pass

class Annotation_ShortGeneticVariation_Manager(Manager):
    def aggregateForReport(self, records):
        def samplePrefix(genid):
            #return genid[:7]
            return genid

        samples = {}
        for x in records:
            sp = samplePrefix(x.id_sample)
            if sp not in samples:
                samples[sp] = {}
            if x.sgv_name not in samples[sp]:
                samples[sp][x.sgv_name] = []
            samples[sp][x.sgv_name].append(x)
       
        return samples

    def formatForReport(self, aggregates):
        snps = set()
        for snp_dict in aggregates.values():
            snps = snps.union(snp_dict.keys())
               
        headers = []
        row1 = ['']
        row2 = []
        row2.append('Sample')
        for s in sorted(snps):
            row1.extend([s] * 3)
            row2.extend([s + ' all.', s + ' alt.', s + ' AF'])
        headers.append(row1)
        headers.append(row2)

        data = []
        for sampleId, snp_dict in aggregates.iteritems():
            row = []
            row.append(sampleId)
            for s in sorted(snps):
                annot_list = snp_dict.get(s, [])
                snp_alleles = []
                snp_alts = []
                snp_afs = []
                for a in sorted(annot_list,key=lambda x:x.allele):
                    snp_alleles.append(a.allele)
                    snp_alts.append(a.alt)
                    snp_afs.append(str(a.allele_frequency))
                row.extend(["/".join(snp_alleles), "/".join(snp_alts), "/".join(snp_afs)])
            data.append(row)
        return headers, data

    def generateExpDataReport(self, filename, params={}):
        if params != {}:
            if params['plates'] != []:
                print "has plate"
                Q_predicates = [Q(plate_id=p) for p in params['plates']]
                plates_Q = reduce(lambda a,b: a | b, Q_predicates, Q())
            else:
                plates_Q = Q()


            if params['samples'] != []:
                Q_predicates = [Q(id_sample__regex=s) for s in [x.replace('-', '.') for x in params['samples']]]
                samples_Q = reduce(lambda a,b: a | b, Q_predicates, Q())
            else:
                samples_Q = Q()

            dates_ops = {'=': '', '<': '__lte', '>': '__gte'}
            if params['dates'] != []:
                Q_predicates = [Q(**{'id_analysis__creationDate' + dates_ops[d['date1'][0]]: d['date1'][1:]}) & (Q(**{'id_analysis__creationDate' + dates_ops[d['date2'][0]]: d['date2'][1:]}) if d['date2'] != '' else Q()) for d in params['dates']]
                dates_Q = reduce(lambda a,b: a | b, Q_predicates, Q())
            else:
                dates_Q = Q()

            if params['snps'] != []:
                Q_predicates = [Q(sgv_name=s) for s in params['snps']]
                snps_Q = reduce(lambda a,b: a | b, Q_predicates, Q())
            else:
                snps_Q = Q()

            params_Q = plates_Q & samples_Q & dates_Q & snps_Q
        else:
            params_Q = Q()

        data = Annotation_ShortGeneticVariation.objects.filter(params_Q).order_by('id_analysis__id', 'id_sample', 'sgv_name')
        analysis_titles = {a.id:a.name for a in Analysis.objects.all()}
        analysis_dates = {a.id:str(a.creationDate) for a in Analysis.objects.all()}
        genotype = ['A', 'T', 'C', 'G']
        genotype_map = {v:i for i,v in enumerate(genotype)}
        headers = ['Analysis title', 'Analysis date', 'Plate', 'Sample ID', 'SNP'] + genotype
        with open(filename, "w") as f:
            f.write("\t".join(headers) + "\n")
            if len(data) > 0:
                previous = [data[0].id_analysis_id, data[0].id_analysis_id, data[0].plate_id, data[0].id_sample, data[0].sgv_name]
                freqs = [''] * len(genotype)
                for d in data:
                    fields = [d.id_analysis_id, d.id_analysis_id, d.plate_id, d.id_sample, d.sgv_name]
                    if previous != fields and previous != [None, None, None, None, None]:
                        # current record does not refer to same analysis, sample or rs as previous one
                        previous[0] = analysis_titles[previous[0]]
                        previous[1] = analysis_dates[previous[1]]
                        f.write("\t".join(previous + freqs) + "\n")
                        previous = fields
                        freqs = [''] * len(genotype)
                    if d.failed:
                        fields[0] = analysis_titles[fields[0]]
                        fields[1] = analysis_dates[fields[1]]
                        freqs = ['bs'] * len(genotype)
                        f.write("\t".join(fields + freqs) + "\n")
                        previous = [None, None, None, None, None]
                        freqs = [''] * len(genotype)
                    else:
                        freqs[genotype_map[d.alt]] = str(d.allele_frequency)
                        previous = fields
                if not d.failed:
                    previous[0] = analysis_titles[previous[0]]
                    previous[1] = analysis_dates[previous[1]]
                    f.write("\t".join(previous + freqs) + "\n")

    def autoAnnotate(self, refObj=None, willExist=None):
        if refObj is not None: # run autoAnnotate for a specific sgv (added/removed)
            if willExist: # sgv exists from now on (and it didn't before): create annotations
                print "update1"
                info = refObj.getInfo()
                for a in Annotation_ShortGeneticVariation.objects.filter(sgv_name=info['name'], allele=info['allele']):
                    print a.id
                    a.copyToGraph()
            else: # sgv will no longer exist (it will be deleted): delete annotations
                print "update2"
                uuid = refObj.getUUID()
                for a in Annotation_ShortGeneticVariation.objects.filter(ref_graph_uuid=uuid):
                    a.removeFromGraph()
        else: # run autoAnnotate to check and update all annotations (can take a long time)
        # N.B. annotations whose reference exists will be created, but the opposite cannot happen (if a reference doesn't exist, neither can annotations that refer to it)
            print "update3"
            for a in Annotation_ShortGeneticVariation.objects.filter(annot_graph_uuid=None):
                try:
                    a.autoAnnotate()
                except Exception as e:
                    print "[Annotation_ShortGeneticVariation (id=%d)] auto-annotate: Exception: %s" % (a.id, str(e))

    def runPostSaveHandlers(self, description=None, analysis_obj=None):
        # put here code that must be MANUALLY run after saving one or MORE objects
        # (called by api.newapi.submitResults)
        # e.g. after saving all records related to a given analysis
        report = FingerPrintingReport()
        report.initialize(user=None, description=description, analysis_obj=analysis_obj)
        tasks.runFingerPrinting.delay(report, False)

class Annotation_ShortGeneticVariation(Model):
    id_sample = CharField(max_length=26)
    id_experimental_data = CharField(max_length=32)
    id_analysis = ForeignKey('Analysis',db_column='id_analysis')
    ref_graph_uuid = CharField(max_length=32,null=True,blank=True)
    chrom = CharField(max_length=2)
    start = IntegerField()
    end = IntegerField()
    strand = CharField(max_length=1, null=True, blank=True)
    alt = CharField(max_length=128, null=True, blank=True)
    num_repeats = IntegerField(null=True,blank=True)
    sgv_type = CharField(max_length=32, null=True, blank=True)
    sgv_name = CharField(max_length=32, null=True, blank=True)
    allele = CharField(max_length=1, null=True, blank=True)
    allele_frequency = FloatField(null=True,blank=True)
    annot_graph_uuid = CharField(max_length=32,null=True,blank=True,default=None)
    failed = BooleanField(default=False)
    plate_id = CharField(max_length=32,blank=True,null=True,default=None)
    well_id = CharField(max_length=10,blank=True,null=True,default=None)
    conflict = BooleanField(default=False)
    conflict_info = CharField(max_length=2048,null=True,blank=True)

    objects = Annotation_ShortGeneticVariation_Manager()

    class Meta:
        db_table = 'Annotation_SGV'
   
    @staticmethod
    def getFilteringParams(chrom, start, end, gene_uuid, gene_symbol):
        return {'chrom': chrom, 'start__gte': start, 'end__lte': end}

    def setAnnotationContent(self, *args):
        # args[0] -> allele frequency
        self.chrom = args[1]
        self.start = args[2]
        self.end = args[3]
        self.strand = args[4]
        self.alt = args[5] if args[5] != 'None' else None
        self.num_repeats = int(args[6]) if args[6] != 'None' else None
        self.sgv_type = args[7]
        self.sgv_name = args[8]
        try:
            allele = str(args[9])
            if str.isalpha(allele):
                self.allele = allele
        except:
            pass
        self.allele_frequency = float(args[10])
        self.failed = False
        self.plate_id = args[11] if args[11] != 'None' else None
        self.well_id = args[12] if args[12] != 'None' else None

    def setFailedContent(self, *args):
        # 0 -> s, 1 -> chrom, 2 -> start, 3 -> end, 4 -> name (rs...)
        self.chrom = args[1].replace('chr', '')
        self.start = args[2]
        self.end = args[3]
        self.strand = None
        self.alt = None
        self.num_repeats = None
        self.sgv_type = None
        self.sgv_name = args[4]
        self.allele = None
        self.allele_frequency = None
        self.failed = True
        self.plate_id = args[5] if args[5] != 'None' else None
        self.well_id = args[6] if args[6] != 'None' else None

    def getSGVObj(self):
        sgv = ShortGeneticVariation()
        if self.sgv_name and self.allele:
            #sgv.set(name=self.sgv_name,allele=self.allele)
            sgv.set(name=self.sgv_name,chrom=self.chrom,start=self.start,end=self.end,var_type=self.sgv_type,allele=self.allele,dbSnpLookup=False,ref='',alt=self.alt,strand=self.strand,num_repeats=self.num_repeats)
            return sgv
        else:
            print self.id
            return None

    def copyToGraph(self):
        if self.annot_graph_uuid is not None:
            warnings.warn("Already in graph", RuntimeWarning)
            return
        # create reference node on graph
        sgv = ShortGeneticVariation()
        if self.failed:
            warnings.warn("Skipping failed record", RuntimeWarning)
            return
        if self.sgv_name is None or self.allele is None:
            raise Exception("Insufficient information to instantiate SGV object")
        #sgv.set(name=self.sgv_name,allele=self.allele)
        sgv.set(name=self.sgv_name,chrom=self.chrom,start=self.start,end=self.end,var_type=self.sgv_type,allele=self.allele,dbSnpLookup=False,ref='',alt=self.alt,strand=self.strand)
        if not sgv.exists():
            sgv.save()
        ref_uuid = sgv.getUUID()
        # create annotation
        ggu = GenomeGraphUtility()
        self.annot_graph_uuid = ggu.annotateNode(src_genid=self.id_sample,ref_uuid=ref_uuid,analysis_uuid=self.id_analysis.graph_uuid,db_model=self._meta.object_name,db_id=self.id)
        # update reference if necessary
        if self.ref_graph_uuid != ref_uuid:
            self.ref_graph_uuid = ref_uuid
        super(Annotation_ShortGeneticVariation, self).save()

    def removeFromGraph(self):
        if self.annot_graph_uuid is None:
            warnings.warn("Not in graph", RuntimeWarning)
            return
        # delete annotation
        ggu = GenomeGraphUtility()
        ggu.deleteAnnotation(self.annot_graph_uuid)
        # clear annot_graph_uuid
        self.ref_graph_uuid = None
        self.annot_graph_uuid = None
        super(Annotation_ShortGeneticVariation, self).save()

    def autoAnnotate(self):
        if self.failed == True:
            print "[Annotation_ShortGeneticVariation (id=%d)] auto-annotate: skip (failed)" % self.id
            return
        sgvObj = self.getSGVObj()
        # auto annotate if reference exists
        if sgvObj.exists():
            print "[Annotation_ShortGeneticVariation (id=%d)] auto-annotate: yes (in refgraph)" % self.id
            self.copyToGraph()
        else:
            print "[Annotation_ShortGeneticVariation (id=%d)] auto-annotate: skip" % self.id

    def save(self, *args, **kwargs):
        super(Annotation_ShortGeneticVariation, self).save(*args, **kwargs)
        self.autoAnnotate()

class Annotation_CopyNumberVariation_Manager(Manager):
    def aggregateForReport(self, records):
        def samplePrefix(genid):
            #return genid[:7]
            return genid

        samples = {}
        for x in records:
            sp = samplePrefix(x.id_sample)
            if sp not in samples:
                samples[sp] = {}
            if not x.gene_symbol:
                x.gene_symbol = 'chr' + x.chrom + ':' + str(x.start) + '-' + str(x.end)
            if x.gene_symbol not in samples[sp]:
                samples[sp][x.gene_symbol] = []
            samples[sp][x.gene_symbol].append(x)
       
        return samples

    def formatForReport(self, aggregates):
        genes = {}
        for gene_dict in aggregates.values():
            for g, annot_list in gene_dict.iteritems():
                if g not in genes:
                    genes[g] = 0
                genes[g] = max(len(annot_list), genes[g])
        headers = []
        row1 = ['']
        row2 = []
        row2.append('Sample')
        for g, cnt in sorted(genes.iteritems()):
            for i in xrange(1, cnt+1):
                if not g:
                    g_name = 'M' + str(i)
                    row1.append('Extra-genic')
                else:
                    g_name = g + ' M' + str(i)
                    row1.append(g)
                row2.append(g_name + ' CN')
        headers.append(row1)
        headers.append(row2)

        data = []
        for sampleId, gene_dict in aggregates.iteritems():
            row = []
            row.append(sampleId)
            for g in sorted(genes):
                gene_muts = []
                annot_list = gene_dict.get(g, [])
                for a in annot_list:
                    gene_muts.append(a.copy_number)
                for i in xrange(len(annot_list), genes[g]):
                    gene_muts.append('')
                row.extend(gene_muts)
            data.append(row)
        return headers, data

    def runPostSaveHandlers(self, description=None, analysis_obj=None):
        # put here code that must be MANUALLY run after saving one or MORE objects
        # (called by api.newapi.submitResults)
        pass

    def autoAnnotate(self, refObj=None, willExist=None):
        if refObj is not None: # run autoAnnotate for a specific cnv (added/removed)
            if willExist: # cnv will exist from now on (and it didn't before): create annotations
                print "update1"
                info = refObj.getInfo()
                for a in Annotation_CopyNumberVariation.objects.filter(args=values):
                    print a.id
                    a.copyToGraph()
            else: # cnv will no longer exist (it will be deleted): delete annotations
                print "update2"
                uuid = refObj.getUUID()
                for a in Annotation_CopyNumberVariation.objects.filter(ref_graph_uuid=uuid):
                    a.removeFromGraph()
        else: # run autoAnnotate to check and update all annotations (can take a long time)
        # N.B. annotations whose reference exists will be created, but the opposite cannot happen (if a reference doesn't exist, neither can annotations that refer to it)
            print "update3"
            for a in Annotation_CopyNumberVariation.objects.filter(annot_graph_uuid=None):
                a.autoAnnotate()

class Annotation_CopyNumberVariation(Model):
    id_sample = CharField(max_length=26)
    id_experimental_data = CharField(max_length=32)
    id_analysis = ForeignKey('Analysis',db_column='id_analysis')
    ref_graph_uuid = CharField(max_length=32,null=True,blank=True)
    chrom = CharField(max_length=3,null=True,blank=True)
    start = IntegerField(null=True,blank=True)
    end = IntegerField(null=True,blank=True)
    gene_symbol = CharField(max_length=64,null=True,blank=True)
    copy_number = FloatField(null=True,blank=True)
    value_type = CharField(max_length=32,null=True,blank=True)
    annot_graph_uuid = CharField(max_length=32,null=True,blank=True,default=None)
    _ref_gene_symbol = CharField(max_length=1024,null=True,blank=True,default=None,db_column='ref_gene_symbol')
    analysis_output_id = CharField(max_length=32,null=True,blank=True)
    failed = BooleanField(default=False)
    conflict = BooleanField(default=False)
    conflict_info = CharField(max_length=2048,null=True,blank=True)

    @property
    def ref_gene_symbol(self):
        return self._ref_gene_symbol.split(',')

    @ref_gene_symbol.setter
    def ref_gene_symbol(self, value):
        self._ref_gene_symbol = ",".join(value)

    objects = Annotation_CopyNumberVariation_Manager()

    class Meta:
        db_table = 'Annotation_CopyNumber'

    @staticmethod
    def getFilteringParams(chrom, start, end, gene_uuid, gene_symbol):
        return {'chrom': chrom, 'start__gte': start, 'end__lte': end}

    def setAnnotationContent(self, *args):
        self.ref_graph_uuid = None # hack (mentre abbiamo ancora SA e SGV che usano ref_uuid)
        self.chrom = args[1].replace('chr', '') # partiamo da 1 a differenza di SA e SGV che in [1] hanno ref_uuid
        self.start = args[2]
        self.end = args[3]
        self.gene_symbol = ",".join(args[4]) if args[4] != 'None' else None
        self.copy_number = args[5]
        self.ref_gene_symbol = [",".join(x['gene_symbol']) for x in args[6]] # gene_symbols
        self.value_type = args[7]
        self.analysis_output_id = args[8]
        self.failed = False

    def setFailedContent(self, *args):
        # 0 -> sample_id, 1 -> test_gene_chrom, 2 -> start, 3 -> end, 4 -> test_gene_symbol, 5 -> ref_genes_info, 6 -> output_id
        self.ref_graph_uuid = None # hack (mentre abbiamo ancora SA e SGV che usano ref_uuid)
        self.chrom = args[1].replace('chr', '')
        self.start = args[2]
        self.end = args[3]
        self.gene_symbol = ",".join(args[4]) if args[4] != 'None' else None
        self.copy_number = None
        self.ref_gene_symbol = [",".join(x['gene_symbol']) for x in args[5]] # gene_symbols
        self.value_type = None
        self.analysis_output_id = args[6]
        self.failed = True

    def copyToGraph(self):
        if self.annot_graph_uuid is not None:
            print "Already in graph"
            return
        if ((self.chrom is None or self.start is None or self.end is None) and self.gene_symbol is None) or self.copy_number is None:
            raise Exception("Annotation_CopyNumberVariation: required information is missing, cannot copy to graph")
       
        ggu = GenomeGraphUtility()
        gene_info = ggu.getGeneInfo(symbol=self.gene_symbol)
        try:
            gene_uuid = gene_info[0].uuid
        except:
            raise Exception("Gene symbol not found: %s" % self.gene_symbol)

        # get annotation in graph (if any)
        result = ggu.checkGeneAnnotation(src_genid=self.id_sample,gene_uuid=gene_uuid,ref_type_label=CopyNumberVariation.getGraphLabel())
        # get relevant records from database (also including the current one) (excluding failed records)
        records = Annotation_CopyNumberVariation.objects.filter(id_sample=self.id_sample,gene_symbol=self.gene_symbol,failed=False)

        if len(result) == 0:
            # no annotation exists for this sample & this gene
            # => there can't be any valid record in the database either (because: if there were 1 or 2, they would have been annotated - no conflicts possible; if there were more than 2, at least 2 would have been annotated. Hence, there can't be any record.)
            # => create an annotation
            # (the label will be assigned based on the current record's GCN value)
            cnv = CopyNumberVariation()
            cnv.set(geneSymbol=self.gene_symbol, chrom=self.chrom, start=self.start, end=self.end, cn=self.copy_number)
            if not cnv.exists():
                print "Saving reference"
                cnv.save()
            u = cnv.getUUID()
            self.annot_graph_uuid = ggu.annotateNode(src_genid=self.id_sample,ref_uuid=u,analysis_uuid=self.id_analysis.graph_uuid,db_model=self._meta.object_name,db_id=self.id,data={"copy_number": self.copy_number})
            self.ref_graph_uuid = u
            self.save()

        elif len(result) == 1:
            # an annotation exists for this sample & this gene
            # store current annotation's reference uuid
            old_ref_uuid = result[0][1]
            
            # classify all records using classifier from outliers library (imported as olib)
            data = [x.copy_number for x in records]
            outliers = olib.test_outliers(data)
            db_ids = []
            skip_current = False
            for o, r in zip(outliers, records):
                if o == True:
                    r.conflict = True
                    r.annot_graph_uuid = None
                    r.ref_graph_uuid = None
                    if r == self:
                        skip_current = True
                else:
                    r.conflict = False
                    db_ids.append(r.id)
                r.save()
            
            if skip_current == False:
                self.annot_graph_uuid = result[0][0]
                aggr_copy_number = self.aggregateCopyNumber(db_ids)
                cnv = CopyNumberVariation()
                cnv.set(geneSymbol=self.gene_symbol, chrom=self.chrom, start=self.start, end=self.end, cn=aggr_copy_number)
                if not cnv.exists():
                    print "Saving reference"
                    cnv.save()
                u = cnv.getUUID()
                self.ref_graph_uuid = u

                if u != old_ref_uuid:
                    # if reference has changed, update the annotation by also updating the reference
                    ggu.updateAnnotationContent(uuid=self.annot_graph_uuid, db_id=db_ids, data={"copy_number": aggr_copy_number}, ref_uuid=u)
                    
                    # not deleting anymore!!!
                    ## delete stale reference (will not be deleted if still in use by other annotations)
                    #cnv_old = CopyNumberVariation()
                    #cnv_old.byUuid(old_ref_uuid)
                    #try:
                    #    cnv_old.delete()
                    #except Exception as e:
                    #    print e
                    # update reference for each record except the current one
                    for r in Annotation_CopyNumberVariation.objects.filter(pk__in=db_ids_others):
                        r.ref_graph_uuid = u
                        r.save()
                else:
                    # annotation reference has not changed, so we only need to update the annotation content
                    ggu.updateAnnotationContent(uuid=self.annot_graph_uuid, db_id=db_ids, data={"copy_number": aggr_copy_number})
           
            # if we reach this point, everything has gone fine, so save current record
            self.save()
           
        else:
            # this should never occur and indicates a corrupted/incoherent graph
            raise Exception("Error in annotation graph: multiple annotations found!")

    def removeFromGraph(self):
        if self.annot_graph_uuid is None:
            warnings.warn("Not in graph", RuntimeWarning)
            return
        # retrieve annotation node from graph
        ggu = GenomeGraphUtility()
        annot = ggu.getAnnotation_byUuid(self.annot_graph_uuid)
        if len(annot.db_id) == 1:
            # current record is the only one generating the graph annotation
            # simply delete the annotation node
            ggu.deleteAnnotation(self.annot_graph_uuid)
            
        else:
            # there is at least one other record, so the annotation node shall not be deleted
            # copy number must be recomputed from remaining records; new copy number may also result in a different label being assigned to it
            db_ids = annot.db_id
            db_ids_others = [x for x in db_ids if x != self.id]
            old_ref_uuid = annot.ref_uuid
            new_aggr_copy_number = self.aggregateCopyNumber(db_ids_others)
            cnv = CopyNumberVariation()
            cnv.set(geneSymbol=self.gene_symbol, chrom=self.chrom, start=self.start, end=self.end, cn=new_aggr_copy_number)
            if not cnv.exists():
                print "Saving reference"
                cnv.save()
            u = cnv.getUUID()
            if u != old_ref_uuid:
                # if reference has changed, update the annotation by also updating the reference
                ggu.updateAnnotationContent(uuid=self.annot_graph_uuid, db_id=db_ids_others, data={"copy_number": new_aggr_copy_number}, ref_uuid=u)
                # also update reference for each record except the current one
                for r in Annotation_CopyNumberVariation.objects.filter(pk__in=db_ids_others):
                    r.ref_graph_uuid = u
                    r.save()
            else:
                # annotation reference has not changed, so we only need to update the annotation content
                ggu.updateAnnotationContent(uuid=self.annot_graph_uuid, db_id=db_ids_others, data={"copy_number": new_aggr_copy_number})

        self.ref_graph_uuid = None
        self.annot_graph_uuid = None
        super(Annotation_CopyNumberVariation, self).save()

    @staticmethod
    def aggregateCopyNumber(id_list):
        cn_list = [x.copy_number for x in Annotation_CopyNumberVariation.objects.filter(pk__in=id_list)]
        if len(cn_list) == 2:
            return sorted(cn_list)[0]
        else:
            return numpy.median(cn_list)

    @staticmethod
    def testCopyNumberDist(id_list):
        THRESHOLD = 0.25
        cn_list = [x.copy_number for x in Annotation_CopyNumberVariation.objects.filter(pk__in=id_list)]
        return numpy.std(cn_list)/numpy.mean(cn_list) <= THRESHOLD

    def autoAnnotate(self):
        cnvObj = self.getCNVObj() ##### !!!!! MUST BE IMPLEMENTED !!!!! #####
        # this method shouldn't be like this: we should check all records related to the same sample+gene before we can conclude anything on the annotation label!

        # auto annotate if reference exists or is in Cosmic
        if cnvObj.exists():
            print "[Annotation_CopyNumberVariation (id=%d)] auto-annotate: yes (in refgraph)" % self.id
            self.copyToGraph()
        else:
            print "[Annotation_CopyNumberVariation (id=%d)] auto-annotate: skip" % self.id

class Annotation_FusionTranscript(Model):
    id_sample = CharField(max_length=26)
    id_experimental_data = CharField(max_length=32)
    id_analysis = ForeignKey('Analysis',db_column='id_analysis')
    ref_graph_uuid = CharField(max_length=32,null=True,blank=True)
    tx_5p_uuid = CharField(max_length=32,null=True,blank=True) # must be tx ac not uuid
    tx_3p_uuid = CharField(max_length=32,null=True,blank=True)
    start_5p = IntegerField()
    end_5p = IntegerField()
    start_3p = IntegerField()
    end_3p = IntegerField()
    conflict = BooleanField(default=False)
    conflict_info = CharField(max_length=2048,null=True,blank=True)

    class Meta:
        db_table = 'Annotation_FusionTranscript'

class FingerPrintingReport(Model):
    timestamp = DateTimeField()
    author = ForeignKey(User, blank=True, null=True)
    description = CharField(max_length=256, blank=True, null=True)
    task_id = CharField(max_length=128,default=None,null=True,blank=True)
    filename = CharField(max_length=128,default=None,null=True,blank=True)
    ready = BooleanField(default=False)
    error = BooleanField(default=False)
    qc_cutoff = IntegerField()
    mismatch_cutoff = IntegerField()
    samples = IntegerField(null=True,blank=True)
    excluded_samples = IntegerField(null=True,blank=True)
    mismatched_samples = IntegerField(null=True,blank=True)
    mismatched_cases = IntegerField(null=True,blank=True)
    false_mismatched_samples = IntegerField(null=True,blank=True)
    unmatched_samples = IntegerField(null=True,blank=True)
    mild_unmatched_cases = IntegerField(null=True,blank=True)
    serious_unmatched_cases = IntegerField(null=True,blank=True)
    validated_samples = IntegerField(null=True,blank=True)

    class Meta:
        db_table = 'FPReport'

    def initialize(self, user=None, description=None, analysis_obj=None):
        QC_cutoff = 5
        mismatch_limit = 2

        if description is None and analysis_obj is not None:
            description = "Auto-generated for analysis %s" % analysis_obj.name

        self.timestamp = timezone.now()
        self.author = user
        self.description = description
        self.ready = False
        self.qc_cutoff = QC_cutoff
        self.mismatch_cutoff = mismatch_limit
        self.save()

    def run(self, notifyViaEmail):
        req = tasks.runFingerPrinting.delay(self, notifyViaEmail)
        self.task_id = req.id
        self.save()

    def cancel(self):
        import annotationsManager.celery
        annotationsManager.celery.app.control.revoke(self.task_id, terminate=True)
        self.ready = True
        self.error = True
        names = self.getNames()
        try:
            shutil.rmtree(names['ResultsPath'])
        except:
            pass
        self.save()

    def delete(self, *args, **kwargs):
        names = self.getNames()
        try:
            if not self.error:
                os.remove(names['output_filename'])
            else:
                shutil.rmtree(names['ResultsPath'])
        except:
            pass
        super(FingerPrintingReport, self).delete(*args, **kwargs)

    def getNames(self):
        sequenom_folder = "sequenom"
        sequenom_report_name = "FPresults_"
        rootdir = os.path.join(settings.MEDIA_ROOT, sequenom_folder)
        st = self.timestamp.strftime('%Y%m%d_%H%M%S')
        ResultsPath = os.path.join(rootdir, "FPresults_" + st)
        filename = sequenom_folder + '/' + sequenom_report_name + st + '.zip'
        output_filename = rootdir + "/" + sequenom_report_name + st + '.zip'
        return {'sequenom_folder': sequenom_folder, 'sequenom_report_name': sequenom_report_name, 'rootdir': rootdir, 'st': st, 'ResultsPath': ResultsPath, 'filename': filename, 'output_filename': output_filename}

    def fingerPrinting(self):
        names = self.getNames()
        st = names['st']
        ResultsPath = names['ResultsPath']
        filename = names['filename']
        output_filename = names['output_filename']

        QC_cutoff = self.qc_cutoff
        mismatch_limit = self.mismatch_cutoff
        
        cases = {}         # cases = {case:[samples]}
        sample_cases = {}  # sample_cases = {sample:case}
        analyses = {}      # analyses = {sample:{SNP:genotype}}
        refs = {}          # refs = {type:[sample]}
        refs["germline"] = set()
        germlines = []
        refs["tumor"] = set()
        summary_results = {}        # scores = {sample:{ref_type:{ref:score}}}
        filtered_results = {}

        mismatched_cases = {} # mismatched pairs of cases {sample:ref}
        unmatched_cases = set()
        cross_matches = {} # cross_matches = {sample:ref}

        badQCsamples = []

        scores_to_germlines = {}
        scores_to_tumors = {}
        scores_to_case = {}
        scores_to_all = []

        GermlineTissues = set(["NLH","NMH"])
        CancerTissues = set(["LMH","PRH"])
        XenoTissues = set(["LMX","PRX"])

        ### array data structures ###
        index_to_sample = []
        sample_to_index = {}
        index_to_sgv = list(Annotation_ShortGeneticVariation.objects.exclude(plate_id=None).exclude(well_id=None).values_list('sgv_name',flat=True).distinct().order_by('sgv_name'))
        sgv_to_index = {k:i for i,k in enumerate(index_to_sgv)}
        analyses_array = []
        nucleotide_map = {'A': 1<<0, 'T': 1<<1, 'C': 1<<2, 'G': 1<<3}
        nucleotide_rev_map = ['A', 'T', 'C', 'G']
        FAILED = 1<<7


        def sample_case(sample):
            return sample[:7]

        def sample_lineage(sample):
            return sample[10:12]

        def tissue_type(sample):
            return sample[7:10]

        def QCscore(sample_index):
            # calcola uno score associato a un campione
            # per ogni snp, assegna:
            # 1 punto se il genotipo contiene lettere diverse da ATCG (es. / oppure BS etc.)
            # 0 punti viceversa
            QCscore = 0
            sample = analyses_array[sample_index]
            QCscore += sum([1 if x == FAILED else 0 for x in sample])

            if QCscore > QC_cutoff:
                print index_to_sample[sample_index] , ":"
                print "QCscore: ", QCscore
                print "*****"
                print
            return QCscore

        def runComparison(final_scores, testArray, refArray):
            analyses_count = 0
            progress = 0
            for i in xrange(0, len(testArray)):
                t = testArray[i]
                scores = array('B', len(refArray) * [0])
                for j in xrange(0, len(refArray)):
                    r = refArray[j]
                    if i == j:
                        # when test and ref are the same, do not calculate score
                        continue
                    s = 0
                    for z in xrange(0,num_rs):
                        s += 1 if t[z] != FAILED and r[z] != FAILED and t[z] & (~r[z]) else 0
                    scores[j] = s
                final_scores[i] = scores
                if progress == 50:
                    print analyses_count, "analyses completed", " - ", index_to_sample[i]
                    print "-------------------"
                    progress = 0
                analyses_count += 1
                progress += 1
            print "done"
            return analyses_count

        print st

        os.makedirs(ResultsPath)
        os.chdir(ResultsPath)

        try:

            file_out = open ("FPanalyses_" + st + "_mismatches.txt", "w")
            file_out1 = open ("FPanalyses_" + st + "_false_mismatches.txt", "w")
            file_out2 = open ("FPanalyses_" + st + "_unmatches.txt", "w")
            file_out3 = open ("FPanalyses_" + st + "_mismatched_cases.txt", "w")
            file_out4 = open ("FPanalyses_" + st + "_unmatched_cases.txt", "w")
            #file_out5 = open ("FPanalyses_" + st + "_validated_samples.txt", "w")
            #file_out6 = open ("FPanalyses_" + st + "_all_scores.txt", "w")
            file_out7= open ("FPanalyses_" + st + "_mild_unmatches.txt", "w")
            file_out8= open ("FPanalyses_" + st + "_serious_unmatches.txt", "w")
            file_out9= open ("FPanalyses_" + st + "_summary_results.txt", "w")
            #file_out10= open ("FPanalyses_" + st + "_BadQC_samples.txt", "w")

            for record in Annotation_ShortGeneticVariation.objects.exclude(plate_id=None).exclude(well_id=None):

                # fill dictionaries with cases, samples, references, and results

                sampleID = record.id_sample + record.plate_id + record.well_id
                if sampleID not in sample_to_index:
                    sample_to_index[sampleID] = len(index_to_sample)
                    index_to_sample.append(sampleID)
                    analyses_array.append(array('B', 24*[0]))
               
                case = record.id_sample[:7]
                if case not in cases:
                    cases[case] = []

                if sampleID not in sample_cases:
                    sample_cases[sampleID] = case

                if not record.failed:
                    if record.allele_frequency > 0:
                        analyses_array[sample_to_index[sampleID]][sgv_to_index[record.sgv_name]] |= nucleotide_map[record.alt]
                else:
                    analyses_array[sample_to_index[sampleID]][sgv_to_index[record.sgv_name]] = FAILED

                if sampleID not in cases[case]:
                    cases[case].append(sampleID)

                if tissue_type(sampleID) in GermlineTissues and sampleID not in refs["germline"]:
                    refs["germline"].add(sampleID)
                elif tissue_type(sampleID) in CancerTissues and sampleID not in refs["tumor"]:
                    refs["tumor"].add(sampleID)

            print
            print
            print "Total records read: ", Annotation_ShortGeneticVariation.objects.count()
            print len(analyses_array) , "GermlineRefs: ", len(refs["germline"]), "TumorRefs: ", len(refs["tumor"]), "Cases: ", len(cases.keys())
            print "------------------------------"

            QC_count = 0
            badQC_count = 0
            goodQC_count = 0
            to_delete = []

            for sample_index in xrange(0, len(analyses_array)):
                QC_value = QCscore(sample_index)
                QC_count += 1
                if QC_value > QC_cutoff :
                    badQCsamples.append(sample_index)
                    badQC_count += 1
                    to_delete.append(sample_index)
                    sample = index_to_sample[sample_index]
                    if sample in refs["germline"]:
                            refs["germline"].remove(sample)                                 # eliminates low QC samples from refs
                    elif sample in refs["tumor"]:
                            refs["tumor"].remove(sample)
                    cases[sample_cases[sample]].remove(sample)
                    # anche del sample_cases[sample]

                else:
                    goodQC_count += 1
                if QC_count % 500 == 0:
                    print QC_count, " QC tests executed, "
                    print "-------------"

            # reverse list before deleting
            to_delete.reverse()
            for i in to_delete:
                del analyses_array[i]
                del index_to_sample[i]
            sample_to_index = {k:i for i,k in enumerate(index_to_sample)}

            germlines = refs["germline"]
            CasesWithGermline = set()
            for ref in refs["germline"]:
                case = sample_case(ref)
                CasesWithGermline.add(case)

            print "Total number of Samples analyzed: ", (goodQC_count + badQC_count)
            print "Total number of Samples excluded from analysis: ", badQC_count
            print "Good QC samples: ", len(analyses_array) , "GermlineRefs: ", len(refs["germline"]), "TumorRefs: ", len(refs["tumor"]), "Cases: ", len(cases.keys())
            print "--------------------------------"

            # mismatch calculations
            false_mismatches = {}
            mismatches_in_case = {}
            matches_to_others = {}
            ok_samples = []
            num_rs = len(index_to_sgv)

            print "computing scores..."
            analyses_count = 0
            scores_to_all = len(analyses_array) * [[]]
            runComparison(scores_to_all, analyses_array, analyses_array)

            # retrieve originating patient
            ggu = GenomeGraphUtility()
            collection_to_patient = {}
            for sample in sample_to_index:
                case = sample_case(sample)
                if case not in collection_to_patient:
                    collection_to_patient[case] = ggu.getPatientUuidFromCollection(case)

            # discriminates matches and mismatches
            for test_index, scores_array in enumerate(scores_to_all):
                mismatch_score = 0
                test_sample = index_to_sample[test_index]
                test_case = sample_case(test_sample)
                for ref_index, result in enumerate(scores_array):
                    if test_index == ref_index:
                        # explicitly skip case where test and reference are the same
                        continue
                    ref_sample = index_to_sample[ref_index]
                    ref_case = sample_case(ref_sample)
                    ref_pt = collection_to_patient[ref_case]
                    test_pt = collection_to_patient[test_case]
                    if (result == 0 or result < mismatch_limit and test_sample in germlines) and ref_case != test_case:
                        if ref_pt is not None and test_pt is not None and ref_pt != test_pt:
                            # true mismatch
                            mismatch_score += 1
                            if test_case not in mismatched_cases:
                                mismatched_cases[test_case] = set()
                            mismatched_cases[test_case].add(ref_case)
                            if test_sample not in matches_to_others:
                                matches_to_others[test_sample] = []
                            matches_to_others[test_sample].append(ref_sample)
                        else:
                            # false mismatch (patient is the same)
                            if test_sample not in false_mismatches:
                                false_mismatches[test_sample] = {'patient': test_pt, 'mismatches': []}
                            false_mismatches[test_sample]['mismatches'].append(ref_sample)
                    elif result > 0 and (ref_case == test_case) and (test_sample not in (refs["germline"] | refs["tumor"])):
                        mismatch_score += 1
                        if test_case not in unmatched_cases:
                            unmatched_cases.add(test_case)
                        if test_sample not in mismatches_in_case:
                            mismatches_in_case[test_sample] = []
                        mismatches_in_case[test_sample].append(ref_sample)
                if mismatch_score == 0:
                    ok_samples.append(test_sample)

            ### DEBUG
            #with open("var_mismatched_cases.txt", "w") as f:
            #    for k, v in sorted(mismatched_cases.iteritems()):
            #        for x in v:
            #            f.write("%s\t%s\n" % (k, x))

            #with open("var_matches_to_others.txt", "w") as f:
            #    for k, v in sorted(matches_to_others.iteritems()):
            #        for x in v:
            #            f.write("%s\t%s\n" % (k, x))

            #with open("var_unmatched_cases.txt", "w") as f:
            #    for v in sorted(unmatched_cases):
            #        f.write("%s\n" % v)

            #with open("var_ok_samples.txt", "w") as f:
            #    for v in sorted(ok_samples):
            #        f.write("%s\n" % v)

            #with open("var_mismatches_in_case.txt", "w") as f:
            #    for k, v in sorted(mismatches_in_case.iteritems()):
            #        for x in v:
            #            f.write("%s\t%s\n" % (k, x))
            ### DEBUG
     
            #filtered_unmatches = {k:set(v) for k,v in mismatches_in_case.iteritems()}
            filtered_unmatches = mismatches_in_case.copy()
            for sample, ref in mismatches_in_case.items():
                if len(ref) > 1:
                    for test, refs in filtered_unmatches.items():
                        if sample in refs:
                            refs.remove(sample)
                            if len(refs) == 0:
                                del filtered_unmatches[test]

            # segregate unmatches in mild and serious
            mild_unmatches = []
            serious_unmatches = []
            unmatch_casescores = {}

            for sample, Refs in filtered_unmatches.items():
                case = sample_case(sample)
                if case not in unmatch_casescores:
                    unmatch_casescores[case] = {}
                    unmatch_casescores[case]["max"] = 1
                    unmatch_casescores[case]["germ"] = 0
                max_score = 1
                germ_score = 0
                if case in CasesWithGermline:
                        germ_score += 1
                for ref in Refs:
                    test_index = sample_to_index[sample]
                    ref_index = sample_to_index[ref]
                    if scores_to_all[test_index][ref_index] > max_score:
                        max_score = scores_to_all[test_index][ref_index]
                    if tissue_type(ref) in (GermlineTissues | CancerTissues) and scores_to_all[test_index][ref_index] > mismatch_limit:
                        unmatch_casescores[case]["germ"] += 1
                if germ_score == 0:
                    unmatch_casescores[case]["germ"] += 1
                if max_score > unmatch_casescores[case]["max"]:
                    unmatch_casescores[case]["max"] = max_score

            for case in unmatch_casescores.keys():
                if unmatch_casescores[case]["max"] <= mismatch_limit or unmatch_casescores[case]["germ"] == 0:
                    mild_unmatches.append(case)
                else:
                    serious_unmatches.append(case)

            real_mismatches = {}
            for Test_Case, ref_cases in mismatched_cases.items():
                for RefCase in ref_cases:
                    i = 0
                    for test, refs in mismatched_cases.items():
                        if test == RefCase:
                            for ref in refs:
                                if ref == Test_Case:
                                    i += 1
                    if i > 0:
                        if RefCase in real_mismatches:
                            if Test_Case not in real_mismatches[RefCase]:
                                real_mismatches[RefCase].append(Test_Case)
                        elif Test_Case not in real_mismatches:
                            real_mismatches[Test_Case]=[]
                            real_mismatches[Test_Case].append(RefCase)
                        elif RefCase not in real_mismatches[Test_Case]:
                            real_mismatches[Test_Case].append(RefCase)

            print
            print "**************"
            print
            print "number of mismatched samples: ", len(matches_to_others.keys())
            print "number of mismatched cases: ", len(real_mismatches.keys())
            print "number of unmatched samples: ", len(filtered_unmatches.keys())
            print "number of cases with mild unmatches: ", len(mild_unmatches)
            print "number of cases with serious unmatches: ", len(serious_unmatches)
            print "number of validated samples: ", len(ok_samples)
            print
            print "---------------"
            print

            file_out.write("Sample"+"\t"+"Reference"+"\n")
            for sample, references in matches_to_others.items():
                for reference in references:
                    file_out.write(str(sample) + "\t" + str(reference)+"\n")
            file_out.close()

            file_out1.write("Test Sample\tReference Sample\tPatient UUID\n")
            for test_sample, data in false_mismatches.iteritems():
                patient = data['patient'] if data['patient'] else ""
                for ref_sample in data['mismatches']:
                    file_out1.write(test_sample + "\t" + ref_sample + "\t" + patient + "\n")
            file_out1.close()

            file_out2.write("Sample"+"\t"+"Reference"+"\n")
            for sample, references in filtered_unmatches.items():
                for reference in references:
                    file_out2.write(str(sample) + "\t" + str(reference)+"\n")
            file_out2.close()

            file_out3.write("Test_Case"+"\t"+"Ref_Case"+"\n")
            for test, refs in real_mismatches.items():
                for ref in refs:
                    file_out3.write(str(test) + "\t" + str(ref)+"\n")
            file_out3.close()

            file_out4.write("Unmatched_Case"+"\n")
            for case in unmatched_cases:
                file_out4.write(str(case) + "\n")
            file_out4.close()

            file_out7.write("Unmatched_Case"+"\n")
            for case in mild_unmatches:
                file_out7.write(str(case) + "\n")
            file_out7.close()

            file_out8.write("Unmatched_Case"+"\n")
            for case in serious_unmatches:
                file_out8.write(str(case) + "\n")
            file_out8.close()

            file_out9.write("Parameters"+"\n")
            file_out9.write("\n" + "QC_cutoff: "+ "\t" + str(QC_cutoff) + "\n"+ "Mismatch_cutoff:" + "\t" + str(mismatch_limit) + "\n"+ "\n")
            file_out9.write("total number of samples: "+ "\t" + str(badQC_count + goodQC_count)+"\n")
            file_out9.write("number of samples excluded from analysis: "+ "\t" + str(badQC_count)+"\n"+ "\n"+ "\n")

            file_out9.write("Summary Results"+"\n" + "number of mismatched samples: "+ "\t" + str(len(matches_to_others.keys()))+"\n")
            file_out9.write("number of mismatched cases: "+ "\t" + str(len(real_mismatches.keys()))+"\n")
            file_out9.write("number of false mismatched samples: "+ "\t" + str(len(false_mismatches))+"\n")
            file_out9.write("number of unmatched samples: "+ "\t" + str(len(filtered_unmatches.keys()))+"\n")
            file_out9.write("number of cases with mild unmatches: "+ "\t" + str(len(mild_unmatches))+"\n")
            file_out9.write("number of cases with serious unmatches: "+ "\t" + str(len(serious_unmatches))+"\n")
            file_out9.write("number of validated samples: "+ "\t" + str(len(ok_samples)))
            file_out9.close()

            shutil.make_archive(output_filename.replace('.zip', ''), 'zip', ResultsPath)
            shutil.rmtree(ResultsPath)

            self.samples = badQC_count + goodQC_count
            self.excluded_samples = badQC_count
            self.mismatched_samples = len(matches_to_others)
            self.mismatched_cases = len(real_mismatches)
            self.false_mismatched_samples = len(false_mismatches)
            self.unmatched_samples = len(filtered_unmatches)
            self.mild_unmatched_cases = len(mild_unmatches)
            self.serious_unmatched_cases = len(serious_unmatches)
            self.validated_samples = len(ok_samples)

            self.ready = True
            self.error = False
            self.filename = filename
            self.save()

            print "Analyses completed."
        except Exception, e:
            print "An error occurred"
            self.filename = None
            self.ready = True
            self.error = True
            self.qc_cutoff = QC_cutoff
            self.mismatch_cutoff = mismatch_limit
            self.samples = None
            self.excluded_samples = None
            self.mismatched_samples = None
            self.mismatched_cases = None
            self.false_mismatched_samples = None
            self.unmatched_samples = None
            self.mild_unmatched_cases = None
            self.serious_unmatched_cases = None
            self.validated_samples = None
            self.save()
            shutil.rmtree(ResultsPath)
            raise e

class DrugResponseCriterion(Model):
    name = CharField(max_length=128, unique=True)
    label = CharField(max_length=64, unique=True)
    class Meta:
        db_table = 'DrugRespCrit'
    def __unicode__(self):
        return "(%d) %s" % (self.id, self.name)
    def getResponseClass(self, value):
        # the following holds:
        # th_low <= VAL < th_high
        return self.drugresponseclass_set.get(Q(thresholdLow__lte=value,thresholdHigh__gt=value)|Q(thresholdLow=None,thresholdHigh__gt=value)|Q(thresholdLow__lte=value,thresholdHigh=None))

class DrugResponseClass(Model):
    criterion = ForeignKey('DrugResponseCriterion')
    shortName = CharField(max_length=16, unique=True)
    fullName = CharField(max_length=128)
    thresholdLow = FloatField(null=True, blank=True)
    thresholdHigh = FloatField(null=True, blank=True)
    class Meta:
        db_table = 'DrugRespClass'
    def __unicode__(self):
        return "(%d) %s: %s (%s) [%g to %g]" % (self.id, self.criterion.name, self.shortName, self.fullName, self.thresholdLow or float("-inf"), self.thresholdHigh or float("inf"))
    def save(self, *args, **kwargs):
        if self.thresholdLow is None and self.thresholdHigh is None:
            # at least one of the thresholds must be non-null
            raise Exception("At least one of the thresholds must be non-null")
        super(DrugResponseClass, self).save(*args, **kwargs)

class ExperimentType(Model):
    # This table should list all types of experiments (e.g. whole exome sequencing)
    name = CharField(max_length=32,unique=True)
    description = CharField(max_length=255, blank=True, null=True)
    hasParameters = NullBooleanField()
    baseLabel = CharField(max_length=255, unique=True,null=True,blank=True)
    technologyLabel = CharField(max_length=32, blank=True, null=True)
    expQuery = ForeignKey('ExperimentQuery',null=True,blank=True)
    hasTargetSequence = BooleanField()
    class Meta:
        db_table = 'ExperimentType'
    def __unicode__(self):
        return self.name
    def getReftypeLabels(self):
        return [x.labelTerm.name for x in set(self.experimenttype_has_analysedlabelterm_set.all())]

class ExperimentQuery(Model):
    name = CharField(max_length=32)
    text = CharField(max_length=1024)
    parameters = CharField(max_length=1024, blank=True, null=True)
    class Meta:
        db_table = 'ExpQuery'
    def __unicode__(self):
        return "(%d) %s" % (self.id, self.name)

class ExperimentType_has_AnalysedLabelTerm(Model):
    # This table links each experiment type to the graph reference labels representing the types of phenomena
    # whose analysis is normally taken into account in this type of experiment
    # e.g. whole-exome seq => [sequence_alteration, ...]
    expType = ForeignKey('ExperimentType')
    labelTerm = ForeignKey('LabelTerm')
    labelQuery = ForeignKey('LabelQuery')
    class Meta:
        db_table = 'ExpType_has_LabelTerm'
    def __unicode__(self):
        return "Experiment = %s, analysed label = %s" % (str(self.expType), str(self.labelTerm))

class LabelQuery(Model):
    name = CharField(max_length=32)
    text = CharField(max_length=1024)
    class Meta:
        db_table = 'LabelQuery'
    def __unicode__(self):
        return "(%d) %s" % (self.id, self.name)

'''
class Analysis_has_AnalysedLabelTerm(Model):
    # This table links each analysis to the graph reference labels representing the types of phenomena
    # whose analysis has been taken into account in this analysis
    # The reason is that, while a technology may allow investigating different types of alterations,
    # it doesn't mean that *all* of them have been considered in each and every analysis.
    # So each analysis will be linked to a subset (or, sometimes, to all) of the labelTerms allowed.
    analysis = ForeignKey('Analysis')
    labelTerm = ForeignKey('LabelTerm')
    class Meta:
        db_table = 'Analysis_has_LabelTerm'
    def __unicode__(self):
        return "Analysis = %s, analysed label = %s" % (str(self.analysis), str(self.labelTerm))
'''

'''
class GraphQueryTemplate(Model):
    # This table should list all queries designed to retrieve annotation references from the graph
    # 'parameters' lists all query parameter names
    name = CharField(max_length=32)
    text = CharField(max_length=1024, blank=True, null=True)
    parameters = CharField(max_length=1024, blank=True, null=True)
    class Meta:
        db_table = 'GraphQueryTemplate'
    def __unicode__(self):
        return "(%d) %s" % (self.id, self.name)
'''

'''
class ExpType_has_GraphQTemplate(Model):
    # This table links one or more experiment types to one or more queries
    expType = ForeignKey('ExperimentType')
    queryTemplate = ForeignKey('GraphQueryTemplate')
    class Meta:
        db_table = 'ET_has_GQT'
    def __unicode__(self):
        return "Exp = %s, GQT = %s" % (str(self.expType), str(self.queryTemplate))
'''

class Analysis(Model):
    # This table mirrors all analysis nodes on the graph
    # The analysis is linked to the refset that includes all of its reference nodes
    # N.B. the refset is linked to one (experiment type, label term) pair
    # Hence, each analysis may only refer to one experiment type and label term
   
    graph_uuid = CharField(max_length=32)
    name = CharField(max_length=255)
    refSet = ForeignKey('RefSet', blank=True, null=True)
    creationDate = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Analysis'
   
    def getReftypeLabels(self):
        return [self.refSet.expTypeAndLabelTerm.labelTerm.name] # N.B. valutare se occorre che questo valore di ritorno sia una lista oppure se sia possibile rimuovere le [] e restituire un singolo valore scalare

    def __unicode__(self):
        return self.name

    def assignQuerySet(self, expTypeHasLabelTerm, params):
        # Check if a label already exists that describes the same set of references
        # if so, select that label
        # otherwise, create a new one
        # Checking whether the current set of reference regions is already described by an existing label boils down to checking whether an analysis already exists
        # - with the same exp. type (i.e., same queries)
        # - with the same values for each query parameter of each query
       
        # N.B. The case in which a different set of query (most probably with different parameters) will produce the same set of reference regions cannot be checked unless all queries are run. Furthermore, the equality may hold at a given point in time, but might not necessarily hold at a later time, when new nodes have been added to the kb. Even so, it may still make sense to keep such sets separate (even if equal) since they might be coming from totally different grounds.

        refsets = RefSet.objects.filterByQueryParamValues(expTypeHasLabelTerm, params)
        if len(refsets) > 0:
            print "using existing refset:", str(refsets[0])
            self.refSet = refsets[0]
        else:
            print "creating new refset"
            rs = RefSet.objects.createNew(expTypeHasLabelTerm, params)
            self.refSet = rs

        self.save()

class RefSet_Manager(Manager):
    def filterByQueryParamValues(self, etHasLt, params):
        refsets = self.filter(expTypeHasLabelTerm=etHasLt)
        expType = etHasLt.expType
        if expType.hasParameters == True:
            results = []
            # check if an existing query set can be reused
            equal = False
            for refset in refsets:
                equal = True
                queryParams = json.loads(expType.expQuery.parameters)
                instanceParams = json.loads(refset.expQParamValues)
                for p in queryParams:
                    p_name = p[0]
                    p_type = p[1]
                    if p_name not in params:
                        raise Exception("Missing reference parameter in params dictionary: {0}".format(p_name))
                    elif type(params[p_name]) in type_map[p_type]['python_types']:
                        if not type_map[p_type]['equal'](params[p_name], instanceParams[p_name]):
                            # parameter has a different value
                            equal = False
                            break
                    else:
                        raise Exception("Parameter '{0}' should be {1}, but incompatible type '{2}' was found".format(p_name, p_type, type(params[p_name]).__name__))
                    if not equal:
                        break
                if equal:
                    results.append(refset)
            return results
        else:
            return refsets

    def createNew(self, etHasLt, params):
        expType = etHasLt.expType
        relevantEtHLt = expType.experimenttype_has_analysedlabelterm_set.all()
        qs = self.model()
        otherRefsets = self.filter(expTypeHasLabelTerm__in=relevantEtHLt)
        if len(otherRefsets) > 0:
            qs.fullLabel = expType.baseLabel + str(int(max(otherRefsets, key=lambda z:int(z.fullLabel.replace(expType.baseLabel, ""))).fullLabel.replace(expType.baseLabel, ""))+1)
        else:
            qs.fullLabel = expType.baseLabel + "1"
        qs.expTypeHasLabelTerm = etHasLt
        queryParams = json.loads(expType.expQuery.parameters)
        instanceParams = {}
        for p in queryParams:
            p_name = p[0]
            p_type = p[1]
            if p_name not in params:
                raise Exception("Missing reference parameter in params dictionary: {0}".format(p_name))
            elif type(params[p_name]) not in type_map[p_type]['python_types']:
                raise Exception("Parameter '{0}' should be a {1}, but incompatible type '{2}' was found".format(p_name, p_type, type(params[p_name]).__name__))
            else:
                instanceParams[p_name] = params[p_name]
        qs.expQParamValues = json.dumps(instanceParams)
        qs.save()
        return qs

class RefSet(Model):
    fullLabel = CharField(max_length=255)
    expTypeHasLabelTerm = ForeignKey('ExperimentType_has_AnalysedLabelTerm')
    lastLabelApplyDate = DateTimeField(blank=True, null=True)
    expQParamValues = CharField(max_length=2048, blank=True, null=True)
    objects = RefSet_Manager()
    class Meta:
        db_table = 'RefSet'
    def __unicode_(self):
        return self.fullLabel

    # 'applyLabel' applies the refset label to all nodes returned by the associated queries
    # It should be run after annotations have been copied
    # to the graph, or whenever the graph reference nodes change
    # A timestamp is created storing the date and time of the last execution
    def applyLabel(self, force=False):
        # by term label we mean the otherwise called "reftype label" i.e., the phenomenon analysed (e.g. seq. alteration etc.)
        term_label = self.expTypeHasLabelTerm.labelTerm

        do_update = True
        if force:
            print "Forcing apply label"
        elif not self.lastLabelApplyDate:
            print "Label has never been applied, applying now"
        elif term_label.lastInsert >= self.lastLabelApplyDate:
            print "%s has newer entries, applying label" % term_label.name
        else:
            do_update = False
       
        if do_update == True:
            g = GenomeGraphUtility()
            g.applyLabelToNodes(self.expTypeHasLabelTerm.expType.expQuery.text, self.expTypeHasLabelTerm.labelQuery.text, self.fullLabel, json.loads(self.expQParamValues))
            self.lastLabelApplyDate = timezone.now()
            self.save()
        print "Up to date"

    def getReferenceNodes(self):
        g = GenomeGraphUtility()
        term_label = self.expTypeHasLabelTerm.labelTerm
        result = {}
        all_info = []
        m = term_label.getGraphModel()
        # getLabeledNodes returns a list of uuids
        uuid_list = g.getLabeledNodes(self.fullLabel, term_label.name)
        if uuid_list == []:
            uuid_list = g.getNodesFromQuery(self.expTypeHasLabelTerm.expType.expQuery.text, self.expTypeHasLabelTerm.labelQuery.text, json.loads(self.expQParamValues), term_label.name)
        # N.B. To avoid unacceptable performance decrease, we must use a method that performs a single query
        # to retrieve the data related to all objects (as opposed to performing a query for each object)
        r = m.byUuid_list(uuid_list)
        for y in r:
            try:
                all_info.extend(y.getInfo())
            except:
                pass
        result[term_label.name] = all_info
        return result
   
    def getReftypeLabel(self):
        return self.expTypeHasLabelTerm.labelTerm.name

'''
class GQTSet(Model):
    # A set of queries that, taken together, describe the reference for a specific class of experiments
    # It is linked to the experiment type
    # If the query set has an experiment type different than "other",
    # then it must have a relationship with each of the queries linked to that
    # type. Otherwise, if the exp. type is "other", the query set
    # may have a relationship with any number of queries
    # The same query set may be referenced by multiple analyses that share the same set of reference region nodes
    # This also means that the reference nodes of all such queries will have the same label
    fullLabel = CharField(max_length=255)
    expType = ForeignKey('ExperimentType')
    lastLabelApplyDate = DateTimeField(blank=True, null=True)
    objects = GQTSet_Manager()
    class Meta:
        db_table = 'GQTSet'
    def __unicode__(self):
        return self.fullLabel

    # 'applyLabel' applies the refset label to all nodes returned by the associated queries
    # It should be run after annotations have been copied
    # to the graph, or whenever the graph reference nodes change
    # A timestamp is created storing date and time of the last execution
    def applyLabel(self, force=False):
        # by term label we mean the otherwise called "reftype label" i.e., the phenomenon analysed (e.g. seq. alteration etc.)
        term_labels = []
        term_labels.extend([x.labelTerm for x in self.expType.experimenttype_has_analysedlabelterm_set.all()])
        term_labels = set(term_labels)
        if force or not self.lastLabelApplyDate:
            do_update = True
        else:
            do_update = False
            for t in term_labels:
                if t.lastInsert >= self.lastLabelApplyDate:
                    print "LabelTerm %s has newer entries" % t.name
                    do_update = True
        if do_update == True:
            g = GenomeGraphUtility()
            for aq in self.gqtset_has_graphqtemplate_set.all():
                g.applyLabelToNodes(aq.queryTemplate.text, ANALYSIS_LABEL_PREFIX + self.fullLabel, json.loads(aq.parameterValues))
            self.lastLabelApplyDate = timezone.now()
            self.save()
        print "Up to date"

    def getReferenceNodes(self):
        g = GenomeGraphUtility()
        term_labels = []
        result = {}
        term_labels.extend([x.labelTerm for x in self.expType.experimenttype_has_analysedlabelterm_set.all()])
        term_labels = set(term_labels)
        for t in term_labels:
            all_info = []
            m = t.getGraphModel()
            # getLabeledNodes returns a list of uuids
            uuid_list = g.getLabeledNodes(ANALYSIS_LABEL_PREFIX + self.fullLabel, t.name)
            # N.B. To avoid unacceptable performance decrease, we must use a method that performs a single query
            # to retrieve the data related to all objects (as opposed to performing a query for each object)
            r = m.byUuid_list(uuid_list)
            for y in r:
                try:
                    all_info.extend(y.getInfo())
                except:
                    pass
            result[t.name] = all_info
        return result
'''

'''class GQTSet_has_GraphQTemplate(Model):
    # This table links a query set to its corresponding reference queries
    # Such relationships always exist (even when the query has no parameters)
    # 'parameterValues' lists a scalar value or a list of values for each query parameter
    # in the form of a JSON dictionary
    querySet = ForeignKey('GQTSet')
    queryTemplate = ForeignKey('GraphQueryTemplate')
    parameterValues = CharField(max_length=2048, blank=True, null=True)
    class Meta:
        db_table = 'GQTSet_has_GQT'
    def __unicode__(self):
        return "GQTSet = %s, GQT = %s" % (str(self.querySet), str(self.queryTemplate))
'''

class FailedAnalysis(Model):
    # This table lists each (analysis, region, sample) tuple for which the analysis resulted in failure
    # This list must be subtracted when querying the graph, so that (sample, site) pairs
    # whose analysis has not been successful are not erroneously considered "wild-type".
    analysis = ForeignKey('analysis')
    sampleGenid = CharField(max_length=26)
    ref = CharField(max_length=30)
    start = IntegerField()
    end = IntegerField()
    class Meta:
        db_table = 'FailedAnalysis'
    def __unicode__(self):
        return "Analysis = {0}, Sample = {1}, failed on = {2}:{3}-{4}".format(str(self.analysis), str(self.sampleGenid), self.ref, self.start, self.end)

class PredefinedGenomicTargetList(Model):
    name = CharField(max_length=64)
    data = CharField(max_length=8192)
    user = ForeignKey(User)
    class Meta:
        unique_together = ('name', 'user')
        db_table = 'PredefGenomList'
    def __unicode__(self):
        return self.name

class AnnotationUpdateBatch(Model):
    WAITING = 'wt'
    RUNNING = 'run'
    COMPLETED = 'ok'
    ERROR = 'err'
    STATUS = ((WAITING, 'waiting'), (RUNNING, 'running'), (COMPLETED, 'completed'), (ERROR, 'error'))

    PARTIAL = 'part'
    FULL = 'full'
    UPDATE_TYPE = ((PARTIAL, 'partial'), (FULL, 'full'))

    dateStart = DateTimeField(null=True,blank=True)
    dateEnd = DateTimeField(null=True,blank=True)
    status = CharField(max_length='3',choices=STATUS,default=WAITING)
    task_id = CharField(max_length=128,default=None,null=True,blank=True)
    updateType = CharField(max_length='4',choices=UPDATE_TYPE,default=PARTIAL)

    class Meta:
        db_table = 'AnnotUpdateBatch'

    def run(self):
        self.dateStart = timezone.now()
        self.status = AnnotationUpdateBatch.RUNNING
        self.save()

        if self.updateType == self.PARTIAL:
            print "[Running partial update]"
            records = self.kbreferencehistory_set.all()
            for r in records:
                obj = KBReference.byUuid(r.uuid)
                if not obj:
                    continue
                print "Add", obj.getInfo()
                model = obj.getAnnotationModel()
                try:
                    model.objects.autoAnnotate(refObj=obj, willExist=True)
                except:
                    r.annotationUpdateBatch = None
                    r.save()
        else:
            print "[Running full update]"
            labels = annotations.models.LabelTerm.objects.filter(fatherLabel=None)
            for l in labels:
                print "label:", l.name
                m = l.getAnnotationModel()
                try:
                    m.objects.autoAnnotate()
                except:
                    pass

        self.dateEnd = timezone.now()
        self.status = AnnotationUpdateBatch.COMPLETED
        self.save()

class KBReferenceHistory_Manager(Manager):
    def pendingReferences(self):
        return len(self.filter(annotationUpdateBatch=None)) > 0

    def createBatchForPendingReferences(self, updateType=AnnotationUpdateBatch.PARTIAL):
        records = self.filter(annotationUpdateBatch=None)
        if len(records) == 0 and updateType == AnnotationUpdateBatch.PARTIAL:
            return None
        b = AnnotationUpdateBatch(status=AnnotationUpdateBatch.WAITING,updateType=updateType)
        b.save()
        print "batch saved", b.id
        for r in records:
            r.annotationUpdateBatch = b
            r.save()
            print "r.annotationUpdateBatch=",r.annotationUpdateBatch_id
        
        if updateType == AnnotationUpdateBatch.FULL:
            # also assign references from previous pending batches to the current one
            backlog = list(AnnotationUpdateBatch.objects.filter(status=AnnotationUpdateBatch.WAITING,updateType=AnnotationUpdateBatch.PARTIAL))
            for bb in backlog:
                for r in bb.kbreferencehistory_set.all():
                    r.annotationUpdateBatch = b
                    r.save()
            # delete previous pending batches
            for bb in backlog:
                bb.delete()

        return b

class KBReferenceHistory(Model):
    ADD = 'add'
    DELETE = 'del'
    ACTIONS = ((ADD, 'add'), (DELETE, 'delete'))

    uuid = CharField(max_length=32)
    data = CharField(max_length=1024)
    labelTerm = ForeignKey('LabelTerm')
    action = CharField(max_length=3,choices=ACTIONS)
    dateAction = DateTimeField(auto_now_add=True)
    annotationUpdateBatch = ForeignKey('AnnotationUpdateBatch',null=True,blank=True)

    objects = KBReferenceHistory_Manager()

    class Meta:
        db_table = 'KBRefHistory'

#### Reference Databases
class UCSCSnp141_Manager(Manager):
    def populate(self):
        if UCSCSnp141.objects.count() > 0:
            print "Table not empty, aborting populate"
            return

        import MySQLdb
        import MySQLdb.cursors
        records = []
        print "Starting to populate UCSCSnp141"
        print "Connecting to " + settings.UCSC['HOST']
        db = MySQLdb.connect(settings.UCSC['HOST'], settings.UCSC['USER'], settings.UCSC['PASSWORD'], settings.UCSC['NAME'])
        print "Connected"
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM `snp141`")
        num_rows = cursor.fetchone()[0]
        step = num_rows / 100
        batch_size = 10000
        
        #results = cursor.fetchall()
        cnt = 0
        progress = 0
        progress_cnt = 0
        max_attempts = 5
        attempts = max_attempts
        print "Importing data"
        while cnt < num_rows:
            try:
                cursor = db.cursor()
                cursor.execute("SELECT `bin`, `chrom`, `chromStart`, `chromEnd`, `name`, `score`, `strand`, `refNCBI`, `refUCSC`, `observed`, `molType`, `class`, `valid`, `avHet`, `avHetSE`, `func`, `locType`, `weight`, `exceptions`, `submitterCount`, `submitters`, `alleleFreqCount`, `alleles`, `alleleNs`, `alleleFreqs`, `bitfields` FROM `snp141` limit %d offset %d" % (batch_size, cnt))
                attempts = max_attempts
                for row in cursor:
                    records.append(UCSCSnp141(*((cnt+1,) + row)))
                    cnt += 1
                    progress_cnt += 1
                    if progress_cnt == step:
                        progress_cnt = 0
                        progress += 1
                        print "%d%%" % progress
                self.bulk_create(records)
                records = []
            except MySQLdb.Error, e:
                while attempts > 0:
                    try:
                        attempts -= 1
                        db = MySQLdb.connect(settings.UCSC['HOST'], settings.UCSC['USER'], settings.UCSC['PASSWORD'], settings.UCSC['NAME'])
                        break
                    except:
                        pass
                else:
                    print "An error occurred while fetching data from " + settings.UCSC['HOST'] + " -- aborting"
                    return

        return num_rows

class UCSCSnp141(Model):    # includes polymorphism data from NCBI's dbSNP
    bin = IntegerField()                                            # Indexing field to speed chromosome range queries.
    chrom = CharField(max_length=93)                                # Reference sequence chromosome or scaffold
    chromStart = IntegerField(db_column='chromStart')               # Start position in chrom
    chromEnd = IntegerField(db_column='chromEnd')                   # End position in chrom
    name = CharField(max_length=45)                                 # dbSNP Reference SNP (rs) identifier
    score = IntegerField()                                          # Not used
    strand = CharField(max_length=3)                                # Which DNA strand contains the observed alleles
    refNCBI = TextField(db_column='refNCBI')                        # Reference genomic sequence from dbSNP
    refUCSC = TextField(db_column='refUCSC')                        # Reference genomic sequence from UCSC lookup of chrom,chromStart,chromEnd
    observed = CharField(max_length=765)                            # The sequences of the observed alleles from rs-fasta files
    molType = CharField(max_length=21, db_column='molType')         # Sample type from exemplar submitted SNPs (ss) ('unknown', 'genomic', 'cDNA')
    snpClass = CharField(max_length=42, db_column='class')          # Class of variant ('unknown', 'single', 'in-del', 'microsatellite', 'mnp', 'insertion', 'deletion')
    valid = CharField(max_length=255)                               # Validation status of the SNP ('unknown', 'by-cluster', 'by-frequency', 'by-submitter', 'by-2hit-2allele', 'by-hapmap', 'by-1000genomes')
    avHet = FloatField(db_column='avHet')                           # Average heterozygosity from all observations. Note: may be computed on small number of samples.
    avHetSE = FloatField(db_column='avHetSE')                       # Standard Error for the average heterozygosity
    func = CharField(max_length=462)                                # Functional category of the SNP ('unknown', 'coding-synon', 'intron', 'near-gene-3', 'near-gene-5', 'ncRNA', 'nonsense', 'missense', 'stop-loss', 'frameshift', 'cds-indel', 'untranslated-3', 'untranslated-5', 'splice-3', 'splice-5')
    locType = CharField(max_length=51, db_column='locType')         # Type of mapping inferred from size on reference; may not agree with class ('range', 'exact', 'between', 'rangeInsertion', 'rangeSubstitution', 'rangeDeletion')
    weight = IntegerField()                                         # The quality of the alignment: 1 = unique mapping, 2 = non-unique, 3 = many matches
    exceptions = CharField(max_length=1146)                         # Unusual conditions noted by UCSC that may indicate a problem with the data ('RefAlleleMismatch', 'RefAlleleRevComp', 'DuplicateObserved', 'MixedObserved', 'FlankMismatchGenomeLonger', 'FlankMismatchGenomeEqual', 'FlankMismatchGenomeShorter', 'SingleClassLongerSpan', 'SingleClassZeroSpan', 'SingleClassTriAllelic', 'SingleClassQuadAllelic', 'ObservedWrongFormat', 'ObservedTooLong', 'ObservedContainsIupac', 'ObservedMismatch', 'NonIntegerChromCount', 'AlleleFreqSumNot1', 'SingleAlleleFreq', 'InconsistentAlleles')
    submitterCount = IntegerField(db_column='submitterCount')       # Number of distinct submitter handles for submitted SNPs for this ref SNP
    submitters = TextField()                                        # List of submitter handles
    alleleFreqCount = IntegerField(db_column='alleleFreqCount')     # Number of observed alleles with frequency data
    alleles = TextField()                                           # Observed alleles for which frequency data are available
    alleleNs = TextField(db_column='alleleNs')                      # Count of chromosomes (2N) on which each allele was observed. Note: this is extrapolated by dbSNP from submitted frequencies and total sample 2N, and is not always an integer.
    alleleFreqs = TextField(db_column='alleleFreqs')                # Allele frequencies
    bitfields = CharField(max_length=486)                           # SNP attributes extracted from dbSNP's SNP_bitfield table
    
    objects = UCSCSnp141_Manager()
    
    class Meta:
        db_table = u'UCSC_hg19_snp141'

    def getAlleles(self):
        if self.observed != 'lengthTooLong':
            if self.snpClass != 'microsatellite':
                return map(chr, range(ord('A'), ord('A') + len(self.observed.split('/'))))
            else:
                parts = self.observed.split(')')
                return map(chr, range(ord('A'), ord('A') + len(parts[1].split('/'))))
        else:
            raise InvalidEntryError()

class EnsemblTranscriptXref_Manager(Manager):
    def populate(self):
        if EnsemblTranscriptXref.objects.count() > 0:
            print "Table not empty, aborting populate"
            return

        import MySQLdb
        import MySQLdb.cursors
        records = []
        print "Starting to populate EnsemblTranscriptXref"
        print "Connecting to " + settings.ENSEMBL['HOST']
        db = MySQLdb.connect(settings.ENSEMBL['HOST'], settings.ENSEMBL['USER'], settings.ENSEMBL['PASSWORD'], settings.ENSEMBL['NAME'],cursorclass = MySQLdb.cursors.SSCursor)
        print "Connected"
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM transcript, object_xref, xref,external_db WHERE transcript.transcript_id = object_xref.ensembl_id AND object_xref.ensembl_object_type = 'Transcript' AND object_xref.xref_id = xref.xref_id AND xref.external_db_id = external_db.external_db_id AND external_db.db_name in ('RefSeq_mRNA', 'CCDS')")
        num_rows = cursor.fetchone()[0]
        step = num_rows / 100
        batch_size = 10000
        cursor = db.cursor()
        cursor.execute("SELECT transcript.stable_id as ensembl_id, xref.display_label as ext_id FROM transcript, object_xref, xref,external_db WHERE transcript.transcript_id = object_xref.ensembl_id AND object_xref.ensembl_object_type = 'Transcript' AND object_xref.xref_id = xref.xref_id AND xref.external_db_id = external_db.external_db_id AND external_db.db_name in ('RefSeq_mRNA', 'CCDS')")
        #results = cursor.fetchall()
        cnt = 0
        progress = 0
        print "Importing data"
        for row in cursor:
            records.append(EnsemblTranscriptXref(ensembl_id=row[0], external_id=row[1]))
            if len(records) == batch_size:
                self.bulk_create(records)
                records = []
            cnt += 1
            if cnt == step:
                cnt = 0
                progress += 1
                print "%d%%" % progress

        if len(records) > 0:
            self.bulk_create(records)
            print "100%"

        return num_rows

class EnsemblTranscriptXref(Model):
    # N.B. the contents of this table were obtained from the public Ensembl database through the following command:
    # mysql -u anonymous -h ensembldb.ensembl.org homo_sapiens_core_84_38 -ss -r -e "SELECT transcript.stable_id as ensembl_id, xref.display_label as ext_id FROM transcript, object_xref, xref,external_db WHERE transcript.transcript_id = object_xref.ensembl_id AND object_xref.ensembl_object_type = 'Transcript' AND object_xref.xref_id = xref.xref_id AND xref.external_db_id = external_db.external_db_id AND external_db.db_name = 'RefSeq_mRNA'" > ensembl.txt
    ensembl_id = CharField(max_length=64)
    external_id = CharField(max_length=64)

    objects = EnsemblTranscriptXref_Manager()

    class Meta:
        db_table = u'ENSEMBL_TranscriptXref'


######################################
# Web services for the other modules
######################################


class WebService(Model):
    name = CharField(max_length=100)
   
    class Meta:
        verbose_name_plural = 'webservices'
        db_table = 'webservice'

    def __unicode__(self):
        return self.name

class Urls(Model):
    _url = CharField(max_length = 255, unique=True, db_column = 'url')
    available = BooleanField()
    id_webservice = ForeignKey(WebService, db_column='id_webservice')
    class Meta:
        verbose_name_plural = 'urls'
        db_table = 'url'
    def __unicode__(self):
        return self.url
    @property
    def url(self):
        if str(self._url).startswith('http'):
            return self._url
        else:
            return settings.DOMAIN_URL+self._url


######################################
# Temporary tables
######################################
class RnaSeqExpression(Model):
    case = CharField(max_length=10)
    gene_id = CharField(max_length=512)
    transcript_id = CharField(max_length=2048)
    length = FloatField()
    effective_length = FloatField()
    expected_count = FloatField()
    TPM = FloatField()
    FPKM = FloatField()
    class Meta:
        db_table = 'RnaSeqExpression'
