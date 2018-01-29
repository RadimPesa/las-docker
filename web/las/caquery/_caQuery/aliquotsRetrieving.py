#!/usr/bin/python -u

# Set up the Django Enviroment
import sys
sys.path.append('/srv/www/caquery')
from django.core.management import setup_environ 
import settings 
setup_environ(settings)
#from django.db import transaction
import urllib, urllib2
from _caQuery.models import Button
from django.core.mail import EmailMessage
import ast
from _caQuery.views import MiceNode
from _caQuery.genealogyID import *
import pydot
import os
from datetime import datetime
from datetime import timedelta
from math import ceil
from copy import deepcopy

#IMAGES_PATH = '/srv/www/caquery/_caQuery/tree_images/'
IMAGES_PATH = '/srv/www/caquery/_caQuery/img/'

button_url = {}

def sortAliquots(al):
    print "sorting aliquots: "
    print al

    aliq_dict= {}

    al_recent = []
    al_old = []

    lastweek_start = datetime.now() - timedelta(days=6)
    
    for x in al:
        if x[14] == '2': #discard historical aliquots
            continue

        aliq_dict['genID'] = [x]
        
        #if GenealogyID(x).getSampleVector() == 'X':
        #    values_to_send={'predecessor':"Aliquots", 'list': aliq_dict, 'successor': "End", 'parameter': '', 'values':''}
        #    data = urllib.urlencode(values_to_send)
        #    button_find=Button.objects.get(name="Explants")
        #    url=button_find.query_api_url 
        #    try:
        #        u = urllib2.urlopen(url, data)
        #    except:
        #        print "An error occurred while trying to retrieve data from "+str(url)   
        #    res=u.read()
        #    objs=ast.literal_eval(res)['objects']
        #
        #    if datetime.strptime(objs[0]['date'], '%Y-%m-%d') >= lastweek_start:
        #        al_recent.append((al[i], datetime.strptime(objs[0]['date'], '%Y-%m-%d')))
        #    else:
        #        al_old.append((al[i], datetime.strptime(objs[0]['date'], '%Y-%m-%d')))

        #elif GenealogyID(x).getSampleVector() == 'H':
        
        #get aliquot data
        values_to_send={'predecessor':"Start", 'list': aliq_dict, 'successor': "End", 'parameter': '', 'values':''}
        data = urllib.urlencode(values_to_send)
        url=button_url["Aliquots"]
        try:
            u = urllib2.urlopen(url, data)
        except:
            print "An error occurred while trying to retrieve data from "+str(url)   
        res=u.read()
        objs=ast.literal_eval(res)['objects']

        #get derivation info
        values_to_send={'predecessor':"Aliquots", 'list': {'id': [objs[0]['id']]}, 'successor': "End", 'parameter': '', 'values':''}
        data = urllib.urlencode(values_to_send)
        url=button_url["Transform. Events"]
        try:
            u = urllib2.urlopen(url, data)
        except:
            print "An error occurred while trying to retrieve data from "+str(url)   
        res=u.read()
        objs1=ast.literal_eval(res)['objects']

        if len(objs1) > 0:
            if 'aliquotExhausted' in objs1[0] and objs1[0]['aliquotExhausted'] == 'True':
                print "%s: aliquot exhausted, skipping" % x 
                continue
            elif 'failed' in objs1[0] and objs1[0]['failed'] == 'False':
                print "%s: aliquot already derived successfully, skipping" % x
                continue

        #sampling date
        sdate = datetime.strptime(objs[0]['Sampling Date'], '%Y-%m-%d')
        #archival date
        adate = datetime.strptime(objs[0]['archiveDate'], '%Y-%m-%d') if objs[0]['archiveDate'] != 'None' else datetime.strptime("1986-03-11", "%Y-%m-%d") 
        if sdate >= lastweek_start:
            al_recent.append((x, sdate, adate))
        else:
            al_old.append((x, sdate, adate))

    al_recent.sort(lambda x,y: (y[1] - x[1]).days)
    al_old.sort(lambda x,y: (y[2] - x[2]).days)

    al_recent = [x[0] for x in al_recent]
    al_old = [x[0] for x in al_old]

    return al_recent, al_old

def find_mice_to_exclude():
    # topi da escludere perche' parte di un treatment protocol
    # inizio topi_da_escludere

    # recupero protocolli
    values_to_send={'predecessor':"start", 'list': "", 'successor': "Mice", 'parameter': '', 'values':''}
    data = urllib.urlencode(values_to_send)
    url=button_url["Treatment Protocols"] 
    try:
        u = urllib2.urlopen(url, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url)   
    res=u.read()
    prot=ast.literal_eval(res)
    
    # recupero topi presenti nei bracci di quei protocolli
    values_to_send={'predecessor':"Treatment Protocols", 'list': prot, 'successor': "Aliquots", 'parameter': '', 'values':''}
    data = urllib.urlencode(values_to_send)
    url=button_url["Mice"]
    try:
        u = urllib2.urlopen(url, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url)   
    res=u.read()
    return ast.literal_eval(res)['genID']

def get_cases():
    values_to_send={'predecessor':"start", 'list': "", 'successor': "Collections", 'parameter': '', 'values':''}
    data = urllib.urlencode(values_to_send)
    url=button_url["Mice"]
    #print url 
    try:
        u = urllib2.urlopen(url, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url)   
    
    res=u.read()
    result=ast.literal_eval(res)
    
    #print result
   
    return list(set([i[:9]+"00000000000000000" for i in result['genID']]))

def get_mice_in_case(c):
    values_to_send={'predecessor':"Collections", 'list': "{'genID': ['"+c+"']}", 'successor': "End", 'parameter': '', 'values':''}
    data = urllib.urlencode(values_to_send)
    url=button_url["Mice"]
    try:
        u = urllib2.urlopen(url, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url)   
    
    res=u.read()
    result=ast.literal_eval(res)
    return result['objects']

def get_aliquot_implanted_in_mice(m_id):
    values_to_send={'predecessor':"Mice", 'list': "{'id': ['"+m_id+"']}", 'successor': "Aliquots", 'parameter': '', 'values':''}
    data = urllib.urlencode(values_to_send)
    url=button_url["Implants"]
    try:
        u = urllib2.urlopen(url, data)
    except:  
        print "An error occurred while trying to retrieve data from "+str(url)
       
    res=u.read()
    res=ast.literal_eval(res)
    return res['genID'][0] if len(res['genID']) else None

def get_mouse_from_explanted_aliquot(a_genid):
    values_to_send={'predecessor': 'Aliquots', 'list': "{'genID': ['"+a_genid+"']}",'parameter': '', 'values': '', 'successor': 'Mice'}
    data = urllib.urlencode(values_to_send)
    url=button_url["Explants"]
    try:
        u = urllib2.urlopen(url, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url)

    res=u.read()
    result=ast.literal_eval(res)
    
    if 'id' in result.keys() and len(result['id']) > 0:
        # get the mouse involved in the explant
        values_to_send={'predecessor': 'Explants', 'list': "{'id': ["+str(result['id'][0])+"]}", 'parameter': '', 'values': '', 'successor': 'Aliquots'}
        data = urllib.urlencode(values_to_send)
        url=button_url["Mice"]
        try:
            u = urllib2.urlopen(url, data)
        except:
            print "An error occurred while trying to retrieve data from "+str(url)   

        res=u.read()
        result=ast.literal_eval(res)

        if 'genID' in result.keys() and len(result['genID'])>0:
            return result['genID'][0]
        else:
            return None
    else:
        return None

def parent_mouse(n):
    if n < 0:
        return None
    elif n < 13:
        return int(ceil(float(n)/4))
    else:
        return 5


def aliquotsretrieving():
    
    print "ALIQUOTS RETRIEVING STARTED"
    
    for file in os.listdir(IMAGES_PATH):
        os.remove(IMAGES_PATH+file)

    mice_to_exclude = set(find_mice_to_exclude())
    print "mice to exclude = ", len(mice_to_exclude)    
    # fine topi_da_escludere

    # RL aliquots chosen for derivation
    aliquots=set()
    critical_VT_aliquots = set()   # non-historical aliquots (i.e., non-'99') aliquots whose father can't be found
    critical_mice = set()          # mice whose implanted VT aliquot can't be found
    critical_mice_1 = set()        # passage-1 mice that need DNA but have no RL available
    critical_cases = set()         # original (human) cases that need DNA but have no RL available
    critical_groups = []        # passage-2 or higher groups of mice that need DNA but have no RL available
    
    
    #for i in result['genID']:
    #    if i[:9]+"00000000000000000" not in casi:
    #        casi.append(i[:9]+"00000000000000000")
    
    #casi.append('CRC0096LM00000000000000000')
    #print casi
    #casi = casi[-80:-30]

    #import pdb
    #pdb.set_trace()

    #casi = ['HNC0039PR00000000000000000']
    casi = get_cases()

    for c in casi:
        mice_list={}
        
        print "\n"
        print c
        
        #d=datetime.datetime.now()
        #print result
        result = get_mice_in_case(c)
                    
        for i in result:
            gid=i['id_genealogy']
            #print result

            print "id topo: " + i['id_genealogy']
            res = get_aliquot_implanted_in_mice(i['id'])
            if res:
                g = GenealogyID(res)
                if g.getSampleVector()=="X":
                    print "parent: esiste A - xeno"
                    #father=GenealogyID(res[0]).zeroOutFieldsAfter('mouse').getGenID()
                    father = get_mouse_from_explanted_aliquot(res)
                    if not father:
                        if g.getAliquotExtraction() != '99':
                            critical_VT_aliquots.add(res)
                        father = g.setImplantSite("SCR").zeroOutFieldsAfter('implantSite').getGenID()
                else:
                    print "parent: esiste A - human"                    
                    father=GenealogyID(res).zeroOutFieldsAfter('sampleVector').getGenID()
            else:
                print "error: implanted VT aliquot not found for mouse %s" % gid
                critical_mice.add(gid)
                # recupero storico
                gg = GenealogyID(gid)
                p = int(gg.getSamplePassage())
                if p == 1:
                    father = c
                else:
                    mouse_no = int(gg.getMouse())
                    delta = 200 if mouse_no > 200 else 0
                    parent_no = parent_mouse(mouse_no - delta)
                    father = gg.setSamplePassage(p-1).setMouse(parent_no + delta).zeroOutFieldsAfter('implantSite').getGenID()

            print "father: ",father
                
            #barcode=i['barcode']
            #gender=i['gender']
            #source=i['id_source']
            #strain=i['id_mouse_strain']
            
            rel={}
            mice_list[i['id_genealogy']]=MiceNode(gid=gid, father=father, barcode="", gender="", source="", strain="", relatives=rel)
        
        #print "***************"
        #print datetime.datetime.now()-d
        #print "***************"
            
        vuoti=[]
        missing_fathers = [v.father for v in mice_list.values() if v.father not in mice_list]

        for f in missing_fathers:
            #print mice_list[i].relatives
            #print mice_list[i].gid
            if GenealogyID(f).getSampleVector()!="H" and f != c and f not in mice_list:
                print "warning: non-existent parent %s" % f
                g = GenealogyID(f)
                p = int(g.getSamplePassage())
                if p == 1:
                    ff = c
                else:
                    mouse_no = int(g.getMouse())
                    delta = 200 if mouse_no > 200 else 0
                    parent_no = parent_mouse(mouse_no - delta)
                    ff = g.setSamplePassage(p-1).setMouse(parent_no + delta).zeroOutFieldsAfter('implantSite').getGenID()
                mice_list[f]=MiceNode(gid=f, father=ff, barcode="Mouse missing", gender="", source="", strain="", relatives={})
                missing_fathers.append(ff)


                
            #    if GenealogyID(mice_list[x].father).getSampleVector()!="H" and mice_list[x].father != c and mice_list[x].father not in vuoti:
            #            vuoti.append(mice_list[x].father)
        #print vuoti
            #print i.gender
            #print i.source
            #print "------------------------"'''
        
        
        #for i in vuoti:
        #    mice_list[i]=MiceNode(gid=i, father=c, barcode="Mouse missing", gender="", source="", strain="", relatives={})
        
        #print mice_list 
    
        gruppi = {}
        for m in mice_list:
            if mice_list[m].father not in gruppi:
                gruppi[mice_list[m].father]=[]
            gruppi[mice_list[m].father].append(mice_list[m].gid)
        #print gruppi

        
        for g in sorted(gruppi.iterkeys()):
            flag = 0
            # per ciascun topo nel gruppo, cerco se esiste una aliquota estratta di DNA
            # se esiste per almeno un topo del gruppo, flag e' settato a 1
            
            #se il gruppo e' di passaggio 1, verifica che sia il padre (aliquota H) sia tutti i topi nel gruppo abbiano aliquota D
            if int(GenealogyID(gruppi[g][0]).getSamplePassage()) == 1:

                print "---passage 1"
                
                print "      ensure father has DNA: " + g
                #aliquota dna del padre
                aliquotdnafather = g[:10] + "----------D-----"
                values_to_send={'predecessor':"Genealogy ID_", 'list': "{'genID': ['"+aliquotdnafather+"']}", 'successor': "Explants", 'parameter': '', 'values':''}
                data = urllib.urlencode(values_to_send)
                url=button_url["Aliquots"]
                try:
                    u = urllib2.urlopen(url, data)
                except:  
                    print "an error occurr in data retrieving: "+str(url)
                   
                res=u.read()
                result=ast.literal_eval(res)

                if len(result['genID']) == 0:
                    print "      father has no DNA"
                    #no dna
                    #cerco RL
                    aliquotrlfather = g[:10] + "----------RL----"

                    values_to_send={'predecessor':"Genealogy ID_", 'list': "{'genID': ['"+aliquotrlfather+"']}", 'successor': "Explants", 'parameter': 'Exhausted', 'values':'No'}
                    #print values_to_send
                    data = urllib.urlencode(values_to_send)
                    url=button_url["Aliquots"]  
                    try:
                        u = urllib2.urlopen(url, data)
                    except:  
                        print "an error occurr in data retrieving: "+str(url)
                       
                    res=u.read()
                    result=ast.literal_eval(res)
                    #print "---rnalater"
                    #print result
                    if len(result['genID'])!=0:
                        aliquots.add(result['genID'][0])
                        #mice_list[g].relatives['scheduled'] = True
                        print "@@@@@@@@@@@@@@@@@@@@@@@@@"
                        print result['genID'][0]
                        print "@@@@@@@@@@@@@@@@@@@@@@@@@"
                    else:
                        print "no RL available for " + g
                        critical_cases.add(g)
                else:
                    print "      father has DNA"


                print "      ensure all children have DNA"
                #aliquote dna di tutti i figli
                for gg in gruppi[g]:
                    aliquotdnag=gg[:17]+"---D-----"
                    values_to_send={'predecessor':"Genealogy ID_", 'list': "{'genID': ['"+aliquotdnag+"']}", 'successor': "Explants", 'parameter': '', 'values':''}
                    data = urllib.urlencode(values_to_send)
                    url=button_url["Aliquots"]
                    try:
                        u = urllib2.urlopen(url, data)
                    except:  
                        print "an error occurr in data retrieving: "+str(url)
                   
                    res=u.read()
                    result=ast.literal_eval(res)
                
                    if len(result['genID'])!=0:
                        #DNA found for current mouse
                        if  mice_list[gg].relatives == []:
                            mice_list[gg].relatives = {}
                        mice_list[gg].relatives["DNA"] = "yes"
                    else:
                        #skip mouse if under treatment
                        if gg in mice_to_exclude:
                            continue

                        #DNA not found for current mouse
                        #find RL
                        aliquotrlg=gg[:17]+"---RL----"
                        values_to_send={'predecessor':"Genealogy ID_", 'list': "{'genID': ['"+aliquotrlg+"']}", 'successor': "Explants", 'parameter': 'Exhausted', 'values':'No'}
                        data = urllib.urlencode(values_to_send)
                        url=button_url["Aliquots"]
                        try:
                            u = urllib2.urlopen(url, data)
                        except:  
                            print "an error occurr in data retrieving: "+str(url)
                           
                        res=u.read()
                        result=ast.literal_eval(res)
                        if len(result['genID'])!=0:
                            aliquots.add(result['genID'][0])
                            mice_list[gg].relatives['scheduled'] = True
                            print "@@@@@@@@@@@@@@@@@@@@@@@@@"
                            print result['genID'][0]
                            print "@@@@@@@@@@@@@@@@@@@@@@@@@"
                        else:
                            print "no RL available for mouse " + gg
                            critical_mice_1.add(gg)


            else:

                for gg in gruppi[g]:

                    aliquotdnag=gg[:17]+"---D-----"
                    values_to_send={'predecessor':"Genealogy ID_", 'list': "{'genID': ['"+aliquotdnag+"']}", 'successor': "Explants", 'parameter': '', 'values':''}
                    data = urllib.urlencode(values_to_send)
                    url=button_url["Aliquots"]
                    try:
                        u = urllib2.urlopen(url, data)
                    except:  
                        print "an error occurr in data retrieving: "+str(url)
                       
                    res=u.read()
                    result=ast.literal_eval(res)
                    
                    if len(result['genID'])!=0:
                        flag = 1
                        if  mice_list[gg].relatives == []:
                            mice_list[gg].relatives = {}
                        mice_list[gg].relatives["DNA"] = "yes"
                        print "DNA FOUND!"
                        #print result['genID']
                
                #print " "
                if flag == 0:
                    #no DNA available in current group

                    #sort gruppi[g] so that leaves appear first
                    tmp = []
                    for x in gruppi[g]:
                        if x in gruppi:
                            tmp.append(x)
                        else:
                            tmp.insert(0, x)
                    gruppi[g] = tmp

                    chosen = ""
                    
                    if ("DNA" in mice_list[g].relatives and mice_list[g].relatives["DNA"] == "yes") or ("scheduled" in mice_list[g].relatives):
                        father_has_dna_or_has_been_scheduled = True
                    else:
                        father_has_dna_or_has_been_scheduled = False

                    for gg in gruppi[g]:
                        if gg in mice_to_exclude:
                            continue;
                        #print "nel gruppo "+g+" non ci sono dna"
                        aliquotrlg=gg[:17]+"---RL----"
                        
                        values_to_send={'predecessor':"Genealogy ID_", 'list': "{'genID': ['"+aliquotrlg+"']}", 'successor': "Explants", 'parameter': 'Exhausted', 'values':'No'}
                        #print values_to_send
                        data = urllib.urlencode(values_to_send)
                        url=button_url["Aliquots"]
                        try:
                            u = urllib2.urlopen(url, data)
                        except:  
                            print "an error occurred in data retrieving: "+str(url)
                           
                        res=u.read()
                        result=ast.literal_eval(res)
                        #print "---rnalater"
                        #print result
                        if len(result['genID'])!=0:
                            #print "RNAlater presente"  
                            #print mice_list[gg].relatives
                            if  mice_list[gg].relatives == []:
                                mice_list[gg].relatives = {}
                            mice_list[gg].relatives["RNAlater"] = "yes"
                            
                            if (chosen==""):
                                present = 0
                                #if passage > 2 choose only if parent has no DNA
                                if int(GenealogyID(gg).getSamplePassage())>2:
                                        #if father has DNA or has been scheduled for derivation
                                        if father_has_dna_or_has_been_scheduled == True:
                                            present = 1
                                # N.B. for passage == 2, a mouse is always chosen
                                if present == 0: 
                                    chosen = result['genID'][0]
                                    print "@@@@@@@@@@@@@@@@@@@@@@@@@"
                                    print chosen
                                    print "@@@@@@@@@@@@@@@@@@@@@@@@@"
                                    aliquots.add(chosen)
                                    mice_list[gg].relatives['scheduled'] = True

                    if chosen=="" and (int(GenealogyID(gg).getSamplePassage())==2 or father_has_dna_or_has_been_scheduled == False):
                        print "Error: no RL aliquot could be selected for group with parent " + g
                        critical_groups.append(gruppi[g])
                            
                        
            
        
        graph = pydot.Dot(graph_type='graph', rankdir="RL")
            
            #n = pydot.Node(name = c)
            #graph.add_node(n)
        
        flagtaken = 0
        
        for m in mice_list:
            color = ""
            shape = ""
            try:
                if mice_list[m].relatives["DNA"] == "yes":
                    color = "blue"
            except:
                pass
            try:
                if mice_list[m].relatives["RNAlater"] == "yes":
                    shape = "box"
            except:
                pass
            
            for a in aliquots:
                if mice_list[m].gid == a[:17]+"000000000":               
            
                    node = pydot.Node(name = mice_list[m].gid[10:17], style="filled", fillcolor="#D00000", color = color, shape = shape)
                    graph.add_node(node)
                    flagtaken = 1
                    #print "Nodo Rosso -------------------------"
                else:
                    n = pydot.Node(name = mice_list[m].gid[10:17], color = color, shape = shape)
                    graph.add_node(n)
                       
        for m in mice_list:
            node = mice_list[m].gid[10:17]
            
            if mice_list[m].father == c or GenealogyID(mice_list[m].father).getSampleVector()=="H":
                father = mice_list[m].father
                    
            else:
                father = mice_list[m].father[10:17]
            
            edge = pydot.Edge(node, father)
            graph.add_edge(edge)
         
        if flagtaken == 1:                    
            try:
                graph.write_png(IMAGES_PATH+c+'.png')
                print "Immagine Salvata ------------------"
            except Exception, e:
                print "Graph write png exception"
                print e
                   
    
    al_recent, al_old = sortAliquots(aliquots)

    mailOperator = []
    from_email = ''
    subject = 'Retrieved Aliquots for DNA Extraction'
    
    text_content = "Red Node = Aliquot selected for extraction\nBlue Border = DNA already extracted\nBox Shape = RNAlater aliquots present\n\n"
    text_content = text_content + "Recent aliquots (" + (datetime.now() - timedelta(days=6)).strftime("%a, %d %b %Y") + " - " + datetime.now().strftime("%a, %d %b %Y") + "): " + str(len(al_recent)) +"\n"
    
    for a in al_recent:
        #urlimg = ""
        #if aliquots.index(a) != 0:
        #    
        #    if a[:9] == aliquots[aliquots.index(a)-1][:9]:
        #        urlimg = ""
        #    
        #    else:
        #        urlimg = ' http://devircc.polito.it/tree_images/'+ a[:9] +'00000000000000000.png'
        #else:
        #    urlimg = ' http://devircc.polito.it/tree_images/'+ a[:9] +'00000000000000000.png'
        urlimg = ''+ a[:9] +'00000000000000000.png'

        text_content = text_content + a + urlimg + '\n'

    text_content = text_content + "\nOlder aliquots: " + str(len(al_old)) + "\n"

    for a in al_old:
        urlimg = ''+ a[:9] +'00000000000000000.png'        
        text_content = text_content + a + urlimg + '\n'            

    try:
        e = EmailMessage(subject=subject, body=text_content, from_email=from_email, to=mailOperator)
        e.attach(filename="Recent_aliquots.las", mimetype = "text/plain", content = '\n'.join(al_recent))
        e.attach(filename="Old_aliquots.las", mimetype = "text/plain", content = '\n'.join(al_old))
        e.send()
        print text_content
        print 'MAIL SENT'
    except Exception, e:
        print e
        print 'MDAM: error sending mail'

    try:
        body = ""
        body += "Critical VT aliquots (non-historical aliquots (i.e., non-'99') aliquots whose father can't be found): %d\n" % len(critical_VT_aliquots)
        body += "\n".join(critical_VT_aliquots)
        body += "\n\n"
        body += "Critical mice 1 (mice whose implanted VT aliquot can't be found): %d\n" % len(critical_mice)
        body += "\n".join(critical_mice)
        body += "\n\n"
        body += "Critical mice 2 (passage-1 mice that require DNA extraction but have no RL available): %d\n" % len(critical_mice_1)
        body += "\n".join(critical_mice_1)
        body += "\n\n"
        body += "Critical cases (original (human) cases hat require DNA extraction but have no RL available): %d\n" % len(critical_cases)
        body += "\n".join(critical_cases)
        body += "\n\n"
        body += "Critical groups (passage-2 or higher groups of mice that require DNA extraction but have no RL available): %d\n" % len(critical_groups)
        for i,x in enumerate(critical_groups):
            body += "(%d) %s\n" % (i+1, ", ".join(x))

        mailOperatorCriticalCases = []
        
        e = EmailMessage(subject="Critical cases", body=body, from_email=from_email, to=mailOperatorCriticalCases)
        e.send()
        print text_content
        print 'MAIL SENT'
    except Exception, e:
        print e
        print 'MDAM: error sending mail'
    
    return

if __name__=='__main__':
    #print 'main'
    button_url['Aliquots'] = Button.objects.get(name="Aliquots").query_api_url
    button_url['Transform. Events'] = Button.objects.get(name="Transform. Events").query_api_url
    button_url['Treatment Protocols'] = Button.objects.get(name="Treatment Protocols").query_api_url
    button_url['Mice'] = Button.objects.get(name="Mice").query_api_url
    button_url['Implants'] = Button.objects.get(name="Implants").query_api_url
    button_url['Explants'] = Button.objects.get(name="Explants").query_api_url

    aliquotsretrieving()
