from archive.forms import *
from archive.models import *
from archive.utils import *
from django import forms
from django.db import transaction
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.db.models import Q, Count
from django.conf import settings
import urllib, urllib2, os, json, ast,requests,datetime
from django.utils import simplejson
from django.contrib.auth.decorators import user_passes_test
from api.handlers import InfoContHandler
from apisecurity.decorators import *
from global_request_middleware import *
from api.utils import *
from django.utils import timezone
import django.utils.html as duh
from LASAuth.decorators import laslogin_required

def error(request):
    return render_to_response('error.html', RequestContext(request))

def start_redirect(request):
    #print "this is the URL I received: " +request.path
    return HttpResponseRedirect(reverse('archive.views.index'))

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
                return HttpResponseRedirect(reverse('archive.views.index'))
            else:
                message = "Bad username or password."
                return render_to_response('login.html', {'message': message}, RequestContext(request))
        else:
            message = "Invalid input."
            return render_to_response('login.html', {'message': message}, RequestContext(request))
    return render_to_response('login.html', RequestContext(request))

@laslogin_required
@login_required
def logout(request):
    auth.logout(request)
    for sesskey in request.session.keys():
        del request.session[sesskey]
    #return HttpResponseRedirect(reverse('archive.views.login'))
    return HttpResponse("loggedout")

@laslogin_required
@login_required
def index(request):
    CancSession(request)
    return render_to_response('index.html',RequestContext(request))

class ErrorPlate(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ErrorPlateSpecification(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

'''#per inserire nuove piastre dato il file di configurazione letto dallo scanner
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_insert_new_container_instance'),login_url=settings.BASE_URL+'/archive/error/')
@permission_decorator('archive.can_view_SMM_insert_new_container_instance')
def InsertPlate(request):
    if request.method=='POST':
        print request.POST
        print request.FILES
        form=PlateInsertForm(request.POST,request.FILES)
        form2=NewContainerForm(request.POST)
        try:
            if form.is_valid():
                barcodepias=' '
                listapiastre=[]
                print 'valido'
                aim=DefaultValue.objects.get(id=request.POST.get('aim'))
                if 'barcode' in request.POST:
                    barcodepias=request.POST.get('barcode').strip()
                    if barcodepias!='':
                        #faccio la chiamata al LASHub per vedere se esiste gia' il codice
                        lista=[]
                        lista.append(barcodepias)
                        if Barcode_unico(lista, request):
                            raise ErrorPlate(barcodepias)
                aliquota_tipo=DefaultValue.objects.get(id=request.POST.get('Aliquot_Type'))
                print 'aim.name',aim.longName
                tipo_cont=request.POST.get('cont_tipo')
                t_cont=ContainerType.objects.get(id=tipo_cont) 
                geom=request.POST.get('geometry')
                geo=Geometry.objects.get(id=geom)           
                regole=json.loads(geo.rules)
                dimensioni=regole['dimension']
                xDim=str(dimensioni[1])
                yDim=str(dimensioni[0])
                #xDim=request.POST.get('x').strip()
                #yDim=request.POST.get('y').strip()
                print 'x',xDim
                print 'y',yDim
                #per il lashub
                prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
                address=request.get_host()+settings.HOST_URL
                indir=prefisso+address
                url = indir + '/clientHUB/saveAndFinalize/'
                print 'url',url
                
                provetta=ContainerType.objects.get(name='Tube')
                #la nuova piastra e' operativa o transitoria 
                if aim.longName!='Stored' and aim.longName!='Extern':
                    storage=None
                    geom_tube=Geometry.objects.get(name='1x1')
                    if 'file_plate' in request.FILES:
                        listafile=request.FILES.getlist('file_plate')
                        print 'f',listafile
                        print '0',listafile[0]
                        #creo le regole per la geometria della nuova piastra
                        #stringa=creaGeometria(xDim, yDim)
                        
                        #scandisce ogni singolo file
                        for f in listafile:
                            #f.chunks divide il file in macropezzi da vari kb l'uno
                            for a in f.chunks():
                                #per cancellare eventuali \n alla fine del file
                                a=a.strip()
                                #c e' un vettore e in ogni posto c'e' una riga del file
                                c=a.split('\n')
                                print 'c',c
                                #verifico che nel file ci siano tutte le posizioni della piastra
                                numeroposti=int(xDim)*int(yDim)
                                print 'numposti',numeroposti
                                if (len(c)!=(numeroposti+1)):
                                    raise ErrorDimension((len(c))-1)
                                
                                riga1=c[0].strip()
                                r=riga1.split(' ')
                                barcode=r[1]
                                print 'barc',barcode
                                if barcode!='':
                                    #faccio la chiamata al LASHub per vedere se esiste gia' il codice
                                    lista=[]
                                    lista.append(barcode)
                                    if Barcode_unico(lista, request):
                                        raise ErrorPlate(barcode)
                                
                                #salvo la nuova piastra
                                p,creato=Container.objects.get_or_create(idContainerType=t_cont,
                                         idFatherContainer=storage,
                                         idGeometry=geo,
                                         barcode=barcode,
                                         availability=1,
                                         full=1)
                                print 'p',p
                                p.save()
                                colonne=0
                                
                                lisbarcc=[]
                                for j in range(1,len(c)):
                                    c[j]=c[j].strip()
                                    #c[i] e' formato da posizione,barcode
                                    v=c[j].split(',')
                                    barc=v[1].strip()
                                    if barc!='No Tube':
                                        lisbarcc.append(barc)
                                if Barcode_unico(lisbarcc, request):
                                    raise ErrorPlate(barcode)
                                
                                for i in range(1,len(c)):
                                    #c[i] e' la singola riga del file
                                    #il .strip toglie gli eventuali spazi e il \r finale nella riga
                                    c[i]=c[i].strip()
                                    #c[i] e' formato da posizione,barcode
                                    v=c[i].split(',')
                                    pos=v[0].strip()
                                    barc=v[1].strip()
                                    if pos[2]!='0':
                                        pos=pos.replace('0','')
                                    #faccio un controllo per vedere se il num di colonne
                                    #inserite dall'utente coincide con quello del file
                                    print 'pos',pos
                                    if pos[0]=='A':
                                        colonne=colonne+1
                                    if barc!='No Tube':
                                        cont=Container(idContainerType=provetta,
                                                 idFatherContainer=p,
                                                 idGeometry=geom_tube,
                                                 position=pos,
                                                 barcode=barc,
                                                 availability=1,
                                                 full=0)
                                        cont.save()
                                print 'colonne',colonne
                                if int(colonne)!=int(yDim):
                                    raise ErrorPlateSpecification(colonne)
                                nome='plate'+yDim+'x'+xDim

                                #salvo le feature della nuova piastra
                                feataliq=Feature.objects.get(name='AliquotType')
                                feataim=Feature.objects.get(name='PlateAim')
                                aliqfeat=ContainerFeature(idFeature=feataliq,
                                                          idContainer=p,
                                                          value=aliquota_tipo.abbreviation)
                                aliqfeat.save()
                                aimfeat=ContainerFeature(idFeature=feataim,
                                                         idContainer=p,
                                                         value=aim.longName)
                                aimfeat.save()
                                
                                if aim.longName=='Operative':
                                    tipopi='Working'
                                elif aim.longName=='Stored':
                                    tipopi='Archive'
                                else:
                                    tipopi=aim.longName
                                listapiastre.append(ReportPlateToHtml(p.barcode,tipopi,aliquota_tipo.longName, xDim, yDim,'', '', '', 'n')) 
                                #finalizzo i dati sul LASHUB
                                lisbarcc.append(barcode)
                                values2 = {'typeO' : 'container', 'listO': str(lisbarcc)}
                                requests.post(url, data=values2, verify=False, headers={"workingGroups" : get_WG_string()})               
                                
                    #ho una piastra vitale e operativa
                    else:
                        #if barcodepias!='':
                            #faccio la chiamata al LASHub per vedere se esiste gia' il codice
                            #if Barcode_unico(barcodepias, request):
                                #raise ErrorPlate(barcodepias)
                        #salvo la nuova piastra
                        p,creato=Container.objects.get_or_create(idContainerType=t_cont,
                                 idFatherContainer=storage,
                                 idGeometry=geo,
                                 barcode=barcodepias,
                                 availability=1,
                                 full=1)
                        print 'p',p
                        p.save()
                        pias=Container.objects.filter(barcode=barcodepias)
                        print 'pias', pias
                        #if pias.count()>1 and barcodepias!='':
                        
                        liscodici=[]
                        for i in range(0,int(xDim)):
                            for j in range(1,(int(yDim)+1)):
                                pos=chr(i+ord('A'))+str(j)
                                barcod=barcodepias+pos
                                liscodici.append(barcod)
                        if Barcode_unico(liscodici, request):
                            raise ErrorPlate(barcode)
                                
                        for i in range(0,int(xDim)):
                            for j in range(1,(int(yDim)+1)):
                                #chr converte da ascii a carattere, ord da carattere ad ascii
                                pos=chr(i+ord('A'))+str(j)
                                cont=Container(idContainerType=provetta,
                                         idFatherContainer=p,
                                         idGeometry=geom_tube,
                                         position=pos,
                                         barcode=barcodepias+pos,
                                         availability=1,
                                         full=0)
                                cont.save()

                        #salvo le feature della nuova piastra
                        feataliq=Feature.objects.get(name='AliquotType')
                        feataim=Feature.objects.get(name='PlateAim')
                        aliqfeat=ContainerFeature(idFeature=feataliq,
                                                  idContainer=p,
                                                  value=aliquota_tipo.abbreviation)
                        aliqfeat.save()
                        aimfeat=ContainerFeature(idFeature=feataim,
                                                 idContainer=p,
                                                 value=aim.longName)
                        aimfeat.save()
                        if aim.longName=='Operative':
                            tipopi='Working'
                        elif aim.longName=='Stored':
                            tipopi='Archive'
                        else:
                            tipopi=aim.longName
                            
                        listapiastre.append(ReportPlateToHtml(p.barcode,tipopi,aliquota_tipo.longName, xDim, yDim, '', '', '', 'n'))
                        #finalizzo i dati sul LASHUB
                        liscodici.append(barcodepias)
                        values2 = {'typeO' : 'container', 'listO': str(liscodici)}
                        requests.post(url, data=values2, verify=False, headers={"workingGroups" : get_WG_string()})
                                
                #la nuova piastra e' stored o extern
                else:
                    posiz=request.POST.get('position').strip()
                    posiz=posiz.upper()
                    rack=request.POST.get('rack').strip()
                    r=Container.objects.get(barcode=rack)
                    print 'rack',rack

                    p=Container(idContainerType=t_cont,
                             idFatherContainer=r,
                             idGeometry=geo,
                             position=posiz,
                             barcode=barcodepias,
                             availability=1,
                             full=0)
                    print 'p',p
                    p.save()
                    
                    #devo vedere se il container padre si e' riempito con l'aggiunta di questo
                    #container
                    lista_c=Container.objects.filter(idFatherContainer=r)
                    regole=json.loads(r.idGeometry.rules)
                    dimensioni=regole['dimension']
                    xDimens=dimensioni[1]
                    yDimens=dimensioni[0]
                    posto_tot=int(xDimens)*int(yDimens)
                    print 'posti_tot',posto_tot
                    print 'lista',len(lista_c)
                    if len(lista_c)>=int(posto_tot):
                        r.full=1
                        print 'cont pieno'
                        r.save()

                    #salvo le feature della nuova piastra
                    feataliq=Feature.objects.get(name='AliquotType')
                    feataim=Feature.objects.get(name='PlateAim')
                    aliqfeat=ContainerFeature(idFeature=feataliq,
                                              idContainer=p,
                                              value=aliquota_tipo.abbreviation)
                    aliqfeat.save()
                    aimfeat=ContainerFeature(idFeature=feataim,
                                             idContainer=p,
                                             value=aim.longName)
                    aimfeat.save()
                    if aim.longName=='Operative':
                        tipopi='Working'
                    elif aim.longName=='Stored':
                        tipopi='Archive'
                    else:
                        tipopi=aim.longName

                    listapiastre.append(ReportPlateToHtml(p.barcode,tipopi,aliquota_tipo.longName, xDim, yDim, p.idFatherContainer.barcode, p.idFatherContainer.idFatherContainer.barcode,posiz, 'n'))
                    #finalizzo i dati sul LASHUB
                    liss=[]
                    liss.append(barcodepias)
                    values2 = {'typeO' : 'container', 'listO': str(liss)}
                    requests.post(url, data=values2, verify=False, headers={"workingGroups" : get_WG_string()})
                                    
                print 'lista',listapiastre
                fine=True
                variables = RequestContext(request,{'fine':fine,'lista':listapiastre})
                return render_to_response('plates/plate_insert.html',variables)
            else:
                form2=NewContainerForm()
                variables = RequestContext(request, {'form':form,'form2':form2})
                return render_to_response('plates/plate_insert.html',variables)
        except ErrorPlate as e:
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore':e.value})
            return render_to_response('plates/plate_insert.html',variables)
        except ErrorPlateSpecification as e:
            print 'My exception occurred, value:', e.value
            transaction.rollback()
            variables = RequestContext(request, {'errorespecifiche':e.value})
            return render_to_response('plates/plate_insert.html',variables)
        except ErrorDimension as e:
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore_dim':e.value})
            return render_to_response('plates/plate_insert.html',variables)
        except Exception,e:
            transaction.rollback()
            errore=True
            print 'err',e
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('index.html',variables)
    else:
        form = PlateInsertForm() 
        form2=NewContainerForm()      
    variables = RequestContext(request, {'form':form,'form2':form2})
    return render_to_response('plates/plate_insert.html',variables)  '''

'''#per cambiare lo stato di una piastra
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_change_plate_status'),login_url=settings.BASE_URL+'/archive/error/')
@permission_decorator('archive.can_view_SMM_change_plate_status')
def ChangePlate(request):
    if request.method=='POST':
        print request.POST
        form=PlateChangeForm(request.POST)
        try:
            if form.is_valid():
                lista=[]
                lista_tip=[]
                piastra_selezionata=[]
                fase2=True
                barcode=request.POST.get('barcode').strip()
                #devo verificare che il barcode sia di una piastra e non di una
                #provetta o di un rack ad esempio
                tipo=GenericContainerType.objects.filter(name='Plate/Box')
                lista_tip.append(Q(**{'idGenericContainerType': tipo} ))
                listatipi=ContainerType.objects.filter(Q(reduce(operator.or_, lista_tip)))
                print 'listatipi',listatipi
                for l in listatipi:
                    lista.append( Q(**{'idContainerType': l} ))
                if len(lista)!=0:
                    piastra_selezionata=Container.objects.filter(Q(barcode=barcode)&Q(reduce(operator.or_, lista)))
                
                    if len(piastra_selezionata)==0:
                        raise ErrorPlate(barcode)
                request.session['selez']=piastra_selezionata
                #se la piastra e' operativa e vitale, impedisco qualsiasi cambiamento
                scopo=Feature.objects.get(name='PlateAim')
                aliqtipo=Feature.objects.get(name='AliquotType')
                contfeatscopo=ContainerFeature.objects.get(Q(idFeature=scopo)&Q(idContainer=piastra_selezionata[0]))
                contfeataliq=ContainerFeature.objects.get(Q(idFeature=aliqtipo)&Q(idContainer=piastra_selezionata[0]))
                print 'scopo',contfeatscopo.value
                print 'aliq',contfeataliq.value
                if contfeatscopo.value=='Operative' and contfeataliq.value=='VT':
                    print 'operativa e vitale'
                    raise ErrorPlateSpecification(barcode)
                print piastra_selezionata[0]
                
                #devo verificare che la piastra sia vuota prima di cambiare le sue caratteristiche
                lisfigli=Container.objects.filter(idFatherContainer=piastra_selezionata[0],full=1)
                #if len(lisfigli)!=0:
                #    raise ErrorDimension(barcode)
                
                form_nuovo=PlateChangeForm2()
                #p[0] e' l'unica piastra che mi restituisce la funzione filter()
                if contfeatscopo.value=='Operative':
                    contfeatscopo.value='Working'
                if contfeatscopo.value=='Stored':
                    contfeatscopo.value='Archive'
                variables = RequestContext(request, {'form':form,'piastra':piastra_selezionata[0],'scopo':contfeatscopo.value,'tipo':contfeataliq.value,'fase2':fase2,'form2':form_nuovo})
                return render_to_response('plates/plate_change.html',variables)
            else:
                variables = RequestContext(request, {'form':form})
                return render_to_response('plates/plate_change.html',variables)
        except ErrorPlate as e:
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore':e.value})
            return render_to_response('plates/plate_change.html',variables)
        except ErrorPlateSpecification as e:
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore2':e.value})
            return render_to_response('plates/plate_change.html',variables)
        
        except ErrorDimension as e:
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore3':e.value})
            return render_to_response('plates/plate_change.html',variables)
        
        except Exception,e:
            print 'errore',e
            return HttpResponseRedirect(reverse('archive.views.index'))
    else:
        form = PlateChangeForm()
    variables = RequestContext(request, {'form':form})
    return render_to_response('plates/plate_change.html',variables)'''

#per cambiare lo stato di un container nel caso sia vuoto
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_change_plate_status'),login_url=settings.BASE_URL+'/archive/error/')
@permission_decorator('archive.can_view_SMM_change_plate_status')
def ChangePlate(request):
    try:
        print request.POST
        if 'final' in request.POST:
            #mi occupo del resoconto finale
            lista=[]
            listafin=request.session.get('lisChangeContainer')
            print 'listafin2',listafin
            intest='<th>Container</th><th>Container type</th><th>Biological content</th><th>Geometry</th><th>Disposable</th>'
            for elem in listafin:
                val=elem.split('|')
                dati='<tr align="center"><td>'+val[0]+'</td><td>'+val[1]+'</td><td>'+val[2]+'</td><td>'+ val[3] +'</td><td>'+ val[4] +'</td></tr>'
                lista.append(dati)
            variables = RequestContext(request, {'fine':True,'intest':intest,'dati':lista})
            return render_to_response('plates/plate_change.html',variables)
        if 'salva' in request.POST:
            lisreport=[]
            aliqtipo=Feature.objects.get(name='AliquotType')
            dizdati=json.loads(request.POST.get('dati'))
            print 'dizdati',dizdati
            #la chiave e' il barcode
            for key in dizdati.keys():
                print 'k',key
                diztmp=dizdati[key]
                cont=Container.objects.get(barcode=key)
                
                tipocont=diztmp['conttipo']
                conttipo=ContainerType.objects.get(id=tipocont)
                cont.idContainerType=conttipo
                
                nomegeom=diztmp['geometry']
                lisgeometria=Geometry.objects.filter(name=nomegeom)
                if len(lisgeometria)!=0:
                    geometria=lisgeometria[0]
                else:
                    #devo creare la nuova geometria
                    gg=nomegeom.split('x')
                    righe=gg[0]
                    colonne=gg[1]
                    stringa=creaGeometria(righe, colonne)
                   
                    geometria=Geometry(name=nomegeom,
                                  rules=stringa)
                    geometria.save()
                    print 'geom',geometria
                cont.idGeometry=geometria
                
                uso=diztmp['uso']
                print 'uso',uso
                cont.oneUse=0
                if uso=='True':
                    cont.oneUse=1                        
                
                cont.save()
                #mi occupo del contenuto biologico
                lisaliqabbr=diztmp['aliqabbr']
                #tolgo i valori che il cont ha gia' e assegno quelli nuovi
                lfeatvecchi=ContainerFeature.objects.filter(idFeature=aliqtipo,idContainer=cont)
                print 'lfeatvecchi',lfeatvecchi
                for feat in lfeatvecchi:
                    feat.delete()
                lisabbr=lisaliqabbr.split('-')
                for val in lisabbr:
                    feat=ContainerFeature(idFeature=aliqtipo,
                                          idContainer=cont,
                                          value=val)
                    feat.save()
                    print 'feat',feat
                
                #formata da barc cont|tipo cont|aliquote|geometria|monouso
                stringareport=key+'|'+conttipo.actualName+'|'+lisaliqabbr+'|'+nomegeom+'|'+uso
                lisreport.append(stringareport)
                
            request.session['lisChangeContainer']=lisreport                    
            return HttpResponse()        

        lis=SelectAliquot()
        form = ChangeContainerForm()
        variables = RequestContext(request, {'form':form,'lista':lis})
        return render_to_response('plates/plate_change.html',variables)
    except Exception,e:
        print 'err',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('index.html',variables)

'''#per salvare le informazioni sul nuovo stato di una piastra
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_change_plate_status'),login_url=settings.BASE_URL+'/archive/error/')
@permission_decorator('archive.can_view_SMM_change_plate_status')
def ChangePlateFinal(request):
    rack=None
    position=None
    try:
        if request.method=='POST':
            print request.POST
            piastra_selezionata=request.session.get('selez')
            print 'selez',piastra_selezionata
            form2=PlateChangeForm2(request.POST)
            if form2.is_valid():
                print 'valido'
                aim=DefaultValue.objects.get(id=request.POST.get('aim'))
                aliquota_tipo=DefaultValue.objects.get(id=request.POST.get('Aliquot_Type'))
                
                pi=Container.objects.get(barcode=piastra_selezionata[0].barcode)
                #la piastra e' stored o extern
                if 'storage' in request.POST:
                    numrack=request.POST.get('rack').strip()
                    position=request.POST.get('position').strip()
                    position=position.upper()
                    rack=Container.objects.get(barcode=numrack)
                    
                #cambio i valori della piastra
                pi.idFatherContainer=rack
                pi.position=position
                pi.save()
                #mi occupo delle feature
                scopo=Feature.objects.get(name='PlateAim')
                aliqtipo=Feature.objects.get(name='AliquotType')
                contfeatscopo=ContainerFeature.objects.get(Q(idFeature=scopo)&Q(idContainer=pi))
                contfeataliq=ContainerFeature.objects.get(Q(idFeature=aliqtipo)&Q(idContainer=pi))
                contfeatscopo.value=aim.longName 
                contfeatscopo.save()
                contfeataliq.value=aliquota_tipo.abbreviation
                contfeataliq.save()
                
                if aim.longName=='Stored':
                    #prendo tutti i figli per impostare la data di archiviazione nella banca
                    lisfigli=Container.objects.filter(idFatherContainer=pi,full=1)
                    dictcontainer={}
                    for cont in lisfigli:
                        dictcontainer[cont.barcode]=cont
                    address = Urls.objects.get(default = '1').url
                    url=address+'/store/archivedate/'
                    val={'dict':dictcontainer.keys()}
                    data = urllib.urlencode(val)
                    req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u = urllib2.urlopen(url, data)
                    res =  u.read()
                    if(res=='err'):
                        transaction.rollback()
                        variables = RequestContext(request, {'errore':True})
                        return render_to_response('index.html',variables)
                
                fine=True
                variables = RequestContext(request, {'fine':fine})
                return render_to_response('plates/plate_change.html',variables)
            else:
                fase2=True
                print 'fase2'
                form=PlateChangeForm()
                variables = RequestContext(request, {'form':form,'form2':form2,'fase2':fase2,'piastra':piastra_selezionata[0]})
                return render_to_response('plates/plate_change.html',variables)
        else:
            form = PlateChangeForm2()
    except Exception,e:
        print 'err',e
        transaction.rollback()
        errore=True
        variables = RequestContext(request, {'errore':errore})
        return render_to_response('index.html',variables)'''

#vista per inserire una nuova tipologia di contenitore
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_insert_new_container_type'),login_url=settings.BASE_URL+'/archive/error/')
@permission_decorator('archive.can_view_SMM_insert_new_container_type')
def InsertContainerType(request):
    if request.method=='POST':
        print request.POST
        form=ContainerTypeForm(request.POST)
        form2= ContainerTypeForm2(request.POST)
        try:
            if form.is_valid() and form2.is_valid():
                nome=duh.escape(request.POST.get('name').strip())
                catalog=duh.escape(request.POST.get('catalog').strip())
                produtt=duh.escape(request.POST.get('producer').strip())
                tipo_gen=duh.escape(request.POST.get('generic'))
                generico=GenericContainerType.objects.get(id=tipo_gen)
                
                righe=duh.escape(request.POST.get('row').strip())
                colonne=duh.escape(request.POST.get('col').strip())
                nom=str(righe)+'x'+str(colonne)
                lisgeometria=Geometry.objects.filter(name=nom)
                if len(lisgeometria)!=0:
                    geometria=lisgeometria[0]
                else:
                    #devo creare la nuova geometria
                    stringa=creaGeometria(righe, colonne)
                   
                    geometria=Geometry(name=nom,
                                  rules=stringa)
                    geometria.save()
                    print 'geom',geometria
                    
                contpadri=form2.cleaned_data.get('contpadri')
                contfigli=form2.cleaned_data.get('contfigli')
                posmax=duh.escape(request.POST.get('maxpos'))
                if posmax=='':
                    posmultiple=None
                else:
                    posmultiple=int(posmax)
                    
                usosingolo=False
                if 'use' in request.POST:
                    usosingolo=True
                    
                #creo la nuova tipologia di container
                cont_tip=ContainerType(idGenericContainerType=generico,
                                       name=nome,
                                       actualName=nome,
                                       maxPosition=posmultiple,
                                       catalogNumber=catalog,
                                       producer=produtt,
                                       idGeometry=geometria,
                                       oneUse=usosingolo)
                cont_tip.save()
                print 'cont',cont_tip
                print 'CONTPADRI',contpadri
                stringapadri=''
                for t in contpadri:
                    tipo=ContainerType.objects.get(id=t)
                    stringapadri+=tipo.actualName+' \n<br>'
                    print 'tipo',tipo
                    cont_type_has=ContTypeHasContType(idContainer=tipo,
                                                      idContained=cont_tip)
                    cont_type_has.save()
                    print 'cont_type',cont_type_has
                    
                stringafigli=''
                for t in contfigli:
                    tipo=ContainerType.objects.get(id=t)
                    stringafigli+=tipo.actualName+' \n<br>'
                    print 'tipo',tipo
                    cont_type_has=ContTypeHasContType(idContainer=cont_tip,
                                                      idContained=tipo)
                    cont_type_has.save()
                    print 'cont_type',cont_type_has
                #se il contenitore fa da radice allora creo una relazione in cui 
                #il suo possibile padre e' nullo
                if 'root' in request.POST:
                    cont_type_has=ContTypeHasContType(idContainer=None,
                                                      idContained=cont_tip)
                    cont_type_has.save()
                    print 'cont_type',cont_type_has
                
                #se il contenitore fa da foglia allora creo una relazione in cui 
                #il suo possibile figlio e' nullo
                if 'leaf' in request.POST:
                    cont_type_has=ContTypeHasContType(idContainer=cont_tip,
                                                      idContained=None)
                    cont_type_has.save()
                    print 'cont_type',cont_type_has
                    
                #mi occupo del resoconto finale
                listafin=[]
                intest='<th>Name</th><th>Catalogue N.</th><th>Producer</th><th>Geometry</th><th>Generic type</th><th>Father container</th><th>Child container</th>'
                dati='<tr align="center"><td>'+nome+'</td><td>'+catalog+'</td><td>'+produtt+'</td><td>'+ str(geometria) +'</td><td>'+ str(generico) +'</td><td>'+ stringapadri +'</td><td>'+ stringafigli +'</td></tr>'
                listafin.append(dati)
                
                variables = RequestContext(request, {'fine':True,'intest':intest,'dati':listafin})
                return render_to_response('plates/cont_type.html',variables)
            else:
                variables = RequestContext(request, {'form':form,'form2':form2})
                return render_to_response('plates/cont_type.html',variables)
        except Exception,e:
            print 'errore',e
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('index.html',variables)
    else:
        form = ContainerTypeForm()
        form2= ContainerTypeForm2()
    variables = RequestContext(request, {'form':form,'form2':form2})
    return render_to_response('plates/cont_type.html',variables)

'''#per inserire un nuovo contenitore singolo
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_insert_new_container_instance'),login_url=settings.BASE_URL+'/archive/error/')
def InsertNewContainerInstance(request):
    if request.method=='POST':
        print request.POST
        form=NewContainerForm(request.POST)
        try:
            if form.is_valid():
                tipo_gen=request.POST.get('generic')
                generico=GenericContainerType.objects.get(id=tipo_gen)
                lista_cont_type=ContainerType.objects.filter(idGenericContainerType=generico)
                print 'lista',lista_cont_type
                geom=Geometry.objects.all().order_by('name')
                fase2=True
                if generico.abbreviation=='freezer':
                    variables = RequestContext(request, {'form':form,'lista':lista_cont_type,'l_geom':geom,'fase2':fase2,'freezer':True})
                    return render_to_response('plates/new_cont.html',variables)
                elif generico.abbreviation=='rack':
                    variables = RequestContext(request, {'form':form,'lista':lista_cont_type,'l_geom':geom,'fase2':fase2,'rack':True})
                    return render_to_response('plates/new_cont.html',variables) 
                elif generico.abbreviation=='plate':
                    form2=PlateInsertForm()
                    variables = RequestContext(request, {'form':form2,'form2':form})
                    return render_to_response('plates/plate_insert.html',variables)
                else: 
                    variables = RequestContext(request, {'form':form,'lista':lista_cont_type,'l_geom':geom,'fase2':fase2,'tube':True,'freezer':True})
                    return render_to_response('plates/new_cont.html',variables)
            else:
                variables = RequestContext(request, {'form':form})
                return render_to_response('plates/new_cont.html',variables)
        except Exception,e:
            print 'errore',e
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('index.html',variables)
    else:
        form = NewContainerForm()
    variables = RequestContext(request, {'form':form})
    return render_to_response('plates/new_cont.html',variables)'''

#vista per salvare un nuovo contenitore
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_insert_new_container_instance'),login_url=settings.BASE_URL+'/archive/error/')
@permission_decorator('archive.can_view_SMM_insert_new_container_instance')
def InsertNewContainerInstance(request):
    if request.method=='POST':
        print request.POST
        form=NewContainerForm(request.POST)
        try:
            if 'final' in request.POST:  
                #mi occupo del resoconto finale
                lista=[]
                listafin=request.session.get('listanuovicontainer')
                print 'listafin2',listafin
                intest='<th>Barcode</th><th>Type</th><th>Geometry</th><th>Father</th><th>Position</th><th>Biological cont.</th>'
                for elem in listafin:
                    val=elem.split('|')
                    dati='<tr align="center"><td>'+val[0]+'</td><td>'+val[1]+'</td><td>'+val[2]+'</td><td>'+ val[3] +'</td><td>'+ val[4] +'</td><td>'+ val[5] +'</td></tr>'
                    lista.append(dati)
                variables = RequestContext(request, {'fine':True,'intest':intest,'dati':lista})
                return render_to_response('plates/new_cont2.html',variables)
            if 'salva' in request.POST:
                listafin=[]
                feataliq=Feature.objects.get(name='AliquotType')
                listacont=json.loads(request.POST.get('dati'))
                if 'lista2' in request.POST:
                    listapresenti=json.loads(request.POST.get('lista2'))
                else:
                    listapresenti=[]
                    
                lista=[]
                #scandisco una volta per il lashub
                for cont in listacont:
                    print 'cont',cont
                    barc=duh.escape(cont['barcode'].strip())
                    lista.append(barc)
                
                if 'batch' in request.POST:    
                    if Barcode_unico(lista, request):
                        #vuol dire che quel container e' gia' presente
                        raise ErrorPlate(barc)         
                
                for cont in listacont:
                    disp=1
                    cont_padre=None
                    full=0
                    posiz=duh.escape(cont['pos'].strip())
                    barc=duh.escape(cont['barcode'].strip())
                    #se c'e' un padre
                    if cont['padre']!='':
                        l_cont_padre=Container.objects.filter(barcode=cont['padre'])
                        if len(l_cont_padre)!=0:
                            cont_padre=l_cont_padre[0]
                        
                    #presente=False
                    tipo_cont=duh.escape(cont['conttipo'])
                    t_cont=ContainerType.objects.get(id=tipo_cont)
                    
                    geom=duh.escape(cont['geometry'])
                    lisgeometria=Geometry.objects.filter(name=geom)
                    if len(lisgeometria)!=0:
                        geometria=lisgeometria[0]
                    else:
                        #devo creare la nuova geometria
                        vett=geom.split('x')
                        #vett[0] contiene le righe, vett[1] contiene le colonne
                        stringa=creaGeometria(vett[0], vett[1])
                        geometria=Geometry(name=geom,
                                      rules=stringa)
                        geometria.save()
                        print 'geom',geometria
                    
                    if cont['uso']=='s':
                        usosing=True
                    else:
                        usosing=False
    
                    c=Container(idContainerType=t_cont,
                                idFatherContainer=cont_padre,
                                idGeometry=geometria,
                                position=posiz,
                                barcode=barc,
                                availability=disp,
                                full=full,
                                oneUse=usosing
                                )
                    c.save()
                    print 'c',c
                    
                    #salvo i contenuti biologici del container
                    lisaliq=cont['aliq']
                    laliq=lisaliq.split('&')
                    defval=DefaultValue.objects.filter(id__in=laliq)
                    
                    stringaaliq=''
                    for al in defval:
                        contfeat=ContainerFeature(idFeature=feataliq,
                                              idContainer=c,
                                              value=al.abbreviation)
                        contfeat.save()
                        print 'contfeat',contfeat
                        stringaaliq+=al.abbreviation+'-'
                        
                    stringdef=stringaaliq[0:-1]

                    padr=duh.escape(cont['padre'])
                    valori=c.barcode+'|'+str(c.idContainerType)+'|'+str(c.idGeometry)+'|'+padr+'|'+posiz+'|'+stringdef
                    listafin.append(valori)
                    
                SaveinLASHub(request,lista)
                
                for pres in listapresenti:
                    barc=duh.escape(pres['barcode'].strip())
                    posiz=duh.escape(pres['pos'].strip())
                    c=Container.objects.get(barcode=barc)
                    print 'contpresente',c
                    padr=duh.escape(pres['padre'])
                    if pres['padre']!='':
                        l_cont_padre=Container.objects.filter(barcode=pres['padre'])
                        if len(l_cont_padre)!=0:
                            cont_padre=l_cont_padre[0]
                            c.idFatherContainer=cont_padre
                            padr=cont_padre.barcode
                            c.position=posiz
                            c.save() 
                    print 'pres',pres
                    liscontfeat=ContainerFeature.objects.filter(idContainer=c,idFeature=feataliq)
                    print 'liscontfeat',liscontfeat
                    if len(liscontfeat)==0:
                        stringaaliq='All-'
                    else:
                        stringaaliq=''
                        for contfeat in liscontfeat:
                            stringaaliq+=contfeat.value+'-'
                    print 'listaaliq',stringaaliq
                    stringdef=stringaaliq[0:-1]
                                
                    valori=c.barcode+'|'+str(c.idContainerType)+'|'+str(c.idGeometry)+'|'+padr+'|'+posiz+'|'+stringdef
                    listafin.append(valori)
                    #print 'listafin',listafin
                
                #devo riscandire la lista per salvare effettivamente gli idFatherContainer che prima ho dovuto
                #mettere a null perche' non esistevano i container padri nel DB
                listatot=listacont+listapresenti
                print 'listatot',listatot
                for cont in listatot:
                    barc=duh.escape(cont['barcode'].strip())
                    #se c'e' un padre
                    if cont['padre']!='':
                        cont_padre=Container.objects.get(barcode=cont['padre'])
                        cont=Container.objects.get(barcode=barc)
                        cont.idFatherContainer=cont_padre
                        cont.save()
                        #devo vedere se il container padre si e' riempito con l'aggiunta di questo
                        #container
                        #se i posti per ogni posizione sono infiniti allora non si riempira' mai
                        if cont_padre.idContainerType.maxPosition!=None:
                            if ImpostaPieno(cont_padre) and cont_padre.full==0:
                                cont_padre.full=1
                                print 'cont pieno'
                                cont_padre.save()
                    
                request.session['listanuovicontainer']=listafin
                return HttpResponse('ok')
        except ErrorPlate as e:
            return HttpResponse('failure')
        except Exception,e:
            print 'errore',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('index.html',variables)
    else:
        form = NewContainerForm()
    variables = RequestContext(request, {'form':form})
    return render_to_response('plates/new_cont2.html',variables)

'''#vista per salvare un nuovo contenitore
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_insert_new_container_instance'),login_url=settings.BASE_URL+'/archive/error/')
def InsertNewContainerFinal(request):
    if request.method=='POST':
        print request.POST
        try:
            disp=1
            posiz=''
            cont_padre=None
            full=0
            lista=[]
            barc=request.POST.get('barcode').strip()
            lista.append(barc)
            if Barcode_unico(lista, request):
                raise ErrorPlate(barc)
            tipo_cont=request.POST.get('cont_tipo')
            t_cont=ContainerType.objects.get(id=tipo_cont)
            geom=request.POST.get('geom')
            geo=Geometry.objects.get(id=geom)
            if 'freezer' in request.POST:
                fr=request.POST.get('freezer')
                cont_padre=Container.objects.get(id=fr)
            if 'position' in request.POST:
                posiz=request.POST.get('position').strip()
                posiz=posiz.upper()
            #c'e' nel caso di inserimento di una provetta
            if 'plate' in request.POST:
                pias=request.POST.get('plate').strip()
                cont_padre=Container.objects.get(barcode=pias)
                        
            c=Container(idContainerType=t_cont,
                        idFatherContainer=cont_padre,
                        idGeometry=geo,
                        position=posiz,
                        barcode=barc,
                        availability=disp,
                        full=full
                        )
            c.save()
            print 'c',c
            #devo vedere se il container padre si e' riempito con l'aggiunta di questo
            #container
            if cont_padre!=None:
                lista_c=Container.objects.filter(idFatherContainer=cont_padre)
                regole=json.loads(cont_padre.idGeometry.rules)
                dimensioni=regole['dimension']
                xDim=dimensioni[1]
                yDim=dimensioni[0]
                posto_tot=xDim*yDim
                print 'posti_tot',posto_tot
                print 'lista',len(lista_c)
                if len(lista_c)>=posto_tot:
                    cont_padre.full=1
                    print 'cont pieno'
                    cont_padre.save()
            prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
            address=request.get_host()+settings.HOST_URL
            indir=prefisso+address
            url = indir + '/clientHUB/saveAndFinalize/'
            print 'url',url
            values2 = {'typeO' : 'container', 'listO': str(lista)}
            requests.post(url, data=values2, verify=False, headers={"workingGroups" : get_WG_string()})
            
            variables = RequestContext(request, {'fine':True})
            return render_to_response('plates/new_cont.html',variables)
        except ErrorPlate as e:
            print 'My exception occurred, value:', e.value
            variables = RequestContext(request, {'errore':e.value})
            return render_to_response('plates/new_cont.html',variables)
        except Exception,e:
            print 'errore',e
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('index.html',variables)  '''

#vista per gestire il caricamento contemporaneo di piu' container
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_insert_new_container_instance'),login_url=settings.BASE_URL+'/archive/error/')
@permission_decorator('archive.can_view_SMM_insert_new_container_instance')
def InsertContainerBatch(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES
            if 'file_plate' in request.FILES:
                listafile=request.FILES.getlist('file_plate')
                feat=Feature.objects.get(name='AliquotType')
                print 'f',listafile
                #lista con dentro tutti i figli presenti nei file. Serve per evitare eventuali doppioni
                listacontfigligen=[]
                listapadrigen=[]
                dizgen={}
                dizlivelli={}
                listavuoti=[]
                #scandisce ogni singolo file
                for f in listafile:
                    print 'f',f
                    dizfigli={}
                    listafigli=[]
                    linee=f.readlines()
                    #nella riga 1 ho il padre
                    riga1=linee[0].strip()
                    r=riga1.split(': ')
                    barcode=r[1]
                    listapadrigen.append(barcode)
                    print 'barcpadre',barcode
                    for j in range(1,len(linee)):
                        linee[j]=linee[j].strip()
                        if linee[j]!='':
                            #c[i] e' formato da posizione,barcode
                            v=linee[j].split(',')
                            barc=v[1].strip()
                            if barc!='No Tube':
                                if ' ' in barc:
                                    raise ErrorPlate('Error: there is a space in barcode "'+barc+'"')
                                pos=v[0].strip()
                                if len(pos)>2 and pos[2]!='0':
                                    pos=pos.replace('0','')
                                if barc not in listacontfigligen:
                                    dizfigli[barc]=pos
                                    diztemp={}
                                    diztemp[barc]=pos
                                    listafigli.append(diztemp)
                                    listacontfigligen.append(barc)
                                else:
                                    raise ErrorPlate('Error: container '+barc+' is present in more than one files')
                                
                    if len(dizfigli.keys())==0:
                        listavuoti.append(barcode)
                    dizgen[barcode]=listafigli
                  
                print 'dizgen prima',dizgen
                listaconttot=listapadrigen+listacontfigligen
                listabarc=Container.objects.filter(barcode__in=listaconttot)
                dizfin={}
                
                if request.session.has_key('dizgenbarcode'):
                    dizgenerale=request.session.get('dizgenbarcode')
                else:
                    dizgenerale={}
                    
                for elem in listabarc:
                    #devo inserire nel dizionario generale i container gia' presenti, in modo che dopo, quando faccio
                    #i vari controlli sui container inseriti, mi ritrovo gia' questi nel dizionario
                    diztemp={}
                    padre=''
                    for key,val in dizgen.items():
                        print 'val',val
                        for elemento in val:
                            #print 'elemento',elemento
                            for k,v in elemento.items():
                                #print 'val',val
                                #val e' la lista dei figli formati da un dizionario con barcode e posizione, mentre key e' il barc del padre
                                if k==elem.barcode:
                                    padre=key
                                    posiz=v
                    print 'padre',padre
                    if padre=='':
                        padre=elem.idFatherContainer
                        posiz=elem.position
                     
                    diztemp['padre']=str(padre)
                    diztemp['pos']=str(posiz)
                    diztemp['geom']=elem.idGeometry.name
                    diztemp['tipo']=str(elem.idContainerType.id)
                                        
                    listipifin=ListaAliquote(elem)
                    diztemp['aliq']=str(listipifin)
                    dizgenerale[elem.barcode]=diztemp
                    
                    #devo prendere anche gli eventuali figli attuali del cont per inserirli nel diz
                    #per evitare che i nuovi figli non abbiano le stesse posizioni di quelli gia' presenti
                    contfigli=Container.objects.filter(idFatherContainer=elem)
                    for f in contfigli:
                        diztemp={}
                        diztemp['padre']=str(f.idFatherContainer)
                        diztemp['pos']=str(f.position)
                        diztemp['geom']=f.idGeometry.name
                        diztemp['tipo']=str(f.idContainerType.id)
                        listipifin=ListaAliquote(f)
                        diztemp['aliq']=str(listipifin)
                        dizgenerale[f.barcode]=diztemp
                    
                    #devo vedere se il numero di figli scritto nel file e' coerente con la geometria del cont padre
                    if dizgen.has_key(elem.barcode):
                        maxpos=elem.idContainerType.maxPosition
                        #se i posti sono infiniti puo' avere quanti figli vuole. Non devo controllare
                        lisfigli=[]
                        if maxpos!=None:
                            lisfigli=dizgen[elem.barcode]
                            print 'lisfigli',lisfigli
                            regole=json.loads(elem.idGeometry.rules)
                            dimensioni=regole['dimension']
                            xDim=dimensioni[1]
                            yDim=dimensioni[0]
                            posto_tot=xDim*yDim*int(maxpos)
                            print 'posti_tot',posto_tot
                            print 'lista',len(lisfigli)
                            if len(lisfigli)>posto_tot:
                                raise ErrorPlate('Error: container '+elem.barcode+' has too many children. Please correct')
                            
                        #devo controllare se le posizioni sono scritte giuste
                        dizposizioni={}
                        for diz in lisfigli:
                            for chiave,val in diz.items():
                                #chiave e' il barcode dei figli, mentre val e' la posizione
                                print 'chiave',chiave
                                #devo verificare se quella posizione e' presente nelle regole della geometria
                                if not ControllaPosizioni(regole, val):
                                    raise ErrorPlate('Error: position '+val+' is inconsistent with geometry for container '+elem.barcode)
                                #devo verificare che non ci siano posizioni duplicate solo se maxpos non e' nullo
                                if maxpos!=None:
                                    if dizposizioni.has_key(val):
                                        contatore=dizposizioni[val]
                                        contatore+=1
                                        dizposizioni[val]=contatore
                                    else:
                                        dizposizioni[val]=1
                        print 'dizposizioni',dizposizioni
                        if maxpos!=None:
                            for ch,valore in dizposizioni.items():
                                if valore>maxpos:
                                    raise ErrorPlate('Error: position '+ch+' is duplicate in container '+elem.barcode)
                    dizfin[elem.barcode]=elem.idContainerType.actualName
                    #listafin.append(elem.barcode)
                
                request.session['dizgenbarcode']=dizgenerale
                print 'dizgenerale',dizgenerale
                print 'dizfin',dizfin
                lisrapporti=[]
                print 'listapadrigen',listapadrigen
                for padre in listapadrigen:
                    #trovato=False
                    for key,val in dizgen.items():
                        for elem in val:
                            for k,v in elem.items():
                                #print 'val',val
                                #val e' la lista dei figli formati da un dizionario con barcode e posizione, mentre key e' il barc del padre
                                if k==padre:
                                    print 'padre',padre
                                    dizrapporti={}
                                    diz2={}
                                    diz2[padre]=elem
                                    dizrapporti[key]=elem
                                    lisrapporti.append(dizrapporti)
                                    #cancello la posizione dal padre perche' tanto al suo posto metto
                                    #l'accordion con i figli
                                    val.remove(elem)
                                    break
                print 'dizlivelli',dizlivelli
                print 'dizgen',dizgen
                print 'lisrapporti',lisrapporti
                print 'listavuoti',listavuoti
                form =NewContainerForm()
            variables = RequestContext(request,{'fase2':True,'diz':dizgen,'listarapporti':lisrapporti,'dizpresenti':dizfin,'form':form, 'listavuoti':listavuoti})
            return render_to_response('plates/batch_cont.html',variables)
        else:
            variables = RequestContext(request)
            return render_to_response('plates/batch_cont.html',variables)
    except ErrorPlate as e:
            print 'Error duplicate, value:', e.value            
            variables = RequestContext(request, {'errore':e.value})
            return render_to_response('plates/batch_cont.html',variables)    
    except Exception,e:
        print 'errore',e
        transaction.rollback()
        errore=True
        variables = RequestContext(request, {'errore':errore})
        return render_to_response('index.html',variables)

#dato un freezer mi da' tutti i rack che sono al suo interno
#@get_functionality_decorator
def AjaxContainerAutoComplete(request):
    if 'term' in request.GET:
        lista1=[]   
        #prendo il container
        tipo=request.GET.get('tipo')
        print 'tipo',tipo
        conttipo=ContainerType.objects.get(id=tipo)
        #vedo quali container possono contenere il tipo scelto
        listatipi=ContTypeHasContType.objects.filter(idContained=conttipo)
        for i in range(0,len(listatipi)):
            lista1.append(listatipi[i].idContainer.id)
        print 'lista1',lista1
        lista_cont = Container.objects.filter(Q(barcode__istartswith=request.GET.get('term'))&Q(idContainerType__in=lista1))[:10]
        res=[]
        for p in lista_cont:
            p = {'id':p.id, 'label':p.__unicode__(), 'value':p.__unicode__()}
            res.append(p)
        return HttpResponse(simplejson.dumps(res))
    return HttpResponse()

'''#funzione a cui arriva una lista di barcode e l'indicazione se porre 
#la provetta a pieno o vuoto e se non esiste la crea 
@transaction.commit_manually
@csrf_exempt
def TubeFull(request):
    try:
        if request.method=='POST':
            print request.POST
            #mi da' i gen 
            lis_aliq=request.POST.get('lista')
            print 'lis',lis_aliq
            f=request.POST.get('tube')
            parti=lis_aliq.split('&')
            for i in range(0,(len(parti))-1):
                print 'lis',parti[i]
                lisprovetta=Container.objects.filter(barcode=parti[i])
                if len(lisprovetta)==0:
                    #creo la provetta
                    contipo=ContainerType.objects.get(name='Tube')
                    geom=Geometry.objects.get(name='1x1')
                    cont=Container(idContainerType=contipo,
                                   idGeometry=geom,
                                   barcode=parti[i],
                                   availability=1,
                                   full=1,
                                   oneUse=1)
                    cont.save()
                    #se c'e' salvo il tipo di aliquota della provetta
                    if 'tipo' in request.POST:
                        listip=request.POST.get('tipo')
                        listatip=ast.literal_eval(listip)
                        #prendo la feature aliquottype
                        feataliq=Feature.objects.get(name='AliquotType')
                        contfeat=ContainerFeature(idFeature=feataliq,
                                                  idContainer=cont,
                                                  value=listatip[i])
                        contfeat.save()
                        print 'contfeat',contfeat
                else:  
                    provetta=lisprovetta[0]  
                    print 'provetta',provetta
                    if f=='full':
                        provetta.full=True
                    elif f=='empty':
                        provetta.full=False
                        if 'canc' in request.POST:
                            print 'canc'
                            #vuol dire che questa vista e' stata chiamata dalla biobanca
                            #nel caso in cui un'aliquota sia terminata durante una derivazione.
                            #Quindi la provetta che la conteneva deve essere resa indisponibile.
                            #E' come se fosse stata buttata via.
                            provetta.idFatherContainer=None
                            provetta.availability=1
                            provetta.full=0
                            provetta.present=0
                            provetta.owner=''
                            print 'provetta dopo',provetta
                    provetta.save()
            transaction.commit()
            return HttpResponse("ok")
    except Exception, e:
        transaction.rollback()
        print e
        return HttpResponse("err")'''

#funzione a cui arriva una lista di gen e l'indicazione se porre 
#la provetta a pieno o vuoto e se non esiste la crea 
@transaction.commit_manually
@csrf_exempt
def TubeFull(request):
    try:
        if request.method=='POST':
            print request.POST
            if 'operator' in request.POST:
                operat=request.POST.get('operator')
                print 'utente',operat
                lutenti=User.objects.filter(username=operat)
                print 'lutenti',lutenti      
                if len(lutenti)==0:
                    utente=None
                else:
                    utente=lutenti[0]
            else:
                utente=None
            #mi da' i gen
            lis_aliq=json.loads(request.POST.get('lista'))
            print 'lis',lis_aliq
            f=request.POST.get('tube')
            #parti=lis_aliq.split('&')
            for valori in lis_aliq:
                #se sto chiamando questa vista per svuotare una provetta allora dentro alla lista
                #ci sara' solo il gen. Se la sto chiamando per salvare nuove aliquote allora ci sara'
                #barcode,gen,data
                print 'valori',valori
                vv=valori.split(',')
                print 'vv',vv
                if len(vv)==1:
                    gen=vv[0]
                else:
                    gen=vv[1]
                print 'gen',gen
                laliq=Aliquot.objects.filter(genealogyID=gen,endTimestamp=None)
                if len(laliq)==0:
                    lcont=Container.objects.filter(barcode=vv[0])
                    #se non trova il container vuol dire che gli ho passato un barcode fittizio
                    #formato da piastra|posizione proveniente dalle piastre di vitale
                    if len(lcont)==0:
                        bar=vv[0].split('|')
                        cont=Container.objects.get(barcode=bar[0])
                        pos=bar[1]
                    else:
                        cont=lcont[0]
                        pos=''
                        #devo impostare a pieno il cont
                        if f=='full':
                            cont.full=True
                            cont.save()
                    #oggi=datetime.datetime.now()
                    oggi=timezone.localtime(timezone.now())
                    datainiz=oggi
                    if len(vv)==3:
                        data=vv[2]
                        dat=data.split('-')
                        dtutente=timezone.datetime(int(dat[0]),int(dat[1]),int(dat[2]),1,0,0)
                        print 'dtutente',dtutente
                        #se la data impostata dall'utente e' quella di oggi allora lascio il .now()
                        #altrimenti metto la data dell'utente impostata all'1 di notte per far capire che l'ora e' fittizia
                        print 'mese utente',dtutente.month
                        if dtutente.year!=oggi.year or dtutente.month!=oggi.month or dtutente.day!=oggi.day:
                            datainiz=dtutente
                    
                    #creo l'aliq
                    a=Aliquot(genealogyID=str(gen),
                              idContainer=cont,
                              position=pos,
                              startTimestamp=datainiz,
                              startOperator=utente
                              )
                    a.save()
                    
                    #devo vedere se con l'aggiunta di questo campione la piastra si e' riempita
                    if cont.idContainerType.idGenericContainerType.abbreviation=='plate' and len(lcont)==0:
                        regole_geom=json.loads(cont.idGeometry.rules)
                        dim = regole_geom['dimension']
                        x = int(dim[1])
                        y = int(dim[0])
                        print 'x',x
                        print 'y',y
                        #devo tenere conto anche della posmax
                        posmax=cont.idContainerType.maxPosition
                        if posmax!=None:
                            dimensione=x*y*int(posmax)
                            laliq=Aliquot.objects.filter(idContainer=cont,endTimestamp=None)
                            print 'laliq',laliq
                            if len(laliq)==dimensione:
                                cont.full=1
                                print 'piastra piena'
                                cont.save()
                else:  
                    aliq=laliq[0]
                    provetta=aliq.idContainer
                    print 'provetta',provetta
                    #solo se ho a che fare con provette. Se ho una piastra con i pozzetti non faccio niente
                    if aliq.position=='' or aliq.position==None:
                        if f=='full':
                            provetta.full=True
                            
                            #oggi=datetime.datetime.now()
                            oggi=timezone.localtime(timezone.now())
                            datainiz=oggi
                            if len(vv)==3:
                                data=vv[2]
                                dat=data.split('-')
                                dtutente=timezone.datetime(int(dat[0]),int(dat[1]),int(dat[2]),1,0,0)
                                print 'dtutente',dtutente
                                #se la data impostata dall'utente e' quella di oggi allora lascio il .now()
                                #altrimenti metto la data dell'utente impostata all'1 di notte per far capire che l'ora e' fittizia
                                print 'anno utente',dtutente.year
                                if dtutente.year!=oggi.year or dtutente.month!=oggi.month or dtutente.day!=oggi.day:
                                    datainiz=dtutente
                            
                            #creo l'aliq
                            a=Aliquot(genealogyID=str(gen),
                                      idContainer=provetta,
                                      position='',
                                      startTimestamp=datainiz,
                                      startOperator=utente
                                      )
                            a.save()
                        elif f=='empty':
                            provetta.full=False
                            #se metto la provetta a vuota, allora chiudo anche la relazione aperta tra
                            #campione e provetta
                            #mi occupo della riga nella tabella Aliquot
                            #aliq.endTimestamp=datetime.datetime.now()
                            aliq.endTimestamp=timezone.localtime(timezone.now())
                            aliq.endOperator=utente
                            aliq.save()
                            if 'canc' in request.POST:
                                print 'canc'
                                #vuol dire che questa vista e' stata chiamata dalla biobanca
                                #nel caso in cui un'aliquota sia terminata durante una derivazione.
                                #Quindi la provetta che la conteneva deve essere resa indisponibile.
                                #E' come se fosse stata buttata via.
                                #Solo se il cont e' monouso
                                #guardo quanti figli ha
                                liscontfigli=Container.objects.filter(idFatherContainer=provetta)
                                lisaliqfigli=Aliquot.objects.filter(idContainer=provetta,endTimestamp=None)
                                if len(liscontfigli)==0 and len(lisaliqfigli)==0:
                                    if provetta.oneUse:
                                        contt=provetta.idFatherContainer
                                        if contt!=None:
                                            if contt.full==1:
                                                contt.full=0
                                                contt.save()
                                        provetta.idFatherContainer=None                                        
                                        provetta.full=0
                                        provetta.present=0                                        
                                        print 'provetta dopo',provetta
                                    provetta.availability=1
                                    provetta.owner=''
                        provetta.save()
                    else:
                        if 'canc' in request.POST:
                            #mi occupo della riga nella tabella Aliquot
                            #aliq.endTimestamp=datetime.datetime.now()
                            aliq.endTimestamp=timezone.localtime(timezone.now())
                            aliq.endOperator=utente
                            aliq.save()
                            #visto che ho tolto un campione, la piastra si e' svuotata e metto full=0
                            contt=aliq.idContainer
                            if contt.full==1:
                                contt.full=0
                                contt.save()
            transaction.commit()
            return HttpResponse("ok")
    except Exception, e:
        transaction.rollback()
        print 'err',e
        return HttpResponse("err")

#funzione per salvare nuovi blocchetti di ff, of o ch. Arriva una lista di blocchetti
#separati da '&' I dati di ogni blocco sono barcode,tipo(ff,of,ch)     
@transaction.commit_manually
@csrf_exempt
def SaveFF(request):
    print 'salva ff'
    try:
        if request.method=='POST':
            print request.POST
            print 'user',request.user.username
            name=''
            if 'user' in request.POST:
                name=request.POST.get('user')
            lutente=User.objects.filter(username=name)
            utente=None
            if len(lutente)!=0:
                utente=lutente[0]
            print 'utente',utente 
            #prendo la feature aliquottype
            feataliq=Feature.objects.get(name='AliquotType')
            #mi da' la lista delle aliquote
            lista=request.POST.get('lista')
            parti=lista.split('&')
            for i in range(0,(len(parti))-1):
                val=parti[i].split(',')
                print 'val',val
                #vedo se il container esiste gia'
                cont=Container.objects.filter(barcode=val[0])
                if len(cont)==0:
                    geom=Geometry.objects.get(name='1x1')
                    #se sto salvando delle singole provette per la raccolta del sangue
                    if val[1]!='FF' and val[1]!='OF' and val[1]!='CH':
                        
                        tipocont=ContainerType.objects.get(name='Tube')
                    else:
                        tipocont=ContainerType.objects.get(name=val[1])
                    c,creato=Container.objects.get_or_create(idContainerType=tipocont,
                                idGeometry=geom,
                                barcode=val[0],
                                availability=1,
                                full=1,
                                oneUse=1)
                    print 'cont',c
                    #se sto salvando delle singole provette per la raccolta del sangue
                    #aggiungo una feature alla provetta. Oppure se faccio una collezione utilizzando 
                    #singole provette e non le piastre
                    #if val[1]!='FF' and val[1]!='OF' and val[1]!='CH':
                    contfeat=ContainerFeature(idFeature=feataliq,
                                              idContainer=c,
                                              value=val[1])
                    contfeat.save()
                    print 'contfeat',contfeat
                    
                    #oggi=datetime.datetime.now()
                    oggi=timezone.localtime(timezone.now())
                    datainiz=oggi
                    if len(val)==4:
                        data=val[3]
                        dat=data.split('-')
                        dtutente=timezone.datetime(int(dat[0]),int(dat[1]),int(dat[2]),1,0,0)
                        print 'dtutente',dtutente
                        #se la data impostata dall'utente e' quella di oggi allora lascio il .now()
                        #altrimenti metto la data dell'utente impostata all'1 di notte per far capire che l'ora e' fittizia
                        print 'anno utente',dtutente.year
                        print 'mese utente',dtutente.month
                        if dtutente.year!=oggi.year or dtutente.month!=oggi.month or dtutente.day!=oggi.day:
                            datainiz=dtutente
                    
                    #devo salvare l'aliquota nella tabella
                    print 'val[2]',val[2]
                    a=Aliquot(genealogyID=str(val[2]),
                              idContainer=c,
                              position='',
                              startTimestamp=datainiz,
                              startOperator=utente
                              )
                    a.save()
                else:
                    raise Exception('Barcode already present')
            transaction.commit()            
            return HttpResponse("ok")
    except Exception,e:    
        transaction.rollback()
        print 'eccezione',e
        return HttpResponse("err") 
    
#funzione per salvare nuove provette. Arriva una lista di blocchetti
#separati da '&' I dati di ogni blocco sono barcode,barcode del padre,posizione    
@transaction.commit_manually
@csrf_exempt
def SaveTube(request):
    print 'salva nuova provetta'
    try:
        if request.method=='POST':
            print request.POST   
            #mi da' la lista delle aliquote
            lista=request.POST.get('lista')
            parti=lista.split('&')
            for i in range(0,(len(parti))-1):
                stringa=parti[i].split(',')
                print 'str',stringa
                tipocont=ContainerType.objects.get(name='Tube')
                contpadre=Container.objects.get(barcode=stringa[1])
                geom=Geometry.objects.get(name='1x1')
                c=Container(idContainerType=tipocont,
                            idFatherContainer=contpadre,
                            idGeometry=geom,
                            position=stringa[2],
                            barcode=stringa[0],
                            availability=1,
                            full=1)
                c.save()
                print 'cont',c
            transaction.commit()
            return HttpResponse("ok")
    except Exception,e:    
        transaction.rollback()
        print 'eccezione',e
        return HttpResponse("err")      

#per cancellare i blocchetti e rimettere a vuote le provette nel caso di cancellazione degli espianti
@transaction.commit_manually
@csrf_exempt
def CancFF(request):
    try:
        if request.method=='POST':
            print request.POST   
            #mi da' la lista delle aliquote
            lista=json.loads(request.POST.get('lista'))
            print 'lista',lista
            for gen in lista:
                aliq=Aliquot.objects.get(genealogyID=gen,endTimestamp=None)
                print 'aliq',aliq
                #solo se ho a che fare con provette. Se ho una piastra con i pozzetti non faccio niente
                if aliq.position=='' or aliq.position==None:
                    cont=aliq.idContainer
                    #devo capire se il cont e' una provetta da mettere a vuota o se e' un blocchetto 
                    #da cancellare. Se il cont ha un padre e non e' una piastra con i pozzetti, allora e' una provetta                
                    if cont.idFatherContainer==None:
                        cont.delete()
                    else:
                        cont.full=False
                        cont.save()
                aliq.delete()
            transaction.commit()
            return HttpResponse("ok")
    except Exception,e:
        print 'ecc',e    
        transaction.rollback()
        return HttpResponse("err")   

#funzione a cui arriva una lista di gen e l'indicazione se porre 
#il container in questione a disponibile o meno
@transaction.commit_manually
@csrf_exempt
def ContainerAvailability(request):
    try:
        if request.method=='POST':
            print request.POST
            #mi da' il gen del campione in questione
            lis_aliq=json.loads(request.POST.get('lista'))
            print 'lis',lis_aliq
            f=request.POST.get('tube')
            parti=Aliquot.objects.filter(genealogyID__in=lis_aliq,endTimestamp=None)
            print 'parti',parti
            for aliq in parti:
                print 'aliq',aliq
                provetta=aliq.idContainer
                print 'provetta',provetta
                if provetta!=None:
                    if f=='1':
                        provetta.availability=True
                        provetta.owner=None
                    elif f=='0':
                        provetta.availability=False
                        nome=request.POST.get('nome')
                        print 'nome',nome
                        provetta.owner=nome
                    provetta.save()
            transaction.commit()
            return HttpResponse("ok")
    except Exception, e:    
        transaction.rollback()
        print e
        return HttpResponse("err")

'''#funzione a cui arriva una lista di barcode separati da & e l'indicazione se porre 
#il container in questione a disponibile o meno
@transaction.commit_manually
@csrf_exempt
def ContainerAvailability(request):
    try:
        if request.method=='POST':
            print request.POST
            #mi da' il barcode della provetta in questione
            lis_aliq=request.POST.get('lista')
            print 'lis',len(lis_aliq)
            f=request.POST.get('tube')
            parti=lis_aliq.split('&')
            for i in range(0,(len(parti))-1):
                print 'lis',parti[i]
                provetta=Container.objects.get(barcode=parti[i])
                print 'provetta',provetta
                if f=='1':
                    provetta.availability=True
                    provetta.owner=None
                elif f=='0':
                    #mettere qua a False perche' funzioni il tutto
                    provetta.availability=False
                    nome=request.POST.get('nome')
                    print 'nome',nome
                    provetta.owner=nome
                provetta.save()
            transaction.commit()
            return HttpResponse("ok")
    except Exception, e:    
        transaction.rollback()
        print e
        return HttpResponse("err")'''

#schermata iniziale per archiviare le aliquote
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_archive_aliquots'),login_url=settings.BASE_URL+'/archive/error/')
@permission_decorator('archive.can_view_SMM_archive_aliquots')
def storeAliquots(request):
    a=Tabella()
    dictcontainer={}
    dictbiobanca={}
    lista=[]
    request.session['listacont']=dictcontainer
    request.session['dictbiobanca']=dictbiobanca
    request.session['piastresorgente']=lista
    try:
        if request.method=='POST':
            print request.POST
            print 'fase2'
            form = StoreForm(request.POST)
            ti=request.POST.get('tipi')
            #sto archiviando da costar a transitoria
            if ti=='0':
                variables = RequestContext(request, {'a':a,'fase2':True,'v':True,'tipo':'well'})
                return render_to_response('trasporto.html',variables)
            #sto archiviando le provette da operativa ad archivio
            elif ti=='1':
                variables = RequestContext(request, {'a':a,'fase2':True,'rs':True,'tipo':'tube'})
                return render_to_response('trasporto.html',variables)
            #se sto archiviando ffpe e simili
            elif ti=='2':
                #creo il dizionario che contiene tutti gli FF e simili da posizionare
                '''diz={}
                tipoff=ContainerType.objects.get(name='FF')
                #tipoof=ContainerType.objects.get(name='OF')
                #tipoch=ContainerType.objects.get(name='CH')
                listacont=Container.objects.filter((Q(idContainerType=tipoff))&Q(idFatherContainer=None))
                print 'lung',len(listacont)
                #ho la lista dei container e adesso ho bisogno di avere il genid del campione
                #contenuto
                num_pass=10
                for j in range(0,num_pass):
                    barc=''
                    lung=len(listacont)*(j+1)/num_pass
                    inizio=len(listacont)*(j)/num_pass
                    for i in range(inizio,lung):
                        barc+=listacont[i].barcode+'&&,'
                    #cancello la virgola alla fine della stringa
                    lu=len(barc)-1
                    strbarc=barc[:lu]
                    print 'strbarc',strbarc
                    indir=Urls.objects.get(default=1).url
                    print 'indir',indir
                    u = urllib2.urlopen(indir+"/api/tubes/"+strbarc)
                    data = json.loads(u.read())
                    for elem in data['data']:
                        val=elem.split(',')
                        #in val[0] ho il barcode del blocchetto, in val[3] ho il genid
                        if len(val)==5:
                            print 'gen',val[3]
                            #se non c'e' il gen vuol dire che il blocchetto e' ancora vuoto
                            diz[val[3]]=val[0]'''
                listaaliq=DefaultValue.objects.filter(~Q(abbreviation=None))
                variables = RequestContext(request, {'a':a,'tipaliq':listaaliq})
                return render_to_response('FFtrasporto.html',variables)
            
        else:
            form = StoreForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('trasporto.html',variables)
    except Exception,e:
        print 'err',e
        variables = RequestContext(request, {'errore':True})
        return render_to_response('index.html',variables)

#per salvare effettivamente l'archiviazione delle aliquote
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_archive_aliquots'),login_url=settings.BASE_URL+'/archive/error/')
@permission_decorator('archive.can_view_SMM_archive_aliquots')
def saveStoreAliquots(request):
    if request.method=='POST':
        if request.session.has_key('listacont'):
            dictcontainer=request.session.get('listacont')
        if request.session.has_key('dictbiobanca'):
            dictbiobanca=request.session.get('dictbiobanca')
        if request.session.has_key('piastresorgente'):
            listapiastresorg=request.session.get('piastresorgente')
        try:
            print request.POST
            if 'partenza' in request.POST:
                pospartenza=request.POST.get('pos')
                request.session['pospartenza']=pospartenza
                return HttpResponse()
            if 'carica' in request.POST:
                tipo=request.POST.get('ti')
                barcodesorg=request.POST.get('barcodesorg')
                barcodedest=request.POST.get('barcodedest')
                posiznuova=request.POST.get('posnuova')
                posizvecchia=request.POST.get('pos')
                barcprovetta=request.POST.get('barcode')
                
                piastrasorg=Container.objects.get(barcode=barcodesorg)
                print 'sorg',piastrasorg
                piastradest=Container.objects.get(barcode=barcodedest)
                print 'dest',piastradest
                prov=Container.objects.get(Q(idFatherContainer=piastrasorg)&Q(barcode=barcprovetta))
                print 'provetta',prov
                #sto trasferendo da vitale a transitoria
                if tipo=="well":
                    postodest=Container.objects.get(Q(idFatherContainer=piastradest)&Q(position=posiznuova))
                    prov.full=0
                    postodest.full=1
                    dictcontainer[barcprovetta]=prov
                    dictcontainer[postodest.barcode]=postodest
                    #e' il dict che passero' alla biobanca
                    dictbiobanca[barcprovetta]=postodest.barcode
                    print 'dict',dictcontainer
                    #se l'utente trasferisce la provetta da un posto all'altro della piastra
                    #transitoria devo rimettere a 0 l'attr full di postodest
                    if request.session.has_key('pospartenza'):
                        #pospartenza contiene la pos nella piastra transitoria da cui
                        #sono partito
                        pospartenza=request.session.get('pospartenza')
                    print 'pospartenza',pospartenza
                    if pospartenza!=None:
                        cont=Container.objects.get(Q(position=pospartenza)&Q(idFatherContainer=piastradest))
                        print 'cont',cont.barcode
                        b=cont.barcode
                        if(dictcontainer.has_key(b)):
                            print 'if'
                            valore=dictcontainer.pop(b)
                            valore.full=0
                            dictcontainer[b]=valore
                            print 'valore',valore
                            #tolgo il vecchio valore anche dal dict della biobanca
                            if (dictbiobanca.has_key(b)):
                                dictbiobanca.pop(b) 
                    request.session['listacont']=dictcontainer
                    request.session['dictbiobanca']=dictbiobanca
                    print 'dict',dictcontainer
                    print 'dictbiobanca',dictbiobanca
                else:
                    prov.idFatherContainer=piastradest
                    print 'prov.piastra',prov.idFatherContainer
                    prov.position=posiznuova
                    print 'prov.position',prov.position
                    dictcontainer[barcprovetta]=prov
                    request.session['listacont']=dictcontainer
                    print 'lista',dictcontainer
                    #faccio una lista con le piastre sorgenti in modo da impostarle
                    #dopo come vuote
                    if piastrasorg not in listapiastresorg:
                        listapiastresorg.append(piastrasorg)
                    request.session['piastresorgente']=listapiastresorg
                    print 'listapiassorg',listapiastresorg
                transaction.commit()
                return HttpResponse()
            if 'batch' in request.POST:
                str=request.POST.get('str')
                barcodesorg=request.POST.get('barcodesorg')
                barcodedest=request.POST.get('barcodedest')
    
                piastrasorg=Container.objects.get(Q(barcode=barcodesorg))
                print 'sorg',piastrasorg
                piastradest=Container.objects.get(Q(barcode=barcodedest))
                print 'dest',piastradest
                s=str.split('_')
                #lung di s meno 1 perche' l'ultimo elemento di s e' vuoto
                for i in range(0,(len(s))-1):
                    provetta=Container.objects.get(Q(idFatherContainer=piastrasorg)&Q(position=s[i]))
                    provetta.idFatherContainer=piastradest
                    print 'provetta',provetta
                    dictcontainer[provetta.barcode]=provetta
                request.session['listacont']=dictcontainer
                print 'lista',dictcontainer
                #faccio una lista con le piastre sorgenti in modo da impostarle
                #dopo come vuote
                if piastrasorg not in listapiastresorg:
                    listapiastresorg.append(piastrasorg)
                request.session['piastresorgente']=listapiastresorg
                print 'listapiassorg',listapiastresorg
                
                transaction.commit()
                return HttpResponse()
            if 'multiplo' in request.POST:
                strsorg=request.POST.get('strsorg')
                strdest=request.POST.get('strdest')
                tipo=request.POST.get('ti')
                barcodesorg=request.POST.get('barcodesorg')
                barcodedest=request.POST.get('barcodedest')
    
                piastrasorg=Container.objects.get(Q(barcode=barcodesorg))
                print 'sorg',piastrasorg
                piastradest=Container.objects.get(Q(barcode=barcodedest))
                print 'dest',piastradest
                s1=strsorg.split('_')
                s2=strdest.split('_')
                if tipo!='well':
                    #lung di s meno 1 perche' l'ultimo elemento di s e' vuoto
                    for i in range(0,(len(s1))-1):
                        provetta=Container.objects.get(Q(idFatherContainer=piastrasorg)&Q(position=s1[i]))
                        provetta.idFatherContainer=piastradest
                        provetta.position=s2[i]
                        print 'provetta',provetta
                        dictcontainer[provetta.barcode]=provetta
                    request.session['listacont']=dictcontainer
                    print 'lista',dictcontainer
                    
                    #faccio una lista con le piastre sorgenti in modo da impostarle
                    #dopo come vuote. Solo se lo spostamento non e' VT perche' la piastra
                    #VT non ha provette che si spostano quindi e' sempre piena
                    if piastrasorg not in listapiastresorg:
                        listapiastresorg.append(piastrasorg)
                    request.session['piastresorgente']=listapiastresorg
                    print 'listapiassorg',listapiastresorg
                    
                else:
                    #lung di s meno 1 perche' l'ultimo elemento di s e' vuoto
                    for i in range(0,(len(s1))-1):
                        prov=Container.objects.get(Q(idFatherContainer=piastrasorg)&Q(position=s1[i]))
                        print 'provetta',prov
                        postodest=Container.objects.get(Q(idFatherContainer=piastradest)&Q(position=s2[i]))
                        prov.full=0
                        postodest.full=1
                        dictcontainer[prov.barcode]=prov
                        dictcontainer[postodest.barcode]=postodest
                        #e' il dict che passero' alla biobanca
                        dictbiobanca[prov.barcode]=postodest.barcode
                    #solo se sposto le aliquote gia' posizionate nella piastra destinazione
                    if 'stored' in request.POST:
                        #e' la lista delle posizioni occupate dalle aliq nella piastra dest
                        #prima che le spostassi in altri posti sempre della piastra dest
                        strsorg_pias_dest=request.POST.get('strsorg2')
                        s3=strsorg_pias_dest.split('_')
                        for i in range(0,(len(s3))-1):
                            cont=Container.objects.get(Q(position=s3[i])&Q(idFatherContainer=piastradest))
                            print 'cont',cont.barcode
                            b=cont.barcode
                            if(dictcontainer.has_key(b)):
                                print 'if'
                                valore=dictcontainer.pop(b)
                                valore.full=0
                                dictcontainer[b]=valore
                                print 'valore',valore
                                #tolgo il vecchio valore anche dal dict della biobanca
                                if (dictbiobanca.has_key(b)):
                                    dictbiobanca.pop(b) 
                    request.session['listacont']=dictcontainer
                    request.session['dictbiobanca']=dictbiobanca
                    print 'dict',dictcontainer
                    print 'dictbiobanca',dictbiobanca
                transaction.commit()
                return HttpResponse()
            #serve a salvare il tutto
            if 'tipospost' in request.POST:
                print 'salva'
                #prendo il tipo di aliq spostata
                tipo=request.POST.get('tipospost')
                print 'tipo',tipo
                if tipo=='well':
                    #mi collego alla biobanca
                    try:
                        address = Urls.objects.get(default = '1').url
                        url=address+'/storevital/'
                        val={'dict':dictbiobanca}
                        data = urllib.urlencode(val)
                        req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                        u = urllib2.urlopen(req)
                        #u = urllib2.urlopen(url, data)
                        res =  u.read()
                        if(res=='err'):
                            transaction.rollback()
                            errore=True
                            variables = RequestContext(request, {'errore':errore})
                            return render_to_response('index.html',variables)
                    except Exception, e:
                        print 'exc',e
                #imposto le piastre sorgenti a vuote. Non devo mettere un controllo per
                #il VT perche' a monte non ho gia' messo le piastre VT nella lista 
                for pias in listapiastresorg:
                    pias.full=0
                    pias.save()
                #salvo le singole provette con la loro nuova posizione
                listadest=[]
                for key,value in dictcontainer.items():
                    value.save()
                    #metto nella lista le piastre di destinazione per vedere se poi
                    #devo impostarle come piene
                    piasdest=value.idFatherContainer
                    if piasdest not in listadest:
                        listadest.append(piasdest)
                print 'listadest',listadest
                
                for cont in listadest:
                    #devo vedere quanti figli ha ogni piastra
                    figli=Container.objects.filter(idFatherContainer=cont)
                    print 'lun',len(figli)
                    #se il nuemro di figli coincide con la sua dimensione allora imposto
                    #full a 1
                    regole_geom=json.loads(cont.idGeometry.rules)
                    dim = regole_geom['dimension']
                    x = int(dim[1])
                    y = int(dim[0])
                    print 'x',x
                    print 'y',y
                    dimensione=x*y
                    if len(figli)==dimensione:
                        cont.full=1
                        print 'pieno'
                        cont.save()
                    
                #devo salvare nella biobanca la data di archiviazione
                if tipo!='well':
                    try:
                        address = Urls.objects.get(default = '1').url
                        url=address+'/store/archivedate/'
                        val={'dict':dictcontainer.keys()}
                        data = urllib.urlencode(val)
                        req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                        u = urllib2.urlopen(req)
                        #u = urllib2.urlopen(url, data)
                        res =  u.read()
                        if(res=='err'):
                            transaction.rollback()
                            errore=True
                            variables = RequestContext(request, {'errore':errore})
                            return render_to_response('index.html',variables)
                    except Exception, e:
                        print 'exc',e
                
                if 'c' in request.POST:
                    print 'ffff'
                    print request.POST
                    #mi da' il numero della piastra di vitale di cui cancellare il contenuto
                    barcodevitale=request.POST.get('c')
                    print 'barcodevitale',barcodevitale
                    #se il barcode e' 0 non faccio niente perche' vuol dire che l'utente ha
                    #deciso di non cancellare il contenuto della piastra
                    if barcodevitale!='00':
                        lista=""
                        print 'cancvitale'
                        
                        piasvitale=Container.objects.get(barcode=barcodevitale)
                        listaprov=Container.objects.filter(idFatherContainer=piasvitale)
                        for prov in listaprov:
                            lista+=prov.barcode+'&'
                        #comunico alla biobanca di rendere indisponibili le aliq
                        try:
                            address = Urls.objects.get(default = '1').url
                            url=address+'/storevital/canc/'
                            val={'lista':lista}
                            data = urllib.urlencode(val)
                            req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                            u = urllib2.urlopen(req)
                            #u = urllib2.urlopen(url, data)
                            res =  u.read()
                            if(res=='err'):
                                transaction.rollback()
                                errore=True
                                variables = RequestContext(request, {'errore':errore})
                                return render_to_response('index.html',variables)
                        except Exception, e:
                            print 'exc',e
                        
                        for prov in listaprov:
                            prov.full=0
                            prov.save()
    
                transaction.commit()
                fine=True
                variables = RequestContext(request,{'fine':fine})
                return render_to_response('trasporto.html',variables)
        except Exception,e:
            print 'err',e
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('index.html',variables)

@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_archive_aliquots'),login_url=settings.BASE_URL+'/archive/error/')
@permission_decorator('archive.can_view_SMM_archive_aliquots')
def saveStoreAliquotsCassette(request):
    if request.method=='POST':
        if request.session.has_key('listacont'):
            dictcontainer=request.session.get('listacont')
        if request.session.has_key('dictbiobanca'):
            dictbiobanca=request.session.get('dictbiobanca')
        try:
            print request.POST
            if 'carica' in request.POST:
                barcode_pezzo=request.POST.get('barcode')
                barcodedest=request.POST.get('barcodedest')
                posiznuova=request.POST.get('posnuova')
                
                cass_dest=Container.objects.get(barcode=barcodedest)
                print 'dest',cass_dest
                cassette=Container.objects.get(Q(barcode=barcode_pezzo))
                print 'biocassette',cassette
                
                cassette.idFatherContainer=cass_dest
                print 'prov.piastra',cassette.idFatherContainer
                cassette.position=posiznuova
                print 'prov.position',cassette.position
                dictcontainer[barcode_pezzo]=cassette
                request.session['listacont']=dictcontainer
                print 'lista',dictcontainer.items()
                transaction.commit()
                return HttpResponse()
            
            #serve a salvare il tutto
            if 'salva' in request.POST:
                print 'salva'
                
                for key,value in dictcontainer.items():
                    value.save()
                    
                #devo salvare nella biobanca la data di archiviazione
                try:
                    address = Urls.objects.get(default = '1').url
                    url=address+'/store/archivedate/'
                    val={'dict':dictcontainer.keys()}
                    data = urllib.urlencode(val)
                    req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                    u = urllib2.urlopen(req)
                    #u = urllib2.urlopen(url, data)
                    res =  u.read()
                    if(res=='err'):
                        transaction.rollback()
                        errore=True
                        variables = RequestContext(request, {'errore':errore})
                        return render_to_response('index.html',variables)
                except Exception, e:
                    print 'exc',e
    
                transaction.commit()
                variables = RequestContext(request,{'fine':True})
                return render_to_response('trasporto.html',variables)
        except:
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('index.html',variables)
        
#per far comparire la pagina con tutte le provette da rimettere a posto
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_return_aliquots'),login_url=settings.BASE_URL+'/archive/error/')
@permission_decorator('archive.can_view_SMM_return_aliquots')
def PutAwayAliquots(request):
    listatot=[]
    nome=request.user.username
    lista=Container.objects.filter(availability=0,owner=nome)
    for l in lista:
        diztot={}
        plate='None'
        platepos='None'
        rack='None'
        freezer='None'
        #devo dividere il caso in cui il container in questione e' una piastra e il caso in cui e' una provetta
        if l.idContainerType.idGenericContainerType.abbreviation=='plate':
            diztot['barcode']='None'
            diztot['tubepos']='None'
            plate=l.barcode            
            if l.idFatherContainer!=None:
                platepos=l.position
                rack=l.idFatherContainer.barcode
                if l.idFatherContainer.idFatherContainer!=None:
                    freezer=l.idFatherContainer.idFatherContainer.barcode
        elif l.idContainerType.idGenericContainerType.abbreviation=='tube':
            diztot['barcode']=l.barcode
            diztot['tubepos']=l.position
            if l.idFatherContainer!=None:
                plate=l.idFatherContainer.barcode                
                if l.idFatherContainer.idFatherContainer!=None:
                    platepos=l.idFatherContainer.position
                    rack=l.idFatherContainer.idFatherContainer.barcode
                    if l.idFatherContainer.idFatherContainer.idFatherContainer!=None:
                        freezer=l.idFatherContainer.idFatherContainer.idFatherContainer.barcode
        diztot['plate']=plate
        diztot['platepos']=platepos
        diztot['rack']=rack
        diztot['freezer']=freezer
        lisaliq=Aliquot.objects.filter(idContainer=l,endTimestamp=None)
        #solo se la corrispondenza tra aliquota e container e' di 1 a 1, cioe' se il cont e' una provetta.
        #Invece se il cont e' una piastra non ha senso far comparire un gen tra i tanti. E' meglio mettere null
        if len(lisaliq)==1 and l.idContainerType.idGenericContainerType.abbreviation=='tube':
            diztot['gen']=lisaliq[0].genealogyID
        else:
            diztot['gen']=''
        print 'diztot',diztot
        listatot.append(diztot)
    print 'listatot',listatot
    variables = RequestContext(request,{'lista':listatot})
    return render_to_response('put.html',variables)

#per salvare definitivamente il riposizionamento delle provette
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_return_aliquots'),login_url=settings.BASE_URL+'/archive/error/')
@permission_decorator('archive.can_view_SMM_return_aliquots')
def PutAwayAliquotsLast(request):
    try:
        if request.method=='POST':
            print request.POST
            if 'final' in request.POST:
                lista=[]
                listafin=request.session.get('returnaliquotslast')
                print 'listafin',listafin
                intest='<th>Genealogy ID</th><th>Freezer</th><th>Rack</th><th>Plate Position</th><th>Plate</th><th>Tube Position</th><th>Barcode</th>'
                for elem in listafin:
                    val=elem.split('|')
                    dati='<tr align="center"><td>'+val[0]+'</td><td>'+val[1]+'</td><td>'+val[2]+'</td><td>'+ val[3] +'</td><td>'+ val[4] +'</td><td>'+ val[5] +'</td><td>'+ val[6] +'</td></tr>'
                    lista.append(dati)
                variables = RequestContext(request, {'fine':True,'intest':intest,'dati':lista})
                return render_to_response('put.html',variables)
            if 'salva' in request.POST:
                listafin=[]
                listabarc=json.loads(request.POST.get('lbarc'))
                print 'listabarc',listabarc
                liscont=Container.objects.filter(barcode__in=listabarc)
                for co in liscont:
                    #devo prendere tutti i suoi discendenti perche' se sto riposizionando lui vuol dire che
                    #rimetto a posto anche i suoi figli
                    lisfin=visit_children2([co],[])                    
                    print 'lisfin',lisfin
                    #nel caso in cui il cont non ha figli, ma ha direttamente le aliquote dentro di se'
                    if co not in lisfin:
                        lisfin.append(co)
                    print 'lisfin dopo',lisfin
                    
                    for cont in lisfin:
                        #solo se il cont e' indisponibile
                        if cont.availability==0:
                            cont.availability=1
                            cont.owner=None
                            print 'cont',cont
                            cont.save()
                            gen=''
                            barc='None'
                            freezer='None'
                            rack='None'
                            pias='None'
                            tubepos='None'
                            platepos='None'
                            
                            lisaliq=Aliquot.objects.filter(idContainer=cont,endTimestamp=None)
                            if len(lisaliq)==1 and cont.idContainerType.idGenericContainerType.abbreviation=='tube':
                                gen=lisaliq[0].genealogyID
                            
                            if cont.idContainerType.idGenericContainerType.abbreviation=='freezer':
                                freezer=cont.barcode
                            if cont.idContainerType.idGenericContainerType.abbreviation=='rack':
                                rack=cont.barcode
                                if cont.idFatherContainer!=None:
                                    freezer=cont.idFatherContainer.barcode                                                    
                            if cont.idContainerType.idGenericContainerType.abbreviation=='plate':
                                pias=cont.barcode                        
                                if cont.idFatherContainer!=None:
                                    rack=cont.idFatherContainer.barcode
                                    platepos=cont.position
                                    if cont.idFatherContainer.idFatherContainer!=None:
                                        freezer=cont.idFatherContainer.idFatherContainer.barcode
                            elif cont.idContainerType.idGenericContainerType.abbreviation=='tube':
                                barc=cont.barcode
                                if cont.idFatherContainer!=None:
                                    tubepos=cont.position
                                    pias=cont.idFatherContainer.barcode                            
                                    if cont.idFatherContainer.idFatherContainer!=None:
                                        platepos=cont.idFatherContainer.position
                                        rack=cont.idFatherContainer.idFatherContainer.barcode
                                        if cont.idFatherContainer.idFatherContainer.idFatherContainer!=None:
                                            freezer=cont.idFatherContainer.idFatherContainer.idFatherContainer.barcode
                            
                            valori=gen+'|'+freezer+'|'+rack+'|'+platepos+'|'+pias+'|'+tubepos+'|'+barc
                            listafin.append(valori)
                request.session['returnaliquotslast']=listafin
                return HttpResponse()
    except Exception, e:
        print 'err',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('index.html',variables)

@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_move_aliquots'),login_url=settings.BASE_URL+'/archive/error/')
@permission_decorator('archive.can_view_SMM_move_aliquots')
def MoveAliquots(request):
    a=Tabella()
    dictcontainer={}
    vt=False
    lista=[]
    
    request.session['containersorgmove']=lista
    request.session['listaprovettemove']=dictcontainer
    if request.method=='POST':
        print request.POST
        form = MoveForm(request.POST)
        if form.is_valid():
            ti=request.POST.get('tipi')
            #aliq=request.POST.get('aliquote')
            tipo_gen=request.POST.get('generic')
            generico=GenericContainerType.objects.get(id=tipo_gen)
            #mi occupo del tipo di aliq spostate
            '''ali=DefaultValue.objects.get(id=aliq)
            if ali.abbreviation=='VT':
                vt=True'''
            fase2=True
            print 'fase2'
            #se sto spostando all'interno dello stesso cont, il tipo e' 0
            if ti=='0':                
                una=True
                variables = RequestContext(request, {'a':a,'fase2':fase2,'una':una,'tipo':generico.abbreviation})
                return render_to_response('move.html',variables)
            else:
                molte=True
                variables = RequestContext(request, {'a':a,'fase2':fase2,'molte':molte,'tipo':generico.abbreviation})
                return render_to_response('move.html',variables)
        else:
            variables = RequestContext(request, {'form':form})
            return render_to_response('move.html',variables)
    else:
        form = MoveForm()
    variables = RequestContext(request, {'form':form})
    return render_to_response('move.html',variables)

@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_move_aliquots'),login_url=settings.BASE_URL+'/archive/error/')
@permission_decorator('archive.can_view_SMM_move_aliquots')
def SaveMoveAliquots(request):
    if request.method=='POST':
        if request.session.has_key('listaprovettemove'):
            dictcontainer=request.session.get('listaprovettemove')
        if request.session.has_key('containersorgmove'):
            listacontsorg=request.session.get('containersorgmove')
        try:
            print request.POST
            if 'carica' in request.POST:
                tipo=request.POST.get('ti')
                barcodesorg=request.POST.get('barcodesorg')
                barcodedest=request.POST.get('barcodedest')
                posiznuova=request.POST.get('posnuova')
                posizvecchia=request.POST.get('pos')
                barcprovetta=request.POST.get('barcode')
                
                piastrasorg=Container.objects.get(barcode=barcodesorg)
                print 'sorg',piastrasorg
                piastradest=Container.objects.get(barcode=barcodedest)
                print 'dest',piastradest
                
                #se sto spostando la paraffina devo muovere tutti i blocchetti 
                #presenti in quella posizione
                conthas=ContTypeHasContType.objects.filter(idContainer=piastrasorg.idContainerType)
                trovato=0
                for tipcont in conthas:
                    if tipcont.idContained.name=='FF':
                        trovato=1
                        break
                #sto spostando paraffina in un cassetto
                if trovato==1:
                    #trovo tutti i figli nella posizione di partenza
                    listacont=Container.objects.filter(Q(idFatherContainer=piastrasorg)&Q(position=posizvecchia))
                    for c in listacont:
                        c.idFatherContainer=piastradest
                        print 'prov.piastra',c.idFatherContainer
                        c.position=posiznuova
                        print 'prov.position',c.position
                        dictcontainer[c.barcode]=c
                else:
                    prov=Container.objects.get(Q(idFatherContainer=piastrasorg)&Q(barcode=barcprovetta))
                    print 'provetta',prov
                    
                    prov.idFatherContainer=piastradest
                    print 'prov.piastra',prov.idFatherContainer
                    prov.position=posiznuova
                    print 'prov.position',prov.position
                    dictcontainer[barcprovetta]=prov
                    
                    #faccio una lista con i container sorgenti in modo da impostarli
                    #dopo come vuoti
                    if piastrasorg not in listacontsorg:
                        listacontsorg.append(piastrasorg)
                    request.session['containersorgmove']=listacontsorg
                    print 'listacontsorg',listacontsorg
                    
                request.session['listaprovettemove']=dictcontainer
                print 'lista',dictcontainer
                transaction.commit()
                return HttpResponse()
            if 'batch' in request.POST:
                str=request.POST.get('str')
                barcodesorg=request.POST.get('barcodesorg')
                barcodedest=request.POST.get('barcodedest')
    
                piastrasorg=Container.objects.get(Q(barcode=barcodesorg))
                print 'sorg',piastrasorg
                piastradest=Container.objects.get(Q(barcode=barcodedest))
                print 'dest',piastradest
                s=str.split('_')
                #lung di s meno 1 perche' l'ultimo elemento di s e' vuoto
                for i in range(0,(len(s))-1):
                    listaprovetta=Container.objects.filter(Q(idFatherContainer=piastrasorg)&Q(position=s[i]))
                    for provetta in listaprovetta:
                        provetta.idFatherContainer=piastradest
                        print 'provetta',provetta
                        dictcontainer[provetta.barcode]=provetta
                request.session['listaprovettemove']=dictcontainer
                print 'lista batch',dictcontainer
                #faccio una lista con i container sorgenti in modo da impostarli
                #dopo come vuoti
                if piastrasorg not in listacontsorg:
                    listacontsorg.append(piastrasorg)
                request.session['containersorgmove']=listacontsorg
                print 'listacontsorg',listacontsorg
                
                transaction.commit()
                return HttpResponse()
            if 'multiplo' in request.POST:
                strsorg=request.POST.get('strsorg')
                strdest=request.POST.get('strdest')
                tipo=request.POST.get('ti')
                barcodesorg=request.POST.get('barcodesorg')
                barcodedest=request.POST.get('barcodedest')
    
                piastrasorg=Container.objects.get(Q(barcode=barcodesorg))
                print 'sorg',piastrasorg
                piastradest=Container.objects.get(Q(barcode=barcodedest))
                print 'dest',piastradest
                s1=strsorg.split('_')
                s2=strdest.split('_')

                #lung di s meno 1 perche' l'ultimo elemento di s e' vuoto
                for i in range(0,(len(s1))-1):
                    provetta=Container.objects.get(Q(idFatherContainer=piastrasorg)&Q(position=s1[i]))
                    provetta.idFatherContainer=piastradest
                    provetta.position=s2[i]
                    print 'provetta',provetta
                    dictcontainer[provetta.barcode]=provetta
                request.session['listaprovettemove']=dictcontainer
                print 'lista',dictcontainer
                
                #faccio una lista con i container sorgenti in modo da impostarli
                #dopo come vuoti
                if piastrasorg not in listacontsorg:
                    listacontsorg.append(piastrasorg)
                request.session['containersorgmove']=listacontsorg
                print 'listacontsorg',listacontsorg
                transaction.commit()
                return HttpResponse()
            #serve a salvare il tutto
            if 'tipospost' in request.POST:
                print 'salva'
                #prendo il tipo di aliq spostata
                tipo=request.POST.get('tipospost')
                print 'tipo',tipo
                #imposto i container sorgenti a vuote.
                for cont in listacontsorg:
                    cont.full=0
                    cont.save()
                    
                listadest=[]
                for key,value in dictcontainer.items():
                    print 'value',value
                    value.save()
                    #metto nella lista i container di destinazione per vedere se poi
                    #devo impostarli come pieni
                    piasdest=value.idFatherContainer
                    if piasdest not in listadest:
                        listadest.append(piasdest)
                print 'listadest',listadest
                
                for cont in listadest:
                    #devo vedere quanti figli ha ogni container
                    figli=Container.objects.filter(idFatherContainer=cont)
                    print 'lun',len(figli)
                    #se il nuemro di figli coincide con la sua dimensione allora imposto
                    #full a 1
                    regole_geom=json.loads(cont.idGeometry.rules)
                    dim = regole_geom['dimension']
                    x = int(dim[1])
                    y = int(dim[0])
                    print 'x',x
                    print 'y',y
                    dimensione=x*y
                    if len(figli)==dimensione:
                        cont.full=1
                        print 'pieno'
                        cont.save()
    
                transaction.commit()
                fine=True
                variables = RequestContext(request,{'fine':fine})
                return render_to_response('move.html',variables)
        except:
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('index.html',variables)    

#schermata per archiviare container
@laslogin_required
@transaction.commit_on_success
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_archive_aliquots'),login_url=settings.BASE_URL+'/archive/error/')
@permission_decorator('archive.can_view_SMM_archive_aliquots')
def ArchiveContainer(request):
    try:
        print request.POST
        if 'final' in request.POST:
            #mi occupo del resoconto finale
            lista=[]
            listafin=request.session.get('lisArchiveContainer')
            print 'listafin2',listafin
            intest='<th>Container moved</th><th>GenealogyID</th><th>Source container</th><th>Source position</th><th>Destination container</th><th>Destination position</th>'
            for elem in listafin:
                val=elem.split('|')
                dati='<tr align="center"><td>'+val[0]+'</td><td>'+val[1]+'</td><td>'+val[2]+'</td><td>'+ val[3] +'</td><td>'+ val[4] +'</td><td>'+ val[5] +'</td></tr>'
                lista.append(dati)
            variables = RequestContext(request, {'fine':True,'intest':intest,'dati':lista})
            return render_to_response('archive.html',variables)
        if 'salva' in request.POST:
            dizdati=json.loads(request.POST.get('dati'))
            print 'dizdati',dizdati
            #se non e' null ho il barcode della piastra da svuotare
            canccont=request.POST.get('contcanc')
            lisaliq_tot=[]
            lisaliqarch=[]
            lisreport=[]
            utente=User.objects.get(username=request.user.username)
            #le chiavi sono i barcode dei cont spostati
            for key in dizdati.keys():                
                print 'key',key
                #e' vera se sto spostando aliquote
                aliq=dizdati[key]['aliq']
                #e' vera se sto spostando piu' container insieme (vedi blocchetti di FF nel cassetto)
                multiplo=dizdati[key]['multiplo']
                print 'aliq',aliq
                barcdest=dizdati[key]['barcdest']
                print 'barcdest',barcdest
                posdest=dizdati[key]['posdest']
                print 'posdest',posdest
                costardest=dizdati[key]['costardest']
                lcontdest=Container.objects.filter(barcode=barcdest)
                contsorg=''
                if len(lcontdest)!=0:
                    contdest=lcontdest[0]
                    if not aliq:                
                        if not multiplo:
                            #devo togliere, se c'e', il |A1 in fondo al barc del cont spostato
                            barcfin=key.split('|')
                            lcont=[]
                            print 'barcfin',barcfin
                            print 'contdest',contdest.barcode
                            #solo se il cont spostato e' diverso dal cont dest
                            if barcfin[0]!=contdest.barcode:
                                ccont=Container.objects.filter(barcode=barcfin[0])
                                cont=ccont[0]
                                posiniz=str(cont.position)
                                if cont.idFatherContainer!=None:
                                    contsorg=cont.idFatherContainer
                                    if cont.idFatherContainer.full==1:
                                        padre=cont.idFatherContainer
                                        padre.full=0
                                        padre.save()
                                cont.idFatherContainer=contdest
                                cont.position=posdest                            
                                cont.save()                                                            
                                lcont.append(cont)
                                print 'contsorg',contsorg
                                barcontsorg=''
                                if contsorg!='':
                                    barcontsorg=contsorg.barcode
                                #formata da barc cont spostato|genid|contsorg|possorg|contdest|posdest
                                stringareport=barcfin[0]+'||'+barcontsorg+'|'+posiniz+'|'+contdest.barcode+'|'+posdest
                                lisreport.append(stringareport)
                        else:
                            #ho tutti i codici dei blocchetti separati da &
                            barcfin=key.split('&')
                            lcont=Container.objects.filter(barcode__in=barcfin)
                            for cc in lcont:
                                #solo se il cont spostato e' diverso dal cont dest
                                if cc.barcode!=contdest.barcode:
                                    posiniz=str(cc.position)
                                    if cc.idFatherContainer!=None:
                                        contsorg=cc.idFatherContainer
                                        if cc.idFatherContainer.full==1:
                                            padre2=cc.idFatherContainer
                                            padre2.full=0
                                            padre2.save()
                                    cc.idFatherContainer=contdest
                                    cc.position=posdest                                
                                    cc.save()
                                    barcontsorg=contsorg
                                    if contsorg!='':
                                        barcontsorg=contsorg.barcode
                                    #formata da barc cont spostato|genid|contsorg|possorg|contdest|posdest
                                    stringareport=cc.barcode+'||'+barcontsorg+'|'+posiniz+'|'+contdest.barcode+'|'+posdest
                                    lisreport.append(stringareport)
                                else:
                                    lcont.remove(cc)
                                    
                        if len(lcont)!=0:
                            #devo prendere tutti i discendenti del cont per avere le eventuali aliq da archiviare
                            lisfin=visit_children(lcont,[])
                            print 'lisfin',lisfin
                            print 'lcont[0]',lcont[0]
                            #nel caso in cui il cont non ha figli, ma ha direttamente le aliquote dentro di se'
                            if lcont[0] not in lisfin:
                                lisfin.append(lcont[0])
                            print 'lisfin',lisfin
                            #prendo le aliquote contenute in quei container
                            lisaliq=Aliquot.objects.filter(idContainer__in=lisfin,endTimestamp=None)
                            print 'lisaliq',lisaliq
                            if len(lisaliq)!=0:
                                lisaliq_tot.append(lisaliq)
                            
                            #devo vedere se con l'aggiunta di questo campione il cont si e' riempito                        
                            regole_geom=json.loads(contdest.idGeometry.rules)
                            dim = regole_geom['dimension']
                            x = int(dim[1])
                            y = int(dim[0])
                            print 'x',x
                            print 'y',y
                            #devo tenere conto anche della posmax
                            posmax=contdest.idContainerType.maxPosition
                            if posmax!=None:
                                dimensione=x*y*int(posmax)
                                print 'dimensione',dimensione
                                #per fare il group by in base alla posizione nel container. Cosi' riesco a trattare anche il caso dei cassetti
                                #Non serve perche' moltiplicando anche per il numero di posmax non devo fare il group by
                                #lcont=Container.objects.filter(idFatherContainer=contdest).values('position').annotate(dcount=Count('position'))
                                lcont2=Container.objects.filter(idFatherContainer=contdest)
                                print 'lcont2',lcont2
                                if len(lcont2)==dimensione:
                                    contdest.full=1
                                    print 'container pieno'
                                    contdest.save()
                                
                    else:
                        if not costardest:
                            #vuol dire che la dest non e' quella presente in barcdest, ma la provetta contenuta li'
                            contdest=Container.objects.get(idFatherContainer=contdest,position=posdest)
                            print 'contdest',contdest
                            posdest=''
                        if not multiplo:
                            #il barcfin e' formato da barcprov|A1 oppure barcpiastra|pos oppure da genid
                            barcfin=key.split('|')
                        else:
                            #key e' formato da barcprov|A1&barcprov|A1... oppure barcpiastra|pos&barcpiastra|pos...
                            barctemp=key.split('&')
                            barcfin=barctemp[0].split('|')                            
                            
                        #if barcfin[0]!=contdest.barcode:
                        lcont=Container.objects.filter(barcode=barcfin[0])
                        print 'lcont',lcont
                        if len(lcont)!=0:
                            #sto trattando il caso di una provetta singola
                            lisaliq=Aliquot.objects.filter(idContainer=lcont[0],position='',endTimestamp=None)
                            if len(lisaliq)==0:
                                #sto trattando il caso di una piastra con i pozzetti
                                lisaliq=Aliquot.objects.filter(idContainer=lcont[0],position=barcfin[1],endTimestamp=None)
                        else:
                            #sto trattando il caso del genid
                            #se il contdest e' gia' quello in cui si trova l'aliq, non devo fare niente
                            lisaliq=Aliquot.objects.filter(genealogyID=barcfin[0],endTimestamp=None).exclude(idContainer=contdest)
                                                        
                        print 'lisaliq',lisaliq
                        
                        regole_geom=json.loads(contdest.idGeometry.rules)
                        dim = regole_geom['dimension']
                        x = int(dim[1])
                        y = int(dim[0])
                        print 'x',x
                        print 'y',y
                        #serve nel caso in cui la dest e' un cont 1x1. Allora devo annullare la posizione, perche' la pos esplicita
                        #ce l'hanno solo le piastre. Devo aggiungere questo controllo perche' anche le provette sono costar e quindi
                        #non entra nell'if prima, che controlla il parametro costar
                        if x==1 and y==1 and posdest=='A1':
                            posdest=''
                        
                        for aliq in lisaliq:
                            lisaliqarch.append(aliq.genealogyID)
                            #rendo vuoto il cont sorgente
                            contsorg=aliq.idContainer
                            posiniz=str(aliq.position)
                            if aliq.idContainer.full==1:
                                contemp=aliq.idContainer
                                contemp.full=0
                                contemp.save()
                            #chiudo la vecchia relazione
                            #aliq.endTimestamp=datetime.datetime.now()
                            aliq.endTimestamp=timezone.localtime(timezone.now())
                            aliq.endOperator=utente
                            aliq.save()
                            #creo l'aliq
                            a=Aliquot(genealogyID=aliq.genealogyID,
                                      idContainer=contdest,
                                      position=posdest,
                                      #startTimestamp=datetime.datetime.now(),
                                      startTimestamp=timezone.localtime(timezone.now()),
                                      startOperator=utente
                                      )
                            a.save()
                            barcontsorg=contsorg
                            if contsorg!='':
                                barcontsorg=contsorg.barcode
                            #formata da barc cont spostato|genid|contsorg|possorg|contdest|posdest
                            stringareport='|'+a.genealogyID+'|'+barcontsorg+'|'+posiniz+'|'+contdest.barcode+'|'+posdest
                            lisreport.append(stringareport)                                
                                
                            #devo vedere se con l'aggiunta di questo campione il cont si e' riempito
                            #questo pezzo di codice non lo posso fare una volta sola anche per l'altro ramo dell'if
                            #perche' in questo ramo, prima, avrei potuto riassegnare il valore del contdest             
                            #devo tenere conto anche della posmax
                            posmax=contdest.idContainerType.maxPosition
                            if posmax!=None:
                                dimensione=x*y*int(posmax)
                                print 'dimensione',dimensione
                                print 'contdest',contdest
                                #per fare il group by in base alla posizione nel container. Cosi' riesco a trattare anche il caso in
                                #cui in una costar ho piu' campioni nello stesso posto
                                #Non serve perche' moltiplicando anche per il numero di posmax non devo fare il group by
                                #laliq=Aliquot.objects.filter(idContainer=contdest,endTimestamp=None).values('position').annotate(dcount=Count('position'))
                                laliq=Aliquot.objects.filter(idContainer=contdest,endTimestamp=None)
                                print 'laliq',laliq
                                if len(laliq)>=dimensione:
                                    contdest.full=1
                                    print 'container pieno'
                                    contdest.save()
                #se il contsorg non ha altri figli ed e' impostato su monouso, allora lo devo buttare
                print 'contsorg2',contsorg
                if contsorg!='':
                    #guardo quanti figli ha
                    liscontfigli=Container.objects.filter(idFatherContainer=contsorg)
                    lisaliqfigli=Aliquot.objects.filter(idContainer=contsorg,endTimestamp=None)
                    if len(liscontfigli)==0 and len(lisaliqfigli)==0:
                        if contsorg.oneUse:
                            print 'elimino sorgente:',contsorg
                            contsorg.idFatherContainer=None
                            contsorg.availability=1
                            contsorg.full=0
                            contsorg.present=0
                            contsorg.owner=''
                            contsorg.save()
                            
            print 'canccont',canccont
            if canccont!='null':
                lcont=Container.objects.filter(barcode=canccont)
                print 'lcont',lcont
                if len(lcont)!=0:
                    cont=lcont[0]
                    #devo prendere tutti i discendenti del cont per avere le eventuali aliq da cancellare
                    lisfintemp=visit_children(lcont,[])
                    print 'lisfintemp',lisfintemp                    
                    #nel caso in cui il cont non ha figli, ma ha direttamente le aliquote dentro di se'
                    if cont not in lisfintemp:
                        lisfinale=lisfintemp+[cont]
                    print 'lisfinale',lisfinale
                    #prendo le aliquote contenute in quei container
                    lisaliq=Aliquot.objects.filter(idContainer__in=lisfinale,endTimestamp=None)
                    
                    #elimino i cont presenti all'interno, se ce ne sono
                    for c in lisfintemp:
                        c.idFatherContainer=None
                        c.present=0
                        c.save()
                    #elimino i campioni
                    listacamp=[]
                    for a in lisaliq:
                        #a.endTimestamp=datetime.datetime.now()
                        a.endTimestamp=timezone.localtime(timezone.now())
                        a.endOperator=utente
                        a.save()                    
                        listacamp.append(a.genealogyID)
                    
                    print 'listacamp',listacamp
                    if len(listacamp)!=0:
                        #comunico alla biobanca di rendere indisponibili le aliq
                        address = Urls.objects.get(default = '1').url
                        url=address+'/storevital/canc/'
                        print 'url',url
                        val={'lista':json.dumps(listacamp)}
                        data = urllib.urlencode(val)
                        req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                        u = urllib2.urlopen(req)
                        res =  u.read()
                        if(res=='err'):
                            raise Exception
            
            print 'listot',lisaliq_tot            
            for lis in lisaliq_tot:
                for aliq in lis:
                    lisaliqarch.append(aliq.genealogyID)
            print 'lisaliqarch',lisaliqarch
            if len(lisaliqarch)!=0:
                #devo salvare nella biobanca la data di archiviazione
                address = Urls.objects.get(default = '1').url
                url=address+'/store/archivedate/'
                val={'lisaliq':json.dumps(lisaliqarch)}
                data = urllib.urlencode(val)
                req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
                u = urllib2.urlopen(req)
                res =  u.read()
                if(res=='err'):
                    raise Exception
            
            request.session['lisArchiveContainer']=lisreport
            return HttpResponse()
        
        listaaliq=DefaultValue.objects.all().exclude(abbreviation=None).order_by('longName')
        variables = RequestContext(request, {'tipaliq':listaaliq})
        return render_to_response('archive.html',variables)
    except Exception,e:
        print 'err',e
        transaction.rollback()
        variables = RequestContext(request, {'errore':True})
        return render_to_response('index.html',variables)

class ErrorHistoric(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

#per il modulo di sanger per creare una piastra nuova
@transaction.commit_on_success
@csrf_exempt
def CreatePlate(request):
    try:
        if request.method=='POST':
            print request.POST   
            l_inform=request.POST.get('info')
            print 'info',l_inform
            l_regole=request.POST.get('rules')
            print 'reg',l_regole
            figli=request.POST.get('children')
            print 'figli',figli
            inform=ast.literal_eval(l_inform)
            regole=ast.literal_eval(l_regole)
            l_figli=ast.literal_eval(figli)
            print 'l_figli',l_figli
            tipo_cont=inform['containerType']
            print 'tip cont',tipo_cont
            t_cont=ContainerType.objects.get(name=tipo_cont)
            barc_piastra=inform['barcode']
            print 'barc pias',barc_piastra
            dim = regole['dimension']
            righe=dim[1]
            print 'righe',righe
            colonne=dim[0]
            nome_geometria=str(righe)+'x'+str(colonne)
            geom=Geometry.objects.filter(name=nome_geometria)
            if len(geom)==0:
                reg=creaGeometria(int(righe), int(colonne))     
                geom2,creato=Geometry.objects.get_or_create(name=nome_geometria,
                                                           rules=reg)
            else:
                geom2=Geometry.objects.get(name=nome_geometria)
                
            p=Container(idContainerType=t_cont,
                         idGeometry=geom2,
                         barcode=barc_piastra,
                         availability=1,
                         full=0)
            print 'p',p
            p.save()
            feataim=Feature.objects.get(name='PlateAim')
            aimfeat=ContainerFeature(idFeature=feataim,
                                     idContainer=p,
                                     value='Operative')
            aimfeat.save()
            #ho salvato la piastra, adesso devo salvare le provette figlie
            provetta=ContainerType.objects.get(name='Tube')
            geom_tube=Geometry.objects.get(name='1x1')
            for elem in l_figli:
                cont=Container(idContainerType=provetta,
                         idFatherContainer=p,
                         idGeometry=geom_tube,
                         position=elem['position'],
                         barcode=elem['barcode'],
                         availability=1,
                         full=elem['full'])
                cont.save()
                
            return HttpResponse("ok")
    except Exception, e:            
        transaction.rollback()
        print 'eccezione',e
        return HttpResponse("err")  

def ProvaCreatePlate(request):
    #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
    #indirizzo=request.get_host()
    indir=settings.DOMAIN_URL+settings.HOST_URL
    url=indir+'/archive/create/plate/'
    print 'url',url
    info={"containerType": "PlateThermoStandard", "position": "", "barcodeF": "", 
        "full": False, "availability": True,"barcode":"provasanger"}
    reg={"dimension": [12,  8]}
    figli=[{"position": "A1", "barcode": "provettasang1", "availability": "False", 
            "full": "True", "idContainerType": "Tube"}, 
        {"position": "C1", "barcode": "provettasang2", "availability": "True", 
            "full": "False", "idContainerType": "Tube"}]
    values_to_send={'info':info, 'rules': reg, 'children': figli}
    data = urllib.urlencode(values_to_send)
    req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    #u = urllib2.urlopen(url, data)
    print 'res',u.read()
    return HttpResponse("ok")  

def ProvaAliquotHandler(request):
    #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
    #indirizzo=request.get_host()
    indir=settings.DOMAIN_URL+settings.HOST_URL
    url=indir+'/api/info/aliquot/'
    print 'url',url
    info=[{'barcode':'10','pos':'A1'},{'barcode':'10','pos':'B1'},{'barcode':'bvnh','pos':'-'}]
    values_to_send={'listBarcode':json.dumps(info)}
    data = urllib.urlencode(values_to_send)
    req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    fff=u.read()
    #u = urllib2.urlopen(url, data)
    print 'res',fff
    return HttpResponse("ok")  
    
@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('archive.can_view_new_geometry'),login_url=settings.BASE_URL+'/archive/error/')
@permission_decorator('archive.can_view_SMM_new_geometry')
def CreateGeometry(request):
    if request.method=='POST':
        print request.POST
        form=NewGeometryForm(request.POST)
        try:
            if form.is_valid():
                xDim=request.POST.get('x').strip()
                yDim=request.POST.get('y').strip()
                
                stringa=creaGeometria(xDim, yDim)     
                   
                nome=xDim+'x'+yDim
                geom,creato=Geometry.objects.get_or_create(name=nome,
                                                           rules=stringa)
                print 'geom',geom
                variables = RequestContext(request,{'fine':True})
                return render_to_response('new_geometry.html',variables)
            else:
                variables = RequestContext(request, {'form':form})
                return render_to_response('new_geometry.html',variables)
        except Exception,e:
            print 'err',e
            transaction.rollback()
            variables = RequestContext(request, {'errore':True})
            return render_to_response('index.html',variables)
    else:
        form = NewGeometryForm()
    variables = RequestContext(request, {'form':form})
    return render_to_response('new_geometry.html',variables)   

#utilizzata quando e' stato aggiornato il DB dell'archivio. Non serve piu'
@transaction.commit_on_success
def CopyGeometry(request):
    try:
        lis_cont=Container.objects.all()
        for c in lis_cont:
            c.idGeometry=c.idContainerType.idGeometry
            c.save()
        return HttpResponse("ok")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#per fare in modo che le provette gia' buttate via vengano modificate. Serve solo una
#volta per aggiornare i dati che gia' sono nel DB. Non serve piu'
@transaction.commit_on_success
def UpdatePresent(request):
    try:
        prov=ContainerType.objects.get(name='Tube')
        #prendo tutte le provette che fisicamente non esistono piu' nell'archivio
        listaprov=Container.objects.filter(Q(idContainerType=prov)&Q(idFatherContainer=None)&Q(full=0)&Q(availability=1))
        for prov in listaprov:
            prov.present=0
            prov.save()
        return HttpResponse("ok")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")
    
'''#Per inizializzare il lashub. Viene creato un file con tutte le istruzioni in SQL
@transaction.commit_on_success
def HubCreate(request):
    try:
        stringa=''
        #prendo i container
        listacont=Container.objects.all()
        oggi=timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
        print 'adesso',oggi
        idobj=700
        idval=1400
        for cont in listacont:
            #inserimento nella tabella object
            stringa+='insert into object values ('+str(idobj)+',1,\''+str(oggi)+'\',2);\n'
            #inserimento del barcode
            stringa+='insert into object_value values ('+str(idval)+','+str(idobj)+',3,\''+cont.barcode+'\');\n'
            idval=idval+1
            idobj=idobj+1
        
        f2=open(os.path.join(os.path.dirname(__file__),'archive_media/File_Format/create2.sql'),'w')
        f2.write(stringa)
        f2.close()
        return HttpResponse("ok")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")'''

#Per inizializzare il lashub. Viene creato un file con tutte le istruzioni in SQL
@transaction.commit_on_success
def HubCreate(request):
    try:
        #prendo i container
        listacont=Container.objects.all()
        oggi=timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
        print 'adesso',oggi
        idobj=700
        idval=1400
        stringa='insert into object values'
        for cont in listacont:
            #inserimento nella tabella object
            stringa+='('+str(idobj)+',1,\''+str(oggi)+'\',2),'
            idobj=idobj+1
        stri2=stringa[:len(stringa)-1]
        stri2+=';\ninsert into object_value values'
        idobj=700
        for cont in listacont:    
            print 'cont',cont
            #inserimento del barcode
            stri2+=' ('+str(idval)+','+str(idobj)+',3,\''+cont.barcode+'\'),'
            idval=idval+1
            idobj=idobj+1
        stri3=stri2[:len(stri2)-1]
        stri3+=';'
        f2=open(os.path.join(os.path.dirname(__file__),'archive_media/File_Format/create2.sql'),'w')
        f2.write(stri3)
        f2.close()
        return HttpResponse("ok")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

def Query(request):
    gen_list={'id':['CRC0499BMH0000000000VT0200','OVR0003SMH0000000000D02000']}
    #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
    #indirizzo=request.get_host()
    indir=settings.DOMAIN_URL+settings.HOST_URL
    url=indir+'/api/query/containers'
    values_to_send={'predecessor':'start', 'list': gen_list, 'successor': 'Aliquots', 'parameter': 'Barcode', 'values':'diatech1|provettavuota'}
    data = urllib.urlencode(values_to_send)
    req = urllib2.Request(url,data=data, headers={"workingGroups" : get_WG_string()})
    u = urllib2.urlopen(req)
    res = json.loads(u.read())
    return HttpResponse("ok")

@transaction.commit_on_success
def HistoricBeamingContainer(request):
    try:
        if request.method=='POST':
            listabarc=[]
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            
            f=request.FILES.get('file')
            lines = f.readlines()
            f.close()
            #print 'lines',lines
            i=0
            feataliq=Feature.objects.get(name='AliquotType')
            feataim=Feature.objects.get(name='PlateAim')
            for line in lines:
                print 'line',line
                valori=line.split(';')
                print 'val',valori

                tipo=valori[1].strip()
                print 'ti',tipo
                tipo_cont=ContainerType.objects.get(name=tipo)
                print 'tipo',tipo_cont
                padre=valori[3].strip()
                cont_padre=Container.objects.get(barcode=padre)
                geom=valori[2].strip()
                geometria=Geometry.objects.get(name=geom)
                pos=valori[5].strip()
                barc=valori[0].strip()
                avail=1
                full=0
                c=Container(idContainerType=tipo_cont,
                            idFatherContainer=cont_padre,
                            idGeometry=geometria,
                            position=pos,
                            barcode=barc,
                            availability=avail,
                            full=full)
                
                c.save()
                print 'c',c
                
                #devo salvare le feature
                tipopiastra=valori[9].strip()

                aliqfeat=ContainerFeature(idFeature=feataliq,
                                          idContainer=c,
                                          value=tipopiastra)
                aliqfeat.save()
                aimfeat=ContainerFeature(idFeature=feataim,
                                         idContainer=c,
                                         value='Stored')
                aimfeat.save()
                listabarc.append(barc)
                i+=1    
                #if i==2:
                    #break
            #faccio il controllo se esistono quei barcode
            Barcode_unico(listabarc, request)
            
            #finalizzo i barc inseriti
            #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
            #address=request.get_host()+settings.HOST_URL
            #indir=prefisso+address
            indir=settings.DOMAIN_URL+settings.HOST_URL
            url = indir + '/clientHUB/saveAndFinalize/'
            print 'url',url
            values2 = {'typeO' : 'container', 'listO': str(listabarc)}
            requests.post(url, data=values2, verify=False, headers={"workingGroups" : get_WG_string()})
            
            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('historic/storico_box.html',variables)
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#serve per caricare nel DB i rack storici
@transaction.commit_on_success
def HistoricRack(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            stringa=''
            form=HistoricForm(request.FILES)
            
            f=request.FILES.get('file')
            lines = f.readlines()
            f.close()
            
            
            stringa+='Father Container;Type;Barcode;Position;Geometry\n'
            
            #print 'lines',lines
            for line in lines:
                valori=line.split(';')
                print 'val',valori[3]
                if valori[3]!='?':
                    tipo=valori[1].decode('latin-1').strip()
                    print 'ti',tipo.encode('latin-1')
                    tipo_cont=ContainerType.objects.get(name=tipo)
                    print 'tipo',tipo_cont
                    padre=unicode(valori[0].strip())
                    cont_padre=Container.objects.get(barcode=padre)
                    geom=valori[4].strip()
                    geometria=Geometry.objects.get(name=geom)
                    pos=valori[5].strip()
                    barc=valori[3].strip()
                    avail=1
                    full=0
                    c=Container(idContainerType=tipo_cont,
                                idFatherContainer=cont_padre,
                                idGeometry=geometria,
                                position=pos,
                                barcode=barc,
                                availability=avail,
                                full=full)
                    stringa+=cont_padre.barcode+';'+tipo_cont.name+';'+barc+';'+pos+';'+geometria.name+'\n'
                    #c.save()
                    print 'c',c
            f2=open(os.path.join(os.path.dirname(__file__),'archive_media/Historical/Rack.csv'),'w')
            f2.write(stringa.encode('latin-1'))
            f2.close()
            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('historic/storico_rack.html',variables)
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")
    
#serve per caricare nel DB i box storici
@transaction.commit_on_success
def HistoricBox(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            stringa=''
            stringa+='Father Container;Type;Barcode;Position;Geometry\n'
            f=request.FILES.get('file')
            lines = f.readlines()
            f.close()
            #print 'lines',lines
            i=0
            feataliq=Feature.objects.get(name='AliquotType')
            feataim=Feature.objects.get(name='PlateAim')
            for line in lines:
                valori=line.split(';')
                print 'val',valori[1]

                tipo=valori[2].strip()
                print 'ti',tipo
                tipo_cont=ContainerType.objects.get(name=tipo)
                print 'tipo',tipo_cont
                padre=valori[5].strip()
                cont_padre=Container.objects.get(barcode=padre)
                geom=valori[3].strip()
                geometria=Geometry.objects.get(name=geom)
                pos=valori[4].strip()
                barc=valori[1].strip()
                avail=1
                full=0
                c=Container(idContainerType=tipo_cont,
                            idFatherContainer=cont_padre,
                            idGeometry=geometria,
                            position=pos,
                            barcode=barc,
                            availability=avail,
                            full=full)
                stringa+=cont_padre.barcode+';'+tipo_cont.name+';'+barc+';'+pos+';'+geometria.name+'\n'
                c.save()
                print 'c',c
                #devo salvare le feature
                tipopiastra=valori[0]
                tipo=tipopiastra.split(' ')
                #in tipo[0] ho RnaLater o SnapFrozen o Genomic o Rna
                if tipo[0]=='RnaLater':
                    aliq='RL'
                elif tipo[0]=='SnapFrozen':
                    aliq='SF'
                elif tipo[0]=='Store003':
                    aliq='VT'
                elif tipo[0]=='Genomic':
                    aliq='DNA'
                elif tipo[0]=='Rna':
                    aliq='RNA'


                aliqfeat=ContainerFeature(idFeature=feataliq,
                                          idContainer=c,
                                          value=aliq)
                aliqfeat.save()
                aimfeat=ContainerFeature(idFeature=feataim,
                                         idContainer=c,
                                         value='Stored')
                aimfeat.save()
                
                i+=1
                #if i==2:
                    #break
            f2=open(os.path.join(os.path.dirname(__file__),'archive_media/Historical/Box.csv'),'w')
            f2.write(stringa)
            f2.close()
            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('historic/storico_box.html',variables)
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")
    
#serve per caricare nel DB le piastre storiche
@transaction.commit_on_success
def HistoricPlate(request):
    try:
        if request.method=='POST':
            print request.POST
            print request.FILES  
            form=HistoricForm(request.FILES)
            stringa=''
            stringa+='Father Container;Type;Barcode;Position;Geometry\n'
            f=request.FILES.get('file')
            lines = f.readlines()
            f.close()
            #print 'lines',lines
            i=0
            feataliq=Feature.objects.get(name='AliquotType')
            feataim=Feature.objects.get(name='PlateAim')
            tipo_cont=ContainerType.objects.get(name='PlateThermoStandard')          
            geometria=Geometry.objects.get(name='8x12')
            
            for line in lines:
                valori=line.split(';')
                print 'val',valori[0]
                for j in range(1,7):
                    padre=valori[0].strip()
                    cont_padre=Container.objects.get(barcode=padre)
                    pos='A'+str(j)
                    barc=valori[j].strip()
                    avail=1
                    full=0
                    if barc!='':
                        print 'barc',barc
                        b=barc.split('_')
                        print 'b',b[0]
                        barc=b[1]
                        c=Container(idContainerType=tipo_cont,
                                    idFatherContainer=cont_padre,
                                    idGeometry=geometria,
                                    position=pos,
                                    barcode=barc,
                                    availability=avail,
                                    full=full)
                        stringa+=cont_padre.barcode+';'+tipo_cont.name+';'+barc+';'+pos+';'+geometria.name+'\n'
                        c.save()
                        print 'c',c
                        #devo salvare le feature    
                        print 'tipo aliq',b[0][0:3]                    
                        aliq=b[0][0:3]
        
                        aliqfeat=ContainerFeature(idFeature=feataliq,
                                                  idContainer=c,
                                                  value=aliq)
                        aliqfeat.save()
                        aimfeat=ContainerFeature(idFeature=feataim,
                                                 idContainer=c,
                                                 value='Stored')
                        aimfeat.save()
                        
                i+=1
                #if i==2:
                    #break
            f2=open(os.path.join(os.path.dirname(__file__),'archive_media/Historical/Plate_RL_SF.csv'),'w')
            f2.write(stringa)
            f2.close()
            return HttpResponse("ok")
        else:
            form = HistoricForm()
        variables = RequestContext(request, {'form':form})
        return render_to_response('historic/storico_plate.html',variables)
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

#serve per salvare le provette storiche collegate ai Box del file ArchiveTissue    
@transaction.commit_manually
@csrf_exempt
def HistoricBoxTube(request):
    try:
        if request.method=='POST':
            print request.POST   
            #mi da' la lista delle aliquote
            lista=request.POST.get('lista')
            parti=lista.split(',')
            listabarc=[]
            utente=User.objects.get(username='carlotta.cancelliere')
            #per il lashub
            for i in range(0,len(parti)):
                stringa=parti[i].split('|')
                print 'str',stringa
                barc=stringa[1].strip()
                listabarc.append(barc)
            Barcode_unico(listabarc, request)
            feataliq=Feature.objects.get(name='AliquotType')
            for i in range(0,len(parti)):
                stringa=parti[i].split('|')
                print 'str',stringa
                barc=stringa[0].strip()
                tipocont=ContainerType.objects.get(name='Tube')
                contpadre=Container.objects.get(barcode=barc)
                geom=Geometry.objects.get(name='1x1')
                c=Container(idContainerType=tipocont,
                            idFatherContainer=contpadre,
                            idGeometry=geom,
                            position=stringa[2],
                            barcode=stringa[1],
                            availability=1,
                            full=1,
                            present=1,
                            oneUse=tipocont.oneUse)
                c.save()
                print 'cont',c
                
                aliqfeat=ContainerFeature(idFeature=feataliq,
                                          idContainer=c,
                                          value='VT')
                aliqfeat.save()
                                
                data=stringa[4]
                dat=data.split('-')
                dtutente=timezone.datetime(int(dat[0]),int(dat[1]),int(dat[2]),1,0,0)
                print 'dtutente',dtutente                
                
                #devo salvare l'aliquota nella tabella
                print 'gen',stringa[3]
                a=Aliquot(genealogyID=str(stringa[3]),
                          idContainer=c,
                          position='',
                          startTimestamp=dtutente,
                          startOperator=utente
                          )
                a.save()
                
                #devo vedere se con l'aggiunta di questo campione la piastra si e' riempita
                if contpadre.idContainerType.idGenericContainerType.abbreviation=='plate':
                    regole_geom=json.loads(contpadre.idGeometry.rules)
                    dim = regole_geom['dimension']
                    x = int(dim[1])
                    y = int(dim[0])
                    print 'x',x
                    print 'y',y
                    #devo tenere conto anche della posmax
                    posmax=contpadre.idContainerType.maxPosition
                    if posmax!=None:
                        dimensione=x*y*int(posmax)
                        lcont=Container.objects.filter(idFatherContainer=contpadre,present=1)
                        print 'lcont',lcont
                        if len(lcont)==dimensione:
                            contpadre.full=1
                            print 'piastra piena'
                            contpadre.save()
            
            #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
            #address=request.get_host()+settings.HOST_URL
            #indir=prefisso+address
            indir=settings.DOMAIN_URL+settings.HOST_URL
            url = indir + '/clientHUB/saveAndFinalize/'
            print 'url',url
            values2 = {'typeO' : 'container', 'listO': str(listabarc)}
            requests.post(url, data=values2, verify=False, headers={"workingGroups" : get_WG_string()})
            
            transaction.commit()
            return HttpResponse("ok")
    except Exception,e:    
        transaction.rollback()
        print 'eccezione',e
        return HttpResponse("err")
    
#serve per salvare gli FF storici    
@transaction.commit_manually
@csrf_exempt
def HistoricFFPETube(request):
    try:
        if request.method=='POST':
            print request.POST   
            #mi da' la lista delle aliquote
            lista=request.POST.get('lista')
            parti=lista.split(',')
            
            tipoFF=ContainerType.objects.get(name='FF')
            
            for i in range(0,len(parti)):
                stringa=parti[i].split('|')
                print 'str',stringa
                barc_padre=stringa[0].strip()
                barc=stringa[1].strip()
                posiz=stringa[2].strip()
                padre=Container.objects.get(barcode=barc_padre)
                c=Container.objects.get(barcode=barc,idContainerType=tipoFF)
                c.position=posiz
                c.idFatherContainer=padre
                c.save()
                print 'cont',c
            
            transaction.commit()
            return HttpResponse("ok")
    except Exception,e:    
        transaction.rollback()
        print 'eccezione',e
        return HttpResponse("err")
    
#serve una sola volta per popolare la tabella delle aliquote con tutte quelle gia' presenti nel LAS al momento della transizione
@transaction.commit_manually
def CreateAliquot(request):
    try:   
        #devo fare una richiesta alla biobanca per farmi restituire tutte le aliquote presenti
        indir=Urls.objects.get(default=1).url
        req = urllib2.Request(indir+'/api/allaliquots', headers={"workingGroups" : 'admin'})
        u = urllib2.urlopen(req)
        #u = urllib2.urlopen(indir+'/api/allaliquots?workingGroups='+get_WG_string())
        data = json.loads(u.read())
        #print 'data',data
        costar=ContainerType.objects.get(name='PlateCostar')
        k=0
        errori=''
        for elem in data:
            #per ogni genealogy creo una riga nella tabella con gen e barcode
            #se il gen e' in una piastra Costar devo mettere il barcode della piastra e la posizione
            #del campione al suo interno
            print 'elem',elem
            barc=elem['barcode']
            gen=elem['gen']
            disp=elem['avail']
            print 'disp',disp
            diniz=elem['startdate']
            datainiz=diniz.split('-')
            dtiniz=timezone.datetime(int(datainiz[0]),int(datainiz[1]),int(datainiz[2]),1,0,0)
            print 'dtiniz',dtiniz
            
            operiniz=elem['startoperator']
            opinizi=User.objects.filter(username=operiniz)
            if len(opinizi)!=0:
                inizioper=opinizi[0]
            else:
                inizioper=None
            #Lo metto sempre a None perche' non so chi ha reso indisponibile un campione, nel caso disp=0
            #Invece per disp=1 e' giusto None 
            endoper=None
                
            print 'gen',gen
            
            pos=''
            cont=None
            dtfine=None
            if barc!='':
                lcont=Container.objects.filter(barcode=barc)
                if len(lcont)!=0:
                    cont=lcont[0]
                else:
                    errori+=gen+' '+barc+'\n'
                
            if cont!=None:    
                if cont.idFatherContainer!=None:
                    piascostar=False
                    #guardo se e' una piastra con i pozzetti
                    gentipo=ContTypeHasContType.objects.filter(idContainer=cont.idFatherContainer.idContainerType)
                    for tip in gentipo:
                        if tip.idContained==None:
                            piascostar=True
                    if piascostar:
                        pos=cont.position
                        cont=cont.idFatherContainer
                        if disp!=1:
                            dtfine=dtiniz
                            print 'dtfine4',dtfine
                    #e' il caso in cui il cont ha un padre e non e' piu' disp
                    else:
                        #se il campione non e' disponibile. Devo trovare la data di cancellazione.
                        if disp!=1:
                            liscont=ContainerAudit.objects.filter(barcode=barc).order_by('_audit_timestamp')
                            print 'liscont',liscont
                            dtfine=liscont[len(liscont)-1]._audit_timestamp
                            print 'dtfine',dtfine
                            
                #e' il caso in cui il cont non ha un padre e non e' piu' disp
                else:
                    #se il campione non e' disponibile. Devo trovare la data di cancellazione.
                    if disp!=1:
                        liscont=ContainerAudit.objects.filter(barcode=barc).order_by('_audit_timestamp')
                        print 'liscont2',liscont
                        dtfine=liscont[len(liscont)-1]._audit_timestamp
                        print 'dtfine2',dtfine
            else:
                #se il campione non e' disponibile. Devo trovare la data di cancellazione.
                #il problema e' che il barcode e' vuoto e non c'e' piu' perche' l'ho cancellato nella biobanca,
                #allora metto la data di fine uguale a quella di inizio
                if disp!=1:
                    dtfine=dtiniz
                    print 'dtfine3',dtfine
                
                    
            aliq=Aliquot(genealogyID=gen,
                         idContainer=cont,
                         position=pos,
                         startTimestamp=dtiniz,
                         endTimestamp=dtfine,
                         startOperator=inizioper,
                         endOperator=endoper
                         )
            aliq.save()
            print 'aliq',aliq
            k=k+1
            
            #if k==4:
                #break
        f1=open(os.path.join(os.path.dirname(__file__),'archive_media/Historical/Container.txt'),'w')
        f1.write(errori)
        f1.close()
        transaction.commit()
        return HttpResponse('ok')
    except Exception,e:    
        transaction.rollback()
        print 'eccezione',e
        return HttpResponse("err")

#serve una sola volta per creare per ogni container le sue feature relative alle aliquote che puo' contenere
@transaction.commit_on_success
def CreateFeature(request):
    try:
        #prendo tutti i cont presenti
        liscont=Container.objects.filter(present=1)
        lisgen=''
        lis_pezzi_url=[]
        feataliq=Feature.objects.get(name='AliquotType')
        defval=FeatureDefaultValue.objects.filter(idFeature=feataliq)
        for cont in liscont:
            #tolgo le piastre perche' hanno gia' una feature del tipo di aliq
            if cont.idContainerType.idGenericContainerType.abbreviation!='plate':
                #se e' una provetta prendo il tipo di aliq della piastra padre se e' vuota
                #se non ha un padre non metto niente
                if cont.idContainerType.idGenericContainerType.abbreviation=='tube':
                    #faccio la lista da dare alla biobanca per farmi restituire il tipo di aliq contenuta
                    laliq=Aliquot.objects.filter(idContainer=cont,endTimestamp=None)
                    if len(laliq)!=0:
                        lisgen+=laliq[0].genealogyID+'&'
                        #2000 e' il numero di caratteri scelto per fare in modo che la url
                        #della api non sia troppo lunga
                        if len(lisgen)>2000:
                            #cancello la virgola alla fine della stringa
                            strbarc=lisgen[:-1]
                            print 'strbarc',strbarc
                            lis_pezzi_url.append(strbarc)
                            lisgen=''
        #cancello la virgola alla fine della stringa
        strbarc=lisgen[:-1]
        print 'strbarc',strbarc
        if strbarc!='':
            lis_pezzi_url.append(strbarc)
        
        diz_tot={}    
        if len(lis_pezzi_url)!=0:
            indir=Urls.objects.get(default=1).url
            for elementi in lis_pezzi_url:
                req = urllib2.Request(indir+"/api/feature/"+elementi, headers={"workingGroups" : 'admin'})
                u = urllib2.urlopen(req)
                data = json.loads(u.read())
                print 'data',data
                for pezzi in data['data']:
                    print 'pezzi',pezzi
                    diz_tot[pezzi['aliquot']]=pezzi['type']
        print 'diz_tot',diz_tot
        
        for cont in liscont:
            tipoaliq=[]
            #tolgo le piastre perche' hanno gia' una feature del tipo di aliq
            if cont.idContainerType.idGenericContainerType.abbreviation!='plate':
                #se ha gia' qualche feature non lo tocco
                lfeat=ContainerFeature.objects.filter(idContainer=cont,idFeature=feataliq)
                if len(lfeat)==0:
                    #se e' una provetta prendo il tipo di aliq della piastra padre se e' vuota
                    #se non ha un padre non metto niente
                    if cont.idContainerType.idGenericContainerType.abbreviation=='tube':
                        laliq=Aliquot.objects.filter(idContainer=cont,endTimestamp=None)
                        if len(laliq)!=0:
                            tipoaliq.append(diz_tot[laliq[0].genealogyID])
                        else:
                            #devo prendere il tipo aliq della piastra padre
                            print 'padre',cont.idFatherContainer
                            if cont.idFatherContainer!=None:
                                contfeat=ContainerFeature.objects.get(idContainer=cont.idFatherContainer,idFeature=feataliq)
                                tipoaliq.append(contfeat.value)
                    elif cont.idContainerType.idGenericContainerType.abbreviation=='rack':
                        if cont.idContainerType.name=='Drawer':
                            tipoaliq.append('FF')
                        else:                        
                            for val in defval:
                                tipoaliq.append(val.idDefaultValue.abbreviation)
                    else:                        
                        for val in defval:
                            tipoaliq.append(val.idDefaultValue.abbreviation)
                    print 'tipoaliq',tipoaliq
                    for tip in tipoaliq:
                        contfeat=ContainerFeature.objects.get_or_create(idFeature=feataliq,
                                                                        idContainer=cont,
                                                                        value=tip)
                        
        return HttpResponse('ok')
    except Exception,e:    
        transaction.rollback()
        print 'eccezione',e
        return HttpResponse("err")
    
