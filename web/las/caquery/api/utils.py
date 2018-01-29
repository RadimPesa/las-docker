#import string
import json
#from pprint import pprint
#from string import maketrans
#from xenopatients import markup
#from django.db import transaction


class Simple:
    def __init__(self, m, select):
        self.attributes={}
        if len(select) == 0:
            for f in m._meta.fields:
                self.attributes[f.name] = str(m.__getattribute__(f.name))
        else:
            for f in m._meta.fields:
                if f.name in select:
                    self.attributes[f.name] = str(m.__getattribute__(f.name))
    def toStr(self):
        output = ''
        a = {}
        for k, v in self.attributes.items():
            a[k] = str(v)
        return json.dumps(a)
    def getAttributes(self):
        return self.attributes
        
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
        
