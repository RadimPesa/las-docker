import optparse, os, sys
from openpyxl.reader.excel import load_workbook
import xlrd

def insertError (aliquots, errors, keyErr, mistake):
    if errors.has_key(keyErr) == False:
        errors[keyErr] = [aliquots[keyErr]]
    errors[keyErr].append(mistake)
    
def transformCSVxlsx (fileName, aliquots, errors):
    wb=load_workbook(filename=fileName)
    for sheet in wb.worksheets:
        #csv_file='%s.txt' % sheet.title
        #print 'Creating %s' % csv_file
        #fd=open(csv_file, 'wt')
        i = 0
        plate = ''
        for row in sheet.rows:
            values=[]
            for cell in row:
                value=cell.value
                if value is None:
                    value=''
                if not isinstance(value, unicode):
                    value=unicode(value)
                value=value.encode('utf8')
                if i == 0 and plate == '':
                    if value.find('_'):
                        plate = value.split('_')[-1]
                    else:
                        plate = value
                elif i > 1:
                    values.append(value)
            if i > 1:
                tupleRow = (plate, str(values[0])+str(values[1]), values[2], fileName.replace('/home/alessandro/Dropbox',''))
                if aliquots.has_key (values[3]):
                    
                    insertError (aliquots, errors, values[3], tupleRow )
                else:
                    aliquots[values[3]] = tupleRow
            i += 1

def transformCSVxls (fileName, aliquots, errors, outputFile):
    print 'start transform'
    pathF = "implants/implantedMice.txt"
    f = fileHandle = open (pathF)
    miceList = []
    sh1List = []
    sh2List = []
    for a in f:
        row = a.strip() #per cancellare eventuali \n alla fine del file
        r = row.strip().split('\t')
        miceList.append({'barcodeMouse':r[0].upper(),'newG':r[1]+'000000000','oldG':r[2]})

    wb = xlrd.open_workbook(fileName)
    sh = wb.sheet_by_index(0)
    sh2 = wb.sheet_by_index(1)
    for rownum in range(sh.nrows):
        values = sh.row_values(rownum)
        if values[0][0:4] == "IMPL":
            sh1List.append({'seriesID':values[0], 'operator':values[1], 'date':str(make_date(float(values[2]) ) )} )
    testDict = {}
    for rownum in range(sh2.nrows):
        values = sh2.row_values(rownum)
        #if values[0][0:6] == "IMPLdt" and values[2] != 23:
        if len(str(values[2])) > 2:
            if values[0][0:6] == "IMPLdt" and values[2][0:3] == "000":
                sh2List.append({'seriesID':values[1].replace('-',''), 'detailID':values[0], 'barcodeMouse':values[2].upper(), 'site':values[7]})
                if testDict.has_key(values[2]):
                    print values[2]
                testDict.update({values[2]:values[2]})
    print 'test doppi',len(testDict)
    print 'sh1',len(sh1List)
    print 'sh2',len(sh1List)
    print 'miceList',len(miceList)
    barcodeList = []
    i = 0
    for m in miceList:
        index = miceList.index(m)
        barcode = m['barcodeMouse']
        for value in sh2List:
            if value['barcodeMouse'] == barcode:
                site = value['site']
                if site == "LIVER":
                    site = "LI"
                series = value['seriesID']
                for v in sh1List:
                    if v['seriesID'] == series:
                        #print i
                        i = i + 1 
                        operator = v['operator']
                        date = v['date']
                        #print date
                        miceList[index].update({'date':date, 'operator':operator,'site':site})


    fout = open (outputFile, 'w')
    for m in miceList:
        #print m
        barcode = m['barcodeMouse']
        date = m['date']
        newG = m['newG']
        oldG = m['oldG']
        operator = m['operator']
        site = m['site']
        #print barcode,date,newG,operator,oldG
        fout.write (str(barcode) + '\t' + str(newG) + '\t' + str(oldG) + '\t' + str(date) + '\t' + str(operator) + '\t' + str(site) + '\t' + str(oldG[0:10] + date.replace('-','') + '.0') + '\n')
    fout.close()

        
def make_date(xlnum):
    from datetime import date
    from datetime import timedelta
    year = timedelta(days=xlnum)
    my_date = date(1899, 12, 30)
    return my_date + year

def main():
    opt = optparse.OptionParser()
    opt.add_option('--folder', '-f', default='./', help="Folder of input plates")
    opt.add_option('--output', '-o', default='output.txt', help="Output file for aliquots")
    #opt.add_option('--error', '-e', default='errors.txt', help="error file for aliquots")
    #opt.add_option('--tanomy', '-t', default='tax_gen.txt', help='source taxonomy of previous steps')

    option, arguments = opt.parse_args()
    aliquots = {}
    errors = {}
    print "start"
    for fileName in os.listdir(option.folder):
        print fileName
        fileN = os.path.join (option.folder, fileName)
        print fileN
        if os.path.isfile (fileN):
            ext = os.path.splitext(fileN)[1]
            if str(ext) == '.xls':
                transformCSVxls (fileN, aliquots, errors, option.output)                
            elif str(ext) == '.xlsx':
                transformCSVxlsx (fileN, aliquots, errors)
    #print aliquots
    #pruneErrors (aliquots, errors)
    #writeAliquots (aliquots, option.output)
    #writeErrors (option.error, errors)

if __name__=='__main__':
    main()
