"""
Copyright 2018 Jason Litzinger
See LICENSE for details.
"""
from __future__ import absolute_import
import attr

from . import _packet, _errors


@attr.s
class ConnectResponse:
    """Object representing a connection response"""
    return_code = attr.ib()
    session_present = attr.ib()


def parse_connack(data, output):
    """Parse a CONNACK packet.

    :param data: Data to parse
    :type data: bytebuffer

    :raises: MQTTParseError if packet is malformed
    :returns: length consumed, return code and session_present flag from the
        CONNACK packet.

    :rtype: int, ConnectResponse

    """
    if len(data) != 4:
        return 0

    remaining_len = data[1]
    if remaining_len != 2:
        raise _errors.MQTTParseError("Remaining length invalid")

    ack_flags = data[2]
    rc = data[3]

    if (ack_flags & 0xFE) != 0:
        raise _errors.MQTTParseError("Reserved bits not clear")

    output.append(
        _packet.MQTTPacket(
            _packet.MQTT_PACKET_CONNACK,
            ConnectResponse(rc, ack_flags)
        )
    )

    return 4


def _null_parse(data, output):
    return len(data)


PARSERS = {
    _packet.MQTT_PACKET_CONNECT: _null_parse,
    _packet.MQTT_PACKET_CONNACK: parse_connack,
    _packet.MQTT_PACKET_PUBLISH: _null_parse,
    _packet.MQTT_PACKET_PUBACK: _null_parse,
    _packet.MQTT_PACKET_PUBREC: _null_parse,
    _packet.MQTT_PACKET_PUBREL: _null_parse,
    _packet.MQTT_PACKET_PUBCOMP: _null_parse,
    _packet.MQTT_PACKET_SUBSCRIBE: _null_parse,
    _packet.MQTT_PACKET_SUBACK: _null_parse,
    _packet.MQTT_PACKET_UNSUBSCRIBE: _null_parse,
    _packet.MQTT_PACKET_UNSUBACK: _null_parse,
    _packet.MQTT_PACKET_PINGREQ: _null_parse,
    _packet.MQTT_PACKET_PINGRESP: _null_parse,
    _packet.MQTT_PACKET_DISCONNECT: _null_parse,
}


def parse(data, output):
    """Parse packets from data.

    :param data: Data to parse into MQTT packets
    :type data: bytearray

    :param output: Output list for storing parsed packets.
    :type output: MutableSequence

    :returns: number of bytes from data consumed

    """
    if not isinstance(data, bytearray):
        raise TypeError("data must be a bytearray")

    consumed = 0
    offset = 0
    while offset < len(data):
        pkt_type = data[offset]
        if (pkt_type <= _packet.MQTT_PACKET_INVALID or
                pkt_type >= _packet.MQTT_PACKET_MAX):
            offset += 1
            continue
        consumed += PARSERS[pkt_type](data[consumed:], output)
        offset += consumed

    return consumed
