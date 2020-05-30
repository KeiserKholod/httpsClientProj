class Response:
    def __init__(self, resp_bytes):
        self.encoding = ''
        self.code = 0
        self.code_message = ''
        self.__get_encoding(resp_bytes)
        self.response_to_print = b''
        border = resp_bytes.find(b'\r\n\r\n')
        meta_data_border = resp_bytes.find(b'\r\n')
        self.all_headers = resp_bytes[meta_data_border + 2:border + 4]
        self.headers = dict()
        self.__get_headers(resp_bytes, meta_data_border, border)
        self.meta_data = resp_bytes[0:meta_data_border + 2]
        self.body = resp_bytes[border + 4:]
        self.__get_code()

    def __get_headers(self, resp_bytes, meta_data_border, border):
        headers_raw = resp_bytes[meta_data_border + 2:border].split(b'\r\n')
        for line in headers_raw:
            partitions = line.split(b':')
            self.headers[partitions[0]] = partitions[1][1:]


    def __get_encoding(self, resp_bytes):
        begin = resp_bytes.find(b'charset=')
        if not begin == -1:
            begin += len('charset=')
        else:
            self.encoding = 'utf-8'
            return 0
        resp = resp_bytes[begin:]
        end = resp.find(b'\r\n')
        self.encoding = str(resp[0:end], encoding='utf-8')

    def __get_code(self):
        self.code = int(self.meta_data.split(b' ')[1])
        self.code_message = self.meta_data.split(b' ')[2][0:-2]

    def prepare_response(self, output_level):
        output_level = int(output_level)
        response = []
        if output_level == 0:
            response.append(self.meta_data)
        if output_level == 1:
            response.append(self.all_headers)
        if output_level == 2:
            response.append(self.body)
        if output_level == 3:
            response.append(self.meta_data)
            response.append(self.all_headers)
            response.append(self.body)
        if output_level == 4:
            response.append(str(self.code).encode())
        if output_level == 5:
            response.append(str(self.code).encode())
            response.append(' ')
            response.append(self.code_message)
        self.response_to_print = b''.join(response)

    def __str__(self):
        return self.response_to_print.decode(encoding=self.encoding)
