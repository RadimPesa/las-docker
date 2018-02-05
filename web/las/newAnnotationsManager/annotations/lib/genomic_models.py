from annotations.lib.graph_utils import *
from annotations.lib.utils import *
import annotations.models
from Bio import Seq, SeqUtils
import copy
import sys

import annotations.lib.UTA_lasannotations as UTAlas
import hgvs.parser, hgvs.posedit, hgvs.edit, hgvs.location, hgvs.variantmapper

from annotations.lib.exceptions import *

class KBReference():
    _graph_utils = GenomeGraphUtility()

    @staticmethod
    def byUuid(uuid):
        results = KBReference._graph_utils.getKBNodeLabelsByUuidList([uuid])
        if len(results) == 0:
            return None
        uuid = results[0][0]
        labels = results[0][1]
        if 'sequence_alteration' in labels:
            model = SequenceAlteration
        elif 'short_genetic_variation' in labels:
            model = ShortGeneticVariation
        elif 'copy_number_variation' in labels:
            model = CopyNumberVariation
        else:
            return None
        x = model()
        x.byUuid(uuid)
        return x

class Treatment():
    _ggu = GenomeGraphUtility()
    def __init__(self):
        self._params = {'name': None}
        self._uuid = None
        self._in_graph = None

    def set(self, name):
        self._params['name'] = name

    def save(self):
        if self._params['name'] is not None:
            if self.exists() == True:
                return
            self._uuid = self._ggu.createTreatment(self._params['name'])
            self._in_graph = True

    def exists(self):
        if self._in_graph is None:
            self._checkExists()
        return self._in_graph

    def byUuid(self, uuid):
        res = self._ggu.getTreatment_byUuid(uuid)
        if res != []:
            self._uuid = uuid
            self._params['name'] = res[0][1]
            self._in_graph = True

    def getUuid(self):
        return self._uuid if self.exists() else None

    def getInfo(self):
        if self.exists():
            return {'uuid': self._uuid, 'name': self._params['name']}

    def _checkExists(self):
        self._uuid = None
        self._in_graph = None
        if self._params['name'] is None:
            return
        res = self._ggu.getTreatment_byName(self._params['name'])
        if res != []:
            self._uuid = res[0][0]
            self._in_graph = True

    def delete(self):
        if self.exists() == False:
            return
        self._ggu.deleteTreatment(self._uuid)
        self._uuid = None
        self._in_graph = False

class DrugResponse():
    _ggu = GenomeGraphUtility()
    _mandatory_parameters = ['treatment_uuid', 'crit_label', 'resp_class_label']
    def __init__(self):
        self._params = {'treatment_uuid': None,
                        'treatment_name': None,
                        'crit_obj': None,
                        'crit_label': None,
                        'value': None,
                        'resp_class_obj': None,
                        'resp_class_label': None}
        self._uuid = None
        self._in_graph = None

    def set(self, treatment_name, criterion_obj, value):
        t = Treatment()
        t.set(treatment_name)
        treatment_info = t.getInfo()
        if treatment_info['uuid'] is None:
            raise Exception("Treatment not found")
        self._params['treatment_uuid'] = treatment_info['uuid']
        self._params['treatment_name'] = treatment_info['name']
        self._params['crit_obj'] = criterion_obj
        self._params['crit_label'] = criterion_obj.label
        self._params['value'] = value
        try:
            resp_class_obj = criterion_obj.getResponseClass(value)
        except:
            raise Exception("No matching response class found with current criterion")
        self._params['resp_class_obj'] = resp_class_obj
        self._params['resp_class_label'] = resp_class_obj.shortName

    def _checkValid(self):
        for x in self._mandatory_parameters:
            if self._params[x] is None:
                raise Exception('Missing required parameter: %s' % x)
    
    def exists(self):
        if self._in_graph is None:
            self._checkExists()
        return self._in_graph

    def _checkExists(self):
        self._uuid = None
        self._in_graph = None
        self._checkValid()
        res = self._ggu.getDrugResponse_byTreatment(self._params['treatment_uuid'], self._params['crit_label'], self._params['resp_class_label'])
        if res is not None:
            self._uuid = res
            self._in_graph = True
        else:
            self._in_graph = False

    def save(self):
        self._checkValid()
        if self.exists() == True:
            return
        self._uuid = self._ggu.createDrugResponse(self._params['treatment_uuid'], self._params['crit_label'], self._params['resp_class_label'])
        self._in_graph = True

    def delete(self):
        if self.exists() == False:
            return
        self._ggu.deleteDrugResponse(self._uuid)
        self._uuid = None
        self._in_graph = False

    def getUuid(self):
        return self._uuid if self.exists() else None

    def getInfo(self):
        if self.exists():
            return {'uuid': self._uuid, 'treatment_uuid': self._params['treatment_uuid'], 'treatment_name': self._params['treatment_name'], 'crit_label': self._params['crit_label'], 'resp_class_label': self._params['resp_class_label']}

    def getDrugResponseCriterionObject(self):
        return self._params['crit_obj']

    def getDrugResponseClassObject(self):
        return self._params['resp_class_obj']

    def byUuid(self, uuid):
        res = self._ggu.getDrugResponse_byUuid(uuid)
        if res is not None:
            self._uuid = uuid
            _params = {}
            _params['treatment_uuid'] = res[1]
            _params['treatment_name'] = res[2]
            _params['crit_label'] = res[3]
            _params['resp_class_label'] = res[4]
            try:
                _params['crit_obj'] = annotations.models.DrugResponseCriterion.objects.get(label=res[3])
            except:
                raise Exception("DrugResponseCriterion object with label '%s' not found" % res[3])
            try:
                _params['resp_class_obj'] = annotations.models.DrugResponseClass.objects.get(shortName=res[4])
            except:
                raise Exception("DrugResponseClass object with label '%s' not found" % res[4])
            self._params.update(_params)
            self._in_graph = True

class PCRProduct():
    def __init__(self):
        self.uuid = None
        self.name = None
        self.length = None
        self.primer1_uuid = None
        self.primer2_uuid = None
        self.alignmentType = None
        self.reg1_uuid = None
        self.reg2_uuid = None
        self.amplifiedReg_uuid = None
        self.p1_is_minus_or_3p = False
        self.primers_unknown = False
        self.ampl_reg_ref = None
        self.ampl_reg_start = None
        self.ampl_reg_end = None

    def createSimpleProduct(self):
        if self.name is None or self.length is None:
            raise Exception("Attributes 'name' and 'length' cannot be None")

        # primer regions cannot be null unless primers_unknown flag is set
        if self.primers_unknown == False and (None in [self.reg1_uuid, self.reg2_uuid] or None in [self.primer1_uuid, self.primer2_uuid]):
            raise Exception("'reg1_uuid', 'reg2_uuid', 'primer1_uuid' and 'primer2_uuid' cannot be None")

        graph_utils = GenomeGraphUtility()
        
        if self.primers_unknown == False:
            # automatically compute coordinates of amplified region
            if self.alignmentType == 'genome':
                graph_utils = GenomeGraphUtility()
                res = graph_utils.getRegionInfo_byUuid([self.reg1_uuid, self.reg2_uuid])
                if len(res) != 2:
                    return False
                # match results to primers
                if res[0][0] == self.reg1_uuid:
                    info1 = res[0]
                    info2 = res[1]
                else:
                    info1 = res[1]
                    info2 = res[0]
                # same chromosome?
                if info1[1] == info2[1]:
                    # compute coordinates of amplified region
                    # -------->##########<--------
                    # s1    e1 S        E s2    e2
                    # s2    e2            s1    e1
                    # S = min (e1, e2)
                    # E = max (s1, s2)
                    start = info1[3] if info1[3][0] < info2[3][0] else info2[3]
                    end = info1[2] if info1[2][0] > info2[2][0] else info2[2]
                    #end = max(info1[3], info2[3])
                    #start = min(info1[2], info2[2])
                    region_list = graph_utils.getRegionByCoords(info1[1], start, end)
                    # determine plus/minus end (based on alignment strand)
                    self.p1_is_minus_or_3p = info1[4] == '-'
                    # amplified region already exists?
                    if len(region_list) == 0:
                        # no, create it
                        self.amplifiedReg_uuid = graph_utils.createRegion(info1[1], start, end)
                    else:
                        # yes, use it
                        self.amplifiedReg_uuid = region_list[0]
                    return True
                else:
                    raise Exception("Cannot create a simple PCR product because primers align to genomic regions of different chromosomes")
            
            elif self.alignmentType == 'transcriptome':
                graph_utils = GenomeGraphUtility()
                res = graph_utils.getTranscriptregionInfo_byUuid([self.reg1_uuid, self.reg2_uuid])
                if len(res) != 2:
                    return False
                # match results to primers
                if res[0][0] == self.reg1_uuid:
                    info1 = res[0]
                    info2 = res[1]
                else:
                    info1 = res[1]
                    info2 = res[0]
                # same tx?
                if info1[1] == info2[1]:
                    # compute coordinates of amplified region
                    # compute coordinates of amplified region
                    # -------->##########<--------
                    # s1    e1 S        E s2    e2
                    # s2    e2            s1    e1
                    # S = min (e1, e2)
                    # E = max (s1, s2)
                    start = info1[3] if info1[3][0] < info2[3][0] else info2[3]
                    end = info1[2] if info1[2][0] > info2[2][0] else info2[2]
                    #end = max(info1[3], info2[3])
                    #start = min(info1[2], info2[2])
                    region_list = graph_utils.getTranscriptregionByCoords(info1[1], start, end)
                    # determine 5p/3p end: if start1 > end2 => p1 is at the 3p end
                    self.p1_is_minus_or_3p = info1[2] > info2[3]
                    # amplified region already exists?
                    if len(region_list) == 0:
                        # no, create it
                        self.amplifiedReg_uuid = graph_utils.createTranscriptregion(info1[1], start, end)
                    else:
                        # yes, use it
                        self.amplifiedReg_uuid = region_list[0]
                    return True
                else:
                    raise Exception("Cannot create a simple PCR product because primers align to transcript regions of different transcripts")
            else:
                raise Exception("Invalid alignment type: {0}".format(self.alignmentType))
        else:
            # coordinates of amplified region must have been manually specified
            if self.ampl_reg_ref is None or self.ampl_reg_start is None or self.ampl_reg_end is None:
                raise Exception("If primers are unknown, values must be provided for 'ampl_reg_ref', 'ampl_reg_start' and 'ampl_reg_end'")
            
            _start = [self.ampl_reg_start, self.ampl_reg_end - self.length]
            _end = [self.ampl_reg_start + self.length, self.ampl_reg_end]

            if self.alignmentType == 'genome':
                # amplified region already exists?
                region_list = graph_utils.getRegionByCoords(self.ampl_reg_ref, _start, _end)
                if len(region_list) == 0:
                    # no, create it
                    self.amplifiedReg_uuid = graph_utils.createRegion(self.ampl_reg_ref, _start, _end)
                else:
                    # yes, use it
                    self.amplifiedReg_uuid = region_list[0]

            elif self.alignmentType == 'transcriptome':
                # amplified region already exists?
                region_list = graph_utils.getTranscriptregionByCoords(self.ampl_reg_ref, _start, _end)
                if len(region_list) == 0:
                    # no, create it
                    self.amplifiedReg_uuid = graph_utils.createTranscriptregion(self.ampl_reg_ref, _start, _end)
                else:
                    # yes, use it
                    self.amplifiedReg_uuid = region_list[0]

            else:
                raise Exception("Invalid alignment type: {0}".format(self.alignmentType))

    def save(self):
        if self.amplifiedReg_uuid is None:
            raise Exception("Amplified region is undefined, call 'createSimpleProduct' first")

        if self.alignmentType not in ['genome', 'transcriptome']:
            raise Exception("Invalid alignment type: {0}".format(self.alignmentType))
            
        graph_utils = GenomeGraphUtility()
        self.uuid = graph_utils.createPCRProduct(self.name, self.length, self.primer1_uuid, self.reg1_uuid, self.primer2_uuid, self.reg2_uuid, self.amplifiedReg_uuid, self.alignmentType, self.p1_is_minus_or_3p, self.primers_unknown)

class Primer():
    def __init__(self, name=None, length=None):
        self.name = name
        self.alignments = []
        self._tmp_alignments = []
        self.length = length
        self.uuid = None

    def addAlignment(self, ref, start, end, strand, alignmentType):
        if self.length > end - start:
            raise Exception("Invalid alignment: specified interval is too short")
        _start = [start, end - self.length]
        _end = [start + self.length, end]
        self._tmp_alignments.append((ref, _start, _end, strand, alignmentType, self.length))

    def getAlignments(self):
        return self.alignments

    def save(self):
        print "Primer.save"
        graph_utils = GenomeGraphUtility()
        if not self.uuid:
            self.uuid = graph_utils.createPrimer(self.name, self.length)
        alignments_found = graph_utils.addPrimerAlignment(self.uuid, self._tmp_alignments)
        self.alignments_not_found = [x for x in self._tmp_alignments if not x in alignments_found]
        self.byUuid(self.uuid)

    def byUuid(self, uuid):
        print "Primer.byUuid"
        graph_utils = GenomeGraphUtility()
        res = graph_utils.getPrimerByUuid(uuid)
        if len(res) > 0:
            self.uuid = uuid
            self.name = res[0][1]
            self.length = res[0][2]
            self.alignments = []
            for aligns in res[0][3]:
                if aligns[0] is None:
                    continue
                self.alignments.append({'uuid': aligns[0], 'reference': aligns[1], 'start': aligns[2], 'end': aligns[3], 'strand': aligns[4], 'gene_symbol': aligns[5], 'type': aligns[6]})
        else:
            raise Exception("Primer not found")


    def byAlignmentUuid(self, uuid):
        graph_utils = GenomeGraphUtility()
        res = graph_utils.getPrimerByAlignmentUuid(uuid)
        if len(res) > 0:
            self.uuid = res[0][0]
            self.name = res[0][1]
            self.length = res[0][2]
            self.alignments = []
            for aligns in res[0][3]:
                self.alignments.append({'uuid': aligns[0], 'reference': aligns[1], 'start': aligns[2], 'end': aligns[3], 'strand': aligns[4], 'gene_symbol': aligns[5], 'type': aligns[6]})

    def setTechnologies(self, labelsYes, labelsNo):
        if self.uuid:
            graph_utils = GenomeGraphUtility()
            graph_utils.setPrimerTechnologies(self.uuid, labelsYes, labelsNo)

class SNPProbe():
    _graph_utils = GenomeGraphUtility()
    def __init__(self, snp_uuid=None, name=None):
        self.snp_uuid = snp_uuid
        self.name = name
        self.uuid = None
        self._in_graph = None

    def save(self):
        if self.exists() == True:
            print "Already in graph"
        else:
            self.uuid = self._graph_utils.createSGVProbe(self.snp_uuid, self.name)
        self._in_graph = True

    def delete(self):
        if self.exists() == True:
            self._graph_utils.deleteSGVProbe(self.uuid)
        self._in_graph = False

    def byUuid(self, uuid):
        res = self._graph_utils.getSGVProbeByUuid_list([uuid])
        if len(res) > 0:
            self._in_graph = True
            self.uuid = uuid
            self.name = res[0]['probe_name']
            self.snp_uuid = res[0]['snp_uuid']
        else:
            raise Exception("Not found")

    def getInfo(self):
        return {'uuid': self.uuid, 'name': self.name, 'snp_uuid': self.snp_uuid}

    def exists(self):
        if self._in_graph is None:
            self._check_exists()
        return self._in_graph

    def _check_exists(self):
        if self.snp_uuid is not None:
            res = self._graph_utils.getSGVProbeBySGVUuid(self.snp_uuid)
            if len(res) > 0:
                self._in_graph = True
                self.uuid = res[0]['uuid']
                self.name = res[0]['probe_name']
                self.snp_uuid = res[0]['snp_uuid']
            else:
                self._in_graph = False
                self.uuid = None

class AlterationSite():
    _seq_utils_tx = RefSequence('transcriptome')
    _seq_utils_gen = RefSequence('genome')
    _graph_utils = GenomeGraphUtility()
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


    def __init__(self, data):
        self.uuid = data[0]
        self.chrom =  data[1]
        self.start =  data[2]
        self.end =  data[3]
        self.strand = data[4]
        self.gene_symbol = data[6]
        self.tx_ac = data[7]
        self.ref = data[8]
        self.start_c = data[9]
        self.offset_c = data[10]
        self.loc_p = data[11]
        if not self.ref:
            self.ref = self._seq_utils_gen.getRefSequence(chrom=self.chrom, start=self.start, length=1, strand='+') # length=self.end-self.start+1
        '''
        if self.tx_ac:
            
            # if hgvs is in cache, skip the rest of the initialization
            try:
                self._hgvscache_obj = annotations.models.HGVSCache.objects.get(graph_uuid=self.uuid, tx_ac=self.tx_ac)
                print "found in db"
                self.ref = None
                self.start_c = self._hgvscache_obj.start_c
                self.offset_c = self._hgvscache_obj.offset_c
                self.start_p = None
                self.aa = None
                return
            except Exception as e:
                self._hgvscache_obj = None
                self.ref = self._seq_utils_gen.getRefSequence(chrom=self.chrom, start=self.start, length=1, strand='+') # length=self.end-self.start+1
                print "not found in db"
                pass
            
            try:
                res = self.__map_g_to_c(chrom=self.chrom, start_g=self.start, tx_ac=self.tx_ac)
            except Exception as e:
                print (e)
                self.start_c = None
                self.offset_c = None
                self.start_p = None
                self.aa = None
                return
                       
            self.start_c = res['start_c']
            self.offset_c = res['offset']
            if self.offset_c == 0:
                self.start_p = self.start_c / 3 + (1 if self.start_c % 3 != 0 else 0)
                seq = self._seq_utils_tx.getRefSequence(self.tx_ac)
                self.aa = SeqUtils.seq3(Seq.Seq(seq[res['tx.cds_start']+(self.start_p-1)*3:res['tx.cds_start']+self.start_p*3]).translate())
            else:
                self.start_p = None
                self.aa = None
        else:
            self.start_c = None
            self.offset_c = None
            self.start_p = None
            self.aa = None
        '''

    def getLoc_g(self):
        '''
        if self._hgvscache_obj is not None:
            print "from db"
            return self._hgvscache_obj.hgvs_g
        else:
        '''
        return "chr{0}:g.{1}{2}".format(self.chrom, self.start, self.ref)

    def getLoc_c(self):
        '''
        if self._hgvscache_obj is not None:
            print "from db"
            return self._hgvscache_obj.hgvs_c
        '''
        if not self.start_c:
            return None
        if self.strand == '+':
            ref = self.ref
        else:
            ref = str(Seq.Seq(self.ref).reverse_complement())
        if self.offset_c == 0:
            pos = str(self.start_c)
        elif self.offset_c < 0:
            pos = "{0}{1}".format(self.start_c, self.offset_c)
        else:
            pos = "{0}+{1}".format(self.start_c, self.offset_c)
        return "c.{0}{1}".format(pos, ref)

    def getLoc_p(self):
        '''
        if self._hgvscache_obj is not None:
            print "from db"
            return self._hgvscache_obj.hgvs_p

        if not self.start_p:
            return "?:p.??"
        else:
            return "?:p.{0}{1}".format(self._aa_3L_to_1L.get(self.aa, self.aa), self.start_p)
        '''
        return self.loc_p

    def __map_g_to_c(self, chrom, start_g, tx_ac):
        tx = self._graph_utils.getTranscriptInfo(ac=tx_ac)
        if len(tx) == 0:
            raise Exception("Transcript not found")
        tx = tx[0]
        if tx['tx.cds_start'] is None:
            raise Exception("Cannot map, transcript is non- protein coding")
        exon_starts_g = tx['exon.starts'] # 0-based left coordinate BEWARE: Cosmic alteration start and end coordinates are left and right respectively
        exon_ends_g = tx['exon.ends'] # 0-based left coordinate
        exon_lengths = tx['exon.lengths']
        exon_id = [i for i in xrange(0, len(exon_starts_g)) if start_g >= exon_starts_g[i] and start_g <= exon_ends_g[i]]

        if len(exon_id) != 1:
            # alteration falls outside exonic region
            if tx['strand'] == '+':
                if start_g < exon_starts_g[0]:
                    # 5' of first exon
                    # reference will be c.1-XXX
                    exon_id = 0
                    sign = '-'
                    abs_offset = exon_starts_g[0] - start_g
                    start_g = exon_starts_g[0]
                elif start_g >= exon_ends_g[-1]:
                    # 3' of last exon
                    # reference will be c.N+XXX
                    exon_id = len(exon_lengths) - 1
                    sign = '+'
                    abs_offset = start_g - exon_ends_g[-1]
                    start_g = exon_ends_g[-1]
                else:
                    # between two exons, find which ones
                    exon_id, = [i for i in xrange(0, len(exon_starts_g)-1) if start_g > exon_ends_g[i] and start_g < exon_starts_g[i+1]]
                    if start_g - exon_ends_g[exon_id] > exon_starts_g[exon_id+1] - start_g:
                        # if start_g is closest to following intron, the latter must be the reference
                        # (for introns with an uneven number of nucleotides, the central nucl. is the last described with a '+'
                        exon_id += 1
                        sign = '-'
                        abs_offset = exon_starts_g[exon_id] - start_g
                        start_g = exon_starts_g[exon_id]
                    else:
                        sign = '+'
                        abs_offset = start_g - exon_ends_g[exon_id]
                        start_g = exon_ends_g[exon_id]
            else:
                if start_g > exon_ends_g[0]:
                    # 5' of first exon
                    # reference will be c.1-XXX
                    exon_id = 0
                    sign = '-'
                    abs_offset = start_g - exon_ends_g[-1]
                    start_g = exon_ends_g[0]
                elif start_g < exon_starts_g[-1]:
                    # 3' of last exon
                    # reference will be c.N+XXX
                    exon_id = len(exon_lengths) - 1
                    sign = '+'
                    abs_offset = exon_starts_g[-1] - start_g
                    start_g = exon_starts_g[-1]
                else:
                    # between two exons, find which ones
                    exon_id, = [i for i in xrange(0, len(exon_starts_g)-1) if start_g < exon_starts_g[i] and start_g > exon_ends_g[i+1]]
                    if  exon_starts_g[exon_id] - start_g > start_g - exon_ends_g[exon_id+1]:
                        # if position is closest to following intron, the latter must be the reference
                        # (for introns with an uneven number of nucleotides, the central nucl. is the last described with a '+'
                        exon_id += 1
                        sign = '-'
                        abs_offset = start_g - exon_ends_g[exon_id]
                        start_g = exon_ends_g[exon_id]
                    else:
                        sign = '+'
                        abs_offset = exon_starts_g[exon_id] - start_g
                        start_g = exon_starts_g[exon_id]

        else:
            exon_id = exon_id[0]
            sign = ''
            abs_offset = 0
        start_tx = sum([exon_lengths[i] for i in xrange(0, exon_id)])
        if tx['strand'] == '+':
            start_tx += start_g - exon_starts_g[exon_id] + 1
        else:
            start_tx += exon_ends_g[exon_id] - start_g + 1

        return {'tx_ac': tx['tx.ac'], 'start_c': start_tx - tx['tx.cds_start'], 'offset': int(sign + str(abs_offset)), 'strand': tx['strand'], 'tx.cds_start': tx['tx.cds_start']}

class SequenceAlteration(KBReference):
    _graph_label = 'sequence_alteration'
    _seq_alt_types_params = {'sub': {'params': ['ref', 'alt'], 'label': 'point_mutation'},
                        'ins': {'params': ['alt'], 'label': 'insertion'},
                        'delins': {'params': ['alt', 'num_bases'], 'label': 'indel'},
                        'del': {'params': ['num_bases'], 'label': 'deletion'},
                        'dup': {'params': ['num_bases'], 'label': 'duplication'},
                        'wt': {'params': [], 'label': 'wild_type'}
                        }
    _seq_alt_label_remap = {'point_mutation': 'sub', 'insertion': 'ins', 'indel': 'delins', 'deletion': 'del', 'duplication': 'dup', 'wild_type': 'wt'}

    _opt_params = ['ref', 'alt', 'num_bases']
    _req_params = ['chrom', 'start', 'end', 'alt_type']
    _hgvsparser = hgvs.parser.Parser()

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
                        'Val': 'V',
                        'Ter': '*'
                    }

    _seq_utils_tx = RefSequence('transcriptome')
    _seq_utils_gen = RefSequence('genome')
    _graph_utils = GenomeGraphUtility()
    _data_prov_tx = None
    _data_prov_gen = None

    _filtering_params = set(['chrom', 'start', 'end', 'gene_uuid', 'tx_uuid'])

    def __init__(self):
        self._params = { 'chrom': None,
                        'start': None,
                        'end': None,
                        'alt_type': None,
                        'alt': None,
                        'ref': None,
                        'num_bases': None,
                        'num_bases_c': None,
                        'label': None,
                        'gene_symbol': None,
                        'gene_uuid': None,
                        'gene_ac': None,
                        'tx_ac': None
                        }
        self._uuid = None
        self._in_graph = None
        self._tx_annot_source = None
        self._hgvscache_obj = None
        self._cosmic_objs = []
        self._xrefs = []
        self._hgvs_c_object = None

    @staticmethod
    def getFilteringParams():
        return copy.copy(SequenceAlteration._filtering_params)

    @staticmethod
    def getAnnotationModel():
        return annotations.models.Annotation_SequenceAlteration

    def getGraphLabel(self):
        return self._graph_label

    def _connectToDataProviders(self):
        self._data_prov_tx = UTAlas.connect(db_url='lasannotations://',graph_utils_obj=self._graph_utils,seq_utils_obj=self._seq_utils_tx)
        self._data_prov_gen = UTAlas.connect(db_url='lasannotations://',graph_utils_obj=self._graph_utils,seq_utils_obj=self._seq_utils_gen)

    def getWildType(self, chrom=None, start=None, end=None):
        chrom = chrom or self._params['chrom']
        start = start or self._params['start']
        end = end or self._params['end']
        if chrom is None or start is None or end is None:
            raise Exception("Missing required parameters: {0}, {1}, {2}".format(chrom, start, end))
        return self._graph_utils.getOrCreateWildType(chrom, start, end)

    def isWildType(self):
        return self._params['alt_type'] == 'wt'

    def exists(self):
        if self._in_graph == None:
            self._checkExists()
        return self._in_graph

    def _checkExists(self):
        self._uuid = None
        self._in_graph = None

        if self._params['alt_type'] == 'wt':
            self._uuid = self._graph_utils.getWildType(self._params['chrom'], self._params['start'], self._params['end'])
            self._in_graph = self._uuid is not None
            return

        self._checkValid()
        try:
            self._checkReference()
        except:
            pass

        res = self._graph_utils.getSequenceAlteration(**self._params)
        if res != None:
            self._uuid = res
            self.byUuid(self._uuid)
            self._in_graph = True
        else:
            self._uuid = None
            self._in_graph = False

    def getCosmicEntry(self):
        self._refreshXrefs()
        return self._cosmic_objs

    def _refreshXrefs(self, checkDb=True):
        # updates two distinct fields: self._xrefs and self._cosmic_objs
        # self._xrefs is a bare list of ids (either manually provided by the user or loaded from the graph). It may include both entries that are included in the local Cosmic db and entries that are not (e.g. originating from newer releases). If instead the user hasn't provided any cosmic id, this list is initially empty. It will be updated from cosmic entries matching the sa object parameters
        # self._cosmic_objs is initially empty. It will be updated from matching self._xrefs (if any) and by looking up the sa object parameters in the local cosmic db
        
        if self._params['alt_type'] == 'wt':
            return []

        self._checkValid()
        try:
            self._checkReference()
        except:
            pass
        
        if checkDb:
            start = self._params['start']
            end = self._params['end'] + 1
            if  self._params['alt_type'] in ['del', 'delins']:
                start -= 1

            cosmic_gene = None
            if self._params['gene_symbol']:
                try:
                    cosmic_gene = annotations.models.CosmicGene.objects.get(symbol=self._params['gene_symbol'])
                except:
                    pass
            if cosmic_gene:
                candidates = annotations.models.CosmicSequenceAlteration.objects.filter(alteration_type=self._params['alt_type'],chromosome=self._params['chrom'],start_position=start,end_position=end,cosmic_gene=cosmic_gene)
            else:
                candidates = annotations.models.CosmicSequenceAlteration.objects.filter(alteration_type=self._params['alt_type'],chromosome=self._params['chrom'],start_position=start,end_position=end)

            # try to find objects also based on the xref id
            candidates_from_ids = annotations.models.CosmicSequenceAlteration.objects.filter(cosmic_id__in=self._xrefs) if len(self._xrefs) > 0 else []

            if self._params['alt_type'] == 'sub':
                candidates = filter(lambda x: x.reference_seq == self._params['ref'] and x.altered_seq == self._params['alt'], candidates)
            elif self._params['alt_type'] == 'ins':
                candidates = filter(lambda x: x.altered_seq[1:] == self._params['alt'], candidates)
            elif self._params['alt_type'] == 'delins':
                candidates = filter(lambda x: x.altered_seq[1:] == self._params['alt'] and len(x.reference_seq) == self._params['num_bases'] + 1, candidates)
            elif self._params['alt_type'] == 'del':
                candidates = filter(lambda x: len(x.reference_seq) == self._params['num_bases'] + 1, candidates)
            elif self._params['alt_type'] == 'dup':
                warning("Duplication found, but don't know how to handle it. Please see source code.")
                candidates = []
        else:
            candidates = []
        
        self._cosmic_objs = list(set(candidates).union(candidates_from_ids))
        self._xrefs = list(set(self._xrefs).union([o.cosmic_id for o in candidates]))

    def _checkValid(self):
        for p in self._req_params:
            if self._params[p] == None:
                print self._uuid
                raise Exception("Missing required parameter: '{0}'".format(p))
        for p in self._seq_alt_types_params[self._params['alt_type']]['params']:
            if self._params[p] == None:
                print self._uuid
                raise Exception("Missing required parameter: '{0}'".format(p))

        return True

    def getGenomicAnnotations(self):
        # returns a list of items (more or less) like the following (indicating where the alteration will be mapped to):
        # {
        #   'exon': {'ensembl_id': ..., 'exon_no': ..., 'start': ..., 'end': ... },
        #   'transcript': [
        #           {'ensembl_id': ..., 'start': ..., 'end': ...}, ...
        #    ],
        #   'gene': {'ensemble_id': ..., 'symbol': ..., 'start': ..., 'end': ..., 'strand': ...}
        #   'chromosome': ...
        # }
        self._checkValid()
        try:
            self._checkReference()
        except:
            pass
        return self._graph_utils.getGenomicLocationAnnotation(self._params['chrom'], self._params['start'])

    def getData(self):
        return {'type': self._params['alt_type'], 'chrom': self._params['chrom'], 'start': self._params['start'], 'alt': self._params['alt'], 'ref': self._params['ref'], 'num_bases': self._params['num_bases'], 'gene_symbol': self._params['gene_symbol']}
    @staticmethod
    def getEndCoordinate(start, ref, num_bases):
        return start + (len(ref) - 1 if ref != None else num_bases-1 if num_bases is not None else 0)
    
    @staticmethod
    def byUuid_list(uuid_list):
        res = SequenceAlteration._graph_utils.getSequenceAlterationByUuid_list(uuid_list=uuid_list)
        objs = []
        for r in res:
            s = SequenceAlteration()
            s.byUuid(r[0], r)
            objs.append(s)
        return objs

    def byUuid(self, uuid, res=None):
        # res is an object that can be optionally passed containing all parameters required to build the SA object without accessing the graph db
        # it can be the result of a previous search (e.g., search by gene name)
        if res is None:
            res = self._graph_utils.getSequenceAlterationByUuid(uuid=uuid)
            if len(res) != 0:
                res = res[0]
        if res:
            self._params['chrom'] = res[1]
            self._params['start'] = res[2]
            self._params['end'] = res[3]
            try:
                label = filter(lambda x: True if x in self._seq_alt_label_remap else False, res[4])[0]
            except Exception as e:
                print e
                print res
                return

            self._params['alt_type'] = self._seq_alt_label_remap[label]
            self._params['label'] = label
            self._params['alt'] = res[7]
            self._params['num_bases'] = int(res[9]) if res[9] else None
            if self._params['alt_type'] == 'sub':
                #from 10: r.ref, r.c_start, r.c_offset, r.loc_p"
                self._params['ref'] = res[5]
                #else:
                #    self._params['ref'] = self._seq_utils_gen.getRefSequence(chrom=self._params['chrom'], start=self._params['start'], length=1, strand='+')
            self._params['start_c'] = res[11]
            self._params['start_c_offset'] = res[12]
            self._params['start_c_datum'] = res[20]
            self._params['end_c'] = res[13]
            self._params['end_c_offset'] = res[14]
            self._params['end_c_datum'] = res[21]
            self._params['loc_p'] = res[6]
            self._params['strand'] = res[18]
            self._params['alt_p'] = res[8]
            self._params['tx_ac'] = res[19]
            self._params['num_bases_c'] = res[10]
            self._params['gene_uuid'] = res[15]
            self._params['gene_symbol'] = res[16]
            self._params['gene_ac'] = res[17]

            if res[22]:
                self._xrefs = res[22]
                    
            self._uuid = uuid
            self._in_graph = True
        else:
            raise Exception("Not found")
        
    def byCosmicObj(self, cosmic_obj):
        if cosmic_obj is not None:
            self._params['alt_type'] = cosmic_obj.alteration_type
            self._params['label'] = self._seq_alt_types_params[cosmic_obj.alteration_type]['label']
            self._params['chrom'] = cosmic_obj.chromosome
            self._params['start'] = cosmic_obj.start_position
            self._params['end'] = cosmic_obj.end_position - 1
            self._params['gene_symbol'] = cosmic_obj.cosmic_gene.symbol
            
            if cosmic_obj.alteration_type == 'sub':
                self._params['ref'] = cosmic_obj.reference_seq
                self._params['alt'] = cosmic_obj.altered_seq

            elif cosmic_obj.alteration_type == 'ins':
                # N.B. The HGVS syntactic convention for insertions is to indicate the
                # nucleotides flanking the insertion site on both sides.
                # However, the syntax generated by the HGVS library only indicates the
                # 5' flanking nucleotide (and we must live with that - I'm not by any
                # means going to fix it).
                # The Cosmic database correctly uses the double flanking syntax, and
                # the coordinates are correct. In addition, both the 'ref' and 'alt'
                # fields include the 5' flanking nucleotide, which must be stripped off.
                self._params['alt'] = cosmic_obj.altered_seq[1:]
            elif cosmic_obj.alteration_type == 'delins':
                # Same goes for indels, however, when mapping to the transcript, the
                # genomic start coordinate seems wrong and apparently must be increased
                # by one
                self._params['start'] += 1
                self._params['alt'] = cosmic_obj.altered_seq[1:]
                self._params['num_bases'] = len(cosmic_obj.reference_seq) - 1
            elif cosmic_obj.alteration_type == 'del':
                # Same goes for dels, coordinate seems again wrong
                self._params['start'] += 1
                self._params['num_bases'] = len(cosmic_obj.reference_seq) - 1
            elif cosmic_obj.alteration_type == 'dup':
                # There's currently only one duplication entry in Cosmic, whose start coordinate
                # seems to be off by 2 nucleotides. I can't even understand whether the
                # 'ref' or 'alt' include one extra nucleotide as in the case of insertions.
                # This is way too little information to figure out the underlying rationale, so I'm not implementing this case
                raise Exception("Duplication found, but don't know how to handle it. Plase see source code.")

            #print self._params
            self._in_graph = None
            self._uuid = None

            self._cosmic_objs = [cosmic_obj]

    def set(self, **kwargs):
        # takes parameters and returns matching alterations (if any)
        # parameters can be either in genomic coordinate + explicit variation mode:
        # (type, chrom, start, ref, alt, num_bases)
        # or in transcript coordinate + HGVS syntax mode:
        # (tx_accession, cds_syntax)
        #print "setting parameters"
        if 'type' in kwargs and 'chrom' in kwargs and 'start' in kwargs:

            ### genomic coordinate mode ###
            #print "genomic coordinate mode"

            if type(kwargs['chrom']) != str:
                kwargs['chrom'] = str(kwargs['chrom'])

            params = {}
            params['chrom'] = kwargs['chrom']
            params['start'] = int(kwargs['start'])
            params['type'] = kwargs['type']
            if params['type'] not in self._seq_alt_types_params:
                raise Exception("Unknown SequenceAlteration type: '{0}'".format(params['type']))
            params['label'] = self._seq_alt_types_params[params['type']]['label']

            for p in self._seq_alt_types_params[params['type']]['params']:
                try:
                    params[p] = kwargs[p]
                except Exception as e:
                    raise Exception("Missing required parameter: '{0}'".format(e))
            if 'num_bases' in params:
                params['num_bases'] = int(params['num_bases'])

            for p in self._opt_params:
                if p not in params:
                    params[p] = None

            params['gene_symbol'] = kwargs.get('gene_symbol', None)
            params['gene_uuid'] = kwargs.get('gene_uuid', None)
            params['gene_ac'] = None

            params['end'] = params['start']
            if params['type'] == 'ins':
                params['end'] += 1
            elif params['type'] in ['del', 'delins', 'dup']:
                params['end'] += params['num_bases'] - 1

        elif 'tx_accession' in kwargs and 'cds_syntax' in kwargs:

            ### tx accession mode ###
            #print "tx accession mode"
            _tx_ac = kwargs['tx_accession']
            _cds = kwargs['cds_syntax']
            cds2 = _cds[2:]
            for letter in ['a', 'c', 't', 'g']:
                cds2 = cds2.replace(letter, letter.upper())
            _cds = _cds[:2] + cds2
            self._params['tx_ac'] = _tx_ac
            self._tx_annot_source = kwargs.get('source', None)
            params = self.__map_c_to_g(_tx_ac, _cds)
            params['label'] = self._seq_alt_types_params[params['type']]['label']

            #if 'ref' in params and params['ref'] is not None and len(params['ref']) > 0:
                # check if provided sequence matches reference
            #    refseq = self._seq_utils_gen.getRefSequence(chrom=params['chrom'],start=params['start'],length=len(params['ref']),strand=params['strand'])
            #    if refseq != params['ref']:
            #        raise Exception("Provided reference ({0}) does not match available reference ({1})".format(params['ref'],refseq))
            #    else:
            #        print "RefSequences match"


        else:
            # invalid mode
            raise Exception("Incorrect call format. Valid formats are (type, chrom, start, ...) or (tx_accesion, HGVS_cds_syntax)")

        #    {'chrom': '1', 'label': 'indel',          'start': 906304, 'alt': 'CTG',            'num_bases': 4,  }
        #    {'chrom': '1', 'label': 'point_mutation', 'start': 69345,  'alt': 'A',  'ref': 'C', 'num_bases': None}


        self._params['chrom'] = params['chrom']
        self._params['start'] = params['start']
        self._params['end'] = params['end']
        self._params['end'] = params['end']
        self._params['alt_type'] = params['type']
        self._params['alt'] = params['alt']
        self._params['ref'] = params['ref']
        self._params['num_bases_c'] = params.get('num_bases_c', None)
        self._params['num_bases'] = params['num_bases']

        if params['gene_symbol']:
            self._params['gene_symbol'] = params['gene_symbol']
            if not params['gene_uuid'] or not params['gene_ac']:
                info = self._graph_utils.getGeneInfo(uuid=params['gene_uuid'],symbol=params['gene_symbol'])
                ret = len(info)
                if len(info) > 0:
                    self._params['gene_uuid'] = info[0].uuid
                    self._params['gene_ac'] = info[0].ac
                    params['strand'] = info[0].strand
                else:
                    self._params['gene_uuid'] = None
                    self._params['gene_ac'] = None
            else:
                self._params['gene_uuid'] = params['gene_uuid']
                self._params['gene_ac'] = params['gene_ac']
                ret = 1
        else:
            if params['gene_uuid']:
                gene_info = self._graph_utils.getGeneInfo(uuid=params['gene_uuid'])
                try:
                    self._params['gene_symbol'] = gene_info[0].symbol
                    self._params['gene_ac'] = gene_info[0].ac
                    self._params['gene_uuid'] = params['gene_uuid']
                except:
                    pass
            if self._params['gene_uuid'] is None:
                info = self._graph_utils.getGenesInRegion(chrom=self._params['chrom'],start=self._params['start'],end=self._params['end'])
                ret = len(info)
                if len(info) > 0:
                    self._params['gene_symbol'] = info[0][1]
                    self._params['gene_uuid'] = info[0][0]
                    self._params['gene_ac'] = info[0][2]
                    params['strand'] = info[0][4]
                else:
                    self._params['gene_symbol'] = None
                    self._params['gene_uuid'] = None
                    self._params['gene_ac'] = None

        self._params['label'] = params['label']
        self._params['strand'] = params.get('strand', None)

        if self._params['tx_ac'] is None and self._params['gene_symbol'] is not None:
            try:
                self._params['tx_ac'] = self._graph_utils.getDefaultTranscriptForGene(gene_ac=self._params['gene_ac'],gene_symbol=self._params['gene_symbol'])['ac']
            except:
                pass

        #print self._params
        self._in_graph = None
        self._uuid = None

        return ret

    def setXref(self, xref_id):
        if isinstance(xref_id, list):
            self._xrefs = xref_id
        else:
            self._xrefs = [xref_id]

    def _checkReference(self):
        #return True
        if self._params['ref'] is None:
            return True
        else:
            num_bases = len(self._params['ref'])
            ref = self._seq_utils_gen.getRefSequence(chrom=self._params['chrom'], start=self._params['start'], length=num_bases, strand='+')
            if self._params['ref'] != ref:
                raise Exception("Reference sequence mismatch: expected '%s' but got '%s' instead" % (ref, self._params['ref']))
            else:
                return True

    def _map_coord_c_to_g(self, tx_ac, cds_start, cds_end):
        pass
    
    def _map_coord_g_to_c(self, chrom, start_g, end_g):
        print "_map_coord_g_to_c"
        if self._params['tx_ac'] is None:
            tx = self._graph_utils.getDefaultTranscriptForGene(gene_ac=self._params['gene_ac'],gene_symbol=self._params['gene_symbol'])
            try:
                self._params['tx_ac'] = tx['ac']
            except Exception as e:
                print e
                return None
        tx = self._graph_utils.getTranscriptInfo(ac=self._params['tx_ac'])
        if len(tx) == 0:
            raise Exception("Transcript not found")
        tx = tx[0]
        if tx['tx.cds_start'] is None:
            raise Exception("Cannot map, transcript is non- protein coding")

        strand = tx['strand']
        if strand == '+':
            e_starts_g = tx['exon.starts']
            e_ends_g = tx['exon.ends']
        else:
            e_starts_g = tx['exon.ends']
            e_ends_g = tx['exon.starts']
            start_g, end_g = end_g, start_g
    
        e_lengths = tx['exon.lengths']

        cds_start_tx = tx['tx.cds_start']
        cds_end_tx = tx['tx.cds_end']
        cds_start_c = 1
        cds_end_c = cds_end_tx - cds_start_tx + 1

        e_coords_g = []
        for i in xrange(0, len(e_starts_g)):
            e_coords_g.append(e_starts_g[i])
            e_coords_g.append(e_ends_g[i])
        if strand == '+':
            e_coords_g.append(sys.maxint)
        else:
            e_coords_g.append(0)

        e_coords_tx = []
        acc = 0
        for i in xrange(0, len(e_lengths)):
            e_coords_tx.append(acc)
            acc += e_lengths[i] - 1
            e_coords_tx.append(acc)
            acc += 1

        e_coords_c = []
        for i in xrange(0, len(e_coords_tx)):
            if e_coords_tx[i] < cds_start_tx:
                e_coords_c.append(e_coords_tx[i] - cds_start_tx)
            else:
                e_coords_c.append(e_coords_tx[i] - cds_start_tx + 1)
            #elif e_coords_tx[i] >= cds_start_tx and e_coords_tx[i] <= cds_end_tx:
            #    e_coords_c.append(e_coords_tx[i] - cds_start_tx + 1)
            #else:
            #    e_coords_c.append(e_coords_tx[i] - cds_end_tx)

        coords = []

        for Z in [start_g, end_g]:
            if strand == '+':
                for i in xrange(0, len(e_coords_g)):
                    if Z < e_coords_g[i]:
                        break
            else:
                for i in xrange(0, len(e_coords_g)):
                    if Z > e_coords_g[i]:
                        break

            #print "selected: ", i

            if i % 2 == 0:
                if i == 0:
                    # before 1st exon
                    base = e_coords_c[0]
                    offset = -abs(e_coords_g[0] - Z)
                    datum = hgvs.location.CDS_START
                elif i == len(e_coords_g) - 1:
                    # after last exon
                    base = e_coords_c[-1]
                    offset = abs(Z - e_coords_g[-2]) # because ..[-1] is either maxint or 0
                    if base > cds_end_c:
                        base -= cds_end_c
                        datum = hgvs.location.CDS_END # nucleotides are numbered as *1, *2, *3 ... from the last nucleotide of the translation stop codon
                    else:
                        datum = hgvs.location.CDS_START
                else:
                    # in intron
                    # what's the closest exon?
                    if abs(Z - e_coords_g[i-1]) <= abs(e_coords_g[i] - Z):
                        # previous exon
                        base = e_coords_c[i-1]
                        offset = abs(Z - e_coords_g[i-1])
                    else:
                        # following exon
                        base = e_coords_c[i]
                        offset = -abs(e_coords_g[i] - Z)
                    datum = hgvs.location.CDS_START
            else:
                # in exon
                off = abs(Z - e_coords_g[i-1])
                base = e_coords_c[i-1] + off + (1 if (e_coords_c[i-1] < 0 and off >= abs(e_coords_c[i-1])) else 0) # if we're crossing the start of the coding region, we need to add 1 because there is a gap (from -1 to +1)
                offset = 0
                if base > cds_end_c:
                    base -= cds_end_c
                    datum = hgvs.location.CDS_END # nucleotides are numbered as *1, *2, *3 ... from the last nucleotide of the translation stop codon
                else:
                    datum = hgvs.location.CDS_START
            
            coords.append((base, offset, datum))

        return {'cds_start_base': coords[0][0], 'cds_start_offset': coords[0][1], 'cds_start_datum': coords[0][2], 'cds_end_base': coords[1][0], 'cds_end_offset': coords[1][1], 'cds_end_datum': coords[1][2]}

    def __map_c_to_g(self, tx_ac, cds):
        # used temporarily until we manage to get HGVS's c_to_g to work
        tx = self._graph_utils.getTranscriptInfo(ac=tx_ac)
        if len(tx) == 0:
            raise Exception("Transcript not found")
        tx = tx[0]
        #print "TX:", tx
        var = self._hgvsparser.parse_hgvs_variant('{tx_ac}:{cds}'.format(tx_ac=tx_ac,cds=cds))
        exon_lengths = tx['exon.lengths']
        intron_lengths = [es - ee for es, ee in zip(tx['exon.starts'][1:], tx['exon.ends'][:-1])]
        exon_starts_tx = [0]
        for l in exon_lengths:
            exon_starts_tx.append(exon_starts_tx[-1] + l)
        # beware: this position is not from the start of the Tx, but from the start of the coding region!!!
        # the start coordinate of the coding region is expressed with respect to the start of the transcript
        v_type = var.posedit.edit.type
        if v_type in ['del', 'delins']:
            num_bases_c = var.posedit.edit.ref_n
        elif v_type == 'dup':
            num_bases_c = var.posedit.edit.n
        else:
            num_bases_c = None

        pos_start_tx = var.posedit.pos.start.base + (tx['tx.cds_start'] if var.posedit.pos.start.datum == hgvs.location.CDS_START else tx['tx.cds_end']) + (-1 if var.posedit.pos.start.base > 0 and var.posedit.pos.start.datum == hgvs.location.CDS_START else 0)
        pos_end_tx = var.posedit.pos.end.base + (tx['tx.cds_start'] if var.posedit.pos.end.datum == hgvs.location.CDS_START else tx['tx.cds_end']) + (-1 if var.posedit.pos.end.base > 0 and var.posedit.pos.end.datum == hgvs.location.CDS_START else 0)

        exon_start_id, = [i for i in xrange(0, len(exon_starts_tx)-1) if pos_start_tx >= exon_starts_tx[i] and pos_start_tx < exon_starts_tx[i+1]]
        exon_end_id, = [i for i in xrange(0, len(exon_starts_tx)-1) if pos_end_tx >= exon_starts_tx[i] and pos_end_tx < exon_starts_tx[i+1]]

        if tx['strand'] == '+':
            # on + strand, exon_start_tx is the same base as exon_start_g, and we go forward
            pos_start_g = tx['exon.starts'][exon_start_id] + (pos_start_tx - exon_starts_tx[exon_start_id]) + var.posedit.pos.start.offset
            pos_end_g = tx['exon.starts'][exon_end_id] + (pos_end_tx - exon_starts_tx[exon_end_id]) + var.posedit.pos.end.offset
            try:
                ref = var.posedit.edit.ref_s
            except:
                ref = None
            try:
                alt = var.posedit.edit.alt
            except:
                alt = None
        else:
            # but on - strand, exon_start_tx is exon_end_g, and we go backwards
            pos_start_g = tx['exon.ends'][exon_start_id] - (pos_start_tx - exon_starts_tx[exon_start_id]) - var.posedit.pos.start.offset
            pos_end_g = tx['exon.ends'][exon_end_id] - (pos_end_tx - exon_starts_tx[exon_end_id]) - var.posedit.pos.end.offset
            try:
                ref = Seq.reverse_complement(var.posedit.edit.ref_s) if var.posedit.edit.ref_s else None
            except:
                ref = None
            try:
                alt = Seq.reverse_complement(var.posedit.edit.alt) if var.posedit.edit.alt else None
            except:
                alt = None

        if num_bases_c is not None or v_type in ['del', 'delins', 'dup']:
            num_bases = abs(pos_end_g - pos_start_g) + 1
        else:
            num_bases = None
        #else:
        #    if exon_start_id == len(exon_starts_tx)-1 or pos_start_tx + num_bases_c < exon_starts_tx[exon_start_id+1]:
        #        num_bases = num_bases_c
        #    else:
        #        num_bases = num_bases_c + intron_lengths[exon_start_id]
        #        exon_end_id = exon_id + 1
        #        while pos_tx + num_bases_c >= exon_starts_tx[exon_end_id+1]:
        #            num_bases += intron_lengths[exon_end_id]
        #            exon_end_id += 1

        if tx['strand'] == '-':
            pos_start_g, pos_end_g = pos_end_g, pos_start_g

        
        chrom = tx['tx.chrom']
        gene_symbol = tx['gene.symbol']
        gene_uuid = tx['gene.uuid']
        gene_ac = tx['gene.ac']
        return {'chrom': chrom, 'start': pos_start_g, 'end': pos_end_g, 'type': v_type, 'ref': ref, 'alt': alt, 'num_bases': num_bases, 'num_bases_c': num_bases_c, 'gene_symbol': gene_symbol, 'gene_uuid': gene_uuid, 'gene_ac': gene_ac, 'strand': tx['strand']}

    def __map_g_to_c(self, chrom, start_g, tx_ac):
        tx = self._graph_utils.getTranscriptInfo(ac=tx_ac)
        if len(tx) == 0:
            raise Exception("Transcript not found")
        tx = tx[0]
        if tx['tx.cds_start'] is None:
            raise Exception("Cannot map, transcript is non- protein coding")
        exon_starts_g = tx['exon.starts'] # 0-based left coordinate BEWARE: Cosmic alteration start and end coordinates are left and right respectively
        exon_ends_g = tx['exon.ends'] # 0-based left coordinate
        exon_lengths = tx['exon.lengths']
        exon_id = [i for i in xrange(0, len(exon_starts_g)) if start_g >= exon_starts_g[i] and start_g <= exon_ends_g[i]]

        if len(exon_id) != 1:
            # alteration falls outside exonic region
            if tx['strand'] == '+':
                if start_g < exon_starts_g[0]:
                    # 5' of first exon
                    # reference will be c.1-XXX
                    exon_id = 0
                    sign = '-'
                    abs_offset = exon_starts_g[0] - start_g
                    start_g = exon_starts_g[0]
                elif start_g >= exon_ends_g[-1]:
                    # 3' of last exon
                    # reference will be c.N+XXX
                    exon_id = len(exon_lengths) - 1
                    sign = '+'
                    abs_offset = start_g - exon_ends_g[-1]
                    start_g = exon_ends_g[-1]
                else:
                    # between two exons, find which ones
                    exon_id, = [i for i in xrange(0, len(exon_starts_g)-1) if start_g > exon_ends_g[i] and start_g < exon_starts_g[i+1]]
                    if start_g - exon_ends_g[exon_id] > exon_starts_g[exon_id+1] - start_g:
                        # if start_g is closest to following intron, the latter must be the reference
                        # (for introns with an uneven number of nucleotides, the central nucl. is the last described with a '+'
                        exon_id += 1
                        sign = '-'
                        abs_offset = exon_starts_g[exon_id] - start_g
                        start_g = exon_starts_g[exon_id]
                    else:
                        sign = '+'
                        abs_offset = start_g - exon_ends_g[exon_id]
                        start_g = exon_ends_g[exon_id]
            else:
                if start_g > exon_ends_g[0]:
                    # 5' of first exon
                    # reference will be c.1-XXX
                    exon_id = 0
                    sign = '-'
                    abs_offset = start_g - exon_ends_g[-1]
                    start_g = exon_ends_g[0]
                elif start_g < exon_starts_g[-1]:
                    # 3' of last exon
                    # reference will be c.N+XXX
                    exon_id = len(exon_lengths) - 1
                    sign = '+'
                    abs_offset = exon_starts_g[-1] - start_g
                    start_g = exon_starts_g[-1]
                else:
                    # between two exons, find which ones
                    exon_id, = [i for i in xrange(0, len(exon_starts_g)-1) if start_g < exon_starts_g[i] and start_g > exon_ends_g[i+1]]
                    if  exon_starts_g[exon_id] - start_g > start_g - exon_ends_g[exon_id+1]:
                        # if position is closest to following intron, the latter must be the reference
                        # (for introns with an uneven number of nucleotides, the central nucl. is the last described with a '+'
                        exon_id += 1
                        sign = '-'
                        abs_offset = start_g - exon_ends_g[exon_id]
                        start_g = exon_ends_g[exon_id]
                    else:
                        sign = '+'
                        abs_offset = exon_starts_g[exon_id] - start_g
                        start_g = exon_starts_g[exon_id]

        else:
            exon_id = exon_id[0]
            sign = ''
            abs_offset = 0
        start_tx = sum([exon_lengths[i] for i in xrange(0, exon_id)])
        if tx['strand'] == '+':
            start_tx += start_g - exon_starts_g[exon_id] + 1
        else:
            start_tx += exon_ends_g[exon_id] - start_g + 1

        return {'tx_ac': tx['tx.ac'], 'start_c': start_tx - tx['tx.cds_start'], 'start_c_offset': int(sign + str(abs_offset)), 'strand': tx['strand']}

    def update(self):
        self._computeTxParameters(force=True)
        reg_uuid = self._graph_utils.getRegionByCoords(chrom=self._params['chrom'], start=self._params['start'], end=self._params['end'], gene_uuid=self._params['gene_uuid'], gene_symbol=self._params['gene_symbol'])
        if len(reg_uuid) > 0:
            print "update"
            if self._params['ref'] is None:
                self._params['ref'] = self._seq_utils_gen.getRefSequence(chrom=self._params['chrom'], start=self._params['start'], length=1, strand='+')
            self._graph_utils.setCodingCoordinatesForRegion(reg_uuid[0], self._params['ref'], self._params['start_c'], self._params['start_c_offset'], self._params['start_c_datum'], self._params['end_c'], self._params['end_c_offset'], self._params['end_c_datum'], self.getLoc_p_1L())
        altp = self._computeHGVS_p_1L()
        altp = altp[2:] if altp is not None else altp
        self._graph_utils.setSequenceAlterationProperties(uuid=self._uuid, num_bases=self._params['num_bases'], num_bases_c=self._params['num_bases_c'], alt_p=altp, x_ref=self._xrefs)
        
    def updateRegion(self):
        reg_uuid = self._graph_utils.getRegionByCoords(chrom=self._params['chrom'], start=self._params['start'], end=self._params['end'], gene_uuid=self._params['gene_uuid'], gene_symbol=self._params['gene_symbol'])
        if len(reg_uuid) == 0:
            return False
        return self._graph_utils.setCodingCoordinatesForRegion(reg_uuid[0], self._params['ref'], self._params['start_c'], self._params['start_c_offset'], self._params['start_c_datum'], self._params['end_c'], self._params['end_c_offset'], self._params['end_c_datum'], self.getLoc_p_1L())

    def save(self):
        # saves current alteration and maps it to the appropriate locations
        # make sure that all required parameters have been defined
        if self.exists() == True:
            #print "Already exists"
            return

        self._checkValid()
        self._checkReference()

        # identify region onto which alteration will be mapped
        reg_uuid = self._graph_utils.getRegionByCoords(chrom=self._params['chrom'], start=self._params['start'], end=self._params['end'], gene_uuid=self._params['gene_uuid'], gene_symbol=self._params['gene_symbol'])
        self._computeTxParameters()
        if len(reg_uuid) == 0:
            if self._params['ref'] is None:
                self._params['ref'] = self._seq_utils_gen.getRefSequence(chrom=self._params['chrom'], start=self._params['start'], length=1, strand='+')
            reg_uuid = self._graph_utils.createRegion(chrom=self._params['chrom'], start=self._params['start'], end=self._params['end'], gene_uuid=self._params['gene_uuid'], gene_symbol=self._params['gene_symbol'])
            if self._params['tx_ac'] is not None:
                self._graph_utils.setCodingCoordinatesForRegion(reg_uuid, self._params['ref'], self._params['start_c'], self._params['start_c_offset'], self._params['start_c_datum'], self._params['end_c'], self._params['end_c_offset'], self._params['end_c_datum'], self.getLoc_p_1L())
        else:
            reg_uuid = reg_uuid[0]  # assume there is always only one region (there should be only one)
            if self._params['tx_ac'] is not None:
                hasCodingCoordinates = self._graph_utils.regionHasCodingCoordinates(reg_uuid)
                if hasCodingCoordinates == False:
                    hasCodingCoordinates = self._graph_utils.setCodingCoordinatesForRegion(reg_uuid, self._params['ref'], self._params['start_c'], self._params['start_c_offset'], self._params['start_c_datum'], self._params['end_c'], self._params['end_c_offset'], self._params['end_c_datum'], self.getLoc_p_1L())

        # create alteration node
        hgvs = self._computeHGVS_p_1L()
        self._params['alt_p'] = hgvs[2:] if hgvs else None
        params = {k: self._params[k] for k in ['alt', 'alt_p', 'num_bases', 'num_bases_c']}

        #print "call createSequenceAlteration"

        
        self._refreshXrefs()
        if len(self._xrefs) > 0:
            params['x_ref'] = self._xrefs

        self._uuid = self._graph_utils.createSequenceAlteration(region_uuid=reg_uuid, alt_label=self._params['label'], **params)
        #print "returned = ", self._uuid
        # get gene(s) to which alteration is linked, if any
        #print "call getGeneUUIDsFromRegion"
        if self._params['gene_uuid'] is not None:
            genes_uuid = [self._params['gene_uuid']]
        else:
            genes_uuid = self._graph_utils.getGeneUUIDsFromRegion(region_uuid=reg_uuid)
        #print "returned = ", genes_uuid
        for g in genes_uuid:
            #print "call linkSequenceAlterationToGene"
            self._graph_utils.linkSequenceAlterationToGene(alt_uuid=self._uuid, gene_uuid=g)
            #print "returned"
        self._in_graph = True

        #if self._params['tx_ac'] is not None:
        #    #print "call addTranscript"
        #    self.addTranscript(self._params['tx_ac'], self._tx_annot_source)
        #    #print "returned"

        self.byUuid(self._uuid)

        #annotations.models.LabelTerm.objects.get(name=self._params['label']).updateLastInsert()

    def getHGVS_g(self):
        if self._params['alt_type'] == 'wt':
            return ':wt'
        else:
            self._checkValid()
            try:
                self._checkReference()
            except:
                return "ERR"

            '''
            if self._hgvscache_obj is None:
                try:
                    self._hgvscache_obj = annotations.models.HGVSCache.objects.get(graph_uuid=self._uuid, tx_ac=tx_ac)
                except:
                    pass
            if self._hgvscache_obj is not None:
                print "from db"
                return self._hgvscache_obj.hgvs_g
            '''

            if self._params['alt_type'] in ['sub', 'delins', 'del']:
                edit = hgvs.edit.NARefAlt(ref=self._params['ref'] or str(self._params['num_bases']), alt=self._params['alt'])
            elif self._params['alt_type'] == 'ins':
                edit = hgvs.edit.NARefAlt(alt=self._params['alt'])
            else: # 'dup'
                edit = hgvs.edit.NADupN(uncertain=False, n=self._params['ref'] or str(self._params['num_bases']))
            loc_start = hgvs.location.SimplePosition(base=self._params['start'], uncertain=False)
            loc_end = hgvs.location.SimplePosition(base=self._params['end'], uncertain=False)
            pos = hgvs.location.Interval(start=loc_start,end=loc_end)
            posedit = hgvs.posedit.PosEdit(pos=pos,edit=edit)
            var = hgvs.variant.SequenceVariant(ac='chr'+self._params['chrom'],type='g',posedit=posedit)
            return str(var)

    def _computeTxParameters(self, force=False):
        if 'start_c' not in self._params or force == True:
            if not self._params['tx_ac']:
                try:
                    self._params['tx_ac'] = self._graph_utils.getDefaultTranscriptForGene(gene_ac=self._params['gene_ac'],gene_uuid=self._params['gene_uuid'],gene_symbol=self._params['gene_symbol'])['ac']
                except:
                    print "no gene specified"
                    return
            tx_info = self._graph_utils.getTranscriptInfo(ac=self._params['tx_ac'])[0]
            try:
                #if tx_info['strand'] == '+':
                remap = self._map_coord_g_to_c(self._params['chrom'], self._params['start'], self._params['end'])
                    #remap = self.__map_g_to_c(self._params['chrom'], self._params['start'], self._params['tx_ac'])
                #else:
                #    remap = self.__map_g_to_c(self._params['chrom'], self._params['end'], self._params['tx_ac'])
                #self._params['start_c'] = remap['start_c']
                #self._params['offset'] = remap['offset']
                self._params['start_c'] = remap['cds_start_base']
                self._params['start_c_offset'] = remap['cds_start_offset']
                self._params['start_c_datum'] = remap['cds_start_datum']
                self._params['end_c'] = remap['cds_end_base']
                self._params['end_c_offset'] = remap['cds_end_offset']
                self._params['end_c_datum'] = remap['cds_end_datum']
                if remap['cds_start_offset'] == 0 and remap['cds_end_offset'] == 0:
                    if self._params['alt_type'] in ['del', 'delins', 'dup']:
                        self._params['num_bases_c'] = remap['cds_end_base'] - remap['cds_start_base'] + 1
                        if (remap['cds_start_base'] > 0) != (remap['cds_end_base'] > 0):
                            self._params['num_bases_c'] -= 1 # we're crossing the translation start codon and there's a coordinate gap from -1 to +1 (no 0), so there's one less nucleotide than the number obtained by simply subtracting
                        if remap['cds_start_datum'] != remap['cds_end_datum']:
                            self._params['num_bases_c'] += tx_info['tx.cds_end']
                    else:
                        self._params['num_bases_c'] = None
                else:
                    self._params['num_bases_c'] = ''
            except Exception, e:
                print e
                self._params['start_c'] = None
                self._params['start_c_offset'] = None
                self._params['start_c_datum'] = None
                self._params['end_c'] = None
                self._params['end_c_offset'] = None
                self._params['end_c_datum'] = None

    def getHGVS_c(self):
        if self._params['alt_type'] == 'wt':
            return ':wt'
        
        if not self.exists():
            self._computeTxParameters()

        if 'start_c' not in self._params or not self._params['start_c']:
            return None
        else:
            self._checkValid()
            try:
                self._checkReference()
            except:
                return "ERR"
            
            if self._hgvs_c_object is None:
                self._hgvs_c_object = self._getHGVS_c_object(tx_ac=self._params['tx_ac'])
            return str(self._hgvs_c_object).split(':')[1]

    def _getHGVS_c_object(self, tx_ac=None):
        #res = self.__map_g_to_c(chrom=self._params['chrom'], start_g=self._params['start'], tx_ac=tx_ac)

        if not tx_ac:
            tx_ac = '?'

        if self._params['strand'] == '+':
            ref, alt = self._params['ref'], self._params['alt']
        else:
            ref = str(Seq.Seq(self._params['ref']).reverse_complement()) if self._params['ref'] is not None else None
            alt = str(Seq.Seq(self._params['alt']).reverse_complement()) if self._params['alt'] is not None else None
        
        if self._params['alt_type'] in ['sub', 'delins', 'del']:
            edit = hgvs.edit.NARefAlt(ref=ref or str(self._params['num_bases_c']), alt=alt)
        elif self._params['alt_type'] == 'ins':
            edit = hgvs.edit.NARefAlt(alt=alt)
        else: # 'dup'
            edit = hgvs.edit.NADupN(uncertain=False, n=ref or str(self._params['num_bases_c']))
        loc_start = hgvs.location.BaseOffsetPosition(base=self._params['start_c'], offset=self._params['start_c_offset'], datum=self._params['start_c_datum'], uncertain=False)
        loc_end = hgvs.location.BaseOffsetPosition(base=self._params['end_c'], offset=self._params['end_c_offset'], datum=self._params['end_c_datum'], uncertain=False)
        
        #loc_end = hgvs.location.BaseOffsetPosition(base=self._params['start_c'] + (len(self._params['ref']) - 1 if self._params['ref'] != None else self._params['num_bases_c']-1 if self._params['num_bases_c'] is not None else 0) if self._params['start_c_offset'] == 0 else 0, offset=self._params['start_c_offset'], datum=1, uncertain=False)
        
        pos = hgvs.location.Interval(start=loc_start,end=loc_end)
        posedit = hgvs.posedit.PosEdit(pos=pos,edit=edit)
        return hgvs.variant.SequenceVariant(ac=tx_ac,type='c',posedit=posedit)

    def getHGVS_p_1L(self):
        self._checkValid()
        try:
            self._checkReference()
        except:
            return "ERR"
        if 'alt_p' in self._params:
            return 'p.' + (self._params['alt_p'] if self._params['alt_p'] else '?')
        else:
            return self._computeHGVS_p_1L()

    def getLoc_p_1L(self):
        if not self.exists():
            self._computeTxParameters()
        if 'start_c' not in self._params or not self._params['start_c'] or self._params['start_c_datum'] != hgvs.location.CDS_START:
            # AA codon cannot be computed if there's no associated transcript or transcript is non-protein-coding or current location is past translation stop codon
            return None
        if self._params['start_c_offset'] == 0:
            start_p = self._params['start_c'] / 3 + (1 if self._params['start_c'] % 3 != 0 else 0)
            seq = self._seq_utils_tx.getRefSequence(self._params['tx_ac'])
            tx_info = self._graph_utils.getTranscriptInfo(ac=self._params['tx_ac'])[0]
            aa = SeqUtils.seq3(Seq.Seq(seq[tx_info['tx.cds_start']+(start_p-1)*3:tx_info['tx.cds_start']+start_p*3]).translate())
            loc_p = "{0}{1}".format(self._aa_3L_to_1L.get(aa, aa), start_p)
        else:
            # AA codon cannot be computed if current location is in an intronic region
            start_p = None
            aa = None
            loc_p = ""
        return loc_p

    def _computeHGVS_p_3L(self):
        if self._params['alt_type'] == 'wt':
            return ':wt'
        else:
            '''
            if self._hgvscache_obj is None:
                try:
                    self._hgvscache_obj = annotations.models.HGVSCache.objects.get(graph_uuid=self._uuid, tx_ac=tx_ac)
                except:
                    pass
            if self._hgvscache_obj is not None:
                print "from db"
                return self._hgvscache_obj.hgvs_p
            '''
            # aminoacidic change cannot be computed if mutation does not affect a gene
            if self._params['gene_ac'] is None:
                return None

            if not self.exists():
                self._computeTxParameters()

            if 'start_c' not in self._params or not self._params['start_c']:
                return None

            self._connectToDataProviders()
            variantmapper = hgvs.variantmapper.VariantMapper(self._data_prov_tx)
            tx = self._graph_utils.getDefaultTranscriptForGene(gene_ac=self._params['gene_ac'])
            try:
                tx_ac = tx['ac']
            except Exception as e:
                print e
                return None
            if self._hgvs_c_object is None:
                self._hgvs_c_object = self._getHGVS_c_object(tx_ac)
            try:
                var_p = variantmapper.c_to_p(self._hgvs_c_object)
                var_p.posedit.uncertain = False
                return str(var_p).replace('unknown:', '')
            except Exception as e:
                print e
                return None

    def _computeHGVS_p_1L(self):
        '''if self._hgvscache_obj is None:
            try:
                self._hgvscache_obj = annotations.models.HGVSCache.objects.get(graph_uuid=self._uuid, tx_ac=tx_ac)
            except:
                pass
        if self._hgvscache_obj is not None:
            print "from db"
            return self._hgvscache_obj.hgvs_p
        '''

        hgvsp3l = self._computeHGVS_p_3L()
        if not hgvsp3l:
            return None
        hgvsp1l = ''
        i = 0
        while i < len(hgvsp3l):
            if hgvsp3l[i:i+3] in self._aa_3L_to_1L:
                hgvsp1l = hgvsp1l + self._aa_3L_to_1L[hgvsp3l[i:i+3]]
                i += 3
            else:
                hgvsp1l = hgvsp1l + hgvsp3l[i]
                i += 1
        return hgvsp1l

    def addTranscript(self, tx_accession, source):
        if self.exists() == False:
            return
        self._graph_utils.linkSequenceAlterationToTranscript(self._uuid, tx_accession, source)

    def delete(self):
        if self.exists() == False:
            return
        alt_region_uuid = self._graph_utils.getRegionFromChild(uuid=self._uuid,label=self._graph_label)
        self._graph_utils.deleteSequenceAlteration(uuid=self._uuid)
        self._graph_utils.deleteRegion(uuid=alt_region_uuid)
        self._uuid = None
        self._in_graph = False

    def getUUID(self):
        self._checkExists()
        return self._uuid

    def getInfo(self):
        res = {}
        res['uuid'] = self._uuid
        res['ref'] = 'chr' + self._params['chrom']
        res['start'] = self._params['start']
        res['end'] = self._params['end']
        res['gene_uuid'] = self._params.get('gene_uuid', None)
        res['gene_symbol'] = self._params.get('gene_symbol', None)
        res['gene_ac'] = self._params.get('gene_ac', None)
        if self._params['tx_ac'] is None and self._params['gene_uuid'] is not None:
            self._params['tx_ac'] = self._graph_utils.getDefaultTranscriptForGene(gene_uuid=self._gene_uuid)
        res['tx_ac'] = self._params['tx_ac']
        res['hgvs_g'] = self.getHGVS_g()
        res['hgvs_c'] = self.getHGVS_c()
        res['hgvs_p'] = self.getHGVS_p_1L()
        res['x_ref'] = self._xrefs
        return res

    def getExtendedInfo(self):
        res = {}
        res['uuid'] = self._uuid
        res['chrom'] = self._params['chrom']
        res['start'] = self._params['start']
        res['end'] = self._params['end']
        res['strand'] = self._params['strand']
        res['type'] = self._params['alt_type']
        res['alt'] = self._params['alt']
        res['ref'] = self._params['ref']
        res['num_bases'] = self._params['num_bases']
        if self._params['gene_uuid'] is not None:
            res['gene_uuid'] = self._params['gene_uuid']
            res['gene_symbol'] = self._params['gene_symbol']
            res['gene_ac'] = self._params['gene_ac']
            #defaultTx = self._graph_utils.getDefaultTranscriptForGene(gene_uuid=self._gene_uuid)
            res['tx_ac'] = self._params['tx_ac']
            res['hgvs_g'] = self.getHGVS_g()
            res['hgvs_c'] = self.getHGVS_c()
            res['hgvs_p'] = self.getHGVS_p_1L()
        return [res]

    @staticmethod
    def filter(**args):
        if len(set(args.keys()).difference(SequenceAlteration._filtering_params)) > 0:
            return []

        res = SequenceAlteration._graph_utils.getSequenceAlterationsByPosition(**args)
        objs = []
        for r in res:
            s = SequenceAlteration()
            s.byUuid(r[0], r)
            objs.append(s)
        return objs

class SequenceAlterationCache():
    
    def __init__(self):
        self.cache = {}

    def getHGVS(self, uuid, tx_ac):
        if (uuid, tx_ac) not in self.cache:
            s = SequenceAlteration()
            s.byUuid(uuid)
            if tx_ac:
                content = []
                content.append(s.getHGVS_g())
                try:
                    content.append(s.getHGVS_c())
                except:
                    content.append(content[0])
                try:
                    content.append(s.getHGVS_p_1L())
                except:
                    content.append(content[0])
                self.cache[(uuid, tx_ac)] = content
            else:
                self.cache[(uuid, tx_ac)] = [s.getHGVS_g(), '', '']
        return self.cache[(uuid, tx_ac)]

class ShortGeneticVariation(KBReference):
    _graph_label = 'short_genetic_variation'
    _var_types_params = {'single': {'params': ['ref', 'alt'], 'label': 'SNP'}, # alt = allele list (may include ref)
                        'in-del': {'params': ['alt'], 'label': 'sgv_indel'}, # alt = allele list (e.g. allele A is a del, allele B is an ins)
                        'microsatellite': {'params': ['ref', 'num_repeats'], 'label': 'microsatellite'}, # alt = e.g. (CA)12/17/... i.e. repeated seq + num repeats in each allele
                        'mnp': {'params': ['ref', 'alt'], 'label': 'MNP'}, # alt = allele list
                        'insertion': {'params': ['alt'], 'label': 'sgv_insertion'}, # no ref because it is null
                        'deletion': {'params': ['ref'], 'label': 'sgv_deletion'} # alt = allele list (may include null allele i.e. deleted)
                        }
    _label_remap = {'SNP': 'single', 'sgv_indel': 'in-del', 'microsatellite': 'microsatellite', 'MNP': 'mnp', 'sgv_insertion': 'insertion', 'sgv_deletion': 'deletion'}
    #_opt_params = ['ref', 'num_repeats', 'strand', 'population_allele_frequencies']
    #_mode_params = {'coord' : ['chrom', 'start', 'end', 'var_type', 'alt'], 'hgvs': ['ac', 'hgvs_syntax']}
    _filtering_params = set(['chrom', 'start', 'end', 'gene_uuid', 'tx_uuid'])
    
    _hgvsparser = hgvs.parser.Parser()

    _seq_utils_tx = RefSequence('transcriptome')
    _seq_utils_gen = RefSequence('genome')
    _graph_utils = GenomeGraphUtility()
    _data_prov_tx = None
    _data_prov_gen = None

    def __init__(self):
        self._params = {'name': None,
                        'chrom': None,
                        'start': None,
                        'end': None,
                        'var_type': None,
                        'ref': None,
                        'strand': None,
                        'allele': None,
                        'label': None,
                        'gene_uuid': None,
                        'gene_ac': None,
                        'gene_symbol': None,
                        'tx_ac': None,
                        'x_ref': None
                        }
        self._in_graph = None
        self._region_uuid = None
        self._multi_region = False
        self._dbSNP_entry = None

    @staticmethod
    def getAnnotationModel():
        return annotations.models.Annotation_ShortGeneticVariation

    @staticmethod
    def getGraphLabel():
        return ShortGeneticVariation._graph_label

    def _connectToDataProviders(self):
        self._data_prov_tx = UTAlas.connect(db_url='lasannotations://',graph_utils_obj=self._graph_utils,seq_utils_obj=self._seq_utils_tx)
        self._data_prov_gen = UTAlas.connect(db_url='lasannotations://',graph_utils_obj=self._graph_utils,seq_utils_obj=self._seq_utils_gen)

    '''def getWildType(self, chrom=None, start=None, end=None):
        chrom = chrom or self._params['chrom']
        start = start or self._params['start']
        end = end or self._params['end']
        if chrom is None or start is None or end is None:
            raise Exception("Missing required parameters: {0}, {1}, {2}".format('chrom', 'start', 'end'))
        return self._graph_utils.getOrCreateWildType(chrom, start, end)'''

    @staticmethod
    def getFilteringParams():
        return copy.copy(ShortGeneticVariation._filtering_params)

    def exists(self):
        if self._in_graph == None:
            self._checkExists()
        return self._in_graph

    def _checkExists(self):
        self._uuid = None
        self._in_graph = None

        self._checkValid()

        res = self._graph_utils.getShortGeneticVariation(name=self._params['name'],allele=self._params['allele'])
        if res != None:
            self._in_graph = True
            self._params['uuid'] = res[0]
            self._region_uuid = res[1]
        else:
            self._in_graph = False

    def convertToMultiRegion(self, chrom, start, end, strand):
        hr_uuid = self._graph_utils.getOrCreateHomologousRegion(self._region_uuid)
        if self._graph_utils.relinkShortGeneticVariationToRegion(self._params['uuid'], hr_uuid) == True:
            self._multi_region = True
            self._region_uuid = hr_uuid
        self.addMultiRegion(chrom, start, end, strand)

    def isMultiRegion(self):
        if self._multi_region is None:
            self._checkMultiRegion()
        return self._multi_region

    def _checkMultiRegion(self):
        self._multi_region = self._graph_utils.isMultiRegion(self._region_uuid)

    def addMultiRegion(self, chrom, start, end, strand):
        # region might already exist as well as not (it will be created)
        reg_uuid = self._graph_utils.getRegionByCoords(chrom, start, end, strand)
        if len(reg_uuid) == 0:
            reg_uuid = self._graph_utils.createRegion(chrom, start, end, strand)
        else:
            reg_uuid = reg_uuid[0] # assume there is always only one region
        # the following shouldn't be done if the region is already linked to the homologous region (which might be the case when the snp has another allele that was already converted to multi-region mode) ---> solved by using merge instead of create in the query
        self._graph_utils.linkRegionToHomologousRegion(reg_uuid, self._region_uuid)
        genes = self._graph_utils.getGeneUUIDsFromRegion(reg_uuid)
        for g_uuid in genes:
            self._graph_utils.linkShortGeneticVariationToGene(self.getUUID(), g_uuid)

    def getMultiRegions(self):
        return self._graph_utils.getContainedRegionsFromHomologousRegion(self._region_uuid)

    def removeMultiRegion(self, region_uuid):
        if not self._graph_utils.deleteRegionFromHomologousRegion(region_uuid, self._region_uuid):
            raise Exception("The specified region is not included in the current multiregion")

    def setDefaultRegion(self, region_uuid):
        if not self._graph_utils.updateHomologousRegionCoordinates(self._region_uuid, region_uuid):
            raise Exception("The specified region is not included in the current multiregion")
        
    def convertToSingleRegion(self, region_uuid):
        # region_uuid is the uuid of the region we wish to associate with the snp
        self._multi_region = False
        # first, unlink snp from homologous region and relink it to the specified region
        rr = self.getMultiRegions()
        if region_uuid not in rr:
            raise Exception("Specified region does not belong to multi-regions")
        self._graph_utils.relinkShortGeneticVariationToRegion(self._params['uuid'], region_uuid)
        # then, unlink snp from all genes
        self._graph_utils.unlinkShortGeneticVariationFromGenes(self._params['uuid'])
        # and link it to the gene (if any) that includes the specified region
        genes = self._graph_utils.getGeneUUIDsFromRegion(region_uuid)
        for g_uuid in genes:
            self._graph_utils.linkShortGeneticVariationToGene(self._params['uuid'], g_uuid)
        # finally, delete hr
        # (note that calling delete hr on an hr that still has nodes linked to it will result in an exception
        # so we should look out for the exception and ignore it, because it means it still has other snps.
        # The region will finally be deleted once there are no more snps.)
        try:
            self._graph_utils.deleteHomologousRegion(self._region_uuid)
        except:
            print "homologous region still has references, skipping delete operation"
        self._region_uuid = region_uuid

    def getDbSNPEntry(self):
        return self._dbSNP_entry
        #else:
        #    return UCSCSnp141.objects.filter(class=self._params['var_type'],chromosome=self._params['chrom'],start_position=self._params['start']-1,end_position=self._params['end'],altered_seq=self._params['alt'],reference_seq=self._params['ref'])

    def _checkValid(self):
        return self._params['name'] is not None

    def getGenomicAnnotations(self):
        # returns a list of items (more or less) like the following (indicating where the alteration will be mapped to):
        # {
        #   'exon': {'ensembl_id': ..., 'exon_no': ..., 'start': ..., 'end': ... },
        #   'transcript': [
        #           {'ensembl_id': ..., 'start': ..., 'end': ...}, ...
        #    ],
        #   'gene': {'ensemble_id': ..., 'symbol': ..., 'start': ..., 'end': ..., 'strand': ...}
        #   'chromosome': ...
        # }
        self._checkValid()
        return self._graph_utils.getGenomicLocationAnnotation(self._params['chrom'], self._params['start'])

    @staticmethod
    def byUuid_list(uuid_list):
        res = ShortGeneticVariation._graph_utils.getShortGeneticVariation_byUuid_list(uuid_list=uuid_list)
        objs = []
        for r in res:
            s = ShortGeneticVariation()
            s.byUuid(r[0], r)
            objs.append(s)
        return objs

    def byUuid(self, uuid, res=None):
        if res is None:
            res = self._graph_utils.getShortGeneticVariation_byUuid(uuid)
        if res is None:
            raise Exception("Not found")
        self._in_graph = True
        self._params['chrom'] = res['chrom']
        self._params['start'] = res['start']
        self._params['end'] = res['end']
        self._params['strand'] = res['strand']
        self._params['name'] = res['name']
        #label = filter(lambda x: True if x in self._label_remap else False, res['labels'])[0]
        self._params['var_type'] = self._label_remap[res['labels']]
        self._params['allele'] = res['allele']
        self._params['popul_freq'] = res['freq']
        self._params['uuid'] = res['uuid']
        if self._params['var_type'] != 'microsatellite':
            #self._params['alleles'] = {res['allele']:{'alt': res['alt'], 'popul_freq': res['freq'], 'allele': res['allele'], 'uuid': uuid}}
            self._params['alt'] = res['alt']
        else:
            #self._params['alleles'] = {res['allele']:{'num_repeats': res['num_repeats'], 'popul_freq': res['freq'], 'allele': res['allele'], 'uuid': uuid}}
            self._params['num_repeats'] = res['num_repeats']
        self._params['gene_uuid'] = res['gene_uuid']
        self._params['gene_ac'] = res['gene_ac']
        self._params['gene_symbol'] = res['gene_symbol']
        self._params['x_ref'] = res['x_ref']
        self._region_uuid = res['region_uuid']
        self._multi_region = res['multi_region']

    '''def getInfo(self):
        r = []
        for allele, content in self._params['alleles'].iteritems():
            res = {}
            res['uuid'] = content['uuid']
            res['ref'] = 'chr' + self._params['chrom']
            res['start'] = self._params['start']
            res['end'] = self._params['end']
            res['strand'] = self._params['strand']
            res['name'] = self._params['name']
            res['type'] = self._params['var_type']
            res['allele'] = allele
            res['freq'] = content['popul_freq']
            if 'alt' in content:
                res['alt'] = content['alt']
            elif 'num_repeats' in content:
                res['num_repeats'] = content['num_repeats']
            r.append(res)
        return r'''

    def getInfo(self):
        res = {}
        res['uuid'] = self.getUUID()
        res['chrom'] = self._params['chrom']
        res['start'] = self._params['start']
        res['end'] = self._params['end']
        res['strand'] = self._params['strand']
        res['name'] = self._params['name']
        res['type'] = self._params['var_type']
        res['allele'] = self._params['allele']
        res['freq'] = self._params.get('popul_freq', None)
        res['alt'] = self._params.get('alt', None)
        res['num_repeats'] = self._params.get('num_repeats', None)
        res['gene_uuid'] = self._params['gene_uuid']
        res['gene_ac'] = self._params['gene_ac']
        res['gene_symbol'] = self._params['gene_symbol']
        res['x_ref'] = self._params['x_ref']
        return res

    def setNewAllele(self, allele, alt):
        if allele.upper() not in map(chr,range(ord('A'),ord('Z')+1)):
            raise Exception("Allele must be a letter from 'A/a' to 'Z/z'")
        if (allele == self._params['allele']) != (alt == self._params['alt']):
            raise Exception("Allele name and alt must be different")
        self._params['allele'] = allele
        self._params['alt'] = alt

    def set(self, dbSnpLookup=True, name=None, allele=None, obj=None, **params):
        # no allele, no party
        if allele is None:
            raise Exception("Please provide the allele")
        # is this an acceptable allele name?
        try:
            allele = str(allele)
            assert(allele.upper() in map(chr,range(ord('A'),ord('Z')+1)))
            allele_name = allele
            allele = ord(allele.upper()) - ord('A')
        except:
            raise Exception("Allele must be a letter from 'A/a' to 'Z/z'")

        self._params['allele'] = allele_name
        
        # which parameters have been provided?
        if obj is not None:
            # use the provided dbSNP object
            _dbSNP_entry = obj
            name = obj.name
        elif name is not None:
            if dbSnpLookup == True:
                # use dbSnp to look this name up
                try:
                    _dbSNP_entry = annotations.models.UCSCSnp141.objects.get(name=name)
                except:
                    # not there or more than one same-named entries found
                    raise NonUniqueEntryError(name)
            else:
                _dbSNP_entry = None
                try:
                    self._params['chrom'] = str(params['chrom'])
                    self._params['start'] = long(params['start'])
                    self._params['end'] = long(params['end'])
                    self._params['var_type'] = params['var_type']
                    try:
                        self._var_types_params[self._params['var_type']]
                    except:
                        raise Exception("Invalid type %s" % self._params['var_type'])
                    for p in self._var_types_params[self._params['var_type']]['params']:
                        self._params[p] = params[p]
                    self._params['strand'] = params['strand']
                except Exception, e:
                    text2 = "\nAllowed values: " + ", ".join(self._var_types_params.keys()) if e.args[0] == 'var_type' else ""
                    raise Exception("Missing parameter %s%s" % (e.args[0], text2))

        else:
            raise Exception("Please provide one of the following parameter combinations: (obj=dbSNPObject) or (dbSnpLookup=True, name=snpName) or (dbSnpLookup=True, name=snpName, param1=...[, param2=...])")

        if _dbSNP_entry is not None:
            self._params['chrom'] = _dbSNP_entry.chrom.replace('chr', '')

            if _dbSNP_entry.chromStart != _dbSNP_entry.chromEnd:
                self._params['start'] = _dbSNP_entry.chromStart + 1
                self._params['end'] = _dbSNP_entry.chromEnd
            else:
                self._params['start'] = _dbSNP_entry.chromEnd
                self._params['end'] = _dbSNP_entry.chromEnd

            self._params['var_type'] = _dbSNP_entry.snpClass
            self._params['ref'] = _dbSNP_entry.refNCBI if _dbSNP_entry.refNCBI.strip() != '-' else None
            self._params['strand'] = _dbSNP_entry.strand
            alleleFreqs = [float(x) for x in _dbSNP_entry.alleleFreqs.split(',')[:-1]]
            try:
                self._params['popul_freq'] = alleleFreqs[allele]
            except:
                self._params['popul_freq'] = None
            
            self._params['uuid'] = None

            if _dbSNP_entry.observed != 'lengthTooLong':

                if self._params['var_type'] != 'microsatellite':
                    alt = [x if x != '-' else None for x in _dbSNP_entry.observed.split('/')]
                    if len(alt) <= allele:
                        raise Exception("Allele %s not found for current entry" % allele_name)
                    #num_alleles = len(alt)
                    #allele_names = map(chr, range(ord('A'), ord('A') + num_alleles))
                    #self._params['alleles'] = {z:{'alt': x, 'popul_freq': y, 'allele': z, 'uuid': None} for x,y,z in zip(alt, alleleFreqs, allele_names)}
                    if self._params['var_type'] != 'deletion':
                        self._params['alt'] = alt[allele]
                    else:
                        self._params['ref'] = alt[allele]
                    try:
                        del self._params['num_repeats']
                    except:
                        pass

                else: # microsatellite
                    parts = _dbSNP_entry.observed.split(')')
                    #alt = parts[0].replace('(', '')
                    #if _dbSNP_entry.strand == '-':
                    #    alt = Seq.reverse_complement(str(alt))
                    num_repeats = []
                    for x in parts[1].split('/'):
                        try:
                            num_repeats.append(int(x))
                        except:
                            num_repeats.append(None)
                    #num_alleles = len(num_repeats)
                    #allele_names = map(chr, range(ord('A'), ord('A') + num_alleles))
                    #self._params['alleles'] = {z:{'num_repeats': x, 'popul_freq': y, 'allele': z, 'uuid': None} for x,y,z in zip(num_repeats, alleleFreqs, allele_names)}
                    if len(num_repeats) <= allele:
                        raise Exception("Allele %s not found for current entry" % allele_name)
                    self._params['num_repeats'] = num_repeats[allele]
                    try:
                        del self._params['alt']
                    except:
                        pass
                    
            else:
                raise InvalidEntryError("lengthTooLong")

        self._dbSNP_entry = _dbSNP_entry
        self._params['name'] = name
        self._in_graph = None

        # fill out gene information
        info = self._graph_utils.getGenesInRegion(chrom=self._params['chrom'],start=self._params['start'],end=self._params['end'])
        ret = len(info)
        if len(info) > 0:
            self._params['gene_symbol'] = info[0][1]
            self._params['gene_uuid'] = info[0][0]
            self._params['gene_ac'] = info[0][2]
            params['strand'] = info[0][4]
        else:
            self._params['gene_symbol'] = None
            self._params['gene_uuid'] = None
            self._params['gene_ac'] = None
        return ret

    def setXref(self, xref):
        self._params['x_ref'] = xref

    def save(self):
        # saves current variation and maps it to the appropriate locations
        # make sure that all required parameters have been defined
        if self.exists() == True:
            print "Already exists"
            return

        self._checkValid()

        # identify region onto which variation will be mapped
        #print "call getRegionByCoords"
        reg_uuid = self._graph_utils.getRegionByCoords(chrom=self._params['chrom'], start=self._params['start'], end=self._params['end'], strand=self._params['strand'])
        #print "returned = ", reg_uuid
        if len(reg_uuid) == 0:
            #print "call createRegion"
            reg_uuid = self._graph_utils.createRegion(self._params['chrom'], self._params['start'], self._params['end'], self._params['strand'])
            #print "returned", reg_uuid
        else:
            reg_uuid = reg_uuid[0] # assume there is always only one region
            # (there should be only one)
        self._region_uuid = reg_uuid
        # create ShortGeneticVariation nodes
        #print "call createShortGeneticVariation"
        args = {'strand': self._params['strand'], 'name': self._params['name'], 'allele': self._params['allele'], 'popul_freq': self._params.get('popul_freq', None)}
        if 'alt' in self._params:
            args['alt'] = self._params['alt']
        elif 'num_repeats' in self._params:
            args['num_repeats'] = self._params['num_repeats']
        elif 'ref' in self._params:
            args['ref'] = self._params['ref']
        if self._params['x_ref'] is not None:
            args['x_ref'] = self._params['x_ref']
        self._params['uuid'] = self._graph_utils.createShortGeneticVariation(region_uuid=reg_uuid, sgv_label=self._var_types_params[self._params['var_type']]['label'], **args)
        #print "returned = ", self._uuid

        # get gene(s) to which alteration is linked, if any
        #print "call getGeneUUIDsFromRegion"
        #genes_uuid = self._graph_utils.getGeneUUIDsFromRegion(region_uuid=reg_uuid)
        #print "returned = ", genes_uuid
        #take first gene only
        #for g in genes_uuid:
        #print "call linkShortGeneticVariationToGene"
        if self._params['gene_uuid'] is not None:
            self._graph_utils.linkShortGeneticVariationToGene(var_uuid=self._params['uuid'], gene_uuid=self._params['gene_uuid'])
        #print "returned"

        self._in_graph = True

    def delete(self):
        if self.exists() == False:
            return
        var_region_uuid = self._graph_utils.getRegionFromChild(uuid=self._params['uuid'],label='short_genetic_variation')
        self._graph_utils.deleteShortGeneticVariation(uuid=self._params['uuid'])
        self._params['uuid'] = None
        self._graph_utils.deleteRegion(uuid=var_region_uuid)
        self._in_graph = False

    def getUUID(self):
        if self.exists() == True:
            return self._params['uuid']

    @staticmethod
    def filter(**args):
        if len(set(args.keys()).difference(SequenceAlteration._filtering_params)) > 0:
            return []

        res = ShortGeneticVariation._graph_utils.getShortGeneticVariationsByPosition(**args)
        objs = []
        for r in res:
            s = ShortGeneticVariation()
            s.byUuid(r[0], r)
            objs.append(s)
        return objs

class CopyNumberVariation(KBReference):
    _graph_label = 'copy_number_variation'
    _cnv_types = {  'amplification': {'label': 'feature_amplification'},
                    'gain': {'label': 'copy_number_gain'},
                    'neutral': {'label': 'copy_number_neutral'},
                    'loss': {'label': 'copy_number_loss'},
                    'deletion': {'label': 'feature_ablation'}
                }
    _label_remap = {'feature_amplification': 'amplification',
                    'copy_number_gain': 'gain',
                    'copy_number_neutral': 'neutral',
                    'copy_number_loss': 'loss',
                    'feature_ablation': 'deletion'}
    _gene_params = ['geneUuid', 'geneAc', 'geneSymbol']
    _region_params = ['chrom', 'start', 'end']

    _thresholds = {0: 'deletion', 0.25: 'loss', 1: 'neutral', 3: 'gain', 5: 'amplification'}
    _graph_utils = GenomeGraphUtility()
    _filtering_params = set(['chrom', 'start', 'end', 'gene_uuid', 'tx_uuid'])

    def __init__(self):
        self._params = {
            'type': None,
            'geneUuid': None,
            'geneAc': None,
            'geneSymbol': None,
            'source': None,
            'chrom': None,
            'start': None,
            'end': None,
            'x_ref': None
        }
        self._uuid = None
        self._other_instances = []
        self._in_graph = None
        self._mode = None

    @staticmethod
    def getFilteringParams():
        return copy.copy(SequenceAlteration._filtering_params)

    @staticmethod
    def getAnnotationModel():
        return annotations.models.Annotation_CopyNumberVariation

    @staticmethod
    def getGraphLabel():
        return CopyNumberVariation._graph_label

    def set(self, **kwargs):
        # type of cnv is mandatory
        # a gene can be provided (uuid, ac or symbol)
        # or a region (chrom,start,end) which will be mapped onto a gene (if possible)
        # (If the provided region cannot be mapped onto a gene, a region node will be created instead and the CNV will be attached to it)
        try:
            if kwargs['type'] in self._cnv_types:
                self._params['type'] = kwargs['type']
            else:
                raise Exception("Unknown CopyNumberVariation type: '{0}'".format(_type))
        except Exception as e:
            if 'cn' in kwargs:
                self._params['type'] = self._thresholds[max(filter(lambda z: z <= kwargs['cn'], self._thresholds))]
            else:
                raise Exception("Missing required parameter: '{0}'".format(e))
        
        # has a gene been provided? (uuid/ac/symbol)

        for p in self._gene_params:
            try:
                self._params[p] = kwargs[p]
                print "Gene mode detected - {0} provided".format(p)
                self._mode = "gene"
                break
            except:
                pass
        else:
            # no gene - check if a region has been provided
            tmp = {}
            for p in self._region_params:
                try:
                    tmp[p] = kwargs[p]
                except:
                    print "Region mode: missing required parameter {0}".format(p)
                    return
            self._params.update(tmp)
            self._mode = "region"
            print "Region mode detected"

        if self._mode == 'gene':
            if self._params['geneUuid'] is None:
                par = {'ac': self._params['geneAc'], 'symbol': self._params['geneSymbol']}
                res = self._graph_utils.getGeneInfo(**par)
                if len(res) == 0:
                    raise Exception("Gene not in database")
                self._params['geneUuid'] = res[0].uuid

        self._params['source'] = kwargs.get('source', None)

    def setXref(self, xref):
        self._params['x_ref'] = xref

    @staticmethod
    def byUuid_list(uuid_list):
        res = CopyNumberVariation._graph_utils.getCopyNumberVariation_byUuid_list(uuid_list=uuid_list)
        objs = []
        for r in res:
            s = CopyNumberVariation()
            s.byUuid(r[0], r)
            objs.append(s)
        return objs

    def byUuid(self, uuid, res=None):
        if res is None:
            res = self._graph_utils.getCopyNumberVariation_byUuid(uuid)
        if res:
            self._uuid = uuid
            label = filter(lambda x: True if x in self._label_remap else False, res[1])[0]
            self._params['type'] = self._label_remap[label]
            self._params['chrom'] = res[2]
            self._params['start'] = res[3]
            self._params['end'] = res[4]
            self._params['geneUuid'] = res[5]
            self._params['geneAc'] = res[6]
            self._params['geneSymbol'] = res[7]
            self._params['source'] = res[8]
            self._mode == 'region'
            self._in_graph = True
            self._params['x_ref'] = res['x_ref']
        else:
            raise Exception("Not found")

    def getInfo(self):
        if self._uuid and self._params['chrom'] is None:
            self.byUuid(self._uuid)
        res = {}
        res['uuid'] = self._uuid
        res['type'] = self._params['type']
        res['ref'] = 'chr' + self._params['chrom']
        res['start'] = self._params['start']
        res['end'] = self._params['end']
        res['geneUuid'] = self._params['geneUuid']
        res['geneAc'] = self._params['geneAc']
        res['geneSymbol'] = self._params['geneSymbol']
        res['source'] = self._params['source']
        res['x_ref'] = self._params['x_ref']
        return res

    def save(self):
        if self.exists() == True:
            print "Already exists"
            return
        
        if self._mode == 'gene':
            target_uuid_list = [self._params['geneUuid']]
        else:
            res = self._graph_utils.getGenesInRegion(self._params['chrom'], self._params['start'], self._params['end'])
            target_uuid_list = [x[0] for x in res]

        if len(target_uuid_list) == 0:
            reg_uuid = self._graph_utils.getRegionByCoords(chrom=self._params['chrom'], start=self._params['start'], end=self._params['end'])
            if len(reg_uuid) == 0:
                reg_uuid = self._graph_utils.createRegion(self._params['chrom'], self._params['start'], self._params['end'])
            else:
                reg_uuid = reg_uuid[0] # assume there is always only one region
            target_uuid_list = [reg_uuid]
        
        args = {}
        if self._params['x_ref'] is not None:
            args['x_ref'] = self._params['x_ref']
        this_uuid_list = self._graph_utils.createCopyNumberVariation(target_uuid_list=target_uuid_list, cnv_label=self._cnv_types[self._params['type']]['label'], source=self._params['source'], **args)
        self._uuid = this_uuid_list[0]
        if len(this_uuid_list) > 1:
            self._other_instances = [x for x in this_uuid_list[1:]]
        self._in_graph = True

    def getOtherUUIDs(self):
        return self._other_instances

    def exists(self):
        if self._in_graph == None:
            self._checkExists()
        return self._in_graph

    def _checkExists(self):
        self._uuid = None
        self._in_graph = None

        self._checkValid()

        if self._mode == 'gene':
            res = self._graph_utils.getCopyNumberVariation_byGene(gene_uuid=self._params['geneUuid'], cnv_label=self._cnv_types[self._params['type']]['label'])
        elif self._mode == 'region':
            res = self._graph_utils.getCopyNumberVariation_byRegion(region_chrom=self._params['chrom'], region_start=self._params['start'], region_end=self._params['end'], cnv_label=self._cnv_types[self._params['type']]['label'])
        else:
            return
        if res != None:
            self._uuid = res
            self._in_graph = True
        else:
            self._in_graph = False

    def getUUID(self):
        if self.exists() == True:
            return self._uuid

    def _checkValid(self):
        return self._params['type'] is not None and self._params['geneUuid'] is not None

    def delete(self):
        if self.exists() == False:
            return
        var_region_uuid = self._graph_utils.getRegionFromChild(uuid=self._uuid,label='copy_number_variation')
        self._graph_utils.deleteCopyNumberVariation(uuid=self._uuid)
        self._uuid = None
        self._in_graph = False
        if var_region_uuid is not None:
            self._graph_utils.deleteRegion(uuid=var_region_uuid)

    @staticmethod
    def filter(**args):
        if len(set(args.keys()).difference(CopyNumberVariation._filtering_params)) > 0:
            return []

        res = CopyNumberVariation._graph_utils.getCopyNumberVariationsByPosition(**args)
        objs = []
        for r in res:
            v = CopyNumberVariation()
            v.byUuid(r[0], r)
            objs.append(v)
        return objs

class FusionTranscript(KBReference):
    _mandatory_args = ['gene1_symbol', 'gene1_chrom', 'gene2_symbol', 'gene2_chrom']
    _mandatory_alternative_args = [(['gene1_brkp'], ['gene1_brkp_interval_start', 'gene1_brkp_interval_end']), (['gene2_brkp'], ['gene2_brkp_interval_start', 'gene2_brkp_interval_end'])]
    _graph_utils = GenomeGraphUtility()

    def __init__(self):
        # N.B.  (1) gene1 := gene 5p of the fusion, gene2 := gene 3p of the fusion
        #       (2) As a first release, an uncertainty interval for the gene breakpoint is supported only if user-provided
        #       ToDo: receive a boolean value (brkp_is_uncertain: true/false) and automatically infer the uncertainty interval based on the breakpoint position (requires knowledge of things such as UTRs, which are currently not in the graph)
        self._params = {
            "gene1_symbol": None,
            "gene1_uuid": None,
            "gene1_start": None,            
            "gene1_end": None,
            "gene1_chrom": None,
            "gene1_brkp": None,
            "gene1_brkp_interval_start": None,
            "gene1_brkp_interval_end": None,            
            "tx1_ac": None,
            "tx1_uuid": None,
            "tx1_brkp": None,
            "tx1_offset": None,
            "tx1_datum": None,
            "tx1_interval_start": None,
            "tx1_interval_start_offset": None,
            "tx1_interval_start_datum": None,
            "tx1_interval_end": None,
            "tx1_interval_end_offset": None,
            "tx1_interval_end_datum": None,
            "gene2_symbol": None,
            "gene2_uuid": None,
            "gene2_start": None,            
            "gene2_end": None,
            "gene2_chrom": None,
            "gene2_brkp": None,
            "gene2_brkp_interval_start": None,
            "gene2_brkp_interval_end": None,            
            "tx2_ac": None,
            "tx2_uuid": None,
            "tx2_brkp": None,
            "tx2_offset": None,
            "tx2_datum": None,
            "tx2_interval_start": None,
            "tx2_interval_start_offset": None,
            "tx2_interval_start_datum": None,
            "tx2_interval_end": None,
            "tx2_interval_end_offset": None,
            "tx2_interval_end_datum": None,
            "fg_uuid": None,
            "ft_uuid": None,
            "fg_name": None,
            "ft_name": None
        }
    def set(self, **args):
        #tx1_start, tx1_end, tx2_start, tx2_end, gene1_symbol, gene2_symbol, gene1_uuid, gene2_uuid, tx1_ac, tx2_ac, tx1_uuid, tx2_uuid
        for x in self._mandatory_args:
            try:
                self._params[x] = args[x]
            except:
                raise Exception("Mandatory argument '{0}' not found".format(x))

        # mandatory but alternative args
        for option_list in self._mandatory_alternative_args:
            # there must exist an option within option_list for which all option_members have been specified
            one_option_is_ok = False
            for option in option_list:
                option_has_all_members = True
                dic = {}
                for option_member in option:
                    try:
                        dic[option_member] = args[option_member]
                    except:
                        option_has_all_members = False
                        break
                if option_has_all_members == True:
                    one_option_is_ok = True
                    break
            if one_option_is_ok == True:
                self._params.update(dic)
            else:
                raise Exception("One of the following argument combinations must be provided, but none found:\n" + "  OR  ".join(["(" + ", ".join(z) + ")" for z in option_list]))

        # names
        for x in ["fg_name", "ft_name"]:
            try:
                self._params[x] = args[x]
            except:
                self._params[x] = "{0}_{1}".format(self._params['gene1_symbol'], self._params['gene2_symbol'])

        # lookup genes and get uuid
        for p in ['gene1_symbol', 'gene2_symbol']:
            try:
                res = self._graph_utils.getGeneInfo(**{'symbol': self._params[p]})
                self._params[p.replace('symbol', 'uuid')] = res[0].uuid
                self._params[p.replace('symbol', 'start')] = res[0].start
                self._params[p.replace('symbol', 'end')] = res[0].end
            except:
                raise Exception("Gene '{0}' not found".format(self._params[p]))

        # get default txs for genes
        for p in ['gene1_uuid', 'gene2_uuid']:
            try:
                res = self._graph_utils.getDefaultTranscriptForGene(gene_uuid=self._params[p])
                q = p.replace('gene', 'tx')
                self._params[q] = res.uuid
                q = q.replace('uuid', 'ac')
                self._params[q] = res.ac
            except:
                raise Exception("Default transcript for gene '{0}' not found".format(self._params[p.replace('uuid', 'symbol')]))

        # tx coordinate calculations from exact brkp or genomic interval
        if self._params['gene1_brkp'] is not None:
            # exact breakpoint
            remap1 = self._map_coord_g_to_c(self._params['gene1_chrom'], self._params['gene1_brkp'], self._params['tx1_ac'])
            self._params['tx1_brkp'], self._params['tx1_offset'], self._params['tx1_datum'] = remap1['cds_start_base'], remap1['cds_start_offset'], remap1['cds_start_datum']
        else:
            # interval
            remap1_start = self._map_coord_g_to_c(self._params['gene1_chrom'], self._params['gene1_brkp_interval_start'], self._params['tx1_ac'])
            remap1_end = self._map_coord_g_to_c(self._params['gene1_chrom'], self._params['gene1_brkp_interval_end'], self._params['tx1_ac'])
            if remap1_start == remap1_end:
                self._params['tx1_brkp'], self._params['tx1_offset'], self._params['tx1_datum'] = remap1_start['cds_start_base'], remap1['cds_start_offset'], remap1['cds_start_datum']
            else:
                self._params['tx1_interval_start'], self._params['tx1_interval_start_offset'], self._params['tx1_interval_start_datum'] = remap1_start['cds_start_base'], remap1_start['cds_start_offset'], remap1_start['cds_start_datum']
                self._params['tx1_interval_end'], self._params['tx1_interval_end_offset'], self._params['tx1_interval_end_datum'] = remap1_end['cds_start_base'], remap1_end['cds_start_offset'], remap1_end['cds_start_datum']

        if self._params['gene2_brkp'] is not None:
            # exact breakpoint
            remap2 = self._map_coord_g_to_c(self._params['gene2_chrom'], self._params['gene2_brkp'], self._params['tx2_ac'])
            self._params['tx2_brkp'], self._params['tx2_offset'], self._params['tx2_datum'] = remap2['cds_start_base'], remap2['cds_start_offset'], remap2['cds_start_datum']
        else:
            # interval
            remap2_start = self._map_coord_g_to_c(self._params['gene2_chrom'], self._params['gene2_brkp_interval_start'], self._params['tx2_ac'])
            remap2_end = self._map_coord_g_to_c(self._params['gene2_chrom'], self._params['gene2_brkp_interval_end'], self._params['tx2_ac'])
            if remap2_start == remap2_end:
                self._params['tx2_brkp'], self._params['tx2_offset'], self._params['tx2_datum'] = remap2_start['cds_start_base'], remap2['cds_start_offset'], remap2['cds_start_datum']
            else:
                self._params['tx2_interval_start'], self._params['tx2_interval_start_offset'], self._params['tx2_interval_start_datum'] = remap2_start['cds_start_base'], remap2_start['cds_start_offset'], remap2_start['cds_start_datum']
                self._params['tx2_interval_end'], self._params['tx2_interval_end_offset'], self._params['tx2_interval_end_datum'] = remap2_end['cds_start_base'], remap2_end['cds_start_offset'], remap2_end['cds_start_datum']
    #TODO: SISTEMARE MODELLO X MEMORIZZARE VALORE DI PROBABILITA', SISTEMARE SCHERMATE
    def save(self):
        # create gene regions
        # gene1 region (g1_start, brkp)
        g1_end = self._params['gene1_brkp'] if self._params['gene1_brkp'] is not None else (self._params['gene1_brkp_interval_start'], self._params['gene1_brkp_interval_end'])
        reg1_g_uuid = self._getOrCreateRegion(self._params['gene1_chrom'], self._params['gene1_start'], g1_end, self._params['gene1_uuid'])
        # gene2 region (brkp, g2_end)
        g2_start = self._params['gene2_brkp'] if self._params['gene2_brkp'] is not None else (self._params['gene2_brkp_interval_start'], self._params['gene2_brkp_interval_end'])
        reg2_g_uuid = self._getOrCreateRegion(self._params['gene2_chrom'], g2_start, self._params['gene2_end'], self._params['gene2_uuid'])
        # create fusion gene
        fg_name = self._params['fg_name']
        fg_uuid = self._graph_utils.createFusionGene(fg_name, self._params['gene1_uuid'], self._params['gene2_uuid'], reg1_g_uuid, reg2_g_uuid)
        self._params['fg_uuid'] = fg_uuid

        # create fusion transcript
        # only if the break position is within the cds region for both genes
        # (TODO: if not, keine Ahnung...??)
        if self._params['tx1_datum'] == hgvs.location.CDS_START and self._params['tx1_brkp'] >= 1 and self._params['tx2_datum'] == hgvs.location.CDS_START and self._params['tx2_brkp'] >= 1:
            
            # start/end coordinates of each transcript need to be retrieved
            # for coherence with other transcript regions created elsewhere, the type of coordinates used to define such regions is the 0-based offset from the start of the transcript (i.e., NOT the cds coordinates)
            tx1_info = self._graph_utils.getTranscriptInfo(ac=self._params['tx1_ac'])[0]
            tx2_info = self._graph_utils.getTranscriptInfo(ac=self._params['tx2_ac'])[0]


            if self._params['tx1_brkp'] is not None:
                tx1_coord = self._map_coord_tx_c_to_tx(self._params['tx1_brkp'], self._params['tx1_datum'], tx1_info['tx.cds_start'], tx1_info['tx.cds_end'])
            else:
                tx1_coord_start = self._map_coord_tx_c_to_tx(self._params['tx1_interval_start'], self._params['tx1_interval_start_datum'], tx1_info['tx.cds_start'], tx1_info['tx.cds_end'])
                tx1_coord_end = self._map_coord_tx_c_to_tx(self._params['tx1_interval_end'], self._params['tx1_interval_end_datum'], tx1_info['tx.cds_start'], tx1_info['tx.cds_end'])
                tx1_coord = (tx1_coord_start, tx1_coord_end)

            if self._params['tx2_brkp'] is not None:
                tx2_coord = self._map_coord_tx_c_to_tx(self._params['tx2_brkp'], self._params['tx2_datum'], tx2_info['tx.cds_start'], tx2_info['tx.cds_end'])
            else:
                tx2_coord_start = self._map_coord_tx_c_to_tx(self._params['tx2_interval_start'], self._params['tx2_interval_start_datum'], tx2_info['tx.cds_start'], tx2_info['tx.cds_end'])
                tx2_coord_end = self._map_coord_tx_c_to_tx(self._params['tx2_interval_end'], self._params['tx2_interval_end_datum'], tx2_info['tx.cds_start'], tx2_info['tx.cds_end'])
                tx2_coord = (tx2_coord_start, tx2_coord_end)

            print "tx1_coord", tx1_coord, "tx2_coord", tx2_coord
            reg1_tx_uuid = self._getOrCreateTranscriptRegion(self._params['tx1_ac'], 0, tx1_coord)
            reg2_tx_uuid = self._getOrCreateTranscriptRegion(self._params['tx2_ac'], tx2_coord, sum(tx2_info['exon.lengths']) - 1)

            print "reg1_tx_uuid", reg1_tx_uuid, "reg2_tx_uuid", reg2_tx_uuid
            print "fg_uuid", fg_uuid

            ft_name = self._params['ft_name']
            self._params['ft_uuid'] = self._graph_utils.createFusionTranscript(ft_name, fg_uuid, reg1_tx_uuid, reg2_tx_uuid)
        
        else:
            # at least one breakpoint is outside of the coding region
            # I don't know what to do with this, I'll skip the creation of the fusion transcript and issue a warning
            print("WARNING: at least one breakpoint is outside of the coding region, fusion transcript not created!")

    def _map_coord_g_to_c(self, chrom, start_g, tx_ac):
        print "_map_coord_g_to_c"
        tx = self._graph_utils.getTranscriptInfo(ac=tx_ac)
        if len(tx) == 0:
            raise Exception("Transcript not found")
        tx = tx[0]
        if tx['tx.cds_start'] is None:
            raise Exception("Cannot map, transcript is non- protein coding")

        strand = tx['strand']
        if strand == '+':
            e_starts_g = tx['exon.starts']
            e_ends_g = tx['exon.ends']
        else:
            e_starts_g = tx['exon.ends']
            e_ends_g = tx['exon.starts']
    
        e_lengths = tx['exon.lengths']

        cds_start_tx = tx['tx.cds_start']
        cds_end_tx = tx['tx.cds_end']
        cds_start_c = 1
        cds_end_c = cds_end_tx - cds_start_tx + 1

        e_coords_g = []
        for i in xrange(0, len(e_starts_g)):
            e_coords_g.append(e_starts_g[i])
            e_coords_g.append(e_ends_g[i])
        if strand == '+':
            e_coords_g.append(sys.maxint)
        else:
            e_coords_g.append(0)

        e_coords_tx = []
        acc = 0
        for i in xrange(0, len(e_lengths)):
            e_coords_tx.append(acc)
            acc += e_lengths[i] - 1
            e_coords_tx.append(acc)
            acc += 1

        e_coords_c = []
        for i in xrange(0, len(e_coords_tx)):
            if e_coords_tx[i] < cds_start_tx:
                e_coords_c.append(e_coords_tx[i] - cds_start_tx)
            else:
                e_coords_c.append(e_coords_tx[i] - cds_start_tx + 1)
            #elif e_coords_tx[i] >= cds_start_tx and e_coords_tx[i] <= cds_end_tx:
            #    e_coords_c.append(e_coords_tx[i] - cds_start_tx + 1)
            #else:
            #    e_coords_c.append(e_coords_tx[i] - cds_end_tx)

        coords = []

        for Z in [start_g]:
            if strand == '+':
                for i in xrange(0, len(e_coords_g)):
                    if Z < e_coords_g[i]:
                        break
            else:
                for i in xrange(0, len(e_coords_g)):
                    if Z > e_coords_g[i]:
                        break

            #print "selected: ", i

            if i % 2 == 0:
                if i == 0:
                    # before 1st exon
                    base = e_coords_c[0]
                    offset = -abs(e_coords_g[0] - Z)
                    datum = hgvs.location.CDS_START
                elif i == len(e_coords_g) - 1:
                    # after last exon
                    base = e_coords_c[-1]
                    offset = abs(Z - e_coords_g[-2]) # because ..[-1] is either maxint or 0
                    if base > cds_end_c:
                        base -= cds_end_c
                        datum = hgvs.location.CDS_END # nucleotides are numbered as *1, *2, *3 ... from the last nucleotide of the translation stop codon
                    else:
                        datum = hgvs.location.CDS_START
                else:
                    # in intron
                    # what's the closest exon?
                    if abs(Z - e_coords_g[i-1]) <= abs(e_coords_g[i] - Z):
                        # previous exon
                        base = e_coords_c[i-1]
                        offset = abs(Z - e_coords_g[i-1])
                    else:
                        # following exon
                        base = e_coords_c[i]
                        offset = -abs(e_coords_g[i] - Z)
                    datum = hgvs.location.CDS_START
            else:
                # in exon
                off = abs(Z - e_coords_g[i-1])
                base = e_coords_c[i-1] + off + (1 if (e_coords_c[i-1] < 0 and off >= abs(e_coords_c[i-1])) else 0) # if we're crossing the start of the coding region, we need to add 1 because there is a gap (from -1 to +1)
                offset = 0
                if base > cds_end_c:
                    base -= cds_end_c
                    datum = hgvs.location.CDS_END # nucleotides are numbered as *1, *2, *3 ... from the last nucleotide of the translation stop codon
                else:
                    datum = hgvs.location.CDS_START
            
            coords.append((base, offset, datum))

        return {'cds_start_base': coords[0][0], 'cds_start_offset': coords[0][1], 'cds_start_datum': coords[0][2] }

    def _map_coord_tx_c_to_tx(self, base, datum, tx_cds_start, tx_cds_end):
        return base + (tx_cds_start if datum == hgvs.location.CDS_START else tx_cds_end) + (-1 if base > 0 and datum == hgvs.location.CDS_START else 0)

    def _getOrCreateRegion(self, chrom, start, end, gene_uuid):
        reg_uuid = self._graph_utils.getRegionByCoords(chrom=chrom, start=start, end=end, gene_uuid=gene_uuid)
        if len(reg_uuid) == 0:
            reg_uuid = self._graph_utils.createRegion(chrom=chrom, start=start, end=end, gene_uuid=gene_uuid)
        else:
            reg_uuid = reg_uuid[0]  # assume there is always only one region (there should be only one)
        return reg_uuid

    def _getOrCreateTranscriptRegion(self, tx_ac, start, end):
        reg_uuid = self._graph_utils.getTranscriptregionByCoords(tx_ac, start, end)
        if len(reg_uuid) == 0:
            reg_uuid = self._graph_utils.createTranscriptregion(tx_ac, start, end)
        else:
            reg_uuid = reg_uuid[0]
        return reg_uuid

class GraphAnnotation():
    # this class should take the following as parameters:
    #   sample_uuid     : the uuid of a node representing a sample
    #   ref_uuid        : the uuid of the node representing the reference for the annotation (e.g., sequence_alteration, copy_number_variation)
    #   db_id           : the ID of the annotationDB record describing the annotation
    def __init__(self):
        self._graph_utils = GenomeGraphUtility()
        self._sample_genid = None
        self._ref_uuid = None
        self._db_id = None
        self._in_graph = None
        self._uuid = None

    def set(self, sample_genid, ref_uuid, db_id):
        self._sample_genid = sample_genid
        self._ref_uuid = ref_uuid
        self._db_id = db_id
        self._in_graph = None
        self._uuid = None

    def getUuid(self):
        return self._uuid

    def exists(self):
        if self._in_graph is None:
            self._checkExists()
        return self._in_graph

    def _checkExists(self):
        if not self._checkValid():
            self._in_graph = None
            self._uuid = None
            return
        res = self._graph_utils.getAnnotation(src_genid=self._sample_genid,ref_uuid=self._ref_uuid)
        if res != None:
            self._uuid = res
            self._in_graph = True
        else:
            self._in_graph = False

    def _checkValid(self):
        return self._sample_genid is not None and self._ref_uuid is not None and self._db_id is not None

    def save(self):
        if not self._checkValid():
            return

        if self.exists() == True:
            print "Already in graph"
            return
        self._uuid = self._graph_utils.annotateNode(src_genid=self._sample_genid,ref_uuid=self._ref_uuid,data={'db_id': self._db_id})
        self._in_graph = True
        return

def setDefaultTranscriptForGeneAndUpdate(gene_uuid, tx_ac):
    g = GenomeGraphUtility()
    g.setDefaultTranscriptForGene(gene_uuid=gene_uuid, tx_ac=tx_ac)
    q = "match (g:kb_node {uuid: { gene_uuid }})-[r1:has_alteration]->(s:sequence_alteration) return s.uuid"
    query1 = neo4j.CypherQuery(g.gdb, q)
    res1 = query1.execute(gene_uuid=gene_uuid)
    res1 = [x for x in res1]
    res2 = SequenceAlteration.byUuid_list(res1)
    for s in res2:
        s.update()

def setCosmicTranscriptsAsDefault():
    g = GenomeGraphUtility()
    for cosmic_gene in annotations.models.CosmicGene.objects.all():
        if not cosmic_gene.transcript_name.upper().startswith('ENST'):
            continue
        graph_genes = g.getGenesByPrefix(cosmic_gene.symbol)
        graph_gene_uuid = None
        for gg in graph_genes:
            if gg[1] == cosmic_gene.symbol and gg[3] == cosmic_gene.chromosome:
                graph_gene_uuid = gg[0]
                break
        if not graph_gene_uuid:
            continue
        print "Gene: ", cosmic_gene.symbol
        try:
            setDefaultTranscriptForGeneAndUpdate(gene_uuid=graph_gene_uuid, tx_ac=cosmic_gene.transcript_name.upper())
        except Exception as e:
            print str(e)

def setAllMissingAltP():
    g = GenomeGraphUtility()
    q = "match (s:sequence_alteration) where not(has(s.alt_p)) return s.uuid"
    query1 = neo4j.CypherQuery(g.gdb, q)
    res1 = query1.execute()
    for u in res1:
        try:
            s = SequenceAlteration()
            s.byUuid(u[0])
            P = s._computeHGVS_p_1L()[2:]
            s._graph_utils.setSequenceAlterationProperties(s._uuid, alt_p=P)
        except Exception as e:
            print str(e)

def updateAllSequenceAlterations():
    g = GenomeGraphUtility()
    res1 = g.getAllSequenceAlterations()
    objs = SequenceAlteration.byUuid_list([x[0] for x in res1 if x[0]])
    for s in objs:
        s.update()

def updateAllSequenceAlterationRegions():
    g = GenomeGraphUtility()
    res1 = g.getAllSequenceAlterations()
    objs = SequenceAlteration.byUuid_list([x[0] for x in res1 if x[0]])
    for s in objs:
        s.updateRegion()

def updateAllSequenceAlterationXrefs():
    g = GenomeGraphUtility()
    res1 = g.getAllSequenceAlterations()
    objs = SequenceAlteration.byUuid_list([x[0] for x in res1 if x[0]])
    for s in objs:
        try:
            s._refreshXrefs()
            s.update()
        except Exception as e:
            print str(e)

