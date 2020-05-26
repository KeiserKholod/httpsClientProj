import socket
import ssl
import json
from HTTPSClient import errors
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
        begin = resp_bytes.find(b'charset=')
        if not begin == -1:
            begin += len('charset=')
        else:
            self.encoding = 'utf-8'
            return 0
        resp = resp_bytes[begin:]
        end = resp.find(b'\r\n')
        self.encoding = str(resp[0:end], encoding='utf-8')

    def prepare_response(self, is_meta, is_head, is_body, is_all):
        text = b''
        if is_meta:
            text = self.meta_data
        if is_head:
            text = self.headers
        if is_body or not (is_head or is_all or is_meta):
            text = b''.join((text, self.body))
        if is_all:
            text = b''.join((self.meta_data, self.headers, self.body))
        self.response_to_print = text

    def __str__(self):
        return self.response_to_print.decode(encoding=self.encoding)


class Request:
    def __init__(self,
                 custom_headers,
                 show_request,
                 agent,
                 referer,
                 cookie,
                 path_to_cookie,
                 is_json,
                 req_type,
                 body,
                 path_to_body,
                 link):
        self.headers = dict()
        self.custom_headers = custom_headers
        self.show_request = show_request
        self.request_to_send = b''
        self.user_agent = agent
        self.referer = referer
        self.cookie = cookie
        self.cookie = ''
        cookie = cookie
        if path_to_cookie != '':
            self.__get_cookie_from_file(path_to_cookie, is_json)
        else:
            if is_json:
                self.__parse_cookie_from_json(self, cookie)
            else:
                self.cookie = cookie
        self.protocol = Protocol.HTTP
        try:
            self.request_method = RequestMethod(req_type.upper())
        except ValueError:
            raise errors.InvalidHTTPMethod()
        self.domain = ""
        self.port = "80"
        self.request = "/"
        self.data_to_send = body
        if path_to_body != '':
            self.__get_data_to_send_from_file(path_to_body)
        self.__parse_link(link)
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

    def __get_cookie_from_file(self, path, is_json):
        cookie = ''
        with open(path, 'r') as file:
            cookie = file.read()
            if is_json:
                self.__parse_cookie_from_json(cookie)
            else:
                self.cookie = cookie

    def __parse_cookie_from_json(self, cookie):
        cookie_dict = json.loads(cookie)
        cookies = []
        for key in cookie_dict:
            cookies.append('{}={};'.format(key, cookie_dict[key]))
        self.cookie = ''.join(cookies)

    def __get_data_to_send_from_file(self, path):
        with open(path, 'r') as file:
            self.data_to_send = file.read()

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
        request = []
        if self.request_method == RequestMethod.GET and self.data_to_send != '':
            self.request = ''.join((self.request, '?', self.data_to_send))
        request.append('{} {} {}'.format(self.request_method.value, self.request, 'HTTP/1.1'))
        for key in self.headers.keys():
            request.append('{}: {}'.format(key, self.headers[key]))
        request.append('')
        request.append('')

        if self.request_method == RequestMethod.POST or \
                self.request_method == RequestMethod.DELETE or \
                self.request_method == RequestMethod.PUT or \
                self.request_method == RequestMethod.PATCH:
            request.pop()
            request.append(self.data_to_send)
        request = '\r\n'.join(request)
        self.request_to_send = request
        if self.show_request != 0:
            print(request.encode() + b'')
        return request

    def do_request(self):
        try:
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
            all_response = []
            while True:
                response_bytes = sock.recv(1024)
                all_response.append(response_bytes)
                if not response_bytes:
                    break
            sock.close()
            response = Response(b''.join(all_response))
        except ValueError:
            raise errors.ConnectionError
        else:
            return response
