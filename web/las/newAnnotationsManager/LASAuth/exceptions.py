class LASAuthException(Exception):
    """Base class for exceptions in LASAuth"""
    pass
    
class AuthenticationSessionExpired(LASAuthException):
    pass
    
class HMACVerificationFailed(LASAuthException):
    pass
    
class AuthenticationDenied(LASAuthException):
    pass
