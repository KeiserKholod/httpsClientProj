class HTTPSClientError(Exception):
    message = 'Error'


class InvalidLink(HTTPSClientError):
    message = "Error: Invalid link"


class InvalidHTTPMethod(HTTPSClientError):
    message = "Error: Invalid HTTP method"


class InvalidProtocol(HTTPSClientError):
    message = "Error: Invalid protocol"


class ConnectionError(HTTPSClientError):
    message = "Error: Connection error"
