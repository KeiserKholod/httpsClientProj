class HTTPSClientError(Exception):
    message = 'Error'


class InvalidLink(HTTPSClientError):
    message = "Invalid link"


class InvalidHTTPMethod(HTTPSClientError):
    message = "Invalid HTTP method"


class InvalidProtocol(HTTPSClientError):
    message = "Invalid protocol"


class ConnectionError(HTTPSClientError):
    message = "Connection error"


class InvalidResponse(HTTPSClientError):
    message = "Invalid response"
