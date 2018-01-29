    
#per cancellare i dati dalla sessione
def CancSession(request):
    if request.session.has_key('aliquotCollectionFunnel'):
        del request.session['aliquotCollectionFunnel']
        
        
    
