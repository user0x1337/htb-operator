class HtbCliException(Exception):
    """Base exception class for `hackthebox`"""
    pass

class AuthenticationException(HtbCliException):
    """An error authenticating to the API"""
    pass

class RequestException(HtbCliException):
    pass

class IncorrectArgumentException(HtbCliException):
    pass

class IncorrectFlagException(HtbCliException):
    pass

class UnknownDirectoryException(HtbCliException):
    pass

class CannotSwitchWithActive(HtbCliException):
    pass

class VpnException(HtbCliException):
    pass

class NoPwnBoxActiveException(HtbCliException):
    pass