### GRAPH-BASED UTILITY FUNCTIONS
from py2neo import neo4j, node, rel
from django.conf import settings
from uuid import uuid4
import collections
from annotations.lib.utils import *
from Bio import Seq, SeqUtils
import json

neo4j._add_header('X-Stream', 'true;format=pretty')

#### labels ####
# -- nodes
BIOENTITY = 'Bioentity'
CHROMOSOME = 'chromosome'
GENE = 'gene'
TRANSCRIPT = 'transcript'
PEPTIDE = 'peptide'
EXON = 'exon'
INTRON = 'intron'
BASE = 'base'
WILD_TYPE = 'wild_type'
REGION = 'region'
TRANSCRIPT_REGION = 'transcript_region'
HOMOLOGOUS_REGION = 'homologous_region'
SEQUENCE_ALTERATION = 'sequence_alteration'
POINT_MUTATION = 'point_mutation'
DELETION = 'deletion'
INDEL = 'indel'
INSERTION = 'insertion'
INVERSION = 'inversion'
TRANSLOCATION = 'translocation'
COPY_NUMBER_VARIATION = 'copy_number_variation'
COPY_NUMBER_GAIN = 'copy_number_gain'
COPY_NUMBER_LOSS = 'copy_number_loss'
COPY_NUMBER_NEUTRAL = 'copy_number_neutral'
FEATURE_AMPLIFICATION = 'feature_amplification'
FEATURE_ABLATION = 'feature_ablation'
DUPLICATION = 'duplication'
SHORT_GENETIC_VARIATION = 'short_genetic_variation'
SNP = 'SNP'
MNP = 'MNP'
MICROSATELLITE = 'microsatellite'
SGV_INSERTION = 'sgv_insertion'
SGV_DELETION = 'sgv_deletion'
SGV_INDEL = 'sgv_indel'
KNOWLEDGE_BASE_NODE = 'kb_node'
RAW_DATA = 'raw_data'
ANALYSIS = 'analysis'
ANNOTATION = 'annotation'
PRIMER = 'primer'
PCR_PRODUCT = 'pcr_product'
SEQUENOM_TEST = 'sequenom_test'
FUSION_TRANSCRIPT = 'fusion_transcript'
FUSION_GENE = 'fusion_gene'
TREATMENT = 'treatment'
DRUG_RESPONSE = 'drug_response'
RTPCR_ASSAY = 'rtpcr_assay'
# -- relationships
PART_OF = 'part_of'
TRANSCRIBED_FROM = 'transcribed_from'
INTEGRAL_PART_OF = 'integral_part_of'
HAS_QUALITY = 'has_quality'
POSITION_OF = 'position_of'
IS_A = 'is_a'
CONTAINS = 'contains'
HOMOLOGOUS_TO = 'homologous_to'
SIMILAR_TO = 'similar_to'
HAS_ALTERATION = 'has_alteration'
HAS_SHORT_GENETIC_VARIATION = 'has_short_genetic_variation'
HAS_COPY_NUMBER_VARIATION = 'has_copy_number_variation'
HAS_WILD_TYPE = 'has_wild_type'
HAS_ANNOTATION = 'has_annotation'
HAS_REFERENCE = 'has_reference'
HAS_RAW_DATA = 'has_raw_data'
HAS_ANALYSIS = 'has_analysis'
ALIGNS_TO = 'aligns_to'
HAS_5P_END = 'has_5p_end'
HAS_PLUS_END = 'has_plus_end'
HAS_3P_END = 'has_3p_end'
HAS_MINUS_END = 'has_minus_end'
DETECTS = 'detects'
TRANSLATION_OF = 'translation_of'
HAS_FUSION_PARTNER = 'has_fusion_partner'
HAS_FUSION_BOUNDARY = 'has_fusion_boundary'
HAS_DRUG_RESPONSE = 'has_drug_response'
HAS_EXPRESSION_LEVEL = 'has_expression_level'
# -- prefixes
PREFIX_SEPARATOR = '_'
ANALYSIS_LABEL_PREFIX = 'A'
DRUG_RESPONSE_CRITERION_PREFIX = 'DRCr'
DRUG_RESPONSE_CLASS_PREFIX = 'DRCl'
#### end labels ####

##### N.B. IMPORTANT!!!
##### All queries that use the IN operator against a list that is a parameter must explicitly tell the cost-based optimizer to use the index
##### the (default) cost-based optimizer in that case does not use the schema indices
##### (unlike the rule-based optimiser, which does)

Gene = collections.namedtuple('Gene', 'uuid symbol strand chrom start end ac')

class GenomeGraphUtility(object):
    _aa_3L_to_1L = {    'Ala': 'A',
                        'Arg': 'R',
                        'Asn': 'N',
                        'Asp': 'D',
                        'Cys': 'C',
                        'Gln': 'Q',
                        'Glu': 'E',
                        'Gly': 'G',
                        'His': 'H',
                        'Ile': 'I',
                        'Leu': 'L',
                        'Lys': 'K',
                        'Met': 'M',
                        'Phe': 'F',
                        'Pro': 'P',
                        'Ser': 'S',
                        'Thr': 'T',
                        'Trp': 'W',
                        'Tyr': 'Y',
                        'Val': 'V'
                    }

    def __init__(self):
        self.gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
        return

    def getClosestNode(self, chrom, start, end):
        # input: region coordinates
        # output: label of nodes returned + list of corresponding regions (if any), or exons/genes/chromosomes containing the region
        try:
            chrom_node = self.gdb.get_indexed_node('node_auto_index', 'identifier', chrom)
            chrom_id = chrom_node._id
        except Exception, e:
            print e
            return None, []
        query_text = "match (r:region) where r.start[0] = { s } and r.end[1] = { e } with r start c=node("+str(chrom_id)+") match (r)-[*1..4]->(c) return r;"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(s=start,e=end)
        if len(res) > 0:
            return "region", [x[0] for x in res]
        else:
            query_text = "match (g:gene) where g.start[0] <= { s } and g.end[1] >= { e } with g start c=node("+str(chrom_id)+") match (g)-[:part_of]->(c) return g;"
            query = neo4j.CypherQuery(self.gdb, query_text)
            res = query.execute(s=start,e=end)
            if len(res) > 0:
                return "gene", [x[0] for x in res]
            else:
                return "chromosome", [chrom_node]

    def getGenomicLocationAnnotation(self, chrom, pos):
        # returns a list of items gene,exon*,transcript set* (* = optional)
        query_text = "match (g:gene) where g.chrom = { chrom } and g.start[0] <= { pos } and g.end[1] >= { pos } optional match (g)<-[:part_of]-(e:exon)-[r:integral_part_of]->(t:transcript) where e.chrom = { chrom } and e.start[0] <= { pos } and e.end[1] >= { pos } return g.ac,g.symbol,g.strand,g.start[0],g.end[1],e.ac,e.start[0],e.end[1],collect([r.exon_number,t.ac,t.start, t.end[1]])"
        query = neo4j.CypherQuery(self.gdb, query_text)

        if not isinstance(chrom, basestring):
            # force cast to string to match graph node attribute type
            chrom = str(chrom)
        else:
            if chrom.startswith('chr'):
                chrom = chrom.replace('chr', '')

        res = query.execute(chrom=chrom,pos=pos)
        result = []
        for row in res:
            result.append({ 'gene.ENS_ac': row[0],
                            'gene.symbol': row[1],
                            'gene.strand': row[2],
                            'gene.start': row[3],
                            'gene.end': row[4],
                            'exon.ENS_ac': row[5],
                            'exon.start': row[6],
                            'exon.end': row[7],
                            'transcript_set': [{'exon.no': t[0], 'transcript.ENS_ac': t[1], 'transcript.start': t[2], 'transcript.end': t[3]} for t in row[8]] if row[5] else []
                            })
        return result

    def getAllChromosomes(self):
        query_text = "match (c:chromosome) return c.uuid, c.chrom, c.start[0], c.end[1]"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute()
        return [(x[0], x[1], x[2], x[3]) for x in res]

    def getAllGenes(self):
        query_text = "match (g:gene) return g.uuid, g.symbol, g.strand, g.chrom, g.start[0], g.end[1], g.ac"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute()
        return [Gene(*x) for x in res]

    def getAllSequenceAlterations(self):
        q = "match (s:sequence_alteration) return s.uuid"
        query = neo4j.CypherQuery(self.gdb, q)
        res = query.execute()
        return res

    def getGenesInRegion(self, chrom, start, end):
        # returns genes that overlap the region (even partially)
        query_text = "match (g:gene) where g.chrom = { chrom } and g.start[0] <= { end } and g.end[1] >= { start } return g.uuid, g.symbol, g.ac, g.chrom, g.strand order by upper(g.symbol)"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(chrom=chrom,start=start,end=end)
        return res#return [(x[0], x[1], x[2]) for x in res]

    def getGenesInRegion_batch(self, l):
        # returns genes that overlap the region (even partially)
        query_text = "match (g:gene) where g.chrom = { chrom } and g.start[0] <= { end } and g.end[1] >= { start } return g.uuid, g.symbol, g.ac, g.chrom order by upper(g.symbol)"
        rbatch = neo4j.ReadBatch(self.gdb)
        for r in l:
            rbatch.append_cypher(query_text, {'chrom': r[0], 'start': r[1], 'end': r[2]})
        res = rbatch.submit()
        return res#return [(x[0], x[1], x[2]) for x in res]

    def getGenesWithExonsInRegion(self, chrom, start, end):
        # return genes whose coding region (exons) overlap (even partially) with the specified region
        query_text = "match (g:gene)<-[:transcribed_from]-(t:transcript)<-[:integral_part_of]-(e:exon) where e.chrom = { chrom } and e.start[0] < { end } and e.end[1] > { start } return distinct g.uuid, g.symbol, g.strand, g.chrom, g.start[0], g.end[1], g.ac"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(chrom=chrom,start=start,end=end)
        return [Gene(*x) for x in res]

    def getGenesByPrefix(self, prefix):
        query_text = "match (g:gene) where g.symbol =~ { prefix } return g.uuid, g.symbol, g.ac, g.chrom order by g.symbol limit 10"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(prefix = '(?i)'+prefix+'.*')
        return res

    def getTranscriptsByPrefix(self, prefix):
        query_text = "match (t:transcript) where t.ac =~ { prefix } return t.uuid, t.ac, t.chrom, t.start, t.end, t.strand, t.is_refseq, t.length, t.is_default order by t.ac limit 10"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(prefix = '(?i)'+prefix+'.*')
        return res

    def getSGVByPrefix(self, prefix):
        query_text = "match (sgv:short_genetic_variation)<-[:has_short_genetic_variation]-(r:region) where sgv.name =~ { prefix } and not(r:gene) return sgv.uuid, sgv.name, sgv.allele, sgv.alt, r.chrom, r.start[0], r.end[1], sgv.strand order by sgv.name limit 10"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(prefix = '(?i)'+prefix+'.*')
        return res#return [(x[0], x[1], x[2], x[3]) for x in res]

    def getOrCreateHomologousRegion(self, region_uuid):
        query_text = "match (r:kb_node:region {uuid: { r_uuid }})<-[:contains]-(hr:homologous_region) return hr.uuid"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(r_uuid=region_uuid)
        if len(res) > 0:
            return res[0][0]
        uuid = self._getNewUUID()
        query_text = "match (r:kb_node:region {uuid: { r_uuid }}) create (hr:kb_node:region:homologous_region {uuid: { hr_uuid }, chrom: r.chrom, start: r.start, end: r.end, strand: r.strand}), (hr)-[:contains]->(r)"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(r_uuid=region_uuid, hr_uuid=uuid)
        return uuid

    def updateHomologousRegionCoordinates(self, hr_uuid, r_uuid):
        query_text = "match (hr:kb_node:region:homologous_region {uuid: { hr_uuid }}), (r:kb_node:region {uuid: { r_uuid }}), (hr)-[rr:contains]->(r) set hr.chrom = r.chrom, hr.start = r.start, hr.end = r.end, hr.strand = r.strand return hr.uuid, id(rr), r.uuid"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(hr_uuid=hr_uuid, r_uuid=r_uuid)
        if len(res) > 0:
            return True
        else:
            return False

    def linkRegionToHomologousRegion(self, r_uuid, hr_uuid):
        print "r_uuid, hr_uuid", r_uuid, hr_uuid
        r_info, hr_info = self.getRegionInfo_byUuid([r_uuid, hr_uuid])
        if r_info['r.end'][1] - r_info['r.start'][0] != hr_info['r.end'][1] - hr_info['r.start'][0]:
            raise Exception("Regions have different sizes, cannot proceed")
        query_text = "match (r:kb_node:region {uuid: { r_uuid }}), (hr:kb_node:region:homologous_region {uuid: { hr_uuid }}) merge (hr)-[:contains]->(r)"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(r_uuid=r_uuid, hr_uuid=hr_uuid)
        return True

    def isHomologousRegion(self, region_uuid):
        query_text = "match (r:kb_node:region {uuid: { uuid }}) where (r:homologous_region) return r.uuid"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=region_uuid)
        if len(res) > 0:
            return True
        else:
            return False

    def getContainedRegionsFromHomologousRegion(self, hr_uuid):
        query_text = "match (hr:kb_node:region:homologous_region {uuid: { hr_uuid }})-[:contains]->(r:region) return r.uuid as uuid, r.chrom as chrom, r.start[0] as start, r.end[1] as end, r.strand as strand"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(hr_uuid=hr_uuid)
        return [{k:x[k] for k in x.columns} for x in res]

    def deleteRegionFromHomologousRegion(self, r_uuid, hr_uuid):
        query_text = "match (r:kb_node:region {uuid: { r_uuid }}), (hr:kb_node:region:homologous_region {uuid: { hr_uuid }}), (hr)-[x:contains]->(r) delete x return r.uuid"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(r_uuid=r_uuid, hr_uuid=hr_uuid)
        if len(res) > 0:
            return True
        else:
            return False

    def deleteHomologousRegion(self, hr_uuid):
        # it may only be deleted when nothing but included regions are linked to it, otherwise the operation will fail!
        query_text = "match (hr:kb_node:region:homologous_region {uuid: { uuid }})-[x]-(y) where type(x) <> 'contains' return count(x)"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=hr_uuid)
        if res[0][0] > 0:
            raise Exception("Cannot delete, homologous region still has relationships")
        query_text = "match (hr:kb_node:region:homologous_region {uuid: { uuid }})-[x:contains]-(y) delete x,hr"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=hr_uuid)

    def createSGVProbe(self, sgv_uuid, probe_name):
        query_text = "match (sgv:kb_node:short_genetic_variation {uuid: { sgv_uuid }}) return sgv.uuid"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(sgv_uuid=sgv_uuid)
        if len(res) == 0:
            return None
        probe_uuid = self._getNewUUID()
        query_text = "match (sgv:kb_node:short_genetic_variation {uuid: { sgv_uuid }}) create (p:kb_node:"+SEQUENOM_TEST+" {uuid: { probe_uuid }, name: { probe_name }})-[:detects]->(sgv)"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(sgv_uuid=sgv_uuid,probe_uuid=probe_uuid,probe_name=probe_name)
        return probe_uuid

    def deleteSGVProbe(self, sgv_uuid):
        query_text = "match (s:" + SEQUENOM_TEST + " {uuid: { uuid }})-[r]-() delete r, s"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=sgv_uuid)
        return

    def getSGVProbeBySGVPrefix(self, prefix):
        query_text = "match (sgv:short_genetic_variation)<-[:has_short_genetic_variation]-(r:region) where sgv.name =~ { prefix } and not(r:gene) match (sgv)<-[:detects]-(probe:"+SEQUENOM_TEST+") return probe.uuid as uuid, sgv.name as name, head(filter(l in labels(sgv) where l in ['SNP', 'sgv_indel', 'microsatellite', 'MNP', 'sgv_insertion', 'sgv_deletion'])) as class, sgv.allele as allele, sgv.alt as alt, r.chrom as chrom, r.start[0] as start, r.end[1] as end, sgv.strand as strand order by sgv.name, sgv.allele limit 10"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(prefix = '(?i)'+prefix+'.*')
        return res#return [(x[0], x[1], x[2], x[3]) for x in res]

    def getSGVProbeByUuid_list(self, uuid_list):
        query_text = "match (probe:kb_node:"+SEQUENOM_TEST+")-[:detects]->(sgv:kb_node:short_genetic_variation)<-[:has_short_genetic_variation]-(r:region) using index probe:kb_node(uuid) where probe.uuid in { uuid_list } and not(r:gene) return probe.uuid as uuid, probe.name as probe_name, sgv.uuid as snp_uuid, sgv.name as name, head(filter(l in labels(sgv) where l in ['SNP', 'sgv_indel', 'microsatellite', 'MNP', 'sgv_insertion', 'sgv_deletion'])) as class, sgv.allele as allele, sgv.alt as alt, r.chrom as chrom, r.start[0] as start, r.end[1] as end, sgv.strand as strand order by sgv.name, sgv.allele"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid_list=uuid_list)
        return res

    def getSGVProbeFromSGVUuid_list(self, uuid_list):
        query_text = "match (probe:kb_node:"+SEQUENOM_TEST+")-[:detects]->(sgv:kb_node:short_genetic_variation) using index sgv:kb_node(uuid) where sgv.uuid in { uuid_list } return probe.uuid as uuid, probe.name as probe_name, sgv.uuid as snp_uuid order by probe.name"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid_list=uuid_list)
        return res

    def getSGVProbeBySGVUuid(self, sgv_uuid):
        query_text = "match (probe:kb_node:"+SEQUENOM_TEST+")-[:detects]->(sgv:kb_node:short_genetic_variation)<-[:has_short_genetic_variation]-(r:region) where sgv.uuid = { sgv_uuid } and not(r:gene) return probe.uuid as uuid, probe.name as probe_name, sgv.uuid as snp_uuid, sgv.name as name, head(filter(l in labels(sgv) where l in ['SNP', 'sgv_indel', 'microsatellite', 'MNP', 'sgv_insertion', 'sgv_deletion'])) as class, sgv.allele as allele, sgv.alt as alt, r.chrom as chrom, r.start[0] as start, r.end[1] as end, sgv.strand as strand order by sgv.name, sgv.allele"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(sgv_uuid=sgv_uuid)
        return res

    def getSGVinSGVProbeByUuid_list(self, uuid_list):
        query_text = "match (probe:kb_node:"+SEQUENOM_TEST+")-[:detects]->(sgv:kb_node:short_genetic_variation)<-[:has_short_genetic_variation]-(r:region) using index probe:kb_node(uuid) where probe.uuid in { uuid_list } and not(r:gene) optional match (sgv)<-[:has_short_genetic_variation]-(g:gene) where g.start[0] <= r.start[0] and g.end[1] >= r.end[1] with probe, sgv, r, head(collect(g)) as g return probe.uuid as probe_uuid, sgv.uuid as uuid, sgv.name as name, head(filter(l in labels(sgv) where l in ['SNP', 'sgv_indel', 'microsatellite', 'MNP', 'sgv_insertion', 'sgv_deletion'])) as labels, sgv.allele as allele, sgv.alt as alt, r.chrom as chrom, r.start[0] as start, r.end[1] as end, sgv.strand as strand, sgv.popul_freq as freq, sgv.num_repeats as num_repeats, g.symbol as gene_symbol, g.ac as gene_ac, g.uuid as gene_uuid, sgv.x_ref as x_ref, r.uuid as region_uuid, case length(filter(x in labels(r) where x = 'homologous_region')) when 1 then true else false end as multi_region order by sgv.name, sgv.allele;"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid_list=uuid_list)
        return res

    def getCodingTranscriptsForGene(self, gene_uuid):
        # query only returns coding transcript
        query_text = "match (g:kb_node:gene)<-[:transcribed_from]-(t:transcript) where g.uuid = { gene_uuid } and has(t.cds_start) with t match (t)<-[:integral_part_of]-(e:exon) return t.uuid, t.ac, count(e) as num_exons, t.is_refseq"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(gene_uuid = gene_uuid)
        return [(x[0], x[1], x[2], x[3]) for x in res]

    def getTranscriptsForGene(self, gene_uuid):
        query_text = "match (g:kb_node:gene)<-[:transcribed_from]-(t:transcript) where g.uuid = { gene_uuid } with t match (t)<-[:integral_part_of]-(e:exon) return t.uuid, t.ac, count(e) as num_exons, t.is_refseq"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(gene_uuid = gene_uuid)
        return [(x[0], x[1], x[2], x[3]) for x in res]

    def findDefaultTranscript(self, all_tx):
        best_nonRefseq = {'uuid': None, 'ac': None, 'num': 0}
        best_refseq = {'uuid': None, 'ac': None, 'num': 0}
        for tx in all_tx:
            if tx[3] == True:
                if tx[2] > best_refseq['num']:
                    best_refseq = {'uuid': tx[0], 'ac': tx[1], 'num': tx[2]}
            else:
                if tx[2] > best_nonRefseq['num']:
                    best_nonRefseq = {'uuid': tx[0], 'ac': tx[1], 'num': tx[2]}
        if best_refseq['num']:
            return {'refSeq': True, 'uuid': best_refseq['uuid'], 'ac': best_refseq['ac']}
        elif best_nonRefseq['num']:
            return {'refSeq': False, 'uuid': best_nonRefseq['uuid'], 'ac': best_nonRefseq['ac']}
        else:
            return {}

    def setDefaultTranscriptForGene(self, gene_ac=None, gene_uuid=None, tx_ac=None, tx_uuid=None):
        data = {}
        if gene_ac is not None:
            gene_query = "{ac: { gene_ac }}"
            data['gene_ac'] = gene_ac
        elif gene_uuid is not None:
            gene_query = "{uuid: { gene_uuid }}"
            data['gene_uuid'] = gene_uuid
        else:
            raise Exception("One of the following parameters must be specified: gene_ac, gene_uuid")
        
        if tx_ac is not None:
            tx_query = "{ac: { tx_ac }}"
            data['tx_ac'] = tx_ac
        elif tx_uuid is not None:
            tx_query = "{uuid: { tx_uuid }}"
            data['tx_uuid'] = tx_uuid
        else:
            raise Exception("One of the following parameters must be specified: tx_ac, tx_uuid")

        query_text = "optional match (:kb_node:gene " + gene_query + ")<-[:transcribed_from]-(t1:transcript {is_default: true}) optional match (:kb_node:gene " + gene_query + ")<-[:transcribed_from]-(t2:transcript " + tx_query + ") foreach (a in case when t1 is null or t2 is null then [] else [t1] end | remove a.is_default) foreach (b in case when t2 is null then [] else [t2] end | set b.is_default=true)"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(**data)
        
        return

    def getDefaultTranscriptForGene(self, gene_ac=None, gene_uuid=None, gene_symbol=None):
        data = {}
        if gene_ac is not None:
            gene_query = "{ac: { gene_ac }}"
            data['gene_ac'] = gene_ac
        elif gene_uuid is not None:
            gene_query = "{uuid: { gene_uuid }}"
            data['gene_uuid'] = gene_uuid
        elif gene_symbol is not None:
            gene_query = "{symbol: { gene_symbol }}"
            data['gene_symbol'] = gene_symbol
        else:
            raise Exception("One of the following must be specified: gene_ac, gene_uuid")
        query_text = "match (g:kb_node:gene " + gene_query + ")<-[:transcribed_from]-(t:kb_node:transcript) where t.is_default = true return t.uuid as uuid, t.ac as ac, t.is_refseq as refSeq, g.uuid as gene_uuid, g.symbol as gene_symbol"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(**data)
        if len(res) > 0:
            return res[0]
        else:
            return None

    def setCodingCoordinatesForRegion(self, region_uuid, ref, start_c_base, start_c_offset, start_c_datum, end_c_base, end_c_offset, end_c_datum, loc_p):
        try:
            query_text = "match (r:kb_node:region) where r.uuid = { uuid } set r.ref = { ref }, r.start_c_base = { start_c_base }, r.start_c_offset = { start_c_offset }, r.start_c_datum = { start_c_datum }, r.end_c_base = { end_c_base }, r.end_c_offset = { end_c_offset }, r.end_c_datum = { end_c_datum }, r.loc_p = { loc_p }"
            query = neo4j.CypherQuery(self.gdb, query_text)
            query.execute(uuid=region_uuid, ref=ref, start_c_base=start_c_base, start_c_offset=start_c_offset, start_c_datum=start_c_datum, end_c_base=end_c_base, end_c_offset=end_c_offset, end_c_datum=end_c_datum, loc_p=loc_p)
            return True
        except Exception as e:
            print "[setCodingCoordinatesForRegion] ", str(e)
            return False

    def getExonsForTranscript(self, tx_uuid):
        query_text = "match (t:kb_node:transcript)<-[r:integral_part_of]-(e:exon) where t.uuid = { tx_uuid } return e.uuid, r.exon_number, e.end[1]-e.start[0]+1 as exon_length order by r.exon_number"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(tx_uuid = tx_uuid)
        return [(x[0], x[1], x[2]) for x in res]

    # obsolete
    def getSequenceAlterationsInGene(self, gene_uuid, tx_uuid=None, exon_uuid=None, cds_only=False):
        if exon_uuid is not None:
            query_text = "match (g:kb_node:gene {uuid: { gene_uuid }})-[:has_alteration]->(a:sequence_alteration)<-[:has_alteration]-(r:region), (t:kb_node:transcript {uuid: { tx_uuid }})<-[i:integral_part_of]-(e:kb_node:exon {uuid: { exon_uuid }}) where e.start[0] <= r.start[0] and e.end[1] >= r.end[1] return distinct a.uuid, r.chrom, r.start[0], r.end[1], a.alt, a.num_bases, labels(a) as alt_type, g.strand, i.exon_number, g.symbol, t.ac, s.num_bases_c, s.x_ref"
        elif tx_uuid is not None:
            query_text = "match (g:kb_node:gene {uuid: { gene_uuid }})-[:has_alteration]->(a:sequence_alteration)<-[:has_alteration]-(r:region), (t:kb_node:transcript {uuid: { tx_uuid }})<-[i:integral_part_of]-(e) where e.start[0] <= r.start[0] and e.end[1] >= r.end[1] return distinct a.uuid, r.chrom, r.start[0], r.end[1], a.alt, a.num_bases, labels(a) as alt_type, g.strand, i.exon_number, g.symbol, t.ac, s.num_bases_c, s.x_ref"
        else:
            if cds_only == False:
                query_text = "match (g:kb_node:gene {uuid: { gene_uuid }})-[:has_alteration]->(a:sequence_alteration)<-[:has_alteration]-(r:region) return distinct a.uuid, r.chrom, r.start[0], r.end[1], a.alt, a.num_bases, labels(a) as alt_type, g.strand, null as exon_number, g.symbol, null as tx_ac, s.num_bases_c, s.x_ref"
            else:
                query_text = "match (g:kb_node:gene {uuid: { gene_uuid }})-[:has_alteration]->(a:sequence_alteration)<-[:has_alteration]-(r:region), (g)<-[:part_of]-(e:exon) where e.start[0] <= r.start[0] and e.end[1] >= r.end[1] return distinct a.uuid, r.chrom, r.start[0], r.end[1], a.alt, a.num_bases, labels(a) as alt_type, g.strand, null as exon_number, g.symbol, null as tx_ac, s.num_bases_c, s.x_ref"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(gene_uuid=gene_uuid, tx_uuid = tx_uuid, exon_uuid=exon_uuid)
        return res#[(x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8]) for x in res]

    def getSequenceAlterationsByPosition(self, chrom=None, start=None, end=None, gene_uuid=None, tx_uuid=None, limit=500):
        match_clause = ["(s:sequence_alteration)", "(s)<-[:has_alteration]-(r:region)"]
        optional_match_clause = []
        where_clause = ["not(r:gene)"]
        if gene_uuid is not None:
            match_clause.append("(s)<-[:has_alteration]-(g:gene {uuid: { gene_uuid }})")
        elif tx_uuid is None:
            optional_match_clause.append("(s)<-[:has_alteration]-(g:gene)")
        if tx_uuid is not None:
            match_clause.append("(s)<-[:has_alteration]-(t:transcript {uuid: { tx_uuid }})")
            if gene_uuid is None:
                match_clause.append("(t)-[:transcribed_from]->(g:gene)")
        else:
            optional_match_clause.append("(g)<-[:transcribed_from]-(t:transcript {is_default: true})")
        if chrom is not None:
            chrom = str(chrom)
            where_clause.append("r.chrom = { chrom }")
        if start is not None:
            start = long(start)
            where_clause.append("r.start[0] >= { start }")
        if end is not None:
            end = long(end)
            where_clause.append("r.end[1] <= { end }")
        return_clause = "return s.uuid, r.chrom, r.start[0], r.end[1], labels(s), r.ref, 'p.' + r.loc_p, s.alt, s.alt_p, s.num_bases, s.num_bases_c, r.start_c_base, r.start_c_offset, r.end_c_base, r.end_c_offset, g.uuid, g.symbol, g.ac, g.strand, t.ac, r.start_c_datum, r.end_c_datum, s.x_ref"
        query_text = "match " + ", ".join(match_clause) + " " + \
                    ("where " if len(where_clause) > 0 else "") + " and ".join(where_clause) + " " + \
                    ("optional match " if len(optional_match_clause) > 0 else "") + ", ".join(optional_match_clause) + " " + \
                    return_clause + " " + \
                    (("limit %d" % limit) if (isinstance(limit, (int, long)) and limit is not None) else "")
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(chrom=chrom,start=start,end=end,gene_uuid=gene_uuid,tx_uuid=tx_uuid)
        return res

    def getAlterationSitesInGene(self, gene_uuid, tx_uuid=None, exon_uuid=None, cds_only=False):
        # N.B. when a transcript is provided, the query ensures that only sites contained within exons included in the transcript
        # are returned. However, the c_start, c_offset and loc_p fields of the site are *not* with reference to the transcript provided, but to
        # the default one
        if exon_uuid is not None:
            query_text = "match (g:kb_node:gene {uuid: { gene_uuid }})<-[:part_of]-(r:region)-[:has_alteration]->(a:sequence_alteration), (t:kb_node:transcript {uuid: { tx_uuid }})<-[i:integral_part_of]-(e:kb_node:exon {uuid: { exon_uuid }}) where e.start[0] <= r.start[0] and e.end[1] >= r.end[1] return distinct r.uuid, r.chrom, r.start[0], r.end[1], g.strand, i.exon_number, g.symbol, t.ac, r.ref, r.c_start, r.c_offset, 'p.' + r.loc_p"
        elif tx_uuid is not None:
            query_text = "match (g:kb_node:gene {uuid: { gene_uuid }})<-[:part_of]-(r:region)-[:has_alteration]->(a:sequence_alteration), (t:kb_node:transcript {uuid: { tx_uuid }})<-[i:integral_part_of]-(e:exon) where e.start[0] <= r.start[0] and e.end[1] >= r.end[1] return distinct r.uuid, r.chrom, r.start[0], r.end[1], g.strand, i.exon_number, g.symbol, t.ac, r.ref, r.c_start, r.c_offset, 'p.' + r.loc_p"
        else:
            if cds_only == False:
                query_text = "match (g:kb_node:gene {uuid: { gene_uuid }})<-[:part_of]-(r:region)-[:has_alteration]->(a:sequence_alteration) return distinct r.uuid, r.chrom, r.start[0], r.end[1], g.strand, null as exon_number, g.symbol, null as tx_ac, r.ref, r.c_start, r.c_offset, 'p.' + r.loc_p"
            else:
                query_text = "match (g:kb_node:gene {uuid: { gene_uuid }})<-[:part_of]-(r:region)-[:has_alteration]->(a:sequence_alteration), (g)<-[:part_of]-(e:exon) where e.start[0] <= r.start[0] and e.end[1] >= r.end[1] return distinct r.uuid, r.chrom, r.start[0], r.end[1], g.strand, null as exon_number, g.symbol, null as tx_ac, r.ref, r.c_start, r.c_offset, 'p.' + r.loc_p"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(gene_uuid=gene_uuid, tx_uuid = tx_uuid, exon_uuid=exon_uuid)
        return res#[(x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8]) for x in res]

    def getSequenceAlterationByUuid(self, uuid):
        query_text = "match (s:sequence_alteration {uuid: { uuid }})<-[:has_alteration]-(r:region) where not (r:gene) optional match (s)<-[:has_alteration]-(g:gene)<-[:transcribed_from]-(t:transcript {is_default: true}) return s.uuid, r.chrom, r.start[0], r.end[1], labels(s), r.ref, 'p.' + r.loc_p, s.alt, s.alt_p, s.num_bases, s.num_bases_c, r.start_c_base, r.start_c_offset, r.end_c_base, r.end_c_offset, g.uuid, g.symbol, g.ac, g.strand, t.ac, r.start_c_datum, r.end_c_datum, s.x_ref"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        return res

    def getSequenceAlterationByUuid_list(self, uuid_list):
        query_text = "match (s:kb_node:sequence_alteration)<-[:has_alteration]-(r:region) using index s:kb_node(uuid) where not (r:gene)  and s.uuid in { uuid_list } optional match (s)<-[:has_alteration]-(g:gene)<-[:transcribed_from]-(t:transcript {is_default: true}) return s.uuid, r.chrom, r.start[0], r.end[1], labels(s), r.ref, 'p.' + r.loc_p, s.alt, s.alt_p, s.num_bases, s.num_bases_c, r.start_c_base, r.start_c_offset, r.end_c_base, r.end_c_offset, g.uuid, g.symbol, g.ac, g.strand, t.ac, r.start_c_datum, r.end_c_datum, s.x_ref"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid_list=uuid_list)
        return res

    def getSequenceAlterationByCosmicId(self, cosm):
        query_text = "match (s:sequence_alteration)<-[:has_alteration]-(r:region) where { cosm } in s.x_ref and not (r:gene) optional match (s)<-[:has_alteration]-(g:gene)<-[:transcribed_from]-(t:transcript {is_default: true}) return s.uuid, r.chrom, r.start[0], r.end[1], s.alt, s.num_bases, labels(s), g.uuid, g.symbol, g.ac, r.ref, r.c_start, r.c_offset, 'p.' + r.loc_p, g.strand, s.alt_p, t.ac, s.num_bases_c, s.x_ref"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(cosm=cosm)
        return res

    def setSequenceAlterationProperties(self, uuid, **params):
        if len(params) == 0:
            return
        query_text = "match (s:sequence_alteration {uuid: { uuid }}) "
        for k,v in params.iteritems():
            query_text += 'set s.{k} = {{ {k} }} '.format(k=k)
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid, **params)
    
    def getPrimerByUuid(self, uuid):
        query_text = """
        match (s:kb_node:primer {uuid: { uuid }})-[:aligns_to]->(r)
        where (r:region or r:transcript_region)
        optional match (r)-[:part_of]->(g:gene)
        optional match (r)-[:part_of]->(c:chromosome)
        optional match (r)-[:part_of]->(t:transcript)-[:transcribed_from]->(gg:gene)
        return s.uuid,
        s.name,
        s.length,
        collect([r.uuid, case when g:gene or g:chromosome then r.chrom when t:transcript then r.tx_ac end, r.start[0], r.end[1], r.strand, case when g:gene then g.symbol when t:transcript then gg.symbol end, case when g:gene or g:chromosome then 'genome' when t:transcript then 'transcriptome' end]) as alignments"""
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        return res

    def getPrimerByUuidList(self, uuid_list):
        query_text = """
        match (s:kb_node:primer)
        using index s:kb_node(uuid)
        where s.uuid in { uuid_list }
        optional match (s)-[:aligns_to]->(r)-[:part_of]->(g)-[tt:transcribed_from*0..1]->(gg)
        where (r:region and (g:gene or g:chromosome) and g = gg) or (r:transcript_region and g:transcript and gg:gene)
        return s.uuid,
        s.name,
        s.length,
        collect([r.uuid, case when g:gene or g:chromosome then "chr"+r.chrom when g:transcript then r.tx_ac end, r.start[0], r.end[1], r.strand, case when g:gene then g.symbol when g:transcript then gg.symbol end, case when g:gene or g:chromosome then 'genome' when g:transcript then 'transcriptome' end]) as alignments"""
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid_list=uuid_list)
        return res

    def getPrimerInGene(self, gene_uuid, label=None):
        query_text = """
        match (gg:kb_node:gene {uuid: { gene_uuid }})<-[tt:transcribed_from*0..1]-(g)<-[:part_of]-(r)<-[:aligns_to]-(s:kb_node:primer%s)
        where (r:region and g:gene and g = gg) or (r:transcript_region and g:transcript)
        return s.uuid,
        s.name,
        s.length,
        collect([r.uuid, case when g:gene or g:chromosome then "chr"+r.chrom when g:transcript then r.tx_ac end, r.start[0], r.end[1], r.strand, case when g:gene then g.symbol when g:transcript then gg.symbol end, case when g:gene or g:chromosome then 'genome' when g:transcript then 'transcriptome' end]) as alignments""" % ((":" + label) if label else "")
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(gene_uuid=gene_uuid)
        return res

    def getPrimerByAlignmentUuid(self, uuid):
        query_text = "match (r:kb_node {uuid: { uuid }})<-[:aligns_to]-(s:primer) where (r:region or r:transcript_region) optional match (r)-[:part_of]->(g)-[tt:transcribed_from*0..1]->(gg) where (r:region and (g:gene or g:chromosome) and g = gg) or (r:transcript_region and g:transcript and gg:gene) return s.uuid, s.name, s.length, collect([r.uuid, case when g:gene or g:chromosome then r.chrom when g:transcript then r.tx_ac end, r.start[0], r.end[1], r.strand, case when g:gene then g.symbol when g:transcript then gg.symbol end, case when g:gene or g:chromosome then 'genome' when g:transcript then 'transcriptome' end]) as alignments"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        return res

    def getPCRProductTechnologies(self, uuid):
        query_text = "match (pcrp:kb_node:pcr_product {uuid: { uuid }}) return filter(l in labels(pcrp) where not(l in ['kb_node', 'pcr_product'])) as labels"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        return res

    def getAllPCRProducts(self):
        query_text = """match
        (pcrp:kb_node:pcr_product)-[:aligns_to]->(r),
        (pcrp)-[has1:has_5p_end|has_plus_end]->(r1)<-[:aligns_to]-(p1:primer),
        (p1)-[:generates]->(pcrp),
        (pcrp)-[has2:has_3p_end|has_minus_end]->(r2)<-[:aligns_to]-(p2:primer),
        (p2)-[:generates]->(pcrp)
where
        (r:region or r:transcript_region) and (r1:region or r1:transcript_region) and (r2:region or r2:transcript_region)
optional match
        (r)-[:part_of]->(g:gene)
optional match
        (r)-[:part_of]->(c:chromosome)
optional match
        (r)-[:part_of]->(t:transcript)-[:transcribed_from]->(gg:gene)
return
        pcrp.uuid as pcrp_uuid,
        pcrp.name as pcrp_name,
        pcrp.length as pcrp_length,
        case when g:gene or c:chromosome then "chr" + r.chrom when t:transcript then r.tx_ac end as a_ref,
        r.start[0] as r_start,
        r.end[1] as r_end,
        collect(case when g:gene then g.uuid when t:transcript then gg.uuid end) as a_gene_uuid,
        collect(case when g:gene then g.symbol when t:transcript then gg.symbol end) as a_gene_symbol,
        p1.name as p1_name,
        p1.length as p1_length,
        case when type(has1)="has_plus_end" then "chr" + r1.chrom when type(has1)="has_5p_end" then r1.tx_ac end as p1_ref,
        r1.start[0] as r1_start,
        r1.end[1] as r1_end,
        p2.name as p2_name,
        p2.length as p2_length,
        case when type(has2)="has_minus_end" then "chr" + r2.chrom when type(has2)="has_3p_end" then r2.tx_ac end as p2_ref,
        r2.start[0] as r2_start,
        r2.end[1] as r2_end,
        case when r:region then "gDNA" when r:transcript_region then "cDNA" end as a_type,
        r.uuid as align_region_uuid
union

match
        (pcrp:kb_node:pcr_product)-[:aligns_to]->(r),
        (pcrp)<-[:generates]-(:rtpcr_assay)
optional match
        (r)-[:part_of]->(g:gene)
optional match
        (r)-[:part_of]->(c:chromosome)
optional match
        (r)-[:part_of]->(t:transcript)-[:transcribed_from]->(gg:gene)
return
        pcrp.uuid as pcrp_uuid,
        pcrp.name as pcrp_name,
        pcrp.length as pcrp_length,
        case when g:gene or c:chromosome then "chr" + r.chrom when t:transcript then r.tx_ac end as a_ref,
        r.start[0] as r_start,
        r.end[1] as r_end,
        collect(case when g:gene then g.uuid when t:transcript then gg.uuid end) as a_gene_uuid,
        collect(case when g:gene then g.symbol when t:transcript then gg.symbol end) as a_gene_symbol,
        null as p1_name,
        null as p1_length,
        null as p1_ref,
        null as r1_start,
        null as r1_end,
        null as p2_name,
        null as p2_length,
        null as p2_ref,
        null as r2_start,
        null as r2_end,
        case when r:region then "gDNA" when r:transcript_region then "cDNA" end as a_type,
        r.uuid as align_region_uuid
"""
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute()
        return res

    def getPCRProductByUuidList(self, uuid_list):
        query_text = """match
        (pcrp:kb_node:pcr_product)-[:aligns_to]->(r),
        (pcrp)-[has1:has_5p_end|has_plus_end]->(r1)<-[:aligns_to]-(p1:primer),
        (p1)-[:generates]->(pcrp),
        (pcrp)-[has2:has_3p_end|has_minus_end]->(r2)<-[:aligns_to]-(p2:primer),
        (p2)-[:generates]->(pcrp)
        using index pcrp:kb_node(uuid)
        where pcrp.uuid in { uuid_list } and (r:region or r:transcript_region) and (r1:region or r1:transcript_region) and (r2:region or r2:transcript_region)
optional match
        (r)-[:part_of]->(g:gene)
optional match
        (r)-[:part_of]->(c:chromosome)
optional match
        (r)-[:part_of]->(t:transcript)-[:transcribed_from]->(gg:gene)
return
        pcrp.uuid as pcrp_uuid,
        pcrp.name as pcrp_name,
        pcrp.length as pcrp_length,
        case when g:gene or c:chromosome then "chr" + r.chrom when t:transcript then r.tx_ac end as a_ref,
        r.start[0] as r_start,
        r.end[1] as r_end,
        collect(case when g:gene then g.uuid when t:transcript then gg.uuid end) as a_gene_uuid,
        collect(case when g:gene then g.symbol when t:transcript then gg.symbol end) as a_gene_symbol,
        p1.name as p1_name,
        p1.length as p1_length,
        case when type(has1)="has_plus_end" then "chr" + r1.chrom when type(has1)="has_5p_end" then r1.tx_ac end as p1_ref,
        r1.start[0] as r1_start,
        r1.end[1] as r1_end,
        p2.name as p2_name,
        p2.length as p2_length,
        case when type(has2)="has_minus_end" then "chr" + r2.chrom when type(has2)="has_3p_end" then r2.tx_ac end as p2_ref,
        r2.start[0] as r2_start,
        r2.end[1] as r2_end,
        case when r:region then "gDNA" when r:transcript_region then "cDNA" end as a_type,
        r.uuid as align_region_uuid
union

match
        (pcrp:kb_node:pcr_product)-[:aligns_to]->(r),
        (pcrp)<-[:generates]-(:rtpcr_assay)
using index pcrp:kb_node(uuid)
where
        pcrp.uuid in { uuid_list } and (r:region or r:transcript_region)
optional match
        (r)-[:part_of]->(g:gene)
optional match
        (r)-[:part_of]->(c:chromosome)
optional match
        (r)-[:part_of]->(t:transcript)-[:transcribed_from]->(gg:gene)
return
        pcrp.uuid as pcrp_uuid,
        pcrp.name as pcrp_name,
        pcrp.length as pcrp_length,
        case when g:gene or c:chromosome then "chr" + r.chrom when t:transcript then r.tx_ac end as a_ref,
        r.start[0] as r_start,
        r.end[1] as r_end,
        collect(case when g:gene then g.uuid when t:transcript then gg.uuid end) as a_gene_uuid,
        collect(case when g:gene then g.symbol when t:transcript then gg.symbol end) as a_gene_symbol,
        null as p1_name,
        null as p1_length,
        null as p1_ref,
        null as r1_start,
        null as r1_end,
        null as p2_name,
        null as p2_length,
        null as p2_ref,
        null as r2_start,
        null as r2_end,
        case when r:region then "gDNA" when r:transcript_region then "cDNA" end as a_type,
        r.uuid as align_region_uuid"""
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid_list=uuid_list)
        return res

    def getPCRProductInGene(self, uuid, label):
        query_text = """match
        (gg)<-[tt:transcribed_from*0..1]-(g)<-[:part_of]-(r)<-[:aligns_to]-(pcrp:kb_node:pcr_product:"""+label+"""),
        (pcrp)-[has1:has_5p_end|has_plus_end]->(r1)<-[:aligns_to]-(p1:primer),
        (p1)-[:generates]->(pcrp),
        (pcrp)-[has2:has_3p_end|has_minus_end]->(r2)<-[:aligns_to]-(p2:primer),
        (p2)-[:generates]->(pcrp)
        where (g:gene and g.uuid = { uuid } and g = gg and r:region) or (gg:gene and gg.uuid =  { uuid } and g:transcript and r:transcript_region)
        return  pcrp.uuid as pcrp_uuid,
        pcrp.name as pcrp_name,
        pcrp.length as pcrp_length,
        case when g:gene then "chr" + r.chrom when g:transcript then r.tx_ac end as a_ref,
        r.start[0] as r_start,
        r.end[1] as r_end,
        case when g:gene then [g.uuid] when g:transcript then [gg.uuid] end as a_gene_uuid,
        case when g:gene then [g.symbol] when g:transcript then [gg.symbol] end as a_gene_symbol,
        p1.name as p1_name,
        p1.length as p1_length,
        case when type(has1)="has_plus_end" then "chr" + r1.chrom when type(has1)="has_5p_end" then r1.tx_ac end as p1_ref,
        r1.start[0] as r1_start,
        r1.end[1] as r1_end,
        p2.name as p2_name,
        p2.length as p2_length,
        case when type(has2)="has_minus_end" then "chr" + r2.chrom when type(has2)="has_3p_end" then r2.tx_ac end as p2_ref,
        r2.start[0] as r2_start,
        r2.end[1] as r2_end,
        case when r:region then "gDNA" when r:transcript_region then "cDNA" end as a_type,
        r.uuid as align_region_uuid

union

match
        (gg)<-[tt:transcribed_from*0..1]-(g)<-[:part_of]-(r)<-[:aligns_to]-(pcrp:kb_node:pcr_product:"""+label+"""),
        (a:rtpcr_assay)-[:generates]->(pcrp)
        where (g:gene and g.uuid = { uuid } and g = gg and r:region) or (gg:gene and gg.uuid =  { uuid } and g:transcript and r:transcript_region)
        return  pcrp.uuid as pcrp_uuid,
        pcrp.name as pcrp_name,
        pcrp.length as pcrp_length,
        case when g:gene then "chr" + r.chrom when g:transcript then r.tx_ac end as a_ref,
        r.start[0] as r_start,
        r.end[1] as r_end,
        case when g:gene then [g.uuid] when g:transcript then [gg.uuid] end as a_gene_uuid,
        case when g:gene then [g.symbol] when g:transcript then [gg.symbol] end as a_gene_symbol,
        null as p1_name,
        null as p1_length,
        null as p1_ref,
        null as r1_start,
        null as r1_end,
        null as p2_name,
        null as p2_length,
        null as p2_ref,
        null as r2_start,
        null as r2_end,
        case when r:region then "gDNA" when r:transcript_region then "cDNA" end as a_type,
        r.uuid as align_region_uuid"""
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        return res

    def setPCRProductTechnologies(self, uuid, labelsYes, labelsNo):
        query_text = "match (p:kb_node:pcr_product {uuid: { uuid }}) " + " ".join(["remove p:" + l for l in labelsNo]) + " " + " ".join(["set p:" + l for l in labelsYes])
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)

    def setPrimerTechnologies(self, uuid, labelsYes, labelsNo):
        query_text = "match (p:kb_node:primer {uuid: { uuid }}) " + " ".join(["remove p:" + l for l in labelsNo]) + " " + " ".join(["set p:" + l for l in labelsYes])
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)

    def getAlterationsIn_gDNAAmpliconList(self, uuid_list):
        #query_text = "match (pcrp:kb_node:pcr_product)-[:aligns_to]->(r:region)-[:part_of]->(g:gene) using index pcrp:kb_node(uuid) where pcrp.uuid in { uuid_list } optional match (g)<-[:part_of]-(r_alt:region)-[:has_alteration]->(a:sequence_alteration) where r_alt.start[0] >= r.start[0] and r_alt.end[1] <= r.end[1] return pcrp.uuid, pcrp.name, g.uuid, g.symbol, collect([r_alt.uuid, r_alt.chrom, r_alt.start[0], r_alt.end[1], a.uuid])"
        query_text = "match (pcrp:kb_node:pcr_product)-[:aligns_to]->(r_pcr:region)-[:part_of]->(g:gene)<-[:part_of]-(r:region)-[:has_alteration]->(s:sequence_alteration) using index pcrp:kb_node(uuid) where pcrp.uuid in { uuid_list } and r.start[0] >= r_pcr.start[0] and r.end[1] <= r_pcr.end[1] return s.uuid"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid_list=uuid_list)
        return [x[0] for x in res] if len(res) else []

    def getAlterationsIn_cDNAAmpliconList(self, uuid_list):
        # first, get amplified region for each amplicon
        pcrProduct_region = self.getTranscriptregionFrom_cDNAAmpliconList(uuid_list)
        result = []

        for txreg in pcrProduct_region:
            pcr_uuid, pcr_name, tx_ac, start, end, gene_uuid, gene_symbol, tx_uuid = txreg[0:8]
            regs = self.mapTranscriptregionToRegions(tx_ac, start, end)
            uuid_alt_in_regs = [x[0] for x in self.getGeneAlterationsInRegionList(gene_uuid, regs)]
            result.extend(uuid_alt_in_regs)

        return result

    def getGeneAlterationsInRegionList(self, gene_uuid, region_list):
        #query_text = "match (g:gene {uuid: { gene_uuid }})<-[:part_of]-(r:region)-[:has_alteration]->(a:sequence_alteration) where any(x in { reg_list } where x.chrom = r.chrom and x.start[0] <= r.start[0] and x.end[1] >= r.end[1]) return r.uuid, r.chrom, r.start[0], r.end[1], a.uuid"
        query_text = "match (g:gene {uuid: { gene_uuid }})<-[:part_of]-(r:region)-[:has_alteration]->(a:sequence_alteration) where any(x in { reg_list } where x.chrom = r.chrom and x.start[0] <= r.start[0] and x.end[1] >= r.end[1]) return a.uuid"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(gene_uuid=gene_uuid,reg_list=region_list)
        return res

    def getTranscriptregionFrom_cDNAAmpliconList(self, uuid_list):
        query_text = "match (pcrp:kb_node:pcr_product)-[:aligns_to]->(r:transcript_region)-[:part_of]->(t:transcript)-[:transcribed_from]->(g:gene) using index pcrp:kb_node(uuid) where pcrp.uuid in { uuid_list } return pcrp.uuid, pcrp.name, r.tx_ac, r.start[0], r.end[1], g.uuid, g.symbol, t.uuid"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid_list=uuid_list)
        return res

    def mapTranscriptregionToRegions(self, tx_ac, start, end):
        tx_info = self.getTranscriptInfo(ac=tx_ac)
        if len(tx_info) == 0:
            raise Exception("Transcript not found: {0}".format(tx_ac))
        tx_info = tx_info[0]
        exon_starts = tx_info['exon.starts']
        exon_ends = tx_info['exon.ends']
        chrom = tx_info['tx.chrom']
        exon_starts_tx = [1]
        for l in tx_info['exon.lengths']:
            exon_starts_tx.append(exon_starts_tx[-1] + l)

        start_exon, = [i for i in xrange(0, len(exon_starts_tx)-1) if start >= exon_starts_tx[i] and start < exon_starts_tx[i+1]]
        end_exon, = [i for i in xrange(0, len(exon_starts_tx)-1) if end >= exon_starts_tx[i] and end < exon_starts_tx[i+1]]

        regions = []
        if tx_info['strand'] == '+':
            r_start = exon_starts[start_exon] + (start - exon_starts_tx[start_exon])
            r_end = exon_ends[start_exon]
            regions.append({'chrom': chrom, 'start': r_start, 'end': r_end})
            i = start_exon + 1
            while i < end_exon:
                regions.append({'chrom': chrom, 'start': exon_starts[i], 'end': exon_ends[i]})
                i += 1
            r_start = exon_starts[end_exon]
            r_end = exon_starts[end_exon] + (end - exon_starts_tx[end_exon])
            regions.append({'chrom': chrom, 'start': r_start, 'end': r_end})
        else:
            r_start = exon_starts[start_exon]
            r_end = exon_ends[start_exon] - (start - exon_starts_tx[start_exon])
            regions.append({'chrom': chrom, 'start': r_start, 'end': r_end})
            i = start_exon + 1
            while i < end_exon:
                regions.append({'chrom': chrom, 'start': exon_starts[i], 'end': exon_ends[i]})
                i += 1
            r_start = exon_ends[end_exon] - (end - exon_starts_tx[end_exon])
            r_end = exon_ends[end_exon]
            regions.append({'chrom': chrom, 'start': r_start, 'end': r_end})

        return regions

    def getGeneInfo(self, uuid=None, symbol=None, ac=None, chrom=None, query=None):
        if uuid is None and symbol is None and ac is None and chrom is None and query is None:
            return
        where_clauses = []
        uuid_list = []
        indices = ''
        if uuid is not None:
            where_clauses.append("g.uuid = { uuid }")
        if chrom is not None:
            where_clauses.append("g.chrom = { chrom }")
        if symbol is not None:
            where_clauses.append("g.symbol = { symbol }")
        if ac is not None:
            where_clauses.append("g.ac = { ac }")
        if query is not None:
            # looks into the gene alias table
            where_clauses.append("g.uuid in { uuid_list }")
            indices = ' using index g:kb_node(uuid)'
            from annotations.models import GeneAlias
            uuid_list = [v[0] for v in GeneAlias.objects.filter(synonym=query.lower()).only('graph_uuid').values_list('graph_uuid')]

        query_text = "match (g:kb_node:gene)" + indices + " where " + " and ".join(where_clauses) + "return g.uuid, g.symbol, g.strand, g.chrom, g.start[0], g.end[1], g.ac"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(symbol=symbol if symbol else None, chrom=str(chrom).replace('chr', '') if chrom else None, ac=ac.upper() if ac else None, uuid=uuid if uuid else None, uuid_list=uuid_list)

        return [Gene(*x) for x in res]

    def getTranscriptInfo(self, uuid=None, ac=None):
        if uuid is None and ac is None:
            return
        where_clauses = []
        if uuid is not None:
            where_clauses.append("t.uuid = { uuid }")
        if ac is not None:
            where_clauses.append("t.ac = { ac }")
            ac = ac.split('.')[0]

        query_text = """match (t:kb_node:transcript) where """ + " and ".join(where_clauses) + """ match (t)-[:transcribed_from]->(g:gene) match (t)<-[r:integral_part_of]-(e:exon) with t, g, e order by toint(r.exon_number) return t.cds_start, t.cds_end, collect(e.end[1]-e.start[0]+1), g.symbol, g.strand, t.chrom, t.start[0], t.end[1], collect(e.start[0]), collect(e.end[1]), t.ac, g.uuid, g.ac, case when has(t.is_default) then true else false end"""
        query = neo4j.CypherQuery(self.gdb, query_text)
        # strip version number off accession (if any)
        res = query.execute(ac=ac,uuid=uuid)
        result = []
        for row in res:
            result.append({ 'tx.chrom': row[5],
                            'tx.start': row[6],
                            'tx.end': row[7],
                            'tx.cds_start': row[0]-1 if row[0] else None,
                            'tx.cds_end': row[1],
                            'exon.lengths': row[2],
                            'exon.starts': row[8],
                            'exon.ends': row[9],
                            'gene.symbol': row[3],
                            'gene.uuid': row[11],
                            'strand': row[4],
                            'tx.ac': row[10],
                            'gene.ac': row[12],
                            'tx.is_default': row[13]
                            })
        return result

    def transcriptContainsCoordinate(self, chrom, pos, tx_ac=None, tx_info=None):
        if tx_ac is None and tx_info is None:
            raise Exception("Either transcript accession or info must be specified")
        if tx_info is None:
            try:
                tx_info = self.getTranscriptInfo(ac=tx_ac)[0]
            except:
                raise Exception("Transcript %s not found" % tx_ac)
        if chrom != tx_info['tx.chrom'] or pos < tx_info['tx.start'] or pos > tx_info['tx.end']:
            # different chromosome or outside gene
            return False
        else:
            exon_starts, exon_ends = tx_info['exon.starts'], tx_info['exon.ends']
            result = filter(lambda k: exon_starts[k] <= pos and exon_ends[k] >= pos, xrange(0, len(exon_starts)))
            return len(result) > 0
            
    def mapGenomicCoordinateToTranscript(self, chrom, pos, tx_ac=None, tx_info=None):
        if tx_ac is None and tx_info is None:
            raise Exception("Either transcript accession or info must be specified")
        if tx_info is None:
            try:
                tx_info = self.getTranscriptInfo(ac=tx_ac)[0]
            except:
                raise Exception("Transcript %s not found" % tx_ac)
        if chrom != tx_info['tx.chrom'] or pos < tx_info['tx.start'] or pos > tx_info['tx.end']:
            raise Exception("Transcript does not contain the specified coordinate")
        exon_starts, exon_ends, exon_lengths = tx_info['exon.starts'], tx_info['exon.ends'], tx_info['exon.lengths']
        result = filter(lambda k: exon_starts[k] <= pos and exon_ends[k] >= pos, xrange(0, len(exon_starts)))
        if len(result) == 0:
            raise Exception("Transcript does not contain the specified coordinate")
        exon_id = result[0]
        tx_pos = sum(exon_lengths[:exon_id])
        tx_pos += pos - exon_starts[exon_id] + 1 if tx_info['strand'] == '+' else exon_ends[exon_id] - pos + 1
        return {'tx_ac': tx_info['tx.ac'], 'pos': tx_pos, 'exon_id': exon_id}

    def getGeneInfo_byUuid(self, uuid_list):
        query_text = "match (g:kb_node:gene) using index g:kb_node(uuid) where g.uuid in { uuid_list } return g.uuid, g.symbol, g.strand, g.chrom, g.start[0], g.end[1], g.ac"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid_list=uuid_list)
        return res

    def getGeneRegionInfo_byUuid(self, uuid_list):
        query_text = "match (g:gene)<-[:part_of]-(r:kb_node:region) using index r:kb_node(uuid) where r.uuid in { uuid_list } return r.uuid, g.symbol, g.strand, r.chrom, r.start[0], r.end[1], g.ac, g.uuid, r.ref, r.c_start, r.c_offset, 'p.' + r.loc_p"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid_list=uuid_list)
        return res

    def getRegionInfo_byUuid(self, uuid_list):
        query_text = "match (r:kb_node:region) using index r:kb_node(uuid) where r.uuid in { uuid_list } return r.uuid, r.chrom, r.start, r.end, r.strand"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid_list=uuid_list)
        return res

    def getTranscriptregionInfo_byUuid(self, uuid_list):
        query_text = "match (r:kb_node:transcript_region) using index r:kb_node(uuid) where r.uuid in { uuid_list } return r.uuid, r.tx_ac, r.start, r.end, r.strand"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid_list=uuid_list)
        return res

    def getSequenceAlteration(self, **kwargs):
        query_text = {  "point_mutation": "match (r:region)%s where r.chrom = { chrom } and r.start[0] = { start } and r.end[1] = { end } match (r)-[:has_alteration]->(s:point_mutation) where s.alt = { alt } return s.uuid;",
                        "insertion": "match (r:region)%s where r.chrom = { chrom } and r.start[0] = { start } and r.end[1] = { end } match (r)-[:has_alteration]->(s:insertion) where s.alt = { alt } return s.uuid;",
                        "indel": "match (r:region)%s where r.chrom = { chrom } and r.start[0] = { start } and r.end[1] = { end } match (r)-[:has_alteration]->(s:indel) where s.alt = { alt } and s.num_bases = { num_bases } return s.uuid;",
                        "deletion": "match (r:region)%s where r.chrom = { chrom } and r.start[0] = { start } and r.end[1] = { end } match (r)-[:has_alteration]->(s:deletion) where s.num_bases = { num_bases } return s.uuid;",
                        "duplication": "match (r:region)%s where r.chrom = { chrom } and r.start[0] = { start } and r.end[1] = { end } match (r)-[:has_alteration]->(s:duplication) where s.num_bases = { num_bases } return s.uuid;"
                    }
        gene_pattern = "-[:part_of]->(g:gene {symbol: { gene_symbol }})"
        query = neo4j.CypherQuery(self.gdb, query_text[kwargs['label']] % (gene_pattern if kwargs.get("gene_symbol", None) else ""))
        res = query.execute(**kwargs)
        return res[0].values[0] if len(res) > 0 else None

    def getShortGeneticVariation(self, name, allele):
        query_text = "match (v:short_genetic_variation)<-[:has_short_genetic_variation]-(r:region) where v.name = { name } and v.allele = { allele } and not(r:gene) return v.uuid, r.uuid"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(name=name,allele=allele)
        return (res[0][0], res[0][1]) if len(res) > 0 else None

    def getShortGeneticVariation_byUuid(self, uuid):
        query_text = "match (v:short_genetic_variation)<-[:has_short_genetic_variation]-(r:region) where v.uuid = { uuid } and not(r:gene) optional match (v)<-[:has_short_genetic_variation]-(g:gene) where g.start[0] <= r.start[0] and g.end[1] >= r.end[1] with v, r, head(collect(g)) as g return v.uuid as uuid, r.chrom as chrom, r.start[0] as start, r.end[1] as end, v.strand as strand, v.name as name, v.alt as alt, v.num_repeats as num_repeats, v.allele as allele, v.popul_freq as freq, head(filter(l in labels(v) where l in ['SNP', 'sgv_indel', 'microsatellite', 'MNP', 'sgv_insertion', 'sgv_deletion'])) as labels, g.symbol as gene_symbol, g.ac as gene_ac, g.uuid as gene_uuid, v.x_ref as x_ref, r.uuid as region_uuid, case length(filter(x in labels(r) where x = 'homologous_region')) when 1 then true else false end as multi_region"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        return res[0] if len(res) > 0 else None

    def getShortGeneticVariation_byUuid_list(self, uuid_list):
        query_text = "match (v:kb_node:short_genetic_variation)<-[:has_short_genetic_variation]-(r:region) and not(r:gene) using index v:kb_node(uuid) where v.uuid in { uuid_list } optional match (v)<-[:has_short_genetic_variation]-(g:gene) where g.start[0] <= r.start[0] and g.end[1] >= r.end[1] return v.uuid as uuid, r.chrom as chrom, r.start[0] as start, r.end[1] as end, v.strand as strand, v.name as name, v.alt as alt, v.num_repeats as num_repeats, v.allele as allele, v.popul_freq as freq, head(filter(l in labels(v) where l in ['SNP', 'sgv_indel', 'microsatellite', 'MNP', 'sgv_insertion', 'sgv_deletion'])) as labels, g.symbol as gene_symbol, g.ac as gene_ac, g.uuid as gene_uuid, v.x_ref as x_ref, r.uuid as region_uuid, case length(filter(x in labels(r) where x = 'homologous_region')) when 1 then true else false end as multi_region"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid_list=uuid_list)
        return res

    def getShortGeneticVariationsByPosition(self, chrom=None, start=None, end=None, gene_uuid=None, tx_uuid=None, limit=500):
        # N.B. when a transcript is provided, the query *doesn't* check whether the short genetic variation is inside the transcript
        # but it simply checks that it falls within the region defined by the corresponding gene
        match_clause = ["(v:short_genetic_variation)", "(v)<-[:has_short_genetic_variation]-(r:region)"]
        optional_match_clause = []
        where_clause = ["not(r:gene)"]
        if gene_uuid is not None:
            match_clause.append("(v)<-[:has_short_genetic_variation]-(g:gene {uuid: { gene_uuid }})")
            if tx_uuid is not None:
                match_clause.append("(g)<-[:transcribed_from]-(t:transcript {uuid: { tx_uuid }})")
        elif tx_uuid is not None:
            match_clause.append("(v)<-[:has_short_genetic_variation]-(g:gene)")
            match_clause.append("(g)<-[:transcribed_from]-(t:transcript {uuid: { tx_uuid }})")
        else:
            optional_match_clause.append("(v)<-[:has_short_genetic_variation]-(g:gene)")
        if chrom is not None:
            chrom = str(chrom)
            where_clause.append("r.chrom = { chrom }")
        if start is not None:
            where_clause.append("r.start[0] >= { start }")
        if end is not None:
            where_clause.append("r.end[1] <= { end }")
        return_clause = "return v.uuid as uuid, r.chrom as chrom, r.start[0] as start, r.end[1] as end, v.strand as strand, v.name as name, v.alt as alt, v.num_repeats as num_repeats, v.allele as allele, v.popul_freq as freq, head(filter(l in labels(v) where l in ['SNP', 'sgv_indel', 'microsatellite', 'MNP', 'sgv_insertion', 'sgv_deletion'])) as labels, g.symbol as gene_symbol, g.ac as gene_ac, g.uuid as gene_uuid, v.x_ref as x_ref, r.uuid as region_uuid, case length(filter(x in labels(r) where x = 'homologous_region')) when 1 then true else false end as multi_region"
        query_text = "match " + ", ".join(match_clause) + " " + \
                    ("where " if len(where_clause) > 0 else "") + " and ".join(where_clause) + " " + \
                    ("optional match " if len(optional_match_clause) > 0 else "") + ", ".join(optional_match_clause) + " " + \
                    return_clause + " " + \
                    (("limit %d" % limit) if (isinstance(limit, (int, long)) and limit is not None) else "")
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(chrom=chrom,start=start,end=end,gene_uuid=gene_uuid,tx_uuid=tx_uuid)
        return res

    def getCopyNumberVariation_byGene(self, gene_uuid, cnv_label):
        query_text = "match (g:gene)-[:has_copy_number_variation]->(v:copy_number_variation:" + cnv_label + ") where g.uuid = { gene_uuid } return v.uuid"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(gene_uuid=gene_uuid)
        return res[0].values[0] if len(res) > 0 else None

    def getCopyNumberVariation_byRegion(self, region_chrom, region_start, region_end, cnv_label):
        query_text = "match (r:region)-[:has_copy_number_variation]->(v:copy_number_variation:" + cnv_label + ") where r.chrom = { region_chrom } and r.start[0] = { region_start } and r.end[1] = { region_end } return v.uuid"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(region_chrom=region_chrom,region_start=region_start,region_end=region_end)
        return res[0].values[0] if len(res) > 0 else None

    def getCopyNumberVariation_byUuid(self, uuid):
        query_text = "match (c:kb_node:copy_number_variation)<-[:has_copy_number_variation]-(g:gene) where c.uuid = { uuid } return c.uuid as uuid, labels(c) as labels, g.chrom as chrom, g.start[0] as start, g.end[1] as end, g.uuid as gene_uuid, g.ac as gene_ac, g.symbol as gene_symbol, c.source as source, c.x_ref as x_ref"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        return res[0] if len(res) > 0 else None

    def getCopyNumberVariation_byUuid_list(self, uuid_list):
        query_text = "match (c:kb_node:copy_number_variation)<-[:has_copy_number_variation]-(g:gene) using index c:kb_node(uuid) where c.uuid in { uuid_list } return c.uuid as uuid, labels(c) as labels, g.chrom as chrom, g.start[0] as start, g.end[1] as end, g.uuid as gene_uuid, g.ac as gene_ac, g.symbol as gene_symbol, c.source as source, c.x_ref as x_ref"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid_list=uuid_list)
        return res

    def getCopyNumberVariationsByPosition(self, chrom=None, start=None, end=None, gene_uuid=None, tx_uuid=None, limit=500):
        # N.B. the transcript is only used to select the corresponsing gene and doesn't imply the copy number was measured on the transcript
        match_clause = ["(v:copy_number_variation)"]
        optional_match_clause = []
        where_clause = []
        if gene_uuid is not None:
            match_clause.append("(v)<-[:has_copy_number_variation]-(g:gene {uuid: { gene_uuid }})")
        else:
            match_clause.append("(v)<-[:has_copy_number_variation]-(g:gene)")
        if tx_uuid is not None:
            match_clause.append("(g)<-[:transcribed_from]-(t:transcript {uuid: { tx_uuid }})")
        if chrom is not None:
            chrom = str(chrom)
            where_clause.append("g.chrom = { chrom }")
        if start is not None:
            where_clause.append("g.start[0] >= { start }")
        if end is not None:
            where_clause.append("g.end[1] <= { end }")
        return_clause = "return v.uuid as uuid, labels(v) as labels, g.chrom as chrom, g.start[0] as start, g.end[1] as end, g.uuid as gene_uuid, g.ac as gene_ac, g.symbol as gene_symbol, v.source as source, v.x_ref as x_ref"
        query_text = "match " + ", ".join(match_clause) + " " + \
                    ("where " if len(where_clause) > 0 else "") + " and ".join(where_clause) + " " + \
                    ("optional match " if len(optional_match_clause) > 0 else "") + ", ".join(optional_match_clause) + " " + \
                    return_clause + " " + \
                    (("limit %d" % limit) if (isinstance(limit, (int, long)) and limit is not None) else "")
        print query_text
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(chrom=chrom,start=start,end=end,gene_uuid=gene_uuid,tx_uuid=tx_uuid)
        return res

    def regionHasCodingCoordinates(self, uuid):
        query_text = "match (r:kb_node:region {uuid: { uuid }}) return has(r.start_c_base)"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        return res[0][0]

    def getRegionByCoords(self, chrom, start, end, strand=None, gene_uuid=None, gene_symbol=None):
        chrom = str(chrom)
        if gene_uuid:
            gene_pattern = "-[:part_of]->(g:gene {uuid: { gene_uuid }})"
        elif gene_symbol:
            gene_pattern = "-[:part_of]->(g:gene {symbol: { gene_symbol }})"
        else:
            gene_pattern = ""
        
        if isinstance(start, list):
            start_condition = "r.start = { start }"
        else:
            start_condition = "r.start[0] = { start }"

        if isinstance(end, list):
            end_condition = "r.end = { end }"
        else:
            end_condition = "r.end[1] = { end }"

        if strand is None:
            query_text = "match (r:region)%s where r.chrom = { chrom } and %s and %s return r.uuid;" % (gene_pattern, start_condition, end_condition)
        else:
            query_text = "match (r:region)%s where r.chrom = { chrom } and %s and %s and r.strand = { strand } return r.uuid;" % (gene_pattern, start_condition, end_condition)

        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(chrom=chrom,start=start,end=end,strand=strand,gene_uuid=gene_uuid,gene_symbol=gene_symbol)
        return [x[0] for x in res]

    def getTranscriptregionByCoords(self, tx_ac, start, end, strand=None):
        if isinstance(start, list):
            start_condition = "r.start = { start }"
        else:
            start_condition = "r.start[0] = { start }"

        if isinstance(end, list):
            end_condition = "r.end = { end }"
        else:
            end_condition = "r.end[1] = { end }"

        if strand is None:
            query_text = "match (r:transcript_region) where r.tx_ac = { tx_ac } and %s and %s return r.uuid;" % (start_condition, end_condition)
        else:
            query_text = "match (r:transcript_region) where r.tx_ac = { tx_ac } and %s and %s and r.strand = { strand } return r.uuid;" % (start_condition, end_condition)

        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(tx_ac=tx_ac,start=start,end=end,strand=strand)
        return [x[0] for x in res]

    def getWildType(self, chrom, start, end):
        query_text = "match (r:region)-[:has_wild_type]->(w:wild_type) where r.chrom = { chrom } and r.start[0] = { start } and r.end[1] = { end } return w.uuid;"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(chrom=chrom,start=start,end=end)
        if len(res) > 0:
            return res[0][0]
        else:
            return None

    def getOrCreateWildType(self, chrom, start, end):
        query_text = "match (r:region) where r.chrom = { chrom } and r.start[0] = { start } and r.end[1] = { end } optional match (r)-[:has_wild_type]->(w:wild_type) return r, w.uuid;"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(chrom=chrom,start=start,end=end)
        if len(res) > 0:
            if res[0][1] is not None:
                # both region and wild type exist
                #print "region exists"
                #print "wild_type exists"
                return res[0][1]
            else:
                # region exists but wild type doesn't
                # create wild type and link it to region
                #print "region exists"
                #print "creating wild_type"
                wbatch = neo4j.WriteBatch(self.gdb)
                wt_uuid = self._getNewUUID()
                wt_node = wbatch.create(node(uuid=wt_uuid))
                wbatch.add_labels(wt_node, KNOWLEDGE_BASE_NODE)
                wbatch.add_labels(wt_node, WILD_TYPE)
                wbatch.create(rel(res[0][0], HAS_WILD_TYPE, wt_node, {}))
                wbatch.submit()
                return wt_uuid
        else:
            # neither region nor wild type exist
            # create region
            #print "creating region"
            reg_uuid = self.createRegion(chrom, start, end)
            reg_node = self._getNodeByUUID(KNOWLEDGE_BASE_NODE, reg_uuid)
            # create wild type
            #print "creating wild_type"
            wbatch = neo4j.WriteBatch(self.gdb)
            wt_uuid = self._getNewUUID()
            wt_node = wbatch.create(node(uuid=wt_uuid))
            wbatch.add_labels(wt_node, KNOWLEDGE_BASE_NODE)
            wbatch.add_labels(wt_node, WILD_TYPE)
            wbatch.create(rel(reg_node, HAS_WILD_TYPE, wt_node, {}))
            wbatch.submit()
            return wt_uuid

    def _getNodeByUUID(self, label, uuid):
        query_text = "match (n:" + label + ") where n.uuid = { uuid } return n;"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        if len(res) > 0:
            return res[0][0]
        else:
            raise Exception("Node :{0}(UUID={1}) not found".format(label, uuid))

    def getKBNodeLabelsByUuidList(self, uuid_list):
        if not isinstance(uuid_list, list):
            uuid_list = [uuid_list]
        query_text = "match (n:kb_node) where n.uuid in { uuid_list } return n.uuid, labels(n);"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid_list=uuid_list)
        return res

    def _getNodeByGenid(self, label, genid):
        query_text = "match (n:" + label + ") where n.identifier = { genid } return n;"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(genid=genid)
        if len(res) > 0:
            return res[0][0]
        else:
            raise Exception("Node :{0}(UUID={1}) not found".format(label, genid))

    def _getNodeByGenid_batch(self, label, genid_list):
        query_text = "match (n:" + label + ") where n.identifier = { genid } return n;"
        rbatch = neo4j.ReadBatch(self.gdb)
        for g in genid_list:
            rbatch.append_cypher(query_text, {'genid': g})
        res = rbatch.submit()
        return dict(zip(genid_list, res))

    def _getNodeByAccession(self, label, ac):
        query_text = "match (n:" + label + ") where n.ac = { ac } return n;"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(ac=ac)
        if len(res) > 0:
            return res[0][0]
        else:
            raise Exception("Node :{0}(ac={1}) not found".format(label, ac))

    def checkGeneAnnotation(self, src_genid, gene_uuid, ref_type_label):
        # Input: the sample, the annotated gene, the reference type
        # Output: a list of annotations
        query_text = "match (b:Bioentity {identifier: { src_genid }})-[:has_annotation]->(a:annotation)-[:has_reference]->(r:kb_node:%s)<-[]-(g:gene { uuid: { gene_uuid }}) return a.uuid, r.uuid, a.db_id" % ref_type_label
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(gene_uuid=gene_uuid,src_genid=src_genid)
        if len(res) > 0:
            return [(x[0], x[1], x[2]) for x in res]
        else:
            return []

    def annotateNode(self, src_genid,  analysis_uuid, ref_uuid, data=None, db_model=None, db_id=None):
        # check whether both reference and bioentity exist
        if data is None:
            data = {}
        print "data=", data
        if isinstance(src_genid, basestring):
            query_text = "optional match (r:kb_node {uuid: { ref_uuid }}) optional match (b:Bioentity {identifier: { src_genid }}) optional match (a:analysis {uuid: { analysis_uuid }}) return id(r) as id_r, id(b) as id_b, id(a) as id_a;"
            query = neo4j.CypherQuery(self.gdb, query_text)
            res = query.execute(ref_uuid=ref_uuid,src_genid=src_genid,analysis_uuid=analysis_uuid)
            id_r, id_b, id_a = res[0]
            if id_r is None:
                raise Exception("Reference node not found")
            if id_b is None:
                raise Exception("Bioentity node not found")
            if id_a is None:
                raise Exception("Analysis node not found")
        elif isinstance(src_genid, list):
            query_text = "optional match (r:kb_node {uuid: { ref_uuid }}) optional match (a:analysis {uuid: { analysis_uuid }}) return id(r) as id_r, id(a) as id_a;"
            query = neo4j.CypherQuery(self.gdb, query_text)
            res = query.execute(ref_uuid=ref_uuid,analysis_uuid=analysis_uuid)
            id_r, id_a = res[0]
            if id_r is None:
                raise Exception("Reference node not found")
            if id_a is None:
                raise Exception("Analysis node not found")
            query_text = "match (b:Bioentity) where b.identifier in { src_genid } return b.identifer;"
            query = neo4j.CypherQuery(self.gdb, query_text)
            res = query.execute(src_genid=src_genid)
            if len(res) != len(src_genid):
                found_b = set([x[0] for x in res])
                missing_b = [x for x in src_genid if x not in found_b]
                raise Exception("Some Bioentity nodes were not found: %s" % str(missing_b))
        else:
            raise Exception("Invalid type for parameter src_genid: expected 'string' or 'list', but found %s" % type(src_genid))

        annotation_args = {"uuid": self._getNewUUID()}
        print "(1) data=", data
        if db_id is not None:
            annotation_args.update({"db_id": db_id if isinstance(db_id, list) else [db_id]})
        if db_model is not None:
            annotation_args.update({"db_model": db_model})

        if len(set(annotation_args.keys()).intersection(data.keys())) > 0:
            print "data =", data
            print "annotation_args =", annotation_args
            raise Exception("Reserved arguments found in data dictionary")
        data.update(annotation_args)
        annotation_args_string = ", ".join(["%s: { %s }" % (k,k) for k in data.keys()])

        if isinstance(src_genid, basestring):
            query_text = "start b=node({ bio_id }), r=node({ ref_id }) match (an:analysis {uuid: { analysis_uuid }}) create (a:annotation {%s}) create (b)-[:has_annotation]->(a) create (a)-[:has_reference]->(r) create (an)-[:generates_annotation]->(a)" % annotation_args_string
            query = neo4j.CypherQuery(self.gdb, query_text)
            res = query.execute(bio_id=id_b,analysis_uuid=analysis_uuid,ref_id=id_r,**data)
            return data["uuid"]
        elif isinstance(src_genid, list):
            query_text = "start r=node({ ref_id }) match (an:analysis {uuid: { analysis_uuid }}) create (a:annotation {%s})-[:has_reference]->(r) create (an)-[:generates_annotation]->(a) with a match (b:Bioentity) where b.identifier in { src_genid } create (b)-[:has_annotation]->(a)" % annotation_args_string
            query = neo4j.CypherQuery(self.gdb, query_text)
            res = query.execute(analysis_uuid=analysis_uuid,ref_id=id_r,src_genid=src_genid,**data)
            return data["uuid"]

        """
        src_node = self._getNodeByGenid(label=BIOENTITY,genid=src_genid)
        wbatch = neo4j.WriteBatch(self.gdb)
        d = {}
        d['uuid'] = 
        d['db_id'] = db_id
        d['db_model'] = db_model
        ann_node = wbatch.create(node(**d))
        wbatch.add_labels(ann_node, ANNOTATION)
        wbatch.create(rel(src_node, HAS_ANNOTATION, ann_node, {}))
        if ref_uuid:
            ref_node = self._getNodeByUUID(label=KNOWLEDGE_BASE_NODE,uuid=ref_uuid)
            wbatch.create(rel(ann_node, HAS_REFERENCE, ref_node, {}))
        wbatch.submit()
        return d['uuid']
        """

    def deleteAnnotation(self, uuid):
        query_text = "match (a:annotation {uuid: { uuid }})-[r]-() delete r, a"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        return

    def updateAnnotationContent(self, uuid, db_id, data={}, ref_uuid=None):
        data.update({'db_id': db_id if isinstance(db_id, list) else [db_id]})
        update_string = ", ".join(["a.%s = { %s }" % (k, k) for k in data.keys()])
        if ref_uuid is not None:
            query_text = "match (a:annotation {uuid: { uuid }})-[r:has_reference]->(), (x:kb_node {uuid: { ref_uuid }}) set %s delete r create (a)-[:has_reference]->(x)" % update_string
        else:
            query_text = "match (a:annotation {uuid: { uuid }}) set %s" % update_string
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid, ref_uuid=ref_uuid, **data)

    def annotateBatch(self, annot_list):
        query_text = "match (b:Bioentity {identifier: { genid }}), (r:kb_node {uuid: { ref_uuid }}) create (a:annotation {uuid: { ann_uuid }, db_id: { db_id }, db_model: { db_model }}) create (b)-[:has_annotation]->(a) create (a)-[:has_reference]->(r)"
        wbatch = neo4j.WriteBatch(self.gdb)
        uuids = {}
        for a in annot_list:
            ref_uuid, src_genid, db_model, db_id = a[0], a[1], a[2], a[3]
            new_uuid = self._getNewUUID()
            uuids[db_id] = new_uuid
            wbatch.append_cypher(query_text, {'genid': src_genid, 'ref_uuid': ref_uuid, 'ann_uuid': new_uuid, 'db_id': db_id, 'db_model': db_model})
        wbatch.submit()
        return uuids

    def getAnnotation(self, src_genid, ref_uuid):
        query_text = "match (a:"+BIOENTITY+")-[:"+ HAS_ANNOTATION + "]->(b:"+ANNOTATION+")-[:"+HAS_REFERENCE+"]->(c:"+KNOWLEDGE_BASE_NODE+") where a.identifier = { src_genid } and c.uuid = { ref_uuid } return b.uuid, b.db_id"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(src_genid=src_genid,ref_uuid=ref_uuid)
        return res[0] if len(res) > 0 else None

    def getAnnotation_byUuid(self, annot_uuid):
        query_text = "match (a:"+BIOENTITY+")-[:"+ HAS_ANNOTATION + "]->(b:"+ANNOTATION+")-[:"+HAS_REFERENCE+"]->(c:"+KNOWLEDGE_BASE_NODE+") where b.uuid = { annot_uuid }return b.uuid as uuid, b.db_id as db_id, a.identifier as id_sample, c.uuid as ref_uuid"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(annot_uuid=annot_uuid)
        return res[0] if len(res) > 0 else None


    def getAnnotationBatch_fromSeqAlt(self, ref_uuid_list, genid_list):
        genid_list = self._convertGenidToCypherRegex(genid_list)
        query_text = "match (s:kb_node)<-[:has_reference]-(a:annotation)<-[:has_annotation]-(b:Bioentity) using index s:kb_node(uuid) where s.uuid in { ref_uuid_list } and b.identifier =~ { genid_regex } return s.uuid, b.identifier, a.uuid, a.db_id"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(ref_uuid_list=ref_uuid_list,genid_regex='|'.join(genid_list))
        return res

    def getAnnotation_SeqAlt_Batch_fromAltSite(self, ref_uuid_list, genid_list):
        genid_list = self._convertGenidToCypherRegex(genid_list)
        query_text = "match (r:kb_node:region)-[:has_alteration|has_wild_type]->(s:kb_node)<-[:has_reference]-(a:annotation)<-[:has_annotation]-(b:Bioentity) using index r:kb_node(uuid) where r.uuid in { ref_uuid_list } and b.identifier =~ { genid_regex } return r.uuid as region_uuid, [s.uuid, r.chrom, r.start[0], r.end[1], s.alt, s.num_bases, labels(s)] as seqalt, b.identifier as sample_genid, [a.uuid, a.db_id] as annot"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(ref_uuid_list=ref_uuid_list,genid_regex='|'.join(genid_list))
        return res

    def getAnnotation_SeqAlt_Batch_fromGene(self, ref_uuid_list, genid_list):
        genid_list = self._convertGenidToCypherRegex(genid_list)
        query_text = "match (g:kb_node)<-[:part_of]-(r:region)-[:has_alteration|has_wild_type]->(s:kb_node)<-[:has_reference]-(a:annotation)<-[:has_annotation]-(b:Bioentity) using index g:kb_node(uuid) where g.uuid in { ref_uuid_list } and b.identifier =~ { genid_regex } return g.uuid as gene_uuid, [s.uuid, r.chrom, r.start[0], r.end[1], s.alt, s.num_bases, labels(s)] as seqalt, b.identifier as sample_genid, [a.uuid, a.db_id] as annot"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(ref_uuid_list=ref_uuid_list,genid_regex='|'.join(genid_list))
        return res

    def _convertGenidToCypherRegex(self, gidlist):
        newlist = []
        for x in gidlist:
            y = x.replace('-','.')
            for i in xrange(25, 0, -1):
                if y[i] != '.':
                    break
            if i < 24:
                y = y[:i+2] + '*'
            newlist.append(y)
        return newlist

    def createRegion(self, chrom, start, end, strand=None, gene_uuid=None, gene_symbol=None):
        if gene_uuid:
            gene_pattern = " {uuid: { gene_uuid }}"
        elif gene_symbol:
            gene_pattern = " {symbol: { gene_symbol }}"
        else:
            gene_pattern = ""

        start = start if isinstance(start, list) else [start, start]
        end = end if isinstance(end, list) else [end, end]

        query_text = "match (g:gene%s) where g.chrom = { chrom } and g.start[0] <= { start } and g.end[1] >= { end } return id(g)" % gene_pattern
        print "query_text:", query_text
        print "chrom", chrom, "start", start, "end", end
        #"match (g:gene) where g.chrom = { chrom } and g.start[0] <= { start } and g.end[1] >= { end } optional match (g)<-[:part_of]-(e:exon) where e.chrom = { chrom } and e.start[0] <= { start } and e.end[1] >= { end } return id(g), id(e);"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(chrom=chrom,start=start[0],end=end[1],gene_uuid=gene_uuid,gene_symbol=gene_symbol)
        if len(res) == 0:
            if gene_uuid or gene_symbol:
                raise Exception("Region {chrom}:{start}-{end} on gene {gene} could not be located".format(chrom=chrom,start=start[0],end=end[1],gene=gene_uuid or gene_symbol))
            print "No genes found, locating chromosome"
            query_text = "match (c:chromosome) where c.chrom = { chrom } and c.start[0] <= { start } and c.end[1] >= { end } return id(c);"
            query = neo4j.CypherQuery(self.gdb, query_text)
            res = query.execute(chrom=chrom,start=start[0],end=end[1])
            if len(res) == 0:
                raise Exception("Region {chrom}:{start}-{end} could not be located".format(chrom=chrom,start=start[0],end=end[1]))

        wbatch = neo4j.WriteBatch(self.gdb)
        region_uuid = self._getNewUUID()
        dic = {'chrom': chrom, 'start': start, 'end': end, 'uuid': region_uuid}
        if strand:
            dic['strand'] = strand
        region_node = wbatch.create(node(**dic))
        wbatch.add_labels(region_node, KNOWLEDGE_BASE_NODE)
        wbatch.add_labels(region_node, REGION)

        for x in res:
            target_id = x[0]
            target = neo4j.Node(settings.GRAPH_DB_URL + str(target_id))
            wbatch.create(rel(region_node, PART_OF, target, {}))

        wbatch.submit()
        return region_uuid

    def createTranscriptregion(self, tx_ac, start, end, strand=None):
        start = start if isinstance(start, list) else [start, start]
        end = end if isinstance(end, list) else [end, end]

        if start[0] < 0:
            raise Exception("TranscriptRegion {tx_ac}:{start}-{end} has an invalid start coordinate".format(tx_ac=tx_ac,start=start[0],end=end[1]))
        
        query_text = "match (t:kb_node:transcript) where t.ac = { tx_ac } and t.length >= { end } return id(t)"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(tx_ac=tx_ac,end=end[1])
        if len(res) == 0:
            raise Exception("TranscriptRegion {tx_ac}:{start}-{end} could not be located".format(tx_ac=tx_ac,start=start[0],end=end[1]))

        wbatch = neo4j.WriteBatch(self.gdb)
        region_uuid = self._getNewUUID()
        dic = {'tx_ac': tx_ac, 'start': start, 'end': end, 'uuid': region_uuid}
        if strand:
            dic['strand'] = strand
        region_node = wbatch.create(node(**dic))
        wbatch.add_labels(region_node, KNOWLEDGE_BASE_NODE)
        wbatch.add_labels(region_node, TRANSCRIPT_REGION)

        for x in res:
            target_id = x[0]
            target = neo4j.Node(settings.GRAPH_DB_URL + str(target_id))
            wbatch.create(rel(region_node, PART_OF, target, {}))

        wbatch.submit()
        return region_uuid

    def createFusionGene(self, name, gene1_uuid, gene2_uuid, reg1_g_uuid, reg2_g_uuid):
        gene1_node = self._getNodeByUUID(label=KNOWLEDGE_BASE_NODE,uuid=gene1_uuid)
        gene2_node = self._getNodeByUUID(label=KNOWLEDGE_BASE_NODE,uuid=gene2_uuid)
        reg1_node = self._getNodeByUUID(label=KNOWLEDGE_BASE_NODE,uuid=reg1_g_uuid)
        reg2_node = self._getNodeByUUID(label=KNOWLEDGE_BASE_NODE,uuid=reg2_g_uuid)
        wbatch = neo4j.WriteBatch(self.gdb)
        fg_uuid = self._getNewUUID()
        dic = { 'name': name, 'uuid': fg_uuid }
        fg_node = wbatch.create(node(**dic))
        wbatch.add_labels(fg_node, KNOWLEDGE_BASE_NODE)
        wbatch.add_labels(fg_node, FUSION_GENE)
        wbatch.create(rel(fg_node, HAS_FUSION_PARTNER, gene1_node, {}))
        wbatch.create(rel(fg_node, HAS_FUSION_PARTNER, gene2_node, {}))
        wbatch.create(rel(fg_node, HAS_FUSION_BOUNDARY, reg1_node, {}))
        wbatch.create(rel(fg_node, HAS_FUSION_BOUNDARY, reg2_node, {}))
        wbatch.submit()
        return fg_uuid

    def createFusionTranscript(self, name, fg_uuid, reg1_tx_uuid, reg2_tx_uuid):
        fg_node = self._getNodeByUUID(label=KNOWLEDGE_BASE_NODE,uuid=fg_uuid)
        reg1_node = self._getNodeByUUID(label=KNOWLEDGE_BASE_NODE,uuid=reg1_tx_uuid)
        reg2_node = self._getNodeByUUID(label=KNOWLEDGE_BASE_NODE,uuid=reg2_tx_uuid)
        wbatch = neo4j.WriteBatch(self.gdb)
        ft_uuid = self._getNewUUID()
        dic = { 'name': name, 'uuid': ft_uuid }
        ft_node = wbatch.create(node(**dic))
        wbatch.add_labels(ft_node, KNOWLEDGE_BASE_NODE)
        wbatch.add_labels(ft_node, FUSION_TRANSCRIPT)
        wbatch.create(rel(ft_node, TRANSCRIBED_FROM, fg_node, {}))        
        wbatch.create(rel(ft_node, HAS_FUSION_BOUNDARY, reg1_node, {}))
        wbatch.create(rel(ft_node, HAS_FUSION_BOUNDARY, reg2_node, {}))
        wbatch.submit()
        return ft_uuid

    def createTreatment(self, tName):
        query_text = "create (d:kb_node:" + TREATMENT + " {uuid: { uuid }, name: { name }})"
        query = neo4j.CypherQuery(self.gdb, query_text)
        uuid = self._getNewUUID()
        res = query.execute(uuid=uuid,name=tName)
        return uuid

    def getTreatment_byName(self, tName):
        query_text = "match (d:" + TREATMENT + ") where d.name =~ { tName } return d.uuid, d.name"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(tName="(?i)"+tName)
        return [(x[0], x[1]) for x in res]

    def getTreatment_byUuid(self, uuid):
        query_text = "match (d:kb_node:" + TREATMENT + " {uuid: { uuid }}) return d.uuid, d.name"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        return [(x[0], x[1]) for x in res]

    def deleteTreatment(self, uuid):
        query_text = "match (n:kb_node:" + TREATMENT + ") using index n:kb_node(uuid) where n.uuid = { uuid } match (n)-[r]-() return count(r)"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        if res[0][0] > 0:
            raise Exception("Cannot delete, treatment still has relationships")
        query_text = "match (n:kb_node:" + TREATMENT + ") using index n:kb_node(uuid) where n.uuid = { uuid } delete n"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)

    def createDrugResponse(self, treatment_uuid, criterion_label, response_label):
        wbatch = neo4j.WriteBatch(self.gdb)
        params = {}

        query_text = "match (t:%s {uuid: { treatment_uuid }}) create (t)-[:%s]->(v:%s:%s:%s:%s { params })" % (KNOWLEDGE_BASE_NODE, HAS_DRUG_RESPONSE, KNOWLEDGE_BASE_NODE, DRUG_RESPONSE, DRUG_RESPONSE_CRITERION_PREFIX + PREFIX_SEPARATOR + criterion_label, DRUG_RESPONSE_CLASS_PREFIX + PREFIX_SEPARATOR + response_label)
        new_uuid = self._getNewUUID()    
        params['uuid'] = new_uuid
        wbatch.append_cypher(query_text, {'treatment_uuid': treatment_uuid, 'params': params})
        wbatch.submit()
        return new_uuid

    def getDrugResponse_byTreatment(self, treatment_uuid, criterion_label, response_label):
        query_text = "match (d:kb_node:" + TREATMENT + ")-[:has_drug_response]->(r:drug_response:%s:%s) using index d:kb_node(uuid) where d.uuid = { treatment_uuid } return r.uuid" % (DRUG_RESPONSE_CRITERION_PREFIX + PREFIX_SEPARATOR + criterion_label, DRUG_RESPONSE_CLASS_PREFIX + PREFIX_SEPARATOR + response_label)
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(treatment_uuid=treatment_uuid)
        return res[0].values[0] if len(res) > 0 else None

    def getDrugResponse_byUuid(self, uuid):
        crt_prefix = DRUG_RESPONSE_CRITERION_PREFIX + PREFIX_SEPARATOR
        cls_prefix = DRUG_RESPONSE_CLASS_PREFIX + PREFIX_SEPARATOR
        query_text = "match (dr:kb_node:drug_response)<-[:has_drug_response]-(d:" + TREATMENT + ") using index dr:kb_node(uuid) where dr.uuid = { uuid } return dr.uuid, d.uuid, d.name, substring(head(filter(l in labels(dr) where l =~ \"%s\")), length(\"%s\")), substring(head(filter(l in labels(dr) where l =~ \"%s\")), length(\"%s\"))" % (crt_prefix+".*", crt_prefix, cls_prefix+".*", cls_prefix)
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        return res[0].values if len(res) > 0 else None

    def deleteDrugResponse(self, uuid):
        query_text = "match (n:kb_node:drug_response) using index n:kb_node(uuid) where n.uuid = { uuid } match (n)-[r]-() where type(r) <> 'has_drug_response' return count(r)"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        if res[0][0] > 0:
            raise Exception("Cannot delete, drug response is being referenced by at least one annotation")
        query_text = "match (n:kb_node:drug_response) using index n:kb_node(uuid) where n.uuid = { uuid } match (n)-[r]-() delete r, n"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)

    def linkSequenceAlterationToGene(self, alt_uuid, gene_uuid):
        print "call _getNodeByUUID (alt_node)"
        alt_node = self._getNodeByUUID(label=KNOWLEDGE_BASE_NODE,uuid=alt_uuid)
        print "call _getNodeByUUID (gene_node)"
        gene_node = self._getNodeByUUID(label=KNOWLEDGE_BASE_NODE,uuid=gene_uuid)

        wbatch = neo4j.WriteBatch(self.gdb)
        wbatch.create(rel(gene_node, HAS_ALTERATION, alt_node, {}))
        wbatch.submit()

    def linkShortGeneticVariationToGene(self, var_uuid, gene_uuid):
        # each subsequent call will create a new instance of the relationship (unless a relationship between snp and gene already exists, in which case it won't)
        query_text = "match (v:kb_node:short_genetic_variation {uuid: { var_uuid }}), (g:kb_node:gene {uuid: { gene_uuid }}) merge (g)-[:has_short_genetic_variation]->(v) return v,g"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(var_uuid=var_uuid, gene_uuid=gene_uuid)
        if len(res) > 0:
            return True
        else:
            return False

    def relinkShortGeneticVariationToGene(self, var_uuid, gene_uuid):
        # each call will delete all instances of the relationship and create a new one to the specified gene
        query_text = "match (v:kb_node:short_genetic_variation {uuid: { var_uuid }}), (g:kb_node:gene {uuid: { gene_uuid }}) optional match (v)<-[r:has_short_genetic_variation]-(gg:gene) delete r merge (g)-[:has_short_genetic_variation]->(v) return v,g"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(var_uuid=var_uuid, gene_uuid=gene_uuid)
        if len(res) > 0:
            return True
        else:
            return False

    def unlinkShortGeneticVariationFromGenes(self, var_uuid):
        # deletes all instances of the relationship
        query_text = "match (v:kb_node:short_genetic_variation {uuid: { var_uuid }})<-[r:has_short_genetic_variation]-(gg:gene) delete r"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(var_uuid=var_uuid)

    def relinkShortGeneticVariationToRegion(self, sgv_uuid, newreg_uuid):
        query_text = "match (s:kb_node:short_genetic_variation {uuid: { sgv_uuid }})-[r]-(oldreg:kb_node:region), (newreg:kb_node:region {uuid: { newreg_uuid }}) where not(oldreg:gene) delete r create (s)<-[:has_short_genetic_variation]-(newreg) return s.uuid, newreg.uuid"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(sgv_uuid=sgv_uuid, newreg_uuid=newreg_uuid)
        if len(res) > 0:
            return True
        else:
            return False

    def linkSequenceAlterationToTranscript(self, alt_uuid, tx_ac, source):
        alt_node = self._getNodeByUUID(label=KNOWLEDGE_BASE_NODE,uuid=alt_uuid)
        tx_node = self._getNodeByAccession(label=TRANSCRIPT,ac=tx_ac)
        wbatch = neo4j.WriteBatch(self.gdb)
        wbatch.create(rel(tx_node, HAS_ALTERATION, alt_node, {'source': source}))
        wbatch.submit()

    def _getNewUUID(self):
        return uuid4().hex

    def createPrimer(self, name, length):
        wbatch = neo4j.WriteBatch(self.gdb)
        params = {}
        params['name'] = name
        params['length'] = length
        params['uuid'] = self._getNewUUID()
        primer_node = wbatch.create(node(params))
        wbatch.add_labels(primer_node, KNOWLEDGE_BASE_NODE)
        wbatch.add_labels(primer_node, PRIMER)
        wbatch.submit()
        return params['uuid']

    def addPrimerAlignment(self, primer_uuid, alignments):
        primer_node = self._getNodeByUUID(label=KNOWLEDGE_BASE_NODE,uuid=primer_uuid)
        wbatch = neo4j.WriteBatch(self.gdb)
        accepted_alignments = []
        for a in alignments:
            print "alignment type:", a[4]
            if a[4] == 'genome':
                chrom = str(a[0]).replace('chr', '')
                start = a[1]
                end = a[2]
                strand = a[3]
                region_list = self.getRegionByCoords(chrom, start, end, strand)
                if len(region_list) == 0:
                    print "region not found, creating one"
                    try:
                        r_uuid = self.createRegion(chrom, start, end, strand)
                        print "new region:", r_uuid
                    except Exception, e:
                        print str(e)
                        raise e
                else:
                    print "region found"
                    print list(region_list)
                    r_uuid = region_list[0]
                accepted_alignments.append(a)
            elif a[4] == 'transcriptome':
                tx_ac = a[0]
                start = a[1]
                end = a[2]
                strand = a[3]
                region_list = self.getTranscriptregionByCoords(tx_ac, start, end, strand)
                if len(region_list) == 0:
                    try:
                        r_uuid = self.createTranscriptregion(tx_ac, start, end, strand)
                    except Exception, e:
                        print str(e)
                        raise e
                else:
                    r_uuid = region_list[0]
                accepted_alignments.append(a)
            region_node = self._getNodeByUUID(label=KNOWLEDGE_BASE_NODE,uuid=r_uuid)
            wbatch.create(rel(primer_node, ALIGNS_TO, region_node, {}))
        wbatch.submit()
        return accepted_alignments

    def createPCRProduct(self, name, length, primer1_uuid, reg1_uuid, primer2_uuid, reg2_uuid, amplifiedReg_uuid, alignmentType, p1_is_minus_or_3p, primers_unknown):
        uuid = self._getNewUUID()
        assay_uuid = self._getNewUUID()
        if p1_is_minus_or_3p == True:
            primer1_uuid, primer2_uuid = primer2_uuid, primer1_uuid
            reg1_uuid, reg2_uuid = reg2_uuid, reg1_uuid

        if primers_unknown == False:
            if alignmentType == 'genome':
                query_text = "match (pr1:kb_node), (pr2:kb_node), (regminus:kb_node), (regplus:kb_node), (ampReg:kb_node) where pr1.uuid = { primer1_uuid } and pr2.uuid = { primer2_uuid } and regplus.uuid = { reg1_uuid } and regminus.uuid = { reg2_uuid } and ampReg.uuid = { ampReg_uuid } create (pcr:kb_node:pcr_product {uuid: { uuid }, name: { name }, length: { length }}), (pr1)-[:generates]->(pcr), (pr2)-[:generates]->(pcr), (pcr)-[:has_plus_end]->(regplus), (pcr)-[:has_minus_end]->(regminus), (pcr)-[:aligns_to]->(ampReg)"
            elif alignmentType == 'transcriptome':
                query_text = "match (pr1:kb_node), (pr2:kb_node), (reg3p:kb_node), (reg5p:kb_node), (ampReg:kb_node) where pr1.uuid = { primer1_uuid } and pr2.uuid = { primer2_uuid } and reg5p.uuid = { reg1_uuid } and reg3p.uuid = { reg2_uuid } and ampReg.uuid = { ampReg_uuid } create (pcr:kb_node:pcr_product {uuid: { uuid }, name: { name }, length: { length }}), (pr1)-[:generates]->(pcr), (pr2)-[:generates]->(pcr), (pcr)-[:has_5p_end]->(reg5p), (pcr)-[:has_3p_end]->(reg3p), (pcr)-[:aligns_to]->(ampReg)"
            else:
                raise Exception("Invalid alignment type: {0}".format(self.alignmentType))
        else:
            if alignmentType == 'genome':
                query_text = "match (ampReg:kb_node) where ampReg.uuid = { ampReg_uuid } create (pcr:kb_node:pcr_product {uuid: { uuid }, name: { name }, length: { length }}), (assay:" + RTPCR_ASSAY +" {uuid: { assay_uuid }}), (assay)-[:generates]->(pcr), (pcr)-[:aligns_to]->(ampReg)"
            elif alignmentType == 'transcriptome':
                query_text = "match (ampReg:kb_node) where ampReg.uuid = { ampReg_uuid } create (pcr:kb_node:pcr_product {uuid: { uuid }, name: { name }, length: { length }}), (assay:" + RTPCR_ASSAY +" {uuid: { assay_uuid }}), (assay)-[:generates]->(pcr), (pcr)-[:aligns_to]->(ampReg)"
            else:
                raise Exception("Invalid alignment type: {0}".format(self.alignmentType))

        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(primer1_uuid=primer1_uuid,primer2_uuid=primer2_uuid,reg1_uuid=reg1_uuid,reg2_uuid=reg2_uuid,ampReg_uuid=amplifiedReg_uuid,uuid=uuid,name=name,length=length,assay_uuid=assay_uuid)
        return uuid

    def createSequenceAlteration(self, region_uuid, alt_label, **kwargs):
        region = self._getNodeByUUID(label=KNOWLEDGE_BASE_NODE,uuid=region_uuid)
        wbatch = neo4j.WriteBatch(self.gdb)
        params = {k:v for k,v in kwargs.items() if v is not None}
        params['uuid'] = self._getNewUUID()
        alt_node = wbatch.create(node(params))
        wbatch.add_labels(alt_node, KNOWLEDGE_BASE_NODE)
        wbatch.add_labels(alt_node, SEQUENCE_ALTERATION)
        wbatch.add_labels(alt_node, alt_label)
        wbatch.create(rel(region, HAS_ALTERATION, alt_node, {}))
        wbatch.submit()
        return params['uuid']

    def createShortGeneticVariation(self, region_uuid, sgv_label, **kwargs):
        region = self._getNodeByUUID(label=KNOWLEDGE_BASE_NODE,uuid=region_uuid)
        wbatch = neo4j.WriteBatch(self.gdb)
        uuid = self._getNewUUID()
        var_node = wbatch.create(node(uuid=uuid, **kwargs))
        wbatch.add_labels(var_node, KNOWLEDGE_BASE_NODE)
        wbatch.add_labels(var_node, SHORT_GENETIC_VARIATION)
        wbatch.add_labels(var_node, sgv_label)
        wbatch.create(rel(region, HAS_SHORT_GENETIC_VARIATION, var_node, {}))
        wbatch.submit()
        return uuid

    def createCopyNumberVariation(self, target_uuid_list, cnv_label, **kwargs):
        wbatch = neo4j.WriteBatch(self.gdb)
        params = {}
        uuids = []
        for k,v in kwargs.iteritems():
            if v is not None:
                params[k] = v
        
        for target_uuid in target_uuid_list:
            query_text = "match (t:%s {uuid: { target_uuid }}) create (t)-[:%s]->(v:%s:%s:%s { params })" % (KNOWLEDGE_BASE_NODE, HAS_COPY_NUMBER_VARIATION, KNOWLEDGE_BASE_NODE, COPY_NUMBER_VARIATION, cnv_label)
            print query_text
            new_uuid = self._getNewUUID()    
            params['uuid'] = new_uuid
            uuids.append(new_uuid)
            print "params:", params
            wbatch.append_cypher(query_text, {'target_uuid': target_uuid, 'params': params})
        wbatch.submit()
        return uuids

    def createRawData(self, target_genid=None, data_link=None):
        
        wbatch = neo4j.WriteBatch(self.gdb)
        params = {}
        params['uuid'] = self._getNewUUID()
        if data_link is not None:
            params['data_link'] = data_link
        raw_data_node = wbatch.create(node(params))
        wbatch.add_labels(raw_data_node, RAW_DATA)
        if target_genid:
            target_node = self._getNodeByGenid(label=BIOENTITY,genid=target_genid)
            wbatch.create(rel(target_node, HAS_RAW_DATA, raw_data_node))
        wbatch.submit()
        return params['uuid']

    def getAnalysisRawData(self, analysis_uuid):
        query_text = "match (a:analysis {uuid: { analysis_uuid }})<-[:has_analysis]-(r:raw_data) return r.uuid"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(analysis_uuid=analysis_uuid)
        return res

    def addRawDataTargetGenid(self, raw_data_uuid, target_genid):
        target_node = self._getNodeByGenid(label=BIOENTITY,genid=target_genid)
        raw_data_node = self._getNodeByUUID(label=RAW_DATA,uuid=raw_data_uuid)
        wbatch = neo4j.WriteBatch(self.gdb)
        wbatch.create(rel(target_node, HAS_RAW_DATA, raw_data_node))
        wbatch.submit()
        return True

    def addRawDataTargetGenid_batch(self, raw_data_uuid, target_genid_list):
        target_nodes = self._getNodeByGenid_batch(label=BIOENTITY,genid_list=target_genid_list)
        raw_data_node = self._getNodeByUUID(label=RAW_DATA,uuid=raw_data_uuid)
        wbatch = neo4j.WriteBatch(self.gdb)
        genids_not_found = []
        for genid,t in target_nodes.iteritems():
            if t is not None:
                wbatch.create(rel(t, HAS_RAW_DATA, raw_data_node))
            else:
                genids_not_found.append(genid)
        wbatch.submit()
        return genids_not_found

    def createAnalysis(self, refset_label=None, target_uuid=None, target_genid=None, data_link=None):
        if (target_uuid is None) == (target_genid is None):
            raise Exception("Exactly one of the following parameters must be specified: target_uuid, target_genid ")
        
        if target_genid is not None:
            target_node = self._getNodeByGenid(label=BIOENTITY,genid=target_genid)
        else:
            target_node = self._getNodeByUUID(label=RAW_DATA,uuid=target_uuid)

        wbatch = neo4j.WriteBatch(self.gdb)
        params = {}
        params['uuid'] = self._getNewUUID()
        if refset_label is not None:
            params['refset_label'] = refset_label
        if data_link is not None:
            params['data_link'] = data_link
        analysis_node = wbatch.create(node(params))
        wbatch.add_labels(analysis_node, ANALYSIS)
        wbatch.create(rel(target_node, HAS_ANALYSIS, analysis_node))
        wbatch.submit()
        return params['uuid']

    def setAnalysisRefsetLabel(self, analysis_uuid, refset_label):
        query_text = "match (a:analysis) where a.uuid = { uuid } set a.refset_label = { label }"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=analysis_uuid,label="A_" + refset_label)
        return

    def setAnalysisReftypeLabel(self, analysis_uuid, reftype_label):
        query_text = "match (a:analysis) where a.uuid = { uuid } set a.reftype_labels = { label }"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=analysis_uuid,label=reftype_label)
        return

    def getGeneUUIDsFromRegion(self, region_uuid):
        query_text = "match (n:region) where n.uuid = { region_uuid } match (n)-[r:part_of]->(g:gene) return g.uuid"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(region_uuid=region_uuid)
        return [x[0] for x in res]

    def deleteSequenceAlteration(self, uuid):
        query_text = "match (n:sequence_alteration) where n.uuid = { uuid } match (n)-[r]-() where type(r) <> 'has_alteration' return count(r)"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        if res[0][0] > 0:
            raise Exception("Cannot delete, alteration is being referenced by at least one other object")
        query_text = "match (n:sequence_alteration {uuid: { uuid }})-[r:has_alteration]-() delete r, n"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)

    def deleteShortGeneticVariation(self, uuid):
        query_text = "match (n:short_genetic_variation) where n.uuid = { uuid } match (n)-[r]-() where type(r) <> 'has_short_genetic_variation' return count(r)"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        if res[0][0] > 0:
            raise Exception("Cannot delete, variation is being referenced by at least one other object")
        query_text = "match (n:short_genetic_variation {uuid: { uuid }})-[r:has_short_genetic_variation]-() delete r, n"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)

    def deleteCopyNumberVariation(self, uuid):
        query_text = "match (n:copy_number_variation) where n.uuid = { uuid } match (n)-[r]-() where type(r) <> 'has_copy_number_variation' return count(r)"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        if res[0][0] > 0:
            raise Exception("Cannot delete, copy number variation is being referenced by at least one other object")
        query_text = "match (n:copy_number_variation {uuid: { uuid }})-[r:has_copy_number_variation]-() delete r, n"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)

    def getRegionFromChild(self, uuid, label):
        query_text = "match (n:" + label + ") where n.uuid = { uuid } match (n)<-[]-(r:region) where not(r:gene) return r.uuid"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        try:
            return res[0][0]
        except:
            return None

    def deleteRegion(self, uuid):
        query_text = "match (n:region) where n.uuid = { uuid } match (n)-[r]-() where type(r) <> 'part_of' return count(r)"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        if res[0][0] == 0:
            query_text = "match (n:region) where n.uuid = { uuid } match (n)-[r:part_of]->() delete r"
            query = neo4j.CypherQuery(self.gdb, query_text)
            res = query.execute(uuid=uuid)
            query_text = "match (n:region) where n.uuid = { uuid } delete n"
            query = neo4j.CypherQuery(self.gdb, query_text)
            res = query.execute(uuid=uuid)

    def applyLabelToNodes(self, expQuery, labelQuery, label, parameters):
        # N.B. the ANALYSIS_LABEL_PREFIX + PREFIX_SEPARATOR is prepended to the label
        print "Applying label %s, expQuery: %s, labelQuery: %s, parameters: %s" % (ANALYSIS_LABEL_PREFIX + PREFIX_SEPARATOR + label, expQuery, labelQuery, parameters)
        query_text = "%s %s set x:%s" % (expQuery, labelQuery, ANALYSIS_LABEL_PREFIX + PREFIX_SEPARATOR + label)
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(**parameters)

    def getNodesFromQuery(self, expQuery, labelQuery, parameters, reftypeLabel):
        print "Retreving nodes through expQuery: %s, labelQuery: %s, parameters: %s" % (expQuery, labelQuery, parameters)
        query_text = "%s %s with x match (x)-[*0..1]->(y:%s) return y.uuid" % (expQuery, labelQuery, reftypeLabel)
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(**parameters)
        if len(res):
            return [x[0] for x in res]
        else:
            return []

    def getLabeledNodes(self, label, targetLabel):
        query_text = "match (x:%s)-[*0..1]->(y:%s) return y.uuid" % (ANALYSIS_LABEL_PREFIX + PREFIX_SEPARATOR + label, targetLabel)
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute()
        if len(res):
            return [x[0] for x in res]
        else:
            return []

    def getGenidListFromGenidPatterns(self, genid_list):
        query_text = "match (b:Bioentity) where b.identifier =~ { genid_regex } return b.identifier"
        genid_regex = self._convertGenidToCypherRegex(genid_list)
        genid_regex='|'.join(genid_regex)
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(genid_regex=genid_regex)
        return [x[0] for x in res]

#### Note about annotations
# 1st version (now obsolete):
# -refset labels always denote region nodes
# -to determine an annotation reference, one must know the region node and the type of phenomenon one wishes to take into account, e.g. sequence_alteration, short genetic variation, copy number variation etc. (this is named the 'reftype')
# -there must exist a relationship between the region node and the phenomenon node (whose label is the reftype)
#
# 2nd version (current):
# -refset labels (A) usually denote region nodes (for phenomena that can be captured by looking at "whatever is happening in that region", e.g. sequence alterations), but might (B) occasionally denote the phenomenon node itself (as it is the case with SNPs - for which one does not simply look at the region, but actually looks for a specific SNP allele)
# -the relationship between the region node and the phenomenon node is optional, so that also case (B) can be covered (region and phenomenon are the same node)

    def getAnnotationNew_fromSamples(self, genid_list, ref_type_labels):
        # from Bioentities with the specified genids, go to analyses
        # filter analyses based on ref_type_labels
        # return each analysis + its samples
        query1_text = "match (b:Bioentity)-[:has_raw_data]->(r:raw_data)-[:has_analysis*0..]->()-[:has_analysis]->(a:analysis) where b.identifier =~ { genid_regex } and length(filter(z in a.reftype_labels where z in { reftype_labels })) > 0 return a.uuid, a.refset_label, collect(b.identifier)"
        query1 = neo4j.CypherQuery(self.gdb, query1_text)
        genid_regex = '|'.join(self._convertGenidToCypherRegex(genid_list))
        res1 = query1.execute(genid_regex=genid_regex,reftype_labels=ref_type_labels)
        
        analyses = [{'uuid': row[0], 'refset_label': row[1], 'samples': row[2], 'annotations': [], 'refset': []} for row in res1]

        # retrieve all annotations between one of the alt.sites taken into account in the given analysis
        # (i.e., identified by means of the refset_label) and one of the bioentities requested
        query2_text = "match (r:%s)-[*0..1]->(x:%s)<-[:has_reference]-(a:annotation)<-[:has_annotation]-(b:Bioentity), (a)<-[:generates_annotation]-(an:analysis) using index b:Bioentity(identifier) where b.identifier in { genids } and an.uuid = { an_uuid } return r.uuid, x.uuid, b.identifier"
        # retrieve all regions (i.e., all references) associated with the given analysis
        query3_text = "match (r:%s) return r.uuid"
        
        rbatch = neo4j.ReadBatch(self.gdb)
        for an in analyses:
            print "Analysis:", an
            rbatch.append_cypher(query2_text % (an['refset_label'],'|'.join(ref_type_labels)), {'genids': an['samples'], 'an_uuid': an['uuid']})
            rbatch.append_cypher(query3_text % (an['refset_label']))
        res23 = rbatch.submit()
        
        # the result is a list
        # each item in the list is a dictionary containing:
        # -the analysis uuid
        # -the refset label
        # -the refset
        # -the samples
        # -the annotations (if any)
        for i in xrange(0, len(analyses)):
            # the following is to fix what IMHO is a *major* bug (or inconsistent behaviour at the very least):
            # if a query returns a single row as a result,
            # then its result is no longer a list of records, but a single record!
            if not isinstance(res23[2*i], list):
                res23[2*i] = [res23[2*i]]
            analyses[i]['annotations'] = [row.values for row in res23[2*i] if row] if res23[2*i] else []
            analyses[i]['refset'] = [row[0] for row in res23[2*i+1]]

        return analyses

    def getAnnotationNew_fromAltSites(self, altsites_list, ref_type_labels):
        # get altsites by uuid and their analysis labels ("A_*")
        query1_text = "match (r:kb_node) using r:kb_node(uuid) where r.uuid in { uuid_list } return r.uuid, filter(z in labels(r) where left(z,2) = 'A_')"
        query1 = neo4j.CypherQuery(self.gdb, query1_text)
        print "run query1"
        res1 = query1.execute(uuid_list=altsites_list)
        print "done"
        # build a map of refsets
        refset = {}
        for row in res1:
            for label in row[1]:
                if label not in refset:
                    refset[label] = []
                refset[label].append(row[0])
        # for each of the refset labels, consider the corresponding analyses, and return them, filtered according to the provided ref_type_labels, together with the samples in the analysis
        query2_text = "match (a:analysis)<-[:has_analysis]-()<-[:has_analysis*0..]-(r:raw_data)<-[:has_raw_data]-(b:Bioentity) where a.refset_label in { refset_labels } and length(filter(z in a.reftype_labels where z in { reftype_labels })) > 0 return a.uuid, a.refset_label, collect(b.identifier)"
        query2 = neo4j.CypherQuery(self.gdb, query2_text)
        print "run query2"
        res2 = query2.execute(refset_labels=refset.keys(),reftype_labels=ref_type_labels)
        print "done"

        analyses = [{'uuid': row[0], 'refset_label': row[1], 'samples': row[2], 'annotations': [], 'refset': refset[row[1]]} for row in res2]

        # query that takes the alt.sites corresponding to the given analysis (filtered so that we only consider those
        # that were actually requested) and the bioentities linked to the given analysis, and returns all annotations between
        # those two sets (if any)
        query3_text = "match (r:kb_node)-[*0..1]->(x:%s)<-[:has_reference]-(a:annotation)<-[:has_annotation]-(b:Bioentity), (a)<-[:generates_annotation]-(an:analysis) using index r:kb_node(uuid) where r.uuid in { altsites_uuid } and an.uuid = { an_uuid } return r.uuid, x.uuid, b.identifier" % ('|'.join(ref_type_labels))
        rbatch = neo4j.ReadBatch(self.gdb)
        for an in analyses:
            rbatch.append_cypher(query3_text, {'altsites_uuid': an['refset'], 'an_uuid': an['uuid']})
        print "run query3"
        res3 = rbatch.submit()
        print "done"
        
        # the result is a list
        # each item in the list is a dictionary containing:
        # -the analysis uuid
        # -the refset label
        # -the refset
        # -the samples
        # -the annotations (if any)

        # the following is to fix what IMHO is a bug (or inconsistent behaviour at the very least):
        # if only one query is inserted into the batch and that query returns a single row as a result,
        # then the result returned by .submit() is no longer a list of lists, but a list with only one
        # (non-list) element

        for i in xrange(0, len(analyses)):
            # the following is to fix what IMHO is a *major* bug (or inconsistent behaviour at the very least):
            # if a query returns a single row as a result,
            # then its result is no longer a list of records, but a single record!
            if not isinstance(res3[i], list):
                res3[i] = [res3[i]]
            analyses[i]['annotations'] = [row.values for row in res3[i] if row] if res3[i] else []

        return analyses

    def getAnnotationNew_fromSamplesAndAltSites(self, genid_list, altsites_list, ref_type_labels):
        # get altsites by uuid and their analysis labels ("A_*")
        query1_text = "match (r:kb_node) using index r:kb_node(uuid) where r.uuid in { uuid_list } return r.uuid, filter(z in labels(r) where left(z,2) = 'A_')"
        query1 = neo4j.CypherQuery(self.gdb, query1_text)
        res1 = query1.execute(uuid_list=altsites_list)
        # build a map of refsets
        refset = {}
        for row in res1:
            for label in row[1]:
                if label not in refset:
                    refset[label] = []
                refset[label].append(row[0])
        # for each of the refset labels, consider the corresponding analyses, and return them, filtered according to the provided ref_type_labels, together with the samples in the analysis
        genid_regex = '|'.join(self._convertGenidToCypherRegex(genid_list))
        query2_text = "match (a:analysis)<-[:has_analysis]-()<-[:has_analysis*0..]-(r:raw_data)<-[:has_raw_data]-(b:Bioentity) where a.refset_label in { refset_labels } and b.identifier =~ { genid_regex } and length(filter(z in a.reftype_labels where z in { reftype_labels })) > 0 return a.uuid, a.refset_label, collect(b.identifier)"
        query2 = neo4j.CypherQuery(self.gdb, query2_text)
        res2 = query2.execute(refset_labels=refset.keys(),reftype_labels=ref_type_labels,genid_regex=genid_regex)
        analyses = [{'uuid': row[0], 'refset_label': row[1], 'samples': row[2], 'annotations': [], 'refset': refset[row[1]]} for row in res2]


        # retrieve annotations whose reference is in refset, whose sample is in genid_list, whose reference type is one of ref_type_labels
        # return annotations grouped by analysis
        query3_text = "match (r:kb_node)-[*0..1]->(x:%s)<-[:has_reference]-(a:annotation)<-[:has_annotation]-(b:Bioentity), (a)<-[:generates_annotation]-(an:analysis) using index r:kb_node(uuid) using index b:Bioentity(identifier) where r.uuid in { altsites_uuid } and an.uuid = { an_uuid } and b.identifier in { genids } return r.uuid, x.uuid, b.identifier"  % ('|'.join(ref_type_labels))

        #print query_text % ('|'.join(ref_type_labels))
        #print genid_list, altsites_list, ref_type_labels
        rbatch = neo4j.ReadBatch(self.gdb)
        for an in analyses:
            rbatch.append_cypher(query3_text, {'altsites_uuid': an['refset'], 'an_uuid': an['uuid'], 'genids': an['samples']})
        res3 = rbatch.submit()

        for i in xrange(0, len(analyses)):
            # the following is to fix what IMHO is a *major* bug (or inconsistent behaviour at the very least):
            # if a query returns a single row as a result,
            # then its result is no longer a list of records, but a single record!
            if not isinstance(res3[i], list):
                res3[i] = [res3[i]]
            analyses[i]['annotations'] = [row.values for row in res3[i] if row] if res3[i] else []

        return analyses

    '''def deleteCopyNumberVariation(self, uuid):
        wbatch = neo4j.WriteBatch(self.gdb)
        # count how many relationships exist between the region node and some other node (besides the one with the cnv node + the one with the gene node)
        # N.B. when the region node does not exist, the query will return no results
        query_text = "match (n:copy_number_variation)<-[:has_copy_number_variation]-(r:region) where n.uuid = { uuid } and not(r:gene) optional match (r)-[rr]-(x) where type(rr) <> 'part_of' and x <> n return r.uuid, count(x)"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)

        query_text = "match (n:copy_number_variation) where n.uuid = { uuid } match (n)-[r:has_copy_number_variation]-() delete r, n"
        wbatch.append_cypher(query_text, {'uuid': uuid})
        # if the count is 0, delete region (region is not used by anything else)
        # N.B. we check whether there are any results at all or not (that is the case when the region node does not exist)
        if len(res) > 0 and res[0][1] == 0:
            query_text = "match (r:kb_node:region)-[rr]-() where r.uuid = { uuid } delete rr, r"
            wbatch.append_cypher(query_text, {'uuid': res[0][0]})
        wbatch.submit()'''

    def getPatientUuidFromCollection(self, genid):
        l = len(genid)
        if l == 7:
            genid = genid + "0" * 19
        elif l != 26:
            raise Exception("Invalid genid")
        query_text = "match (:Collection {identifier: { genid }})-[:belongs]->(:IC)<-[:signed]-(pt:Patient) return pt.identifier"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(genid=genid)
        return res[0][0] if len(res) > 0 else None

    def getAllAnnotationsForReftype(self, reftype):
        query_text = "match (a:"+BIOENTITY+")-[:"+ HAS_ANNOTATION + "]->(b:"+ANNOTATION+")-[:"+HAS_REFERENCE+"]->(c:"+KNOWLEDGE_BASE_NODE+":"+reftype+") return b.uuid as annot_graph_uuid, b.db_id as db_id, a.identifier as idSample"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute()
        return res
