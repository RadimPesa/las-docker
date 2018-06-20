from __init__ import *
from catissue.tissue.utils import *
import tempfile, mimetypes, os, pytz
from django.core.servers.basehttp import FileWrapper
from django.utils import timezone

def error(request):
    return render_to_response('tissue2/error.html', RequestContext(request))

def start_redirect(request):
    #print "this is the URL I received: " +request.path
    return HttpResponseRedirect(reverse('tissue.views.index'))

#def login(request):
#    return auth.views.login(request, template_name='tissue2/login.html')

def login(request):
    #print request
    if request.method == 'POST':
        #print request
        #print request.POST
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            #User.username = username
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('tissue.views.index'))
            else:
                message = "Bad username or password."
                return render_to_response('tissue2/login.html', {'message': message}, RequestContext(request))
        else:
            message = "Invalid input."
            return render_to_response('tissue2/login.html', {'message': message}, RequestContext(request))
    return render_to_response('tissue2/login.html', RequestContext(request))

@laslogin_required
@login_required
def logout(request):
    auth.logout(request)
    for sesskey in request.session.keys():
        del request.session[sesskey]
    #return HttpResponseRedirect(reverse('tissue.views.login'))
    return HttpResponse("loggedout")

@laslogin_required
@login_required
def index(request):
    CancSession(request)        
    projects = [app for app in settings.INSTALLED_APPS if app in ['mercuric','funnel','symphogen','motricolor'] ]
    return render_to_response('tissue2/index.html', {'projects': projects },  RequestContext(request))

#@login_required
#def logout(request):
#    auth.logout(request)
#    return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))

'''@laslogin_required
@permission_required('tissue.add_Places', '/tissue/permission')
@login_required
def place(request):
    if request.method=='POST':
        form = PlaceForm(request.POST)
        if form.is_valid():
            try:
                Source.objects.create(name=request.POST['hospital'].strip())
                return HttpResponseRedirect(reverse('tissue.views.place'))
            except:
                return HttpResponseRedirect(reverse('tissue.views.index'))
    else:
        form = PlaceForm()
    variables = RequestContext(request, {'form': form})
    return render_to_response('tissue2/place.html',variables)

def ajax_hospital_autocomplete(request):
    if 'term' in request.GET:
        posti = Source.objects.filter(name__istartswith=request.GET.get('term'))[:10]
        res=[]
        for p in posti:
            p = {'id':p.id, 'label':p.__unicode__(), 'value':p.__unicode__()}
            res.append(p)
        return HttpResponse(simplejson.dumps(res))
    return HttpResponse()


def caxeno(request):
    if request.method=='POST':
        try:
            barcode=request.POST['barcode'] 
            print barcode   
            return HttpResponse()
        except:
            return HttpResponseRedirect(reverse('tissue.views.index'))
    variables = RequestContext(request)
    return render_to_response('tissue2/caxeno.html',variables)'''



#serve a salvare gli espianti di caxeno e anche il salvataggio delle linee cellulari
@transaction.commit_on_success
@csrf_exempt
@get_functionality_decorator
def saveExplants(request):
    try:
        if request.method=='POST':
            listaal=[]
            lisbarclashub=[]
            print request.POST
            pezziusati=0
            disponibile=1
            derivato=0
            #mi da' l'operatore che ha fatto l'espianto
            operatore=request.POST.get('operator')
            data_generale=request.POST.get('date')
            
            #dato=ali.split(",")            
            if 'source' in request.POST:
                sorg=Source.objects.get(Q(name='cellline')&Q(type='Las'))
            else:
                #prendo la sorgente, che e' caxeno, dalla tabella source
                sorg=Source.objects.get(name='caxeno')
            
            listaaliq=json.loads(request.POST.get('explants'))
            
            for tipialiq in listaaliq:
                for topi in listaaliq[tipialiq]:
                    for barc in listaaliq[tipialiq][topi]:
                        for prov in listaaliq[tipialiq][topi][barc]:
                            genid=prov['genID']
                            tipoaliq=tipialiq
                            piastra=barc
                            pos=prov['pos']
                            numpezzi=prov['qty']
                            print 'gen',genid
                            print 'tipoaliq',tipoaliq
                            print 'piastra',piastra
                            print 'pos',pos
                            print 'numpezzi',numpezzi
                            
                            g = GenealogyID(genid)
                            #tumore=genid[0:3]
                            tumore=g.getOrigin()
                            print 'tumore',tumore
                            #caso=genid[3:7]
                            caso=g.getCaseCode()
                            print 'caso',caso
                            tipotum=CollectionType.objects.get(abbreviation=tumore)
                            print 'tipotum',tipotum
                            #prendo la collezione da associare al sampling event
                            colle=Collection.objects.get(Q(itemCode=caso)&Q(idCollectionType=tipotum))
                            
                            #t=genid[7:9]
                            t=g.getTissue()
                            tessuto_esp=TissueType.objects.get(abbreviation=t)
                            print 'tessuto',tessuto_esp.id
                            print 'prov',prov
                            #questa chiave c'e' solo quando salvo gli espianti in batch
                            if 'date_expl' in prov:
                                data_expl=prov['date_expl']
                            else:
                                data_expl=data_generale
                            print 'data expl',data_expl
                            #salvo la serie
                            ser,creato=Serie.objects.get_or_create(operator=operatore,
                                                                   serieDate=data_expl)
                            
                            #salvo il campionamento
                            campionamento,creato=SamplingEvent.objects.get_or_create(idTissueType=tessuto_esp,
                                                         idCollection=colle,
                                                         idSource=sorg,
                                                         idSerie=ser,
                                                         samplingDate=data_expl)
                            print 'camp',campionamento
                            
                            barcode=None
                            #se sto trattando vitale, rna e snap
                            if(tipoaliq!='FF')and(tipoaliq!='OF')and(tipoaliq!='CH'):
                                barcodepiastraurl=piastra.replace('#','%23')
                                url = Urls.objects.get(default = '1').url + "/api/container/"+barcodepiastraurl
                                try:
                                    #prendo i dati dall'archivio che mi da' la posizione e il barcode delle aliq
                                    req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
                                    u = urllib2.urlopen(req)
                                    #u = urllib2.urlopen(url)
                                    res =  u.read()
                                    #print res
                                    data = json.loads(res)
                                    #print 'data',data
                                except Exception, e:
                                    print 'e',e
                                
                                #se la API mi restituisce dei valori perche' gli ho dato un codice
                                #corretto per la piastra    
                                if 'children' in data:    
                                    #per ottenere il barcode data la posizione    
                                    for w in data['children']:
                                        if w['position']==pos:
                                            barcode=w['barcode']
                                            print 'barc',barcode
                                            break;
                                    ffpe='false'
                                else:
                                    #vuol dire che sto salvando una nuova provetta e quindi il barcode 
                                    #risulta essere cio' che e' salvato nella variabile piastra
                                    barcode=piastra
                                    piastra=''
                                    pos=''
                                    ffpe='true'
                                    lisbarclashub.append(barcode)
                                #valori=str(genid)+','+str(piastra)+','+str(pos)+','+str(numpezzi)+','+barcode+','+tipoaliq+',false, , '
                            #se ho ffpe o of o ch o pl o px il barcode ce l'ho gia' e non devo andare a leggerlo
                            #il barcode e' salvato nella variabile piastra
                            else:
                                barcode=piastra
                                piastra=''
                                pos=''
                                ffpe='true'
                                lisbarclashub.append(barcode)
                                    
                            conta=prov['conta']
                            volu=prov['volume']
                            if volu!='-' or numpezzi=='-':
                                numpezzi=''
                            
                            valori=genid+','+str(piastra)+','+str(pos)+','+str(numpezzi)+','+barcode+','+tipoaliq+','+ffpe+',,,,,,'+str(data_expl)
                            
                            tipoaliquota= AliquotType.objects.get(abbreviation=tipoaliq)
                            print 'tipo aliquota',tipoaliq
                            a=Aliquot(barcodeID=barcode,
                                   uniqueGenealogyID=str(genid),
                                   idSamplingEvent=campionamento,
                                   idAliquotType=tipoaliquota,
                                   timesUsed=pezziusati,
                                   availability=disponibile,
                                   derived=derivato
                                   )
                            print 'a',a
                            
                            disable_graph()
                            a.save()
                            enable_graph()

                            
                            listaal.append(valori)
                            print 'listaaliq',listaal
                            print 'volu',volu
                            #se sto salvando del sangue ho anche altre feature
                            if volu!='-':
                                print 'vol dentro if',volu
                                #ho il valore in ml e devo trasformarlo in ul
                                vo=float(volu)*1000
                                featvol=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='Volume'))
                                aliqfeaturevol=AliquotFeature(idAliquot=a,
                                                           idFeature=featvol,
                                                           value=vo)
                                aliqfeaturevol.save()
                                print 'featu volume',aliqfeaturevol
                                if conta!='-':
                                    featconta=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='Count'))
                                    aliqfeatureconta=AliquotFeature(idAliquot=a,
                                                               idFeature=featconta,
                                                               value=conta)
                                    aliqfeatureconta.save()
                                    print 'aliq',aliqfeatureconta
                                    
                            #salvo i campioni normali
                            else:
                                #salvo il numero di pezzi solo se ci sono
                                if numpezzi!='':
                                    fea=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='NumberOfPieces'))
                                    aliqfeature=AliquotFeature(idAliquot=a,
                                                               idFeature=fea,
                                                               value=numpezzi)
                                    aliqfeature.save()
                                    print 'aliq',aliqfeature
            
            #address=request.get_host()+settings.HOST_URL
            request,errore=SalvaInStorage(listaal,request)
            print 'err', errore   
            if errore==True:
                raise Exception
            
            #comunico al LASHub che quei barcode sono stati utilizzati
            #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
            #indir=prefisso+address
            indir=settings.DOMAIN_URL+settings.HOST_URL
            url = indir + '/clientHUB/saveAndFinalize/'
            print 'url',url
            values = {'typeO' : 'container', 'listO': str(lisbarclashub)}
            requests.post(url, data=values, verify=False, headers={"workingGroups" : get_WG_string()})
        else:
            return HttpResponse('This url needs a post request, not a get.')
        transaction.commit()
        return HttpResponse("ok")
    except Exception, e:
        print 'errore', e    
        transaction.rollback()
        return HttpResponse("err")
    
'''#usato una volta sola per salvare gli espianti. Non serve piu'
@transaction.commit_on_success
@csrf_exempt
def SaveExpl(request):
    try:
        listaal=[]
        lisbarclashub=[]
        print request.POST
        pezziusati=0
        disponibile=1
        derivato=0
        #mi da' l'operatore che ha fatto l'espianto
        operatore='francesca.cottino'
        data_expl='2014-03-11'
        
        #dato=ali.split(",")
        #salvo la serie
        ser,creato=Serie.objects.get_or_create(operator=operatore,
                                               serieDate=data_expl)
        #prendo la sorgente, che e' caxeno, dalla tabella source
        sorg=Source.objects.get(name='caxeno')
        
        listaaliq=json.loads(request.POST.get('explants'))
        
        for tipialiq in listaaliq:
            for topi in listaaliq[tipialiq]:
                for barc in listaaliq[tipialiq][topi]:
                    for prov in listaaliq[tipialiq][topi][barc]:
                        genid=prov['genID']
                        tipoaliq=tipialiq
                        piastra=barc
                        pos=prov['pos']
                        numpezzi=prov['qty']
                        print 'gen',genid
                        print 'tipoaliq',tipoaliq
                        print 'piastra',piastra
                        print 'pos',pos
                        print 'numpezzi',numpezzi
                        
                        g = GenealogyID(genid)
                        #tumore=genid[0:3]
                        tumore=g.getOrigin()
                        print 'tumore',tumore
                        #caso=genid[3:7]
                        caso=g.getCaseCode()
                        print 'caso',caso
                        tipotum=CollectionType.objects.get(abbreviation=tumore)
                        print 'tipotum',tipotum
                        #prendo la collezione da associare al sampling event
                        colle=Collection.objects.get(Q(itemCode=caso)&Q(idCollectionType=tipotum))
                        
                        #t=genid[7:9]
                        t=g.getTissue()
                        tessuto_esp=TissueType.objects.get(abbreviation=t)
                        print 'tessuto',tessuto_esp.id
                        
                        #salvo il campionamento
                        campionamento,creato=SamplingEvent.objects.get_or_create(idTissueType=tessuto_esp,
                                                     idCollection=colle,
                                                     idSource=sorg,
                                                     idSerie=ser,
                                                     samplingDate=data_expl)
                        print 'camp',campionamento
                        
                        barcode=None
                        #se sto trattando vitale, rna e snap
                        if(tipoaliq!='FF')and(tipoaliq!='OF')and(tipoaliq!='CH'):
                            barcodepiastraurl=piastra.replace('#','%23')
                            url = Urls.objects.get(default = '1').url + "/api/container/"+barcodepiastraurl
                            try:
                                #prendo i dati dall'archivio che mi da' la posizione e il barcode delle aliq
                                req = urllib2.Request(url, headers={"workingGroups" : get_WG_string()})
                                u = urllib2.urlopen(req)
                                #u = urllib2.urlopen(url)
                                res =  u.read()
                                #print res
                                data = json.loads(res)
                                #print 'data',data
                            except Exception, e:
                                print 'e',e
                            
                            #se la API mi restituisce dei valori perche' gli ho dato un codice
                            #corretto per la piastra    
                            if 'children' in data:    
                                #per ottenere il barcode data la posizione    
                                for w in data['children']:
                                    if w['position']==pos:
                                        barcode=w['barcode']
                                        print 'barc',barcode
                                        break;
                                ffpe='false'
                            else:
                                #vuol dire che sto salvando una nuova provetta e quindi il barcode 
                                #risulta essere cio' che e' salvato nella variabile piastra
                                barcode=piastra
                                piastra=''
                                pos=''
                                ffpe='true'
                                lisbarclashub.append(barcode)
                            #valori=str(genid)+','+str(piastra)+','+str(pos)+','+str(numpezzi)+','+barcode+','+tipoaliq+',false, , '
                        #se ho ffpe o of o ch o pl o px il barcode ce l'ho gia' e non devo andare a leggerlo
                        #il barcode e' salvato nella variabile piastra
                        else:
                            barcode=piastra
                            piastra=''
                            pos=''
                            ffpe='true'
                            lisbarclashub.append(barcode)
                                
                        conta=prov['conta']
                        volu=prov['volume']
                        if volu!='-':
                            numpezzi=''
                        
                        valori=genid+','+str(piastra)+','+str(pos)+','+str(numpezzi)+','+barcode+','+tipoaliq+','+ffpe+',,,,,,'+str(data_expl)
                        
                        tipoaliquota= AliquotType.objects.get(abbreviation=tipoaliq)
                        print 'tipo aliquota',tipoaliq
                        a=Aliquot(barcodeID=barcode,
                               uniqueGenealogyID=str(genid),
                               idSamplingEvent=campionamento,
                               idAliquotType=tipoaliquota,
                               timesUsed=pezziusati,
                               availability=disponibile,
                               derived=derivato
                               )
                        print 'a',a
                        a.save()
                        
                        listaal.append(valori)
                        print 'listaaliq',listaal
                        
                        #se sto salvando del sangue ho anche altre feature
                        if volu!='-':
                            #ho il valore in ml e devo trasformarlo in ul
                            vo=float(volu)*1000
                            featvol=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='Volume'))
                            aliqfeaturevol=AliquotFeature(idAliquot=a,
                                                       idFeature=featvol,
                                                       value=vo)
                            aliqfeaturevol.save()
                            print 'featu volume',aliqfeaturevol
                            if conta!='-':
                                featconta=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='Count'))
                                aliqfeatureconta=AliquotFeature(idAliquot=a,
                                                           idFeature=featconta,
                                                           value=conta)
                                aliqfeatureconta.save()
                                print 'aliq',aliqfeatureconta
                                
                        #salvo i campioni normali
                        else:
                            #salvo il numero di pezzi
                            fea=Feature.objects.get(Q(idAliquotType=tipoaliquota)&Q(name='NumberOfPieces'))
                            aliqfeature=AliquotFeature(idAliquot=a,
                                                       idFeature=fea,
                                                       value=numpezzi)
                            aliqfeature.save()
                            print 'aliq',aliqfeature
        
        address=request.get_host()+settings.HOST_URL
        request=SalvaInStorage(listaal,request)
        
        #comunico al LASHub che quei barcode sono stati utilizzati
        prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
        indir=prefisso+address
        url = indir + '/clientHUB/saveAndFinalize/'
        print 'url',url
        values = {'typeO' : 'container', 'listO': str(lisbarclashub)}
        requests.post(url, data=values, verify=False)
        transaction.commit()
        return HttpResponse("ok")
    except Exception, e:
        print 'errore', e    
        transaction.rollback()
        print 'eccezione'
        return HttpResponse("err")'''

@transaction.commit_on_success
@csrf_exempt
@get_functionality_decorator
def DeleteExplants(request):
    if request.method=='POST':
        print 'fine expl'
        print request.POST
        try:
            resp=request.POST.get('response')
            print 'resp',resp
            if resp=="err":
                print 'cancellazione espianti'
                lista_sample=[]
                lista_gen=[]
                disable_graph()
                listaaliq=json.loads(request.POST.get('aliquots'))
                print 'listaaliq',listaaliq
                for tipialiq in listaaliq:
                    print 'tipialiq',tipialiq
                    for topi in listaaliq[tipialiq]:
                        print 'topi',topi
                        for barc in listaaliq[tipialiq][topi]:
                            print 'barc',barc
                            for prov in listaaliq[tipialiq][topi][barc]:
                                print 'prov',prov
                                genid=prov['genID']
                                print 'genid',genid
                                al=Aliquot.objects.get(uniqueGenealogyID=genid)
                                #expl=al.idSamplingEvent.idExplant.id
                                sample=al.idSamplingEvent.id
                                if sample not in lista_sample:
                                    lista_sample.append(sample)
                                    print 'sample',sample
                                print 'al',al                                
                                lista_gen.append(genid)
                                #cancello il numero di pezzi
                                listafeat=AliquotFeature.objects.filter(idAliquot=al)
                                for f in listafeat:
                                    f.delete()
                                #cancello l'aliquota
                                al.delete()
                    
                #conto quanti samplingevent hanno quella serie come riferimento
                sam=SamplingEvent.objects.get(id=lista_sample[0])
                lista_s=SamplingEvent.objects.filter(idSerie=sam.idSerie)
                print 'lunglista',lista_s.count()
                
                for i in range(0,len(lista_sample)):
                    s=SamplingEvent.objects.get(id=lista_sample[i])
                    #devo vedere se quei sampling non hanno altre aliq collegate
                    listal=Aliquot.objects.filter(idSamplingEvent=s)
                    
                    #se non ci sono aliq, allora cancello il sampling
                    if len(listal)==0:
                        s.delete()
                #se gli unici samplingevent che avevano come riferimento quella serie
                #sono quelle da cancellare, cancello anche la serie. Altrimenti la lascio
                if len(lista_sample)==lista_s.count():
                    serie=Serie.objects.get(id=sam.idSerie.id)
                    serie.delete()
                #comunico all'archivio di rimettere a full=false le provette che sono
                #state riempite con le aliq cancellate adesso e di cancellare i blocchetti
                url = Urls.objects.get(default = '1').url + "/cancFFPE/"
                print 'listagen',lista_gen
                val={'lista':json.dumps(lista_gen)}
                enable_graph()
                try:
                    print 'url',url
                    data = urllib.urlencode(val)
                    req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u = urllib2.urlopen(url, data)
                    res1 =  u.read()
                except Exception, e: 
                    transaction.rollback()
                    errore=True
                    variables = RequestContext(request, {'errore':errore})
                    return render_to_response('tissue2/index.html',variables)
                    print e
                if (res1 == 'err'):
                    print 'errore'
                    transaction.rollback()
                    errore=True
                    variables = RequestContext(request, {'errore':errore})
                    return render_to_response('tissue2/index.html',variables)
            return HttpResponse("ok")
        except Exception,e:
            transaction.rollback()
            print 'eccezione',e
            return HttpResponse("err")
    return HttpResponse("ok")





#per cambiare il barcode ai campioni vitali quando vengono passati nella piastra
#transitoria
@transaction.commit_on_success
@csrf_exempt
@get_functionality_decorator
def StoreVitalAliquots(request):
    try:
        if request.method=='POST':
            print request.POST   
            #mi da' la lista delle aliquote
            dic=request.POST.get('dict')
            #serve a trasformare la stringa ottenuta con la post in un dizionario
            dizionario=ast.literal_eval(dic)
            for key,value in dizionario.items():
                ali=Aliquot.objects.get(Q(barcodeID=key)&Q(availability=1))
                print 'ali',ali
                ali.barcodeID=str(value)
                ali.save()
            return HttpResponse("ok")
    except Exception, e:            
        transaction.rollback()
        print 'eccezione',e
        return HttpResponse("err")  
    
@transaction.commit_on_success
@csrf_exempt
@get_functionality_decorator
def StoreVitalAliquotsCanc(request):
    try:
        if request.method=='POST':
            print request.POST   
            #mi da' la lista delle aliquote
            lista=json.loads(request.POST.get('lista'))
            print 'lista',lista
            for gen in lista:
                ali=Aliquot.objects.filter(uniqueGenealogyID=gen,availability=1)
                if ali.count()!=0:
                    print 'ali',ali
                    al=ali[0]
                    al.availability=0
                    al.save()
                    print 'al',al
            return HttpResponse("ok")
    except Exception, e:            
        transaction.rollback()
        print 'eccezione',e
        return HttpResponse("err")    

#per salvare la data di archiviazione quando vengono archiviati i campioni nello storage
@transaction.commit_on_success
@csrf_exempt
@get_functionality_decorator
def StoreArchiveDate(request):
    try:
        if request.method=='POST':
            print request.POST   
            #mi da' la lista delle aliquote
            lis=json.loads(request.POST.get('lisaliq'))           
            #dizionario=ast.literal_eval(dic)
            print 'dizionario',lis
            for key in lis:
                print 'key',key
                #solo se la data di archivio e' nulla salvo una nuova data
                lali=Aliquot.objects.filter(uniqueGenealogyID=key,availability=1,archiveDate=None)
                if len(lali)!=0:
                    ali=lali[0]
                    print 'ali',ali
                    ali.archiveDate=date.today()
                    ali.save()
            return HttpResponse("ok")
    except Exception, e:            
        transaction.rollback()
        print 'eccezione',e
        return HttpResponse("err")  

#funzione per gli altri moduli (uarray, Sanger, ...) che aggiorna il volume rimanente
#in una provetta e, nel caso, la rende indisponibile, oppure assegna una provetta 
#ad un utente rendendola cosi' inaccessibile agli altri
@transaction.commit_on_success
@csrf_exempt
@get_functionality_decorator
def UpdateVolume(request):
    try:
        if request.method=='POST':
            print request.POST
            lista=[]
            #nella post avro' una lista con genid&possessore&volumeattuale
            if 'info' in request.POST:
                lis=request.POST.get('info')
            #elif 'volume' in request.POST:
                #lis=request.POST.get('volume')
                lista=ast.literal_eval(lis)
            print 'lista',lista
            lgen=[]
            for elem in lista:
                val=elem.split('&')
                genid=val[0]                
                print 'genid',genid
                lgen.append(genid)
                
                #in val[1] ho il possessore
                aliq=Aliquot.objects.get(uniqueGenealogyID=genid)
                #devo comunicare allo storage che il container non e' piu' disponibile
                #lo faccio ogni volta perche' il possessore potrebbe cambiare da un campione all'altro
                url1 = Urls.objects.get(default = '1').url + "/container/availability/"
                val1={'lista':json.dumps(lgen),'tube':'0','nome':val[1]}
                print 'url1',url1
                data = urllib.urlencode(val1)
                req = urllib2.Request(url1,data=data, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                res1 =  u.read()
                if res1=='err':
                    transaction.rollback()
                    return HttpResponse("err")
                #in val[2] ho il volume rimanente
                #recupero l'oggetto feature relativo al volume
                featuvol=Feature.objects.get(Q(name='Volume')&Q(idAliquotType=aliq.idAliquotType.id))                
                lvol=AliquotFeature.objects.filter(Q(idAliquot=aliq)&Q(idFeature=featuvol))
                if len(lvol)!=0:
                    vol=lvol[0]
                    print 'vol',vol.value
                    vol.value=float(val[2])
                    vol.save()
                
            lista_es=[]
            #e' la lista delle provette terminate, in cui ho il genid del campione da
            #rendere indisponibile
            if 'exhausted' in request.POST:
                lista_es=request.POST.get('exhausted')
                print 'lista es',lista_es     
                lista2=ast.literal_eval(lista_es)
                gen_da_svuotare=[]
                for elem in lista2:    
                    aliq=Aliquot.objects.get(uniqueGenealogyID=elem)
                    print 'aliq',aliq
                    aliq.availability=0
                    aliq.save()
                    #metto a zero il volume
                    #recupero l'oggetto feature relativo al volume
                    featuvol=Feature.objects.get(Q(name='Volume')&Q(idAliquotType=aliq.idAliquotType.id))
                    lvol=AliquotFeature.objects.filter(Q(idAliquot=aliq)&Q(idFeature=featuvol))
                    if len(lvol)!=0:
                        vol=lvol[0]
                        print 'vol',vol.value
                        vol.value=0.0
                        vol.save()
                    #devo rendere indisponibile anche la provetta chiamando la API dello
                    #storage
                    gen_da_svuotare.append(aliq.uniqueGenealogyID)
                    
                #mi collego allo storage per svuotare le provette contenenti le aliq
                #esaurite
                address=Urls.objects.get(default=1).url
                url = address+"/full/"
                print url
                values = {'lista' : json.dumps(gen_da_svuotare), 'tube': 'empty','canc':True,'operator':None}
                data = urllib.urlencode(values)
                req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                urllib2.urlopen(req)
                #urllib2.urlopen(url, data) 
            return HttpResponse("ok")
    except Exception, e:            
        transaction.rollback()
        print 'eccezione',e
        return HttpResponse("err")  


def Query(request):
    gen_list={'genID':['CRC0499BMH0000000000VT0200','OVR0003SMH0000000000D02000']}
    #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
    #indirizzo=request.get_host()+settings.HOST_URL
    indir=settings.DOMAIN_URL+settings.HOST_URL
    url=indir+'/api/query/aliquots'
    values_to_send={'predecessor':'Containers', 'list':gen_list, 'successor': 'End', 'parameter': 'GROUP BY', 'values':''}
    data = urllib.urlencode(values_to_send)
    req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res = json.loads(u.read())
    return HttpResponse("ok")

def ProvaCanc(request):
    #struttura dati per il salvataggio degli espianti da file
    gen_list={'VT':{'topo':{'40':[{'genID':'GIS0001LMH0000000000RL0100','pos': 'C1', 'qty': '1'},{'genID':'GIS0001LMH0000000000RL0200','pos': 'A3', 'qty': '4'}]}}}
    #gen_list=['CRC0058LMX0A02201TUMD11000','CRC0058LMX0A02201TUMD10000']
    #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
    #indirizzo=request.get_host()+settings.HOST_URL
    indir=settings.DOMAIN_URL+settings.HOST_URL
    url=indir+'/api/save/batchexplant/'
    print 'url',url
    values_to_send={'explants':json.dumps(gen_list),'operator':'ema','date':'2014-08-04'}
    data = urllib.urlencode(values_to_send)
    req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
    print 'req',req
    u = urllib2.urlopen(req)
    res = u.read()
    return HttpResponse(res)

#per provare la post alla API che salva gli eseprimenti eseguiti da un altro modulo
def ProvaExperiment(request):
    gen_diz={'CRC0014LMH0000000000D04000':{'volume':8,'exhausted':False,'plan':False},'CRC0014LMX0A02201TUMD01000':{'volume':1,'exhausted':True,'plan':False}}
    #gen_diz=['LNF0001LYH0000000000D05000','LNF0001LYH0000000000D03000']
    #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
    #indirizzo=request.get_host()+settings.HOST_URL
    indir=settings.DOMAIN_URL+settings.HOST_URL
    url=indir+'/api/experiment/confirm'
    #url=indir+'/api/experiment/canc'
    values_to_send={'aliquots':json.dumps(gen_diz),'experiment':'Collaboration','operator':'emanuele.geda','undo':False,'notes':'yyyyyy'}
    data = urllib.urlencode(values_to_send)
    req = urllib2.Request(url,data=data, headers={"workingGroups" : 'Bertotti_WG'})
    u = urllib2.urlopen(req)
    #u = urllib2.urlopen(url, data)
    res = json.loads(u.read())
    return HttpResponse("ok")

#per provare la post alla API di Funnel
def ProvaFunnel(request):
    gen_diz=[{'barcode':'AA-barc3','project':'Funnel','localId':'paziente100','ICcode':'paziente100','type':'CRC','tissue':'LI','operator':'emanuele.geda'},
             {'barcode':'AA-barc5','project':'Funnel','localId':'paziente100','ICcode':'paziente100','type':'CRC','tissue':'00','operator':'emanuele.geda'},
             {'barcode':'AA-barc6','project':'Funnel','localId':'paziente100','ICcode':'paziente100','type':'CRC','tissue':'LI','operator':'emanuele.geda'}]
    #gen_diz=[{'childBarcode':'dnafun9','fatherSpecimenBarcode':'AA-barc1','aliquotType':'DNA','volume':'33','concentration':'3','operator':'emanuele.geda'},
    #         {'childBarcode':'psfun10','fatherSpecimenBarcode':'AA-barc1','aliquotType':'SLIDE','thickness':'3','nSlices':'2','operator':'emanuele.geda'},
    #         {'childBarcode':'psfun11','fatherSpecimenBarcode':'AA-barc1','aliquotType':'SLIDE','thickness':'4','nSlices':'3','operator':'emanuele.geda'},
    #         {'childBarcode':'psfun12','fatherSpecimenBarcode':'AA-barc1','aliquotType':'HE','thickness':'5','nSlices':'1','operator':'emanuele.geda'},
    #         {'childBarcode':'psfun13','fatherSpecimenBarcode':'AA-barc3','aliquotType':'HE','thickness':'6','nSlices':'4','operator':'emanuele.geda'},
    #         {'childBarcode':'dnafun14','fatherSpecimenBarcode':'AA-barc3','aliquotType':'DNA','volume':'66','concentration':'6','operator':'emanuele.geda'}]
    #gen_diz=[{'operator':'francesca.cottino','vials':['psfun15','psfun16']},{'operator':'emanuele.geda','vials':['dnafun10']}]
    indir=settings.DOMAIN_URL+settings.HOST_URL
    url=indir+'/api/blocks/'
    #url=indir+'/api/derivedsamples/'
    #url=indir+'/api/vials/'
    values_to_send=json.dumps({'specimens':gen_diz,'operator':'emanuele.geda'})
    '''data = urllib.urlencode(values_to_send)
    req = urllib2.Request(url,data=data, headers={"workingGroups" : 'admin'})
    u = urllib2.urlopen(req)
    res = json.loads(u.read())'''
    r=requests.post(url, data=values_to_send, verify=False, headers={'Content-type': 'application/json'})
    #devo fare il controllo se la POST ha avuto successo
    status=r.status_code
    print 'status',status
    print 'text',r.text
    return HttpResponse("ok")

#Dato in ingresso un file con una lista di gen, li mette ad esauriti
@transaction.commit_on_success
@laslogin_required
@login_required
def CancAliquot(request):
    try:
        if request.method=='POST':
            enable_graph()
            disable_graph()
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file con la lista dei gen
            f1=listafile[0]
            lis_aliq = f1.readlines()
            f1.close()
            
            svuot=[]
            for l in lis_aliq:
                valori=l.split(';')
                ge=valori[0].strip()
                al=Aliquot.objects.get(uniqueGenealogyID=ge)
                al.availability=0
                al.save()
                svuot.append(ge)
            print 'svuot',svuot
            if len(svuot)!=0:
                svuotare=json.dumps(svuot)
                #mi collego allo storage per svuotare le provette contenenti le aliq
                #esaurite
                address=Urls.objects.get(default=1).url
                url = address+"/full/"
                print url
                values = {'lista' : svuotare, 'tube': 'empty','canc':True}
                data = urllib.urlencode(values)
                req = urllib2.Request(url,data=data, headers={"workingGroups" : 'admin'})
                urllib2.urlopen(req)
                
            return HttpResponse("ok")
        else:
            form = HistoricForm()    
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#Dato in ingresso un file con una lista di gen, li ripristina
@transaction.commit_on_success
@laslogin_required
@login_required
def RestoreAliquot(request):
    try:
        if request.method=='POST':
            enable_graph()
            disable_graph()
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file con la lista dei gen
            f1=listafile[0]
            lis_aliq = f1.readlines()
            f1.close()
            
            laliq=[]
            for l in lis_aliq:
                valori=l.split(';')
                ge=valori[0].strip()
                #al=Aliquot.objects.get(uniqueGenealogyID=ge)
                #al.availability=1
                #al.save()
                laliq.append(ge)
            print 'laliq',laliq
            if len(laliq)!=0:
                #mi collego allo storage per ripristinare le provette contenenti queste aliq e le aliquote stesse
                address=Urls.objects.get(default=1).url
                url = address+"/api/restore/"
                print 'url',url
                values = {'lista' : json.dumps(laliq)}
                data = urllib.urlencode(values)
                req = urllib2.Request(url,data=data, headers={"workingGroups" : 'admin'})
                u=urllib2.urlopen(req)
                res=json.loads(u.read())
                print 'res',res
                if res!='ok':
                    raise Exception()
            
            for l in lis_aliq:
                valori=l.split(';')
                ge=valori[0].strip()
                al=Aliquot.objects.get(uniqueGenealogyID=ge)
                al.availability=1
                al.save()
                
            return HttpResponse("ok")
        else:
            form = HistoricForm()    
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_tess.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#Dato in ingresso un file con una lista di gen e i rispettivi pezzi, aggiorna il numero di pezzi salvato
@transaction.commit_on_success
@laslogin_required
@login_required
def ChangeAliquotPieces(request):
    try:
        if request.method=='POST':
            enable_graph()
            disable_graph()
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            listafile=request.FILES.getlist('file')
            
            #e' il file con la lista dei gen
            f1=listafile[0]
            lis_aliq = f1.readlines()
            f1.close()
            
            for l in lis_aliq:
                valori=l.split('\t')
                gen=valori[0].strip()
                pezzi=valori[1].strip()
                al=Aliquot.objects.get(uniqueGenealogyID=gen)
                print 'al',al
                lfea=Feature.objects.filter(Q(idAliquotType=al.idAliquotType)&Q(name='NumberOfPieces'))
                if len(lfea)!=0:                    
                    lalfeat=AliquotFeature.objects.filter(idAliquot=al,idFeature=lfea[0])
                    print 'lalfeat',lalfeat
                    if len(lalfeat)!=0:
                        lalfeat[0].value=pezzi
                        lalfeat[0].save()                
                
            return HttpResponse("ok")
        else:
            form = HistoricForm()    
        variables = RequestContext(request, {'form':form})
        return render_to_response('tissue2/historic/storico_sampl.html',variables)
    except ErrorHistoric as e:
        print 'My exception occurred, value:', e.value
        transaction.rollback()
        return HttpResponse("err")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#Visualizza la lista delle procedure di block/unblock per mismatch eseguite finora, filtrando solo per unblock (ossia non visualizza le delete)
#L'utente sceglie un punto di partenza e il sistema genera la lista delle aliquote che risultano sbloccate alla data corrente applicando
#in successione le procedure di blocco/sblocco a partire da quella selezionata.
#Il file generato deve poi essere caricato nella view las.ircc.it/biobank/restore/aliquot
def ListAliquotsToRestore(request):
    if request.method == 'POST':
        try:
            proc_id = request.POST['proc_id']
        except:
            procedures = BlockProcedureBatch.objects.filter(delete=False).order_by('timestamp')
            return render_to_response('tissue2/historic/storico_blockproc.html', RequestContext(request, {'procedures': procedures, 'post_url': reverse('tissue.views.ListAliquotsToRestore')}))
        try:
            initial = BlockProcedureBatch.objects.get(pk=proc_id)
        except:
            return HttpResponse("error: BlockProcedureBatch with pk=%d does not exist" % proc_id)

        restored_aliquots = set()

        for bpb in BlockProcedureBatch.objects.filter(timestamp__gte=initial.timestamp).order_by('timestamp'):
            for bp in bpb.blockprocedure_set.all():
                if bpb.delete == False:
                    restored_aliquots.update([bb.genealogyID for bb in bp.blockbioentity_set.all() if GenealogyID(bb.genealogyID).isAliquot()])
                else:
                    restored_aliquots.difference_update([bb.genealogyID for bb in bp.blockbioentity_set.all() if GenealogyID(bb.genealogyID).isAliquot()])

        f = tempfile.NamedTemporaryFile(delete=False)
        f.write("\n".join(restored_aliquots))
        f.close()
        resp = HttpResponse(FileWrapper(open(f.name,"rb")), content_type=mimetypes.guess_type(f.name)[0])
        resp['Content-Disposition'] = 'attachment; filename="Restored_aliquots_%s_%s.txt"' % (initial.operator.username, initial.timestamp.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %I:%M %p"))
        os.remove(f.name)
        return resp
    else:
        procedures = BlockProcedureBatch.objects.filter(delete=False).order_by('timestamp')
        return render_to_response('tissue2/historic/storico_blockproc.html', RequestContext(request, {'procedures': procedures, 'post_url': reverse('tissue.views.ListAliquotsToRestore')}))

#Visualizza la lista delle procedure di block/unblock per mismatch eseguite finora, filtrando solo per block (ossia non visualizza le change group)
#L'utente sceglie un punto di partenza e il sistema genera la lista delle aliquote che risultano bloccate alla data corrente applicando1
#in successione le procedure di blocco/sblocco a partire da quella selezionata.
#Il file generato deve poi essere caricato nella view https://las.ircc.it/biobank/aliquot/notavailable/ per trasferire le aliquote a un altro gruppo (e.g. QCInspector_WG)
def ListDeletedAliquots(request):
    if request.method == 'POST':
        try:
            proc_id = request.POST['proc_id']
        except:
            procedures = BlockProcedureBatch.objects.filter(delete=True).order_by('timestamp')
            return render_to_response('tissue2/historic/storico_blockproc.html', RequestContext(request, {'procedures': procedures, 'post_url': reverse('tissue.views.ListDeletedAliquots')}))
        try:
            initial = BlockProcedureBatch.objects.get(pk=proc_id)
        except:
            return HttpResponse("error: BlockProcedureBatch with pk=%d does not exist" % proc_id)

        deleted_aliquots = set()

        for bpb in BlockProcedureBatch.objects.filter(timestamp__gte=initial.timestamp).order_by('timestamp'):
            for bp in bpb.blockprocedure_set.all():
                if bpb.delete == True:
                    deleted_aliquots.update([bb.genealogyID for bb in bp.blockbioentity_set.all() if GenealogyID(bb.genealogyID).isAliquot()])
                else:
                    deleted_aliquots.difference_update([bb.genealogyID for bb in bp.blockbioentity_set.all() if GenealogyID(bb.genealogyID).isAliquot()])

        f = tempfile.NamedTemporaryFile(delete=False)
        f.write("\n".join(deleted_aliquots))
        f.close()
        resp = HttpResponse(FileWrapper(open(f.name,"rb")), content_type=mimetypes.guess_type(f.name)[0])
        resp['Content-Disposition'] = 'attachment; filename="Deleted_aliquots_%s_%s.txt"' % (initial.operator.username, initial.timestamp.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %I:%M %p"))
        os.remove(f.name)
        return resp
    else:
        procedures = BlockProcedureBatch.objects.filter(delete=True).order_by('timestamp')
        return render_to_response('tissue2/historic/storico_blockproc.html', RequestContext(request, {'procedures': procedures, 'post_url': reverse('tissue.views.ListDeletedAliquots')}))

