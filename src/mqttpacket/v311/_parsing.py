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

def parse_remaining_len(data):
    """Parse remaining length field from data"""
    #TODO can be variable
    return data[1], 1


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
        raise _errors.MQTTMoreDataNeededError("CONNACK needs more data")

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


def parse_pingresp(data, _):
    """
    Parse a PINGRESP, consume and discard.
    """
    if len(data) >= 2:
        return 2
    return 0


@attr.s
class SubackResponse(object):
    """
    Payload for SUBACK packets.
    """
    packet_id = attr.ib()
    return_codes = attr.ib()

def parse_suback(data, output):
    """
    Parse a SUBACK packet.

    :param data: The data to parse.

    :param output: List of output packets.

    """

    remaining_len, consumed = parse_remaining_len(data)
    offset = 1 + consumed
    total_size = remaining_len + offset

    if len(data) != total_size:
        raise _errors.MQTTMoreDataNeededError("CONNACK needs more data")

    packet_id = (data[offset] << 8) | data[offset+1]
    offset += 2
    output.append(
        _packet.MQTTPacket(
            _packet.MQTT_PACKET_SUBACK,
            SubackResponse(
                packet_id,
                [rc for rc in data[offset:total_size]]
            )
        )
    )
    return total_size


@attr.s(slots=True)
class PublishPacket(object):
    """
    Packet representing an incoming publish message.
    """
    topic = attr.ib()
    packetid = attr.ib()
    payload = attr.ib()


def parse_publish(data, output):
    """Parse a PUBLISH packet.

    :param data: Incoming data to parse.
    :type data: bytearray

    :param output: List of result messages
    :type output: [mqttpacket.v311.MQTTPacket]

    :returns: number of bytes consumed.

    """
    flags = data[0] & 0x0F
    qos = (flags & 0x06) >> 1

    remaining_len, consumed = parse_remaining_len(data)
    offset = 1 + consumed
    total_len = remaining_len + offset

    print(total_len)
    if len(data) != total_len:
        raise _errors.MQTTMoreDataNeededError("PUBLISH needs more data")

    topic_len = (data[offset] << 8) | data[offset+1]
    offset += 2
    topic = data[offset:offset+topic_len].decode('utf-8')
    # Check for wildcard chars
    offset += topic_len
    packetid = None
    if qos:
        packetid = (data[offset] << 8) | data[offset+1]
        offset += 2

    pp = PublishPacket(topic, packetid, data[offset:])
    output.append(
        _packet.MQTTPacket(
            _packet.MQTT_PACKET_PUBLISH,
            pp
        )
    )
    return remaining_len + 2


def _null_parse(data, output):
    return len(data)


PARSERS = {
    _packet.MQTT_PACKET_CONNECT: _null_parse,
    _packet.MQTT_PACKET_CONNACK: parse_connack,
    _packet.MQTT_PACKET_PUBLISH: parse_publish,
    _packet.MQTT_PACKET_PUBACK: _null_parse,
    _packet.MQTT_PACKET_PUBREC: _null_parse,
    _packet.MQTT_PACKET_PUBREL: _null_parse,
    _packet.MQTT_PACKET_PUBCOMP: _null_parse,
    _packet.MQTT_PACKET_SUBSCRIBE: _null_parse,
    _packet.MQTT_PACKET_SUBACK: parse_suback,
    _packet.MQTT_PACKET_UNSUBSCRIBE: _null_parse,
    _packet.MQTT_PACKET_UNSUBACK: _null_parse,
    _packet.MQTT_PACKET_PINGREQ: _null_parse,
    _packet.MQTT_PACKET_PINGRESP: parse_pingresp,
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
        pkt_type = data[offset] >> 4
        try:
            consumed += PARSERS[pkt_type](data[offset:], output)
        except KeyError:
            offset += 1
        except _errors.MQTTMoreDataNeededError:
            return consumed
        else:
            offset += consumed

    return consumed
