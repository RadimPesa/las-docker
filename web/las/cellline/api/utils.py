from cellLine.models import *
from django.db import transaction
from django.db.models import Q
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
import string, urllib, urllib2, json


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
    
def translateLineage(lineage):
    try:
        result = 0
        if lineage[0].isdigit():
            first = int(lineage[0])
            if first:
                result += (26 + first) * 36
        else:
            result += (ord(lineage[0]) - 64 )  * 36

        if lineage[1].isdigit():
            second = int(lineage[1])
            if second:
                result += 26 + second
        else:
            result += ord(lineage[1]) - 64 

        return result
    except Exception, e:
        print e
        pass
    return

#calcola il nuovo lineage per l genID degli impianti
def newLineage(n):
    try:
        print 'newLineage(): integer riceived = '+str(n)
        n = n + 1
        first = n / 36
        second = n % 36
        base = 64
        if first > 26:
            first = first - 26
        elif first > 0:
            first = chr(base + first)
        else:
            first = 0
        if second > 26:
            second = second - 26
        elif second > 0:
            second = chr(base + second)
        else:
            second = 0
        print 'newLineage(): lineage created = '+str(first)+str(second)
        return str(first) + str(second)
    except Exception, e:
        print e
        pass
    return
