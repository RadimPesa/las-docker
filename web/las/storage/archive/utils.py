from archive import markup
from archive.models import *
from string import maketrans
from django.db import transaction
from django.http import HttpResponse
from django.db.models import Q
from django.conf import settings
import operator,json,requests
from global_request_middleware import *

#per mappare da numeri a lettere maiuscole
partenza = "123456789"
destinazione = "ABCDEFGHI"
trasftab = maketrans(partenza, destinazione)

class Tabella(models.Model):
    def table_vital(self):
        page=markup.page()
        page.table(id='vital',align='center')
        page.th(colspan=7)
        page.add('VITAL')
        page.th.close()
        page.tr()
        page.td()
        page.td.close()
        for i in range(1,7):
            page.td(align='center')
            page.strong(i)
            page.td.close()
        page.tr.close()
        for i in range (1,5):
            page.tr()
            page.td()
            page.br()
            page.strong(str(i).translate(trasftab))
            page.td.close()
            for j in range(1,7):
                page.td()
                page.button(type='submit', id='v-'+str(i).translate(trasftab)+str(j))
                #page.add(str(0))
                page.button.close()
                page.td.close()
            page.tr.close()
        page.table.close()
        return page
    def table_rna(self):
        page=markup.page()
        page.table(id='rna')
        page.th(colspan=13)
        page.add('RNA LATER')
        page.th.close()
        page.tr()
        page.td()
        page.td.close()
        for i in range(1,13):
            page.td(align='center')
            page.strong(i)
            page.td.close()
        page.tr.close()
        for i in range (1,9):
            page.tr()
            page.td()
            page.br()
            page.strong(str(i).translate(trasftab))
            page.td.close()
            for j in range(1,13):
                page.td()
                page.button(type='submit', id='r-'+str(i).translate(trasftab)+str(j))
                #page.add(str(0))
                page.button.close()
                page.td.close()
            page.tr.close()
        page.table.close()
        return page
    def table_sf(self):
        page=markup.page()
        page.table(id='sf')
        page.th(colspan=13)
        page.add('SNAP FROZEN')
        page.th.close()
        page.tr()
        page.td()
        page.td.close()
        for i in range(1,13):
            page.td(align='center')
            page.strong(i)
            page.td.close()
        page.tr.close()
        for i in range (1,9):
            page.tr()
            page.td()
            page.br()
            page.strong(str(i).translate(trasftab))
            page.td.close()
            for j in range(1,13):
                page.td()
                page.button(type='submit', id='s-'+str(i).translate(trasftab)+str(j))
                #page.add(str(0))
                page.button.close()
                page.td.close()
            page.tr.close()
        page.table.close()
        return page
    def drawer(self):
        page=markup.page()
        page.table(id='rna',align='center')
        page.th(colspan=15)
        page.add('DRAWER/PLATE')
        page.th.close()
        page.tr()
        page.td()
        page.td.close()
        for i in range(1,15):
            page.td(align='center')
            page.strong(i)
            page.td.close()
        page.tr.close()
        for i in range (1,5):
            page.tr()
            page.td()
            page.br()
            page.strong(str(i).translate(trasftab))
            page.td.close()
            for j in range(1,15):
                page.td()
                page.button(type='submit', id='v-'+str(i).translate(trasftab)+str(j))
                #page.add(str(0))
                page.button.close()
                page.td.close()
            page.tr.close()
        page.table.close()
        return page

#funzione per creare il json con le informazioni su come e' fatta la piastra
def creaGeometria(xDim,yDim):
    stringa='{"dimension": ['+yDim+','+xDim+'],"row_label": ['
    if int(xDim)<27:
        for i in range(0,int(xDim)):
            stringa=stringa+'"'+chr(i+ord('A'))+'",'
        #tolgo l'ultima virgola alla fine della stringa
        lung=len(stringa)-1
        stringanuova=stringa[:lung]
        stringa=stringanuova
        stringa+='],"column_label": ['
        for i in range(0,int(yDim)):
            stringa+=str(i+1)+','
        #tolgo l'ultima virgola alla fine della stringa
        lung=len(stringa)-1
        stringanuova=stringa[:lung]
        stringa=stringanuova
        stringa+='],"items": ['
        for i in range(0,int(xDim)):
            for j in range(0,int(yDim)):
                stringa+='{"id":"'+chr(i+ord('A'))+str(j+1)+'","position":['+str(j+1)+','+str(i+1)+']},'
        #tolgo l'ultima virgola alla fine della stringa
        lung=len(stringa)-1
        stringanuova=stringa[:lung]
        stringa=stringanuova
        stringa+=']}'
        print 'strr',stringa
    else:
        x_mezzi=int(int(xDim)/2)
        print 'x_mezzi',x_mezzi
        for i in range(0,2):
            for j in range(0,x_mezzi):
                #print 'j',j
                stringa=stringa+'"'+chr(i+ord('A'))+chr(j+ord('A'))+'",'
        #tolgo l'ultima virgola alla fine della stringa
        lung=len(stringa)-1
        print 'lung',lung
        stringanuova=stringa[:lung]
        stringa=stringanuova
        stringa+='],"column_label": ['
        for i in range(0,int(yDim)):
            stringa+=str(i+1)+','
        #tolgo l'ultima virgola alla fine della stringa
        lung=len(stringa)-1
        stringanuova=stringa[:lung]
        stringa=stringanuova
        stringa+='],"items": ['
        indice1=1
        indice2=1
        for k in range(0,2):
            for i in range(0,int(x_mezzi)):
                for j in range(0,int(yDim)):
                    stringa+='{"id":"'+chr(k+ord('A'))+chr(i+ord('A'))+str(j+1)+'","position":['+str(indice1)+','+str(indice2)+']},'
                    indice1+=1
                indice1=1
                indice2+=1
                    
        #tolgo l'ultima virgola alla fine della stringa
        lung=len(stringa)-1
        stringanuova=stringa[:lung]
        stringa=stringanuova
        stringa+=']}'
        print 'strr',stringa
    return stringa

#serve per trasformare la visualizzazione delle piastre inserite in un formato
#compatibile con la visualizzazione in html
#si puo' usare sia per la tabella di riepilogo che per la creazione del pdf
def ReportPlateToHtml(barcode,aim,aliq,x,y,rack,freezer,pos,pdf):
    if pdf=="s":
        return '<tr align="center"><td><br>'+barcode+'</td><td><br>'+aim+'</td><td><br>'+aliq+'</td><td><br>'+x+'</td><td><br>'+ y +'</td><td><br>'+ rack +'</td><td><br>'+ freezer +'</td><td><br>'+ pos +'</td></tr>'
    else:
        return '<tr align="center"><td>'+barcode+'</td><td>'+aim+'</td><td>'+aliq+'</td><td>'+x+'</td><td>'+ y +'</td><td>'+ rack +'</td><td>'+ freezer +'</td><td>'+ pos +'</td></tr>'

#per aggiornare i container mettendo full a 1 
@transaction.commit_on_success
def SetFull(request):
    try:
        lista1=[]
        prov=GenericContainerType.objects.get(name='Tube/BioCassette')
        tipicont=ContainerType.objects.filter(idGenericContainerType=prov)
        #print 'tipi',tipicont
        for tipcont in tipicont:
            lista1.append( Q(**{'idContainerType': tipcont.id} ))
        listacont=Container.objects.filter(Q(present=1)&Q(full=0)&~Q(reduce(operator.or_, lista1)))
        for cont in listacont:
            #devo vedere quanti figli ha ogni container
            print 'cont',cont
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
        return HttpResponse("ok")
    except Exception,e:
        print 'err',e
        transaction.rollback()
        return HttpResponse("err")

def Barcode_unico(barcode,request):
    try:
        #faccio la chiamata al LASHub per vedere se esiste gia' il codice
        presente=False
        #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
        #address=request.get_host()
        #indir=prefisso+address+settings.HOST_URL
        indir=settings.DOMAIN_URL+settings.HOST_URL
        url = indir + '/clientHUB/checkBarcode/'
        print 'url',url
        #la variabile barcode e' gia' una lista
        values = {'barcode' : str(barcode)}
        r = requests.post(url, data=values, verify=False, headers={"workingGroups" : get_WG_string()})
        if r.text=='False':
            presente=True
        elif r.text=='not active':
            pias=Container.objects.filter(barcode__in=barcode)
            print 'pias', pias
            if pias.count()!=0:
                presente=True
        return presente       
    except Exception,e:
        print 'err',e
        return True 
    
def CheckBarcodeHub(barcode,request):
    lista=[]
    print 'barc',barcode
    #faccio la chiamata al LASHub per vedere se esiste gia' il codice
    #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
    #address=request.get_host()
    #indir=prefisso+address+settings.HOST_URL
    indir=settings.DOMAIN_URL+settings.HOST_URL
    url = indir + '/clientHUB/checkBarcode/'
    print 'url',url
    lista.append(barcode)
    values = {'barcode' : str(lista)}
    r = requests.post(url, data=values, verify=False, headers={"workingGroups" : get_WG_string()})
    print 'r.text',r.text
    return r

def SaveinLASHub(request,listabarc):
    #prefisso= 'https://' if settings.LAS_AUTH_USE_HTTPS else 'http://'
    #address=request.get_host()+settings.HOST_URL
    #indir=prefisso+address
    indir=settings.DOMAIN_URL+settings.HOST_URL
    url = indir + '/clientHUB/saveAndFinalize/'
    print 'url',url
    values2 = {'typeO' : 'container', 'listO': str(listabarc)}
    requests.post(url, data=values2, verify=False, headers={"workingGroups" : get_WG_string()})
    
#dati degli id della tabella containertype serve a verificare se il tipo figlio puo' stare nel padre
def ControllaTipo(tipopadre,tipofiglio):
    tip=ContainerType.objects.get(id=tipofiglio)
    tippadre=ContainerType.objects.get(id=tipopadre)
    print 'tip',tip
    #vedo quali container possono contenere il tipo scelto
    listatipi=ContTypeHasContType.objects.filter(idContained=tip)
    print 'lista',listatipi
    for tipi in listatipi:
        if tipi.idContainer.id==tippadre.id:
            print 'tipi',tipi.idContainer
            return True
    return False

#dati degli id della tabella default value, vedo se il tipo di aliq presente nel padre puo' stare nel figlio
def ControllaAliquota(aliqpadre,aliqfiglio):
    laliqp=aliqpadre.split('&')
    laliqf=aliqfiglio.split('&')
    print 'aliq figlio',laliqf
    return set(laliqf).issubset(set(laliqp))

#per vedere se una posizione e' presente all'interno delle regole della geometria
def ControllaPosizioni(regole,posiz):
    items=regole['items']
    for oggetti in items:
        if oggetti['id']==posiz:
            return True
    return False

#per vedere se un container si e' riempito con l'aggiunta di figli
def ImpostaPieno(cont_padre):
    lista_c=Container.objects.filter(idFatherContainer=cont_padre)
    regole=json.loads(cont_padre.idGeometry.rules)
    dimensioni=regole['dimension']
    xDim=dimensioni[1]
    yDim=dimensioni[0]
    posto_tot=xDim*yDim*int(cont_padre.idContainerType.maxPosition)
    print 'posti_tot',posto_tot
    print 'lista',len(lista_c)
    if len(lista_c)>=posto_tot:
        return True
    else:
        return False
    
#per avere la lista delle aliquote che possono andare in un container
def ListaAliquote(elem):
    feat=Feature.objects.get(name='AliquotType')
    liscontfeat=ContainerFeature.objects.filter(idContainer=elem,idFeature=feat)
    if len(liscontfeat)==0:
        lisfeat=FeatureDefaultValue.objects.filter(idFeature=feat)
        listemp=[]
        for fea in lisfeat:
            listemp.append(fea.idDefaultValue.id)
        lisval=DefaultValue.objects.filter(id__in=listemp)
    else:
        listipi=[]
        for contfeat in liscontfeat:
            listipi.append(contfeat.value)
        lisval=DefaultValue.objects.filter(abbreviation__in=listipi)
    print 'lisval',lisval
    tipifin=''
    for val in lisval:
        tipifin+=str(val.id)+'&'
    listipifin=tipifin[:-1]
    print 'listipifin',listipifin
    return listipifin
    
#per cancellare i dati dalla sessione
def CancSession(request):
    if request.session.has_key('listanuovicontainer'):
        del request.session['listanuovicontainer']
    if request.session.has_key('dizgenbarcode'):
        del request.session['dizgenbarcode']
    if request.session.has_key('returnaliquotslast'):
        del request.session['returnaliquotslast']
    if request.session.has_key('lisArchiveContainer'):
        del request.session['lisArchiveContainer']
    if request.session.has_key('lisChangeContainer'):
        del request.session['lisChangeContainer']
        
            