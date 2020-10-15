import string
from datetime import datetime, timedelta
import struct
import fxp_bytes

MICROS_PER_SECOND = 1_000_000


def serialize_address(ip: string, port: int) -> bytes:
    ip_as_bytes = bytes(map(int, ip.split('.')))
    port_as_bytes = struct.pack('>H', port)

    full_byte = ip_as_bytes + port_as_bytes

    # print(ip_as_bytes)
    # print(port_as_bytes)

    return full_byte


def deserialize_price(b: bytes) -> float:
    p = struct.unpack('<d', b)
    return p[0]


def deserialize_utcdatetime(b: bytes) -> datetime:
    epoch = datetime(1970, 1, 1)
    p = struct.unpack('>Q', b)
    microseconds = p[0]
    seconds = microseconds / MICROS_PER_SECOND
    deserialized_time = epoch + timedelta(seconds=seconds)
    return deserialized_time


def unmarshal_message(b: bytes):
    unmarshalled_message = ''
    time = deserialize_utcdatetime(b[0:8])
    currencies = b[8:14].decode("utf-8")
    conversion = deserialize_price(b[14:22])
    unmarshalled_message += str(time) + ' '
    unmarshalled_message += currencies[0:3] + ' '
    unmarshalled_message += currencies[3:] + ' '
    unmarshalled_message += str(conversion)
    return unmarshalled_message


# full_byte = serialize_address('127.0.0.1', 65534)
#
# print(fxp_bytes.deserialize_address(full_byte))

# print('Original number: ' + str(9006104071832581.0))
# p = deserialize_price(b'\x05\x04\x03\x02\x01\xff?C')
# print('Deserialized: ' + str(p))
# print('Serialized: ' + str(fxp_bytes.serialize_price(9006104071832581.0)))
# print('Serialized (after deserialized): ' + str(fxp_bytes.serialize_price(p)))

# print(fxp_bytes.serialize_utcdatetime(datetime(1971, 12, 10, 1, 2, 3, 64000)))
# print(deserialize_utcdatetime(b'\x00\x007\xa3e\x8e\xf2\xc0'))

# print(unmarshal_message(b'\x00\x04\tT\xdd5@\x00GBPUSD\xbba\xdb\xa2\xcc\x86\xf3?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'))
# print(unmarshal_message(b'\x00\x04\t@\xbf]\xe0\x00USDJPY\x12\x83\xc0\xca\xa1\x11[@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'))

