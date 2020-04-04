import socket
import ssl
import sys
from enum import Enum


class Protocol(Enum):
    HTTP = 0
    HTTPS = 1


keys = ["-h", "--help", "-0", "--http", "-1", "--https",
        "-t", "--type", "-r", "--req", "-d", "--data", "-n", "response"]
request_types = ["GET", "POST"]


# "HEAD", "PUT","PATCH", "DELETE", "TRACE", "CONNECT", "OPTIONS"

class Data:
    protocol = Protocol.HTTP
    request_type = request_types[0]
    domain = ""
    port = "80"
    request = ""
    data_to_send = ""
    path_to_response = ""
    # user_agent = ""


def write_help():
    """line = sys.argv[0] + " [-0 -1] <domain>[:port] " \
                         "[-t <type>] [-r <req>] " \
                         "[- d <text> -p <path>] [-n <path>] " \
                         "[-u <user-agent>]" \
                         "\n\n"
                         """
    line = sys.argv[0] + " [-0 -1] <domain>[:port] " \
                         "[-t <type>] [-r <req>] " \
                         "[- d <text>] [-n <path>]\n\n"
    line += "keys:\n"
    line += "\t-h or --help to show this text\n"
    line += "\t-0 or --http <domain>[:port] to connect with http\n"
    line += "\t-1 or --https <domain>[:port] to connect with https\n"
    line += "\t-t or --type <type> to choose type of request\n"
    line += "\t\tGET\n\t\tPOST\n"
    line += "\t-r or --req <text> to send this request\n"
    # line += "\t-p or --path <absolute path> to PUT or PATCH data from file\n"
    line += "\t-d or --data <text> to PUT, POST or PATCH data\n"
    # line += "\t-n or --response <absolute path> " \
    #        "to write server response in file\n"
    # line += "\t-u or --user-agent <text> to write user-agent manually\n"
    print(line)


def parse_data(line):
    args = line.split(" ")
    data = check_keys(args)
    return data


def parse_data_from_cmd():
    args = sys.argv[1:]
    data = check_keys(args)
    return data


def prepare_request(data):
    if data.request_type == "GET":
        line = 'GET ' + data.request + ' HTTP/1.1\r\n'
        line += 'Host: ' + data.domain + ' \r\n'
        line += 'Connection: close\r\n\r\n'
    if data.request_type == "POST":
        line = 'POST ' + data.request + ' HTTP/1.1\r\n'
        line += 'Host: ' + data.domain + '\r\n'
        line += 'Content-Type: application/x-www-form-urlencoded\r\n'
        line += 'Connection: close\r\n'
        line += 'Content-Length: ' + str(len(data.data_to_send)) + \
                '\r\n\r\n' + data.data_to_send
    return line


def do_request(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((data.domain, int(data.port)))
    if data.protocol == Protocol.HTTPS:
        sock = ssl.wrap_socket(sock,
                               keyfile=None,
                               certfile=None,
                               server_side=False,
                               cert_reqs=ssl.CERT_NONE,
                               ssl_version=ssl.PROTOCOL_SSLv23)
    line = prepare_request(data)
    sock.sendall(str.encode(line))
    while True:
        response = sock.recv(1024)
        if not response:
            sock.close()
            break
        print(response)


def check_keys(args):
    not_error = True
    protocol = Protocol.HTTP
    request_type = request_types[0]
    domain = ""
    port = "80"
    request = "/"
    data_to_send = ""
    path_to_response = ""
    # user_agent = ""
    i = 0
    while i < len(args):
        word = args[i].lower()
        if word not in keys:
            not_error = False
            break
        if word in ["-h", "--help"]:
            write_help()
            sys.exit(0)
        if word in ["-1", "--https", "-0", "--http"]:
            if word in ["-1", "--https"]:
                protocol = Protocol.HTTPS
                port = "443"
            i += 1
            not_error = i < len(args)
            if not_error:
                tmp = args[i].split(":")
                domain = tmp[0]
                if len(tmp) > 1:
                    port = tmp[1]
        if word in ["-t", "--type"]:
            i += 1
            not_error = i < len(args)
            if not_error:
                type = args[i].upper()
                if type in request_types:
                    request_type = type
                else:
                    not_error = False
        if word in ["-r", "--req"]:
            i += 1
            not_error = i < len(args)
            if not_error:
                request = args[i]
        if word in ["-d", "--data"]:
            i += 1
            not_error = i < len(args)
            if not_error:
                data_to_send = args[i]
        if word in ["-n", "response"]:
            i += 1
            not_error = i < len(args)
            if not_error:
                path_to_response = args[i]
        i += 1
    if domain == "":
        not_error = False
    if not not_error:
        print("ERROR: syntax error, write -h or --help to get help")
        sys.exit(-1)
    else:
        data = Data()
        data.protocol = protocol
        data.request_type = request_type
        data.domain = domain
        data.port = port
        data.request = request
        data.data_to_send = data_to_send
        data.path_to_response = path_to_response
        return data


# args = parse_data(input())
data = parse_data_from_cmd()
do_request(data)
