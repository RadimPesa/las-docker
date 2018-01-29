from __init__ import *

def getMdamTemplates (templateList):
    mdamUrl = Urls.objects.get(id_webservice=WebService.objects.get(name='mdam').id, available=True)
    url = mdamUrl.url + "api/describetemplate/"
    templates = []
    for t in templateList:
        data = urllib.urlencode({'template_id':t})
        req = urllib2.Request(url + "?" + data, headers={"workingGroups" : get_WG_string()})
        u = urllib2.urlopen(req)
        res=u.read()
        res=ast.literal_eval(res)
        templates.append(res)
    return templates