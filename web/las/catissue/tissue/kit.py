from __init__ import *
from catissue.tissue.utils import *

'''@laslogin_required
@login_required
def KitsInitial(request):
    variables = RequestContext(request)   
    return render_to_response('tissue2/kit/kit_index.html',variables)'''

@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_insert_new_kit_type'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_insert_new_kit_type')
def SaveKitType(request):
    if request.method=='POST':
        print request.POST
        print request.FILES  
        form=KitTypeForm(request.POST)
        try:
            if form.is_valid():
                print 'valido'
                istruzioni=''
                if 'instruction' in request.FILES:
                    f=request.FILES['instruction']
                    fn = os.path.basename(f.name)
                    percorso=os.path.join(os.path.dirname(__file__),'tissue_media/Kit_instructions/'+fn)
                    open(percorso, 'wb').write(f.read())
                    print 'Il file "' + fn + '" e\' stato caricato'
                    istruzioni=f.name
                fine=True
                nome=request.POST.get('name').strip()
                produttore=request.POST.get('producer').strip()
                capacit=request.POST.get('capacity').strip()
                catal=request.POST.get('catalogue').strip()
                
                k=KitType(name=nome,
                       producer=produttore,
                       capacity=int(capacit),
                       catalogueNumber=catal,
                       instructions=istruzioni
                       )
                k.save()
                variables = RequestContext(request, {'fine':fine,'nome':nome,'produttore':produttore,'capacit':capacit,'catal':catal})
                return render_to_response('tissue2/kit/kit_type.html',variables)
            else:
                variables = RequestContext(request, {'form':form})
                return render_to_response('tissue2/kit/kit_type.html',variables)
        except Exception,e:
            print 'err',e
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('tissue2/index.html',variables)
    else:
        form = KitTypeForm()
    variables = RequestContext(request, {'form':form})
    return render_to_response('tissue2/kit/kit_type.html',variables)

@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_register_new_kit'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_register_new_kit')
def SaveSingleKit(request):
    if request.method=='POST':
        print request.POST
        form=SingleKitForm(request.POST)
        try:
            if form.is_valid():
                print 'valido'
                tipo_kit=KitType.objects.get(id=request.POST.get('kit_Type'))
                request.session['tipokit']=tipo_kit
                nome=tipo_kit.name
                #nome=nome.replace(' ','%20');
                da=request.POST.get('expiration_Date').strip()
                lotto=request.POST.get('lot').strip()
                variables = RequestContext(request, {'kit':nome,'data':da,'lotto':lotto})
                return render_to_response('tissue2/kit/final_single_kit.html',variables)
            else:
                variables = RequestContext(request, {'form':form})
                return render_to_response('tissue2/kit/single_kit.html',variables)
        except:
            transaction.rollback()
            errore=True
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('tissue2/index.html',variables)
    else:
        form = SingleKitForm()
    variables = RequestContext(request, {'form':form})
    return render_to_response('tissue2/kit/single_kit.html',variables)

@transaction.commit_on_success
@laslogin_required
@login_required
#@user_passes_test(lambda u: u.has_perm('tissue.can_view_register_new_kit'),login_url=settings.BASE_URL+'/tissue/error/')
@permission_decorator('tissue.can_view_BBM_register_new_kit')
def SaveFinalSingleKit(request):
    if request.method=='POST':
        print request.POST
        try:
            listakit=[]
            lista=[]
            if request.session.has_key('tipokit'):
                tipo=request.session.get('tipokit')
            numerokit=request.POST.get('tot_righe')
            lotto=request.POST.get('lotto').strip()
            #data ha la notazione anno-mese-giorno
            data=request.POST.get('data').strip()        
            for i in range(0,int(numerokit)):
                barc='barc_'+str(i)
                codice=request.POST.get(barc).strip()
                #per gestire il caso in cui cancello una riga dalla lista dei kit
                if codice!=None:
                    print 'codice',codice
                    print 'tipo',tipo
                    k=Kit(idKitType=tipo,
                           barcode=codice,
                           openDate=None,
                           expirationDate=data,
                           remainingCapacity=tipo.capacity,
                           lotNumber=lotto
                           )
                    k.save()
                    val=str(tipo.name)+'|'+codice+'|'+data+'|'+lotto
                    print 'val', val
                    lista.append(val)
                    #do 1 come numero fittizio, tanto poi js mi mette il giusto
                    #numero nella prima colonna
                    listakit.append(ReportToHtml([(i+1),str(tipo.name),codice,data,lotto]))
                    print 'k',k
            variables = RequestContext(request, {'fine':True,'lista':listakit})
            return render_to_response('tissue2/kit/final_single_kit.html',variables)
        except Exception,e:
            transaction.rollback()
            errore=True
            print 'err',e
            variables = RequestContext(request, {'errore':errore})
            return render_to_response('tissue2/index.html',variables)

'''#@user_passes_test(lambda u: u.has_perm('tissue.can_view_register_new_kit'),login_url='/tissue/error/')
@permission_decorator('tissue.can_view_BBM_register_new_kit')
def createPDFKit(request):
    if request.session.get('listafinalekit'):
        lista=[]
        listak = request.session.get('listafinalekit')
        print 'createpdfkit'
        for i in range(0,len(listak)):
            s=listak[i].split('|')
            lista.append(ReportKitToHtml(i+1,s[0],s[1],s[2],s[3],'s'))
        print 'lista',lista
        response=PDFMaker(request, 'Inserted_kits.pdf', 'tissue2/kit/pdf_kit.html', lista)
       
        return response
    else:
        return HttpResponseRedirect(reverse('tissue.views.index'))

#@user_passes_test(lambda u: u.has_perm('tissue.can_view_register_new_kit'),login_url='/tissue/error/')
@permission_decorator('tissue.can_view_BBM_register_new_kit')
def createCSVKit(request):
    if request.session.get('listafinalekit'):
        listak = request.session.get('listafinalekit') 
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Inserted_kit.csv'
        writer = csv.writer(response)
        writer.writerow(["N;" "KitType;""Barcode;""ExpirationDate;""LotNumber;"])
        for i in range(0,listak.__len__()):
            val=listak[i].split('|')
            csvString=str(i+1)+";"+str(val[0])+";"+str(val[1])+";"+val[2]+";"+val[3]
            writer.writerow([csvString])
        return response 
    else:
        return HttpResponseRedirect(reverse('tissue.views.index'))'''
