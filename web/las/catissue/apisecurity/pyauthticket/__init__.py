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
PyAuthTicket? uses HMAC to generate a one time ticket based on a secret key,
optional message and timestamp (defaults to the current time).

If both sides know a secret key (ie, an API key), a receiver can verify the
identity of a sender by requiring a ticket digest and the timestamp used to
create it along with the actual request.

To verify the sender, the receiver would create a ticket with the same
credentials (key, request, timestamp) and verify it against the provided digest.
This does not prevent replay attacks but as the timestamp is provided, a lower
threshold can be set to reduce the time window in which replays can run. 
"""

Version = '0.1'

from authticket import AuthTicket

__all__ = [
    'Version',
    'AuthTicket',
]