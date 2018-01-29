import urllib, urllib2, json
from django.conf import settings

class LASEmail ():
    def __init__ (self,wg=[], functionality='', wgString = '', DOMAIN_URL=None):
        self.mailDict = {}
        
        self.addWg(wg)
        self.functionality = functionality
        self.wgString = wgString
        if DOMAIN_URL:
            self.DOMAIN_URL = DOMAIN_URL
        else:
            try:
                from django.conf import settings
                self.DOMAIN_URL = settings.DOMAIN_URL
            except ImportError:
                self.DOMAIN_URL = 'https://dom87.polito.it'

    def setFunctionality(self, funct):
        self.functionality = funct

    def setWgString(self, wg):
        self.wgString = wg

    def addWg(self, wg):
        for w in wg:
            if not self.mailDict.has_key(w):
                self.mailDict[w] = {'Executor':[], 'Recipient':[], 'Assignee':[], 'Planner':[], 'msg':{'default':[],'subject':''}}

    def addRoleEmail(self, wg, role, users):
        for w in wg:
            if self.mailDict.has_key(w):
                if self.mailDict[w].has_key(role):
                    self.mailDict[w][role].extend(users)
                    self.mailDict[w][role] = list(set(self.mailDict[w][role]))
                else:
                    raise Exception('Role error')
            else:
                self.addWg([w])
                self.addRoleEmail([w], role, users)

   
    def addMsg(self, wg, msg, fileName=None):
        for w in wg:
            if self.mailDict.has_key(w):
                if fileName is not None:
                    if fileName not in self.mailDict[w]['msg']:
                        self.mailDict[w]['msg'][fileName]=list()
                    self.mailDict[w]['msg'][fileName].extend(msg)
                else:
                    #if 'default' not in self.mailDict[w]['msg']:
                    #    self.mailDict[w]['msg']['default']=list()
                    self.mailDict[w]['msg']['default'].extend(msg)
            else:
                self.addWg([w])
                self.addMsg([w], msg, fileName)

    def appendSubject(self,wg,subject):
        for w in wg:
            if self.mailDict.has_key(w):
                self.mailDict[w]['msg']['subject']=self.mailDict[w]['msg']['subject']+subject
            else:
                self.addWg([w])
                self.appendSubject([w], subject)

    def send(self):
        if settings.USE_GRAPH_DB==True:
            mail={'mailDict':json.dumps(self.mailDict),'functionality':self.functionality}
            data = urllib.urlencode(mail)
            req = urllib2.Request(self.DOMAIN_URL+'/las/sendLASMail/',data=data, headers={"workingGroups" : self.wgString})
            u = urllib2.urlopen(req)
            res1 =  json.loads(u.read())
            print 'res',res1
            if res1['message']!='ok':
                raise Exception('Error in sending email')
