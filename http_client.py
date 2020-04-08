import socket
import ssl
import sys
import argparse
from enum import Enum


class Protocol(Enum):
    HTTP = 'HTTP'
    HTTPS = 'HTTPS'


class RequestType(Enum):
    GET = 'GET'
    POST = 'POST'


class Errors(Enum):
    Link = 'Link'
    Req = 'Req'


# keys = ["-h", "--help", "-0", "--http", "-1", "--https",
#         "-t", "--type", "-r", "--req", "-d", "--data", "-n", "response"]


# "HEAD", "PUT","PATCH", "DELETE", "TRACE", "CONNECT", "OPTIONS"

class Request:
    def __init__(self, args):
        self.protocol = Protocol.HTTP
        self.request_type = RequestType('GET')
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
            print("ERROR: Invalid link")
            exit(-1)

    def __parse_link(self, link):
        parts = link.split(':')
        if len(parts) < 2 or len(parts) > 3:
            Request.__throw_error(Errors.Link)

        self.protocol = parts[0].upper()
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

        # if :
        #     print("ERROR: Invalid link")
        #     exit(-1)

    def prepare_request(self):
        if self.request_type == "GET":
            line = 'GET ' + self.request + ' HTTP/1.1\r\n'
            line += 'Host: ' + self.domain + ' \r\n'
            line += 'Connection: close\r\n\r\n'
        if self.request_type == "POST":
            line = 'POST ' + self.request + ' HTTP/1.1\r\n'
            line += 'Host: ' + self.domain + '\r\n'
            line += 'Content-Type: application/x-www-form-urlencoded\r\n'
            line += 'Connection: close\r\n'
            line += 'Content-Length: ' + str(len(self.data_to_send)) + \
                    '\r\n\r\n' + self.data_to_send
        self.request_to_send = line

    def do_request(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.domain, int(self.port)))
        if self.protocol == Protocol.HTTPS:
            sock = ssl.wrap_socket(sock,
                                   keyfile=None,
                                   certfile=None,
                                   server_side=False,
                                   cert_reqs=ssl.CERT_NONE,
                                   ssl_version=ssl.PROTOCOL_SSLv23)
        sock.sendall(self.request_to_send.encode())
        while True:
            response = sock.recv(1024)
            if not response:
                sock.close()
                break
            print(response)


def create_cmd_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('link', default=[''],
                        help='example: http://domain.com/path')
    parser.add_argument('-t', '--type', action="store", default=['GET'], dest="req_type",
                        help='Possible: GET, POST')
    parser.add_argument('-d', '--data', action="store", default=[''], dest="data",
                        help='body of POST request or args of GET request')
    return parser


cmd_parser = create_cmd_parser()
args = cmd_parser.parse_args()
print(args)
request = Request(args)
