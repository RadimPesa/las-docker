import copy
import subprocess
import tempfile
import os

class SequenceAlignment(object):
    def __init__(self, strand, ref, start, end, alignerProfile):
        self.strand = strand
        self.reference = ref
        self.start = int(start)
        self.end = int(end)
        self.alignerProfile = alignerProfile

class SequenceAligner():
    def __init__ (self, paths=None, profiles=None):
        if paths is None:
            try:
                from django.conf import settings
                paths = settings.ALIGNER_PATHS
            except:
                raise Exception("Aligner paths not provided, failed to import defaults")

        if profiles is None:
            try:
                from django.conf import settings
                profiles = settings.ALIGNER_PROFILES
            except:
                raise Exception("Error: Aligner profiles not provided, failed to import defaults")

        self._paths = copy.deepcopy(paths)
        self._profiles = { p['name']: { k: v for k,v in p.items()} for p in profiles }
        self._align_methods = {'BLAT_CLIENT': self.blatClientAlign}

    def getProfiles(self):
        return self._profiles.keys()
    
    def align(self, sequence, profile_name, minIdentity=None, minScore=None):
        try:
            profile = self._profiles[profile_name]
        except:
            raise Exception("Unknown profile: {0}".format(profile_name))
        try:
            aligner = self._align_methods[profile['type']]
        except:
            raise Exception("Unknown aligner type: {0}".format(profile['type']))
        return aligner(sequence, profile, minIdentity, minScore)
        
    def blatClientAlign(self, sequence, profile, minIdentity=None, minScore=None):

        sequence = sequence.strip()
        name = 'seq0'

        DEVNULL = open(os.devnull, 'w')
        BLATCLIENT_BIN = self._paths[profile['type']]
        BLATSRV_HOST = profile['host']
        BLATSRV_PORT = profile['port']
        BLAT_SEQPATH = profile['seqDir']
        MIN_IDENTITY = 80 if minIdentity is None else minIdentity
        MIN_SCORE = len(sequence) if minScore is None else minScore
        
        with tempfile.NamedTemporaryFile() as in_f:
            in_f.delete = False
            in_f_name = in_f.name
            in_f.write(">" + name + "\n")
            in_f.write(sequence + "\n")

        with tempfile.NamedTemporaryFile() as out_f:
            out_f.delete = False
            out_f_name = out_f.name

        output = subprocess.check_output([BLATCLIENT_BIN, "-nohead", "-minScore={0}".format(MIN_SCORE), "-minIdentity={0}".format(MIN_IDENTITY), BLATSRV_HOST, BLATSRV_PORT, BLAT_SEQPATH, in_f_name, out_f_name], stderr=subprocess.STDOUT)

        with open(out_f_name, "r") as out_f:

            alignments = []
            for l in out_f:
                l = l.split()
                a = SequenceAlignment(strand=l[8], ref=l[13], start=l[15], end=l[16], alignerProfile=profile['name'])
                alignments.append(a)

        os.remove(in_f_name)
        os.remove(out_f_name)
        
        DEVNULL.close()

        return alignments
