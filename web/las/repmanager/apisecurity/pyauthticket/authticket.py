# Copyright (c) 2008 JJ Geewax http://geewax.org/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""
This is the main module that holds the AuthTicket class. This class is 
where all the work is done.
"""

import hmac, sha
from datetime import datetime

TIMESTAMP_FORMAT = "%a, %d %b %Y %H:%M:%S +0000"
TIMESTAMP_THRESHOLD = 60 * 20 # 20 minutes
DIGEST = sha

__all__ = ['AuthTicket']

class AuthTicket(object):
    """
    This is the main ticket object. Create a ticket with a key only to
    get started.
    """
    def __init__(self, key, message=None, threshold=None, timestamp=None, digest=None):
        """
        Create a new AuthTicket object.
        
        If digest is None, this method will generate a digest based on the 
        provided options. 
        """
        super(AuthTicket, self).__init__()
        
        self.key = key
        self.message = message or ''
        self.threshold = threshold or TIMESTAMP_THRESHOLD
        self.timestamp = timestamp
        self.digest = digest or self.get_digest()
    
    @classmethod
    def current_timestamp(cls):
        """
        Gets the current time in UTC time with the specified format.
        """
        return datetime.utcnow().strftime(TIMESTAMP_FORMAT)
    
    def timestamp_meets_threshold(self):
        """
        Checks whether a timestamp is within `threshold` seconds of now.
        
        Expects the timestamp to be in UTC time.
        """
        if not self.threshold:
            return False
        if not self.timestamp:
            self.timestamp = self.current_timestamp()
        
        timestamp = datetime.strptime(self.timestamp, TIMESTAMP_FORMAT)

        return not abs((datetime.utcnow()-timestamp)).seconds > self.threshold
    
    def get_digest(self):
        """
        Using `self.timestamp`, generate the HMAC digest.
        """
        if not self.timestamp:
            self.timestamp = self.current_timestamp()
            
        return hmac.new(
            key = self.key,
            msg = "%s\n%s" % (self.message, self.timestamp),
            digestmod = DIGEST
        ).digest()
    
    def is_valid(self):
        """
        Checks whether the current ticket is valid or not.
        """
        # Check if we're within the threshold:
        if not self.timestamp_meets_threshold():
            return False
        
        return self.get_digest() == self.digest

 
