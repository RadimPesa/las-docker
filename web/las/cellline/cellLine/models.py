from django.db import models
from django.contrib.auth.models import User, Permission
from django.conf import settings
from py2neo import neo4j, cypher, node, rel
from django_transaction_signals import defer
from global_request_middleware import *
import pylibmc,json,urllib,urllib2
import datetime
from django.db import transaction
from django.core.mail import EmailMessage
from cellLine.genealogyID import *



'''
ADDED FOR GRAPH_DB MANAGEMENT
'''
class WG(models.Model):
    name= models.CharField(max_length=40)
    users = models.ManyToManyField(User, through="WG_User")
    owner= models.ForeignKey(User,related_name="owner_wg_set")
    class Meta:
        db_table = 'cellline_wg'

class WG_User(models.Model):
    WG=models.ForeignKey(WG)
    user=models.ForeignKey(User)
    permission=models.ForeignKey(Permission,blank=True, null=True)
    class Meta:
        unique_together = ("WG","user","permission")
        db_table = 'cellline_wg_user'

class Cell_WG(models.Model):
    cell=models.ForeignKey('Cells',db_column='id_cell')
    WG=models.ForeignKey(WG,db_column='WG_id')
    class Meta:
        db_table = 'cells_wg'

class WgObjectManager(models.Manager):
    def get_query_set(self):
        if settings.USE_GRAPH_DB==True and 'admin' not in get_WG():
            groups=get_WG()
            qs=Cell_WG.objects.filter(WG__name__in=list(groups)).values_list('cell__id')#
            return super(WgObjectManager, self).get_query_set().filter(id__in=qs)
        else:
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
            qs=Cell_WG.objects.filter(WG__name__in=list(groups)).values_list('cell__id')
            return super(WgObjectRelatedManager, self).get_query_set().filter(cells_id__in=qs)
        else:
            return super(WgObjectRelatedManager, self).get_query_set()

    def all_old(self):
        return super(WgObjectRelatedManager, self).get_query_set()

    def get_old(self, *args, **kwargs):
        return super(WgObjectRelatedManager, self).get_query_set().get(*args, **kwargs)

    def filter_old(self, *args, **kwargs):
        return super(WgObjectRelatedManager, self).get_query_set().filter(*args, **kwargs)

    def count_old(self):
        return super(WgObjectRelatedManager, self).get_query_set().count()


# Aliquots
class Aliquots(models.Model):
    gen_id = models.CharField(max_length=26, unique=True)
    archive_details_id = models.ForeignKey('Archive_details',db_column='archive_details_id', null=True, blank=True)
    experiment_details_id = models.ForeignKey('Experiment_details',db_column='experiment_details_id', null=True, blank=True)
    def __unicode__(self):
        return self.gen_id
    def __str__(self):
        return self.gen_id
    class Meta:
        verbose_name_plural = 'Aliquots'
        db_table = 'aliquots'

    def save(self, *args, **kwargs):
        from django_transaction_signals import defer
        if settings.USE_GRAPH_DB == True and 'admin' not in get_WG():
            if self.pk is None:
                print "saving on graph ",self.gen_id
                defer(add_aliquot_node, self)
        super(Aliquots, self).save(*args, **kwargs)

class Allowed_values(models.Model):
    allowed_value = models.CharField(max_length=45)
    condition_feature_id =  models.ForeignKey('Condition_feature', db_column='condition_feature_id')

    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name
    class Meta:
        unique_together = ("allowed_value", "condition_feature_id")
        verbose_name_plural = 'Allowed_values'
        db_table = 'allowed_values'

class Archive_details(models.Model):
    experiment_in_vitro_id = models.ForeignKey('Experiment_in_vitro', db_column='experiment_in_vitro_id', null=True,blank=True )
    events_id = models.ForeignKey('Events', db_column='events_id')
    amount = models.IntegerField()
    application_date = models.DateTimeField(null=True, blank=True)
    def __unicode__(self):
        return str(self.events_id.cell_details_id)+' '+str(self.application_date)    
    class Meta:
        verbose_name_plural = 'Archive_details'
        db_table = 'archive_details'

# Cell Line
class Cells(models.Model):
    objects=WgObjectManager()
    genID = models.CharField(max_length=26)
    nickname = models.CharField(max_length = 45, unique=True, blank=True, null=True)
    nickid = models.CharField(max_length = 5, blank=True, null=True)
    #cancer_research_group_id = models.ForeignKey('Cancer_research_group', db_column='cancer_research_group_id')
    expansion_details_id = models.ForeignKey('Expansion_details', db_column='expansion_details_id', null=True, blank=True)
    #aliquots_id = models.ForeignKey('Aliquots', db_column='aliquots_id',null=True, blank=True)
    def __unicode__(self):
        return self.genID + ' ' +self.nickname
    def __str__(self):
        return self.genID + ' ' +self.nickname
    class Meta:
        verbose_name_plural = 'Cells'
        db_table = 'cells'


    def save(self, *args, **kwargs):
        from django_transaction_signals import defer
        if settings.USE_GRAPH_DB == True and 'admin' not in get_WG():
            if self.pk is None:
                print "saving on graph ",self.genID
                defer(add_cell_node, self)
        super(Cells, self).save(*args, **kwargs)

class Cell_details(models.Model):
    objects=WgObjectRelatedManager()
    num_plates = models.IntegerField()
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField(null=True, blank=True)
    cells_id = models.ForeignKey('Cells', db_column='cells_id')
    condition_configuration_id = models.ForeignKey('Condition_configuration', db_column='condition_configuration_id')
    generation_user = models.ForeignKey(User, db_column='generation_user_id', blank=True, null=True)
    
    def __unicode__(self):
        return self.cells_id.genID
    class Meta:
        verbose_name_plural = 'Cell_details'
        db_table = 'cell_details'

class Cell_details_feature(models.Model):
    cell_details_id = models.ForeignKey('Cell_details', db_column='cell_details_id')
    feature_id = models.ForeignKey('Feature', db_column='feature_id')
    start_date_time = models.DateTimeField(null=True, blank=True)
    end_date_time = models.DateTimeField(null=True, blank=True, default=None)
    operator_id = models.ForeignKey(User, db_column='operator_id', blank=True, null=True)
    value = models.CharField(max_length=100, blank=True,null=True)
    
    def __unicode__(self):
        return str(self.cell_details_id)+' '+str(self.feature_id)
    class Meta:
        verbose_name_plural = 'Cell details feature'
        db_table = 'cell_details_feature'


class Cells_has_aliquots(models.Model):
    objects=WgObjectRelatedManager()
    aliquots_id = models.ForeignKey('Aliquots', db_column='aliquots_id')
    cells_id = models.ForeignKey('Cells', db_column='cells_id')
    def __unicode__(self):
        return str(self.aliquots_id) + ' ' + str(self.cells_id)
    def __str__(self):
        return str(self.aliquots_id) + ' ' + str(self.cells_id)
    class Meta:
        verbose_name_plural = 'Cells_has_aliquots'
        db_table = 'cells_has_aliquots'

class Condition_configuration(models.Model):
    version = models.IntegerField()
    condition_protocol_id =  models.ForeignKey('Condition_protocol', db_column='condition_protocol_id')
    def __unicode__(self):
        return self.condition_protocol_id.protocol_name + '_' + str(self.version)
    def __str__(self):
        return self.condition_protocol_id.protocol_name + '_' + str(self.version)
    class Meta:
        verbose_name_plural = 'Condition_configuration'
        db_table = 'condition_configuration'
        
class Condition_feature(models.Model):
    name = models.CharField(max_length=30)
    unity_measure = models.CharField(max_length=10, null=True, blank=True)
    default_value = models.CharField(max_length=45, null=True, blank=True)
    condition_protocol_element_id =  models.ForeignKey('Condition_protocol_element', db_column='condition_protocol_element_id', null=True, blank=True)

    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Condition_feature'
        db_table = 'condition_feature'

class Condition_has_experiments(models.Model):
    end_time = models.DateTimeField(null=True,blank=True)
    start_time = models.DateTimeField()
    experiment_in_vitro_id = models.ForeignKey('Experiment_in_vitro', db_column='experiment_in_vitro_id', null=True,blank=True )
    condition_configuration_id = models.ForeignKey('Condition_configuration', db_column='condition_configuration_id')

    #non sapevo che mettere
    def __unicode__(self):
        return self.start_time
    def __str__(self):
        return self.start_time
    class Meta:
        verbose_name_plural = 'Condition_has_experiments'
        db_table = 'conditions_has_experiments'
   
class Condition_has_feature(models.Model):
    value = models.CharField(max_length=80, null=True, blank=True)
    condition_feature_id = models.ForeignKey('Condition_feature', db_column='condition_feature_id')
    condition_configuration_id = models.ForeignKey('Condition_configuration', db_column='condition_configuration_id')
    start = models.IntegerField()
    end = models.IntegerField()
    def __unicode__(self):
        return self.value
    def __str__(self):
        return self.value
    class Meta:
        verbose_name_plural = 'Condition_has_feature'
        db_table = 'condition_has_feature'

class Condition_protocol(models.Model):
    protocol_name = models.CharField(max_length=255, unique=True)
    creation_date_time = models.DateTimeField()
    file_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.protocol_name
    def __str__(self):
        return self.protocol_name
    class Meta:
        verbose_name_plural = 'Condition_protocol'
        db_table = 'condition_protocol'

#Protocol
class Condition_protocol_element(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.TextField(null=True, blank=True)
    condition_protocol_element_id = models.ForeignKey('self', db_column='condition_protocol_element_id', null=True, blank=True)

    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Condition_protocol_element'
        db_table = 'condition_protocol_element'

class Eliminated_details(models.Model):
    events_id = models.ForeignKey('Events', db_column='events_id')
    amount = models.IntegerField()
    def __unicode__(self):
        return str(self.events_id)    
    class Meta:
        verbose_name_plural = 'Eliminated_details'
        db_table = 'eliminated_details'

# Expansion
class Expansion_details(models.Model):
    events_id = models.ForeignKey('Events', db_column='events_id')
    input_area = models.IntegerField()
    output_area = models.IntegerField()
    reduction_factor = models.IntegerField()
    def __unicode__(self):
        return ' event_id= '+ str(self.events_id)+' inp area: '+str(self.input_area)
    def __str__(self):
        return ' event_id= '+ str(self.events_id)+' inp area: '+str(self.input_area)
    class Meta:
        verbose_name_plural = 'Expansion_details'
        db_table = 'expansion_details'

# Experiment details
class Experiment_details(models.Model):
    events_id = models.ForeignKey('Events', db_column='events_id', unique=True)
    amount = models.IntegerField()
    #univoco finche non ci saranno altri campi
    def __unicode__(self):
        return self.events_id.cell_details_id.cells_id.genID+' amount:'+str(self.amount)    
    class Meta:
        verbose_name_plural = 'Exepriment_details'
        db_table = 'experiment_details'

# Experiment in Vitro
class Experiment_in_vitro(models.Model):
    objects=WgObjectRelatedManager()
    genID = models.CharField(max_length=26)
    experiment_details_id = models.ForeignKey('Experiment_details', db_column='experiment_details_id')
    cells_id = models.ForeignKey('Cells', db_column='cells_id')
    barcode_container = models.CharField(max_length=45)
    position = models.CharField(max_length=45)
    is_exausted = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    def __unicode__(self):
        return self.experiment_details_id
    def __str__(self):
        return self.experiment_details_id
    class Meta:
        verbose_name_plural = 'Experiment_in_vitro'
        db_table = 'experiment_in_vitro'

#Events
class Events(models.Model):
    date_time_event = models.DateTimeField()
    cellline_users_id = models.ForeignKey(User, db_column='cellline_users_id')
    type_event_id =  models.ForeignKey('Type_events', db_column='type_event_id')
    cell_details_id =  models.ForeignKey('Cell_details', db_column='cell_details_id')

    def __unicode__(self):
        return str(self.cell_details_id.cells_id.genID)
    class Meta:
        unique_together = ("date_time_event", "cellline_users_id", "type_event_id", "cell_details_id")
        verbose_name_plural = 'Events'
        db_table = 'events'

class External_request(models.Model):
    data = models.TextField()
    done = models.BooleanField(default=False)
    action = models.CharField(max_length=80)
    username = models.CharField(max_length=80,blank=True,null=True)
    assigner = models.CharField(max_length=80)
    date_time = models.DateTimeField()
    deleteTimestamp=models.DateTimeField('Delete Timestamp',blank=True,null=True)
    deleteOperator=models.ForeignKey(User, db_column='deleteOperator',related_name='id_deleteOperator',verbose_name='Delete Operator',blank=True,null=True)
    def __unicode__(self):
        return self.data
    def __str__(self):
        return self.data
    class Meta:
        verbose_name_plural = 'external_request'
        db_table = 'external_request'

class Feature(models.Model):
    name=models.CharField(max_length=30)
    class Meta:
        verbose_name_plural='Features'
        db_table='feature'
    def __unicode__(self):
        return self.name

class Instrument(models.Model):
    name = models.CharField(max_length = 45, unique=True)
    code = models.IntegerField(null=True,blank=True)
    manufacturer = models.CharField(max_length = 45, null=True,blank=True)
    description =  models.TextField(null=True,blank=True)

    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Instrument'
        db_table = 'instrument'

class Measure_details(models.Model):
    events_id = models.ForeignKey('Events', db_column='events_id', unique=True)

    def __unicode__(self):
        return self.events_id
    def __str__(self):
        return self.events_id
    class Meta:
        verbose_name_plural = 'Measure_details'
        db_table = 'measure_details'
        
class Measure_event_has_measure_type(models.Model):
    value = models.FloatField(null=True, blank=True)
    datasheet = models.CharField(max_length = 45, null=True, blank=True)
    measure_details_id = models.ForeignKey('Measure_details', db_column='measure_details_id')
    measure_id = models.ForeignKey('Measure_type', db_column='measure_id')
    experiment_in_vitro_id = models.ForeignKey('Experiment_in_vitro', db_column='experiment_in_vitro_id', null=True,blank=True )


    def __unicode__(self):
        return self.value
    def __str__(self):
        return self.value
    class Meta:
        verbose_name_plural = 'Measure_event_has_measure_type'
        db_table = 'measure_event_has_measure_type'

class Measure_type(models.Model):
    name = models.CharField(max_length = 45)
    unity_measure = models.CharField(max_length = 45)
    instrument_id = models.ForeignKey('Instrument', db_column='instrument_id')
    cell_destroy =     models.BooleanField(default=False)

    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name
    class Meta:
        unique_together = ("name", "unity_measure", "instrument_id", "cell_destroy")
        verbose_name_plural = 'Measure_type'
        db_table = 'measure_type'

#per il momento non usato.
class Selection_protocol(models.Model):
    name = models.CharField(max_length = 45, unique=True)
    datasheet = models.CharField(max_length = 30)

    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Selection_protocol'
        db_table = 'selection_protocol'

#per il momento non usato.
class Selection_details(models.Model):
    experiment_in_vitro_id = models.ForeignKey(Experiment_in_vitro, db_column='experiment_in_vitro_id', null=True,blank=True )
    selection_protocol_id = models.ForeignKey(Selection_protocol, db_column='selection_protocol_id', null=True,blank=True )
    aliquots_id = models.ForeignKey(Aliquots, db_column='aliquots_id')
    events_id = models.ForeignKey(Events, db_column='events_id')

    def __unicode__(self):
        return self.experiment_in_vitro_id
    def __str__(self):
        return self.experiment_in_vitro_id
    #class Meta:
        #verbose_name_plural = 'Selection_details'
        #db_table = 'selection_details'

class Type_events(models.Model):
    type_name = models.CharField(max_length=45, unique=True)

    def __unicode__(self):
        return self.type_name
    def __str__(self):
        return self.type_name
    class Meta:
        verbose_name_plural = 'Type_events'
        db_table = 'type_event'

class Url(models.Model):
    _url = models.CharField(max_length = 255, unique=True, db_column = 'url')
    available = models.BooleanField()
    id_webservice = models.ForeignKey('WebService', db_column='id_webservice')
    class Meta:
        verbose_name_plural = 'url'
        db_table = 'url'
    def __unicode__(self):
        return self.url
    @property
    def url(self):
        if str(self._url).startswith('http'):
            return self._url
        else:
            return settings.DOMAIN_URL+self._url

# URL TABLE
class Urls_handler(models.Model):
    name = models.CharField(max_length=30, unique=True)
    _url = models.CharField(max_length=255, db_column = 'url')
    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Urls_handler'
        db_table = 'urls_handler'
    @property
    def url(self):
        if str(self._url).startswith('http'):
            return self._url
        else:
            return settings.DOMAIN_URL+self._url

class WebService(models.Model):
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'webservice'
        db_table = 'webservice'
    def __unicode__(self):
        return self.name



def setLabels(nodeType, altype):
    labels = []
    alTypes = {'VT':'Viable', 'SF':'SnapFrozen', 'RL':'RNALater', 'D':'DNA', 'FF':'FormalinFixed', 'PL': 'PlasmaIsolation', 'OF': 'OCTFrozen', 'SI': 'SerumIsolation', 'CH':'ChinaBlack', 'PX':'PAXtube', 'R':'RNA', 'D':'DNA', 'P':'Protein', 'cR':'cRNA', 'cD':'cDNA'}
    if nodeType == 'Biomouse':
        labels = ['Bioentity', 'Biomouse']
    elif nodeType == 'Cellline':
        labels = ['Bioentity', 'Cellline']
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
    elif nodeType == 'Cellline':
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
        father_gen_id = None
        app = ''
        disable_graph()
        if aliquot.experiment_details_id:
            father_gen_id=aliquot.experiment_details_id.events_id.cell_details_id.cells_id.genID
            app = 'experimentCell'
        elif aliquot.archive_details_id:
            father_gen_id=aliquot.archive_details_id.events_id.cell_details_id.cells_id.genID
            app = 'archiveCell'
        app = 'bank'
        if father_gen_id == None:
            print 'No father'
            raise Exception ('no father cellline')

        enable_graph()
        groupsToSend=list()
        gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
        if gdb.get_indexed_node('node_auto_index','identifier',aliquot.gen_id):
            return
        else:
            batch = neo4j.WriteBatch(gdb)

            nodes = {}

            g = GenealogyID(aliquot.gen_id)
            altype = 'c'+g.get2Derivation() if g.is2Derivation() else g.getArchivedMaterial()
            dateAl = datetime.datetime.now()
            nodes[g.getGenID()] = {'type':'Aliquot', 'altype': altype, 'id':aliquot.id, 'relationships':{}, 'nodeid': None, 'date':str(dateAl)}

            nodes[father_gen_id] = {'type':'Cellline', 'nodeid': None, 'wg':{}, 'relationships':{}}
            nodes[father_gen_id]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',father_gen_id)


            query="START n=node:node_auto_index(identifier='"+father_gen_id+"') match (w:WG)-[r]->n WHERE not has(r.endDate) RETURN id(r), type(r), w.identifier, id(w)"
            data, metadata = cypher.execute(gdb, query)
            if len(data)>0:
                for d in data:
                    nodes[father_gen_id]['wg'][d[0]] = {'nodeid':  gdb.get_indexed_node('node_auto_index','identifier',d[2]), 'rel_type': d[1], 'name':d[2]}

            #relsWg = list(graph_db.match(end_node=nodes[father_gen_id]['nodeid']), rel_type="OwnsData") # e i paramteri associati? e i nodi attaccati?
            fatherNode = nodes[father_gen_id]

            nodes[g.getGenID()]['relationships'][father_gen_id] = {'type': 'generates', 'app':app}

            buildSemanticNode(g.getGenID(), 'Aliquot', None, nodes, dateAl)

            batch = neo4j.WriteBatch(gdb)

            for n, nInfo in nodes.items():
                flagInsert = True
                if nInfo['nodeid'] is None:
                    nInfo['nodeid'] = batch.create(node(identifier=n))
                    labels = setLabels(nInfo['type'], nInfo['altype'])
                    batch.add_labels(nInfo['nodeid'], *labels)
                    if nInfo['type'] in ['Biomouse', 'Aliquot', 'Collection', 'Cellline']:
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
        message='Error saving genid: ',str(aliquot.gen_id)
        toList=list()
        email = EmailMessage(subject,message,'',toList,[],'','','',[])
        #email.send(fail_silently=False)

    address = Urls_handler.objects.get(name = 'biobank').url
    url = address + "/api/saveWgAliquot/"
    h=''
    groupsToSend = [ wgInfo['name'] for wg, wgInfo in fatherNode['wg'].items() ]
    values = {'api_key' : h, 'genid':aliquot.gen_id,'wgList':json.dumps(groupsToSend) }
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
def add_cell_node(cell):
    try:
        gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
        if gdb.get_indexed_node('node_auto_index','identifier',cell.genID):
            return
        else:
            print "inizio aggiunta cell", cell.genID
            g = GenealogyID(cell.genID)
            dateCell = datetime.datetime.now()

            nodes = {}

            app = ''
            fatherNodes = []

            nodes[cell.genID] = {'type':'Cellline', 'altype': None, 'id':cell.id,  'relationships':{}, 'nodeid': None, 'date':str(dateCell)}


            if cell.expansion_details_id:
                print 'Expansion'
                fatherNodes.append(cell.expansion_details_id.events_id.cell_details_id.cells_id.genID)
                father_gen_id = fatherNodes[0]
                app = 'expansion'
                nodes[father_gen_id] = {'type':'Cellline', 'nodeid': None, 'wg':{}, 'relationships':{}, 'alType': None}
                nodes[father_gen_id]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',father_gen_id)
                nodes[g.getGenID()]['relationships'][father_gen_id] = {'type': 'generates', 'app':app}

            else:
                if int (g.getSamplePassage() ) > 1:
                    app = 'thawing'
                else:
                    app = 'cellGeneration'
                print app
                print cell
                print Cells_has_aliquots.objects.filter(cells_id = cell)
                disable_graph()
                als = Aliquots.objects.filter(id__in = (Cells_has_aliquots.objects.filter(cells_id = cell).values_list('aliquots_id')))
                enable_graph()
                print als
                for a in als:
                    fatherNodes.append(a.gen_id)
                    nodes[a.gen_id] = {'type':'Cellline', 'nodeid': None, 'wg':{}, 'relationships':{}, 'alType': None}
                    nodes[a.gen_id]['nodeid'] = gdb.get_indexed_node('node_auto_index','identifier',a.gen_id)
                    nodes[g.getGenID()]['relationships'][a.gen_id] = {'type': 'generates', 'app':app}

            # get WG relationships
            print 'fatherNodes', fatherNodes
            father_list = ' '.join(x for x in fatherNodes)
            print 'father_list', father_list
            query = "START n=node:node_auto_index('identifier:("+ father_list  +")') match (w:WG)-[r]->n WHERE not has(r.endDate) RETURN  DISTINCT  type(r), w.identifier, id(w)"
            fatherNodeWG = {}
            data, metadata = cypher.execute(gdb, query)
            if len(data)>0:
                i = 0
                for d in data:
                    fatherNodeWG[i] = {'nodeid': gdb.get_indexed_node('node_auto_index','identifier',d[1]), 'rel_type': d[0], 'name':d[1]}
                    i+=1


            buildSemanticNode(g.getGenID(), 'Cellline', None, nodes, dateCell)

            batch = neo4j.WriteBatch(gdb)

            for n, nInfo in nodes.items():
                if nInfo['nodeid'] is None:
                    print n, nInfo
                    nInfo['nodeid'] = batch.create(node(identifier=n))
                    labels = setLabels(nInfo['type'], nInfo['altype'])
                    batch.add_labels(nInfo['nodeid'], *labels)
                    if nInfo['type'] in ['Cellline' ,'Biomouse', 'Aliquot', 'Collection']:
                        for wg, wgInfo in fatherNodeWG.items():
                            batch.create( rel( wgInfo['nodeid'], wgInfo['rel_type'], nInfo['nodeid'], {'startDate': nInfo['date'], 'endDate':None} ) )


            for dest, destInfo in nodes.items():
                for source, relInfo in destInfo['relationships'].items():
                    if relInfo['app']:
                        batch.create( rel( nodes[source]['nodeid'], relInfo['type'], destInfo['nodeid'], {'app': relInfo['app']} ) )
                    else:
                        batch.create( rel( nodes[source]['nodeid'], relInfo['type'], destInfo['nodeid'] ) )

            results = batch.submit()
            batch.clear()


            ## To change more than one father
            for wg, wgInfo in fatherNodeWG.items():
                print wg, wgInfo
                if Cell_WG.objects.filter(cell=cell,WG=WG.objects.get(name=wgInfo['name'])).count()==0:
                    m2m=Cell_WG(cell=cell,WG=WG.objects.get(name=wgInfo['name']))
                    m2m.save()

    except Exception,e:
        print e
        transaction.rollback()
        if Cell_WG.objects.filter(cell=cell,WG=WG.objects.get(name='Bertotti_WG')).count()==0:
            m2m=Cell_WG(cell=cell,WG=WG.objects.get(name='Bertotti_WG'))
            m2m.save()
        subject='ERROR DURING SAVING CELL IN GRAPH DB'
        message='Error saving genid :', str(cell.genID)
        toList=list()
        email = EmailMessage(subject,message,'',toList,[],'','','',[])
        email.send(fail_silently=False)

    return
