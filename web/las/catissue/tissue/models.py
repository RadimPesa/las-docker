from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from catissue.tissue import markup
from catissue.tissue.mw import threadlocals
from string import maketrans
import audit,pylibmc,datetime
from py2neo import neo4j, cypher, node, rel
from django_transaction_signals import defer
from django.db import transaction
from django.db.models.query import QuerySet
from django.conf import settings
from catissue.global_request_middleware import *
from django.db.models.query import QuerySet
from catissue.tissue.genealogyID import *
from django.core.mail import EmailMessage
from django.utils import timezone

'''
ADDED FOR GRAPH_DB MANAGEMENT
'''
class WG(models.Model):
    name= models.CharField(max_length=40)
    users = models.ManyToManyField(User, through="WG_User")
    owner= models.ForeignKey(User,related_name="owner_wg_set")
    def __unicode__(self):
        return str(self.name)
   
class WG_User(models.Model):
    WG=models.ForeignKey(WG)
    user=models.ForeignKey(User)
    permission=models.ForeignKey(Permission,blank=True, null=True)
    class Meta:
        unique_together = ("WG","user","permission")
        
class Aliquot_WG(models.Model):
    aliquot=models.ForeignKey('Aliquot',db_column='id_aliquot')
    WG=models.ForeignKey(WG,db_column='WG_id')
    class Meta:
        db_table = 'aliquot_wg'
    def __unicode__(self):
        return str(self.aliquot)+' -> '+str(self.WG)

'''class Aliquot_OldWG(models.Model):
    aliquot=models.ForeignKey('Aliquot',db_column='id_aliquot')
    WG=models.ForeignKey(WG,db_column='WG_id')
    class Meta:
        db_table = 'aliquot_old_wg'
    def __unicode__(self):
        return str(self.aliquot)+' -> '+ str(self.WG)'''

class WgObjectManager(models.Manager):
    def get_query_set(self):
        if settings.USE_GRAPH_DB==True and 'admin' not in get_WG():
            groups=get_WG()
            qs=Aliquot_WG.objects.filter(WG__name__in=list(groups)).values_list('aliquot__id')
            return super(WgObjectManager, self).get_query_set().filter(id__in=qs)
        else:
            print "old_man"
            return super(WgObjectManager, self).get_query_set()

    def all_old(self):
        return super(WgObjectManager, self).get_query_set()

    def get_old(self, *args, **kwargs):
        return super(WgObjectManager, self).get_query_set().get(*args, **kwargs)

    def filter_old(self, *args, **kwargs):
        return super(WgObjectManager, self).get_query_set().filter(*args, **kwargs)

    def count_old(self):
        return super(WgObjectManager, self).get_query_set().count()


class WgObjectRelatedManager(models.Manager):
    def get_query_set(self):
        if settings.USE_GRAPH_DB==True and 'admin' not in get_WG():
            groups=get_WG()
            qs=Aliquot_WG.objects.filter(WG__name__in=list(groups)).values_list('aliquot__id')
            return super(WgObjectRelatedManager, self).get_query_set().filter(idAliquot__in=qs)
        else:
            print "old_man"
            return super(WgObjectRelatedManager, self).get_query_set()

    def all_old(self):
        return super(WgObjectRelatedManager, self).get_query_set()

    def get_old(self, *args, **kwargs):
        return super(WgObjectRelatedManager, self).get_query_set().get(*args, **kwargs)

    def filter_old(self, *args, **kwargs):
        return super(WgObjectRelatedManager, self).get_query_set().filter(*args, **kwargs)

    def count_old(self):
        return super(WgObjectRelatedManager, self).get_query_set().count()

def setLabels(nodeType, altype):
    labels = []
    alTypes = {'VT':'Viable', 'SF':'SnapFrozen', 'RL':'RNALater', 'D':'DNA', 'FF':'FormalinFixed', 'PL': 'PlasmaIsolation', 'OF': 'OCTFrozen', 'SI': 'SerumIsolation', 'CH':'ChinaBlack', 'PX':'PAXtube', 'PS':'Paraffin section', 'OS':'OCT section', 'R':'RNA', 'D':'DNA', 'P':'Protein', 'cR':'cRNA', 'cD':'cDNA','FR':'Frozen','FS':'FrozenSediment', 'LS':'Labeled section'}
    if nodeType == 'Biomouse':
        labels = ['Bioentity', 'Biomouse']
    elif nodeType == 'Aliquot':
        labels = ['Bioentity', 'Aliquot', alTypes[altype]]
    elif nodeType == 'Genid':
        labels = ['Genid']
    elif nodeType == 'Collection':
        labels = ['Genid', 'Collection']
    return labels


def padGenid (genid):
    newgenid = genid + ''.join('0' for x in range(26 - len(genid)))
    return newgenid

def buildSemanticNode(label, nodeType, nextSemanticLevel, nodes, dateAl):
    gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
    genid = GenealogyID(label)
    if nodeType == 'Aliquot':
        if genid.getSampleVector() == 'H':
            newLabel = genid.getCase() + genid.getTissue() + genid.getSampleVector() + genid.getTissueType()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasInstance', 'app':None}
            nodes[newLabel]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',newLabel)
            if nodes[newLabel]['nodeid'] is not None:
                return
            buildSemanticNode(newLabel, 'Genid', 'Tissue', nodes, dateAl)
        elif genid.getSampleVector() == 'X':
            newLabel = genid.getCase() + genid.getTissue() + genid.getGeneration() + genid.getMouse() + genid.getTissueType()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasInstance', 'app':None}
            nodes[newLabel]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',newLabel)
            if nodes[newLabel]['nodeid'] is not None:
                return
            buildSemanticNode(newLabel, 'Genid', 'Sample', nodes, dateAl)
        elif genid.getSampleVector() in ['A','S', 'O']:
            newLabel = genid.getCase() + genid.getTissue() + genid.getGeneration() + genid.getMouse()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasInstance', 'app':None}
            nodes[newLabel]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',newLabel)
            if nodes[newLabel]['nodeid'] is not None:
                return
            buildSemanticNode(newLabel, 'Genid', 'SamplePassage', nodes, dateAl)
    elif nodeType == 'Biomouse':
        newLabel = genid.getCase() + genid.getTissue() + genid.getGeneration() + genid.getMouse()
        newLabel = padGenid(newLabel)
        if not nodes.has_key(newLabel):
            nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
        nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasInstance', 'app':None}
        nodes[newLabel]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',newLabel)
        if nodes[newLabel]['nodeid'] is not None:
            return
        buildSemanticNode(newLabel, 'Genid', 'SamplePassage', nodes, dateAl)
    elif nodeType == 'Genid':
        if nextSemanticLevel == 'Sample':
            newLabel = genid.getCase() + genid.getTissue() + genid.getGeneration() + genid.getMouse()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasSuffix', 'app':None}
            nodes[newLabel]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',newLabel)
            if nodes[newLabel]['nodeid'] is not None:
                return
            buildSemanticNode(newLabel, 'Genid', 'SamplePassage', nodes, dateAl)
        if nextSemanticLevel == 'SamplePassage':
            newLabel = genid.getCase() + genid.getTissue() + genid.getGeneration()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasSuffix', 'app':None}
            nodes[newLabel]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',newLabel)
            if nodes[newLabel]['nodeid'] is not None:
                return
            buildSemanticNode(newLabel, 'Genid', 'Lineage', nodes, dateAl)
        if nextSemanticLevel == 'Lineage':
            newLabel = genid.getCase() + genid.getTissue() + genid.getSampleVector() + genid.getLineage()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasSuffix', 'app':None}
            nodes[newLabel]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',newLabel)
            if nodes[newLabel]['nodeid'] is not None:
                return
            buildSemanticNode(newLabel, 'Genid', 'SampleVector', nodes, dateAl)
        if nextSemanticLevel == 'SampleVector':
            newLabel = genid.getCase() + genid.getTissue() + genid.getSampleVector()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasSuffix', 'app':None}
            nodes[newLabel]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',newLabel)
            if nodes[newLabel]['nodeid'] is not None:
                return
            buildSemanticNode(newLabel, 'Genid', 'Tissue', nodes, dateAl)
        if nextSemanticLevel == 'Tissue':
            newLabel = genid.getCase() + genid.getTissue()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasSuffix', 'app':None}
            nodes[newLabel]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',newLabel)
            if nodes[newLabel]['nodeid'] is not None:
                return
            buildSemanticNode(newLabel, 'Genid', 'Case', nodes, dateAl)
        if nextSemanticLevel == 'Case':
            newLabel = genid.getCase()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Collection', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None, 'date': dateAl}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasSuffix', 'app':None}
            nodes[newLabel]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',newLabel)
            if nodes[newLabel]['nodeid'] is not None:
                return
            buildSemanticNode(newLabel, 'Genid', 'Origin', nodes, dateAl)
        if nextSemanticLevel == 'Origin': 
            newLabel = genid.getOrigin()
            newLabel = padGenid(newLabel)
            if not nodes.has_key(newLabel):
                nodes[newLabel] = {'type':'Genid', 'altype': None, 'id':'Root',  'relationships':{}, 'nodeid': None}
            nodes[genid.getGenID()]['relationships'][newLabel] = {'type':'hasSuffix', 'app':None}
            nodes[newLabel]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',newLabel)
            if nodes[newLabel]['nodeid'] is not None:
                return
            return
        return    

@transaction.commit_on_success
def add_aliquot_node(aliquot):
    try:
        gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
        if gdb.get_indexed_node('node_auto_index','identifier',aliquot.uniqueGenealogyID):
            return
        from manageGraph import find_parent
        father_gen_id, app =find_parent(aliquot.uniqueGenealogyID)
        print "si"
        nodes = {}
        g = GenealogyID(aliquot.uniqueGenealogyID)
        altype = 'c'+g.get2Derivation() if g.is2Derivation() else g.getArchivedMaterial()
        #dateAl = datetime.datetime.now()
        dateAl=timezone.localtime(timezone.now())
        nodes[g.getGenID()] = {'type':'Aliquot', 'altype': altype, 'id':aliquot.id, 'relationships':{}, 'nodeid': None, 'date':str(dateAl)}
        #print nodes[g.getGenID()]
        fatherNode = None
        print father_gen_id,app
        if father_gen_id:
            nodes[father_gen_id] = {'type':'Aliquot', 'nodeid': None, 'wg':{}, 'relationships':{}, 'id':None}
            nodes[father_gen_id]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',father_gen_id)
            query="START n=node:node_auto_index(identifier='"+father_gen_id+"') match (w:WG)-[r]->n WHERE not has(r.endDate) RETURN id(r), type(r), w.identifier, id(w)"
            print query
            data, metadata = cypher.execute(gdb, query)
            if len(data)>0:
                for d in data:
                    nodes[father_gen_id]['wg'][d[0]] = {'nodeid':  gdb.get_indexed_node('node_auto_index','identifier',d[2]), 'rel_type': d[1], 'name':d[2]}

            #relsWg = list(graph_db.match(end_node=nodes[father_gen_id]['nodeid']), rel_type="OwnsData") # e i paramteri associati? e i nodi attaccati?
            fatherNode = nodes[father_gen_id]
            nodes[g.getGenID()]['relationships'][father_gen_id] = {'type': 'generates', 'app':app}
        else:
            collection_genid = g.getCase()
            collection_genid = padGenid(collection_genid)
            nodes[collection_genid] =  {'type':'Collection', 'altype': None, 'id':None,  'relationships':{}, 'nodeid': None, 'date': str(dateAl), 'wg':{}}
            #la prima volta che entra qui nodeid rimane None perche' non trova il nodo della collezione. Per le aliq successive lo trovera'
            nodes[collection_genid]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',collection_genid)
            nodes[g.getGenID()]['relationships'][collection_genid] = {'type': 'generates', 'app':'collection'}
            fatherNode = nodes[collection_genid]
            groups=get_initWG()
            groups_list=list(groups)
            print 'len',len(groups_list)
            if len(groups_list)>0:
                print 'groups_list', groups_list
                wg_node=gdb.get_indexed_node('node_auto_index','identifier',groups_list.pop(0))
            else:
                wg_node=gdb.get_indexed_node('node_auto_index','identifier','admin')
            print 'wg_node',wg_node
            fatherNode['wg'][1] = {'nodeid': wg_node, 'rel_type': 'OwnsData', 'name':wg_node['identifier']}
            #data la lista dei gruppi, il primo avra' una relazione OwnsData che ho gia' impostato prima.
            #Gli altri della lista avranno una relazione SharesData. Parto da 0 perche' con il .pop() di prima
            #ho gia' tolto il wg proprietario
            for i in range(0,len(groups_list)):
                other_wg_node=gdb.get_indexed_node('node_auto_index','identifier',groups_list[i])
                fatherNode['wg'][i+2] = {'nodeid': other_wg_node, 'rel_type': 'SharesData', 'name':other_wg_node['identifier']}
            '''#recupero il valore del consenso che ho impostato prima nelle utils nella funzione saveInClinicalModule
            #diz con chiave tumore+caso e valore il uid del nodo del consenso
            try:
                dizconsenso=get_ICCodeCollection()
                print 'dizconsenso',dizconsenso
                consenso=dizconsenso[g.getCase()]
            except:
                consenso=''
            #devo vedere se la relazione tra collezione e consenso c'e' gia' e se si' non devo fare niente
            q=neo4j.CypherQuery(gdb,"START n=node:node_auto_index(identifier='"+collection_genid+"'), cons=node:node_auto_index(identifier='"+consenso+"') MATCH n-[r]-cons return r")
            print 'query',q
            r=q.execute()
            print 'r.data',r.data
            if len(r.data)==0:
                nodocons=gdb.get_indexed_node('node_auto_index','identifier',consenso)
                print 'nodocons',nodocons
                #dovrebbe sempre esistere questo nodo perche' e' stato creato dal modulo clinico
                if nodocons:
                    nodes[consenso] =  {'nodeid': nodocons,'relationships':{}}
                    #cosi' ho una relazione che va da consenso a collezione
                    #nodes[collection_genid]['relationships'][consenso] = {'type': 'prova', 'app':None}
                    #cosi' ho una relazione che va da collezione a consenso
                    nodes[consenso]['relationships'][collection_genid] = {'type': 'prova', 'app':None}'''
                
        print 'fatherNode',fatherNode
        #questa funzione mi aggiunge altre chiavi a nodes, che rappresentano i nodi da creare, ad esempio i nodi con relazione hassuffix
        #tra di loro 
        buildSemanticNode(g.getGenID(), 'Aliquot', None, nodes, dateAl)

        batch = neo4j.WriteBatch(gdb)
        batch.clear()
        print '---------------------------------------------'
        print 'nodes',nodes

        for n, nInfo in nodes.items():
            print 'before ', n, nInfo
            if nInfo['nodeid'] is None:
                nInfo['nodeid'] = batch.create(node(identifier=n))
                labels = setLabels(nInfo['type'], nInfo['altype'])
                #print labels
                batch.add_labels(nInfo['nodeid'], *labels)
                if nInfo['type'] in ['Biomouse', 'Aliquot', 'Collection']:
                    for wg, wgInfo in fatherNode['wg'].items():
                        print 'create rel with wg', wg, wgInfo, nInfo
                        batch.create( rel( wgInfo['nodeid'], wgInfo['rel_type'], nInfo['nodeid'], {'startDate': nInfo['date'], 'endDate':None} ) )
            print 'after ', n, nInfo

        for dest, destInfo in nodes.items():
            for source, relInfo in destInfo['relationships'].items():
                print dest, destInfo, source, relInfo
                if relInfo['app']:
                    batch.create( rel( nodes[source]['nodeid'], relInfo['type'], destInfo['nodeid'], {'app': relInfo['app']} ) )
                else:
                    batch.create( rel( nodes[source]['nodeid'], relInfo['type'], destInfo['nodeid'] ) )
        print 'before batch submit'
        results = batch.submit()
        print 'batch submit'
        batch.clear()
        print 'batch clear'

        for wg, wgInfo in fatherNode['wg'].items():
            print 'wg', wg
            print 'wginfo',wgInfo
            if Aliquot_WG.objects.filter(aliquot=aliquot,WG=WG.objects.get(name=wgInfo['name'])).count()==0:
                m2m=Aliquot_WG(aliquot=aliquot,WG=WG.objects.get(name=wgInfo['name']))
                m2m.save()
        print '---------------------------------------------'

    except Exception,e:
        print 'errore grafo',e
        transaction.rollback()
        #if Aliquot_WG.objects.filter(aliquot=aliquot,WG=WG.objects.get(name='Bertotti_WG')).count()==0:
        #    m2m=Aliquot_WG(aliquot=aliquot,WG=WG.objects.get(name='Bertotti_WG'))
        #    m2m.save()
        subject='ERROR DURING SAVING ALIQUOT IN GRAPH DB'
        message='Error saving genid:',str(aliquot.uniqueGenealogyID)
        toList=list()
        #toList.append('domenico.schioppa@gmail.com')
        email = EmailMessage(subject,message,'',toList,[],'','','',[])
        #email.send(fail_silently=False)
    
    return

'''
END GRAPH DB
'''

def getUsername(instance):
    return threadlocals.get_current_user()
    #return 'emanuele.geda'

class Aliquot(models.Model):
    objects=WgObjectManager()
    #id=models.IntegerField(primary_key=True, editable=False)
    barcodeID=models.CharField('barcode ID',max_length=45,blank=True)
    uniqueGenealogyID=models.CharField('Unique Genealogy ID',max_length=30, unique=True)
    idSamplingEvent=models.ForeignKey('SamplingEvent', db_column='idSamplingEvent',verbose_name='Sampling Event')
    idAliquotType=models.ForeignKey('AliquotType', db_column='idAliquotType',verbose_name='Aliquot Type')
    timesUsed=models.IntegerField('Times Used')
    availability=models.BooleanField()
    derived=models.BooleanField()    
    archiveDate=models.DateField('Archive Date',blank=True)
        
    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername),))
    
    class Meta:
        verbose_name_plural='Aliquots'
        db_table='aliquot'
    def __unicode__(self):
        return self.uniqueGenealogyID
    
    def save(self, *args, **kwargs):
        from django_transaction_signals import defer
        print "salvo",get_WG()
        if settings.USE_GRAPH_DB == True and 'admin' not in get_WG():
            print "si graph"
            if self.pk is not None:
                print "non differisco"
                print self
                print self.uniqueGenealogyID
            elif self.uniqueGenealogyID is not None :
                print "differire"
                defer(add_aliquot_node,self)
                print "differire 2"
        super(Aliquot, self).save(*args, **kwargs)

    def save_old(self, *args, **kwargs):
        super(Aliquot, self).save(*args, **kwargs)

class AliquotDerivationSchedule(models.Model):
    objects=WgObjectRelatedManager()
    idAliquot=models.ForeignKey(Aliquot, db_column='idAliquot',verbose_name='Aliquot')
    idDerivationSchedule=models.ForeignKey('DerivationSchedule', db_column='idDerivationSchedule',verbose_name='Derivation Schedule')
    idDerivedAliquotType=models.ForeignKey('AliquotType', db_column='idDerivedAliquotType',verbose_name='Derived Aliquot Type')
    idDerivationProtocol=models.ForeignKey('DerivationProtocol', db_column='idDerivationProtocol',verbose_name='Derivation Protocol',blank=True,null=True)
    idKit=models.ForeignKey('Kit', db_column='idKit',verbose_name='Kit',blank=True,null=True)
    derivationExecuted=models.BooleanField()
    operator=models.CharField(max_length=45,blank=True,null=True)
    failed=models.BooleanField(blank=True)
    loadQuantity=models.FloatField('Load Quantity',blank=True,null=True)
    volumeOutcome=models.FloatField('Volume Outcome',blank=True)
    initialDate=models.DateField('Initial Date',blank=True)
    measurementExecuted=models.BooleanField('Measurement Executed',blank=True)
    aliquotExhausted=models.BooleanField(blank=True)
    deleteTimestamp=models.DateTimeField('Delete Timestamp',blank=True,null=True)
    deleteOperator=models.ForeignKey(User, db_column='deleteOperator',related_name='id_deleteOperatorder',verbose_name='Delete Operator',blank=True,null=True)
    validationTimestamp=models.DateTimeField('Validation Timestamp',blank=True,null=True)
    notes=models.CharField(max_length=150,blank=True)
    idPlanRobot=models.IntegerField(blank=True,null=True)
    idPlanDilution=models.IntegerField(blank=True,null=True)
    
    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername),))
    
    class Meta:
        verbose_name_plural='Aliquot DerivationSchedules'
        db_table='aliquotderivationschedule'
        #unique_together=("idAliquot","idDerivationSchedule","idDerivedAliquotType")
    def __unicode__(self):
        return str(self.idAliquot)+' '+str(self.idDerivationSchedule)

class AliquotExperiment(models.Model):
    objects=WgObjectRelatedManager()
    idAliquot=models.ForeignKey(Aliquot, db_column='idAliquot',verbose_name='Aliquot')
    idExperiment=models.ForeignKey('Experiment', db_column='idExperiment',verbose_name='Experiment')
    idExperimentSchedule=models.ForeignKey('ExperimentSchedule', db_column='idExperimentSchedule',verbose_name='Experiment Schedule',null=True,blank=True)
    takenValue=models.FloatField('Taken Value')
    remainingValue=models.FloatField('remaining Value')
    operator=models.CharField(max_length=45,null=True,blank=True)
    experimentDate=models.DateField('Experiment Date')
    aliquotExhausted=models.BooleanField(blank=True)
    confirmed=models.BooleanField()
    fileInserted=models.BooleanField(default=False)
    notes=models.CharField(max_length=150,blank=True)
    deleteTimestamp=models.DateTimeField('Delete Timestamp',blank=True,null=True)
    deleteOperator=models.ForeignKey(User, db_column='deleteOperator',related_name='id_deleteOperatorexp',verbose_name='Delete Operator',blank=True,null=True)
    validationTimestamp=models.DateTimeField('Validation Timestamp',blank=True,null=True)
    class Meta:
        verbose_name_plural='Aliquot Experiments'
        db_table='aliquotexperiment'
    def __unicode__(self):
        return str(self.idAliquot)+' '+str(self.idExperiment)+' '+str(self.experimentDate)

class AliquotFeature(models.Model):
    objects=WgObjectRelatedManager()
    idAliquot=models.ForeignKey(Aliquot, db_column='idAliquot',verbose_name='Aliquot')
    idFeature=models.ForeignKey('Feature', db_column='idFeature',verbose_name='Feature')
    value=models.FloatField('Value')
    class Meta:
        verbose_name_plural='Aliquot Features'
        db_table='aliquotfeature'
        unique_together=("idAliquot","idFeature")
    def __unicode__(self):
        return str(self.idAliquot)+' '+str(self.idFeature)

class AliquotLabelSchedule(models.Model):
    objects=WgObjectRelatedManager()
    idAliquot=models.ForeignKey(Aliquot, db_column='idAliquot',verbose_name='Aliquot')
    idLabelSchedule=models.ForeignKey('LabelSchedule', db_column='idLabelSchedule',verbose_name='Label Schedule')
    idLabelConfiguration=models.ForeignKey('LabelConfiguration', db_column='idLabelConfiguration',verbose_name='Label Configuration',blank=True,null=True)
    idSamplingEvent=models.ForeignKey('SamplingEvent', db_column='idSamplingEvent',verbose_name='Sampling Event',blank=True,null=True)
    operator=models.ForeignKey(User, db_column='operator',verbose_name='Operator',blank=True,null=True)
    executionDate=models.DateField('Execution Date',blank=True)
    executed=models.BooleanField()
    fileInsertionDate=models.DateField('File Insertion Date',blank=True)
    fileInserted=models.BooleanField(default=False)
    notes=models.CharField(max_length=150,blank=True)
    validationTimestamp=models.DateTimeField('Validation Timestamp',blank=True,null=True)
    deleteTimestamp=models.DateTimeField('Delete Timestamp',blank=True,null=True)
    deleteOperator=models.ForeignKey(User, db_column='deleteOperator',related_name='id_deleteOperatorlabel',verbose_name='Delete Operator',blank=True,null=True)
    class Meta:
        verbose_name_plural='Aliquot LabelSchedules'
        db_table='aliquotlabelschedule'
    def __unicode__(self):
        return str(self.idAliquot)+' '+str(self.idLabelSchedule)

class AliquotPositionSchedule(models.Model):
    objects=WgObjectRelatedManager()
    idAliquot=models.ForeignKey(Aliquot, db_column='idAliquot',verbose_name='Aliquot')
    idPositionSchedule=models.ForeignKey('PositionSchedule', db_column='idPositionSchedule',verbose_name='Position Schedule')
    positionExecuted=models.BooleanField()
    notes=models.CharField(max_length=150,blank=True)
    deleteTimestamp=models.DateTimeField('Delete Timestamp',blank=True,null=True)
    deleteOperator=models.ForeignKey(User, db_column='deleteOperator',related_name='id_deleteOperatorpos',verbose_name='Delete Operator',blank=True,null=True)
    class Meta:
        verbose_name_plural='Aliquot PositionSchedules'
        db_table='aliquotpositionschedule'
        unique_together=("idAliquot","idPositionSchedule")
    def __unicode__(self):
        return str(self.idAliquot)+' '+str(self.idPositionSchedule)
    
class AliquotQualitySchedule(models.Model):
    objects=WgObjectRelatedManager()
    idAliquot=models.ForeignKey(Aliquot, db_column='idAliquot',verbose_name='Aliquot')
    idQualitySchedule=models.ForeignKey('QualitySchedule', db_column='idQualitySchedule',verbose_name='Quality Schedule')
    revaluationExecuted=models.BooleanField()
    validationTimestamp=models.DateTimeField('Validation Timestamp',blank=True,null=True)
    operator=models.ForeignKey(User, db_column='operator',related_name='id_operator_quality',verbose_name='Operator',blank=True,null=True)
    idPlanRobot=models.IntegerField(blank=True,null=True)
    deleteTimestamp=models.DateTimeField('Delete Timestamp',blank=True,null=True)
    deleteOperator=models.ForeignKey(User, db_column='deleteOperator',related_name='id_deleteOperatorqual',verbose_name='Delete Operator',blank=True,null=True)
    class Meta:
        verbose_name_plural='Aliquot QualitySchedules'
        db_table='aliquotqualityschedule'
        unique_together=("idAliquot","idQualitySchedule")
    def __unicode__(self):
        return str(self.idAliquot)+' '+str(self.idQualitySchedule)

class AliquotSlideSchedule(models.Model):
    objects=WgObjectRelatedManager()
    idAliquot=models.ForeignKey(Aliquot, db_column='idAliquot',verbose_name='Aliquot')
    idSlideSchedule=models.ForeignKey('SlideSchedule', db_column='idSlideSchedule',verbose_name='Slide Schedule')
    idSamplingEvent=models.ForeignKey('SamplingEvent', db_column='idSamplingEvent',verbose_name='Sampling Event',blank=True, null=True)
    idSlideProtocol=models.ForeignKey('SlideProtocol', db_column='idSlideProtocol',verbose_name='Slide Protocol',blank=True, null=True)
    operator=models.ForeignKey(User, db_column='operator',verbose_name='Operator',blank=True,null=True)
    aliquotExhausted=models.BooleanField(blank=True)
    executionDate=models.DateField('Execution Date',blank=True)
    executed=models.BooleanField()
    notes=models.CharField(max_length=150,blank=True)
    deleteTimestamp=models.DateTimeField('Delete Timestamp',blank=True,null=True)
    deleteOperator=models.ForeignKey(User, db_column='deleteOperator',related_name='id_deleteOperatorslide',verbose_name='Delete Operator',blank=True,null=True)
    class Meta:
        verbose_name_plural='Aliquot SlideSchedules'
        db_table='aliquotslideschedule'
    def __unicode__(self):
        return str(self.idAliquot)+' '+str(self.idSlideSchedule)

class AliquotSplitSchedule(models.Model):
    objects=WgObjectRelatedManager()
    idAliquot=models.ForeignKey(Aliquot, db_column='idAliquot',verbose_name='Aliquot')
    idSplitSchedule=models.ForeignKey('SplitSchedule', db_column='idSplitSchedule',verbose_name='Split Schedule')
    idSamplingEvent=models.ForeignKey('SamplingEvent', db_column='idSamplingEvent',verbose_name='Sampling Event',blank=True, null=True)
    splitExecuted=models.BooleanField()
    aliquotExhausted=models.BooleanField(blank=True)
    validationTimestamp=models.DateTimeField('Validation Timestamp',blank=True,null=True)
    operator=models.ForeignKey(User, db_column='operator',related_name='id_operator_split',verbose_name='Operator',blank=True,null=True)
    idPlanRobot=models.IntegerField(blank=True,null=True)
    deleteTimestamp=models.DateTimeField('Delete Timestamp',blank=True,null=True)
    deleteOperator=models.ForeignKey(User, db_column='deleteOperator',related_name='id_deleteOperatorsplit',verbose_name='Delete Operator',blank=True,null=True)
    class Meta:
        verbose_name_plural='Aliquot SplitSchedules'
        db_table='aliquotsplitschedule'
        unique_together=("idAliquot","idSplitSchedule")
    def __unicode__(self):
        return str(self.idAliquot)+' '+str(self.idSplitSchedule)

class AliquotTransferSchedule(models.Model):
    objects=WgObjectRelatedManager()
    idAliquot=models.ForeignKey(Aliquot, db_column='idAliquot',verbose_name='Aliquot')
    idTransfer=models.ForeignKey('Transfer', db_column='idTransfer',verbose_name='Transfer')
    class Meta:
        verbose_name_plural='Aliquot TransferSchedules'
        db_table='aliquottransferschedule'
    def __unicode__(self):
        return str(self.idAliquot)+' '+str(self.idTransfer)
    
class AliquotType(models.Model):
    id=models.IntegerField(primary_key=True, editable=False)
    abbreviation=models.CharField(max_length=4)
    longName=models.CharField(max_length=20)
    type=models.CharField(max_length=20)
    class Meta:
        verbose_name_plural='Aliquot Types'
        db_table='aliquottype'
    def __unicode__(self):
        return self.longName
    
class AliquotTypeExperiment(models.Model):
    idExperiment=models.ForeignKey('Experiment', db_column='idExperiment',verbose_name='Experiment')
    idAliquotType=models.ForeignKey(AliquotType, db_column='idAliquotType',verbose_name='Aliquot Type')
    class Meta:
        verbose_name_plural='Aliquot Type Experiments'
        db_table='aliquottypeexperiment'
    def __unicode__(self):
        return str(self.idExperiment)+' > '+str(self.idAliquotType)
    
class AliquotVector(models.Model):
    id=models.IntegerField(primary_key=True, editable=False)
    name=models.CharField(max_length=20)
    abbreviation=models.CharField(max_length=5)
    class Meta:
        verbose_name_plural='Aliquot Vectors'
        db_table='aliquotvector'
    def __unicode__(self):
        return self.name

class BlockBioentity(models.Model):
    idBlockProcedure=models.ForeignKey('BlockProcedure', db_column='idBlockProcedure', verbose_name='Block procedure')
    genealogyID=models.CharField(max_length=30)
    class Meta:
        verbose_name_plural='Block bioentities'
        db_table='blockbioentity'
    def __unicode__(self):
        return self.genealogyID

class BlockProcedure(models.Model):
    workGroup=models.CharField(max_length=30)
    genealogyID=models.CharField(max_length=30)
    extendToChildren=models.BooleanField('Extend to children')    
    operator=models.ForeignKey(User, db_column='operator')
    executionTime=models.DateTimeField('Execution time')
    blockProcedureBatch = models.ForeignKey('BlockProcedureBatch', db_column='blockProcedureBatch_id')
    class Meta:
        verbose_name_plural='Block procedures'
        db_table='blockprocedure'
    def __unicode__(self):
        return self.genealogyID+' to '+self.workGroup

class BlockProcedureBatch(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    operator = models.ForeignKey(User, db_column='operator',default=lambda: User.objects.get(username=getUsername(0)))
    workGroup = models.ForeignKey(WG, db_column='wg_id',null=True,blank=True)
    delete = models.BooleanField(default=False, db_column='isDelete')

    class Meta:
        verbose_name_plural = 'Block procedure batches'
        db_table = 'blockprocedurebatch'
    def __unicode__(self):
        return self.operator.username + " on " + str(self.timestamp) + " : " + ("delete" if self.delete else self.workGroup.name)
    
class ClinicalFeature(models.Model):
    name=models.CharField(max_length=50)
    measureUnit=models.CharField(max_length=20, blank=True)
    type=models.CharField(max_length=30, blank=True)
    idClinicalFeature = models.ForeignKey('self', db_column='idClinicalFeature',verbose_name='Father feature', null = True,blank=True) 
    class Meta:
        verbose_name_plural='Clinical Features'
        db_table='clinicalfeature'
    def __unicode__(self):
        return self.name+' '+str(self.measureUnit)

class ClinicalFeatureCollectionType(models.Model):
    idClinicalFeature=models.ForeignKey(ClinicalFeature, db_column='idClinicalFeature',verbose_name='Clinical Feature')
    idCollectionType=models.ForeignKey('CollectionType', db_column='idCollectionType',verbose_name='Collection Type',blank=True, null=True)
    value=models.CharField(max_length=150)
    class Meta:
        verbose_name_plural='ClinicalFeature CollectionType'
        db_table='clinicalfeaturecollectiontype'
    def __unicode__(self):
        return str(self.idClinicalFeature)+' '+str(self.value)
    
#per mappare da numeri a lettere maiuscole
partenza = "123456789"
destinazione = "ABCDEFGHI"
trasftab = maketrans(partenza, destinazione)
    
class Collection(models.Model):
    itemCode=models.CharField('Item Code',max_length=10)
    idCollectionType=models.ForeignKey('CollectionType',db_column='idCollectionType',verbose_name='Collection Type')
    idSource=models.ForeignKey('Source', db_column='idSource',verbose_name='Source')
    collectionEvent=models.CharField('Collection Event',max_length=45)
    patientCode=models.CharField('Patient Code',max_length=50,blank=True)
    idCollectionProtocol=models.ForeignKey('CollectionProtocol',db_column='idCollectionProtocol',verbose_name='Collection Protocol',blank=True,null=True)
    class Meta:
        verbose_name_plural='Collections'
        db_table='collection'
        unique_together=("itemCode","idCollectionType")
    def __unicode__(self):
        return str(self.idCollectionType.abbreviation)+' '+str(self.itemCode)
    def toString(self):
        return str(self.idCollectionType.abbreviation)+str(self.itemCode)    
    
    def table_vital(self):
        page=markup.page()
        page.table(id='vital',align='center')
        page.th(colspan=7)
        page.add('VIABLE')
        page.th.close()
        page.tr()
        page.td()
        page.td.close()
        for i in range(1,7):
            page.td(align='center')
            page.strong(i)
            page.td.close()
        page.tr.close()
        for i in range (1,5):
            page.tr()
            page.td()
            page.br()
            page.strong(str(i).translate(trasftab))
            page.td.close()
            for j in range(1,7):
                page.td()
                page.button(type='submit', id='v-'+str(i).translate(trasftab)+str(j))
                #page.add(str(0))
                page.button.close()
                page.td.close()
            page.tr.close()
        page.table.close()
        return page
    def table_rna(self):
        page=markup.page()
        page.table(id='rna')
        page.th(colspan=13)
        page.add('RNA LATER')
        page.th.close()
        page.tr()
        page.td()
        page.td.close()
        for i in range(1,13):
            page.td(align='center')
            page.strong(i)
            page.td.close()
        page.tr.close()
        for i in range (1,9):
            page.tr()
            page.td()
            page.br()
            page.strong(str(i).translate(trasftab))
            page.td.close()
            for j in range(1,13):
                page.td()
                page.button(type='submit', id='r-'+str(i).translate(trasftab)+str(j))
                #page.add(str(0))
                page.button.close()
                page.td.close()
            page.tr.close()
        page.table.close()
        return page
    def table_ffpe(self):
        page=markup.page()
        page.table(align='center',id='ffpe')
        page.th(colspan=6)
        page.add('FFPE')
        page.th.close()
        
        for i in range (1,5):
            page.tr()
            page.td()
            page.br()
            page.strong(i)
            page.td.close()
            page.td()
            page.button(type='submit', id='f-'+str(i))
            page.button.close()
            page.td.close()
            page.td()
            page.label('Barcode:')
            page.label.close()
            page.input(type='text', id='inputf'+str(i),maxlength=45,size=15)
            page.td()
            page.br()
            page.strong(i+4)
            page.td.close()
            page.td()
            page.button(type='submit', id='f-'+str(i+4))
            page.button.close()
            page.td.close()
            page.td()
            page.label('Barcode:')
            page.label.close()
            page.input(type='text', id='inputf'+str(i+4),maxlength=45,size=15)
            page.tr.close()
        page.table.close()
        return page
    def table_sf(self):
        page=markup.page()
        page.table(id='sf')
        page.th(colspan=13)
        page.add('SNAP FROZEN')
        page.th.close()
        page.tr()
        page.td()
        page.td.close()
        for i in range(1,13):
            page.td(align='center')
            page.strong(i)
            page.td.close()
        page.tr.close()
        for i in range (1,9):
            page.tr()
            page.td()
            page.br()
            page.strong(str(i).translate(trasftab))
            page.td.close()
            for j in range(1,13):
                page.td()
                page.button(type='submit', id='s-'+str(i).translate(trasftab)+str(j))
                #page.add(str(0))
                page.button.close()
                page.td.close()
            page.tr.close()
        page.table.close()
        return page
    
    def table_tubes(self):
        page = markup.page()
        page.table(align='center',id='tubes')

        page.th()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td("Last inserted aliquot: ")
        page.td.close()
        
        page.tr()
        page.td()
        page.strong('FFPE: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='f-0')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='inputf0',maxlength=45, size=8)
        page.td.close()
        page.td()
        page.p("-", id = 'f-output', align='center' )
        page.td.close()
        page.tr.close()
        
        page.tr()
        page.td()
        page.strong('OCT: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='o-0')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='inputo0',maxlength=45, size='8')
        page.td.close()
        page.td()
        page.p("-", id = 'o-output', align='center' )
        page.td.close()
        page.tr.close()

        page.tr()
        page.td()
        page.strong('CB: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='c-0')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='inputc0',maxlength=45, size='8')
        page.td.close()
        page.td()
        page.p("-", id = 'c-output', align='center' )
        page.td.close()
        page.tr.close()

        page.table.close()
        return page
    def table_blood(self):
        page = markup.page()
        page.table(align='center',id='tab_blood')

        page.tr()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td("Last inserted aliquot: ",style='padding-bottom:1.5em;')
        page.td.close()
        page.tr.close()
        
        page.tr()
        page.td()
        page.strong('Plasma: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='plas')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcplas',maxlength=45, size=8)
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_PL', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_PL', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='volplas',maxlength=10, size=6)
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.p("-", id = 'plasoutput', align='center' )
        page.td.close()
        page.tr.close()
        
        page.tr()
        page.td()
        page.strong('Whole blood: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='who')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcwho',maxlength=45, size='8')
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_SF', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_SF', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='volwho',maxlength=10, size=6)
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.p("-", id = 'whooutput', align='center' )
        page.td.close()
        page.tr.close()

        page.tr()
        page.td()
        page.strong('PAX tube: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='pax')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcpax',maxlength=45, size='8')
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_PX', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_PX', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='volpax',maxlength=10, size=6)
        page.td.close()
        page.td()       
        page.td.close()
        page.td()
        page.p("-", id = 'paxoutput', align='center' )
        page.td.close()
        page.tr.close()
        
        page.tr()
        page.td()
        page.strong('PBMC: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='pbmc')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcpbmc',maxlength=45, size='8')
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_VT', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_VT', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='volpbmc',maxlength=10, size=6)
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Count(cell/ml):')
        page.label.close()
        page.input(type='text', id='contapbmc',maxlength=10, size=6)
        page.td.close()
        page.td()
        page.p("-", id = 'pbmcoutput', align='center' )
        page.td.close()
        page.tr.close()

        page.table.close()
        return page
    
    def table_urine(self):
        page = markup.page()
        page.table(align='center',id='tab_uri')

        page.tr()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.td.close()
        page.td("Last inserted aliquot: ",style='padding-bottom:1.5em;')
        page.td.close()
        page.tr.close()
        
        page.tr()
        page.td()
        page.strong('Frozen: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='uri')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcuri',maxlength=45, size=8)
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_FR', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_FR', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='voluri',maxlength=10, size=6)
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.p("-", id = 'urioutput', align='center' )
        page.td.close()
        page.tr.close()
        
        page.tr()
        page.td()
        page.strong('Frozen Sediments: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='sedim')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcsedim',maxlength=45, size=8)
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_FS', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_FS', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='volsedim',maxlength=10, size=6)
        page.td.close()
        page.td()
        page.td.close()
        page.td()
        page.p("-", id = 'sedimoutput', align='center' )
        page.td.close()
        page.tr.close()
        
        page.table.close()
        return page

class CollectionClinicalFeature(models.Model):
    idCollection=models.ForeignKey(Collection, db_column='idCollection',verbose_name='Collection',blank=True, null=True)
    idSamplingEvent=models.ForeignKey('SamplingEvent', db_column='idSamplingEvent',verbose_name='Sampling event',blank=True, null=True)
    idClinicalFeature=models.ForeignKey('ClinicalFeature', db_column='idClinicalFeature',verbose_name='Clinical Feature')
    value=models.CharField(max_length=150)
    class Meta:
        verbose_name_plural='Collection ClinicalFeatures'
        db_table='collectionclinicalfeature'
    def __unicode__(self):
        return str(self.idCollection)+' '+str(self.idClinicalFeature)

class CollectionProtocol(models.Model):
    name=models.CharField(max_length=45)
    title=models.CharField(max_length=100)    
    project=models.CharField(max_length=50)
    projectDateRelease=models.DateField('Project Date Release')
    informedConsent=models.CharField('Informed Consent',max_length=50)
    informedConsentDateRelease=models.DateField('Informed Consent Date Release')
    ethicalCommittee=models.CharField('Ethical Committee',max_length=45)
    approvalDocument=models.CharField('Approval Document',max_length=45)
    approvalDate=models.DateField('Approval Date')
    defaultSharings = models.ManyToManyField(WG, blank=True, db_table='tissue_collectionprotocol_wg') # Default sharing event(s)

    class Meta:
        verbose_name_plural='Collection Protocols'
        db_table='collectionprotocol'

    def __unicode__(self):
        return self.name

    def get_defaultSharings(self): # for the admin
        return ', '.join([ defaultSharing.name for defaultSharing in self.defaultSharings.all() ])

    get_defaultSharings.short_description = 'Default Sharing'


class CollectionProtocolInvestigator(models.Model):
    idCollectionProtocol=models.ForeignKey(CollectionProtocol, db_column='idCollectionProtocol',verbose_name='Collection Protocol')
    idPrincipalInvestigator=models.ForeignKey('PrincipalInvestigator', db_column='idPrincipalInvestigator',verbose_name='Principal Investigator')
    class Meta:
        verbose_name_plural='CollectionProtocol Investigators'
        db_table='collectionprotocolinvestigator'
        unique_together=("idCollectionProtocol","idPrincipalInvestigator")
    def __unicode__(self):
        return str(self.idCollectionProtocol)+' '+str(self.idPrincipalInvestigator)
    
class CollectionProtocolParticipant(models.Model):
    idCollectionProtocol=models.ForeignKey(CollectionProtocol, db_column='idCollectionProtocol',verbose_name='Collection Protocol')
    idParticipant=models.ForeignKey('ParticipantSponsor', db_column='idParticipant',verbose_name='Participant')
    class Meta:
        verbose_name_plural='CollectionProtocol Participants'
        db_table='collectionprotocolparticipant'
        unique_together=("idCollectionProtocol","idParticipant")
    def __unicode__(self):
        return str(self.idCollectionProtocol)+' '+str(self.idParticipant)
    
class CollectionProtocolSponsor(models.Model):
    idCollectionProtocol=models.ForeignKey(CollectionProtocol, db_column='idCollectionProtocol',verbose_name='Collection Protocol')
    idSponsor=models.ForeignKey('ParticipantSponsor', db_column='idSponsor',verbose_name='Sponsor')
    class Meta:
        verbose_name_plural='CollectionProtocol Sponsors'
        db_table='collectionprotocolsponsor'
        unique_together=("idCollectionProtocol","idSponsor")
    def __unicode__(self):
        return str(self.idCollectionProtocol)+' '+str(self.idSponsor)
   
class CollectionType(models.Model):
    abbreviation=models.CharField(max_length=3)
    longName=models.CharField(max_length=30)
    type=models.CharField(max_length=30,blank=True, null=True)
    class Meta:
        verbose_name_plural='Collection Types'
        db_table='collectiontype'
    def __unicode__(self):
        return self.longName

class Courier(models.Model):
    name=models.CharField(max_length=50)  
    class Meta:
        verbose_name_plural='Couriers'
        db_table='courier'
    def __unicode__(self):
        return self.name

class DerivationEvent(models.Model):
    idSamplingEvent=models.ForeignKey('SamplingEvent', db_column='idSamplingEvent',verbose_name='Sampling Event',blank=True, null=True)
    idAliqDerivationSchedule=models.ForeignKey('AliquotDerivationSchedule', db_column='idAliqDerivationSchedule',verbose_name='Aliquot Derivation Schedule',blank=True, null=True)
    derivationDate=models.DateField('Derivation Date')
    operator=models.CharField(max_length=45)
    class Meta:
        verbose_name_plural='Derivation Events'
        db_table='derivationevent'
    def __unicode__(self):
        return str(self.idSamplingEvent)+' '+str(self.derivationDate)+' '+str(self.operator)
    
class DerivationProtocol(models.Model):
    idKitType=models.ForeignKey('KitType', db_column='idKitType',verbose_name='Kit Type',blank=True,null=True)
    name=models.CharField(max_length=45)
    class Meta:
        verbose_name_plural='Derivation Protocols'
        db_table='derivationprotocol'
    def __unicode__(self):
        return self.name
    
class DerivationSchedule(models.Model):
    scheduleDate=models.DateField('Schedule Date')
    operator=models.CharField(max_length=30)
    class Meta:
        verbose_name_plural='Derivation Schedules'
        db_table='derivationschedule'
    def __unicode__(self):
        return self.operator+' '+str(self.scheduleDate)
    
class Drug(models.Model):
    name=models.CharField(max_length=100)
    externalId=models.IntegerField('External ID', blank=True, null=True)
    class Meta:
        verbose_name_plural='Drugs'
        db_table='drug'
    def __unicode__(self):
        return self.name
    
class Experiment(models.Model):
    name=models.CharField(max_length=45)
    folder=models.CharField(max_length=45)
    class Meta:
        verbose_name_plural='Experiments'
        db_table='experiment'
    def __unicode__(self):
        return self.name
    
class ExperimentFile (models.Model):
    idAliquotExperiment= models.ForeignKey(AliquotExperiment, db_column='idAliquotExperiment',verbose_name='Aliquot Experiment')
    fileName = models.CharField(max_length=100)
    linkId = models.CharField(max_length=100)
    idFileType= models.ForeignKey('FileType', db_column='idFileType',verbose_name='File Type',blank=True,null=True)
    class Meta:
        verbose_name_plural='Experiment Files'
        db_table = 'experimentfile'
    def __unicode__(self):
        return str(self.idAliquotExperiment)+' '+self.fileName
    
class ExperimentSchedule(models.Model):
    scheduleDate=models.DateField('Schedule Date')
    operator= models.ForeignKey(User, db_column='operator',verbose_name='Operator')
    class Meta:
        verbose_name_plural='Experiment Schedules'
        db_table='experimentschedule'
    def __unicode__(self):
        return self.operator.username+' '+str(self.scheduleDate)
    
class Feature(models.Model):
    idAliquotType=models.ForeignKey(AliquotType, db_column='idAliquotType',verbose_name='Aliquot Type')
    name=models.CharField(max_length=30)  
    measureUnit=models.CharField(max_length=20, blank=True)
    class Meta:
        verbose_name_plural='Features'
        db_table='feature'
    def __unicode__(self):
        return self.name+' '+str(self.measureUnit)+' '+str(self.idAliquotType)

class FeatureDerivation(models.Model):
    name=models.CharField(max_length=50)
    class Meta:
        verbose_name_plural='Feature Derivations'
        db_table='featurederivation'
    def __unicode__(self):
        return self.name
    
class FeatureDerAliqType(models.Model):
    idFeatureDerivation=models.ForeignKey(FeatureDerivation, db_column='idFeatureDerivation',verbose_name='Feature Derivation')
    idAliqType=models.ForeignKey(AliquotType, db_column='idAliqType',verbose_name='Aliquot Type')
    unityMeasure=models.CharField(max_length=20, blank=True)
    class Meta:
        verbose_name_plural='FeatureDerivation AliquotType'
        db_table='featurederaliqtype'
    def __unicode__(self):
        return str(self.idFeatureDerivation)+' '+str(self.idAliqType)+' '+self.unityMeasure

class FeatureDerProtocol(models.Model):
    idDerProtocol=models.ForeignKey(DerivationProtocol, db_column='idDerProtocol',verbose_name='Derivation Protocol')
    idFeatureDerivation=models.ForeignKey(FeatureDerivation, db_column='idFeatureDerivation',verbose_name='Feature Derivation')
    value=models.FloatField('Value')
    unityMeasure=models.CharField(max_length=20, blank=True)
    class Meta:
        verbose_name_plural='Feature DerivationProtocol'
        db_table='featurederprotocol'
    def __unicode__(self):
        return str(self.idDerProtocol)+' '+str(self.idFeatureDerivation)
    
class FeatureSlideProtocol(models.Model):
    idSlideProtocol=models.ForeignKey('SlideProtocol', db_column='idSlideProtocol',verbose_name='Slide Protocol')
    idFeatureDerivation=models.ForeignKey(FeatureDerivation, db_column='idFeatureDerivation',verbose_name='Feature Derivation')
    value=models.CharField(max_length=30)
    unityMeasure=models.CharField(max_length=20, blank=True)
    class Meta:
        verbose_name_plural='Feature SlideProtocol'
        db_table='featureslideprotocol'
    def __unicode__(self):
        return str(self.idSlideProtocol)+' '+str(self.idFeatureDerivation)

class FileType(models.Model):
    name=models.CharField(max_length=50)
    abbreviation=models.CharField(max_length=30)
    class Meta:
        verbose_name_plural='File Types'
        db_table='filetype'
    def __unicode__(self):
        return self.name

class FileTypeExperiment(models.Model):
    idExperiment=models.ForeignKey('Experiment', db_column='idExperiment',verbose_name='Experiment')
    idFileType=models.ForeignKey(FileType, db_column='idFileType',verbose_name='File Type')
    class Meta:
        verbose_name_plural='File Type Experiments'
        db_table='filetypeexperiment'
    def __unicode__(self):
        return str(self.idExperiment)+' > '+str(self.idFileType)
    
class Instrument(models.Model):
    code=models.CharField(max_length=45)
    name=models.CharField(max_length=45)
    manufacturer=models.CharField(max_length=45, blank=True)
    description=models.CharField(max_length=150, blank=True)
    class Meta:
        verbose_name_plural='Instruments'
        db_table='instrument'
    def __unicode__(self):
        return str(self.name)+' '+str(self.code)
    
class Kit(models.Model):
    idKitType=models.ForeignKey('KitType', db_column='idKitType',verbose_name='Kit Type')
    barcode=models.CharField(max_length=45)
    openDate=models.DateField('Open Date',blank=True)
    expirationDate=models.DateField('Expiration Date')
    remainingCapacity=models.IntegerField('Capacity')
    lotNumber=models.CharField(max_length=45, blank=True)
    
    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername),))
    
    class Meta:
        verbose_name_plural='Kits'
        db_table='kit'
    def __unicode__(self):
        return str(self.barcode)
    
class KitType(models.Model):
    name=models.CharField(max_length=45)
    capacity=models.IntegerField('Capacity')
    producer=models.CharField(max_length=45, blank=True)
    catalogueNumber=models.CharField('Catalogue Number',max_length=45, blank=True)
    instructions=models.CharField(max_length=50, blank=True)
    class Meta:
        verbose_name_plural='Kit Types'
        db_table='kittype'
    def __unicode__(self):
        return str(self.name)

class LabelConfiguration(models.Model):
    name=models.CharField(max_length=30)
    idLabelProtocol=models.ForeignKey('LabelProtocol', db_column='idLabelProtocol',verbose_name='Label Protocol',blank=True, null=True)
    class Meta:
        verbose_name_plural='Label Configurations'
        db_table='labelconfiguration'
    def __unicode__(self):
        return self.name

class LabelConfigurationLabelFeature(models.Model):
    idLabelConfiguration=models.ForeignKey(LabelConfiguration, db_column='idLabelConfiguration',verbose_name='Label Configuration')
    idLabelFeature=models.ForeignKey('LabelFeature', db_column='idLabelFeature',verbose_name='Label Feature', blank=True, null=True)
    idLabelMarker=models.ForeignKey('LabelMarker', db_column='idLabelMarker',verbose_name='Label Marker', blank=True, null=True)    
    value=models.CharField(max_length=100, blank=True)
    class Meta:
        verbose_name_plural='Label Configuration LabelFeature'
        db_table='labelconfigurationlabelfeature'
    def __unicode__(self):
        return str(self.idLabelConfiguration)+' '+str(self.idLabelFeature)+' '+str(self.idLabelMarker)

class LabelFeature(models.Model):
    name=models.CharField(max_length=50)
    measureUnit=models.CharField(max_length=10, blank=True)
    type=models.CharField(max_length=30, blank=True)
    class Meta:
        verbose_name_plural='Label Features'
        db_table='labelfeature'
    def __unicode__(self):
        return self.name+' '+str(self.measureUnit)

class LabelFeatureHierarchy(models.Model):
    idFatherFeature=models.ForeignKey(LabelFeature, db_column='idFatherFeature',related_name='father',verbose_name='Father Feature')
    idChildFeature=models.ForeignKey(LabelFeature, db_column='idChildFeature',related_name='child',verbose_name='Child Feature')
    class Meta:
        verbose_name_plural='Label Feature Hierarchies'
        db_table='labelfeaturehierarchy'
        unique_together=("idFatherFeature","idChildFeature")
    def __unicode__(self):
        return str(self.idChildFeature)+' is in '+str(self.idFatherFeature)

class LabelFile(models.Model):
    idAliquotLabelSchedule=models.ForeignKey(AliquotLabelSchedule, db_column='idAliquotLabelSchedule',verbose_name='Aliquot Label Schedule')
    fileName=models.CharField(max_length=100, blank=True)
    originalFileName=models.CharField(max_length=100, blank=True)
    fileId=models.CharField(max_length=50, blank=True)
    rawNodeId=models.CharField(max_length=50, blank=True)
    deleteTimestamp=models.DateTimeField('Delete Timestamp',blank=True,null=True)
    deleteOperator=models.ForeignKey(User, db_column='deleteOperator',related_name='id_deleteOperatorlabfile',verbose_name='Delete Operator',blank=True,null=True)
    class Meta:
        verbose_name_plural='Label Files'
        db_table='labelfile'
    def __unicode__(self):
        return str(self.idAliquotLabelSchedule)+' '+self.fileName

class LabelMarker(models.Model):
    name=models.CharField(max_length=40)
    class Meta:
        verbose_name_plural='Label Markers'
        db_table='labelmarker'
    def __unicode__(self):
        return self.name

class LabelMarkerLabelFeature(models.Model):
    idLabelMarker=models.ForeignKey(LabelMarker, db_column='idLabelMarker',verbose_name='Label Marker')
    idLabelFeature=models.ForeignKey(LabelFeature, db_column='idLabelFeature',verbose_name='Label Feature')
    value=models.CharField(max_length=100, blank=True)
    class Meta:
        verbose_name_plural='Label Marker LabelFeature'
        db_table='labelmarkerlabelfeature'
    def __unicode__(self):
        return str(self.idLabelMarker)+' '+str(self.idLabelFeature)

class LabelProtocol(models.Model):
    name=models.CharField(max_length=50)
    class Meta:
        verbose_name_plural='Label Protocols'
        db_table='labelprotocol'
    def __unicode__(self):
        return self.name
    
class LabelProtocolLabelFeature(models.Model):
    idLabelProtocol=models.ForeignKey(LabelProtocol, db_column='idLabelProtocol',verbose_name='Label Protocol')
    idLabelFeature=models.ForeignKey(LabelFeature, db_column='idLabelFeature',verbose_name='Label Feature', blank=True, null=True)
    idLabelMarker=models.ForeignKey(LabelMarker, db_column='idLabelMarker',verbose_name='Label Marker', blank=True, null=True)    
    value=models.CharField(max_length=100, blank=True)
    class Meta:
        verbose_name_plural='Label Protocol LabelFeature'
        db_table='labelprotocollabelfeature'
    def __unicode__(self):
        return str(self.idLabelProtocol)+' '+str(self.idLabelFeature)+' '+str(self.idLabelMarker)

class LabelSchedule(models.Model):
    scheduleDate=models.DateField('Schedule Date')
    operator= models.ForeignKey(User, db_column='operator',verbose_name='Operator')
    class Meta:
        verbose_name_plural='Label Schedules'
        db_table='labelschedule'
    def __unicode__(self):
        return self.operator.username+' '+str(self.scheduleDate)

class Mask(models.Model):
    name=models.CharField(max_length=40)
    class Meta:
        verbose_name_plural='Masks'
        db_table='mask'
    def __unicode__(self):
        return self.name

class MaskField(models.Model):
    name=models.CharField(max_length=40)
    identifier=models.CharField(max_length=10)
    class Meta:
        verbose_name_plural='Mask Fields'
        db_table='maskfield'
    def __unicode__(self):
        return self.name
    
class MaskMaskField(models.Model):
    idMask=models.ForeignKey(Mask, db_column='idMask',verbose_name='Mask')
    idMaskField=models.ForeignKey(MaskField, db_column='idMaskField',verbose_name='Mask Field')
    encrypted = models.BooleanField()
    class Meta:
        verbose_name_plural='Mask MaskFields'
        db_table='maskmaskfield'
    def __unicode__(self):
        return str(self.idMask)+' '+str(self.idMaskField)
    
class MaskOperator(models.Model):
    idMask=models.ForeignKey(Mask, db_column='idMask',verbose_name='Mask')
    operator= models.ForeignKey(User, db_column='operator',verbose_name='Operator')
    class Meta:
        verbose_name_plural='Mask Operator'
        db_table='maskoperator'
    def __unicode__(self):
        return str(self.idMask)+' '+str(self.operator)
    
class Measure(models.Model):
    idInstrument=models.ForeignKey(Instrument, db_column='idInstrument',verbose_name='Instrument')
    name=models.CharField(max_length=30)
    measureUnit=models.CharField(max_length=30)
    class Meta:
        verbose_name_plural='Measures'
        db_table='measure'
    def __unicode__(self):
        return self.name+' '+str(self.idInstrument)+' '+self.measureUnit
    
class MeasurementEvent(models.Model):
    idMeasure=models.ForeignKey(Measure, db_column='idMeasure',verbose_name='Measure')
    idQualityEvent=models.ForeignKey('QualityEvent', db_column='idQualityEvent',verbose_name='Quality Event')
    value=models.FloatField()
    class Meta:
        verbose_name_plural='Measurement Events'
        db_table='measurementevent'
    def __unicode__(self):
        return str(self.idMeasure)+' '+str(self.idQualityEvent)
    
class MeasureParameter(models.Model):
    idMeasure=models.ForeignKey(Measure, db_column='idMeasure',verbose_name='Measure')
    idParameter=models.ForeignKey('Parameter', db_column='idParameter',verbose_name='Parameter')
    idQualityProtocol=models.ForeignKey('QualityProtocol', db_column='idQualityProtocol',verbose_name='Quality Protocol')
    class Meta:
        verbose_name_plural='Measure Parameters'
        db_table='measureparameter'
        unique_together=("idMeasure","idParameter","idQualityProtocol")
    def __unicode__(self):
        return str(self.idMeasure)

class Member(models.Model):
    class Meta:
        permissions=(
                     ('can_view_institutional_collection','Institutional Collection'),
                     ('can_view_collaboration_collection','Collaboration Collection'),
                     ('can_view_insert_new_kit_type','Insert New Kit Type'),
                     ('can_view_register_new_kit','Register New Kit'),
                     ('can_view_create_new_protocol','Create New Protocol'),
                     ('can_view_plan_derivation','Plan Derivation'),
                     ('can_view_select_aliquots_and_protocols','Select Aliquots And Protocols'),
                     ('can_view_select_kit','Select Kit'),
                     ('can_view_perform_QC_QA','Perform Qc Qa'),
                     ('can_view_create_derivatives','Create Derivatives'),
                     ('can_view_calculate_aliquot_values','Calculate Aliquot Values'),
                     ('can_view_plan_aliquots_to_revalue','Plan Aliquots To Revalue'),
                     ('can_view_revalue_aliquots','Revalue Aliquots'),
                     ('can_view_file_saved','File Saved'),
                     ('can_view_plan_aliquots_to_split','Plan Aliquots To Split'),
                     ('can_view_split_aliquots','Split Aliquots'),
                     ('can_view_plan_retrieval','Plan Retrieval'),
                     ('can_view_retrieve_aliquots','Retrieve Aliquots'),
                     ('can_view_plan_experiments','Plan Experiments'),
                     ('can_view_execute_experiments','Execute Experiments'),
                    )

class MouseTissueType(models.Model):
    abbreviation=models.CharField(max_length=3)
    longName=models.CharField(max_length=30)
    class Meta:
        verbose_name_plural='Mouse Tissue Types'
        db_table='mousetissuetype'
    def __unicode__(self):
        return self.longName
    
class Parameter(models.Model):
    name=models.CharField(max_length=30)
    measureUnit=models.CharField(max_length=30)
    class Meta:
        verbose_name_plural='Parameters'
        db_table='parameter'
    def __unicode__(self):
        return self.name+' '+self.measureUnit
    
class ParticipantSponsor(models.Model):
    name=models.CharField(max_length=80)
    base=models.CharField(max_length=40)
    class Meta:
        verbose_name_plural='Participant Sponsors'
        db_table='participantsponsor'
    def __unicode__(self):
        return self.name+' - '+self.base
    
class PositionSchedule(models.Model):
    scheduleDate=models.DateField('Schedule Date')
    operator=models.CharField(max_length=30)
    class Meta:
        verbose_name_plural='Position Schedules'
        db_table='positionschedule'
    def __unicode__(self):
        return self.operator+' '+str(self.scheduleDate)
    
class PrincipalInvestigator(models.Model):
    name=models.CharField(max_length=30)
    surname=models.CharField(max_length=30)
    class Meta:
        verbose_name_plural='Principal Investigators'
        db_table='principalinvestigator'
    def __unicode__(self):
        return self.name+' '+self.surname
    
class QualityEvent(models.Model):
    objects=WgObjectRelatedManager()
    idQualityProtocol=models.ForeignKey('QualityProtocol', db_column='idQualityProtocol',verbose_name='Quality Protocol')
    idQualitySchedule=models.ForeignKey('QualitySchedule', db_column='idQualitySchedule',verbose_name='Quality Schedule', blank=True, null=True)
    idAliquot=models.ForeignKey(Aliquot, db_column='idAliquot',verbose_name='Aliquot', blank=True, null=True)
    idAliquotDerivationSchedule=models.ForeignKey('AliquotDerivationSchedule', db_column='idAliquotDerivationSchedule',verbose_name='Aliquot Derivation Schedule',blank=True, null=True)
    misurationDate=models.DateField('Misuration Date')
    insertionDate=models.DateField('Insertion Date',blank=True)
    operator=models.CharField(max_length=45)
    quantityUsed=models.FloatField(blank=True)
    class Meta:
        verbose_name_plural='Quality Events'
        db_table='qualityevent'
    def __unicode__(self):
        return str(self.idQualityProtocol)+' '+str(self.misurationDate)+' '+str(self.idAliquot)

class QualityEventFile(models.Model):
    idQualityEvent=models.ForeignKey('QualityEvent', db_column='idQualityEvent',verbose_name='Quality Event')
    file=models.CharField(max_length=150)
    judge=models.CharField(max_length=10)
    linkId = models.CharField(max_length=100,blank=True,null=True)
    class Meta:
        verbose_name_plural='Quality Event Files'
        db_table='qualityeventfile'
    def __unicode__(self):
        return str(self.idQualityEvent)+' '+self.file

class QualityProtocol(models.Model):
    idAliquotType=models.ForeignKey(AliquotType, db_column='idAliquotType',verbose_name='Aliquot Type')
    name=models.CharField(max_length=30)
    description=models.CharField(max_length=150,blank=True,null=True)
    mandatoryFields=models.BooleanField()
    quantityUsed=models.FloatField(blank=True)
    class Meta:
        verbose_name_plural='Quality Protocols'
        db_table='qualityprotocol'
    def __unicode__(self):
        return self.name+' '+str(self.idAliquotType)
    
class QualitySchedule(models.Model):
    scheduleDate=models.DateField('Schedule Date')
    operator=models.CharField(max_length=30)
    class Meta:
        verbose_name_plural='Quality Schedules'
        db_table='qualityschedule'
    def __unicode__(self):
        return self.operator+' '+str(self.scheduleDate)
    
class SamplingEvent(models.Model):
    idTissueType=models.ForeignKey('TissueType', db_column='idTissueType',verbose_name='Tissue Type', blank=True, null=True)
    idCollection=models.ForeignKey(Collection, db_column='idCollection',verbose_name='Collection')
    idSource=models.ForeignKey('Source', db_column='idSource',verbose_name='Source')
    idSerie=models.ForeignKey('Serie', db_column='idSerie',verbose_name='Serie')
    samplingDate=models.DateField('Sampling Date')
    class Meta:
        verbose_name_plural='Sampling Events'
        db_table='samplingevent'
    def __unicode__(self):
        return str(self.idCollection)+' '+str(self.idTissueType)
    
class Serie(models.Model):
    operator=models.CharField(max_length=30)
    serieDate=models.DateField('Serie date')
    class Meta:
        verbose_name_plural='Series'
        db_table='serie'
    def __unicode__(self):
        return self.operator+' '+str(self.serieDate)
    
class SlideProtocol(models.Model):
    name=models.CharField(max_length=40)
    class Meta:
        verbose_name_plural='Slide Protocols'
        db_table='slideprotocol'
    def __unicode__(self):
        return self.name
    
class SlideSchedule(models.Model):
    scheduleDate=models.DateField('Schedule Date')
    operator= models.ForeignKey(User, db_column='operator',verbose_name='Operator')
    class Meta:
        verbose_name_plural='Slide Schedules'
        db_table='slideschedule'
    def __unicode__(self):
        return self.operator.username+' '+str(self.scheduleDate)
    
class Source(models.Model):
    name=models.CharField(max_length=45)
    type=models.CharField(max_length=30)
    internalName=models.CharField(max_length=45)
    class Meta:
        verbose_name_plural='Sources'
        db_table='source'
    def __unicode__(self):
        return self.name

class SplitSchedule(models.Model):
    scheduleDate=models.DateField('Schedule Date')
    operator=models.CharField(max_length=30)
    class Meta:
        verbose_name_plural='Split Schedules'
        db_table='splischedule'
    def __unicode__(self):
        return self.operator+' '+str(self.scheduleDate)
    
class TissueType(models.Model):
    abbreviation=models.CharField(max_length=2)
    longName=models.CharField(max_length=30)
    type=models.CharField(max_length=30,blank=True, null=True)
    class Meta:
        verbose_name_plural='Tissue Types'
        db_table='tissuetype'
    def __unicode__(self):
        return self.longName

class Transfer(models.Model):
    idTransferSchedule=models.ForeignKey('TransferSchedule', db_column='idTransferSchedule',verbose_name='Transfer Schedule')
    operator=models.ForeignKey(User, db_column='operator',related_name='id_operator',verbose_name='Operator',blank=True,null=True)
    addressTo=models.ForeignKey(User, db_column='addressTo',related_name='id_addressTo',verbose_name='Address To')
    plannedDepartureDate=models.DateField('Planned Departure Date',blank=True)
    departureDate=models.DateField('Departure Date',blank=True)
    departureExecuted=models.BooleanField(default=False)
    departureValidated=models.BooleanField()
    deliveryDate=models.DateField('Delivery Date',blank=True)
    deliveryExecuted=models.BooleanField(default=False)
    deliveryValidated=models.BooleanField()
    idCourier=models.ForeignKey(Courier, db_column='idCourier',verbose_name='Courier',blank=True,null=True)
    trackingNumber=models.CharField('Tracking Number',max_length=45,blank=True)
    deleteTimestamp=models.DateTimeField('Delete Timestamp',blank=True,null=True)
    deleteOperator=models.ForeignKey(User, db_column='deleteOperator',related_name='id_deleteOperator',verbose_name='Delete Operator',blank=True,null=True)
    class Meta:
        verbose_name_plural='Transfers'
        db_table='transfer'
    def __unicode__(self):
        return str(self.idTransferSchedule)+' assigned to '+str(self.operator)

class TransferSchedule(models.Model):
    scheduleDate=models.DateField('Schedule Date')
    operator=models.ForeignKey(User, db_column='operator',verbose_name='Operator')
    class Meta:
        verbose_name_plural='Transfer Schedules'
        db_table='transferschedule'
    def __unicode__(self):
        return self.operator.username+' '+str(self.scheduleDate)

class TransformationChange(models.Model):
    idFromType=models.ForeignKey(AliquotType, db_column='idFromType',related_name='from',verbose_name='From Type')
    idToType=models.ForeignKey(AliquotType, db_column='idToType',related_name='to',verbose_name='To Type')
    class Meta:
        verbose_name_plural='Transformation Changes'
        db_table='transformationchange'
        unique_together=("idFromType","idToType")
    def __unicode__(self):
        return str(self.idFromType)+'->'+str(self.idToType)
    
class TransformationDerivation(models.Model):
    idDerivationProtocol=models.ForeignKey(DerivationProtocol, db_column='idDerivationProtocol',verbose_name='Derivation Protocol')
    idTransformationChange=models.ForeignKey(TransformationChange, db_column='idTransformationChange',verbose_name='Transformation Change')
    class Meta:
        verbose_name_plural='Transformation Derivations'
        db_table='transformationderivation'
        unique_together=("idDerivationProtocol","idTransformationChange")
    def __unicode__(self):
        return str(self.idDerivationProtocol)+' '+str(self.idTransformationChange)

class TransformationSlide(models.Model):
    idSlideProtocol=models.ForeignKey(SlideProtocol, db_column='idSlideProtocol',verbose_name='Slide Protocol')
    idTransformationChange=models.ForeignKey(TransformationChange, db_column='idTransformationChange',verbose_name='Transformation Change')
    class Meta:
        verbose_name_plural='Transformation Slides'
        db_table='transformationslide'
        unique_together=("idSlideProtocol","idTransformationChange")
    def __unicode__(self):
        return str(self.idSlideProtocol)+' '+str(self.idTransformationChange)
    
class Urls(models.Model):
    _url = models.CharField(max_length = 60,db_column='url')
    default = models.BooleanField()
    idWebService = models.ForeignKey('WebService', db_column='idWebService',null=True,blank=True)
    class Meta:
        verbose_name_plural = 'urls'
        db_table = 'url'
    @property
    def url(self):
        if str(self._url).startswith('http'):
            return self._url
        else:
            return settings.DOMAIN_URL+self._url
    def __unicode__(self):
        return self.url
    
class WebService(models.Model):
    name = models.CharField(max_length=100)
   
    class Meta:
        verbose_name_plural = 'Web Services'
        db_table = 'webservice'

    def __unicode__(self):
        return self.name

class ChildHamilton(models.Model):    
    taskid=models.IntegerField('Task id')    
    barcode=models.CharField(max_length=45,blank=True,null=True)
    #e' il vol da prelevare dalla madre, che sommato al diluente, da' il vol totale del campione 
    volume=models.FloatField()
    #e' il vol del diluente
    vol_kit=models.FloatField()
    concentration=models.FloatField(blank=True,null=True)
    verify_remain=models.BooleanField(default=True)
    sample_id=models.ForeignKey('SampleHamilton', db_column='sample_id',verbose_name='Sample')
    run_id=models.ForeignKey('RunHamilton', db_column='run_id',verbose_name='Run id', blank=True, null=True)
    class Meta:
        verbose_name_plural='Child'
        db_table='child'
        app_label='hamiltonapp'
    def __unicode__(self):
        return 'Father: '+str(self.sample_id.genid)+'. It is in '+str(self.barcode)

class LabwareTypeHamilton (models.Model):
    name = models.CharField(max_length = 45)
    description = models.CharField(max_length = 100)
    class Meta:
        verbose_name_plural = 'Labware type'
        db_table = 'labware_type'
        app_label='hamiltonapp'
    def __unicode__(self):
        return self.name
    
class MeasureHamilton(models.Model):
    name=models.CharField(max_length=45)
    value=models.CharField(max_length=45)    
    sample_id=models.ForeignKey('SampleHamilton', db_column='sample_id',verbose_name='Sample')
    run_id=models.ForeignKey('RunHamilton', db_column='run_id',verbose_name='Run id')
    version=models.IntegerField(default=1)
    class Meta:
        verbose_name_plural='Measure'
        db_table='measure'
        app_label='hamiltonapp'
    def __unicode__(self):
        return self.name+': '+self.value
    
class OutFileHamilton(models.Model):
    path=models.CharField(max_length=255)    
    run_id=models.ForeignKey('RunHamilton', db_column='run_id',verbose_name='Run')
    class Meta:
        verbose_name_plural='Out file'
        db_table='out_file'
        app_label='hamiltonapp'
    def __unicode__(self):
        return self.path

class PlanHamilton(models.Model):
    name=models.CharField(max_length=100)
    timestamp=models.DateTimeField()
    operator=models.CharField(max_length=45)
    executed=models.DateTimeField(blank=True,null=True)
    processed=models.DateTimeField(blank=True,null=True)
    alerted=models.DateTimeField(blank=True,null=True)
    labwareid=models.ForeignKey(LabwareTypeHamilton, db_column='labwareid',verbose_name='Labware')
    class Meta:
        verbose_name_plural='Plan'
        db_table='plan'
        app_label='hamiltonapp'
    def __unicode__(self):
        return self.name+': '+str(timezone.localtime(self.timestamp))
    
class PlanHasProtocolHamilton(models.Model):        
    plan_id=models.ForeignKey(PlanHamilton, db_column='plan_id',verbose_name='Plan')
    protocol_id=models.ForeignKey('ProtocolHamilton', db_column='protocol_id',verbose_name='Protocol')
    class Meta:
        verbose_name_plural='Plan has protocol'
        db_table='plan_has_protocol'
        app_label='hamiltonapp'
    def __unicode__(self):
        return self.plan_id.name+' '+self.protocol_id.name

class ProtocolHamilton(models.Model):
    name=models.CharField(max_length=100)
    protocol=models.CharField(max_length=100,blank=True,null=True)
    vol_kit=models.FloatField(blank=True,null=True)
    vol_taken=models.FloatField(blank=True,null=True)
    replica=models.IntegerField(blank=True,null=True)
    protocol_type_id=models.ForeignKey('ProtocolTypeHamilton', db_column='protocol_type_id',verbose_name='Protocol type')
    class Meta:
        verbose_name_plural='Protocol'
        db_table='protocol'
        app_label='hamiltonapp'
    def __unicode__(self):
        return self.name

class ProtocolTypeHamilton (models.Model):
    name = models.CharField(max_length = 45)
    class Meta:
        verbose_name_plural = 'Protocol type'
        db_table = 'protocol_type'
        app_label='hamiltonapp'
    def __unicode__(self):
        return self.name

class ProtStdHamilton(models.Model):
    id_protocol=models.ForeignKey(ProtocolHamilton, db_column='id_protocol',verbose_name='Protocol')
    concentration=models.FloatField()
    class Meta:
        verbose_name_plural='Prot std'
        db_table='prot_std'
        app_label='hamiltonapp'
    def __unicode__(self):
        return self.id_protocol.name+' '+str(self.concentration)
    
class RunHamilton (models.Model):
    timestamp = models.DateTimeField()
    plan_id=models.ForeignKey('PlanHamilton', db_column='plan_id',verbose_name='Plan id',blank=True, null=True)
    class Meta:
        verbose_name_plural = 'Run'
        db_table = 'run'
        app_label='hamiltonapp'
    def __unicode__(self):
        return str(timezone.localtime(self.timestamp))
    
class SampleHamilton(models.Model):
    genid=models.CharField(max_length=45)
    barcode=models.CharField(max_length=45,blank=True,null=True)
    volume=models.FloatField()
    concentration=models.FloatField(blank=True,null=True)
    rank=models.IntegerField(blank=True,null=True)
    plan_id=models.ForeignKey('PlanHamilton', db_column='plan_id',verbose_name='Plan id')
    class Meta:
        verbose_name_plural='Sample'
        db_table='sample'
        app_label='hamiltonapp'
    def __unicode__(self):
        return self.genid
    
class SampleHasOutFileHamilton(models.Model):        
    sample_id=models.ForeignKey(SampleHamilton, db_column='sample_id',verbose_name='Sample')
    out_file_id=models.ForeignKey(OutFileHamilton, db_column='out_file_id',verbose_name='Out file')
    class Meta:
        verbose_name_plural='Sample has out file'
        db_table='sample_has_out_file'
        app_label='hamiltonapp'
    def __unicode__(self):
        return self.sample_id.genid+' '+self.out_file_id.path
    
    
