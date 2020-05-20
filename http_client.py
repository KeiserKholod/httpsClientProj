import socket
import ssl
import argparse
import errors
import sys
from enum import Enum
from yarl import URL


class Protocol(Enum):
    HTTP = 'HTTP'
    HTTPS = 'HTTPS'


class RequestMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'
    CONNECT = 'CONNECT'
    TRACE = 'TRACE'
    DELETE = 'DELETE'
    PUT = 'PUT'
    PATCH = 'PATCH'


class Errors(Enum):
    Link = 0
    Req_type = 1
    Prot_type = 2


class Response:
    def __init__(self, resp_bytes):
        self.encoding = ''
        self.get_encoding(resp_bytes)
        self.response_to_print = b''
        border = resp_bytes.find(b'\r\n\r\n')
        meta_data_border = resp_bytes.find(b'\r\n')
        self.headers = resp_bytes[meta_data_border + 2:border + 4]
        self.meta_data = resp_bytes[0:meta_data_border + 2]
        self.body = resp_bytes[border + 4:]

    def get_encoding(self, resp_bytes):
        begin = resp_bytes.find(b'charset=') + len('charset=')
        resp = resp_bytes[begin:]
        end = resp.find(b'\r\n')
        self.encoding = str(resp[0:end], encoding='utf-8')

    def prepare_response(self, args):
        text = b''
        if args.is_meta:
            text = self.meta_data
        if args.is_head:
            text = self.headers
        if args.is_body or not (args.is_head or args.is_all or args.is_meta):
            text = b''.join((text, self.body))
        if args.is_all:
            text = b''.join((self.meta_data, self.headers, self.body))
        self.response_to_print = text

        
    def __str__(self):
        return self.response_to_print.decode(encoding=self.encoding)


class Request:
    def __init__(self, args):
        self.headers = dict()
        self.custom_headers = args.custom_headers
        self.show_request = args.show_request
        self.request_to_send = b''
        self.user_agent = args.agent
        self.referer = args.referer
        self.cookie = args.cookie
        if args.path_to_cookie != '':
            self.__get_cookie_from_file(args.path_to_cookie)
        self.protocol = Protocol.HTTP
        try:
            self.request_method = RequestMethod(args.req_type.upper())
        except ValueError:
            raise errors.InvalidHTTPMethod()
        self.domain = ""
        self.port = "80"
        self.request = "/"
        self.data_to_send = args.body
        if args.path_to_body != '':
            self.__get_data_to_send_from_file(args.path_to_body)
        self.__parse_link(args.link)
        self.__init_headers()

    def __parse_custom_headers(self):
        if not (self.custom_headers is None):
            for header in self.custom_headers:
                separator_ind = header.find(':')
                key = header[0:separator_ind]
                value = header[separator_ind + 1:].strip()
                self.headers[key] = value

    def __init_headers(self):
        self.headers['Host'] = self.domain
        self.headers['Connection'] = 'close'
        if self.user_agent != '':
            self.headers['User-Agent'] = self.user_agent
        if self.referer != '':
            self.headers['Referer'] = self.referer
        if self.cookie != '':
            self.headers['Cookie'] = self.cookie
        if self.request_method == RequestMethod.POST or \
                self.request_method == RequestMethod.DELETE or \
                self.request_method == RequestMethod.PUT or \
                self.request_method == RequestMethod.PATCH:
            self.headers['Content-Type'] = 'application/x-www-form-urlencoded'
            self.headers['Content-Length'] = str(len(self.data_to_send))
        self.__parse_custom_headers()

    def __parse_link(self, link):
        parts = link.split(':')
        if len(parts) < 2 or len(parts) > 3:
            raise errors.InvalidLink()

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

    def __parse_link(self, link):
        url = URL(link)
        try:
            self.protocol = Protocol(url.scheme.upper())
        except ValueError:
            raise errors.InvalidProtocol()

        if self.protocol == Protocol.HTTPS:
            self.port = "443"
        port = url.port
        if port is not None:
            self.port = str(port)
        self.domain = url.host
        self.request = url.path_qs

    def __prepare_request(self):
        if self.request_method == RequestMethod.GET and self.data_to_send != '':
            self.request = ''.join((self.request, '?', self.data_to_send))
        request = ''.join((
            self.request_method.value, ' ', self.request, ' HTTP/1.1\r\n'))
        for key in self.headers.keys():
            request = ''.join((request, key, ': ', self.headers[key], '\r\n'))

        request = ''.join((request, '\r\n'))
        if self.request_method == RequestMethod.POST or \
                self.request_method == RequestMethod.DELETE or \
                self.request_method == RequestMethod.PUT or \
                self.request_method == RequestMethod.PATCH:
            request = ''.join((
                request, self.data_to_send))
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
                        help='Possible: GET, POST, HEAD, OPTIONS, CONNECT, TRACE, DELETE, PUT, TRACE')
    parser.add_argument('-d', '--body', default='', dest="body",
                        help='body of POST request or args of GET request')
    parser.add_argument('--body-file', default='', dest="path_to_body",
                        help='get body of POST request or'
                             ' args of GET request from file ')
    parser.add_argument('-a', '--agent', default='', dest="agent",
                        help='to send user-agent')
    parser.add_argument('-r', '--ref', default='', dest="referer",
                        help='to send referer')
    parser.add_argument('-c', '--cookie', default='', dest="cookie",
                        help='to send cookie')
    parser.add_argument('--cookie-file', default='', dest="path_to_cookie",
                        help='to send cookie from file')
    parser.add_argument('-v', '--verbose', action='store_true', dest="show_request",
                        help='to show request')
    parser.add_argument('-0', action='store_true', dest="is_meta",
                        help='to write meta data of response')
    parser.add_argument('-1', action='store_true', dest="is_head",
                        help='to write head of response')
    parser.add_argument('-2', action='store_true', dest="is_body",
                        help='to write body of response')
    parser.add_argument('-3', '--all', action='store_true', dest="is_all",
                        help='to write all response')
    parser.add_argument('-f', '--file', default='', dest="path_to_response",
                        help='save response in file')
    parser.add_argument('-H', '--headers', default=None, nargs='+', dest="custom_headers",
                        help='to add custom headers or change already existing')
    parser.add_argument('-b', '--bin', action='store_true', dest="resp_is_bin",
                        help='to write response as binary data')
    return parser


if __name__ == '__main__':
    cmd_parser = create_cmd_parser()
    args = cmd_parser.parse_args()
    try:
        request = Request(args)
    except errors.HTTPSClientError as e:
        print(e.message)
        exit(-1)
    else:
        response = request.do_request()
        response.prepare_response(args)
        # response.print_response(args)
        # print(response)
        if not args.resp_is_bin:
            sys.stdout.write(response.__str__())
        else:
            sys.stdout.buffer.write(response.response_to_print)
