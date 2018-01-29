from py2neo import *
from xenopatients.models import * 
from django.conf import settings


def shareData(wgName,usersList):
    enable_graph()
    disable_graph()
    fatherList=set()
    fatherAliquotList=set()
    xList=BioMice.objects.none()
    gdb=neo4j.GraphDatabaseService('http://172.28.9.101:7474/db/data/')
    for name in usersList:
        xList=xList | BioMice.objects.filter(id__in=Explant_details.objects.filter(id_series__in=Series.objects.filter(id_operator=User.objects.get(username=name))).values_list('id_mouse',flat=True)).values_list('id_genealogy',flat=True)
    print 'Found Xeno:',len(xList)
    for x in xList:
        q=neo4j.CypherQuery(gdb,"MATCH (n:Biomouse), (wg:Social) where wg.identifier='"+wgName+"' and n.identifier='"+x+"' MATCH (father)-[:generates]-(n) CREATE UNIQUE (wg)-[r:SharesData {startDate:'"+str(datetime.datetime.now())+"'}]->father return father")
        r=q.execute()
        try:
            fatherList.add(r.data[0][0]['identifier'])
        except:
            print "no padre per",x
    xObjectsList=BioMice.objects.filter(id_genealogy__in=xList)
    wg=WG.objects.get(name=wgName)
    for x in xObjectsList:
        try:
           item=BioMice_WG.objects.get(biomice=x,WG=wg)
        except:
          item=BioMice_WG(biomice=x,WG=wg)
          item.save()

    for x in fatherList:
        try:
            item=BioMice.objects.get(id_genealogy=x)
            try:
                item=BioMice_WG.objects.get(aliquot=Aliquot.objects.get(uniqueGenealogyID=x,WG=wg))
            except:
                item=BioMice_WG(aliquot=x,WG=wg)
                item.save()
        except:
            fatherAliquotList.add(x)

    return fatherAliquotList

