from py2neo import neo4j, node, rel
from django.conf import settings
import numpy as np
import datetime

MAX_ITEMS_IN_BATCH = 250000

neo4j._add_header('X-Stream', 'true;format=pretty')

class TestGraph(object):
    def __init__(self):
        self.gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)

    def _getNodeIds(self, num):
        query_text = "match (n) return id(n) limit { num }"
        query = neo4j.CypherQuery(self.gdb, query_text)
        res = query.execute(num=num)
        return [x[0] for x in res]

    def Test1(self):
        startTime = datetime.datetime.now()

        num_nodes = 100000
        num_labels = 1000

        print "Adding %d labels to %d nodes" % (num_labels, num_nodes)
        print "(# nodes in label ~ Uniform)"

        nodes_in_label = map( lambda x: int(round(x)), np.random.uniform(low=0,high=num_nodes,size=num_labels) )

        cnt = 0        
        wbatch = neo4j.WriteBatch(self.gdb)
        for index, num in enumerate(nodes_in_label):
            print "--adding label_%d to %d nodes" % (index, num)
            wbatch.append_cypher(self._getAddLabelCypher('label_%d' % index), {'num': num})
            cnt += 1
            if cnt == 5:
                wbatch.submit()
                cnt = 0
                wbatch = neo4j.WriteBatch(self.gdb)

        
        endTime = datetime.datetime.now()
        
        print "%d labels added to %d nodes" % (num_labels, num_nodes)
        print endTime - startTime

    def _getAddLabelCypher(self, label):
        return "match (n) with n skip { offset } limit { num } set n:" + label

    def _getReadLabeledNodesCypher(self, label):
        return "match (n:" + label + ") return n.uuid, n.identifier"

    def WriteTest2(self):
        startTime = datetime.datetime.now()

        num_nodes = 1000000
        num_labels = 10000

        print "---------------------------------------------"
        print "Adding %d labels to %d nodes" % (num_labels, num_nodes)
        print "(# nodes in label ~ Zipf)"
        print "---------------------------------------------"
        print ""

        nodes_in_label = map( lambda x: int(round(x if x <= num_nodes else num_nodes)), np.random.zipf(a=1.45,size=num_labels) )
        #nodes_in_label = [num_nodes] * num_labels

        cnt_items = 0        
        wbatch = neo4j.WriteBatch(self.gdb)
        for index, num in enumerate(nodes_in_label):
            print "+ adding label_%d to %d nodes" % (index, num)
            if cnt_items + num > MAX_ITEMS_IN_BATCH:
                tot = 0
                while tot < num:
                    step = min(MAX_ITEMS_IN_BATCH-cnt_items, num-tot)
                    wbatch.append_cypher(self._getAddLabelCypher('label_%d' % index), {'offset': tot, 'num': step})
                    #print self._getAddLabelCypher('label_%d' % index).format(**{' offset ': tot, ' num ': step})
                    print "  - applying to %d nodes" % step
                    tot += step
                    cnt_items += step
                    if cnt_items == MAX_ITEMS_IN_BATCH:
                        wbatch.run()
                        wbatch.clear()
                        cnt_items = 0
                    
            else:
                wbatch.append_cypher(self._getAddLabelCypher('label_%d' % index), {'offset': 0, 'num': num})
                #print self._getAddLabelCypher('label_%d' % index).format(**{' offset ': 0, ' num ': step})
                print "  - applying to %d nodes" % num
                cnt_items += num

        if cnt_items > 0:
            #wbatch.submit()
            wbatch.run()
            cnt_items = 0
            #wbatch = neo4j.WriteBatch(self.gdb)
            wbatch.clear()

        
        endTime = datetime.datetime.now()
        
        print "Done"
        print endTime - startTime


    def ReadTest2(self):

        startTime = datetime.datetime.now()

        num_nodes = 1000000
        num_labels = 10000

        print ""
        print "---------------------------------------------"
        print "Reading labeled nodes"
        print "---------------------------------------------"
        print ""

        cnt = 0
        rbatch = neo4j.ReadBatch(self.gdb)
        for index in range(0, num_labels):
            print "+ reading label_%d" % index
            rbatch.append_cypher(self._getReadLabeledNodesCypher('label_%d' % index))
            cnt += 1
            if cnt == MAX_QUERIES_IN_RBATCH:
                rbatch.submit()
                cnt = 0
                rbatch.clear()

        endTime = datetime.datetime.now()
        
        print "Done"
        print endTime - startTime

