#!/usr/bin/python
# Set up the Django Environment
import sys
sys.path.append('/srv/www/biobank')
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

def Collezioni_storiche():
    try:
        enable_graph()
        disable_graph()
        request=HttpRequest()
        profiling=CollectionProtocol.objects.get(project='ML8713-S54185')
        liscoll=Collection.objects.all()
        gdb = neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)        
        
        k=0
        for coll in liscoll:
            lisexists=[]
            lisnotexists=[]
            lislocalid=[]
            genid=coll.idCollectionType.abbreviation+coll.itemCode+'0000000000000000000'
            print 'genid',genid
            #posso fare il check patient per ogni collezione, cosi' da sapere se quel consenso esiste per quel progetto
            #dopo faccio la POST ad una delle due API a seconda che il consenso esista o meno. Questo lo devo fare per ogni
            #collezione, non posso farlo tutto in una botta sola. Cosi' creo sul grafo il consenso e lo collego alla collezione 
            #che esiste gia'
            #Poi devo fare una nuova scansione delle collezioni e salvare, per quelle che lo hanno, il localid, creando un arco tra
            #consenso e progetto 
            handler=CheckPatientHandler()
            #le collezioni storiche potrebbero non avere un protocollo, cosi' metto profiling
            if coll.idCollectionProtocol==None:
                prot=profiling
            else:
                prot=coll.idCollectionProtocol
                
            #ogni volta devo chiamare la API per sapere quali pazienti ci sono gia' per quel progetto
            hand=LocalIDListHandler()
            dizlocalid=hand.read(request,str(prot.id))
            print 'dizlocalid',dizlocalid
            
            #tolgo il _ eventualmente presente nel consenso cosi' per le collezioni di Bardelli ho il consenso pulito
            #senza numeri sequenziali
            cons=coll.collectionEvent
            print 'cons prima',cons
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
                print 'len',len(cc)
                for jj in range(1,(len(cc)-1)):
                    cons+=cc[jj]+'_'
                cons=cons[0:len(cons)-1]
            print 'cons dopo',cons            
            valore=handler.read(request, cons, coll.patientCode, coll.idSource.id,prot.id)
            print 'val',valore
            #nel valore c'e' scritto se il consenso esiste o no
            ev=valore['event']
            if ev=='new':
                #vuol dire che l'ic non esiste ancora
                #vado sul grafo a prendere il wg che possiede la collezione perche' ho bisogno di sapere un solo wg.
                #Invece nel DB, basandomi sull'utente, avrei una lista di wg
                q=neo4j.CypherQuery(gdb,"MATCH ((n:Collection)-[r:OwnsData]-wg)where n.identifier='"+genid+"' RETURN wg")
                r=q.execute()
                print 'wg',r.data[0][0]['identifier']
                workgr=r.data[0][0]['identifier']
                wgList=[workgr]
                #per l'operatore prendo tutti i samplingevent collegati a serie che abbiano un operatore esplicito e non None, poi li ordino in base
                #alla data e prendo quello piu' vecchio, che e' quello che rappresenta il collezionamento iniziale
                lisserie=Serie.objects.all().exclude(operator='None')
                listasamp=SamplingEvent.objects.filter(idCollection=coll,idSerie__in=lisserie).order_by('samplingDate')
                #ci sono delle collezioni che non hanno sampling collegati, quindi assegno a priori la Zanella
                if len(listasamp)==0:
                    operatore='debby.thomas'
                else:
                    operatore=listasamp[0].idSerie.operator
                    #ci sono ancora due collezionamenti che hanno "torti" come operatore, che pero' non c'e' piu' tra gli utenti
                    #della biobanca
                    if operatore=='davide.torti':
                        operatore='eugenia.zanella'
                print 'oper',operatore
                diztemp={'caso':coll.itemCode,'tum':coll.idCollectionType.abbreviation,'consenso':cons,'progetto':prot.project,'source':coll.idSource.internalName,'wg':[workgr],'operator':operatore}
                lislocal=dizlocalid[prot.id]
                if coll.patientCode in lislocal:
                    diztemp['paziente']=coll.patientCode
                else:
                    diztemp['paziente']=''
                lisnotexists.append(diztemp)                
            else:
                #controllo se c'e' gia' un arco tra questa collezione e il consenso
                q=neo4j.CypherQuery(gdb,"MATCH (n:IC)-[r:belongs]-(c:Collection) where n.icCode='"+cons+"' and c.identifier='"+genid+"' RETURN r")
                rel=q.execute()
                print 'belongs   ',rel.data
                wgList=[]
                #se non c'e', allora dico al modulo clinico di creare l'arco 
                if len(rel)==0:
                    iniziogen=coll.idCollectionType.abbreviation+coll.itemCode
                    #faccio enable e poi disable perche' se facessi subito disable darebbe errore perche' scatena un'eccezione
                    enable_graph()
                    disable_graph()
                    #per avere la lista dei wg, guardo tutte le aliquote di quella collezione e poi prendo i gruppi collegati
                    lisal=Aliquot.objects.filter(uniqueGenealogyID__startswith=iniziogen)
                    print 'lisal',lisal
                    listemp=WG.objects.filter(id__in=Aliquot_WG.objects.filter(aliquot__in=lisal).values_list('WG',flat=True).distinct())                
                    print 'wg list',listemp              
                    for wg in listemp:
                        wgList.append(wg.name)
                    lisexists.append({'caso':coll.itemCode,'tum':coll.idCollectionType.abbreviation,'consenso':cons,'progetto':prot.project,'wg':wgList})
                    localid=valore['idgrafo']
                    lislocalid.append(localid)
            #il wg e l'operatore che passo qui non sono significativi tranne per la parte del wg del localid
            errore=saveInClinicalModule(lisexists,lisnotexists,wgList,'',lislocalid)
            if errore:
                raise Exception
            
            #devo salvare un arco tra nodo paziente e progetto se la collezione ha il
            #codice paziente salvato            
            if coll.patientCode!='' and coll.patientCode!=None:
                paziente=coll.patientCode
                #prendo il nodo paziente partendo dal nodo consenso a cui e' collegato tramite una relazione signed
                q=neo4j.CypherQuery(gdb,"MATCH ((n:IC)-[r:signed]-paz) where n.icCode='"+cons+"' RETURN paz")
                nodopaz=q.execute()              
                if len(nodopaz)>0:
                    #prendo il progetto
                    identifnodopaz=nodopaz.data[0][0]['identifier']
                    #verifico che non ci sia gia' una relazione tra i due nodi
                    q=neo4j.CypherQuery(gdb,"MATCH (n:Patient)-[r:hasAlias]-(proj:Project) where n.identifier='"+identifnodopaz+"' and proj.identifier='"+prot.project+"' RETURN r")
                    relaz=q.execute()
                    print 'relazione esistente',relaz.data
                    #solo se non esiste gia' una relazione tra i due nodi, la creo
                    if len(relaz)==0:
                        q=neo4j.CypherQuery(gdb,"MATCH (n:Patient),(proj:Project) where n.identifier='"+identifnodopaz+"' and proj.identifier='"+prot.project+"' CREATE (n)-[:hasAlias { localId : '"+paziente+"' }]->(proj)")
                        print 'crea localid',q
                        r=q.execute()
            #k=k+1
            #if k==3:
                #break
                
    except Exception,e:
        print 'err',e
    return

if __name__=='__main__':
    Collezioni_storiche()
    
