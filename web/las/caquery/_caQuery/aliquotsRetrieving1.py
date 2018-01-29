#!/usr/bin/python

# Set up the Django Enviroment
import sys
sys.path.append('/srv/www/caquery')
from django.core.management import setup_environ 
import settings 
setup_environ(settings)
#from django.db import transaction
import urllib, urllib2
from _caQuery.models import Button
from django.core.mail import EmailMultiAlternatives
import ast
from _caQuery.views import MiceNode
from _caQuery.genealogyID import *
import pydot
import os

def aliquotsretrieving():
    
    print "ALIQUOTS RETRIEVING STARTED"
    
    for file in os.listdir('/srv/www/caquery/_caQuery/tree_images'):
        os.remove('/srv/www/caquery/_caQuery/tree_images/'+file)


    
    aliquots=[]
    
    values_to_send={'predecessor':"start", 'list': "", 'successor': "Collections", 'parameter': '', 'values':''}
    data = urllib.urlencode(values_to_send)
    button_find=Button.objects.get(name="Mice")
    url=button_find.query_api_url 
    #print url 
    try:
        u = urllib2.urlopen(url, data)
    except:
        print "An error occurred while trying to retrieve data from "+str(url)   
    
    res=u.read()
    result=ast.literal_eval(res)
    
    #print result
    
    casi = []
    
    for i in result['genID']:
        if i[:9]+"00000000000000000" not in casi:
            casi.append(i[:9]+"00000000000000000")
    #casi.append('CRC0096LM00000000000000000')
    #print casi
    
    for c in casi:
        mice_list={}
        
        print "\n"
        print c
        
        values_to_send={'predecessor':"Collections", 'list': "{'genID': ['"+c+"']}", 'successor': "End", 'parameter': '', 'values':''}
        data = urllib.urlencode(values_to_send)
        button_find=Button.objects.get(name="Mice")
        url=button_find.query_api_url  
        try:
            u = urllib2.urlopen(url, data)
        except:
            print "An error occurred while trying to retrieve data from "+str(url)   
        
        res=u.read()
        result=ast.literal_eval(res)
        #d=datetime.datetime.now()
        #print result
                    
        for i in result['objects']:
            gid=i['id_genealogy']
            values_to_send={'predecessor':"Mice", 'list': "{'id': ['"+i['id']+"']}", 'successor': "Aliquots", 'parameter': '', 'values':''}
            data = urllib.urlencode(values_to_send)
            button_find=Button.objects.get(name="Implants")
            url=button_find.query_api_url
            try:
                u = urllib2.urlopen(url, data)
            except:  
                print "An error occurred while trying to retrieve data from "+str(url)
               
            res=u.read()
            result=ast.literal_eval(res)
            #print result
        
            if len(result['genID']):
                if(GenealogyID(result['genID'][0]).getSampleVector()=="X"):
                    father=GenealogyID(result['genID'][0]).zeroOutFieldsAfter('mouse').getGenID()
                else:
                    father=result['genID'][0]
            else:
                gg = GenealogyID(gid)
                p = int(gg.getSamplePassage())
                if p == 1:
                    father = c
                else:
                    father = GenealogyID(gid).setSamplePassage(p-1).clearFieldsAfter('samplePassage').getGenID()

            print "father: "+father
                
            barcode=i['barcode']
            gender=i['gender']
            source=i['id_source']
            strain=i['id_mouse_strain']
            
            rel={}
            mice_list[i['id_genealogy']]=MiceNode(gid=gid, father=father, barcode=barcode, gender=gender, source=source, strain=strain, relatives=rel)
        
        #print "***************"
        #print datetime.datetime.now()-d
        #print "***************"
            
        vuoti=[]
        for x in mice_list:
            present=0
            
            #print mice_list[i].relatives
            #print mice_list[i].gid
            for y in mice_list:
                if mice_list[y].gid == mice_list[x].father:
                    present=1
            if present==0 and GenealogyID(mice_list[x].father).getSampleVector()!="H" and mice_list[x].father != c:
                if mice_list[x].father not in vuoti:
                    vuoti.append(mice_list[x].father)
        #print vuoti
            #print i.gender
            #print i.source
            #print "------------------------"'''
        
        
        for i in vuoti:
            mice_list[i]=MiceNode(gid=i, father=c, barcode="Mouse missing", gender="", source="", strain="", relatives={})
        
        #print mice_list 
    
        gruppi = {}
        for m in mice_list:
            if mice_list[m].father in gruppi.keys():
                gruppi[mice_list[m].father].append(mice_list[m].gid)
            else:
                gruppi[mice_list[m].father]=[]
                gruppi[mice_list[m].father].append(mice_list[m].gid)
        #print gruppi
        
        for g in sorted(gruppi.iterkeys()):
            flag = 0
            for gg in gruppi[g]:
                
                aliquotdnag=gg[:17]+"---D-----"
                values_to_send={'predecessor':"Genealogy ID_", 'list': "{'genID': ['"+aliquotdnag+"']}", 'successor': "Explants", 'parameter': '', 'values':''}
                data = urllib.urlencode(values_to_send)
                button_find=Button.objects.get(name="Aliquots")
                url=button_find.query_api_url  
                try:
                    u = urllib2.urlopen(url, data)
                except:  
                    print "an error occurr in data retrieving: "+str(url)
                   
                res=u.read()
                result=ast.literal_eval(res)
                
                if len(result['genID'])!=0:
                    flag = 1
                    mice_list[gg].relatives["DNA"] = "yes"
                    print "DNA FOUND!"
                    #print result['genID']
            
            #print " "
            if flag == 0:
                chosen = ""
                
                for gg in gruppi[g]:
                    #print "nel gruppo "+g+" non ci sono dna"
                    aliquotrlg=gg[:17]+"---RL----"
                    
                    values_to_send={'predecessor':"Genealogy ID_", 'list': "{'genID': ['"+aliquotrlg+"']}", 'successor': "Explants", 'parameter': 'Exhausted', 'values':'No'}
                    #print values_to_send
                    data = urllib.urlencode(values_to_send)
                    button_find=Button.objects.get(name="Aliquots")
                    url=button_find.query_api_url  
                    try:
                        u = urllib2.urlopen(url, data)
                    except:  
                        print "an error occurr in data retrieving: "+str(url)
                       
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
                        
                        if (chosen=="" or (gg not in gruppi.keys())):
                            present = 0
                            if int(GenealogyID(gg).getSamplePassage())>2:
                                for a in aliquots:
                                    if g == a[:17]+"000000000":
                                        present = 1
                                    try:
                                        if mice_list[g].relatives["DNA"] == "yes":
                                            present = 1
                                    except:
                                        pass                    
                            if present == 0: 
                                chosen = result['genID'][0]
                                #print "chosen"
                                #print chosen
                                #print " "
                        
                if chosen != "":
                    print "@@@@@@@@@@@@@@@@@@@@@@@@@"
                    print chosen
                    print "@@@@@@@@@@@@@@@@@@@@@@@@@"
                
                    aliquots.append(chosen)        
        
        
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
            graph.write_png('/srv/www/caquery/_caQuery/tree_images/'+c+'.png')
            print "Immagine Salvata ------------------"
        except Exception, e:
            print "Graph write png exception"
            print e
               
    mailOperator = []
    from_email = ''
    subject = 'Retrieved Aliquots for DNA Extraction'
    
    text_content = "Red Node = Aliquot Retrieved\nBlue Border = DNA already extracted\nBox Shape = RNAlater aliquots present\n\n"
    for a in aliquots:
        urlimg = ""
        if aliquots.index(a) != 0:
            
            if a[:9] == aliquots[aliquots.index(a)-1][:9]:
                urlimg = ""
            
            else:
                urlimg = ' http://caircc.polito.it/tree_images/'+ a[:9] +'00000000000000000.png'
        else:
            urlimg = ' http://caircc.polito.it/tree_images/'+ a[:9] +'00000000000000000.png'

        text_content = text_content + a + urlimg + '\n'
            

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, mailOperator)
        msg.send()
        print text_content
        print 'MAIL SENT'
    except Exception, e:
        print e
        print 'MDAM: error mail'
    
    return

if __name__=='__main__':
    #print 'main'
    aliquotsretrieving()
