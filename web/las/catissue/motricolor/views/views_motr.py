from __init__ import *
from catissue.api.handlers import LocalIDListHandler

@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_motricolor')
def collectionMotr1(request):
    try:
        progetto='EORTC 1615 - NKI M16TGA'
        project='EORTC1615'
        if request.method=='POST':
            print request.POST
            form = CollectionMotrForm(request.POST,tipo=project)        
        else:
            form = CollectionMotrForm(tipo=project)
        variables = RequestContext(request, {'form': form,'prog_esteso':progetto,'prog_abbr':project,'tipo':'Motricolor'})   
        return render_to_response('collectionMotr.html',variables)
    except Exception,e:
        print 'errore',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('indexMotr.html',variables)
    
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_motricolor')
def collectionMotr2(request):
    try:
        progetto='EORTC 1616 - NKI M16VIB'
        project='EORTC1616'
        if request.method=='POST':
            print request.POST
            form = CollectionMotrForm(request.POST,tipo=project)        
        else:
            form = CollectionMotrForm(tipo=project)
        variables = RequestContext(request, {'form': form,'prog_esteso':progetto,'prog_abbr':project,'tipo':'Motricolor'})   
        return render_to_response('collectionMotr.html',variables)
    except Exception,e:
        print 'errore',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('indexMotr.html',variables)

@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_motricolor')
def collectionMotr3(request):
    try:
        progetto='EORTC 1604 - VHIO16001'
        project='EORTC1604'
        if request.method=='POST':
            print request.POST
            form = CollectionMotrForm(request.POST,tipo=project)        
        else:
            form = CollectionMotrForm(tipo=project)
        variables = RequestContext(request, {'form': form,'prog_esteso':progetto,'prog_abbr':project,'tipo':'Motricolor'})   
        return render_to_response('collectionMotr.html',variables)
    except Exception,e:
        print 'errore',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('indexMotr.html',variables)

@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_motricolor')
@transaction.commit_manually
def collectionSaveMotr(request):
    if request.method=='POST':
        print request.POST
        print 'Motricolor'
        try:
            if 'final' in request.POST:   
                listaaliq=request.session.get('aliquotCollectionMotricolor')
                print 'listaaliq',listaaliq
                lista,intest=LastPartCollectionMotr(listaaliq)
                variables = RequestContext(request,{'fine2':True,'aliq':lista,'intest':intest})
                return render_to_response('collectionMotr.html',variables)
            if 'salva' in request.POST:
                listaal=[]
                lisbarclashub=[]
                pezziusati=0
                disponibile=1
                derivato=0
                liscasi=[]
                listacoll=[]
                lisexists=[]
                lisnotexists=[]
                lislocalid=[]
                if request.session.has_key('aliquotCollectionMotricolor'):
                    del request.session['aliquotCollectionMotricolor']
                tum=CollectionType.objects.get(abbreviation='CRC')
                tess=TissueType.objects.get(abbreviation='BL')
                protcoll=CollectionProtocol.objects.get(name=request.POST.get('progetto'))
                #creo il plasma
                tipoaliq=AliquotType.objects.get(abbreviation='PL')
                casuale=True
                
                #mi faccio dare la lista dei localid per sapere quali ci sono gia'
                hand=LocalIDListHandler()
                diztemp=hand.read(request,str(protcoll.id))
                lislocalsym=diztemp[protcoll.id]
                print 'lislocalsym',lislocalsym
                
                listaaliq=json.loads(request.POST.get('dati'))
                lcasi=json.loads(request.POST.get('liscasi'))
                print 'lcasi',lcasi
                
                lisconsensi=[]
                for key in lcasi:
                    valch=key.split('|')
                    paz=valch[0]
                    lisconsensi.append(paz+'_'+protcoll.project)
                diztotconsensi=checkListInformedConsent(lisconsensi)
                print 'diztotcons',diztotconsensi
                operatore=request.POST.get('operatore')
                
                #prendo il wg dell'operatore per impostarlo nella collezione
                oper=User.objects.get(username=operatore)
                liswg=WG_User.objects.filter(user=oper)
                
                #se il protocollo e' della Marsoni allora devo mettere in share anche lei per le aliquote
                """liscollinvestig=CollectionProtocolInvestigator.objects.filter(idCollectionProtocol=protcoll)
                trovato=False
                if len(liscollinvestig)!=0:
                    for coll in liscollinvestig:
                        if coll.idPrincipalInvestigator.surname=='Marsoni' and coll.idPrincipalInvestigator.name=='Silvia':
                            trovato=True
                            break
                listawg=[liswg[0].WG.name]
                if trovato:
                    listawg.append('Marsoni_WG')"""
                
                # share with default wg(s)
                defaultSharings =set()

                #for project in CollectionProtocol.objects.filter(title__in=['EORTC1604','EORTC1615','EORTC1616']):
                for wg in protcoll.defaultSharings.all():
                    defaultSharings.add(wg.name)

                print '[Motricolor Collection] defaultSharings ',defaultSharings

                listawg = []
                # add user wg
                # TODO attenzione: questa linea di codice recupera il primo WG da una lista. Non viene gestito il caso in cui un utente appartenga a piu' WG. Sarebbe da rivedere.
                listawg=[liswg[0].WG.name]

                # add default wg(s) to lista wg
                for wg in defaultSharings:
                    if wg not in listawg:
                        listawg.append(wg)
               
               
                print '[Motricolor Collection] listawg ',listawg

                #print 'listawg',listawg
                set_initWG(listawg)
                workingGroup=listawg
                paramnote=ClinicalFeature.objects.get(name='Notes')
                for key in lcasi:                  
                    #chiave e' formata da paziente|data|idsorgente
                    #val e' una lista di dizionari
                    print 'key',key
                    val=listaaliq[key]
                    print 'val',val
                    #per ogni chiave creo una collezione
                    valor=LasHubNewCase(request, casuale, tum.abbreviation)
                    print 'r.text',valor
                    caso=NewCase(valor, casuale, tum)
                    
                    #se il lashub non e' attivo
                    if valor=='not active' and len(liscasi)!=0:
                        #se voglio un valore casuale allora devo andare a vedere se c'e' gia' quel valore nel dizionario
                        if casuale:
                            trovato=False
                            while not trovato:
                                pres=False
                                if caso in liscasi:
                                    #vuol dire che devo ricreare un nuovo caso
                                    caso=NewCase(valor, casuale, tum)
                                    print 'caso nuovo',caso
                                    pres=True
                                #termino il ciclo while perche' non ho trovato doppioni per il codice del caso
                                print 'pres',pres
                                if not pres:
                                    trovato=True
                    #non devo fare lo zfill, il caso arriva gia' su 4 lettere
                    liscasi.append(caso)
                    
                    valch=key.split('|')
                    paz=valch[0]
                    data_coll=valch[1]
                    posto=Source.objects.get(id=valch[2])
                    
                    #val[3] e' il consenso informato
                    cons=paz

                    collez=Collection(itemCode=caso,
                                 idSource=posto,
                                 idCollectionType=tum,
                                 collectionEvent=cons,
                                 patientCode=paz,
                                 idCollectionProtocol=protcoll)
                    print 'collez',collez
                    collez.save()
                    
                    valore=diztotconsensi[paz+'_'+protcoll.project]
                    print 'val',valore
                    if valore==None:
                        #vuol dire che l'ic non esiste ancora
                        diztemp={'caso':collez.itemCode,'tum':collez.idCollectionType.abbreviation,'consenso':collez.collectionEvent,'progetto':collez.idCollectionProtocol.project,'source':collez.idSource.internalName,'wg':workingGroup,'operator':operatore}
                        if paz in lislocalsym:
                            #il paziente esiste gia'
                            diztemp['paziente']=collez.patientCode
                        else:
                            #il paziente inserito non esiste ancora
                            if collez.patientCode=='':
                                #il paziente non e' stato inserito dall'utente, quindi non viene creato niente
                                diztemp['paziente']=''
                            else:
                                #il paziente e' stato inserito
                                diztemp['newLocalId']=collez.patientCode
                        lisnotexists.append(diztemp)
                    else:
                        lisexists.append({'caso':collez.itemCode,'tum':collez.idCollectionType.abbreviation,'consenso':collez.collectionEvent,'progetto':collez.idCollectionProtocol.project,'wg':workingGroup})
                        localid=valore['patientUuid']
                        lislocalid.append(localid)
                    
                    #per il LASHub
                    iniziogen=collez.idCollectionType.abbreviation+collez.itemCode
                    if iniziogen not in listacoll:
                        listacoll.append(iniziogen)
                                        
                    #salvo la serie
                    ser,creato=Serie.objects.get_or_create(operator=operatore,
                                                           serieDate=data_coll)
                    
                    #salvo il campionamento
                    campionamento=SamplingEvent(idTissueType=tess,
                                                 idCollection=collez,
                                                 idSource=posto,
                                                 idSerie=ser,
                                                 samplingDate=data_coll)
                    campionamento.save()
                    print 'camp',campionamento
                    #per dare il contatore al genid dei campioni
                    contatore=1
                    note=''
                    for diz in val:                        
                        barcode=diz['barcode']
                        genid=tum.abbreviation+caso+tess.abbreviation+'H0000000000'+tipoaliq.abbreviation+str(contatore).zfill(2)+'00'
                        contatore+=1
                        print 'genid',genid
                        print 'len gen',len(genid)
                                            
                        a=Aliquot(barcodeID=barcode,
                                  uniqueGenealogyID=str(genid),
                                  idSamplingEvent=campionamento,
                                  idAliquotType=tipoaliq,
                                  timesUsed=pezziusati,
                                  availability=disponibile,
                                  derived=derivato
                                  )
                        print 'a',a

                        a.save()
                        
                        lisbarclashub.append(barcode)
                        
                        volu=float(diz['vol'])
                        #converto da ml a ul
                        vol=volu*1000
                        featvol=Feature.objects.get(idAliquotType=tipoaliq,name='Volume')
                        aliqfeaturevol=AliquotFeature(idAliquot=a,
                                               idFeature=featvol,
                                               value=vol)
                        aliqfeaturevol.save()
                        
                        notealiq=diz['note']
                        #ho gia' fatto un controllo nella schermata verificando che le note, se ci sono, sono tutte uguali all'interno della collezione
                        if notealiq!='':
                            note=notealiq
                        
                        valori=genid+',,,0,'+barcode+','+tipoaliq.abbreviation+',true,'+str(volu)+','+str(posto)+','+str(data_coll)+','+str(paz)+','+note
                        listaal.append(valori)
                        print 'listaaliq',listaal
                        
                    #se ci sono delle note le salvo
                    print 'note',note
                    if note!='':
                        clinfeat=CollectionClinicalFeature(idCollection=collez,
                                                           idSamplingEvent=campionamento,
                                                           idClinicalFeature=paramnote,
                                                           value=note)
                        clinfeat.save()
                        print 'clinfeat',clinfeat
                #per controllare se esistono gia' questi barc
                print 'lisbarc',lisbarclashub
                if len(lisbarclashub)!=0:
                    #faccio una richiesta allo storage per vedere se questi barc esistono gia'
                    url1 = Urls.objects.get(default = '1').url + '/api/check/presence/'
                    val1={'lista':json.dumps(lisbarclashub),'salva':True}
                    print 'url1',url1
                    data = urllib.urlencode(val1)
                    req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u = urllib2.urlopen(url1, data)
                    re = json.loads(u.read())
                    print 're',re
                    res=re['data']
                    print 'res',res
                    if res!='ok':
                        raise ErrorDerived('Error: barcode '+res+' already exists')
                
                request,errore=SalvaInStorageMotr(listaal,request)
                print 'err', errore   
                if errore==True:
                    transaction.rollback()
                    variables = RequestContext(request, {'errore':errore})
                    return render_to_response('indexMotr.html',variables)                                            
                                
                #devo fare gia' il commit perche' devo passare al modulo clinico la collezione, che deve gia' esistere sul grafo
                #altrimenti non si riesce a collegare il nodo collezione con il consenso informato
                transaction.commit()
                #faccio la API al modulo clinico per dirgli di salvare
                errore=saveInClinicalModule(lisexists,lisnotexists,workingGroup,operatore,lislocalid)
                if errore:
                    raise Exception
                
                request.session['aliquotCollectionMotricolor']=listaal
                """email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                msg=['Samples collected:','','N\tPlace\tDate\tPatient code\tBarcode\tVolume(ml)\tNotes']
                for wg in workingGroup:
                    print 'wg',wg
                    email.addMsg([wg], msg)
                    for i in range(0,len(listaal)):
                        info=listaal[i].split(',')
                        email.addMsg([wg],[str(i+1)+'\t'+info[8]+'\t'+info[9]+'\t'+info[10]+'\t'+info[4]+'\t'+info[7]+'\t'+info[11]])
                    #mando l'e-mail a tutti gli appartenenti a quel wg. Saranno poi loro a decidere se volerla o no
                    wgobj=WG.objects.get(name=wg)
                    liswguser=WG_User.objects.filter(WG=wgobj)
                    lisutenti=[]
                    for wgus in liswguser:
                        if wgus.user.username not in lisutenti and wgus.user.username!=operatore:
                            lisutenti.append(wgus.user.username)
                    print 'lisutenti',lisutenti
                    email.addRoleEmail([wg], 'Executor', [operatore])
                    email.addRoleEmail([wg], 'Planner', lisutenti)

                email.send()"""

                print '[Motricolor Collection] sending mail notification (except fake motricolor PI)'
                recipients = {s.email for s in WG.objects.get(name='Motricolor_WG').users.all().distinct() if s.username != 'motricolor'}
                #recipients = ['andrea.mignone@ircc.it']
                subject="[LAS/Motricolor] Collection notification"
                message = 'Dear Users,\n\n\tthe present is to notify the following collection(s):\n\n'
                for a in listaal:
                    info=a.split(',')
                    message += '{0}\t{1}\t{2}\t{3}\n'.format(info[9], info[0], info[4], info[8])
                message += '\n\nBest,\n\n--\nLAS for Motricolor'
                message=message.encode('utf-8')
                email = EmailMessage(subject,message,"",recipients,"","","","","")
                email.send(fail_silently=False)
                print '[Motricolor Collection] mail sent'

                
                transaction.commit()
                return HttpResponse()
        except ErrorDerived as e:
            transaction.rollback()
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore':e.value})
            return render_to_response('collectionMotr.html',variables)
        except Exception,e:
            print 'err',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('indexMotr.html',variables)

def SalvaInStorageMotr(listaaliquota,request):
    listaffpe=''
    listaaliq=''
    listatipialiq=[]
    errore=False
    for i in range(0,len(listaaliquota)):
        val=listaaliquota[i].split(',')
        if val[6]=='false':
            #in val[4] c'e' il barcode della provetta
            listaaliq.append(val[4]+','+val[0]+','+val[9])
            listatipialiq.append(val[5])
        else:
            #in val[5] c'e' il tipo dell'aliq (VT,SF...)
            listaffpe=listaffpe+val[4]+','+val[5]+','+val[0]+','+val[9]+'&'
    print 'listaaliq',listaaliq
    print 'listaffpeeeee',listaffpe
    #per salvare in rna,snap o vitale
    url1 = Urls.objects.get(default = '1').url + "/full/"
    val1={'lista':json.dumps(listaaliq),'tube':'full','tipo':listatipialiq}
    
    try:
        if len(listaaliq)!=0:
            print 'url1',url1
            data = urllib.urlencode(val1)
            req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url1, data)
            res1 =  u.read()
        else:
            res1='ok'
        if len(listaffpe)!=0:
            #per salvare in ffpe,of o ch
            url2 = Urls.objects.get(default = '1').url + "/saveFFPE/"
            val2={'lista':listaffpe,'user':request.user.username}
            print 'url2',url2
            data = urllib.urlencode(val2)
            req = urllib2.Request(url2,data=data, headers={"workingGroups" : get_WG_string()})
            u = urllib2.urlopen(req)
            #u = urllib2.urlopen(url2, data)
            res2 =  u.read()
    except Exception, e: 
        #transaction.rollback()
        errore=True
        variables = RequestContext(request, {'errore':errore})
        return render_to_response('indexMotr.html',variables)
        print e
    if (res1 == 'err')or(len(listaffpe)!=0 and res2=='err'):
        print 'errore'
        #transaction.rollback()
        errore=True
        return request,errore
    return request,errore


def LastPartCollectionMotr(listaaliq):
    lista=[]
    for i in range(0,len(listaaliq)):
        info=listaaliq[i].split(',')
        lista.append(ReportToHtml([i+1,info[8],info[9],info[10],info[4],info[7],info[11]]))
    intest='<th>N</th><th>Place</th><th>Date</th><th>Patient code</th><th>Barcode</th><th>Volume(ml)</th><th>Notes</th>'
    
    print 'lista',lista
    print 'intest',intest
    return lista,intest

