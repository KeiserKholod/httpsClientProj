import re
from https_client import errors


class Response:
    def __init__(self,
                 proto=None,
                 code=None,
                 message=None,
                 headers=None,
                 body=None,
                 encoding=None):
        self.proto = proto
        self.code = code
        self.message = message
        self.headers = headers
        self.body = body
        self.encoding = encoding

    @property
    def meta_data(self):
        return f'{self.proto} {self.code} {self.message}'

    @property
    def raw_headers(self):
        return '\r\n'.join(f'{header}: {value}' for header, value in self.headers.items())

    @staticmethod
    def parse_from_bytes(response_data):
        meta_and_headers, *body = response_data.split(b'\r\n\r\n', 2)
        body = b''.join(body)
        meta_and_headers = meta_and_headers.decode(encoding='utf-8')
        lines = meta_and_headers.splitlines()
        meta = lines.pop(0)
        check_meta = re.compile(r"(?P<proto>HTTP/\d\.\d) (?P<code>\d{3}) (?P<message>[\w]*)")
        checked_meta = check_meta.match(meta)
        if checked_meta is None:
            raise errors.InvalidResponse
        proto, code, message = checked_meta.groups()[0], checked_meta.groups()[1], checked_meta.groups()[2]
        code = int(code)
        headers = {}
        while True:
            if not lines:
                break
            line = lines.pop(0).strip()
            header, value = line.split(': ', 1)
            headers[header] = value
        encoding = Response.__get_encoding(headers)
        return Response(proto=proto, code=code, message=message, headers=headers, body=body, encoding=encoding)

    @staticmethod
    def __get_encoding(headers):
        if 'Content-Type' in headers:
            encoding = headers['Content-Type'].split('charset=')[1]
        elif 'Content-Encoding' in headers:
            encoding = headers['Content-Encoding']
        else:
            encoding = 'utf-8'
        return encoding
