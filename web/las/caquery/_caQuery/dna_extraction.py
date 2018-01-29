#!/usr/bin/python -u

from py2neo import *

import sys
sys.path.append('/srv/www/caquery')
from django.core.management import setup_environ 
import settings 
setup_environ(settings)

import urllib, urllib2
import ast
import json
from django.core.mail import EmailMessage
from datetime import datetime
from datetime import timedelta
from termcolor import cprint

from _caQuery.models import Button
from _caQuery.genealogyID import *

gdb = neo4j.GraphDatabaseService(settings.NEO4J_URL)
dna_query = neo4j.CypherQuery(gdb, "start n=node({ node_id }) match (n)-[:hasChild]->(rl {archived_material:'RL'})-[:hasChild]->(a {archived_material:'D'}) return id(a), a.genid")
rl_query = neo4j.CypherQuery(gdb, "start n=node({ node_id }) match (n)-[:hasChild]->(a {archived_material:'RL'}) return id(a), a.genid order by a.genid")
mouse_query = neo4j.CypherQuery(gdb, "start n=node({ node_id }) match (n)-[:hasChild]->(a {archived_material:'VT'})-[:hasChild]->(m {entity:'X'}) return id(m), m.genid")
sorted_mouse_query = neo4j.CypherQuery(gdb, "start n=node({ node_id }) match (n)-[:hasChild]->(a {archived_material:'VT'})-[:hasChild]->(m {entity:'X'}) optional match (m)-[:hasChild]->(aa {archived_material:'VT'})-[hasChild]->(mm {entity:'X'}) return id(m), m.genid, count(mm) as CC order by CC, m.genid")

button_url = {}
button_url['Aliquots'] = Button.objects.get(name="Aliquots").query_api_url
button_url['Treatment Protocols'] = Button.objects.get(name="Treatment Protocols").query_api_url
button_url['Mice'] = Button.objects.get(name="Mice").query_api_url
button_url['Transform. Events'] = Button.objects.get(name="Transform. Events").query_api_url
days_recent = 7

rl_aliquots = set()
no_rl = set()
mice_to_exclude = set()

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

def sortAliquots(al):
    print "Sorting aliquots by date..."

    aliq_dict= {}

    al_recent = []
    al_old = []

    lastweek_start = datetime.now() - timedelta(days=days_recent)
    
    for x in al:
        if x[14] == '2': #discard historical aliquots
            print x, ": discarding historical aliquot"
            continue

        aliq_dict['genID'] = [x]
        
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
        if len(objs) == 0:
        	print "Error finding aliquot %s" % x
        	continue

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
            skip = False
            for y in objs1:
                if 'derivationExecuted' in y and y['derivationExecuted'] == 'False':
                    print "%s : aliquot currently under derivation, skipping" % x 
                    skip = True
                    break
                elif 'failed' in objs1[0] and objs1[0]['failed'] == 'False':
                    print "%s : aliquot already derived successfully, skipping" % x
                    skip = True
                    break
                elif 'aliquotExhausted' in objs1[0] and objs1[0]['aliquotExhausted'] == 'True':
                    print "%s : aliquot exhausted, skipping" % x 
                    skip = True
                    break
            if skip:
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

def check_dna(id, genid):
	if genid in mice_to_exclude:
		return False
	res = dna_query.execute(node_id=id)
	return len(res) > 0

def get_RL(id, genid):
	if genid in mice_to_exclude:
		return []
	res = rl_query.execute(node_id=id)
	if len(res) > 0:
		res = [x[1] for x in res.data]
	else:
		return []

	# check aliquot availability (i.e., {'Exhausted': 'No'}) in BioBank
	values_to_send={'predecessor':'Genealogy ID_', 'list': '{"genID":'+json.dumps(res)+'}', 'successor': 'Explants', 'parameter': 'Exhausted', 'values':'No'}
	data = urllib.urlencode(values_to_send)
	url = button_url["Aliquots"]
	try:
		u = urllib2.urlopen(url, data)
	except:  
		print "an error occurr in data retrieving: "+str(url)
	res = u.read()
	return ast.literal_eval(res)['genID']

def visit_subtree(parent_id, parent_gid, parent_has_dna, passage):
	print "[P%d] parent: %s, has_DNA: %s" % (passage, parent_gid, parent_has_dna)
	children = sorted_mouse_query.execute(node_id=parent_id)
	children = [[x[0], x[1], x[2], False] for x in children]
	if parent_has_dna == True:
		print "     skip passage"
		for m in children:
			m[3] = check_dna(m[0], m[1])
	else:
		dna = False
		chosen = None
		for m in children:
			m[3] = check_dna(m[0], m[1])
			if m[3]:
				dna = True
				chosen = m[1]
		if not dna:
			for m in children:
				rl = get_RL(m[0], m[1])
				if len(rl) > 0:
					## add logic here to check RL availability (!= existence)
					rl_aliquots.add(rl[0])
					chosen = rl[0]
					m[3] = True
					break
		if not chosen:
			print "     no RL available for group"
			no_rl.add(parent_gid)
		else:
			if not dna:
				cprint("     chosen: %s" % chosen, 'green')
			else:
				print "     %s has DNA" % chosen
	for m in children:
		c_id = m[0]
		c_gid = m[1]
		c_num_children = m[2]
		has_dna = m[3]
		if c_num_children > 0:
			visit_subtree(c_id, c_gid, has_dna, passage+1)

def check_case(case_id, case_gid):
	# human aliquots
	print "[P0]"
	if not check_dna(case_id, case_gid):
		rl = get_RL(case_id, case_gid)
		if len(rl) > 0:
			rl_aliquots.add(rl[0])
			cprint("     chosen: %s" % rl[0], "green")
		else:
			print "     %s has no DNA or RL" % case_gid
			no_rl.add(case_gid)
	else:
		print "     %s has DNA" % case_gid
	
	# passage-1 mice
	mice1 = sorted_mouse_query.execute(node_id=case_id)
	if len(mice1) == 0:
		return
	print "[P1]"
	for m in mice1:
		mouse_id = m[0]
		mouse_gid = m[1]
		if not check_dna(mouse_id, mouse_gid):
			rl = get_RL(mouse_id, mouse_gid)
			if len(rl) > 0:
				rl_aliquots.add(rl[0])
				cprint("     chosen: %s" % rl[0], "green")
			else:
				print "     %s has no DNA or RL" % mouse_gid
				no_rl.add(mouse_gid)
		else:
			print "     %s has DNA" % mouse_gid

	# passage-2 mice
	# call recursive visit by setting parent_has_dna to False
	# so that a passage-2 mouse is always chosen
	for m in mice1:
		mouse_id = m[0]
		mouse_gid = m[1]
		c_num_children = m[2]
		if c_num_children > 0:
			visit_subtree(mouse_id, mouse_gid, False, 2)

def dna_extraction():
    q = "start c=node(*) match (c)-[:hasChild]->(cc) where c.entity ='C' and cc.entity='C' return id(cc), cc.genid"
    print "Retrieving mice to exclude from aliquot extraction..."
    mice_to_exclude = set(find_mice_to_exclude())
    print "Retrieving cases..."
    cq = neo4j.CypherQuery(gdb,q)
    cases = cq.execute()
    print len(cases), " case(s) found"

    for c in cases:
        case_id = c[0]
        case_gid = c[1]
        gid = GenealogyID(case_gid)
        if gid.getOrigin() == 'CRC' and int(gid.getCaseCode()) <= 430:
            continue
        print "===[ Case %s ]====================" % case_gid
        check_case(case_id, case_gid)
        print ""

    print ""
    print "Aliquots for extraction (%d):" % len(rl_aliquots)
    rl = sorted(rl_aliquots)
    al_recent, al_old = sortAliquots(rl_aliquots)

    recipients = []
    sender = ''
    subject = 'Aliquots for DNA Extraction'
    
    text_content = ""
    #text_content = "Red Node = Aliquot selected for extraction\nBlue Border = DNA already extracted\nBox Shape = RNAlater aliquots present\n\n"
    text_content = text_content + "Recent aliquots (" + (datetime.now() - timedelta(days=days_recent)).strftime("%a, %d %b %Y") + " - " + datetime.now().strftime("%a, %d %b %Y") + "): " + str(len(al_recent)) +"\n"
    
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
        #urlimg = ' http://lasircc.polito.it/tree_images/'+ a[:9] +'00000000000000000.png'

        #text_content = text_content + a + urlimg + '\n'
        text_content = text_content + a + '\n'

    text_content = text_content + "\nOlder aliquots: " + str(len(al_old)) + "\n"

    for a in al_old:
        #urlimg = ' http://lasircc.polito.it/tree_images/'+ a[:9] +'00000000000000000.png'        
        #text_content = text_content + a + urlimg + '\n'            
        text_content = text_content + a + '\n'            

    print ""
    print "Sending email"
    print "Recipients: ", ", ".join(recipients)
    print "Content:"
    cprint(text_content, 'cyan')

    try:
        e = EmailMessage(subject=subject, body=text_content, from_email=sender, to=recipients)
        e.attach(filename="Recent_aliquots.las", mimetype = "text/plain", content = '\n'.join(al_recent))
        e.attach(filename="Old_aliquots.las", mimetype = "text/plain", content = '\n'.join(al_old))
        e.send()
        print
        print 'Email sent'
    except Exception, e:
        print e
        cprint('Error sending email', 'red')






if __name__=='__main__':
    dna_extraction()
