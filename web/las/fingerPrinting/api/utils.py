import json


class ClassSimple:
    def __init__(self, c, select):
        self.attributes={}
        for f in c._meta.fields:
            if len(select) == 0:
                self.attributes[f.name] = str(c.__getattribute__(f.name))
            elif f.name in select:
                self.attributes[f.name] = str(c.__getattribute__(f.name))

    def toStr(self):
        output = ''
        a = []
        for k, v in self.attributes.items():
#            output += str(k) + ':' + str(v) + ','

            b={k:str(v)}
            a.append(b)
           
        #return output[:len(output)-1]
        print json.dumps(a)
        return json.dumps(a)

    def getAttributes(self):
        return self.attributes