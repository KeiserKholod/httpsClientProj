from HTTPSClient import request as req
from HTTPSClient import errors
import argparse
import sys


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
    parser.add_argument('-j', '--json', action='store_true', dest="is_json",
                        help='to take cookie from json')
    parser.add_argument('-0', action='store_true', dest="is_meta",
                        help='to write meta data of response')
    parser.add_argument('-1', action='store_true', dest="is_head",
                        help='to write head of response')
    parser.add_argument('-2', action='store_true', dest="is_body",
                        help='to write body of response')
    parser.add_argument('-3', '--all', action='store_true', dest="is_all",
                        help='to write all response')
    parser.add_argument('-H', '--headers', default=None, nargs='+', dest="custom_headers",
                        help='to add custom headers or change already existing')
    parser.add_argument('-b', '--bin', action='store_true', dest="resp_is_bin",
                        help='to write response as binary data')
    return parser


if __name__ == '__main__':
    cmd_parser = create_cmd_parser()
    args = cmd_parser.parse_args()
    try:
        request = req.Request(args.custom_headers, args.show_request, args.agent, args.referer, args.cookie,
                              args.path_to_cookie, args.is_json, args.req_type, args.body, args.path_to_body,
                              args.link)
        response = request.do_request()
        response.prepare_response(args.is_meta, args.is_head, args.is_body, args.is_all)
        if not args.resp_is_bin:
            sys.stdout.write(response.__str__())
        else:
            sys.stdout.buffer.write(response.response_to_print)
    except errors.HTTPSClientError as e:
        print(e.message)
        exit(-1)
