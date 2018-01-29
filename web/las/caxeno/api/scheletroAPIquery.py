class H(BaseHandler):
    allowed_methods = ('GET','POST')
    def read(self, request):
        try:
            return {'data':'ok'}
        except Exception, e:
            print e
            return {"data": 'err'}
    @csrf_exempt
    def create(self, request):

        try:
            filter_list = []
            successorDict = {'Mice':'Mice', 'Implants':'Implants', 'Explants':'Explants', 'Qual. Measures':'Qual. Measures', 'Quant.Measures':'Quant.Measures', 'Treatment Arms':'Treatment Arms', 'Treatment Protocols':'Treatment Protocols'}
            predecessor = request.POST['predecessor']
            successor = request.POST['successor']
            listID = request.POST['list']
            parameter = request.POST['parameter']
            values = request.POST['values'] #to split
            argument_list = []
            if predecessor == 'start':
                if values == "":
                    query = .objects.all()
                else:
                    if parameter == 

                    elif parameter == 

            else:
                print 'else'
                listID = ast.literal_eval(listID)
                listID = listID['id']
                if predecessor == 
                elif predecessor == 
                elif predecessor == 
                    
                if values == "":                    
                    query = dataList
                else:
                    if parameter == 
                    elif parameter == 

            if successor in successorDict.keys():
                print 'f'
                result = []
                for q in query:
                    print q
                    result.append(q.id)
                print 'res ID'
                print result
                return {'id':result}
            elif successor == 'End':
                print 'end'
                result = []
                for q in query:
                    result.append(Simple(q, []).getAttributes())
                print 'res obj'
                print result
                return {'objects':result}
                    
        except Exception, e:
            print e
            return {"code": 'err'}
