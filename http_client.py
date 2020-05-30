from HTTPSClient import request as req
from HTTPSClient import errors
import argparse
import sys


def create_cmd_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('link', default=None,
                        help='example: http://domain.com/path')
    parser.add_argument('-t', '--type', default='GET', dest="req_type",
                        help='Possible: GET, POST, HEAD, OPTIONS, CONNECT, TRACE, DELETE, PUT, TRACE')
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
                             '1 - write headers; 2 - write body; '
                             '3 - write all response; '
                             '4 - write code of response; '
                             '5 - write code of response and message;')
    parser.add_argument('-H', '--headers', default=None, nargs='+', dest="custom_headers",
                        help='to add custom headers or change already existing')
    parser.add_argument('-b', '--bin', action='store_true', dest="resp_is_bin",
                        help='to write response as binary data')
    return parser


if __name__ == '__main__':
    cmd_parser = create_cmd_parser()
    args = cmd_parser.parse_args()
    try:
        request = req.Request(args.link, args.custom_headers, args.show_request, args.agent, args.referer, args.cookie,
                              args.path_to_cookie, args.is_json, args.req_type, args.body, args.path_to_body)
        response = request.do_request()
        response.prepare_response(args.output_level)
        if not args.resp_is_bin:
            sys.stdout.write(response.__str__())
        else:
            sys.stdout.buffer.write(response.response_to_print)
    except errors.HTTPSClientError as e:
        print(e.message)
        exit(1)
