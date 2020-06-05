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

    @staticmethod
    def parse_from_bytes(response_data):
        meta_and_headers, body = response_data.split(b'\r\n\r\n', 2)
        meta_and_headers = meta_and_headers.decode(encoding='utf-8')
        lines = meta_and_headers.splitlines()
        meta = lines.pop(0)
        proto, code, message = meta.split(' ', 3)
        code = int(code)
        headers = {}
        while True:
            line = lines.pop(0).strip()
            if not lines:
                break
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
