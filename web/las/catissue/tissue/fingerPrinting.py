from __init__ import *
from catissue.tissue.utils import *
from catissue.api.handlers import StorageTubeHandler 

@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_freeze_aliquots')
def NotAvailable(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES
            operatore=request.user
            listafile=request.FILES.getlist('file')
            
            #e' il file con i genid da bloccare e da assegnare al wg
            #nella prima colonna c'e' l'inizio del genid, nella seconda un booleano: false= prendere tutti i campioni che iniziano con quel gen
            #e fermarsi li'. true= prendere i campioni e proseguire all'ingiu' nell'albero fino alle foglie
            f1=listafile[0]
            linee = f1.readlines()
            f1.close()
            print 'linee',linee
            gdb=neo4j.GraphDatabaseService(settings.GRAPH_DB_URL)
            lisaliq=[]
            listopi=[]
            lislinee=[]
            #dizionario con chiave il wg e valore una lista di gen da assegnare a quel wg
            dizaliq={}
            diztopi={}
            dizlinee={}
            primalinea=linee[0].strip().split('\t')
            wg_assegnare=primalinea[0]
            lisgen=[]
            lisflag=[]
            #chiave l'oggetto blockprocedure e valore la lista di genealogy collegati
            diztot={}
            #lista per mantenere l'ordine dei genid del file
            listot=[]

            blockProcBatch = BlockProcedureBatch()

            #se non devo cancellare, ma cambiare di gruppo
            if wg_assegnare.lower()!='delete':

                liswg=WG.objects.filter(name=wg_assegnare)
                print 'liswg',liswg
                if len(liswg)==0:
                    lwg=WG.objects.all()
                    wgstr=''
                    for wg in lwg:
                        wgstr+=wg.name+', '
                    wgstr=wgstr[0:len(wgstr)-2]                
                    raise ErrorDerived('Error: work group "'+wg_assegnare+'" does not exist. Choices are: '+wgstr)
                else:
                    wg_nuovo=liswg[0].name

                blockProcBatch.delete = False
                blockProcBatch.workGroup = WG.objects.get(name=wg_nuovo)
                blockProcBatch.save()

                for i in range(1,len(linee)):
                    lisgenid=[]
                    rbatch = neo4j.ReadBatch(gdb)
                    line=linee[i].strip()
                    if line!='':
                        valori=line.split('\t')
                        genid=valori[0]
                        booleano=valori[1].lower()
                        prosegui=0
                        if booleano=='true':
                            prosegui=1
                        print 'prosegui',prosegui
                        lisgen.append(genid)
                        lisflag.append(valori[1].capitalize())
                        
                        #salvo l'oggetto nel DB
                        blockproc=BlockProcedure(workGroup=wg_nuovo,
                                                 genealogyID=genid,
                                                 extendToChildren=prosegui,
                                                 operator=operatore,
                                                 executionTime=timezone.localtime(timezone.now()),
                                                 blockProcedureBatch=blockProcBatch
                                                )
                        blockproc.save()
                        if prosegui:
                            #prendo tutti i campioni che discendono da quel nodo, dividendoli nei tre tipi di bioentita'. In questo modo prendo tutti i
                            #campioni in questione una volta sola e poi li passo alle altre query per non doverli recuperare ogni volta.
                            query="match (n:Bioentity) where n.identifier=~'"+genid+".*' match (n)-[:generates*0..]->(x:Aliquot) return id(x)"
                            cyquery = neo4j.CypherQuery(gdb,query)
                            result = cyquery.execute()
                            laliquote=[]
                            for r in result:
                                laliquote.append(r[0])
                            
                            query="match (n:Bioentity) where n.identifier=~'"+genid+".*' match (n)-[:generates*0..]->(x:Biomouse) return id(x)"
                            cyquery = neo4j.CypherQuery(gdb,query)
                            result = cyquery.execute()
                            lbiomouse=[]
                            for r in result:
                                lbiomouse.append(r[0])
                            
                            query="match (n:Bioentity) where n.identifier=~'"+genid+".*' match (n)-[:generates*0..]->(x:Cellline) return id(x)"
                            cyquery = neo4j.CypherQuery(gdb,query)
                            result = cyquery.execute()
                            lcell=[]
                            for r in result:
                                lcell.append(r[0])
                            print 'laliq',laliquote
                            #devo partire da un nodo e proseguire fino alle foglie attraverso le relazioni generates. Nello stesso tempo 
                            #salvo gia' la data di fine della relazione di Owns o Share. Questa query mi trova anche le aliquote collegate direttamente alla 
                            #collezione (tipo le linee cellulari) e va bene.
                            #divido in due casi: se c'e' gia' una relazione con il wg nuovo o no                            
                            #Per le aliquote
                            rbatch.append_cypher("match (x) where id(x) in {lis} return distinct x.identifier",{'lis':laliquote})                            
                            #se non c'e' la relazione tra wg nuovo e nodo bio (di solito serve per bloccare). Controllo anche che non ci sia gia' una relazione di share
                            rbatch.append_cypher("match (wg:WG) where wg.identifier='"+wg_nuovo+"' "
                            "match (x) where id(x) in {lis} and not exists((x)-[:OwnsData]-(wg)) with x,wg match (x)-[rel:OwnsData|SharesData]-(work:WG) "
                            "where not(has(rel.endDate)) and work.identifier<>'"+wg_nuovo+"' set rel.endDate='"+str(timezone.localtime(timezone.now()))+"' with x,wg "
                            "where not exists((x)-[:SharesData]-(wg)) create (wg)-[:OwnsData {startDate:'"+str(timezone.localtime(timezone.now()))+"'}]->(x) "
                            "return distinct x.identifier",{'lis':laliquote})
                            #se c'e' la relazione tra wg nuovo e nodo bio (di solito serve per sbloccare)
                            rbatch.append_cypher("match (wg:WG) where wg.identifier='"+wg_nuovo+"' "
                            "match (x)-[r:OwnsData|SharesData]-(wg) where id(x) in {lis} and (exists((x)-[:OwnsData]-(wg)) or exists((x)-[:SharesData]-(wg))) and has(r.endDate) "
                            "set r.endDate=null with x match (x)-[rel:OwnsData]-(work:WG) where work.identifier<>'"+wg_nuovo+"' with x,substring(rel.startDate,0,10) as dat "
                            "match (x)-[rel2:OwnsData|SharesData]-(work2:WG) where not(has(rel2.endDate)) and work2.identifier<>'"+wg_nuovo+"' "
                            "set rel2.endDate='"+str(timezone.localtime(timezone.now()))+"' with x,dat match (x)-[rel3:SharesData]-(work3:WG) where has(rel3.endDate) "
                            "and work3.identifier<>'"+wg_nuovo+"' and substring(rel3.endDate,0,10)=dat set rel3.endDate=null  return distinct x.identifier, work3.identifier",{'lis':laliquote})
                            
                            #Per i topi
                            rbatch.append_cypher("match (x) where id(x) in {lis} return distinct x.identifier",{'lis':lbiomouse})
                            #se non c'e' la relazione tra wg nuovo e nodo bio (di solito serve per bloccare)
                            rbatch.append_cypher("match (wg:WG) where wg.identifier='"+wg_nuovo+"' "
                            "match (x) where id(x) in {lis} and not exists((x)-[:OwnsData]-(wg)) with x,wg match (x)-[rel:OwnsData|SharesData]-(work:WG) "
                            "where not(has(rel.endDate)) and work.identifier<>'"+wg_nuovo+"' set rel.endDate='"+str(timezone.localtime(timezone.now()))+"' with x,wg "
                            "where not exists((x)-[:SharesData]-(wg)) create (wg)-[:OwnsData {startDate:'"+str(timezone.localtime(timezone.now()))+"'}]->(x) "
                            "return distinct x.identifier",{'lis':lbiomouse})
                            #se c'e' la relazione tra wg nuovo e nodo bio (di solito serve per sbloccare)                            
                            rbatch.append_cypher("match (wg:WG) where wg.identifier='"+wg_nuovo+"' "
                            "match (x)-[r:OwnsData|SharesData]-(wg) where id(x) in {lis} and (exists((x)-[:OwnsData]-(wg)) or exists((x)-[:SharesData]-(wg))) and has(r.endDate) "
                            "set r.endDate=null with x match (x)-[rel:OwnsData]-(work:WG) where work.identifier<>'"+wg_nuovo+"' with x,substring(rel.startDate,0,10) as dat "
                            "match (x)-[rel2:OwnsData|SharesData]-(work2:WG) where not(has(rel2.endDate)) and work2.identifier<>'"+wg_nuovo+"' "
                            "set rel2.endDate='"+str(timezone.localtime(timezone.now()))+"' with x,dat match (x)-[rel3:SharesData]-(work3:WG) where has(rel3.endDate) "
                            "and work3.identifier<>'"+wg_nuovo+"' and substring(rel3.endDate,0,10)=dat set rel3.endDate=null  return distinct x.identifier, work3.identifier",{'lis':lbiomouse})
                            
                            #Per le linee
                            rbatch.append_cypher("match (x) where id(x) in {lis} return distinct x.identifier",{'lis':lcell})
                            #se non c'e' la relazione tra wg nuovo e nodo bio (di solito serve per bloccare)
                            rbatch.append_cypher("match (wg:WG) where wg.identifier='"+wg_nuovo+"' "
                            "match (x) where id(x) in {lis} and not exists((x)-[:OwnsData]-(wg)) with x,wg match (x)-[rel:OwnsData|SharesData]-(work:WG) "
                            "where not(has(rel.endDate)) and work.identifier<>'"+wg_nuovo+"' set rel.endDate='"+str(timezone.localtime(timezone.now()))+"' with x,wg "
                            "where not exists((x)-[:SharesData]-(wg)) create (wg)-[:OwnsData {startDate:'"+str(timezone.localtime(timezone.now()))+"'}]->(x) "
                            "return distinct x.identifier",{'lis':lcell})
                            #se c'e' la relazione tra wg nuovo e nodo bio (di solito serve per sbloccare)                            
                            rbatch.append_cypher("match (wg:WG) where wg.identifier='"+wg_nuovo+"' "
                            "match (x)-[r:OwnsData|SharesData]-(wg) where id(x) in {lis} and (exists((x)-[:OwnsData]-(wg)) or exists((x)-[:SharesData]-(wg))) and has(r.endDate) "
                            "set r.endDate=null with x match (x)-[rel:OwnsData]-(work:WG) where work.identifier<>'"+wg_nuovo+"' with x,substring(rel.startDate,0,10) as dat "
                            "match (x)-[rel2:OwnsData|SharesData]-(work2:WG) where not(has(rel2.endDate)) and work2.identifier<>'"+wg_nuovo+"' "
                            "set rel2.endDate='"+str(timezone.localtime(timezone.now()))+"' with x,dat match (x)-[rel3:SharesData]-(work3:WG) where has(rel3.endDate) "
                            "and work3.identifier<>'"+wg_nuovo+"' and substring(rel3.endDate,0,10)=dat set rel3.endDate=null  return distinct x.identifier, work3.identifier",{'lis':lcell})
                                                                                
                        else:
                            #divido in due casi: se c'e' gia' una relazione con il wg nuovo o no
                            #lancio la prima query per avere la lista dei campioni in questione, che poi mi servira' per bloccare i campioni nei vari DB
                            #per le aliquote.
                            rbatch.append_cypher("match (n:Aliquot) where n.identifier=~'"+genid+".*' return distinct n.identifier")
                            #se non c'e' (di solito serve per bloccare)
                            #Prendo tutti i nodi che non hanno una relazione con quel wg (optional match mi restituisce lo stesso i nodi anche se non sono
                            #coinvolti in una relazione). Di questi prendo quelli che hanno owns o shares con altri wg e chiudo le rel e poi creo la nuova
                            #relazione con il nuovo wg
                            rbatch.append_cypher("match (n:Aliquot) where n.identifier=~'"+genid+".*' match (wg:WG) where wg.identifier='"+wg_nuovo+"' "
                            "optional match (n)-[r:OwnsData]-(wg) with n,wg,count(r) as cnt where cnt=0 match (n)-[rel:OwnsData|SharesData]-(work:WG) "
                            "where not(has(rel.endDate)) and work.identifier<>'"+wg_nuovo+"' set rel.endDate='"+str(timezone.localtime(timezone.now()))+"' with n,wg "
                            "where not exists((n)-[:SharesData]-(wg)) create (wg)-[:OwnsData {startDate:'"+str(timezone.localtime(timezone.now()))+"'}]->(n) "
                            " return distinct n.identifier")
                            
                            #se c'e' (in genere e' usato per riabilitare campioni bloccati)                            
                            #Prendo i nodi che hanno una relazione finita con il wg, quindi con la data di fine
                            #e la tolgo. Poi prendo la relazione di owns con il gruppo possessore attuale per avere la data di inizio della rel.
                            #Poi prendo le relazioni di owns e shares ancora aperte con gli altri wg e le chiudo con la data attuale.
                            #Infine prendo gli shares chiusi che hanno una data di chiusura uguale a quella di apertura della relazione di owns tra campione e wg
                            #attuale e li riabilito. Mi faccio restituire una riga con genealogy e wg in modo da salvare poi il dato nel DB.
                            rbatch.append_cypher("match (n:Aliquot) where n.identifier=~'"+genid+".*' match (wg:WG) where wg.identifier='"+wg_nuovo+"' "
                            "match (n)-[r:OwnsData|SharesData]-(wg) where (exists((n)-[:OwnsData]-(wg)) or exists((n)-[:SharesData]-(wg))) and has(r.endDate) set r.endDate=null with n "
                            "match (n)-[rel:OwnsData]-(work:WG) where work.identifier<>'"+wg_nuovo+"' with n,substring(rel.startDate,0,10) as dat "
                            "match (n)-[rel2:OwnsData|SharesData]-(work2:WG) where not(has(rel2.endDate)) and work2.identifier<>'"+wg_nuovo+"' set rel2.endDate='"+str(timezone.localtime(timezone.now()))+"' with n,dat "
                            "match (n)-[rel3:SharesData]-(work3:WG) where has(rel3.endDate) and work3.identifier<>'"+wg_nuovo+"' and "
                            "substring(rel3.endDate,0,10)=dat set rel3.endDate=null  return distinct n.identifier, work3.identifier")
                            
                            #per i topi
                            rbatch.append_cypher("match (n:Biomouse) where n.identifier=~'"+genid+".*' return distinct n.identifier")
                            rbatch.append_cypher("match (n:Biomouse) where n.identifier=~'"+genid+".*' match (wg:WG) where wg.identifier='"+wg_nuovo+"' "
                            "optional match (n)-[r:OwnsData]-(wg) with n,wg,count(r) as cnt where cnt=0 match (n)-[rel:OwnsData|SharesData]-(work:WG) "
                            "where not(has(rel.endDate)) and work.identifier<>'"+wg_nuovo+"' set rel.endDate='"+str(timezone.localtime(timezone.now()))+"' with n,wg "
                            "where not exists((n)-[:SharesData]-(wg)) create (wg)-[:OwnsData {startDate:'"+str(timezone.localtime(timezone.now()))+"'}]->(n) "
                            " return distinct n.identifier")
                            rbatch.append_cypher("match (n:Biomouse) where n.identifier=~'"+genid+".*' match (wg:WG) where wg.identifier='"+wg_nuovo+"' "
                            "match (n)-[r:OwnsData|SharesData]-(wg) where (exists((n)-[:OwnsData]-(wg)) or exists((n)-[:SharesData]-(wg))) and has(r.endDate) set r.endDate=null with n "
                            "match (n)-[rel:OwnsData]-(work:WG) where work.identifier<>'"+wg_nuovo+"' with n,substring(rel.startDate,0,10) as dat "
                            "match (n)-[rel2:OwnsData|SharesData]-(work2:WG) where not(has(rel2.endDate)) and work2.identifier<>'"+wg_nuovo+"' set rel2.endDate='"+str(timezone.localtime(timezone.now()))+"' with n,dat "
                            "match (n)-[rel3:SharesData]-(work3:WG) where has(rel3.endDate) and work3.identifier<>'"+wg_nuovo+"' and "
                            "substring(rel3.endDate,0,10)=dat set rel3.endDate=null  return distinct n.identifier, work3.identifier")
                            
                            #per le linee cellulari
                            rbatch.append_cypher("match (n:Cellline) where n.identifier=~'"+genid+".*' return distinct n.identifier")
                            rbatch.append_cypher("match (n:Cellline) where n.identifier=~'"+genid+".*' match (wg:WG) where wg.identifier='"+wg_nuovo+"' "
                            "optional match (n)-[r:OwnsData]-(wg) with n,wg,count(r) as cnt where cnt=0 match (n)-[rel:OwnsData|SharesData]-(work:WG) "
                            "where not(has(rel.endDate)) and work.identifier<>'"+wg_nuovo+"' set rel.endDate='"+str(timezone.localtime(timezone.now()))+"' with n,wg "
                            "where not exists((n)-[:SharesData]-(wg)) create (wg)-[:OwnsData {startDate:'"+str(timezone.localtime(timezone.now()))+"'}]->(n) "
                            " return distinct n.identifier")
                            rbatch.append_cypher("match (n:Cellline) where n.identifier=~'"+genid+".*' match (wg:WG) where wg.identifier='"+wg_nuovo+"' "
                            "match (n)-[r:OwnsData|SharesData]-(wg) where (exists((n)-[:OwnsData]-(wg)) or exists((n)-[:SharesData]-(wg))) and has(r.endDate) set r.endDate=null with n "
                            "match (n)-[rel:OwnsData]-(work:WG) where work.identifier<>'"+wg_nuovo+"' with n,substring(rel.startDate,0,10) as dat "
                            "match (n)-[rel2:OwnsData|SharesData]-(work2:WG) where not(has(rel2.endDate)) and work2.identifier<>'"+wg_nuovo+"' set rel2.endDate='"+str(timezone.localtime(timezone.now()))+"' with n,dat "
                            "match (n)-[rel3:SharesData]-(work3:WG) where has(rel3.endDate) and work3.identifier<>'"+wg_nuovo+"' and "
                            "substring(rel3.endDate,0,10)=dat set rel3.endDate=null  return distinct n.identifier, work3.identifier")
                                                                                   
                        res = rbatch.submit()
                        print 'res',res
                        #in tre liste diverse ho tutti i genealogy a cui cambiare il wg
                        #Ho il problema che se c'e' un solo elemento mi restituisce una stringa con il gen di quell'elemento. Se ce n'e' piu' di uno
                        #mi da' una lista con dentro i genid
                        
                        #aliquote
                        #prende solo i risultati delle prime due query sul grafo. La terza viene analizzata dopo guardando res[2]
                        for j in range(0,2):
                            if res[j]!=None:
                                print 'res aliq',res[j]
                                if isinstance(res[j], basestring):
                                    lisaliq.append(res[j])
                                    lisgenid.append(res[j])
                                else:
                                    for r in res[j]:
                                        #r[0] e' il genid
                                        lisaliq.append(r[0])
                                        lisgenid.append(r[0])
                        if len(lisaliq)!=0:
                            dizaliq[wg_nuovo]=lisaliq
                        if res[2]!=None:
                            #ho una lista da scandire con per ogni riga il gen e il wg
                            for riga in res[2]:
                                if isinstance(riga, basestring):
                                    #vuol dire che c'e' una riga sola e allora e' gia' una stringa e non un vettore
                                    gen=res[2][0]
                                    wg=res[2][1]                                    
                                else:
                                    gen=riga[0]
                                    wg=riga[1]
                                if wg in dizaliq:
                                    lisgen=dizaliq[wg]
                                else:
                                    lisgen=[]
                                if gen not in lisgen:
                                    lisgen.append(gen)
                                dizaliq[wg]=lisgen
                        #topi
                        for j in range(3,5):
                            if res[j]!=None:
                                print 'res topi',res[j]
                                if isinstance(res[j], basestring):
                                    listopi.append(res[j])
                                    lisgenid.append(res[j])
                                else:
                                    for r in res[j]:
                                        #r[0] e' il genid
                                        listopi.append(r[0])
                                        lisgenid.append(r[0])
                        if len(listopi)!=0:
                            diztopi[wg_nuovo]=listopi
                        if res[5]!=None:
                            #ho una lista da scandire con per ogni riga il gen e il wg
                            for riga in res[5]:
                                if isinstance(riga, basestring):
                                    #vuol dire che c'e' una riga sola e allora e' gia' una stringa e non un vettore
                                    gen=res[5][0]
                                    wg=res[5][1]                                    
                                else:
                                    gen=riga[0]
                                    wg=riga[1]
                                if wg in diztopi:
                                    lisgen=diztopi[wg]
                                else:
                                    lisgen=[]
                                if gen not in lisgen:
                                    lisgen.append(gen)
                                diztopi[wg]=lisgen
                        #linee
                        for j in range(6,8):
                            if res[j]!=None:
                                print 'res linee',res[j]
                                if isinstance(res[j], basestring):
                                    lislinee.append(res[j])
                                    lisgenid.append(res[j])
                                else:
                                    for r in res[j]:
                                        #r[0] e' il genid
                                        lislinee.append(r[0])
                                        lisgenid.append(r[0])
                        if len(lislinee)!=0:
                            dizlinee[wg_nuovo]=lislinee
                        if res[8]!=None:
                            #ho una lista da scandire con per ogni riga il gen e il wg
                            for riga in res[8]:
                                if isinstance(riga, basestring):
                                    #vuol dire che c'e' una riga sola e allora e' gia' una stringa e non un vettore
                                    gen=res[8][0]
                                    wg=res[8][1]                                    
                                else:
                                    gen=riga[0]
                                    wg=riga[1]
                                if wg in dizlinee:
                                    lisgen=dizlinee[wg]
                                else:
                                    lisgen=[]
                                if gen not in lisgen:
                                    lisgen.append(gen)
                                dizlinee[wg]=lisgen
                        diztot[blockproc]=lisgenid
                        listot.append(blockproc)
            else:
                wg_nuovo='delete'

                blockProcBatch.delete = True
                blockProcBatch.save()

                for i in range(1,len(linee)):
                    rbatch = neo4j.ReadBatch(gdb)
                    line=linee[i].strip()
                    #lista per unire tutti i genid trovati sul grafo che iniziano con il valore scritto in questa riga.
                    #non prendo i risultati della query lunga con gli share perche' sono un sottoinsieme degli altri risultati e mi bastano le prime due query
                    lisgenid=[]
                    if line!='':
                        valori=line.split('\t')
                        genid=valori[0]
                        booleano=valori[1].lower()
                        prosegui=0
                        if booleano=='true':
                            prosegui=1
                        print 'prosegui',prosegui
                        lisgen.append(genid)
                        lisflag.append(valori[1].capitalize())
                        
                        #salvo l'oggetto nel DB
                        blockproc=BlockProcedure(workGroup=wg_nuovo,
                                                 genealogyID=genid,
                                                 extendToChildren=prosegui,
                                                 operator=operatore,
                                                 executionTime=timezone.localtime(timezone.now()),
                                                 blockProcedureBatch=blockProcBatch
                                                )
                        blockproc.save()
                        if prosegui:
                            #prendo solo i genid per sapere quali campioni rendere esauriti nel DB. Sul grafo non faccio niente
                            #Per le aliquote
                            rbatch.append_cypher("match (n:Bioentity) where n.identifier=~'"+genid+".*' match (n)-[:generates*0..]->(x:Aliquot) return distinct x.identifier")
                            #Per i topi
                            rbatch.append_cypher("match (n:Bioentity) where n.identifier=~'"+genid+".*' match (n)-[:generates*0..]->(x:Biomouse) return distinct x.identifier")
                            #Per le linee cellulari
                            rbatch.append_cypher("match (n:Bioentity) where n.identifier=~'"+genid+".*' match (n)-[:generates*0..]->(x:Cellline) return distinct x.identifier")
                        else:
                            #Per le aliquote
                            rbatch.append_cypher("match (n:Aliquot) where n.identifier=~'"+genid+".*' return distinct n.identifier")
                            #Per i topi
                            rbatch.append_cypher("match (n:Biomouse) where n.identifier=~'"+genid+".*' return distinct n.identifier")
                            #Per le linee cellulari
                            rbatch.append_cypher("match (n:Cellline) where n.identifier=~'"+genid+".*' return distinct n.identifier")
                        
                        res = rbatch.submit()
                        print 'res',res
                        
                        #aliquote
                        if res[0]!=None:
                            print 'res[0]',res[0]
                            if isinstance(res[0], basestring):
                                lisaliq.append(res[0])
                                lisgenid.append(res[0])
                            else:
                                for r in res[0]:
                                    #r[0] e' il genid
                                    lisaliq.append(r[0])
                                    lisgenid.append(r[0])
                        if len(lisaliq)!=0:
                            dizaliq[wg_nuovo]=lisaliq
                        #topi
                        if res[1]!=None:
                            print 'res[1]',res[1]
                            if isinstance(res[1], basestring):
                                listopi.append(res[1])
                                lisgenid.append(res[1])
                            else:
                                for r in res[1]:
                                    #r[0] e' il genid
                                    listopi.append(r[0])
                                    lisgenid.append(r[0])
                        if len(listopi)!=0:
                            diztopi[wg_nuovo]=listopi
                        #linee
                        if res[2]!=None:
                            print 'res[2]',res[2]
                            if isinstance(res[2], basestring):
                                lislinee.append(res[2])
                                lisgenid.append(res[2])
                            else:
                                for r in res[2]:
                                    #r[0] e' il genid
                                    lislinee.append(r[0])
                                    lisgenid.append(r[0])
                        if len(lislinee)!=0:
                            dizlinee[wg_nuovo]=lislinee
                            
                        diztot[blockproc]=lisgenid
                        listot.append(blockproc)
                       
            print 'wg nuovo',wg_nuovo                        
            print 'lisaliq',lisaliq
            print 'listopi',listopi
            print 'lislinee',lislinee
            print 'dizaliq',dizaliq
            print 'diztopi',diztopi
            print 'dizlinee',dizlinee
            print 'diztot',diztot
            
            #prendo le posizioni dei campioni
            lgen=''
            lis_pezzi_url=[]
            dizgen={}
            for gen in lisaliq:
                lgen+=gen+'&'
                if len(lgen)>2000:
                    lis_pezzi_url.append(lgen)
                    lgen=''
            if lgen=='':
                lis_pezzi_url.append('')
            else:
                lis_pezzi_url.append(lgen)
            
            for parti in lis_pezzi_url:
                if parti!='':
                    storbarc=StorageTubeHandler()
                    res=storbarc.read(request, parti, 'admin')                
                    diz = json.loads(res['data'])                    
                    print 'diz',diz
                    dizgen = dict(dizgen.items() + diz.items())
            
            print 'dizgen',dizgen
            
            #salvo nel DB
            listareport=[]
            listamail=[]
            indice=1
            for proc in listot:                
                lisgen=diztot[proc]
                print 'lisgen',lisgen
                if len(lisgen)!=0:
                    for gen in lisgen:
                        blockbioent=BlockBioentity(idBlockProcedure=proc,
                                                   genealogyID=gen)
                        blockbioent.save()
                        freezer=''
                        rack=''
                        platepos=''
                        plate=''
                        tubepos=''
                        barc=''
                        if gen in dizgen:
                            lisvalori=dizgen[gen]
                            print 'lisvalori',lisvalori
                            val=lisvalori.split('|')
                            freezer=str(val[5])
                            rack=str(val[4])
                            platepos=str(val[3])
                            plate=str(val[2])
                            tubepos=str(val[1])
                            barc=str(val[0])
                        extend=False
                        if proc.extendToChildren:
                            extend=True
                        listareport.append(ReportToHtml([indice,gen,freezer,rack,platepos,plate,tubepos,barc,proc.genealogyID,extend,proc.workGroup]))
                        listamail.append(str(indice)+'\t'+str(gen)+'\t'+freezer+'\t'+rack+'\t'+platepos+'\t'+plate+'\t'+tubepos+'\t'+barc+'\t'+str(proc.genealogyID)+'\t'+str(extend)+'\t'+str(proc.workGroup))
                        indice+=1
            
            if len(dizaliq.keys())!=0:
                #lista di genid per sapere se i vecchi wg di quell'aliquota sono gia' stati cancellati
                cancwg=[]
                for workg,lisgen in dizaliq.items():
                    disable_graph()
                    laliq=Aliquot.objects.filter(uniqueGenealogyID__in=lisgen)
                    enable_graph()
                    listemp=[]
                    if workg=='delete':
                        for al in laliq:
                            print 'al',al
                            #allo storage comunico di eliminare solo le aliquote che erano ancora disponibili
                            if al.availability==1:
                                listemp.append(al.uniqueGenealogyID)
                            al.availability=0
                            al.save()                            
                        
                        #mi collego allo storage per svuotare le provette contenenti le aliq
                        #esaurite
                        address=Urls.objects.get(default=1).url
                        url = address+"/full/"
                        print 'url',url
                        values = {'lista' : json.dumps(listemp), 'tube': 'empty','canc':True}
                        data = urllib.urlencode(values)
                        req = urllib2.Request(url,data=data, headers={"workingGroups" : 'admin'})
                        urllib2.urlopen(req)
                    else:
                        #ho una lista di aliquote a cui devo cambiare il wg
                        wgnuovo=WG.objects.get(name=workg)
                        for al in laliq:
                            print 'al',al
                            #solo se l'aliquota non e' ancora in lista cancello i vecchi wg. Altrimenti non li tolgo piu' perche'
                            #cancellerei anche i wg che ho salvato io al ciclo prima con un altro wg
                            if al.uniqueGenealogyID not in cancwg:
                                #prendo i wg attuali
                                listaAlWg=Aliquot_WG.objects.filter(aliquot=al)
                                for lalwg in listaAlWg:                    
                                    #cancello i wg attuali
                                    lalwg.delete()
                            #assegno le aliquote al nuovo wg
                            if Aliquot_WG.objects.filter(aliquot=al,WG=wgnuovo).count()==0:
                                m2m=Aliquot_WG(aliquot=al,WG=wgnuovo)
                                m2m.save()
                            #nuovowg,creato=Aliquot_WG.objects.get_or_create(aliquot=al,
                            #                   WG=wgnuovo)
                            #print 'nuovowg',nuovowg
                            cancwg.append(al.uniqueGenealogyID)
            if len(diztopi.keys())!=0:
                servizio=WebService.objects.get(name='Xeno')
                url=Urls.objects.get(idWebService=servizio).url
                url=url+'/api.changeWGBiomice/' 
                #diztopi ha come chiave il wg e come valore una lista di gen di topi
                val2={'genid':json.dumps(diztopi)}
                print 'url',url
                print 'val2',val2
                data1 = urllib.urlencode(val2)
                req = urllib2.Request(url,data=data1, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                res =  json.loads(u.read())
                print 'res topi',res['data']
                if res['data']=='error':
                    raise Exception
            
            if len(dizlinee.keys())!=0:
                #prendo il servizio CellLineGeneration che punta alla url di base del modulo delle linee 
                servizio=WebService.objects.get(name='CellLineGeneration')
                url=Urls.objects.get(idWebService=servizio).url
                url=url+'/api/changeWGCellLine/'
                #dizlinee ha come chiave il wg e come valore una lista di gen
                val2={'genid':json.dumps(dizlinee)}
                print 'url',url
                print 'val2',val2
                data1 = urllib.urlencode(val2)
                req = urllib2.Request(url,data=data1, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                res =  json.loads(u.read())
                print 'res linee',res['data']
                if res['data']=='error':
                    raise Exception
            
            if len(listamail)!=0:
                liswg=WG.objects.filter(id__in=WG_User.objects.filter(user=operatore).values_list('WG',flat=True).distinct())
                email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                msg=['Genotype mismatch','','Aliquots:','N\tGenealogy ID\tFreezer\tRack\tPlate pos.\tPlate\tTube pos.\tBarcode\tGen. ID (file)\tExtend to children\tWork group']                    
                #prendo tutti i wg dell'utente che ha lanciato la procedura. Non segrego in base ai wg perche' qui, se sono nel caso in cui assegno al
                #QC_Inspector, non avrei nessun utente che gli appartiene e quindi non partirebbe l'e-mail. Invece a me serve che parta sempre. 
                print 'listamail',listamail
                print 'liswg',liswg
                for val in liswg:
                    email.addMsg([val.name], msg)
                    email.addMsg([val.name],listamail)
                    email.addRoleEmail([val.name], 'Executor', [request.user.username])
                    print 'email', email
                try:
                    email.send()
                except Exception, e:
                    print 'err e-mail:',e
                    pass
                    
            variables = RequestContext(request,{'fine':True,'listaliq':listareport})
            return render_to_response('tissue2/freeze_aliquots.html',variables)
        
        variables = RequestContext(request)
        return render_to_response('tissue2/freeze_aliquots.html',variables)
    except ErrorDerived as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        variables = RequestContext(request, {'errore':e.value})
        return render_to_response('tissue2/freeze_aliquots.html',variables)
    except Exception,e:
        print 'err',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('tissue2/index.html',variables)

