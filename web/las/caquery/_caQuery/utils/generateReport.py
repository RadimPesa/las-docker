from __init__ import *

def writeReport(dataTable, formatFile, dest, filename):
    try:

        result = StringIO.StringIO()
        if formatFile == 'pdf':
            fName = filename + '.pdf'
            html  = render_to_string('reportPdf.html', { 'pagesize' : 'landscape', 'header':dataTable['header'], 'body':dataTable['body'], 'title':dataTable['title']}, context_instance=RequestContext(request))
            pdf = pisa.CreatePDF(StringIO.StringIO(html.encode("UTF-8")), dest=result )
            if pdf.err:
                raise Exception("error in rendering pdf")
        elif formatFile == 'las':
            fName = filename + '.las'
            result.write('\t'.join(dataTable['header']))
            result.write('\n')
            for row in dataTable['body']:
                result.write('\t'.join(row))
                result.write('\n')
        elif formatFile == 'data':
            fName = filename +  '.data'
            for row in dataTable['body']:
                result.write('\t'.join(row))
                result.write('\n')
        elif formatFile == 'excel':
            fName = filename +  '.xls'
            wbk = xlwt.Workbook()
            sheet = wbk.add_sheet('Data')
            fontBold = xlwt.Font()
            fontBold.bold = True
            patternH = xlwt.Pattern() # Create the Pattern 
            patternH.pattern = xlwt.Pattern.SOLID_PATTERN # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12 
            patternH.pattern_fore_colour = 22 # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray, the list goes on... 
            patternC = xlwt.Pattern()
            patternC.pattern = xlwt.Pattern.SOLID_PATTERN
            patternC.pattern_fore_colour = 5
            styleHeader = xlwt.XFStyle()
            styleHeader.pattern = patternH
            styleHeader.font = fontBold
            styleCell = xlwt.XFStyle()
            styleCell.pattern = patternC
            row = 0
            col = 0
            for h in dataTable['header']:
                sheet.write(row, col, str(h), styleHeader)
                col +=1
            row += 1
            for r in dataTable['body']:
                col = 0
                for cell in r:
                    dCell = cell
                    try:
                        float(dCell)
                        dCell = float(dCell)
                    except ValueError:
                        pass
                    sheet.write(row, col, dCell)
                    col+=1
                row +=1
            wbk.save(result) # write to stdout
        fout = open (os.path.join(dest, fName) ,"wb")
        fout.write(result.getvalue())
        fout.close()
        return fName
    except Exception, e:
        print "exception",e
        return ''
