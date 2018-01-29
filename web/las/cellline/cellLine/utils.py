from cellLine.forms import *
from cellLine.genealogyID import *
from cellLine.models import *
from cellLine import markup
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.utils import simplejson
from string import maketrans
from LASAuth.decorators import laslogin_required
import datetime, webbrowser, os.path

class Simple:
    def __init__(self, m, select):
       self.attributes={}
       for f in m._meta.fields:
           if len(select) == 0:
                self.attributes[f.name] = str(m.__getattribute__(f.name))
           elif f.name in select:
                self.attributes[f.name] = str(m.__getattribute__(f.name))
    def toStr(self):
        output = ''
        a = []
        for k, v in self.attributes.items():
            b={k:str(v)}
            a.append(b)
        return json.dumps(a)
    def getAttributes(self):
        return self.attributes



#per mappare da numeri a lettere maiuscole
partenza = "12345678"
destinazione = "ABCDEFGH"
trasftab = maketrans(partenza, destinazione)

#classe usata per creare le varie tabelle della seconda schermata dell'interfaccia degli espianti
class Plate():
    def table_vital(self):
        page=markup.page()
        page.table(id='vital',align='center')
        page.th(colspan=7)
        page.add('VIABLE')
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
                page.td(width="20px", style="background-color: grey;")
                #page.button(type='submit', id='v-'+str(i).translate(trasftab)+str(j))
                #page.add(str(0))
                #page.button.close()
                page.td.close()
            page.tr.close()
        page.table.close()
        return page
    def table_archive(self):
        page=markup.page()
        page.table(id='tableContainer')
        page.th(colspan=13)
        page.add('DESTINATION CONTAINER')
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
                page.td(width="20px", style="background-color: grey;")
                #page.button(type='submit', id='r-'+str(i).translate(trasftab)+str(j))
                #page.add(str(0))
                #page.button.close()
                page.td.close()
            page.tr.close()
        page.table.close()
        return page
    def volume_count(self):
        page = markup.page()
        page.table(align='center',id='tab_cv')
        page.tr()
        page.td()
        page.strong('PBMC: ')
        page.td.close()
        page.td()
        page.button(type='submit', id='pbmc')
        page.button.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Barcode:')
        page.label.close()
        page.input(type='text', id='barcpbmc',maxlength=45, size='8')
        page.td.close()
        page.td(style='font-size:15px;padding-left:1em;')
        page.input(type='radio', name='cho_VT', value='tube', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Tube')
        page.span.close()
        page.input(type='radio', name='cho_VT', value='plate', style='display:inline;')
        page.span(style='display:inline;')
        page.add('Plate')
        page.span.close()
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Volume(ml):')
        page.label.close()
        page.input(type='text', id='volpbmc',maxlength=10, size=6)
        page.td.close()
        page.td(style='padding-left:2em;')
        page.label('Count(cell/ml):')
        page.label.close()
        page.input(type='text', id='contapbmc',maxlength=10, size=6)
        page.td.close()
        page.td()
        page.p("-", id = 'pbmcoutput', align='center' )
        page.td.close()
        page.tr.close()
        page.table.close()
        return page