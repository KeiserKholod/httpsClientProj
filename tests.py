import unittest
import http_client


class TestInit(unittest.TestCase):
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


class TestPrepareRequest(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
