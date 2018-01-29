#!/usr/bin/python
# Set up the Django Environment
import sys
import site
import os
site.addsitedir('~/.virtualenvs/venvdj1.4/local/lib/python2.7/site-packages')
sys.path.append('/srv/www/biobank')
activate_env=os.path.expanduser("~/.virtualenvs/venvdj1.4/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

from django.core.management import setup_environ 
import settings
setup_environ(settings)
from catissue.tissue.models import *
from catissue.tissue.utils import *
from catissue.api.handlers import *
from django.http import HttpRequest
from py2neo import neo4j

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

#serve per creare gli archi hasAlias tra paziente e progetto per le collezioni che ancora non ce l'hanno
def Collezioni_storiche():
    try:
        enable_graph()
        disable_graph()
        profiling=CollectionProtocol.objects.get(project='Profiling')
        liscoll=Collection.objects.all()
        gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)        
        print 'liscoll',liscoll
        k=0
        for coll in liscoll:
            #per ogni collezione, se ha il codice paziente, guardo se esiste gia' l'arco tra paziente e protocollo. Se non c'e' lo creo 
            if coll.patientCode!='' and coll.patientCode!=None:
                #le collezioni storiche potrebbero non avere un protocollo, cosi' metto profiling
                if coll.idCollectionProtocol==None:
                    prot=profiling
                else:
                    prot=coll.idCollectionProtocol
            
                #tolgo il _ eventualmente presente nel consenso, cosi' per le collezioni di Bardelli ho il consenso pulito
                #senza numeri sequenziali
                cons=coll.collectionEvent
                #print 'cons prima',cons
                cc=cons.split('_')
                #ricreo il consenso con tutte le parti tranne l'ultima 
                ctemp=cc[0]+'_'
                for kk in range(1,(len(cc)-1)):
                    ctemp+=cc[kk]+'_'
                ctemp=ctemp[0:len(ctemp)-1]
                
                #solo se l'ultimo valore del vettore e' un numero intero, altrimenti non tocco niente
                #se la prima parte del cons e' uguale al cod paziente, vuol dire che sono collezioni storiche che ho caricato dando al consenso
                #la forma codpaziente_casocasuale. Allora devo togliere l'ultima parte con le 4 lettere casuali
                if RepresentsInt(cc[len(cc)-1]) or ctemp==coll.patientCode:
                    cons=cc[0]+'_'
                    #print 'len',len(cc)
                    for jj in range(1,(len(cc)-1)):
                        cons+=cc[jj]+'_'
                    cons=cons[0:len(cons)-1]
                print 'cons dopo',cons
                print 'coll',coll
                #per la data prendo tutti i samplingevent della collezione e poi li ordino in base
                #alla data e prendo quello piu' vecchio, che e' quello che rappresenta il collezionamento iniziale
                listasamp=SamplingEvent.objects.filter(idCollection=coll).order_by('samplingDate')
                #ci sono delle collezioni che non hanno sampling collegati, quindi assegno a priori la Zanella
                if len(listasamp)==0:
                    print 'collezione senza sampling',coll
                    d=timezone.localtime(timezone.now())
                else:
                    data =str(listasamp[0].samplingDate).split('-')
                    d=datetime.datetime(int(data[0]),int(data[1]),int(data[2]))
                    print 'd',d                
                            
                #devo salvare un arco tra nodo paziente e progetto
                paziente=coll.patientCode
                print 'paziente',paziente
                #prendo il nodo paziente partendo dal nodo consenso a cui e' collegato tramite una relazione signed
                q=neo4j.CypherQuery(gdb,"MATCH ((n:IC)-[r:signed]-paz) where n.icCode='"+cons+"' RETURN paz")
                nodopaz=q.execute()              
                #print 'nodopaz',nodopaz
                if len(nodopaz)>0:
                    #prendo il progetto
                    identifnodopaz=nodopaz.data[0][0]['identifier']
                    #print 'identifnodopaz',identifnodopaz
                    #verifico che non ci sia gia' una relazione tra i due nodi
                    q=neo4j.CypherQuery(gdb,"MATCH (n:Patient)-[r:hasAlias]-(proj:Project) where n.identifier='"+identifnodopaz+"' and proj.identifier='"+prot.project+"' RETURN r")
                    relaz=q.execute()
                    print 'relazione esistente',relaz.data
                    #solo se non esiste gia' una relazione tra i due nodi, la creo
                    if len(relaz)==0:
                        q=neo4j.CypherQuery(gdb,"MATCH (n:Patient),(proj:Project) where n.identifier='"+identifnodopaz+"' and proj.identifier='"+prot.project+"' CREATE (n)-[:hasAlias { localId : '"+paziente+"', startDate : '"+str(d)+"' }]->(proj)")
                        print 'crea localid',q
                        #q.execute()
                        k=k+1
                #if k==3:
                    #break
        print 'k',k
    except Exception,e:
        print 'err',e
    return

if __name__=='__main__':
    Collezioni_storiche()
    
