from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User,Permission
from time import strptime, strftime
from xenopatients import markup
from xenopatients.mw import threadlocals
import string, htmllib, audit, cgi, operator
from global_request_middleware import *
from django.db.models.query import QuerySet
from py2neo import neo4j, cypher, node, rel
from xenopatients.genealogyID import *
import pylibmc,json,urllib,urllib2
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
import datetime

class Member(models.Model):
    class Meta:
        permissions = (
            ("can_view_register_mice", "Register Mice"),
            ("can_view_change_status", "Change Status"),
            ("can_view_perform_qualitative", "Perform Qualitative"),
            ("can_view_perform_quantitative", "Perform Quantitative"),
            ("can_view_implant_xenografts", "Implant Xenografts"),
            ("can_view_explant_xenografts", "Explant Xenografts"),
            ("can_view_finalize_treatments", "Finalize Treatments"),
            ("can_view_manage_treatments", "Manage Treatments"),
            ("can_view_new_measurements", "New Measurements"),
        )

GENDERCHOICE = (
    ('m', 'male'),
    ('f', 'female'),
)

''' START GRAPH AREA'''

class WgObjectManager(models.Manager):

    def get_query_set(self):
        if settings.USE_GRAPH_DB==True and 'admin' not in get_WG():
            groups=get_WG()
            qs=BioMice_WG.objects.filter(WG__name__in=list(groups)).values_list('biomice__id')
            return super(WgObjectManager, self).get_query_set().filter(id__in=qs)
        else:
            return super(WgObjectManager, self).get_query_set()

    def all_old(self):
        return super(WgObjectManager, self).get_query_set()

    def get_old(self, *args, **kwargs):
        return super(WgObjectManager, self).get_query_set().get(*args, **kwargs)

    def filter_old(self, *args, **kwargs):
        return super(WgObjectManager, self).get_query_set().filter(*args, **kwargs)

    def values_list_old(self, *args, **kwargs):
        return super(WgObjectManager, self).get_query_set().values_list(*args, **kwargs)

    def values_list(self, *args, **kwargs):
        return super(WgObjectManager, self).values_list(*args, **kwargs)

    def count_old(self):
        return super(WgObjectManager, self).get_query_set().count()



class WgObjectRelatedManager(models.Manager):

    def get_query_set(self):
        if settings.USE_GRAPH_DB==True and 'admin' not in get_WG():
            qs=BioMice.objects.all()
            return super(WgObjectRelatedManager, self).get_query_set().filter(id_mouse__in=qs)
        else:
            return super(WgObjectRelatedManager, self).get_query_set()

    def all_old(self):
        return super(WgObjectRelatedManager, self).get_query_set()

    def get_old(self, *args, **kwargs):
        return super(WgObjectRelatedManager, self).get_query_set().get(*args, **kwargs)

    def filter_old(self, *args, **kwargs):
        return super(WgObjectRelatedManager, self).get_query_set().filter(*args, **kwargs)

    def values_list_old(self, *args, **kwargs):
        return super(WgObjectRelatedManager, self).get_query_set().values_list(*args, **kwargs)

    def count_old(self):
        return super(WgObjectManager, self).get_query_set().count()

def setLabels(nodeType, altype):
    labels = []
    alTypes = {'VT':'Viable', 'SF':'SnapFrozen', 'RL':'RNALater', 'D':'DNA', 'FF':'FormalinFixed', 'PL': 'PlasmaIsolation', 'OF': 'OCTFrozen', 'SI': 'SerumIsolation', 'CH':'ChinaBlack', 'PX':'PAXtube', 'R':'RNA', 'D':'DNA', 'P':'Protein', 'cR':'cRNA', 'cD':'cDNA'}
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
        if nextSemanticLevel == 'Origin': # TODO valutare se inserire o meno visto che sarebbe duplicato per il numero di casi con stessa origine
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


def add_aliquot_node(aliquot):
    try:
        father_gen_id=aliquot.id_explant.id_mouse.id_genealogy
        groupsToSend=list()
        gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
        if gdb.get_indexed_node('node_auto_index','identifier',aliquot.id_genealogy):
            return
        else:
            batch = neo4j.WriteBatch(gdb)

            nodes = {}
            print aliquot.id_genealogy
            g = GenealogyID(aliquot.id_genealogy)
            altype = 'c'+g.get2Derivation() if g.is2Derivation() else g.getArchivedMaterial()
            print altype
            dateAl = datetime.datetime.now()
            nodes[g.getGenID()] = {'type':'Aliquot', 'altype': altype, 'id':aliquot.id, 'relationships':{}, 'nodeid': None, 'date':str(dateAl)}

            nodes[father_gen_id] = {'type':'Biomouse', 'nodeid': None, 'wg':{}, 'relationships':{}}
            nodes[father_gen_id]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',father_gen_id)


            query="START n=node:node_auto_index(identifier='"+father_gen_id+"') match (w:WG)-[r]->n WHERE not has(r.endDate) RETURN id(r), type(r), w.identifier, id(w)"
            data, metadata = cypher.execute(gdb, query)
            if len(data)>0:
                for d in data:
                    nodes[father_gen_id]['wg'][d[0]] = {'nodeid': gdb.get_indexed_node('node_auto_index','identifier',d[2]), 'rel_type': d[1], 'name':d[2]}

            #relsWg = list(graph_db.match(end_node=nodes[father_gen_id]['nodeid']), rel_type="OwnsData") # e i paramteri associati? e i nodi attaccati?
            fatherNode = nodes[father_gen_id]

            nodes[g.getGenID()]['relationships'][father_gen_id] = {'type': 'generates', 'app':'explant'}

            buildSemanticNode(g.getGenID(), 'Aliquot', None, nodes, dateAl)

            batch = neo4j.WriteBatch(gdb)

            for n, nInfo in nodes.items():
                flagInsert = True
                print n, nInfo
                if nInfo['nodeid'] is None:
                    nInfo['nodeid'] = batch.create(node(identifier=n))
                    labels = setLabels(nInfo['type'], nInfo['altype'])
                    batch.add_labels(nInfo['nodeid'], *labels)
                    if nInfo['type'] in ['Biomouse', 'Aliquot', 'Collection']:
                        for wg, wgInfo in fatherNode['wg'].items():
                            batch.create( rel( wgInfo['nodeid'], wgInfo['rel_type'], nInfo['nodeid'], {'startDate': nInfo['date'], 'endDate':None} ) )


            for dest, destInfo in nodes.items():
                for source, relInfo in destInfo['relationships'].items():
                    if relInfo['app']:
                        batch.create( rel( nodes[source]['nodeid'], relInfo['type'], destInfo['nodeid'], {'app': relInfo['app']} ) )
                    else:
                        batch.create( rel( nodes[source]['nodeid'], relInfo['type'], destInfo['nodeid'] ) )

            results = batch.submit()
            batch.clear()

    except Exception,e:
        print 'Error graph', e
        subject='ERROR DURING SAVING ALIQUOT EXPLANTED IN GRAPH DB'
        message='Error saving genid: ',str(aliquot.id_genealogy)
        toList=list()
        email = EmailMessage(subject,message,'',toList,[],'','','',[])
        email.send(fail_silently=False)

    address = Urls.objects.get(default = '1').url
    url = address + "/api/saveWgAliquot/"
    h=''
    groupsToSend = [ wgInfo['name'] for wg, wgInfo in fatherNode['wg'].items() ]
    values = {'api_key' : h, 'genid':aliquot.id_genealogy,'wgList':json.dumps(groupsToSend) }
    data = urllib.urlencode(values)
    try:
        u = urllib2.urlopen(url,data)
        res =  u.read()
        res=json.loads(res)
        if res['data']=='ok':
            return
        else:
            print "valutare! errore in biob"
    except urllib2.HTTPError,e:
        print e

    return

@transaction.commit_on_success
def add_mice_node(mice):
    try:
        gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
        if gdb.get_indexed_node('node_auto_index','identifier',mice.id_genealogy):
            return
        else:
            
            print "inizio aggiunta topo", mice.id_genealogy
            father_gen_id = Implant_details.objects.get_old(id_mouse=mice.id).aliquots_id.id_genealogy
            print father_gen_id
            g = GenealogyID(mice.id_genealogy)
            nodes = {}
            dateMouse = datetime.datetime.now()

            nodes[mice.id_genealogy] = {'type':'Biomouse', 'altype': None, 'id':mice.id,  'relationships':{}, 'nodeid': None, 'date':str(dateMouse)}

            nodes[father_gen_id] = {'type':'Aliquot', 'nodeid': None, 'wg':{}, 'relationships':{}, 'alType': None}
            nodes[father_gen_id]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',father_gen_id)


            query="START n=node:node_auto_index(identifier='"+father_gen_id+"') match (w:WG)-[r]->n WHERE not has(r.endDate) RETURN id(r), type(r), w.identifier, id(w)"
            data, metadata = cypher.execute(gdb, query)
            print query, data
            if len(data)>0:
                for d in data:
                    nodes[father_gen_id]['wg'][d[0]] = {'nodeid': gdb.get_indexed_node('node_auto_index','identifier',d[2]), 'rel_type': d[1], 'name':d[2]}

            #relsWg = list(graph_db.match(end_node=nodes[father_gen_id]['nodeid']), rel_type="OwnsData") # e i paramteri associati? e i nodi attaccati?
            fatherNode = nodes[father_gen_id]
            print fatherNode

            nodes[g.getGenID()]['relationships'][father_gen_id] = {'type': 'generates', 'app':'implant'}

            buildSemanticNode(g.getGenID(), 'Biomouse', None, nodes, dateMouse)
            print 'after buildSemanticNode for ', g.getGenID()
            batch = neo4j.WriteBatch(gdb)
            batch.clear()


            rels = []

            for n, nInfo in nodes.items():
                print 'before ', n, nInfo
                if nInfo['nodeid'] is None:
                    nInfo['nodeid'] = batch.create(node(identifier=n))
                    labels = setLabels(nInfo['type'], nInfo['altype'])
                    #print labels
                    batch.add_labels(nInfo['nodeid'], *labels)
                    if nInfo['type'] in ['Biomouse', 'Aliquot', 'Collection']:
                        for wg, wgInfo in fatherNode['wg'].items():
                            batch.create( rel (wgInfo['nodeid'], wgInfo['rel_type'], nInfo['nodeid'], {'startDate': nInfo['date'], 'endDate':None} ) )
                print 'after ', n, nInfo
            
            for dest, destInfo in nodes.items():
                for source, relInfo in destInfo['relationships'].items():
                    print dest, destInfo, source, relInfo
                    if relInfo['app']:
                        batch.create( rel( nodes[source]['nodeid'], relInfo['type'], destInfo['nodeid'], {'app': relInfo['app']} ) )
                    else:
                        batch.create( rel( nodes[source]['nodeid'], relInfo['type'], destInfo['nodeid'] ) )

            print '---------------------------------------------'
            print 'nodes',nodes
            print 'batch submit'
            results = batch.submit()
            batch.clear()
            print 'batch clear'

            for wg, wgInfo in fatherNode['wg'].items():
                if BioMice_WG.objects.filter(biomice=mice,WG=WG.objects.get(name=wgInfo['name'])).count()==0:
                    m2m=BioMice_WG(biomice=mice,WG=WG.objects.get(name=wgInfo['name']))
                    m2m.save()

    except Exception,e:
        print e
        transaction.rollback()
        if BioMice_WG.objects.filter(biomice=mice,WG=WG.objects.get(name='admin')).count()==0:
            m2m=BioMice_WG(biomice=mice,WG=WG.objects.get(name='admin'))
            m2m.save()
        subject='ERROR DURING SAVING XENO IN GRAPH DB'
        message='Error saving genid :',str(mice.id_genealogy)
        toList=list()
        email = EmailMessage(subject,message,'',toList,[],'','','',[])
        #email.send(fail_silently=False)

    return



    '''END GRAPH AREA '''



def getUsername(instance):
    return threadlocals.get_current_user()

class Via_mode (models.Model):
    id_via = models.AutoField(primary_key=True)
    description = models.CharField(max_length=45, blank=True, unique=True)
    longDescription = models.TextField(blank=True,null=True)
    class Meta:
        verbose_name_plural = 'via_mode'
        db_table = 'via_mode'
    def __unicode__(self):
        return self.description
    def __str__(self):
        return self.description

class Status_info (models.Model):
    description = models.CharField(max_length=45,blank=True, unique=True)
    class Meta:
        verbose_name_plural = 'status_info'
        db_table = 'status_info'
    def __unicode__(self):
      return self.description

class Status (models.Model):
    name = models.CharField(max_length=45, unique=True)
    description = models.CharField(max_length=45,blank=True)
    default = models.BooleanField()
    class Meta:
        verbose_name_plural = 'status'
        db_table = 'status'
    def __unicode__(self):
      return self.name

class ChangeStatus (models.Model):
    from_status = models.ForeignKey(Status, related_name='from', db_column='from_status')
    to_status = models.ForeignKey(Status, related_name='to', db_column='to_status')
    class Meta:
        verbose_name_plural = 'change_status'
        db_table = 'change_status'
        unique_together = ("from_status", "to_status")
    def __unicode__(self):
        return str(self.to_status)

class Status_info_has_status (models.Model):
    id_status = models.ForeignKey(Status,  db_column='id_status')
    id_info = models.ForeignKey(Status_info, db_column='id_info')
    class Meta:
        verbose_name_plural = 'status_info_has_status'
        db_table = 'status_info_has_status'
        unique_together = ("id_status", "id_info")
    def __unicode__(self):
      return str(self.id_status) +" - "+ str(self.id_info)


class Source(models.Model):
    id_source = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, unique=True)
    description = models.CharField(max_length=45)
    class Meta:
        verbose_name_plural = 'source'
        db_table = 'source'
    def __unicode__(self):
        return self.name

class Measure_type(models.Model):
    id_measure_type = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    description = models.CharField(max_length=45,blank=True)
    class Meta:
        verbose_name_plural = 'measure type'
        db_table = 'measure_type'
    def __unicode__(self):
        return self.name

class Scope_details(models.Model):
    id_scope_details = models.AutoField(primary_key=True)
    description = models.CharField(max_length=45,blank=True, unique=True)
    class Meta:
        verbose_name_plural = 'scope_details'
        db_table = 'scope_details'
    def __unicode__(self):
        return self.description


class Type_of_serie(models.Model):
    description = models.CharField(max_length=45, unique=True)
    class Meta:
        verbose_name_plural = 'type_of_serie'
        db_table = 'type_of_serie'
    def __unicode__(self):
        return self.description

class Protocols(models.Model):
    name = models.CharField(max_length=45)
    description = models.CharField(max_length=180, null=True, blank=True)
    class Meta:
        verbose_name_plural = 'protocols'
        db_table = 'protocols'
    def __unicode__(self):
        return str(self.name)


class Series(models.Model):
    id_operator = models.ForeignKey(User, db_column='id_operator')
    id_type = models.ForeignKey(Type_of_serie, db_column='id_type')
    id_protocol = models.ForeignKey(Protocols, db_column='id_protocol', blank=True, null=True)
    date = models.DateField('date of the series')
    notes = models.CharField(max_length=45, blank=True)
    class Meta:
        verbose_name_plural = 'series'
        db_table = 'series'
    def __unicode__(self):
        return str(self.id) + ' - ' + str(self.date)

class Mouse_strain(models.Model):
    id_strain = models.AutoField(primary_key=True)
    mouse_type_name = models.CharField(max_length=45, unique=True)
    officialName = models.CharField(max_length=80)
    linkToDoc = models.TextField()
    class Meta:
        verbose_name_plural = 'mouse_strain'
        db_table = 'mouse_strain'
    def __unicode__(self):
        return self.mouse_type_name

class Groups(models.Model):
    name = models.CharField(max_length=150)
    creationDate = models.DateField('creation date', blank=True, null=True)
    id_protocol = models.ForeignKey(Protocols, db_column='id_protocol', null=True, blank=True)
    class Meta:
        verbose_name_plural = 'groups'
        db_table = 'groups'
    def __unicode__(self):
        return self.name

class Mice(models.Model):
    id_mouse_strain = models.ForeignKey(Mouse_strain, blank=True, db_column='id_mouse_strain')
    barcode = models.CharField(max_length=32, blank=True, unique=True)
    available_date = models.DateField('available date',blank=True)
    #arrival_date = models.DateField('arrival date',blank=True, db_column='arrival_date')
    arrival_date = models.DateField(db_column='arrival_date')
    birth_date = models.DateField('birth date', blank=True)
    death_date = models.DateField('death date', blank=True)
    gender = models.CharField(max_length=1, choices = GENDERCHOICE)
    id_status = models.ForeignKey(Status, db_column='id_status')
    id_source = models.ForeignKey(Source, db_column='id_source')
    #id_cancer_research_group = models.ForeignKey(Cancer_research_group, db_column='id_cancer_research_group')
    notes = models.CharField(max_length=45, blank=True)

    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername), ))

    class Meta:
        verbose_name_plural = 'phys_mice'
        db_table = 'phys_mice'
    def __unicode__(self):
        return self.barcode
    def report(self):
        page = markup.page()
        page.tr()
        page.td(str(self.barcode), align='center')
        page.td(str(self.birth_date), align='center')
        page.td(str(self.available_date), align='center')
        page.td(str(self.id_mouse_strain), align='center')
        page.td(str(self.gender), align='center')
        page.td(str(self.id_status), align='center')
        page.td(str(self.id_source), align='center')
        page.tr.close()
        return page
    def list_mice(self):
        text = self.barcode   + ", "+ self.gender
        return text
    def __getattribute__(self,name): #ritorna il valore dell'attributo 'name'
        return object.__getattribute__(self, name)

class Mice_audit(models.Model):
    id_mouse_strain = models.ForeignKey(Mouse_strain, blank=True, db_column='id_mouse_strain')
    barcode = models.CharField(max_length=32, blank=True, unique=True)
    available_date = models.DateField('available date',blank=True)
    arrival_date = models.DateField(db_column='arrival_date')
    birth_date = models.DateField('birth date', blank=True)
    death_date = models.DateField('death date', blank=True)
    gender = models.CharField(max_length=1, choices = GENDERCHOICE)
    id_status = models.ForeignKey(Status, db_column='id_status')
    id_source = models.ForeignKey(Source, db_column='id_source')
    notes = models.CharField(max_length=45, blank=True)
    username = models.CharField(blank=True,null=True)
    _audit_timestamp=models.DateTimeField(blank=True,null=True)
    _audit_change_type=models.CharField(blank=True,null=True)

    class Meta:
        verbose_name_plural = 'Mice audit'
        db_table = 'phys_mice_audit'
    def __unicode__(self):
        return self.barcode

class BioMice(models.Model):
    objects=WgObjectManager()
    phys_mouse_id = models.ForeignKey(Mice, blank=True, db_column='phys_mice_id')
    id_genealogy = models.CharField(max_length=45, null=True)
    id_group = models.ForeignKey(Groups, db_column='id_group', null=True,blank=True)
    notes = models.CharField(max_length=45, blank=True, null=True)

    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername), ))

    class Meta:
        verbose_name_plural = 'bio_mice'
        db_table = 'bio_mice'
    def __unicode__(self):
        return self.id_genealogy

    def save(self, *args, **kwargs):
        from django_transaction_signals import defer
        if settings.USE_GRAPH_DB == True and 'admin' not in get_WG():
	    if self.pk is None:
                print "differisco",self.id_genealogy
                defer(add_mice_node,self)
	    else:
	        print "non differisco"
        super(BioMice, self).save(*args, **kwargs)

    def save_old(self, *args, **kwargs):
        super(BioMice, self).save(*args, **kwargs)

class Programmed_explant(models.Model):
    objects=WgObjectRelatedManager()
    id_scope = models.ForeignKey(Scope_details, db_column='id_scope')
    id_mouse = models.ForeignKey(BioMice, db_column='id_mouse')
    done = models.BooleanField()
    scopeNotes = models.TextField(blank=True,null=True)
    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername), ))
    #unique_together = ("id_mouse", "done")
    class Meta:
        verbose_name_plural = 'programmed_explant'
        db_table = 'programmed_explant'


class Explant_details(models.Model):
    objects=WgObjectRelatedManager()
    id_series = models.ForeignKey(Series, db_column='id_series')
    id_mouse = models.ForeignKey(BioMice, db_column='id_mouse')
    class Meta:
        verbose_name_plural = 'explant_details'
        db_table = 'explant_details'

class TissueType(models.Model):
    abbreviation = models.CharField(max_length=3)
    name = models.CharField(max_length=45)
    notes = models.CharField(max_length=150, blank=True)
    class Meta:
        verbose_name_plural='Tissue Types'
        db_table='tissuetype'
    def __unicode__(self):
        return self.name

class Aliquots(models.Model):
    id_explant = models.ForeignKey(Explant_details, null=True,blank=True, db_column='id_explant')
    idType = models.ForeignKey(TissueType, blank=True, null=True,db_column='idType')
    id_genealogy = models.CharField(max_length=45, unique=True)

    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername), ))

    class Meta:
        verbose_name_plural = 'aliquots'
        db_table = 'aliquots'
    def __unicode__(self):
        return self.id_genealogy

    def save(self, *args, **kwargs):
        from django_transaction_signals import defer
        if settings.USE_GRAPH_DB == True and 'admin' not in get_WG():
            if self.pk is not None:
                print "non inserisco nodo, gia' presente"
            else:
                print self
                if self.id_genealogy is not None and self.id_explant is not None and self.pk is None:
                    print "salvo aliquota da espianto nel grafo"
                    defer(add_aliquot_node,self)
                super(Aliquots, self).save(*args, **kwargs)
        else:
            super(Aliquots, self).save(*args, **kwargs)



class Drugs(models.Model):
    name = models.CharField(max_length=45, unique=True)
    description = models.CharField(max_length=255, blank=True)
    linkToDoc = models.TextField(blank=True,null=True)
    safetySheet = models.TextField(blank=True,null=True)
    class Meta:
        verbose_name_plural = 'drugs'
        db_table = 'drugs'
    def __unicode__(self):
        return self.name

class Site(models.Model):
    shortName = models.CharField(max_length = 3, unique=True)
    longName = models.CharField(max_length = 50, unique=True)
    class Meta:
        verbose_name_plural = 'site'
        db_table = 'site'
    def __unicode__(self):
        return self.longName

class Urls(models.Model):
    _url = models.CharField(max_length = 255, unique=True, db_column = 'url')
    default = models.BooleanField()
    class Meta:
        verbose_name_plural = 'urls'
        db_table = 'urls'
    def __unicode__(self):
        return self.url
    @property
    def url(self):
        if str(self._url).startswith('http'):
            return self._url
        else:
            return settings.DOMAIN_URL+self._url

class UrlStorage(models.Model):
    _address = models.CharField(max_length = 255, unique=True, db_column = 'address')
    default = models.BooleanField()
    class Meta:
        verbose_name_plural = 'urlStorage'
        db_table = 'urlstorage'
    def __unicode__(self):
        return self.address
    @property
    def address(self):
        if str(self._address).startswith('http'):
            return self._address
        else:
            return settings.DOMAIN_URL+self._address

class Implant_details(models.Model):
    objects=WgObjectRelatedManager()
    id_mouse = models.ForeignKey(BioMice, db_column = 'id_mouse')
    id_series = models.ForeignKey(Series, db_column = 'id_series')
    aliquots_id = models.ForeignKey(Aliquots, db_column = 'aliquots_id')
    bad_quality_flag = models.BooleanField()
    site = models.ForeignKey(Site, db_column = 'site')

    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername), ))

    class Meta:
        verbose_name_plural = 'implant_details'
        db_table = 'implant_details'

class Qualitative_values (models.Model):
    value = models.CharField(max_length=45, unique=True)
    description = models.CharField(max_length=45,blank=True)
    class Meta:
        verbose_name_plural = 'qualitative_values'
        db_table = 'qualitative_values'
    def __unicode__(self):
      return str(self.value)

class Type_of_measure(models.Model):
    description = models.CharField(max_length=99, unique=True)

    class Meta:
        verbose_name_plural = 'type_of_measure'
        db_table = 'type_of_measure'
    def __unicode__(self):
        return str(self.description)

class Measurements_series(models.Model):
    id_series = models.AutoField(primary_key=True)
    id_operator = models.ForeignKey(User, db_column='id_operator')
    id_type = models.ForeignKey(Type_of_measure, db_column='id_type')
    date = models.DateField('date of measurements series')
    class Meta:
        verbose_name_plural = 'measurements_series'
        db_table = 'measurements_series'
    def __unicode__(self):
        return str(self.id_operator.username)+' '+str(self.date)


class Quantitative_measure(models.Model):
    objects=WgObjectRelatedManager()
    x_measurement = models.FloatField()
    y_measurement = models.FloatField()
    z_measurement = models.FloatField()
    volume = models.FloatField()
    weight = models.FloatField()
    id_mouse = models.ForeignKey(BioMice, db_column = 'id_mouse')
    id_series = models.ForeignKey(Measurements_series, db_column='id_series')
    notes = models.CharField(max_length=255, blank=True)
    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername), ))

    class Meta:
        verbose_name_plural = 'quantitative_measure'
        db_table = 'quantitative_measure'
    def __unicode__(self):
        return str(self.volume)


class Qualitative_measure(models.Model):
    objects=WgObjectRelatedManager()
    id_value = models.ForeignKey(Qualitative_values, db_column='id_value')
    id_mouse = models.ForeignKey(BioMice, db_column = 'id_mouse')
    id_series = models.ForeignKey(Measurements_series, db_column='id_series')
    weight = models.FloatField()
    notes = models.CharField(max_length=255, blank=True)
    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername), ))

    class Meta:
        verbose_name_plural = 'qualitative_measure'
        db_table = 'qualitative_measure'
    def __unicode__(self):
        return str(self.id_value)


TIMECHOICE = (
    ('minutes', 'minutes'),
    ('hours', 'hours'),
    ('days', 'days'),
    ('months', 'months'),
)


class Arms(models.Model):
    name = models.CharField(max_length=45, unique=True)
    description = models.CharField(max_length=255)
    duration = models.IntegerField()
    type_of_time = models.CharField(max_length=7, choices=TIMECHOICE, default='hours')
    forces_explant = models.BooleanField()
    class Meta:
        verbose_name_plural = 'arms'
        db_table = 'arms'
    def __unicode__(self):
        return str(self.name)

class Details_arms(models.Model):
    id_via = models.ForeignKey(Via_mode, db_column='id_via')
    arms_id = models.ForeignKey(Arms, db_column = 'arms_id')
    drugs_id = models.ForeignKey(Drugs, db_column='drugs_id')
    start_step = models.IntegerField()
    end_step = models.IntegerField()
    dose = models.FloatField()
    schedule = models.IntegerField()
    class Meta:
        verbose_name_plural = 'detail_arms'
        db_table = 'detail_arms'
    def __unicode__(self):
        return str(self.schedule)



class Protocols_has_arms(models.Model):
    id_protocol = models.ForeignKey('Protocols', db_column='id_protocol')
    id_arm = models.ForeignKey('Arms', db_column = 'id_arm')
    class Meta:
        verbose_name_plural = 'protocols_has_arms'
        db_table = 'protocols_has_arms'




#tipo di evento in attesa di essere approvato/modificato/rifiutato
#class TypeEvent(models.Model):
#    name = models.CharField(max_length=45, unique=True)
#    class Meta:
#        verbose_name_plural = 'typeEvent'
#        db_table = 'typeevent'
#    def __unicode__(self):
#      return self.name

#status dell'evento: pending/accepted/rejected/modified
class EventStatus(models.Model):
    name = models.CharField(max_length=45, unique=True)
    class Meta:
        verbose_name_plural = 'eventStatus'
        db_table = 'eventstatus'
    def __unicode__(self):
      return self.name

#tabella per raccogliere gli espianti e i trattamenti pending con i riferimenti alle relative misure
class ProgrammedEvent(models.Model):
    objects=WgObjectRelatedManager()
    insertionDate = models.DateTimeField()
    #id_type = models.ForeignKey(TypeEvent, db_column = 'id_type')
    id_mouse = models.ForeignKey(BioMice, db_column = 'id_mouse')
    measureOperator = models.ForeignKey(User, db_column = 'measureOperator')
    id_status = models.ForeignKey(EventStatus, db_column = 'id_status')
    id_quant = models.ForeignKey(Quantitative_measure, db_column = 'id_quant', null = True, blank = True)
    id_qual = models.ForeignKey(Qualitative_measure, db_column = 'id_qual', null = True, blank = True)
    checkDate = models.DateTimeField(blank = True, null = True)
    checkComments = models.TextField(null = True, blank = True)
    checkOperator = models.ForeignKey(User, db_column = 'checkOperator', related_name='check', null = True, blank = True)
    id_parent = models.ForeignKey('self', null=True, db_column='id_parent', blank=True)
    class Meta:
        verbose_name_plural = 'programmedEvent'
        db_table = 'programmedevent'
    def __unicode__(self):
      return self.id_status.name



#gestisce gli espianti pending
class Pr_explant(models.Model):
    id_event = models.ForeignKey(ProgrammedEvent, db_column = 'id_event')
    id_scope = models.ForeignKey(Scope_details, db_column='id_scope')
    scopeNotes = models.TextField(blank=True,null=True)
    class Meta:
        verbose_name_plural = 'pr_explant'
        db_table = 'pr_explant'

#gestisce i trattamenti pending
class Pr_treatment(models.Model):
    id_event = models.ForeignKey(ProgrammedEvent, db_column = 'id_event')
    id_pha = models.ForeignKey(Protocols_has_arms, db_column = 'id_pha')
    expectedStartDate = models.DateTimeField(null = True, blank = True)
    class Meta:
        verbose_name_plural = 'pr_treatment'
        db_table = 'pr_treatment'

class Mice_has_arms(models.Model):
    objects=WgObjectRelatedManager()
    id_mouse = models.ForeignKey(BioMice, db_column = 'id_mouse')
    id_operator = models.ForeignKey(User, db_column='id_operator')
    id_protocols_has_arms = models.ForeignKey(Protocols_has_arms, db_column = 'id_protocols_has_arms')
    id_prT = models.ForeignKey(Pr_treatment, db_column = 'id_prT', blank = True, null = True)
    start_date = models.DateTimeField(blank = True, null = True)
    expected_end_date = models.DateTimeField(blank = True, null = True)
    end_date = models.DateTimeField(blank = True, null = True)
    history = audit.AuditTrail(track_fields=(('username', models.CharField(max_length=30), getUsername), ))

    class Meta:
        verbose_name_plural = 'mice_has_arms'
        db_table = 'mice_has_arms'
    def __unicode__(self):
        return str(self.id_operator)



#gestisce le richieste di stop treatment
class Pr_stopTreatment(models.Model):
    id_event = models.ForeignKey(ProgrammedEvent, db_column = 'id_event')
    id_mha = models.ForeignKey(Mice_has_arms, db_column = 'id_mha')
    stopDate = models.DateTimeField()
    class Meta:
        verbose_name_plural = 'pr_stopTreatment'
        db_table = 'pr_stopTreatment'


class Pr_changeStatus(models.Model):
    id_event = models.ForeignKey(ProgrammedEvent, db_column = 'id_event')
    newStatus = models.ForeignKey(Status,  db_column='newStatus')
    class Meta:
        verbose_name_plural = 'pr_changeStatus'
        db_table = 'pr_changestatus'



'''START WORKING GROUP AREA'''

class WG(models.Model):
    name= models.CharField(max_length=40)
    users = models.ManyToManyField(User, through="WG_User")
    owner= models.ForeignKey(User,related_name="owner_wg_set")

class WG_User(models.Model):
    WG=models.ForeignKey(WG)
    user=models.ForeignKey(User)
    permission=models.ForeignKey(Permission,blank=True, null=True)
    class Meta:
        unique_together = ("WG","user","permission")

'''END WG AREA'''


class BioMice_WG(models.Model):
    biomice=models.ForeignKey(BioMice,db_column='id_mouse')
    WG=models.ForeignKey(WG,db_column='WG_id')
    class Meta:
        db_table = 'biomice_wg'
