"""
CPSC 5520, Seattle University
This is free and unencumbered software released into the public domain.
:Author: Ruifeng Wang
:Version: Fall2020
"""
import string
from datetime import datetime, timedelta
import struct

MICROS_PER_SECOND = 1_000_000


def serialize_address(ip: string, port: int) -> bytes:
    """
    Converts an IP address (string) and port (int) into a byte stream to send to
    the publisher.
    :param ip: IP address to be converted
    :param port: Port number to be converted
    :return: bytes to be sent to the publisher
    """
    ip_as_bytes = bytes(map(int, ip.split('.')))
    port_as_bytes = struct.pack('>H', port)

    full_byte = ip_as_bytes + port_as_bytes

    return full_byte


def deserialize_price(b: bytes) -> float:
    """
    Deserializes the exchange rate from bytes to a float
    :param b: byte sequence of conversion rate
    :return: conversion rate as a float
    """
    p = struct.unpack('<d', b)
    return p[0]


def deserialize_utcdatetime(b: bytes) -> datetime:
    """
    Deserializes a UTC datetime from a byte stream into a datetime
    :param b: byte sequence of UTC datetime
    :return: datetime timestamp
    """
    epoch = datetime(1970, 1, 1)
    p = struct.unpack('>Q', b)
    microseconds = p[0]
    seconds = microseconds / MICROS_PER_SECOND
    deserialized_time = epoch + timedelta(seconds=seconds)
    return deserialized_time


def unmarshal_message(b: bytes) -> list:
    """
    Combines all parts of the unmarshalled message together from bytes into
    a list
    :param b: byte stream of a quote
    :return: list form of a message
    """
    unmarshalled_message_list = []
    time = deserialize_utcdatetime(b[0:8])
    currencies = b[8:14].decode("utf-8")
    conversion = deserialize_price(b[14:22])
    unmarshalled_message_list.append(time)
    unmarshalled_message_list.append(currencies[0:3])
    unmarshalled_message_list.append(currencies[3:])
    unmarshalled_message_list.append(conversion)
    return unmarshalled_message_list
