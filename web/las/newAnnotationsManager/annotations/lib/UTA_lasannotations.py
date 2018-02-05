import hgvs.dataproviders.uta
from hgvs.utils.aminoacids import seq_md5
import urlparse

# alberto.grand Nov 2014
# interface with las annotations graph db

def connect(db_url=None,graph_utils_obj=None,seq_utils_obj=None):
    """
    Connect to a UTA database instance and return a UTA interface instance.

    When called with an explicit db_url argument, that db_url is used for connecting.

    When called without an explicit argument, the function default is
    determined by the environment variable UTA_DB_URL if it exists, or
    hgvs.datainterface.uta.public_db_url otherwise.

    The format of the db_url is driver://user:pass@host/database (the same
    as that used by SQLAlchemy).  Examples:

    A remote public postgresql database:
        postgresql://uta_public:uta_public@uta.invitae.com/uta'

    A local postgresql database:
        postgresql://localhost/uta
    
    A local SQLite database:
      sqlite:////tmp/uta-0.0.6.db

    N.B. The original UTA connect function is called unless the url scheme is 'lasnnotations'
    """

    if not db_url:
        return hgvs.dataproviders.uta.connect(db_url)

    url = urlparse.urlparse(db_url)
    
    if url.scheme == 'lasannotations':
        if graph_utils_obj != None and seq_utils_obj != None:
	    conn = UTA_lasannotations(graph_utils_obj, seq_utils_obj)
        else:
            raise RuntimeError("Url scheme '{0}' requires passing valid graph_utils and seq_utils objects".format(url.scheme))
    else:
        return hgvs.dataproviders.uta.connect(db_url)

    conn.db_url = db_url
    res = conn
    return res

class UTA_lasannotations(hgvs.dataproviders.uta.UTABase):
    def __init__(self,graph_utils_obj,seq_utils_obj):
        self.guo = graph_utils_obj
        self.suo = seq_utils_obj

    def _get_cursor(self):
        pass

    def get_tx_identity_info(self, tx_ac):
        r = self.guo.getTranscriptInfo(ac=tx_ac)[0]
        return {'tx_ac': tx_ac, 'alt_ac': tx_ac, 'alt_aln_method': 'transcript', 'cds_start_i': r['tx.cds_start'], 'cds_end_i': r['tx.cds_end'], 'lengths': r['exon.lengths'], 'hgnc': r['gene.symbol']}

    def get_tx_seq(self,tx_ac):
        return self.suo.getRefSequence(tx_ac)

    def get_acs_for_protein_seq(self, seq):
	md5 = seq_md5(seq)
        return ['unknown', md5]

