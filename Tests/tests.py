import unittest
import http_client
from HTTPSClient import response as respf
from HTTPSClient import request as reqf
from HTTPSClient import errors
import tempfile
import os


class TestRequest(unittest.TestCase):
    def test_request_get_http(self):
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['http://ptsv2.com/t/xfg/post', '-t', 'get'])
        request = reqf.Request(args.link, args.custom_headers, args.show_request, args.agent, args.referer, args.cookie,
                              args.path_to_cookie, args.is_json, args.req_type, args.body, args.path_to_body)
        self.assertEqual(request.request_method, reqf.RequestMethod.GET)
        self.assertEqual(request.protocol, reqf.Protocol.HTTP)
        self.assertEqual(request.request, '/t/xfg/post')
        self.assertEqual(request.domain, 'ptsv2.com')
        self.assertEqual(request.port, '80')
        self.assertEqual(request.data_to_send, '')

    def test_request_post_http(self):
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['http://ptsv2.com/t/xfg/post', '-t', 'post'])
        request = reqf.Request(args.link, args.custom_headers, args.show_request, args.agent, args.referer, args.cookie,
                              args.path_to_cookie, args.is_json, args.req_type, args.body, args.path_to_body)
        self.assertEqual(request.request_method, reqf.RequestMethod.POST)
        self.assertEqual(request.protocol, reqf.Protocol.HTTP)
        self.assertEqual(request.request, '/t/xfg/post')
        self.assertEqual(request.domain, 'ptsv2.com')
        self.assertEqual(request.port, '80')
        self.assertEqual(request.data_to_send, '')

    def test_custom_request_https(self):
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['https://abc.de:123/request', '-t', 'post', '-d', 'data=0123'])
        request = reqf.Request(args.link, args.custom_headers, args.show_request, args.agent, args.referer, args.cookie,
                              args.path_to_cookie, args.is_json, args.req_type, args.body, args.path_to_body)
        self.assertEqual(request.request_method, reqf.RequestMethod.POST)
        self.assertEqual(request.protocol, reqf.Protocol.HTTPS)
        self.assertEqual(request.request, '/request')
        self.assertEqual(request.domain, 'abc.de')
        self.assertEqual(request.port, '123')
        self.assertEqual(request.data_to_send, 'data=0123')

    def test_wrong_link(self):
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['httpqweq'])
        with self.assertRaises(errors.HTTPSClientError):
            request = reqf.Request(args.link, args.custom_headers, args.show_request, args.agent, args.referer, args.cookie,
                              args.path_to_cookie, args.is_json, args.req_type, args.body, args.path_to_body)

    def test_wrong_req_type(self):
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['https://abc.de:123/request', '-t', 'qwer'])
        with self.assertRaises(errors.InvalidHTTPMethod):
            request = reqf.Request(args.link, args.custom_headers, args.show_request, args.agent, args.referer, args.cookie,
                              args.path_to_cookie, args.is_json, args.req_type, args.body, args.path_to_body)

    def test_wrong_protocol(self):
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['qwerty://abc.de:123/request'])
        with self.assertRaises(errors.InvalidProtocol):
            request = reqf.Request(args.link, args.custom_headers, args.show_request, args.agent, args.referer, args.cookie,
                              args.path_to_cookie, args.is_json, args.req_type, args.body, args.path_to_body)

    def test_user_agent(self):
        req = 'GET /t/xfg/post HTTP/1.1\r\n' \
              'Host: ptsv2.com\r\n' \
              'Connection: close\r\n' \
              'User-Agent: qwerty\r\n\r\n'
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['http://ptsv2.com/t/xfg/post', '-a', 'qwerty'])
        request = reqf.Request(args.link, args.custom_headers, args.show_request, args.agent, args.referer, args.cookie,
                              args.path_to_cookie, args.is_json, args.req_type, args.body, args.path_to_body)
        request.do_request()
        self.assertEqual(req, request.request_to_send)

    def test_referer(self):
        req = 'GET /t/xfg/post HTTP/1.1\r\n' \
              'Host: ptsv2.com\r\n' \
              'Connection: close\r\n' \
              'Referer: qwerty\r\n\r\n'
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['http://ptsv2.com/t/xfg/post', '-r', 'qwerty'])
        request = reqf.Request(args.link, args.custom_headers, args.show_request, args.agent, args.referer, args.cookie,
                              args.path_to_cookie, args.is_json, args.req_type, args.body, args.path_to_body)
        request.do_request()
        self.assertEqual(req, request.request_to_send)

    def test_cookie(self):
        req = 'GET /t/xfg/post HTTP/1.1\r\n' \
              'Host: ptsv2.com\r\n' \
              'Connection: close\r\n' \
              'Cookie: qwerty\r\n\r\n'
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['http://ptsv2.com/t/xfg/post', '-c', 'qwerty'])
        request = reqf.Request(args.link, args.custom_headers, args.show_request, args.agent, args.referer, args.cookie,
                              args.path_to_cookie, args.is_json, args.req_type, args.body, args.path_to_body)
        request.do_request()
        self.assertEqual(req, request.request_to_send)

    def test_cookie_file(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as file:
            file.write('qwer=ty')
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['http://ptsv2.com/t/xfg/post', '--cookie-file', file.name])
        request = reqf.Request(args.link, args.custom_headers, args.show_request, args.agent, args.referer, args.cookie,
                              args.path_to_cookie, args.is_json, args.req_type, args.body, args.path_to_body)
        self.assertEqual('qwer=ty', request.cookie)
        os.unlink(file.name)

    def test_cookie_json_file(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as file:
            file.write('{"a": "b", "c": "d", "e": "f"}')
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['http://ptsv2.com/t/xfg/post', '--cookie-file', file.name, '-j'])
        request = reqf.Request(args.link, args.custom_headers, args.show_request, args.agent, args.referer, args.cookie,
                              args.path_to_cookie, args.is_json, args.req_type, args.body, args.path_to_body)
        self.assertEqual('a=b;c=d;e=f;', request.cookie)
        os.unlink(file.name)

    def test_body_file(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as file:
            file.write('pass=word')
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['http://ptsv2.com/t/xfg/post', '--body-file', file.name])
        request = reqf.Request(args.link, args.custom_headers, args.show_request, args.agent, args.referer, args.cookie,
                              args.path_to_cookie, args.is_json, args.req_type, args.body, args.path_to_body)
        self.assertEqual('pass=word', request.data_to_send)
        os.unlink(file.name)

    def test_get_with_args(self):
        req = 'GET /t/xfg/post?qw=12 HTTP/1.1\r\n' \
              'Host: ptsv2.com\r\n' \
              'Connection: close\r\n\r\n'
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['http://ptsv2.com/t/xfg/post', '-d', 'qw=12'])
        request = reqf.Request(args.link, args.custom_headers, args.show_request, args.agent, args.referer, args.cookie,
                              args.path_to_cookie, args.is_json, args.req_type, args.body, args.path_to_body)
        request.do_request()
        self.assertEqual(req, request.request_to_send)


class TestResponse(unittest.TestCase):
    meta = b'HTTP/1.1 200 OK\r\n'
    headers = b'Access-Control-Allow-Origin: *\r\n' \
              b'Content-Type: text/html; charset=utf-8\r\n' \
              b'X-Cloud-Trace-Context: 22097699704b3f0712a88db1c88d3974\r\n' \
              b'Date: Sat, 11 Apr 2020 14:05:46 GMT\r\n' \
              b'Server: Google Frontend\r\n' \
              b'Content-Length: 54\r\n' \
              b'Connection: close\r\n\r\n'
    body = b'Thank you for this dump. I hope you have a lovely day!'

    def test_init_resp(self):
        resp_txt = TestResponse.meta + TestResponse.headers + TestResponse.body
        resp = respf.Response(resp_txt)
        self.assertEqual(TestResponse.headers, resp.headers)
        self.assertEqual(TestResponse.body, resp.body)

    def test_prepare_resp_head(self):
        resp_txt = TestResponse.meta + TestResponse.headers + TestResponse.body
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['https://abc.de:123/request', '-1'])
        resp = respf.Response(resp_txt)
        resp.prepare_response(args.is_meta, args.is_head, args.is_body, args.is_all)
        self.assertEqual(resp.response_to_print, TestResponse.headers)

    def test_prepare_resp_body(self):
        resp_txt = TestResponse.meta + TestResponse.headers + TestResponse.body
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['https://abc.de:123/request', '-2'])
        resp = respf.Response(resp_txt)
        resp.prepare_response(args.is_meta, args.is_head, args.is_body, args.is_all)
        self.assertEqual(resp.response_to_print, TestResponse.body)

    def test_prepare_resp_all(self):
        resp_txt = TestResponse.meta + TestResponse.headers + TestResponse.body
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['https://abc.de:123/request', '-3'])
        resp = respf.Response(resp_txt)
        resp.prepare_response(args.is_meta, args.is_head, args.is_body, args.is_all)
        self.assertEqual(resp.response_to_print, resp_txt)


if __name__ == '__main__':
    unittest.main()
