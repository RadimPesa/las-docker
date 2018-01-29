import hmac
import hashlib
from django.conf import settings
from pyauthticket import AuthTicket
from datetime import datetime
TIMESTAMP_FORMAT = "%a, %d %b %Y %H:%M:%S +0000"
from time import sleep

def getApiKey():
    k = settings.API_SHARED_KEY 
    t = AuthTicket(key=k,message=datetime.utcnow().strftime(TIMESTAMP_FORMAT))
    key=dict()
    key['message']=t.message
    key['timestamp']=t.timestamp
    key['digest']=t.digest

    return key

def checkApiKey(digest,timestamp):
    k = settings.API_SHARED_KEY
    print k
    t1 = AuthTicket(key=k, timestamp=timestamp, digest=digest, message=timestamp,threshold=60*10)

    
    if t1.is_valid():
        print "Ticket was valid."
        return True
    else:
        print "Ticket was not valid."
        return False
    
 
