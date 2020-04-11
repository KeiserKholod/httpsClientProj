import socket
import ssl
import argparse
from enum import Enum


class Protocol(Enum):
    HTTP = 'HTTP'
    HTTPS = 'HTTPS'


class RequestType(Enum):
    GET = 'GET'
    POST = 'POST'
    HEAD = 'HEAD'


class Errors(Enum):
    Link = 0
    Req_type = 1
    Prot_type = 2


# "HEAD", "PUT","PATCH", "DELETE", "TRACE", "CONNECT", "OPTIONS"

class Response:
    def __init__(self, resp_bytes):
        border = resp_bytes.find(b'\r\n\r\n')
        self.headers = resp_bytes[0:border]
        self.body = resp_bytes[border + 4:]



class Request:
    def __init__(self, args):
        self.protocol = Protocol.HTTP
        try:
            self.request_type = RequestType(args.req_type.upper())
        except ValueError:
            Request.__throw_error(Errors.Req_type)
        self.domain = ""
        self.port = "80"
        self.request = "/"
        self.data_to_send = args.data
        self.path_to_response = ""
        self.request_to_send = ""
        self.__parse_link(args.link)

    @staticmethod
    def __throw_error(type):
        if type == Errors.Link:
            raise ValueError("ERROR: Invalid link")
            # print("ERROR: Invalid link")
            # exit(-1)
        if type == Errors.Req_type:
            raise ValueError("Invalid request type")
            # print("ERROR: Invalid request type")
            # exit(-1)
        if type == Errors.Prot_type:
            raise ValueError("Invalid protocol")
            # print("ERROR: Invalid protocol")
            # exit(-1)

    def __parse_link(self, link):
        parts = link.split(':')
        if len(parts) < 2 or len(parts) > 3:
            Request.__throw_error(Errors.Link)
        try:
            self.protocol = Protocol(parts[0].upper())
        except ValueError:
            Request.__throw_error(Errors.Prot_type)
        if self.protocol == Protocol.HTTPS:
            self.port = "443"
        line = parts[1][2:]

        req_index = line.find('/')
        if req_index == -1:
            self.domain = line
        else:
            self.domain = line[0:req_index]
            self.request = line[req_index:]
        if len(parts) == 3:
            req_index = parts[2].find('/')
            if req_index == -1:
                self.port = parts[2]
            else:
                self.port = parts[2][0:req_index]
                self.request = parts[2][req_index:]

    def __prepare_request(self):
        request = ''.join((
            self.request_type.value, ' ', self.request, ' HTTP/1.1\r\n',
            'Host: ', self.domain, '\r\n',
            'Connection: close\r\n'))
        if self.request_type == RequestType.GET or \
                self.request_type == RequestType.HEAD:
            request = ''.join((request, '\r\n'))
        if self.request_type == RequestType.POST:
            request = ''.join((
                request,
                'Content-Type: application/x-www-form-urlencoded\r\n',
                'Content-Length: ', str(len(self.data_to_send)),
                '\r\n\r\n' + self.data_to_send))
        return request

    def do_request(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.domain, int(self.port)))
        request_to_send = self.__prepare_request()
        print(request_to_send)
        if self.protocol == Protocol.HTTPS:
            sock = ssl.wrap_socket(sock,
                                   keyfile=None,
                                   certfile=None,
                                   server_side=False,
                                   cert_reqs=ssl.CERT_NONE,
                                   ssl_version=ssl.PROTOCOL_SSLv23)
        sock.sendall(request_to_send.encode())
        while True:
            responseBytes = sock.recv(1024)
            if not responseBytes:
                sock.close()
                break
            response = Response(responseBytes)
            print(response)


def create_cmd_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('link', default=[''],
                        help='example: http://domain.com/path')
    parser.add_argument('-t', '--type', default='GET', dest="req_type",
                        help='Possible: GET, POST, HEAD')
    parser.add_argument('-d', '--data', default='', dest="data",
                        help='body of POST request or args of GET request')
    return parser


if __name__ == '__main__':
    cmd_parser = create_cmd_parser()
    args = cmd_parser.parse_args()
    print(args)
    request = Request(args)
    response = request.do_request()
