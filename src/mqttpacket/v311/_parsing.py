"""
Copyright 2018 Jason Litzinger
See LICENSE for details.


Parsers should return the total length consumed, which should
include all headers (Fixed, variable, and payload).

"""
from __future__ import absolute_import

from . import _packet, _errors

def parse_connack(data, remaining_length, variable_begin, output):
    """Parse a CONNACK packet.

    :param data: Data to parse
    :type data: bytebuffer

    :param variable_begin: Offset of start of variable length header

    :raises: MQTTParseError if packet is malformed
    :returns: length consumed, return code and session_present flag from the
        CONNACK packet.

    :rtype: int

    """
    if len(data) != 4:
        raise _errors.MQTTMoreDataNeededError("CONNACK needs more data")

    if remaining_length != 2:
        raise _errors.MQTTParseError("Remaining length invalid")

    ack_flags = data[variable_begin]
    rc = data[variable_begin+1]

    if (ack_flags & 0xFE) != 0:
        raise _errors.MQTTParseError("Reserved bits not clear")

    output.append(
        _packet.ConnectResponse(
            _packet.MQTT_PACKET_CONNACK,
            rc,
            ack_flags
        )
    )

    return 4


def parse_pingresp(data, _remaining_length, _offset, _output):
    """
    Parse a PINGRESP, consume and discard.
    """
    if len(data) >= 2:
        return 2
    return 0




def parse_suback(data, remaining_length, variable_begin, output):
    """
    Parse a SUBACK packet.

    :param data: The data to parse.
    :param remaining_length: Remaining length field parsed
        from the packet.

    :param variable_begin: Offset of start of variable length header

    :param output: List of output packets.

    """

    total_size = remaining_length + variable_begin
    if len(data) != total_size:
        raise _errors.MQTTMoreDataNeededError("CONNACK needs more data")

    packet_id = (data[variable_begin] << 8) | data[variable_begin+1]
    variable_begin += 2
    output.append(
        _packet.SubackResponse(
            _packet.MQTT_PACKET_SUBACK,
            packet_id,
            [rc for rc in data[variable_begin:total_size]]
        )
    )
    return total_size


def parse_publish(data, remaining_length, variable_begin, output):
    """Parse a PUBLISH packet.

    :param data: Incoming data to parse.
    :type data: bytearray

    :param variable_begin: Offset of start of variable length header

    :param output: List of result messages
    :type output: [mqttpacket.v311.PublishPacket]

    :returns: number of bytes consumed.

    """
    flags = data[0] & 0x0F
    qos = (flags & 0x06) >> 1

    total_len = remaining_length + variable_begin

    if len(data) != total_len:
        raise _errors.MQTTMoreDataNeededError("PUBLISH needs more data")

    topic_len = (data[variable_begin] << 8) | data[variable_begin+1]
    variable_begin += 2
    topic = data[variable_begin:variable_begin+topic_len].decode('utf-8')
    # Check for wildcard chars
    variable_begin += topic_len
    packetid = None
    if qos:
        packetid = (data[variable_begin] << 8) | data[variable_begin+1]
        variable_begin += 2

    output.append(
        _packet.PublishPacket(
            _packet.MQTT_PACKET_PUBLISH,
            topic,
            packetid,
            data[variable_begin:]
        )
    )

    return total_len


def _null_parse(data, _remaining_length, _offset, _output):
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


_MAX_MULTIPLIER = 128 * 128 * 128
_MULTIPLIERS = (1, 128, 128, 128)

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
        variable_begin = offset + 1
        remaining_length = 0
        parsing_len = True
        nb = 0
        while parsing_len:
            remaining_length += (data[variable_begin] & 127) * _MULTIPLIERS[nb]
            nb += 1
            parsing_len = (variable_begin < len(data)
                           and (nb < 4)
                           and ((data[variable_begin] & 128) != 0))
            variable_begin += 1

        if nb == 4:
            raise _errors.MQTTParseError("Invalid remaining length")

        try:
            consumed += PARSERS[pkt_type](
                data[offset:],
                remaining_length,
                variable_begin,
                output
            )
        except KeyError:
            offset += 1
        except _errors.MQTTMoreDataNeededError:
            return consumed
        else:
            offset += consumed

    return consumed
