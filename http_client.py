from https_client.request import Request
from https_client.response import Response
from https_client import errors
import argparse
import sys


def create_cmd_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('link', default=None,
                        help='example: http://domain.com/path')
    parser.add_argument('-t', '--type', default='GET', dest="req_type",
                        help='Possible: GET, POST, HEAD, OPTIONS, CONNECT, TRACE, DELETE, PUT, TRACE')
    parser.add_argument('-T', '--timeout', default='0', dest="timeout",
                        help='to set timeout')
    parser.add_argument('-d', '--body', default='', dest="body",
                        help='body of POST request or args of GET request')
    parser.add_argument('--body-file', default=None, dest="path_to_body",
                        help='get body of POST request or'
                             ' args of GET request from file ')
    parser.add_argument('-a', '--agent', default=None, dest="agent",
                        help='to send user-agent')
    parser.add_argument('-r', '--ref', default=None, dest="referer",
                        help='to send referer')
    parser.add_argument('-c', '--cookie', default=None, dest="cookie",
                        help='to send cookie')
    parser.add_argument('--cookie-file', default=None, dest="path_to_cookie",
                        help='to send cookie from file')
    parser.add_argument('-v', '--verbose', action='store_true', dest="show_request",
                        help='to show request')
    parser.add_argument('-j', '--json', action='store_true', dest="is_json",
                        help='to take cookie from json')
    parser.add_argument('-o', '--output-level', default='2', dest="output_level",
                        help='0 - write meta data; '
                             '1 - write headers; '
                             '2 - write body; '
                             '3 - write all response; ')
    parser.add_argument('-H', '--headers', default=None, nargs='+', dest="custom_headers",
                        help='to add custom headers or change already existing')
    parser.add_argument('-b', '--bin', action='store_true', dest="resp_is_bin",
                        help='to write response as binary data')
    parser.add_argument('-P', '--pass', default=None, dest="password",
                        help='to set password')
    parser.add_argument('-U', '--user', default=None, dest="user",
                        help='to set user')
    return parser


def print_response(args, response_data):
    response_to_print = []
    if int(args.output_level) == 0:
        response_to_print.append(response.meta_data)
    if int(args.output_level) == 1:
        response_to_print.append(response.raw_headers)
    if int(args.output_level) == 2:
        if not args.resp_is_bin:
            response_to_print.append(response.body.decode(encoding=response.encoding))
        else:
            response_to_print.append(response.body)
    if int(args.output_level) == 3:
        response_to_print.append(response.meta_data)
        response_to_print.append(response.raw_headers)
        response_to_print.append('')
        response_to_print.append('')
        if not args.resp_is_bin:
            response_to_print.append(response.body.decode(encoding=response.encoding))
        else:
            response_to_print.append(response.body)

    if args.resp_is_bin:
        for i in range(len(response_to_print)):
            if isinstance(response_to_print[i], str):
                response_to_print[i] = response_to_print[i].encode('utf-8')
        sys.stdout.buffer.write(b'\r\n'.join(response_to_print))
    else:
        sys.stdout.write('\r\n'.join(response_to_print))


if __name__ == '__main__':
    cmd_parser = create_cmd_parser()
    args = cmd_parser.parse_args()
    try:
        request = Request(args.link, args.custom_headers, args.agent, args.referer, args.cookie,
                          args.path_to_cookie, args.is_json, args.req_type, args.body, args.path_to_body,
                          args.timeout, args.password, args.user)
        response = Response.parse_from_bytes(request.do_request())
        if args.show_request:
            print(request.request_to_send)
        print_response(args, response)
    except errors.HTTPSClientError as e:
        print('Error: ' + e.message)
        exit(1)
