### GRAPH-BASED UTILITY FUNCTIONS
from py2neo import neo4j, node, rel
from django.conf import settings
from uuid import uuid4
import collections

neo4j._add_header('X-Stream', 'true;format=pretty')

#### labels ####
# -- nodes
BIOENTITY = 'Bioentity'
CHROMOSOME = 'chromosome'
GENE = 'gene'
TRANSCRIPT = 'transcript'
EXON = 'exon'
INTRON = 'intron'
BASE = 'base'
WILD_TYPE = 'wild_type'
REGION = 'region'
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
KNOWLEDGE_BASE_NODE = 'kb_node'
RAW_DATA = 'raw_data'
ANALYSIS = 'analysis'
ANNOTATION = 'annotation'
# -- relationships
PART_OF = 'part_of'
TRANSCRIBED_FROM = 'transcribed_from'
INTEGRAL_PART_OF = 'integral_part_of'
HAS_QUALITY = 'has_quality'
POSITION_OF = 'position_of'
IS_A = 'is_a'
VARIANT_OF = 'variant_of'
HAS_ALTERATION = 'has_alteration'
HAS_SHORT_GENETIC_VARIATION = 'has_short_genetic_variation'
HAS_COPY_NUMBER_VARIATION = 'has_copy_number_variation'
HAS_WILD_TYPE = 'has_wild_type'
HAS_ANNOTATION = 'has_annotation'
HAS_REFERENCE = 'has_reference'
HAS_RAW_DATA = 'has_raw_data'
HAS_ANALYSIS = 'has_analysis'
#### end labels ####

Gene = collections.namedtuple('Gene', 'uuid symbol strand chrom start end ac')


class GenomicAnalysis():
    def __init__(self):
        self.gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
        return

    def _getNewUUID(self):
        return uuid4().hex

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

    def _getNodeByUUID(self, label, uuid):
        query_text = "match (n:" + label + ") where n.uuid = { uuid } return n;"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        if len(res) > 0:
            return res[0][0]
        else:
            raise Exception("Node :{0}(UUID={1}) not found".format(label, uuid))


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


    def createAnalysis(self, target_uuid=None, target_genid=None, data_link=None, results_uuid=None, description_uuid=None):
        if (target_uuid is None) == (target_genid is None):
            raise Exception("Exactly one of the following parameters must be specified: target_uuid, target_genid ")
        
        if target_genid is not None:
            target_node = self._getNodeByGenid(label=BIOENTITY,genid=target_genid)
        else:
            target_node = self._getNodeByUUID(label=RAW_DATA,uuid=target_uuid)

        wbatch = neo4j.WriteBatch(self.gdb)
        params = {}
        params['uuid'] = self._getNewUUID()
        if data_link is not None:
            params['data_link'] = data_link
        if results_uuid is not None:
            params['results_uuid'] = results_uuid
        if description_uuid is not None:
            params['description_uuid'] = description_uuid
        analysis_node = wbatch.create(node(params))
        wbatch.add_labels(analysis_node, ANALYSIS)
        wbatch.create(rel(target_node, HAS_ANALYSIS, analysis_node))
        wbatch.submit()
        return params['uuid']

    def deleteAnalysis(self, uuid):
        if uuid is None:
            return
        query_text = "match (a:analysis {uuid: { uuid }})<-[r:has_analysis]-(x:raw_data) optional match (a)-[r1:generates_annotation]->(an:annotation) delete r, r1, an, a;"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(uuid=uuid)
        return
