import unittest
import http_client


class TestInitReq(unittest.TestCase):
    def test_request_get_http(self):
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['http://ptsv2.com/t/xfg/post', '-t', 'get'])
        request = http_client.Request(args)
        self.assertEqual(request.request_type, http_client.RequestType.GET)
        self.assertEqual(request.protocol, http_client.Protocol.HTTP)
        self.assertEqual(request.request, '/t/xfg/post')
        self.assertEqual(request.domain, 'ptsv2.com')
        self.assertEqual(request.port, '80')
        self.assertEqual(request.data_to_send, '')

    def test_request_post_http(self):
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['http://ptsv2.com/t/xfg/post', '-t', 'post'])
        request = http_client.Request(args)
        self.assertEqual(request.request_type, http_client.RequestType.POST)
        self.assertEqual(request.protocol, http_client.Protocol.HTTP)
        self.assertEqual(request.request, '/t/xfg/post')
        self.assertEqual(request.domain, 'ptsv2.com')
        self.assertEqual(request.port, '80')
        self.assertEqual(request.data_to_send, '')

    def test_custom_request_https(self):
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['https://abc.de:123/request', '-t', 'post', '-d', 'data=0123'])
        request = http_client.Request(args)
        self.assertEqual(request.request_type, http_client.RequestType.POST)
        self.assertEqual(request.protocol, http_client.Protocol.HTTPS)
        self.assertEqual(request.request, '/request')
        self.assertEqual(request.domain, 'abc.de')
        self.assertEqual(request.port, '123')
        self.assertEqual(request.data_to_send, 'data=0123')

    def test_wrong_link(self):
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['httpqweq'])
        with self.assertRaises(ValueError):
            request = http_client.Request(args)

    def test_wrong_req_type(self):
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['https://abc.de:123/request', '-t', 'qwer'])
        with self.assertRaises(ValueError):
            request = http_client.Request(args)

    def test_wrong_protocol(self):
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['qwerty://abc.de:123/request'])
        with self.assertRaises(ValueError):
            request = http_client.Request(args)


class TestResponse(unittest.TestCase):
    headers = b'HTTP/1.1 200 OK\r\n' \
              b'Access-Control-Allow-Origin: *\r\n' \
              b'Content-Type: text/html; charset=utf-8\r\n' \
              b'X-Cloud-Trace-Context: 22097699704b3f0712a88db1c88d3974\r\n' \
              b'Date: Sat, 11 Apr 2020 14:05:46 GMT\r\n' \
              b'Server: Google Frontend\r\n' \
              b'Content-Length: 54\r\n' \
              b'Connection: close\r\n\r\n'
    body = b'Thank you for this dump. I hope you have a lovely day!'

    def test_init_resp(self):
        resp_txt = TestResponse.headers + TestResponse.body
        resp = http_client.Response(resp_txt)
        self.assertEqual(TestResponse.headers, resp.headers)
        self.assertEqual(TestResponse.body, resp.body)

    def test_prepare_resp_head(self):
        resp_txt = TestResponse.headers + TestResponse.body
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['https://abc.de:123/request', '-0'])
        resp = http_client.Response(resp_txt)
        resp.prepare_response(args)
        self.assertEqual(resp.response_to_print, TestResponse.headers)

    def test_prepare_resp_body(self):
        resp_txt = TestResponse.headers + TestResponse.body
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['https://abc.de:123/request', '-1'])
        resp = http_client.Response(resp_txt)
        resp.prepare_response(args)
        self.assertEqual(resp.response_to_print, TestResponse.body)

    def test_prepare_resp_all(self):
        resp_txt = TestResponse.headers + TestResponse.body
        cmd_parser = http_client.create_cmd_parser()
        args = cmd_parser.parse_args(['https://abc.de:123/request', '-2'])
        resp = http_client.Response(resp_txt)
        resp.prepare_response(args)
        self.assertEqual(resp.response_to_print, resp_txt)


if __name__ == '__main__':
    unittest.main()
