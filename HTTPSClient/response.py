class Response:
    def __init__(self, resp_bytes):
        self.encoding = ''
        self.get_encoding(resp_bytes)
        self.response_to_print = b''
        border = resp_bytes.find(b'\r\n\r\n')
        meta_data_border = resp_bytes.find(b'\r\n')
        self.headers = resp_bytes[meta_data_border + 2:border + 4]
        self.meta_data = resp_bytes[0:meta_data_border + 2]
        self.body = resp_bytes[border + 4:]

    def get_encoding(self, resp_bytes):
        begin = resp_bytes.find(b'charset=')
        if not begin == -1:
            begin += len('charset=')
        else:
            self.encoding = 'utf-8'
            return 0
        resp = resp_bytes[begin:]
        end = resp.find(b'\r\n')
        self.encoding = str(resp[0:end], encoding='utf-8')

    def prepare_response(self, is_meta, is_head, is_body, is_all):
        text = b''
        if is_meta:
            text = self.meta_data
        if is_head:
            text = self.headers
        if is_body or not (is_head or is_all or is_meta):
            text = b''.join((text, self.body))
        if is_all:
            text = b''.join((self.meta_data, self.headers, self.body))
        self.response_to_print = text

    def __str__(self):
        return self.response_to_print.decode(encoding=self.encoding)
