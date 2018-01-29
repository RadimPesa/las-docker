#!/usr/bin/python
# Set up the Django Environment
import sys
sys.path.append('/srv/www/biobank')
from django.core.management import setup_environ 
import settings
setup_environ(settings)
import datetime
from catissue.tissue.models import *
from catissue.tissue.utils import *
from catissue.tissue.genealogyID import *
from django.template.loader import render_to_string
from django.template.context import RequestContext
import xlwt
from django.db.models import Q

def Trova_aliquote():
    try:
        enable_graph()
        disable_graph()
        tipoaliq=AliquotType.objects.get(abbreviation='FF')
        lisaliq=Aliquot.objects.filter((Q(uniqueGenealogyID__iendswith='FF0200')|Q(uniqueGenealogyID__iendswith='FF0300')|Q(uniqueGenealogyID__iendswith='FF0400'))&Q(idAliquotType=tipoaliq))
        print 'len aliq prima',len(lisaliq)
        lisserie=Serie.objects.filter(operator='gabriele.picco')
        #print 'lisserie',lisserie
        lisampl=SamplingEvent.objects.filter(idSerie__in=lisserie)
        #print 'lisampl',lisampl
        listaal=Aliquot.objects.filter(Q(idAliquotType=tipoaliq)&Q(idSamplingEvent__in=lisampl))
        print 'aliq picco',listaal
        print 'len picco',len(listaal)
        lisfin=lisaliq.exclude(id__in=listaal)
        print 'len dopo',len(lisfin)
        #lista per salvare le parti iniziali dei gen
        lisgen=[]
        for al in lisfin:
            gen=GenealogyID(al.uniqueGenealogyID)
            iniziogen=gen.getCase()+gen.getTissue()+gen.getGeneration()
            if iniziogen not in lisgen:
                lisgen.append(iniziogen)
        print 'lisgen',lisgen
        print 'len lista',len(lisgen)
        scrivi = xlwt.Workbook(encoding="utf-8")
        for inizio in lisgen:
            lisal=Aliquot.objects.filter(uniqueGenealogyID__istartswith=inizio)
            if len(lisal)!=0:
                sh=scrivi.add_sheet(inizio)
                sh.write(0,0,'Barcode')
                sh.write(0,1,'Genealogy')
                sh.write(0,2,'Sampling date')
                sh.write(0,3,'operator')
                sh.write(0,4,'Availability')
                sh.write(0,5,'Type')
                i=1
                for al in lisal:
                    sh.write(i,0,al.barcodeID)
                    sh.write(i,1,al.uniqueGenealogyID)
                    data=al.idSamplingEvent.samplingDate
                    dat=str(data).split('-')
                    datfin=dat[2]+'-'+dat[1]+'-'+dat[0]
                    sh.write(i,2,datfin)
                    sh.write(i,3,al.idSamplingEvent.idSerie.operator)
                    if al.availability==1:
                        disp='True'
                    else:
                        disp='False'
                    sh.write(i,4,disp)
                    sh.write(i,5,al.idAliquotType.longName)
                    i=i+1
        scrivi.save("Casi_FFPE.xls")        
    except Exception,e:
        print 'err',e
    return

if __name__=='__main__':
    Trova_aliquote()
    