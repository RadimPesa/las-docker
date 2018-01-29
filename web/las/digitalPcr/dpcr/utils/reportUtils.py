from __init__ import *


#crea il codice HTML per la tabella con il report
def reportHtml (data, header, title):
    table =  "<h1>" + title + "</h1> <table border=\"1\"> <tr> "
    for h in header:
                table += "<td><b>" + str(h) + "</b></td> "                
    table += "</tr> "
    for d in data:
        table += "<tr> "
        for item in d:
            table+= "<td align=\"center\"><br>" + str(item) + "</td> "
        table += "</tr> "
    table+= "</table>"
    return table

#per creare il PDF
def PDFMaker(request, nameSession, nameFile, template):
    dictData = {}
    for name in nameSession:
        if request.session.get(name):
            dictData[name] = request.session.get(name)
        else:
            return HttpResponseRedirect(reverse("dpcr.views.home"))
    print dictData
    file_data = render_to_string(template, dictData, RequestContext(request))
    myfile = cStringIO.StringIO()
    pisa.CreatePDF(file_data, myfile)
    myfile.seek(0)
    response =  HttpResponse(myfile, mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + nameFile
    print 'pdf'
    return response


#per creare il CSV
def CSVMaker(request, nameSession, nameFile, columns):
    list_report = []
    csvString = ''
    if request.session.get(nameSession):
        list_report = request.session.get(nameSession)
    else:
        return HttpResponseRedirect(reverse("dpcr.views.home"))
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + nameFile
    writer = csv.writer(response, delimiter='\t')
    if len(columns) > 0:
        writer.writerow(columns)
    for i in list_report:
        csvString += i.replace('<td align="center">','').replace('<br>','').replace('</td>','\t').replace('<tr>','').replace('</tr>','\n')
    csvString = csvString[:-1]
    for l in csvString.split('\n'):
        writer.writerow(l.split('\t'))
    return response
