# -*- coding: utf-8 -*-
###############################################################

try:
    import smartcard
except ImportError:
    pass

from datetime import date


def check_result(func):
    if isinstance(func, tuple) and len(func) == 2:
        if func != (0x90, 0x00):
            raise Exception('Wrong result code: %x %x' % func)

    elif callable(func):
        def decorator(*args, **kwargs):
            data, w1, w2 = func(*args, **kwargs)
            if (w1, w2) != (0x90, 0x00):
                raise Exception('Wrong result code: %x %x' % (w1, w2))
            return data
        return decorator


def decode_int(length):
    # https://en.wikipedia.org/wiki/X.690#Length_octets
    if length[0] & 0b10000000:
        length = length[1:]
        result = 0
        for i, byte in enumerate(length):
            result += byte << ((len(length) - i - 1) * 8)
        return result
    else:
        return length[0]

owner_information = (
    ('policy_number', 38, str, {}),
    ('last_name', 33, str, {}),
    ('first_name', 34, str, {}),
    ('patr_name', 35, str, {'optional': True}),
    ('sex', 37, int, {}),
    ('birth_date', 36, date, {}),
    ('citizenship', 48, (
                            ('country_code', 49, str, {}),
                            ('country_cyrillic_name', 50, str, {})
                        ),
        {'optional': True}),
    ('snils', 39, str, {'optional': True}),
    ('expire_date', 40, date, {'optional': True}),
    ('birth_place', 41, str, {'optional': True}),
    ('issue_date', 42, date, {'optional': True}),
    # ('photo', 64, None, {'optional': True})
)

smo_information = (
    ('ogrn', 81, str, {}),
    ('okato', 82, str, {}),
    ('insurance_start_date', 83, date, {}),
    ('insurance_expire_date', 84, date, {'optional': True}),
    # ('eds', 96, None, {'optional': True})
)


class POMSDataDecoder:
    def __init__(self, data, struct):
        self.data = data
        self.struct = struct
        self.dp = 0

    def check_field(self, field_info):
        if (isinstance(field_info[2], tuple) and self.data[self.dp] & 0b100000) or not (self.data[self.dp] & 0b100000):
            if self.data[self.dp+1] == field_info[1]:
                return True
        return False

    def decode_next(self, field_info):
        # check field attributes (simple/complex, id)
        if self.check_field(field_info):
            self.dp += 2
            length = [self.data[self.dp]]
            if length[0] & 0b10000000:
                length += self.data[self.dp+1: self.dp+1+(length[0] & 0b01111111)]
            self.dp += len(length)
            length = decode_int(length)  # field length
            data = self.data[self.dp: self.dp+length]

            if isinstance(field_info[2], tuple):
                out = dict()
                for fi in field_info[2]:
                    out[fi[0]] = self.decode_next(fi)
                return out

            self.dp += length
            if field_info[2] is str:
                return self.decode_str(data)
            elif field_info[2] is int:
                return self.decode_int(data)
            elif field_info[2] is date:
                return self.decode_date(data)
            return ''
        elif field_info[3].get('optional', False):
            return ''
        else:
            raise Exception('Field is missing')

    def decode_all(self):
        out = dict()
        for field_info in self.struct:
            out[field_info[0]] = self.decode_next(field_info)
        return out

    @staticmethod
    def decode_str(arr):
        return ''.join([chr(c) for c in arr]).decode('utf-8', 'replace')

    @staticmethod
    def decode_int(arr):
        return arr[0]  # used only for sex (1/2)

    @staticmethod
    def decode_date(arr):
        year = int(str(arr[2] >> 4) + str(arr[2] & 0b1111) + str(arr[3] >> 4) + str(arr[3] & 0b1111))
        month = int(str(arr[1] >> 4) + str(arr[1] & 0b1111))
        day = int(str(arr[0] >> 4) + str(arr[0] & 0b1111))
        return date(year, month, day).strftime('%d.%m.%Y')


class POMSReader:
    SELECT_APP = b'\x00\xa4\x04\x0c%c%s'  # length, app name
    SELECT_FILE = b'\x00\xa4\x02\x0c\x02%c%c'  # two last bytes of file id
    READ_FILE = b'\x00\xb0%c%c%c'  # 2-byte offset, length
    GET_DATA = b'\x00\xca%c%c\x02'  # 2 bytes

    def __init__(self, reader=0):
        self.connection = None

        readers_list = smartcard.listReaders()
        if not readers_list:
            raise Exception('No smartcard readers were found')
        try:
            readers = smartcard.System.readers()
            if isinstance(reader, int):
                self.reader = readers[reader]
            elif isinstance(reader, str):
                self.reader = readers[readers_list.index(reader)]
            else:
                raise Exception('Wrong reader parameter: "%s"' % reader)
            self.connection = self.reader.createConnection()
        except KeyError:
            raise Exception('Specified smartcard reader was not found')

    def connect(self):
        self.connection.connect()

    def disconnect(self):
        self.connection.disconnect()

    def transmit(self, s):
        return self.connection.transmit([ord(c) for c in s])

    @check_result
    def select_application(self, name):
        return self.transmit(self.SELECT_APP % (len(name), name))

    @check_result
    def select_file(self, b1, b2):
        return self.transmit(self.SELECT_FILE % (b1, b2))

    @check_result
    def binary_read(self, offset, length):
        out = []
        w1 = w2 = None
        for i in range(offset, offset+length, 220):
            l = 220
            if i + 220 > offset + length:
                l = length % 220
            data, w1, w2 = self.transmit(self.READ_FILE % (i / 0xFF, i & 0xFF, l))
            check_result((w1, w2))
            out += data
        return out, w1, w2

    @staticmethod
    def get_bit_state(num, offset):
        return bool((num >> (offset & 31)) & 1)

    def read_object(self, root, tag_type):
        tag = self.binary_read(0, 1)
        if tag[0] and ((tag[0] & 0b11111) == root or (tag[0] & 0b11000000) == (tag_type << 6)):
            length = self.binary_read(1, 1)
            if length[0]:
                if length[0] & 0b10000000:  # https://en.wikipedia.org/wiki/X.690#Length_octets
                    length += self.binary_read(2, length[0] & 0b01111111)
                data_length = decode_int(length)
                if data_length:
                    data = self.binary_read(1+len(length), data_length)
                    return data
                else:
                    return []
            else:
                return []
        else:
            return []

    @check_result
    def get_data(self, b1, b2):
        return self.transmit(self.GET_DATA % (b1, b2))

    def get_owner_information(self):
        self.select_application('foms_root')
        self.select_application('FOMS_ID')
        self.select_file(2, 1)
        obj = self.read_object(2, 1)
        return obj

    def get_smo_information(self):
        self.select_application('FOMS_INS')
        file_id = self.get_data(1, 176)
        if len(file_id) == 2:
            self.select_file(*file_id)
            obj = self.read_object(4, 1)
        else:
            obj = []
        return obj