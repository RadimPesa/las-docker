from django import forms
from django.db import models
from django.contrib.auth.models import User
from mongoengine import *
import datetime
import json
import re
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
#from mongoengine import EmbeddedDocumentField

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.PasswordInput()
    
class DataSource(models.Model):
    name = models.CharField(max_length=64,unique=True)
    description = models.CharField(max_length=256,null=True,blank=True)
    color = models.CharField(max_length=8,unique=True)
    colorHover = models.CharField(max_length=8,unique=True)
    colorClicked = models.CharField(max_length=8,unique=True)
    iconUrl = models.CharField(max_length=128,unique=True, db_column="icon_url")
    _url = models.CharField(max_length=128,db_column='url')

    @property
    def url(self):
        if str(self._url).startswith('http'):
            return self._url
        else:
            return settings.DOMAIN_URL+self._url

    class Meta:
        verbose_name_plural = 'DataSources'
        db_table = 'DataSource'
    def __unicode__(self):
        return self.name
        
class DSTable(models.Model):
    name = models.CharField(max_length=128)
    dataSource = models.ForeignKey(DataSource, db_column='dataSource_id')
    attrList = models.CharField(max_length=16384)
    primaryKey = models.CharField(max_length=128)
    genId = models.CharField(max_length=128,null=True,blank=True)
    class Meta:
        verbose_name_plural = 'DSTables'
        db_table = 'DSTable'
        unique_together = ('name', 'dataSource')
    def __unicode__(self):
        return ' ['+str(self.dataSource) + '].' + self.name 
        
class DSRelationship(models.Model):
    fromDSTable = models.ForeignKey(DSTable, db_column = 'fromDSTable_id', related_name = 'dsrelationship_from_set')
    toDSTable = models.ForeignKey(DSTable, db_column = 'toDSTable_id', related_name = 'dsrelationship_to_set')
    leftRelatedAttr = models.CharField(max_length=64)
    rightRelatedAttr = models.CharField(max_length=64)
    join_prefix_len = models.IntegerField(null=True, blank=True)
    oneToMany = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'DSRelationships'
        db_table = 'DSRelationship'
        unique_together = ('fromDSTable', 'toDSTable', 'leftRelatedAttr')
    def __unicode__(self):
        return str(self.fromDSTable) + ' => ' + str(self.toDSTable)

class JoinedTable(models.Model):
    fromDSTable = models.ForeignKey('DSTable', db_column='fromDst_id', related_name='from_jndTab_set')
    toDSTable = models.ForeignKey('DSTable', db_column='toDst_id', related_name='to_jndTab_set')
    oneToMany = models.BooleanField(default=False)
    summary = models.CharField(max_length=16384, null=True, blank=True)
    def fillSummary(self):
        jt_dsr = self.joinedtable_has_dsrelationship_set.all().order_by('no')
        summ = []
        for x in jt_dsr:
            summ.append((x.dsr.fromDSTable.name, x.dsr.leftRelatedAttr, x.dsr.toDSTable.name, x.dsr.rightRelatedAttr, x.dsr.join_prefix_len, x.dsr.oneToMany))
        self.summary = json.dumps(summ)
        self.save()
    
    @staticmethod
    def getOrCreateJTWithPath(fromDst, toDst, dsrList):
        # look for joined tables with given source and destination
        jt_list = JoinedTable.objects.filter(fromDSTable=fromDst,toDSTable=toDst)
        # check if one such joined table has the same dsr sequence as the one we need
        found = False
        for x in jt_list:
            #scan list of jnd tabs and for each of those do compare the sequence of dsr's to the current one
            curr_dsr_list = [y.dsr_id for y in x.joinedtable_has_dsrelationship_set.all().order_by('no')]
            if curr_dsr_list == dsrList:
                found = True
                jt = x
                break

        if found == False:
            jt = JoinedTable()
            jt.fromDSTable = fromDst
            jt.toDSTable = toDst
            jt.save()

            oneToMany = True
            for x in dsrList:
                jtdsr = JoinedTable_has_DSRelationship()
                jtdsr.jndTable = jt
                dsr = DSRelationship.objects.get(pk=x)
                jtdsr.dsr = dsr
                jtdsr.no = dsrList.index(x)
                jtdsr.save()
                oneToMany = oneToMany and dsr.oneToMany

            jt.oneToMany = oneToMany
            jt.fillSummary()
            jt.save()

        return jt

    class Meta:
        db_table = 'JoinedTable'
    def __unicode__(self):
        return str(self.fromDSTable) + " -> " + str(self.toDSTable)

class JoinedTable_has_DSRelationship(models.Model):
    jndTable = models.ForeignKey('JoinedTable', db_column='jndTab_id')
    dsr = models.ForeignKey('DSRelationship', db_column='dsr_id')
    no = models.IntegerField(db_column='no')
    class Meta:
        db_table = 'JndTab_has_DSR'
    def __unicode__(self):
        return "[" + str(self.jndTable_id) + "] " + str(self.dsr)

class AutoCompleteAPI(models.Model):
    dsTable = models.ForeignKey(DSTable, db_column='dsTable_id')
    attrName = models.CharField(max_length=64)
    tableName = models.CharField(max_length=128)
    _url = models.CharField(max_length=128,db_column='url')
    
    @property
    def url(self):
        if str(self._url).startswith('http'):
            return self._url
        else:
            return settings.DOMAIN_URL+self._url

    class Meta:
        db_table = 'AutoCompleteAPI'
    def __unicode__(self):
        return str(self.dsTable) + '.' + self.attrName
    def fill_attrs(self):
        from query_api_constants import RUNQUERY_API
        self.tableName = self.dsTable.name
        self._url = self.dsTable.dataSource._url + RUNQUERY_API

class QueryableEntity(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=256,null=True,blank=True)
    dsTable = models.ForeignKey(DSTable, db_column='dsTable_id')
    enabled = models.BooleanField(default=False)
    genid_prefilter = models.BooleanField(default=False, db_column='genid_prefilter')
    isVirtualTable = models.BooleanField(default=False, db_column='isVirtual')
    shareable = models.BooleanField(default=False)
    outputShareable = models.ForeignKey('Output', db_column='output_share',null=True,blank=True)

    class Meta:
        verbose_name_plural = 'QueryableEntities'
        db_table = 'QueryableEntity'
    def __unicode__(self):
        return self.name + ' (based on ' + str(self.dsTable) + ')'

        
class JTAttribute(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=64,null=True,blank=True)
    jndTable = models.ForeignKey('JoinedTable', db_column='jndTab_id')
    attrName = models.CharField(max_length=64)
    attrType = models.ForeignKey('AttributeType', db_column='attrType_id')
    predefList_Dst = models.ForeignKey('DSTable', db_column='predefList_Dst_id', null=True, blank=True, related_name="qefilter_predeflist_set")
    predefList_Attr = models.CharField(max_length=64, null=True, blank=True)
    class Meta:
        db_table = 'JTAttribute'
        #unique_together = ('jndTable', 'attrName', 'attrType')

class AttributeType(models.Model):
    name=models.CharField(max_length=32)
    operator=models.CharField(max_length=64)
    subfilter=models.BooleanField()
    class Meta:
        verbose_name_plural='AttributeTypes'
        db_table='AttributeType'
    def __unicode__(self):
        return self.name

class Filter(models.Model):
    jtAttr = models.ForeignKey('JTAttribute', db_column='jtAttr_id')
    qe = models.ForeignKey('QueryableEntity', db_column='qe_id')
    multiValued = models.BooleanField()
    batchInput = models.BooleanField()
    fileInput = models.BooleanField()
    autocomplete_api = models.ForeignKey(AutoCompleteAPI, db_column='ac_api_id',null=True,blank=True)
    parentFilter = models.ForeignKey('Filter', null=True, blank=True, db_column='parFilt_id')
    parentValue = models.ForeignKey('JTAValue', null=True, blank=True, db_column='parVal_id')
    class Meta:
        db_table = 'Filter'

class JTAValue(models.Model):
    jtAttr = models.ForeignKey('JTAttribute', db_column='jtAttr_id')
    value = models.CharField(max_length=255)
    valueForDisplay = models.CharField(max_length=255,blank=True,null=True)
    hasBeenExcluded = models.BooleanField(default=False)
    class Meta:
        db_table = 'JTAValue'
        unique_together = ('jtAttr', 'value')
    def __unicode__(self):
        return str(self.valueForDisplay) + "(" + str(self.value) + ") [" + str(self.jtAttr) + "]"


class Output(models.Model):
    qe = models.ForeignKey('QueryableEntity', db_column='qe_id')
    name = models.CharField(max_length=64)
    fnName = models.CharField(max_length=128, blank=True, null=True, db_column='fnName')
    summary = models.CharField(max_length=16384, null=True, blank=True)
    class Meta:
        db_table = 'Output'
    def fillSummary(self):
        s = []
        jta = [x.jtAttr for x in self.output_has_jtattribute_set.all().order_by('no')]
        for x in jta:
            s.append((x.jndTable.toDSTable.name, x.attrName, json.loads(x.jndTable.summary), x.id if x.attrType_id == 1 else None))
        self.summary = json.dumps(s)

class Output_has_JTAttribute(models.Model):
    no = models.IntegerField(db_column='no')
    output = models.ForeignKey('Output', db_column='out_id')
    jtAttr = models.ForeignKey('JTAttribute', db_column='jtAttr_id')
    class Meta:
        db_table = 'Out_has_jtAttr'

class QueryPath(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=64,null=True,blank=True)
    fromQEntity = models.ForeignKey('QueryableEntity', db_column = 'fromQEntity_id', related_name = 'querypath_fromQE_set')
    toQEntity = models.ForeignKey('QueryableEntity', db_column = 'toQEntity_id', related_name = 'querypath_toQE_set')
    leftPath = models.ForeignKey('JoinedTable', db_column = 'leftJndTab_id', null=True, blank=True,related_name = 'QueryPath_left_set')
    rightPath = models.ForeignKey('JoinedTable', db_column = 'rightJndTab_id', null=True, blank=True, related_name = 'QueryPath_right_set')
    bridgeDsr = models.ForeignKey('DSRelationship', db_column='bridgeDsr', null=True, blank=True)
    bridgeSummary = models.CharField(max_length=16384)
    oneToMany = models.BooleanField(default=False)
    isDefault = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = 'QueryPaths'
        db_table = 'QueryPath'
    def __unicode__(self):
        return str(self.fromQEntity) + ' to ' + str(self.toQEntity)
    def save(self, *args, **kwargs):
        s = QueryPath.objects.filter(fromQEntity=self.fromQEntity,toQEntity=self.toQEntity,isDefault=True)
        if len(s) == 0 and self.isDefault == False:
        # there must be a default path, so if there's none, set the current one
            self.isDefault == True
        elif self.isDefault == True:
        # only one path can be set as the default one, so if the current one is the default one, then we need to unset the other(s)
            for x in s:
                x.isDefault = False
                x.save()
        if self.bridgeDsr:
            self.bridgeSummary = json.dumps((self.bridgeDsr.fromDSTable.name, self.bridgeDsr.leftRelatedAttr, self.bridgeDsr.toDSTable.name, self.bridgeDsr.rightRelatedAttr, self.bridgeDsr.join_prefix_len, self.bridgeDsr.oneToMany))
        super(QueryPath, self).save(*args, **kwargs)
        

class QueryTemplate(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=256,null=True,blank=True)
    baseQuery = models.TextField()
    configuration = models.TextField()
    parameters = models.TextField(null=True, blank=True)
    valueSubfilterMapping = models.TextField(null=True, blank=True)
    outputEntity = models.ForeignKey(QueryableEntity, db_column = 'outputEntity_id',related_name='querytemplateSet')
    outputBlockId = models.IntegerField(db_column = 'outputBlockId')
    outputsList = models.TextField(db_column = 'outputsList')
    isTranslator = models.BooleanField(db_column = 'isTranslator')
    translatorInputType = models.ForeignKey(QueryableEntity, db_column = 'translatorInputType_id', null=True, blank=True)
    outputTranslatorsList = models.CharField(max_length=256,db_column = 'outputTranslatorsList',null=True,blank=True)
    class Meta:
        db_table = 'QueryTemplate'


class QueryTemplateWG(models.Model):
    queryTemplate = models.ForeignKey('QueryTemplate', db_column = 'qt_id')
    WG=models.ForeignKey('WG', db_column = 'wg_id')
    class Meta:
        db_table = 'QueryTemplateWG'


class QueryTemplate_has_input(models.Model):
    queryTemplate = models.ForeignKey(QueryTemplate, db_column = 'qt_id')
    entity = models.ForeignKey(QueryableEntity, db_column = 'entity_id', related_name = 'templateInputEntity')
    no = models.IntegerField(db_column = 'no')
    blockId = models.IntegerField(db_column = 'blockId')
    inputId = models.IntegerField(db_column = 'inputId')
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256,null=True,blank=True)
    class Meta:
        db_table = 'QueryTemplate_has_input'

class Operator(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=256,null=True,blank=True)
    iconUrl = models.CharField(max_length=128,unique=True, db_column="icon_url")
    numInputs = models.IntegerField()
    configurable = models.BooleanField()
    outTypeDependsOnIn = models.BooleanField(db_column='outFromIn')
    outTypeDependsOnConf = models.BooleanField(db_column='outFromConf')
    canBeFirst = models.BooleanField(db_column='canBeFirst')
    canBeLast = models.BooleanField(db_column='canBeLast')
    no = models.IntegerField()
    class Meta:
        db_table = 'Operator'
    def __unicode__(self):
        return self.name

class GenIDType(models.Model):
    name = models.CharField(max_length=64, db_column='name')
    class Meta:
        db_table = 'GenIDType'
    def __unicode__(self):
        return str(self.name)

class GenIDType_has_Filter(models.Model):
    relatedGenIDType = models.ForeignKey('GenIDType', db_column='gtype_id',null=False,blank=False)
    relatedFilter = models.ForeignKey('Filter', db_column='f_id',null=False,blank=False)
    class Meta:
        db_table = 'GenIDType_has_Filter'


class GenIDFieldType(models.Model):
    name = models.CharField(max_length=64, unique=True)
    class Meta:
        db_table = 'GenIDFieldType'
    def __unicode__(self):
        return str(self.name)

class GenIDField(models.Model):
    name = models.CharField(max_length=64)
    start = models.IntegerField(db_column='start')
    end = models.IntegerField(db_column='end')
    genid_type = models.ForeignKey(GenIDType, db_column='genid_type_id')
    field_type = models.ForeignKey(GenIDFieldType, db_column='field_type_id')
    dsTable = models.ForeignKey(DSTable, db_column='dsTable_id', null=True, blank=True)
    attrName = models.CharField(max_length=64, null=True, blank=True)
    class Meta:
        db_table = 'GenIDField'
    def __unicode__(self):
        return str(self.genid_type) + '.' + str(self.name)

class GenIDFieldValue(models.Model):
    genid_field = models.ForeignKey(GenIDField, db_column='field_id')
    value = models.CharField(max_length=64, db_column='value')
    class Meta:
        db_table = 'GenIDFieldValue'
        unique_together = ('genid_field', 'value')
    def __unicode__(self):
        return str(self.genid_field) + ': ' + str(self.value)

class SavedQuery(models.Model):
    title = models.CharField(max_length=128,null=True,blank=True)
    description = models.CharField(max_length=256,null=True,blank=True)
    graph_nodes = models.TextField()
    author = models.ForeignKey(User)
    timestamp = models.DateTimeField()
    class Meta:
        db_table = 'SavedQuery'
    def __unicode__(self):
        return '[' + str(self.id) + '] ' + str(self.title)

# non-relational models
class QueryRun(Document):
    timestamp = DateTimeField()
    results = FileField()
    translators_results = FileField()
    sort_keys = ListField()
    user = IntField()
    query = ReferenceField('SubmittedQuery')


e = re.compile(r"[()#_\\/\s*.-]")

class SubmittedQuery(Document):
    title = StringField(max_length=128)
    description = StringField(max_length=256)
    query_graph = DictField()
    author = IntField()
    timestamp = DateTimeField() #split
    headers = ListField()
    column_keys = ListField()
    has_translators = BooleanField()
    translators_meta = DictField()
    outputEntityId = IntField()
    runs = ListField(ReferenceField('QueryRun'))

    def __unicode__(self):
        return '[ ' + str(self.author) + ' on ' + str(self.timestamp) + ' ] ' + str(self.title)

    def save(self, *args, **kwargs):
        self.column_keys = [e.sub("", x) for x in self.headers]
        for tid, tdata in self.translators_meta.iteritems():
            tdata['column_keys'] = [e.sub("", x) for x in tdata['headers']]
        super(SubmittedQuery, self).save(*args, **kwargs)

class GenealogyTreeInfo(Document):
    timestamp = DateTimeField()
    user = IntField()
    case = StringField(max_length=9)
    parents = DictField()

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


'''
ADDED FOR GRAPH_DB MANAGEMENT
'''
class WG(models.Model):
    name= models.CharField(max_length=40)
    users = models.ManyToManyField(User, through="WG_User")
    owner= models.ForeignKey(User,related_name="owner_wg_set")
    class Meta:
        db_table = 'wg'

class WG_User(models.Model):
    WG=models.ForeignKey(WG)
    user=models.ForeignKey(User)
    permission=models.ForeignKey(Permission,blank=True, null=True)
    class Meta:
        unique_together = ("WG","user","permission")
        db_table = 'wg_user'

#per LAS permissions
class Member(models.Model):
    class Meta:
        permissions = (
            ("can_view_templates", "Templates"),
            ("can_view_query_generator", "Query generator"),
            ("can_view_query_generator_light", "Query generator light"),
            ("can_view_history", "History"),
            ("can_view_interface_update", "Interface update"),
        )
