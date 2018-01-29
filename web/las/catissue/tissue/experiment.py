from __init__ import *

from catissue.tissue.utils import *
from catissue.api.handlers import StorageTubeHandler
from catissue.tissue.position import ExecPositionVitalAliquots

#serve per la schermata in cui, dati dei genid o dei barcode di campioni derivati, l'
#utente puo' diminuirne il volume 
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_plan_experiments'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_plan_experiments')
def DecreaseView(request):
    assignUsersList=[]
    addressUsersList=[]
    if settings.USE_GRAPH_DB == True:
        for g in get_WG():
            assignUsersDict={}
            assignUsersDict['wg']=WG.objects.get(name=g)
            assignUsersDict['usersList']=list()
            for u in User.objects.filter(~Q(username='admin')&~Q(first_name='')).filter(id__in=WG_User.objects.filter(user__is_active=1,WG__name=g,permission__codename=get_functionality()).values_list("user",flat=True)).order_by('last_name'):
                assignUsersDict['usersList'].append(u)
            assignUsersList.append(assignUsersDict)
        for g in WG.objects.all():
            addressUsersDict={}
            addressUsersDict['wg']=g
            addressUsersDict['usersList']=list()
            for u in User.objects.filter(~Q(username='admin')&~Q(first_name='')).filter(id__in=WG_User.objects.filter(user__is_active=1,WG=g,permission__codename=get_functionality()).values_list("user",flat=True)).order_by('last_name'):
                addressUsersDict['usersList'].append(u)
            addressUsersList.append(addressUsersDict)
    else:
        assignUsersDict={}
        assignUsersDict['wg']=''
        assignUsersDict['usersList']=list()
        for u in User.objects.filter(~Q(username='admin')&~Q(first_name='')&Q(is_active=1)).order_by('last_name'):
            assignUsersDict['usersList'].append(u)
        assignUsersList.append(assignUsersDict)
        addressUsersList.append(assignUsersDict)

    if request.method=='POST':
        print request.POST
        form=VolumeForm(request.POST)
        try:
            #e' il form iniziale in cui scelgo la data e l'esperimento e le note
            if 'fase1' in request.POST:
                esp=request.POST.get('experiment')
                esper=Experiment.objects.get(id=esp)
                uten=request.POST.get('utente')
                dat=request.POST.get('date').strip()
                wg=request.POST.get('idWG')
                commenti=request.POST.get('notes').strip().replace(' ','%20')
                variables = RequestContext(request, {'form':form,'valido':'True','espe':esp,'uten':uten,'data':dat,'note':commenti,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList,'wg':wg})
                if esper.name=='MicroArray':
                    return render_to_response('tissue2/update/exp_microarray.html',variables)
                else:
                    return render_to_response('tissue2/update/update_volume.html',variables)
                      
            if 'salva' in request.POST:
                listaaliq=json.loads(request.POST.get('dati'))
                dat=request.POST.get('dat')
                exp=request.POST.get('exp')
                operat=request.POST.get('operat')
                note=request.POST.get('note')
                wg=request.POST.get('workg')
                lisgen=[]
                listot=[]
                if len(listaaliq)!=0:
                    for val in listaaliq:
                        print 'val',val
                        ch=val.split('|')
                        if ch[0] not in lisgen:
                            try:
                                vv=str(float(ch[4])-float(ch[7]))
                            except:
                                vv=''
                            aggiorna=AggiornaVolume(gen=ch[0],
                                                barcode=ch[1],
                                                position=ch[2],
                                                concattuale=ch[3],
                                                volattuale=ch[4],
                                                volpreso=ch[5],
                                                quantpresa=ch[6],
                                                volequiv=vv,
                                                volfinale=ch[7])
                            print 'aggiorna',aggiorna
                        
                            lisgen.append(ch[0])
                            listot.append(aggiorna)
                            print 'lisgen',listot
                print 'lista esperimenti',listot
                request.session['genealogyesperimenti']=lisgen
                request.session['aliqesperimenti']=listot
                request.session['datesperim']=dat
                request.session['expesperim']=exp
                request.session['operatesperim']=operat
                request.session['noteesperim']=note
                request.session['workgesperim']=wg
                return HttpResponse()   
            
            #ho cliccato sul tasto 'add file'
            if 'aggiungi_file' in request.POST:
                if 'file' in request.FILES:
                    lista_dati=request.session.get('aliqesperimenti')
                    listagentot=request.session.get('genealogyesperimenti')
                    esp=request.session.get('expesperim')
                    print 'esp',esp
                    dat=request.session.get('datesperim').strip()
                    commenti=request.session.get('noteesperim').strip()
                    wg=request.session.get('workgesperim')
                    utente=request.session.get('operatesperim').strip()
                    print 'utente',utente
                    print 'valido'
                    
                    listacolonne=['GenealogyID','Barcode','Schedule Volume(ul)','Schedule Quantity(ug)']
                    dizio={}
                    
                    f=request.FILES['file']
                    for a in f.chunks():
                        #c e' un vettore e in ogni posto c'e' una riga del file
                        c=a.split('\n')
                        #print 'c',c[0]
                        #la prima riga contiene l'intestazione del file e mi serve
                        #per capire come sono messi i valori all'interno
                        val_primariga=c[0].strip().split('\t')
                        k=0
                        for titoli in val_primariga:
                            if titoli!='':
                                dizio[titoli]=k
                                k=k+1
                        print 'dizio',dizio
                        stringalinee=''
                        dizvol={}
                        dizquant={}
                        #parto da 1 perche' la prima riga contiene l'intestazione
                        for i in range(1,len(c)):
                            vvv=c[i].strip()
                            if vvv!='':
                                riga_fin=c[i].split('\t')
                                #devo capire dove si trova il genid e il barcode
                                indicegen=dizio[listacolonne[0]]
                                indicebarc=dizio[listacolonne[1]]
                                indicevol=dizio[listacolonne[2]]
                                indicequant=dizio[listacolonne[3]]
                                print 'indicegen',indicegen
                                print 'riga_fin',riga_fin
                                gen=riga_fin[indicegen].strip()                            
                                barc=riga_fin[indicebarc].strip()
                                volu=riga_fin[indicevol].strip()
                                quantit=riga_fin[indicequant].strip()
                                print 'gen',gen
                                print 'barc',barc
                                if gen!='':
                                    stringalinee+=gen+'&'
                                    dizvol[gen]=volu
                                    dizquant[gen]=quantit
                                else:
                                    stringalinee+=barc+'&'
                                    dizvol[barc]=volu
                                    dizquant[barc]=quantit
                                    
                        stringtot=stringalinee[:-1]     
                        diz=AllAliquotsContainer(stringtot)
                        for genealogy in diz:
                            lista=diz[genealogy]
                            if len(lista)==0:
                                raise ErrorDerived('Error: aliquot '+genealogy+' does not exist in storage')
                            else:
                                if lista not in lista_dati:
                                    #lista_dati.append(lista)
                                    #e' una lista in cui ogni valore e' una stringa formata da gen|barcode|posizione
                                    for val in lista:
                                        print 'val',val
                                        ch=val.split('|')
                                        gen=ch[0]
                                        barc=ch[1]
                                        pos=ch[2]
                                        if gen not in listagentot:
                                            listagentot.append(gen)
                                            laliq=Aliquot.objects.filter(uniqueGenealogyID=gen,availability=1)
                                            if len(laliq)==0:
                                                raise ErrorDerived('Error: aliquot '+gen+' does not exist in storage')
                                            else:
                                                aliq=laliq[0]
                                                print 'aliq',aliq
                                                #guardo se l'aliquota puo' essere collegata a quell'esperimento
                                                esperim=Experiment.objects.get(id=esp)
                                                aliqexp=AliquotTypeExperiment.objects.filter(idExperiment=esperim,idAliquotType=aliq.idAliquotType)
                                                
                                                if aliqexp.count()==0:
                                                    raise ErrorDerived('Error: aliquot '+gen+' with barcode "'+barc+'" is not supported by experiment chosen')
                                                
                                                #controllo se e' un esperimento di generazione o scongelamento linee e se si' devo controllare che
                                                #il tipo di aliq sia coerente
                                                gg=GenealogyID(gen)
                                                vettore=gg.getSampleVector()
                                                print 'vettore',vettore
                                                if esperim.name=='CellLineGeneration' and (vettore=='S' or vettore=='A' or vettore=='O'):
                                                    raise ErrorDerived('Error: aliquot '+gen+' with barcode "'+barc+'" is not supported by experiment chosen')
                                                if esperim.name=='CellLineThawing' and (vettore!='S' and vettore!='A' and vettore!='O'):
                                                    raise ErrorDerived('Error: aliquot '+gen+' with barcode "'+barc+'" is not supported by experiment chosen')
                                                                                
                                                alexpsched=AliquotExperiment.objects.filter(idAliquot=aliq,confirmed=0,deleteTimestamp=None)
                                                if(alexpsched.count()!=0):
                                                    raise ErrorDerived('Error: aliquot '+gen+' with barcode "'+barc+'" is already scheduled for this procedure. Please first confirm past action.')
                                                
                                                concval=''
                                                volval=''
                                                volum=''
                                                quant=''
                                                vol_finale=''
                                                vol_temp=''
                                                #booleano per capire se il campione puo' avere un volume o meno
                                                volume=False
                    
                                                #prendo le feature dell'aliquota
                                                lconc=Feature.objects.filter(name='Concentration',idAliquotType=aliq.idAliquotType)
                                                lvol=Feature.objects.filter(name='Volume',idAliquotType=aliq.idAliquotType)
                                                if len(lconc)!=0:
                                                    
                                                    lisconc=AliquotFeature.objects.filter(Q(idAliquot=aliq)&Q(idFeature=lconc[0]))
                                                    #se il derivato non ha conc e vol viene salvato nel DB -1. Quindi cambio -1
                                                    #con None
                                                    if len(lisconc)!=0:
                                                        if lisconc[0].value==-1:
                                                            concval='None'
                                                        else:
                                                            concval=str(lisconc[0].value)
                                                if len(lvol)!=0:
                                                
                                                    lisvol=AliquotFeature.objects.filter(idAliquot=aliq,idFeature=lvol[0])
                                                    if len(lisvol)!=0:
                                                        if lisvol[0].value==-1:
                                                            volval='None'
                                                        else:
                                                            volval=str(lisvol[0].value)
                                                            print 'voll',volval
                                                            volume=True
                                                
                                                #vuol dire che il campione e' prima da rivalutare e quindi
                                                #non si puo' proseguire in questa schermata
                                                if volval=='None' or concval=='None':
                                                    raise ErrorDerived('Error: Aliquot volume is not defined. Please first revalue aliquot '+gen+' with barcode "'+barc+'"')
                                                if volume:
                                                    if dizvol.has_key(gen):
                                                        volum=dizvol[gen]
                                                        quant=dizquant[gen]
                                                    elif dizvol.has_key(barc):
                                                        volum=dizvol[barc]
                                                        quant=dizquant[barc]
                                                    #questo caso ce l'ho quando inserisco una piastra e voglio avere tutti i suoi figli
                                                    elif dizvol.has_key(genealogy):
                                                        volum=dizvol[genealogy]
                                                        quant=dizquant[genealogy]
                                                        
                                                    print 'volu',volum
                                                    print 'quant',quant
                                                
                                                
                                                    if volum!='' and quant!='':
                                                        raise ErrorDerived('Error: You can only insert either volume or quantity taken. Please correct value for aliquot '+gen+' with barcode "'+barc+'"')
                                                    try:
                                                        
                                                        if volum!='':
                                                            volu=float(volum.replace(',','.'))
                                                            print 'volval',volval
                                                            vol_finale=float(volval)-volu;
                                                            vol_temp=volu
                                                        if quant!='':
                                                            quantit=float(quant.replace(',','.'))
                                                            print 'concval',concval
                                                            if concval=='':
                                                                raise ErrorDerived('Error: aliquot '+gen+' with barcode "'+barc +'" has not a concentration. Please insert volume taken')
                                                            vol_temp=quantit/(float(concval)/1000);
                                                            print 'vol temp',vol_temp
                                                            vol_finale=float(volval)-vol_temp;
                                                        if volum=='' and quant=='':                                                            
                                                            raise ErrorDerived('Please insert volume or quantity taken for aliquot '+gen+' with barcode "'+barc +'"')
                                                        #if vol_finale<0:
                                                            #vol_finale=0;
                                                        vol_finale=round(vol_finale,2)
                                                        vol_temp=round(vol_temp,2)
                                                        print 'vol',volu
                                                        print 'vol finale',vol_finale
                                                    except ValueError:
                                                        raise ErrorDerived('Error: You can only insert number. Please correct value for aliquot '+gen+' with barcode "'+barc+'"')
                    
                                                print 'vol_temp',vol_temp
                                                #creo la struttura dati da passare al file html
                                                aggiorna=AggiornaVolume(gen=gen,
                                                                        barcode=barc,
                                                                        position=pos,
                                                                        concattuale=concval,
                                                                        volattuale=volval,
                                                                        volpreso=volum,
                                                                        quantpresa=quant,
                                                                        volequiv=vol_temp,
                                                                        volfinale=str(vol_finale))
                                                lista_dati.append(aggiorna)
                print 'lista dati',lista_dati
                comm=commenti.replace(' ','%20')
                variables = RequestContext(request, {'form':form,'valido':'True','espe':esp,'data':dat,'lista':lista_dati,'note':comm,'uten':utente,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList,'wg':wg})
                return render_to_response('tissue2/update/update_volume.html',variables)
            if 'conf_tutto' in request.POST or 'prosegui' in request.POST:
                lista_dati=request.session.get('aliqesperimenti')
                name=request.user.username
                pianificatore=User.objects.get(username=name)
                print '[BBM] utente',pianificatore
                esp=request.session.get('expesperim')
                esperim=Experiment.objects.get(id=esp)

                uten=request.session.get('operatesperim').strip()
                if uten=='':
                    utente=''
                else:
                    utente=User.objects.get(id=uten).username
                
                data_fin=request.session.get('datesperim').strip()
                #d=dat.split('-')
                #data_fin=d[2]+'-'+d[1]+'-'+d[0]
                
                commenti=request.session.get('noteesperim').strip()
                commenti=commenti.replace('%20',' ')
                
                #creo l'experiment schedule
                schedule=ExperimentSchedule(scheduleDate=date.today(),
                                            operator=pianificatore)
                schedule.save()
                lisaliq=[]
                for val in lista_dati:
                    
                    gen=val.gen
                    volumerim=val.volfinale
                    volumepres=val.volequiv
                    try:
                        volumerim=float(volumerim)
                        volumepres=float(volumepres)
                    except:
                        volumerim=-1
                        volumepres=-1                   

                    aliq=Aliquot.objects.get(uniqueGenealogyID=gen,availability=1)
                                        
                    #salvo l'indicazione dell'esperimento
                    aliqesp=AliquotExperiment(idAliquot=aliq,
                                              idExperiment=esperim,
                                              idExperimentSchedule=schedule,
                                              takenValue=volumepres,
                                              remainingValue=volumerim,
                                              operator=utente,
                                              experimentDate=data_fin,
                                              confirmed=0,
                                              notes=commenti)
                    aliqesp.save()
                    print 'aliqesp',aliqesp
                    lisaliq.append(gen)
                if 'conf_tutto' in request.POST:
                    if utente!='':
                        email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                        msg=['You have been designated to execute the following:','','Assigner:\t'+name,'Experiment:\t'+str(esperim.name),'Description:\t'+commenti,'','Aliquots:','N\tGenealogy ID\tBarcode\tPosition\tUsed volume(ul)\tLeft volume(ul)']
                        aliquots=Aliquot.objects.filter(uniqueGenealogyID__in=lisaliq,availability=1)
                        wgList=WG.objects.filter(id__in=Aliquot_WG.objects.filter(aliquot__in=aliquots).values_list('WG',flat=True).distinct())
                        print 'wglist',wgList
                        for wg in wgList:
                            print 'wg',wg
                            email.addMsg([wg.name], msg)
                            aliq=aliquots.filter(id__in=Aliquot_WG.objects.filter(WG=wg).values_list('aliquot',flat=True).distinct())
                            print 'aliq',aliq
                            i=1
                            #per mantenere l'ordine dei campioni anche nell'e-mail
                            for valgenerale in lista_dati:
                                for al in aliq:
                                    if valgenerale.gen==al.uniqueGenealogyID:                                  
                                        email.addMsg([wg.name],[str(i)+'\t'+al.uniqueGenealogyID+'\t'+valgenerale.barcode+'\t'+valgenerale.position+'\t'+valgenerale.volequiv+'\t'+valgenerale.volfinale])
                                        i=i+1
                            #devo mandare l'e-mail all'operatore incaricato di eseguire la procedura
                            email.addRoleEmail([wg.name], 'Assignee', [utente])
                            email.addRoleEmail([wg.name], 'Executor', [request.user.username])
                            print 'messaggio',email.mailDict
                        try:
                            email.send()
                        except Exception, e:
                            print 'err',e
                            pass
                        
                    variables = RequestContext(request, {'listafin':lista_dati,'fine':True,'exp':esperim,'operat':utente,'note':commenti,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
                    return render_to_response('tissue2/update/update_volume.html',variables)
                if 'prosegui' in request.POST:
                    #sto facendo un esperimento di beaming o micro o sanger, quindi devo fare la POST alla pagina dello 
                    #specifico modulo
                    if esperim.name=='Beaming' or esperim.name=='SangerSequencing' or esperim.name=='RealTimePCR' or esperim.name=='DigitalPCR' or esperim.name=='Sequenom' or esperim.name=='CellLineGeneration' or esperim.name=='CellLineThawing' or esperim.name=='NextGenerationSequencing':
                        #listaaliq=AliquotExperiment.objects.filter(Q(confirmed=0)&Q(idExperiment=esperim))
                        lista=[]
                        lis_pezzi_url=[]
                        lgen=''
                        dizgen={}
                        for l in lista_dati:   
                            diz={}
                            diz['genid']=l.gen
                            diz['barcode']=l.barcode
                            diz['vol']=l.volattuale
                            diz['conc']=l.concattuale
                            diz['takenvol']=str(l.volequiv)
                            diz['remainingvol']=str(l.volfinale)
                            #diz['operator']=l.operator
                            aliq=Aliquot.objects.get(uniqueGenealogyID=l.gen)
                            diz['date']=str(aliq.idSamplingEvent.samplingDate)
                            #listagen+=l.gen+'&'
                            lgen+=l.gen+'&'
                            if len(lgen)>2000:
                            #cancello la & alla fine della stringa
                                lis_pezzi_url.append(lgen[:-1])
                                lgen=''

                            lista.append(diz)
                        #cancello la & alla fine della stringa
                        strbarc=lgen[:-1]
                        if strbarc!='':
                            lis_pezzi_url.append(strbarc)
                        print 'lista',lista
                        print 'pezzi_url',lis_pezzi_url
                        #la API mi da' la posizione dei canpioni e gli devo passare il nome di un utente per sapere se il campione
                        #e' disponibile o meno. Se pero' non ho un utente a cui assegnare passo x, cosi' non ho problemi sul possesso
                        operatore=utente
                        if utente=='':
                            operatore='x'
                        if len(lis_pezzi_url)!=0:
                            for elementi in lis_pezzi_url:                                
                                barc=elementi.replace(' ','%20')
                                listabarcurl=barc.replace('#','%23')
                                print 'listabarcurl',listabarcurl
                                #interrogo lo storage per sapere dove si trova quella provetta
                                request.META['HTTP_WORKINGGROUPS']=get_WG_string()
                                storbarc=StorageTubeHandler()                                
                                data=storbarc.read(request, listabarcurl, operatore)
                                print 'data',data
                                dizprov=json.loads(data['data'])
                                dizgen = dict(dizgen.items() + dizprov.items())
                        print 'dizgen',dizgen
                        for val in lista:
                            gen=val['genid']
                            print 'gen',gen
                            for key,value in dizgen.items():
                                if key==gen:
                                    valoritot=value.split('|')
                                    val['pos']=valoritot[1]
                                    val['father']=valoritot[2]
                                    
                        print 'lista',lista

                        servizio=WebService.objects.get(name=esperim.name)
                        urlmodul=Urls.objects.get(idWebService=servizio).url
                        if esperim.name=='Beaming':
                            #faccio la post al modulo di beaming dandogli la lista con dentro i dizionari
                            url=urlmodul+'/api.newbeamingrequest'
                        if esperim.name=='SangerSequencing':
                            #faccio la post al modulo di sanger dandogli la lista con dentro i dizionari
                            url=urlmodul+'/api.newsangerrequest'
                        if esperim.name=='RealTimePCR':
                            #faccio la post al modulo di real time dandogli la lista con dentro i dizionari
                            url=urlmodul+'/api.newrealtimerequest'
                        if esperim.name=='DigitalPCR':
                            #faccio la post al modulo di digitalpcr dandogli la lista con dentro i dizionari
                            url=urlmodul+'/api.newdigitalpcrrequest'
                        if esperim.name=='Sequenom':
                            #faccio la post al modulo di fingerprinting dandogli la lista con dentro i dizionari
                            url=urlmodul+'/api.newfingerprintingrequest'
                        if esperim.name=='CellLineGeneration':
                            #faccio la post al modulo di linee cellulari dandogli la lista con dentro i dizionari
                            url=urlmodul+'/api/externalRequest/'
                        if esperim.name=='CellLineThawing':
                            #faccio la post al modulo di linee cellulari dandogli la lista con dentro i dizionari
                            url=urlmodul+'/api/externalRequest/'
                        if esperim.name=='NextGenerationSequencing':
                            #faccio la post al modulo di ngs dandogli la lista con dentro i dizionari
                            url=urlmodul+'/api.newngsrequest'
                            
                        lis=json.dumps(lista)
                        val2={'aliquots':lis,'operator':utente,'notes':commenti,'assigner':name,'source':'BioBank','experiment':esperim.name}
                        print 'url',url
                        print 'val2',val2
                        data1 = urllib.urlencode(val2)
                        req = urllib2.Request(url,data=data1, headers={"workingGroups" : get_WG_string()})
                        u = urllib2.urlopen(req)
                        #u = urllib2.urlopen(url, data1)
                        res =  json.loads(u.read())
                        print 'res',res
                        reqid=res['requestid']
                        print 'reqid',reqid

                        #reindirizzo sulla pagina del modulo
                        if reqid!='Error':
                            if esperim.name=='Beaming':
                                urlfin=urlmodul+'/new_request/'+str(reqid)+'/'
                            if esperim.name=='SangerSequencing':
                                urlfin=urlmodul+'/new_request/'+str(reqid)+'/'
                            if esperim.name=='RealTimePCR':
                                urlfin=urlmodul+'/new_request/'+str(reqid)+'/'
                            if esperim.name=='DigitalPCR':
                                urlfin=urlmodul+'/new_request/'+str(reqid)+'/'
                            if esperim.name=='Sequenom':
                                urlfin=urlmodul+'/new_request/'+str(reqid)+'/'
                            if esperim.name=='CellLineGeneration':
                                urlfin=urlmodul+'/generation/aliquots/?reqid='+str(reqid)
                            if esperim.name=='CellLineThawing':
                                urlfin=urlmodul+'/thawing/start/?reqid='+str(reqid)
                            if esperim.name=='NextGenerationSequencing':
                                urlfin=urlmodul+'/new_request/'+str(reqid)+'/'
                            
                            #non mando l'e-mail per gli altri moduli perche' in quei moduli l'utente a cui 
                            #viene assegnato l'esperimento puo' essere modificato e quindi non posso mandare
                            #l'avviso gia' adesso
                            if utente!='':
                                if esperim.name=='CellLineGeneration' or esperim.name=='CellLineThawing':
                                    #mando l'e-mail a chi deve eseguire
                                    email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                                    msg=['You have been designated to execute the following:','','Assigner:\t'+name,'Experiment:\t'+str(esperim.name),'Description:\t'+commenti,'','Aliquots:','N\tGenealogy ID\tBarcode\tPosition\tUsed volume(ul)\tLeft volume(ul)']
                                    #queste due righe le scrivo ogni volta perche' ci sono casi in cui non devo farle e quindi
                                    #non posso renderle generali
                                    aliquots=Aliquot.objects.filter(uniqueGenealogyID__in=lisaliq,availability=1)
                                    wgList=WG.objects.filter(id__in=Aliquot_WG.objects.filter(aliquot__in=aliquots).values_list('WG',flat=True).distinct())
                                    print 'wglist',wgList
                                    for wg in wgList:
                                        print 'wg',wg
                                        email.addMsg([wg.name], msg)
                                        aliq=aliquots.filter(id__in=Aliquot_WG.objects.filter(WG=wg).values_list('aliquot',flat=True).distinct())
                                        print 'aliq',aliq
                                        i=1
                                        #per mantenere l'ordine dei campioni anche nell'e-mail
                                        for valgenerale in lista_dati:
                                            for al in aliq:
                                                if valgenerale.gen==al.uniqueGenealogyID:                                  
                                                    email.addMsg([wg.name],[str(i)+'\t'+al.uniqueGenealogyID+'\t'+valgenerale.barcode+'\t'+valgenerale.position+'\t'+valgenerale.volequiv+'\t'+valgenerale.volfinale])
                                                    i=i+1
                                        #devo mandare l'e-mail all'operatore incaricato di eseguire la procedura
                                        email.addRoleEmail([wg.name], 'Assignee', [utente])
                                        email.addRoleEmail([wg.name], 'Executor', [request.user.username])
                                        print 'messaggio',email.mailDict
                                    try:
                                        email.send()
                                    except Exception, e:
                                        print 'err',e
                                        pass                             
                            return HttpResponseRedirect(urlfin)
                        else:
                            raise Exception
                        
                    else:   
                        if utente!='':                     
                            #mando l'e-mail a chi deve eseguire
                            email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                            msg=['You have been designated to execute the following:','','Assigner:\t'+name,'Experiment:\t'+str(esperim.name),'Description:\t'+commenti,'','Aliquots:','N\tGenealogy ID\tBarcode\tPosition\tUsed volume(ul)\tLeft volume(ul)']
                            #queste due righe le scrivo ogni volta perche' ci sono casi in cui non devo farle e quindi
                            #non posso renderle generali
                            aliquots=Aliquot.objects.filter(uniqueGenealogyID__in=lisaliq,availability=1)
                            wgList=WG.objects.filter(id__in=Aliquot_WG.objects.filter(aliquot__in=aliquots).values_list('WG',flat=True).distinct())
                            print 'wglist',wgList
                            for wg in wgList:
                                print 'wg',wg
                                email.addMsg([wg.name], msg)
                                aliq=aliquots.filter(id__in=Aliquot_WG.objects.filter(WG=wg).values_list('aliquot',flat=True).distinct())
                                print 'aliq',aliq
                                i=1
                                #per mantenere l'ordine dei campioni anche nell'e-mail
                                for valgenerale in lista_dati:
                                    for al in aliq:
                                        if valgenerale.gen==al.uniqueGenealogyID:                                  
                                            email.addMsg([wg.name],[str(i)+'\t'+al.uniqueGenealogyID+'\t'+valgenerale.barcode+'\t'+valgenerale.position+'\t'+valgenerale.volequiv+'\t'+valgenerale.volfinale])
                                            i=i+1
                                #devo mandare l'e-mail all'operatore incaricato di eseguire la procedura
                                email.addRoleEmail([wg.name], 'Assignee', [utente])
                                email.addRoleEmail([wg.name], 'Executor', [request.user.username])
                                print 'messaggio',email.mailDict
                            try:
                                email.send()
                            except Exception, e:
                                print 'err',e
                                pass
                         
                        if esperim.name=='RetrieveForImplant':
                            #faccio comparire la schermata apposita per il posizionamento dei campioni
                            return ExecPositionVitalAliquots(request)
                        else:                            
                            lisexp=['Beaming','MicroArray','SangerSequencing','RealTimePCR','DigitalPCR','Sequenom','CellLineGeneration','CellLineThawing','NextGenerationSequencing','RetrieveForImplant']
                            lexp=Experiment.objects.filter(name__in=lisexp).values_list('id',flat=True)
                            listaaliq=AliquotExperiment.objects.filter(Q(confirmed=0)&Q(Q(operator=name)|Q(operator=''))&Q(deleteTimestamp=None)&Q(fileInserted=0)).exclude(idExperiment__in=lexp)
                            #listaaliq=AliquotExperiment.objects.filter(Q(confirmed=0)&Q(Q(operator=name)|Q(operator=''))&Q(deleteTimestamp=None)&~Q(idExperiment=beam)&~Q(idExperiment=micro)&~Q(idExperiment=sang)&~Q(idExperiment=pcr)&~Q(idExperiment=digital)&~Q(idExperiment=finger)&~Q(idExperiment=cellgen)&~Q(idExperiment=cellscong)&~Q(idExperiment=nextgen)&~Q(idExperiment=implant))
                            l_conc=[]
                            for l in listaaliq:
                                #se e' un tessuto non ha la concentrazione
                                aliq=l.idAliquot
                                if aliq.derived==1:
                                    conc=Feature.objects.get(Q(name='Concentration')&Q(idAliquotType=aliq.idAliquotType))
                                    lisconc=AliquotFeature.objects.filter(Q(idAliquot=aliq)&Q(idFeature=conc))
                                    if len(lisconc)!=0:
                                        concval=str(lisconc[0].value)
                                else:
                                    concval=''
                                #creo l'oggetto aggiornavolume da mettere nella lista
                                agg=AggiornaVolume(gen=aliq.uniqueGenealogyID,
                                                   concattuale=concval)
                                l_conc.append(agg)
                            print 'lis conc finali',l_conc
    
                            variables = RequestContext(request, {'listagenerale':zip(listaaliq,l_conc),'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
                            return render_to_response('tissue2/update/update_final.html',variables)
                        
        except ErrorDerived as e:
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore':e.value,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
            return render_to_response('tissue2/update/update_volume.html',variables)
        except Exception,e:
            print 'err',e
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
            return render_to_response('tissue2/index.html',variables)
    else:
        form = VolumeForm()
    variables = RequestContext(request, {'form':form,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
    return render_to_response('tissue2/update/update_volume.html',variables)

#serve per la schermata in cui, dati dei genid o dei barcode di campioni l'
#utente comunica all'altro modulo (microarray, sanger...) le aliquote in questione
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_plan_experiments'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_plan_experiments')
def DecreaseViewMicro(request):
    if request.method=='POST':
        print request.POST
        form=VolumeForm(request.POST)
        try:
            if 'salva' in request.POST:
                listaaliq=json.loads(request.POST.get('dati'))
                dat=request.POST.get('dat')
                exp=request.POST.get('exp')
                operat=request.POST.get('operat')
                note=request.POST.get('note')
                wg=request.POST.get('workg')
                lisgen=[]
                listot=[]
                if len(listaaliq)!=0:
                    for val in listaaliq:
                        print 'val',val
                        ch=val.split('|')
                        if ch[0] not in lisgen:                        
                            aggiorna=AggiornaVolume(gen=ch[0],
                                                barcode=ch[1],
                                                position=ch[2],
                                                concattuale=ch[3],
                                                volattuale=ch[4],
                                                replicati=ch[5])
                            print 'aggiorna',aggiorna
                        
                            lisgen.append(ch[0])
                            listot.append(aggiorna)
                            print 'lisgen',listot
                print 'lista esperimenti',listot
                request.session['genealogyesperimenti']=lisgen
                request.session['aliqesperimenti']=listot
                request.session['datesperim']=dat
                request.session['expesperim']=exp
                request.session['operatesperim']=operat
                request.session['noteesperim']=note
                request.session['workgesperim']=wg
                return HttpResponse()   
            #ho cliccato sul tasto 'add file'
            if 'aggiungi_file' in request.POST:
                if 'file' in request.FILES:
                    assignUsersList=[]
                    addressUsersList=[]
                    if settings.USE_GRAPH_DB == True:
                        for g in get_WG():
                            assignUsersDict={}
                            assignUsersDict['wg']=WG.objects.get(name=g)
                            assignUsersDict['usersList']=list()
                            for u in User.objects.filter(~Q(username='admin')&~Q(first_name='')).filter(id__in=WG_User.objects.filter(user__is_active=1,WG__name=g,permission__codename=get_functionality()).values_list("user",flat=True)).order_by('last_name'):
                                assignUsersDict['usersList'].append(u)
                            assignUsersList.append(assignUsersDict)
                        for g in WG.objects.all():
                            addressUsersDict={}
                            addressUsersDict['wg']=g
                            addressUsersDict['usersList']=list()
                            for u in User.objects.filter(~Q(username='admin')&~Q(first_name='')).filter(id__in=WG_User.objects.filter(user__is_active=1,WG=g,permission__codename=get_functionality()).values_list("user",flat=True)).order_by('last_name'):
                                addressUsersDict['usersList'].append(u)
                            addressUsersList.append(addressUsersDict)
                    else:
                        assignUsersDict={}
                        assignUsersDict['wg']=''
                        assignUsersDict['usersList']=list()
                        for u in User.objects.filter(~Q(username='admin')&~Q(first_name='')&Q(is_active=1)).order_by('last_name'):
                            assignUsersDict['usersList'].append(u)
                        assignUsersList.append(assignUsersDict)
                        addressUsersList.append(assignUsersDict)
                    
                    lista_dati=[]
                    esp=request.POST.get('esper')
                    dat=request.POST.get('data').strip()
                    commenti=request.POST.get('comm').strip()
                    utente=request.POST.get('utent').strip()
                    
                    lista_dati=request.session.get('aliqesperimenti')
                    listagentot=request.session.get('genealogyesperimenti')
                    esp=request.session.get('expesperim')
                    dat=request.session.get('datesperim').strip()
                    commenti=request.session.get('noteesperim').strip()
                    utente=request.session.get('operatesperim').strip()
                    wg=request.session.get('workgesperim')
                    print 'lis_dati',lista_dati
                    
                    f=request.FILES['file']
                    linee=f.readlines()
                    stringalinee=''
                    
                    for i in range(0,len(linee)):
                        c=linee[i]
                        #c e' la singola riga del file
                        #il .strip toglie gli eventuali spazi e il \r finale nella riga
                        c=c.strip()
                        print 'c',c
                        if c!='':
                            stringalinee+=c+'&'                            
                    stringtot=stringalinee[:-1]     
                    diz=AllAliquotsContainer(stringtot)
                    
                    for gen in diz:
                        lista=diz[gen]
                        if len(lista)==0:
                            raise ErrorDerived('Error: aliquot '+gen+' does not exist in storage')
                        else:
                            if lista not in lista_dati:
                                #lista_dati.append(lista)
                                #e' una lista in cui ogni valore e' una stringa formata da gen|barcode|posizione
                                for val in lista:
                                    print 'val',val
                                    ch=val.split('|')
                                    gg=ch[0]
                                    barc=ch[1]
                                    pos=ch[2]
                                    
                                    if gg not in listagentot:
                                        listagentot.append(gg)
                                        laliq=Aliquot.objects.filter(uniqueGenealogyID=gg,availability=1)
                                        if len(laliq)==0:
                                            raise ErrorDerived('Error: aliquot '+gen+' does not exist in storage')
                                        else:
                                            aliq=laliq[0]
                                            print 'aliq',aliq
                                            #guardo se l'aliquota puo' essere collegata a quell'esperimento
                                            esperim=Experiment.objects.get(id=esp)
                                            aliqexp=AliquotTypeExperiment.objects.filter(idExperiment=esperim,idAliquotType=aliq.idAliquotType)
                                            
                                            if aliqexp.count()==0:
                                                raise ErrorDerived('Error: aliquot '+gen+' with barcode "'+barc+'" is not supported by experiment chosen')
                                                                            
                                            alexpsched=AliquotExperiment.objects.filter(idAliquot=aliq,confirmed=0,deleteTimestamp=None)
                                            if(alexpsched.count()!=0):
                                                raise ErrorDerived('Error: aliquot '+gen+' with barcode "'+barc+'" is already scheduled for this procedure. Please first confirm past action.')
                                                
                                            concval=''
                                            volval=''
                                            #prendo le feature dell'aliquota
                                            lconc=Feature.objects.filter(name='Concentration',idAliquotType=aliq.idAliquotType)
                                            lvol=Feature.objects.filter(name='Volume',idAliquotType=aliq.idAliquotType)
                                            if len(lconc)!=0:
                                                lisconc=AliquotFeature.objects.filter(idAliquot=aliq,idFeature=lconc[0])
                                                #se il derivato non ha conc e vol viene salvato nel DB -1. Quindi cambio -1
                                                #con None
                                                if len(lisconc)!=0:
                                                    if lisconc[0].value==-1:
                                                        concval='None'
                                                    else:
                                                        concval=str(lisconc[0].value)
                                                        
                                            if len(lvol)!=0:
                                                lisvol=AliquotFeature.objects.filter(idAliquot=aliq,idFeature=lvol[0])
                                                if len(lisvol)!=0:
                                                    if lisvol[0].value==-1:
                                                        volval='None'
                                                    else:
                                                        volval=str(lisvol[0].value)
                                                        print 'voll',volval
                                            
                                            #vuol dire che il campione e' prima da rivalutare e quindi
                                            #non si puo' proseguire in questa schermata
                                            if volval=='None' or concval=='None':
                                                raise ErrorDerived('Error: Aliquot volume is not defined. Please first revalue aliquot '+gen+' with barcode "'+barc+'"')
                                            
                                            #creo la struttura dati da passare al file html
                                            aggiorna=AggiornaVolume(gen=gg,
                                                                    barcode=barc,
                                                                    position=pos,
                                                                    concattuale=concval,
                                                                    volattuale=volval,
                                                                    replicati=1)
                                            lista_dati.append(aggiorna)
                variables = RequestContext(request, {'form':form,'valido':'True','espe':esp,'data':dat,'lista':lista_dati,'note':commenti,'uten':utente,'wg':wg,'assignUsersList':assignUsersList,'addressUsersList':addressUsersList})
                return render_to_response('tissue2/update/exp_microarray.html',variables)
            if 'prosegui' in request.POST:
                lista_dati=request.session.get('aliqesperimenti')
                listaaliqesp=[]
                name=request.user.username
                pianificatore=User.objects.get(username=name)
                print '[BBM] utente',pianificatore
                esp=request.session.get('expesperim')
                esperim=Experiment.objects.get(id=esp)

                uten=request.session.get('operatesperim').strip()
                if uten=='':
                    utente=''
                else:
                    utente=User.objects.get(id=uten).username
                
                data_fin=request.session.get('datesperim').strip()
                
                commenti=request.session.get('noteesperim').strip()
                commenti=commenti.replace('%20',' ')
                
                #creo l'experiment schedule
                schedule=ExperimentSchedule(scheduleDate=date.today(),
                                            operator=pianificatore)
                schedule.save()
                
                dizio={}
                for val in lista_dati:
                    
                    gen=val.gen
                    repl=val.replicati
                    dizio[gen]=repl
                    
                    volumerim=-1
                    volumepres=-1

                    aliq=Aliquot.objects.get(uniqueGenealogyID=gen,availability=1)
                                        
                    #salvo l'indicazione dell'esperimento
                    aliqesp=AliquotExperiment(idAliquot=aliq,
                                              idExperiment=esperim,
                                              idExperimentSchedule=schedule,
                                              takenValue=volumepres,
                                              remainingValue=volumerim,
                                              operator=utente,
                                              experimentDate=data_fin,
                                              confirmed=0,
                                              notes=commenti)
                    aliqesp.save()
                    print 'aliqesp',aliqesp
                    listaaliqesp.append(aliqesp)
                    print 'dizio',dizio
                    
                #sto facendo un esperimento di microarray, quindi devo fare la POST alla pagina del modulo 
                #di microarray
                if esperim.name=='MicroArray':
                    
                    lista=[]
                    lis_pezzi_url=[]
                    lgen=''
                    dizgen={}
                    for l in lista_dati:   
                        diz={}                               
                        diz['genid']=l.gen
                        diz['barcode']=l.barcode
                        diz['vol']=l.volattuale
                        diz['conc']=l.concattuale
                        
                        aliq=Aliquot.objects.get(uniqueGenealogyID=l.gen)
                        diz['date']=str(aliq.idSamplingEvent.samplingDate)
                        diz['replicates']=dizio[aliq.uniqueGenealogyID]
                        lgen+=l.gen+'&'                        
                        if len(lgen)>2000:
                        #cancello la & alla fine della stringa
                            lis_pezzi_url.append(lgen[:-1])
                            lgen=''                    
                        lista.append(diz)
                    #cancello la & alla fine della stringa
                    strbarc=lgen[:-1]
                    if strbarc!='':
                        lis_pezzi_url.append(strbarc)
                    print 'lista',lista
                    print 'pezzi_url',lis_pezzi_url
                    #la API mi da' la posizione dei canpioni e gli devo passare il nome di un utente per sapere se il campione
                    #e' disponibile o meno. Se pero' non ho un utente a cui assegnare passo x, cosi' non ho problemi sul possesso
                    operatore=utente
                    if utente=='':
                        operatore='x'
                    if len(lis_pezzi_url)!=0:
                        for elementi in lis_pezzi_url:                                
                            barc=elementi.replace(' ','%20')
                            listabarcurl=barc.replace('#','%23')
                            print 'listabarcurl',listabarcurl
                            #interrogo lo storage per sapere dove si trova quella provetta
                            request.META['HTTP_WORKINGGROUPS']=get_WG_string()
                            storbarc=StorageTubeHandler()
                            
                            data=storbarc.read(request, listabarcurl, operatore)
                            dizprov=json.loads(data['data'])
                            dizgen = dict(dizgen.items() + dizprov.items())
                    print 'dizgen',dizgen
                    for val in lista:
                        gen=val['genid']
                        print 'gen',gen
                        for key,value in dizgen.items():
                            if key==gen:
                                valoritot=value.split('|')
                                val['pos']=valoritot[1]
                                val['father']=valoritot[2]
                                
                    print 'lista',lista
                    
                    servizio=WebService.objects.get(name='MicroArray')
                    urlmi=Urls.objects.get(idWebService=servizio).url
                    #faccio la post al modulo dandogli la lista con dentro i dizionari
                    url=urlmi+'/api.newuarrayrequest'
                    lis=json.dumps(lista)
                    print 'utente',utente
                    val2={'aliquots':lis,'operator':utente,'notes':commenti,'assigner':name}
                    print 'url',url
                    print 'val2',val2
                    data1 = urllib.urlencode(val2)
                    req = urllib2.Request(url,data=data1, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u = urllib2.urlopen(url, data1)
                    res =  json.loads(u.read())
                    print 'res',res
                    reqid=res['requestid']
                    print 'reqid',reqid
                    #reindirizzo sulla pagina del modulo dei microarray
                    #time.sleep(5)
                    if reqid!='Error':
                        urlbea=urlmi+'/new_request/'+str(reqid)+'/'
                        return HttpResponseRedirect(urlbea)
                    else:
                        raise Exception
                        
        except ErrorDerived as e:
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore':e.value})
            return render_to_response('tissue2/update/update_volume.html',variables)
        except Exception,e:
            print 'err',e
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('tissue2/index.html',variables)
    else:
        form = VolumeForm()
    variables = RequestContext(request, {'form':form})
    return render_to_response('tissue2/update/update_volume.html',variables)

#serve per la schermata in cui, dati dei genid o dei barcode di campioni derivati, l'
#utente puo' diminuirne il volume 
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_execute_experiments'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_execute_experiments')
def DecreaseFinal(request):
    name=request.user.username
    if request.method=='POST':
        print request.POST
        try:
            if 'salva' in request.POST:
                listagen=json.loads(request.POST.get('lgen'))
                print 'listagen',listagen
                request.session['listainiz_volume']=listagen
                return HttpResponse()
            if 'conferma' in request.POST or 'file' in request.POST:
                adesso=timezone.localtime(timezone.now())
                #metto i secondi a zero in modo di partire dal minuto preciso. Poi ad ogni convalida aggiungo un secondo
                adesso=adesso.replace(second=0, microsecond=0)
                lisfin=[]
                listagen=request.session.get('listainiz_volume')
                listemp=[]
                diztotale={}
                for diz in listagen:
                    listemp.append(diz['gen'])
                    diztotale[diz['gen']]=diz
                lisaliq=Aliquot.objects.filter(uniqueGenealogyID__in=listemp,availability=1)
                print 'lisaliq',lisaliq
                lisqual=AliquotExperiment.objects.filter(idAliquot__in=lisaliq,confirmed=0,deleteTimestamp=None)
                lgen=[]
                for qual in lisqual:
                    lgen.append(qual.idAliquot.uniqueGenealogyID)
                    print 'aliquota_exp',qual.idAliquot
                #devo ordinare la lista degli aliquot exp sched in base a come sono state convalidate le aliquote
                for diz in listagen:
                    for qual in lisqual:
                        if qual.idAliquot.uniqueGenealogyID==diz['gen']:
                            lisfin.append(qual)
                print 'lisfin',lisfin
                request.session['listafinale_volume']=lisfin
                
                url1 = Urls.objects.get(default = '1').url + "/container/availability/"
                val1={'lista':json.dumps(lgen),'tube':'0','nome':request.user.username}

                print 'url1',url1
                data = urllib.urlencode(val1)
                req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                #u = urllib2.urlopen(url1, data)
                res1 =  u.read()
                print 'res',res1
                if res1=='err':
                    variables = RequestContext(request, {'errore':True})
                    return render_to_response('tissue2/index.html',variables)
 
                listagenfiniti=[]
                lista=[]
                #listastringhe=[]
                i=1
                strgen=''
                for g in lgen:
                    strgen+=g+'&'
                lgenfin=strgen[:-1]
                diction=AllAliquotsContainer(lgenfin)
                for exp in lisfin:
                    lisvol=[]
                    aliq=exp.idAliquot

                    volumepres=diztotale[aliq.uniqueGenealogyID]['volpreso']
                    print 'volpres',volumepres
                    volrimanente=''
                    concval=''
                    #se l'aliquota e' un derivato
                    if volumepres!=-1:
                        volumepres=round(float(volumepres),2)                        
                        #decremento il volume
                        lvol=Feature.objects.filter(name='Volume',idAliquotType=aliq.idAliquotType)
                        if len(lvol)!=0:
                            lisvol=AliquotFeature.objects.filter(idAliquot=aliq,idFeature=lvol[0])
                            if len(lisvol)!=0:
                                volrimanente=lisvol[0].value-volumepres
                                if volrimanente<=0.0:
                                    volrimanente=0.0
                                lisvol[0].value=volrimanente
                                lisvol[0].save()
                                #aggiorno il volume nell'esperimento
                                exp.takenValue=volumepres
                                exp.remainingValue=volrimanente
                        lconc=Feature.objects.filter(name='Concentration',idAliquotType=aliq.idAliquotType)
                        if len(lconc)!=0:
                            lisconc=AliquotFeature.objects.filter(idAliquot=aliq,idFeature=lconc[0])
                            if len(lisconc)!=0:
                                concval=str(lisconc[0].value)
                    else:
                        volumepres=''
                        
                    #se l'aliquota e' finita
                    finita=diztotale[aliq.uniqueGenealogyID]['esaurito']
                    if finita==1:
                        #se e' esausta allora metto a zero il suo volume
                        if len(lisvol)!=0 and aliq.derived==1:
                            lisvol[0].value=0.0
                            lisvol[0].save()
                        aliq.availability=0
                        listagenfiniti.append(aliq.uniqueGenealogyID)
                        aliq.save()
                        exp.aliquotExhausted=1
                        esausta='True'
                    else:
                        esausta='False'
                    #aggiorno le note
                    note=diztotale[aliq.uniqueGenealogyID]['note']
                    #e' meglio non stampare le note perche' se c'e' qualche carattere non ASCII si blocca
                    #print 'note',note
                    exp.notes=note
                    #metto come confermato l'esperimento
                    exp.confirmed=1
                    #aggiorno la data a quella odierna
                    exp.experimentDate=date.today()
                    tempovalidaz=adesso+timezone.timedelta(seconds=i)
                    #salvo data e ora per avere l'ordinamento giusto nella schermata dopo (opzionale), quella dell'inserimento dei file 
                    exp.validationTimestamp=tempovalidaz
                    #imposto a 1 il booleano per il file solo se ho confermato e termino qui la procedura
                    if 'conferma' in request.POST:
                        exp.fileInserted=1
                    if exp.operator=='':
                        exp.operator=name
                    exp.save()
                    
                    valori=diction[aliq.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barc=val[1]
                    pos=val[2]
                    print 'valori',valori
                    #mi occupo del report finale                    
                    #valore=exp.idExperiment.name+'&'+aliq.uniqueGenealogyID+'&'+barc+'&'+concval+'&'+str(volumepres)+'&'+str(volrimanente)+'&'+esausta
                    #listastringhe.append(valore)
                    #request.session['listavolume_pdf_csv']=listastringhe
                    lista.append(ReportVolumeToHtml(i,exp.idExperiment.name, aliq.uniqueGenealogyID, barc,pos, concval, str(volumepres), str(volrimanente), esausta, 'n'))
                    print 'lista',lista
                    i=i+1                    
                
                email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                msg=['Experiment executed','','Assigned to:\t'+name,'','Aliquots:','N\tGenealogy ID\tBarcode\tPosition\tTaken volume(uL)\tFinal volume(uL)\tExhausted\tExperiment\tDescription']                    
                #non metto availability=1 perche' se l'aliquota e' esaurita non me la prende e non va bene
                lisdafiltrare=Aliquot.objects.filter(uniqueGenealogyID__in=listemp)
                wgList=WG.objects.filter(id__in=Aliquot_WG.objects.filter(aliquot__in=lisdafiltrare).values_list('WG',flat=True).distinct())
                print 'wglist',wgList
                for wg in wgList:
                    print 'wg',wg
                    email.addMsg([wg.name], msg)
                    aliq=lisdafiltrare.filter(id__in=Aliquot_WG.objects.filter(WG=wg).values_list('aliquot',flat=True).distinct())
                    print 'aliq',aliq
                    i=1
                    lisplanner=[]
                    #per mantenere l'ordine dei campioni anche nell'e-mail
                    for exp in lisfin:
                        for al in aliq:
                            if exp.idAliquot.uniqueGenealogyID==al.uniqueGenealogyID:
                                valori=diction[al.uniqueGenealogyID]
                                val=valori[0].split('|')
                                barc=val[1]
                                pos=val[2]
                                volpres=exp.takenValue
                                if volpres==-1:
                                    volpres=''
                                volrim=exp.remainingValue
                                if volrim==-1:
                                    volrim=''
                                esausta='False'
                                if exp.aliquotExhausted==1:
                                    esausta='True'
                                email.addMsg([wg.name],[str(i)+'\t'+al.uniqueGenealogyID+'\t'+barc+'\t'+pos+'\t'+str(volpres)+'\t'+str(volrim)+'\t'+esausta+'\t'+exp.idExperiment.name+'\t'+exp.notes])
                                i=i+1
                                if exp.idExperimentSchedule.operator.username not in lisplanner:
                                    lisplanner.append(exp.idExperimentSchedule.operator.username)
                    print 'lisplanner',lisplanner
                    #mando l'e-mail al pianificatore
                    email.addRoleEmail([wg.name], 'Planner', lisplanner)
                    email.addRoleEmail([wg.name], 'Executor', [request.user.username])
                try:
                    email.send()
                except Exception, e:
                    print 'err experiment:',e
                    pass
                        
                if len(listagenfiniti)!=0:
                    #mi collego allo storage per svuotare le provette contenenti le aliq
                    #esaurite
                    address=Urls.objects.get(default=1).url
                    url = address+"/full/"
                    print url
                    values = {'lista' : json.dumps(listagenfiniti), 'tube': 'empty','canc':True,'operator':name}
                    data = urllib.urlencode(values)
                    req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u=urllib2.urlopen(url, data)               
                    res1 =  u.read()
                    print 'res',res1
                    if res1=='err':
                        variables = RequestContext(request, {'errore':True})
                        return render_to_response('tissue2/index.html',variables)
                
                if 'conferma' in request.POST:
                    variables = RequestContext(request, {'fine':True,'lista_vol':lista})
                    return render_to_response('tissue2/update/update_final.html',variables)
                elif 'file' in request.POST:
                    urlfin=settings.DOMAIN_URL+settings.HOST_URL+'/decrease/insertfiles'
                    print 'urlfin',urlfin
            
                    return HttpResponseRedirect(urlfin)
                    
        except Exception, e:
            print 'err',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('tissue2/index.html',variables)
    else:        
        lisexp=['Beaming','MicroArray','SangerSequencing','RealTimePCR','DigitalPCR','Sequenom','CellLineGeneration','CellLineThawing','NextGenerationSequencing','RetrieveForImplant']
        lexp=Experiment.objects.filter(name__in=lisexp).values_list('id',flat=True)        
        listaaliq=AliquotExperiment.objects.filter(Q(confirmed=0)&Q(Q(operator=name)|Q(operator=''))&Q(deleteTimestamp=None)&Q(fileInserted=0)).exclude(idExperiment__in=lexp)
        print 'listaaliqexp',listaaliq
        l_conc=[]
        for l in listaaliq:    
            #se e' un tessuto non ha la concentrazione
            aliq=l.idAliquot
            lconc=Feature.objects.filter(name='Concentration',idAliquotType=aliq.idAliquotType)
            if len(lconc)!=0:
                lisconc=AliquotFeature.objects.filter(idAliquot=aliq,idFeature=lconc[0])
                if len(lisconc)!=0:
                    concval=str(lisconc[0].value)
            else:
                concval=''
            #creo l'oggetto aggiornavolume da mettere nella lista
            agg=AggiornaVolume(gen=aliq.uniqueGenealogyID,
                               concattuale=concval)
            l_conc.append(agg)
        print 'lis conc finali',l_conc

        variables = RequestContext(request, {'listagenerale':zip(listaaliq,l_conc)})
        return render_to_response('tissue2/update/update_final.html',variables)

#per cancellare gli esperimenti gia' pianificati
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_execute_experiments'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_execute_experiments')
def DecreaseCanc(request):
    try:
        if request.method=='POST':
            name=request.user.username
            if 'salva' in request.POST:             
                operatore=User.objects.get(username=name)
                listaexp=[]
                listaaliq=json.loads(request.POST.get('dati'))
                print 'listaaliq',listaaliq

                for diz in listaaliq:
                    for gen, note in diz.items():
                        aliq=Aliquot.objects.get(uniqueGenealogyID=gen)
                        listaexpsched=AliquotExperiment.objects.filter(idAliquot=aliq,confirmed=0,deleteTimestamp=None)
                        if len(listaexpsched)!=0:
                            #listaexpsched[0].deleteTimestamp= datetime.datetime.now()
                            listaexpsched[0].deleteTimestamp=timezone.localtime(timezone.now())
                            listaexpsched[0].deleteOperator=operatore
                            listaexpsched[0].notes=note
                            listaexpsched[0].save()
                            listaexp.append(listaexpsched[0])
                print 'listaexp',listaexp
                request.session['listaexperiment_canc']=listaexp
                return HttpResponse()
            if 'final' in request.POST:
                lista=[]
                laliq=[]
                listar=request.session.get('listaexperiment_canc')
                print 'listar',listar
                                
                lgen=''
                for val in listar:
                    lgen+=val.idAliquot.uniqueGenealogyID+'&'
                    laliq.append(val.idAliquot.uniqueGenealogyID)
                lgenfin=lgen[:-1]
                diz=AllAliquotsContainer(lgenfin)
                print 'dizio',diz
                
                email = LASEmail (functionality=get_functionality(), wgString=get_WG_string())
                msg=['Experiment aborted','','Assigned to:\t'+name,'','Aliquots:','N\tGenealogy ID\tBarcode\tPosition\tAssignment date\tExperiment\tDescription']
                aliquots=Aliquot.objects.filter(uniqueGenealogyID__in=laliq,availability=1)
                wgList=WG.objects.filter(id__in=Aliquot_WG.objects.filter(aliquot__in=aliquots).values_list('WG',flat=True).distinct())
                print 'wglist',wgList
                for wg in wgList:
                    print 'wg',wg
                    email.addMsg([wg.name], msg)
                    aliq=aliquots.filter(id__in=Aliquot_WG.objects.filter(WG=wg).values_list('aliquot',flat=True).distinct())
                    print 'aliq',aliq
                    i=1
                    lisplanner=[]
                    #per mantenere l'ordine dei campioni anche nell'e-mail
                    for alder in listar:
                        for al in aliq:   
                            if alder.idAliquot.uniqueGenealogyID==al.uniqueGenealogyID:
                                lval=diz[al.uniqueGenealogyID]
                                val=lval[0].split('|')
                                barc=val[1]
                                pos=val[2]
                                email.addMsg([wg.name],[str(i)+'\t'+al.uniqueGenealogyID+'\t'+barc+'\t'+pos+'\t'+str(alder.idExperimentSchedule.scheduleDate)+'\t'+alder.idExperiment.name+'\t'+alder.notes])
                                i=i+1                                
                                if alder.idExperimentSchedule.operator.username not in lisplanner:
                                    lisplanner.append(alder.idExperimentSchedule.operator.username)
                    print 'lisplanner',lisplanner
                    #devo mandare l'e-mail al pianificatore della procedura
                    email.addRoleEmail([wg.name], 'Planner', lisplanner)
                    email.addRoleEmail([wg.name], 'Executor', [request.user.username])
                try:
                    email.send()
                except Exception, e:
                    print 'errore',e
                    pass
                
                for i in range(0,len(listar)):
                    possch=listar[i]
                    dat=possch.idExperimentSchedule.scheduleDate
                    print 'dat',dat
                    data2=str(dat).split('-')
                    d=data2[2]+'-'+data2[1]+'-'+data2[0]
                    print 'd',d
                    valori=diz[possch.idAliquot.uniqueGenealogyID]
                    val=valori[0].split('|')
                    barc=val[1]
                    pos=val[2]
                    lista.append(ReportScheduleCancToHtml(i+1,possch.idAliquot.uniqueGenealogyID,barc,pos,possch.idExperimentSchedule.operator.username,d,'n'))                
                    
                variables = RequestContext(request,{'lista_sch':lista})
                return render_to_response('tissue2/revalue/cancel.html',variables)
    except Exception,e:
        print 'err',e
        transaction.rollback()
        errore=True
        variables = RequestContext(request, {'errore':errore})
        return render_to_response('tissue2/index.html',variables)

#Per far comparire la schermata per caricare i file collegati ad un esperimento e poi salvarli
@transaction.commit_on_success
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_execute_experiments')
def InsertFiles(request):
    print 'BBM view: start views_experiment.InsertFiles'
    print request.POST
    name=request.user.username
    if request.method == "GET":
        try:
            lisexp=['Beaming','MicroArray','SangerSequencing','RealTimePCR','DigitalPCR','Sequenom','CellLineGeneration','CellLineThawing','NextGenerationSequencing','RetrieveForImplant']
            lexp=Experiment.objects.filter(name__in=lisexp).values_list('id',flat=True)
            listaaliq=AliquotExperiment.objects.filter(confirmed=1,fileInserted=0,operator=name,deleteTimestamp=None).exclude(idExperiment__in=lexp).order_by('validationTimestamp','id')
            print 'listaaliqexp',listaaliq
            #devo prendere i tipi di file collegati agli esperimenti presenti nella lista e passarli alla schermata
            lisexp=[]
            for alexp in listaaliq:
                lisexp.append(alexp.idExperiment)
            lisfiletype=FileTypeExperiment.objects.filter(idExperiment__in=lisexp)
            print 'lisfiletype',lisfiletype
            variables = RequestContext(request,{'aliquots':listaaliq,'lisfiletype':lisfiletype})
            return render_to_response('tissue2/update/insert_file.html',variables)
        except Exception, e:
            print 'err get',e
            variables = RequestContext(request, {'errore':True})
            return render_to_response('tissue2/index.html',variables)
    else:
        try:
            print request.FILES
            raw_data = json.loads(request.POST['aliquots_list'])
            
            filesUploaded = {}
            diz_aliquots = {}
            lisaliq=[]
            listFiles=[]
            strgen=''
            for aliquot_info in raw_data:                
                lisfile=json.loads(aliquot_info['files'])
                print 'lisfile',lisfile
                nofile=aliquot_info['nofile']
                print 'nofile',nofile
                if 'filetype' in aliquot_info:
                    idfiletype=aliquot_info['filetype']
                else:
                    idfiletype=''
                print 'idfiletype',idfiletype
                tipofile=None
                if idfiletype!='':
                    tipofile=FileType.objects.get(id=idfiletype)
                if nofile==True or len(lisfile)!=0:
                    alexp = AliquotExperiment.objects.get(id=aliquot_info['idAliquotExperiment'])
                    alexp.fileInserted=1
                    alexp.save()
                    gen=alexp.idAliquot.uniqueGenealogyID
                    strgen+=gen+'&'
                    for f in lisfile:
                        if not filesUploaded.has_key(f):
                            uploaded_file = [upfile for upfile in request.FILES.getlist('file') if upfile.name == f][0]
                            print 'namefile',uploaded_file.name                        
                            destination = handle_uploaded_file(uploaded_file,settings.TEMP_URL)
                            print destination
                            listFiles.append(destination)
                            responseUpload = uploadRepFile({'operator':request.user.username}, destination)
                            print responseUpload
                            if responseUpload == 'Fail':
                                transaction.rollback()
                                raise Exception
                            filesUploaded[f] = responseUpload
                        expfile=ExperimentFile(idAliquotExperiment=alexp,
                                               fileName=f,
                                               linkId=filesUploaded[f],
                                               idFileType=tipofile)
                        expfile.save()
                    diz_aliquots[gen]=lisfile
                    lisaliq.append(gen)
                                    
            print 'listfiles',listFiles
            remove_uploaded_files(listFiles)            
            
            lgenfin=strgen[:-1]            
            #uso questo metodo per prendere il barcode perche' ho bisogno di sapere il codice anche delle provette esaurite,
            #cosa che non avrei con la funzione AllAliquotsContainer
            strgendopo=lgenfin.split('&')
            lis_pezzi_url=[]
            dizgen={}
            strgen2=''
            for parti in strgendopo:
                strgen2+=parti+'&'
                if len(strgen2)>2000:
                    #cancello la & alla fine della stringa
                    lis_pezzi_url.append(strgen2[:-1])
                    strgen2=''
            #cancello la & alla fine della stringa
            lgen=strgen2[:-1]
            print 'lgen',lgen
            if lgen!='':
                lis_pezzi_url.append(lgen)
            
            if len(lis_pezzi_url)!=0:
                for elementi in lis_pezzi_url:
                    storbarc=StorageTubeHandler()
                    data=storbarc.read(request, elementi, request.user.username)
                    dizprov=json.loads(data['data'])
                    dizgen = dict(dizgen.items() + dizprov.items())                  
            print 'dizgen',dizgen
            
            lista=[]
            i=1
            for gen in lisaliq:
                print 'gen',gen
                strnomifile=''
                lfile=diz_aliquots[gen]
                for val in lfile:
                    strnomifile+=val+'; '
                strnomifile=strnomifile[:len(strnomifile)-2]
                print 'nomifile',strnomifile
                posti=dizgen[gen]
                val2=posti.split('|')
                print 'val2',val2
                barc=val2[0]
                #pos=val2[1]
                
                lista.append(ReportToHtml([str(i),gen,barc,strnomifile]))
                i+=1            
                       
            print 'lista finale',lista            
            
            request.session['listafinaleexperimentsalvafile']=lista
            urlfin=settings.DOMAIN_URL+settings.HOST_URL+'/decrease/insertfiles/final'
            print 'urlfin',urlfin
            
            return HttpResponseRedirect(urlfin)            
            
        except Exception, e:
            print 'err post',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('tissue2/index.html',variables)

#per far vedere il report finale del salvataggio dei file
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_execute_experiments')
def InsertFilesFinal(request):
    lista=request.session.get('listafinaleexperimentsalvafile')
    variables = RequestContext(request,{'fine':True,'lista_fin':lista})
    return render_to_response('tissue2/update/insert_file.html',variables)

#per far vedere la schermata che permette di scaricare i file salvati prima   
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_execute_experiments')
def DownloadInit(request):
    mdamTemplates = getMdamTemplates([41,44,45])
    print 'mdamTemplates',mdamTemplates
    mdamurl=Urls.objects.get(idWebService=WebService.objects.get(name='MDAM').id).url
    listot=getGenealogyDict()
    variables = RequestContext(request, {'mdamTemplates':json.dumps(mdamTemplates), 'mdam_url':mdamurl,'genid':json.dumps(listot),'type':'None' })   
    return render_to_response('tissue2/update/view_data.html',variables)

#per far vedere la schermata che permette di scaricare i file salvati prima   
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_symphogen_file1')
def DownloadRAS(request):
    mdamTemplates = getMdamTemplates([41,44,45])
    print 'mdamTemplates',mdamTemplates
    mdamurl=Urls.objects.get(idWebService=WebService.objects.get(name='MDAM').id).url
    listot=getGenealogyDict()
    variables = RequestContext(request, {'mdamTemplates':json.dumps(mdamTemplates), 'mdam_url':mdamurl,'genid':json.dumps(listot),'type':'RAS','experiment':'Symphogen' })   
    return render_to_response('tissue2/update/view_data.html',variables)

#per far vedere la schermata che permette di scaricare i file salvati prima   
@laslogin_required
@login_required
@permission_decorator('tissue.can_view_BBM_symphogen_file2')
def DownloadECD(request):
    mdamTemplates = getMdamTemplates([41,44,45])
    print 'mdamTemplates',mdamTemplates
    mdamurl=Urls.objects.get(idWebService=WebService.objects.get(name='MDAM').id).url
    listot=getGenealogyDict()
    variables = RequestContext(request, {'mdamTemplates':json.dumps(mdamTemplates), 'mdam_url':mdamurl,'genid':json.dumps(listot),'type':'ECD','experiment':'Symphogen' })
    return render_to_response('tissue2/update/view_data.html',variables)

#per passare alla schermata il contenuto del file che si vuole scaricare
@csrf_exempt
@get_functionality_decorator
def DownloadFilesFinal(request):
    try:
        print request.POST
        #e' una lista con dentro stringhe formate da idaliq|idaliqlabelsched|idlabelfile
        sNodesJson = json.loads(request.POST['selectedNodes'])
        dataStruct = json.loads(request.POST['dataStruct'])
        
        sNodes = {}
        selectedNodes = [ s.strip().split('|') for s in sNodesJson ]
        print 'sNodesJson', sNodesJson
        print 'selectedNodes', selectedNodes
        #con questo for viene popolato il diz sNodes
        for pathNode in selectedNodes:
            current_level = sNodes
            for part in pathNode:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
        #e' un diz con chiave idaliq e valore un diz con chiave id dell'experimentfile e valore vuoto
        print 'sNodes', sNodes

        tmpDir = request.user.username.replace('.','-') + '_' + str(date.today())
        os.mkdir ( os.path.join(settings.TEMP_URL, tmpDir) )

        repositoryUrl = Urls.objects.get(idWebService=WebService.objects.get(name='Repository').id)

        for diz in dataStruct:
            idaliq=diz['idaliq']           
            #se quell'aliq ha un file selezionato da scaricare da parte dell'utente
            if sNodes.has_key(idaliq):
                currPath = os.path.join(settings.TEMP_URL, tmpDir, diz['gen'] )
                #creo la cartella piu' esterna chiamandola come il gen solo se non esiste gia'
                try:
                    os.mkdir ( currPath )
                except:
                    print 'cartella gia\' presente'
                    pass
                if 'file' in diz:
                    for dizfile in diz['file']:
                        idexpfile=dizfile['id']
                        if sNodes[idaliq].has_key(idexpfile):
                            link = dizfile['link']
                            r = requests.get(repositoryUrl.url + "/get_file/"+ link, verify=False, stream=True)
                            with open(os.path.join(currPath, dizfile['nome']) , 'wb') as f:
                                for chunk in r.iter_content(chunk_size=1024): 
                                    if chunk: # filter out keep-alive new chunks
                                        f.write(chunk)
                                        f.flush()
        #prima creo la struttura con tutte le cartelle annidate e poi chiamo questa funzione che ne fa il tar gz
        archiveFile = tarfile.open(os.path.join(TEMP_URL, tmpDir + '.tar.gz'),mode='w:gz')
        print 'creato .tar.gz'

        archiveFile.add( os.path.join(settings.TEMP_URL, tmpDir) , arcname=tmpDir)
        print 'aggiunta cartella'
        archiveFile.close()
        
        fout = open(os.path.join(TEMP_URL, tmpDir + '.tar.gz'))
        response = HttpResponse(fout, content_type='application/octet-stream')
        #creo la risposta con dentro il file tar gz che ho creato 
        response['Content-Disposition'] = 'attachment; filename=' + tmpDir + '.tar.gz'
        
        shutil.rmtree( os.path.join(settings.TEMP_URL, tmpDir))
        os.remove(os.path.join(TEMP_URL, tmpDir + '.tar.gz'))
        return response
    except Exception, e:
        print e
        return HttpResponseBadRequest("Error in retrieving data")

#@user_passes_test(lambda u: u.has_perm('tissue.can_view_execute_experiments'),login_url='/tissue/error/')
@permission_decorator('tissue.can_view_BBM_execute_experiments')
def createPDFDecreaseVol(request):
    if request.session.get('listavolume_pdf_csv'):
        lista=[]
        listaexp = request.session.get('listavolume_pdf_csv')
        print 'createpdfdecrvolume'
        for i in range(0,len(listaexp)):
            val=listaexp[i].split('&')
            lista.append(ReportVolumeToHtml(i+1,val[0],val[1],val[2],val[3],val[4],val[5],val[6], 's'))
            print 'lista',lista
        response=PDFMaker(request, 'Used_Aliquots.pdf', 'tissue2/update/pdf_AliquotsDecrease.html', lista)
        return response
    else:
        return HttpResponseRedirect(reverse('tissue.views.index'))

#@user_passes_test(lambda u: u.has_perm('tissue.can_view_execute_experiments'),login_url='/tissue/error/')
@permission_decorator('tissue.can_view_BBM_execute_experiments')
def createCSVDecreaseVol(request):
    if request.session.get('listavolume_pdf_csv'):
        listaexp = request.session.get('listavolume_pdf_csv')
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Used_Aliquots.csv'
        writer = csv.writer(response,delimiter='\t')
        writer.writerow(["N","Experiment","GenealogyID","Barcode","Concentration(ng/ul)","Taken vol.(ul)","Final vol.(ul)","Exhausted"])
        for i in range(0,len(listaexp)):
            val=listaexp[i].split('&')
            conc=str(val[3]).replace('.',',')
            volpreso=str(val[4]).replace('.',',')
            volfinale=str(val[5]).replace('.',',')
            csvString=str(i+1)+"\t"+str(val[0])+"\t"+str(val[1])+"\t"+str(val[2])+"\t"+conc+"\t"+volpreso+"\t"+volfinale+"\t"+val[6]
            writer.writerow([csvString])
        return response
    else:
        return HttpResponseRedirect(reverse('tissue.views.index'))

