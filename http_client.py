import socket
import ssl
import argparse
from enum import Enum
from yarl import URL


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
        self.response_to_print = b''
        border = resp_bytes.find(b'\r\n\r\n')
        self.headers = resp_bytes[0:border + 4]
        self.body = resp_bytes[border + 4:]

    def prepare_response(self, args):
        text = b''
        if args.is_head:
            text = self.headers
        if args.is_body or not (args.is_head or args.is_all):
            text = b''.join((text, self.body))
        if args.is_all:
            text = b''.join((self.headers, self.body))
        self.response_to_print = text

    def print_response(self, args):
        if args.path_to_response != '':
            file = open(args.path_to_response, 'wb')
            file.write(self.response_to_print)
            file.close()
        else:
            print(self.response_to_print)


class Request:
    def __init__(self, args):
        self.cont_type = 'application/x-www-form-urlencoded'
        self.show_request = args.show_request
        self.request_to_send = b''
        self.user_agent = args.agent
        self.referer = args.referer
        self.cookie = args.cookie
        if args.path_to_cookie != '':
            self.__get_cookie_from_file(args.path_to_cookie)
        self.protocol = Protocol.HTTP
        try:
            self.request_type = RequestType(args.req_type.upper())
        except ValueError:
            Request.__throw_error(Errors.Req_type)
        self.domain = ""
        self.port = "80"
        self.request = "/"
        self.data_to_send = args.body
        if args.path_to_body != '':
            self.__get_data_to_send_from_file(args.path_to_body)
        self.__parse_link(args.link)

    def __get_cookie_from_file(self, path):
        file = open(path, 'r')
        try:
            self.cookie = file.read()
        except Errors:
            pass
        finally:
            file.close()

    def __get_data_to_send_from_file(self, path):
        file = open(path, 'r')
        try:
            self.data_to_send = file.read()
        except Errors:
            pass
        finally:
            file.close()

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
        url = URL(link)
        try:
            self.protocol = Protocol(url.scheme.upper())
        except ValueError:
            Request.__throw_error(Errors.Prot_type)
        if self.protocol == Protocol.HTTPS:
            self.port = "443"
        port = url.port
        if port is not None:
            self.port = str(port)
        self.domain = url.host
        self.request = url.path_qs

    def __prepare_request(self):
        if self.request_type == RequestType.GET and self.data_to_send != '':
            self.request = ''.join((self.request, '?', self.data_to_send))
        request = ''.join((
            self.request_type.value, ' ', self.request, ' HTTP/1.1\r\n',
            'Host: ', self.domain, '\r\n',
            'Connection: close\r\n'))
        if self.user_agent != '':
            request = ''.join((request,
                               'User-Agent: ', self.user_agent, '\r\n'))
        if self.referer != '':
            request = ''.join((request,
                               'Referer: ', self.referer, '\r\n'))
        if self.cookie != '':
            request = ''.join((request,
                               'Cookie: ', self.cookie, '\r\n'))
        if self.request_type == RequestType.GET or \
                self.request_type == RequestType.HEAD:
            request = ''.join((request, '\r\n'))
        if self.request_type == RequestType.POST:
            request = ''.join((
                request,
                'Content-Type: ', self.cont_type, '\r\n',
                'Content-Length: ', str(len(self.data_to_send)),
                '\r\n\r\n' + self.data_to_send))
        self.request_to_send = request
        if self.show_request != 0:
            print(request)
        return request

    def do_request(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.domain, int(self.port)))
        request_to_send = self.__prepare_request()
        if self.protocol == Protocol.HTTPS:
            sock = ssl.wrap_socket(sock,
                                   keyfile=None,
                                   certfile=None,
                                   server_side=False,
                                   cert_reqs=ssl.CERT_NONE,
                                   ssl_version=ssl.PROTOCOL_SSLv23)
        sock.sendall(request_to_send.encode())
        all_response = b''
        while True:
            response_bytes = sock.recv(1024)
            all_response = b''.join((all_response, response_bytes))
            if not response_bytes:
                break
        sock.close()
        response = Response(all_response)
        return response


def create_cmd_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('link', default=[''],
                        help='example: http://domain.com/path')
    parser.add_argument('-t', '--type', default='GET', dest="req_type",
                        help='Possible: GET, POST, HEAD')
    parser.add_argument('-d', '--body', default='', dest="body",
                        help='body of POST request or args of GET request')
    parser.add_argument('--body-file', default='', dest="path_to_body",
                        help='body of POST request or args of GET request')
    parser.add_argument('-a', '--agent', default='', dest="agent",
                        help='to send user-agent')
    parser.add_argument('-r', '--ref', default='', dest="referer",
                        help='to send referer')
    parser.add_argument('-c', '--cookie', default='', dest="cookie",
                        help='to send cookie')
    parser.add_argument('--cookie-file', default='', dest="path_to_cookie",
                        help='to send cookie from file')
    parser.add_argument('-s', '--show', action='store_true', dest="show_request",
                        help='to show request')
    parser.add_argument('-0', action='store_true', dest="is_head",
                        help='to write head of response')
    parser.add_argument('-1', action='store_true', dest="is_body",
                        help='to write body of response')
    parser.add_argument('-2', '--all', action='store_true', dest="is_all",
                        help='to write all response')
    parser.add_argument('-f', '--file', default='', dest="path_to_response",
                        help='save response in file')
    return parser


if __name__ == '__main__':
    cmd_parser = create_cmd_parser()
    args = cmd_parser.parse_args()
    print(args)
    request = Request(args)
    response = request.do_request()
    response.prepare_response(args)
    response.print_response(args)
