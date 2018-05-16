"""
Copyright 2018 Jason Litzinger
See LICENSE for details.
"""
import binascii
import json
import pytest

from mqttpacket.v311 import _parsing, _packet
from mqttpacket.v311 import MQTTParseError

def test_parse_publish_simple():
    """
    A simple publish with QoS of 0 is successfully parsed.
    """
    data = bytearray()
    data.extend(
        binascii.unhexlify(b'31150004746573747b2274657374223a2274657374227d')
    )
    msgs = []
    c = _parsing.parse(data, msgs)
    assert len(data) == c
    assert len(msgs) == 1
    payload = msgs[0].payload.decode('utf-8')
    res = json.loads(payload)
    assert res == {"test": "test"}
    assert msgs[0].packetid is None
    assert msgs[0].topic == u'test'
    assert msgs[0].pkt_type == _packet.MQTT_PACKET_PUBLISH


def test_parse_publish_in_pieces():
    """
    A publish received in chunks is not successfully parsed until all
    data received.
    """
    data = bytearray()
    data.extend(
        binascii.unhexlify(b'31150004746573747b2274657374223a2274657374227d')
    )
    msgs = []

    assert _parsing.parse(data[:len(data)-1], msgs) == 0
    assert not msgs


def test_parse_suback():
    """
    A suback for a single successful subscribe is successfully parsed
    to a single MQTTPacket and all bytes are consumed.
    """
    data = bytearray()
    data.extend(
        binascii.unhexlify(b'9003000100')
    )
    msgs = []
    c = _parsing.parse(data, msgs)
    assert len(data) == c
    assert len(msgs) == 1
    assert msgs[0].packet_id == 1
    assert msgs[0].return_codes == [0]
    assert msgs[0].pkt_type == _packet.MQTT_PACKET_SUBACK


def test_parse_connack():
    """
    A CONNACK for a successful connect is successfuly parsed.
    """
    data = bytearray()
    data.extend(
        binascii.unhexlify(b'20020000')
    )
    msgs = []
    c = _parsing.parse(data, msgs)
    assert len(data) == c
    assert msgs[0].return_code == 0
    assert msgs[0].session_present == 0
    assert msgs[0].pkt_type == _packet.MQTT_PACKET_CONNACK


@pytest.fixture(scope='function')
def capture_len():
    rem_len = []

    def _capture(data, remaining_length, _offset, _output):
        rem_len.append(remaining_length)
        return len(data)

    old = _parsing.PARSERS[_packet.MQTT_PACKET_PUBLISH]
    _parsing.PARSERS[_packet.MQTT_PACKET_PUBLISH] = _capture
    yield rem_len
    _parsing.PARSERS[_packet.MQTT_PACKET_PUBLISH] = old


def test_parse_single_byte_remaining_length(capture_len):
    """
    A single byte remaining length is properly parsed.
    """
    print(capture_len)
    data = bytearray()
    data.extend(
        binascii.unhexlify(b'31150004746573747b2274657374223a2274657374227d')
    )
    msgs = []
    _parsing.parse(data, msgs)
    assert capture_len[0] == 0x15


def test_parse_only_fixed_header(capture_len):
    """
    A single byte remaining length is properly parsed even it 
    """
    data = bytearray()
    data.extend(
        binascii.unhexlify(b'3000')
    )
    msgs = []
    _parsing.parse(data, msgs)
    assert capture_len[0] == 0

def test_parse_two_byte(capture_len):
    """
    A two byte encoded remaining length is properly parsed.
    """
    data = bytearray()
    data.extend(
        binascii.unhexlify(b'30ff7f1a')
    )
    msgs = []
    _parsing.parse(data, msgs)
    assert capture_len[0] == 16383

    data = bytearray()
    data.extend(
        binascii.unhexlify(b'3080011a')
    )
    msgs = []
    _parsing.parse(data, msgs)
    assert capture_len[1] == 128

def test_parse_three_byte(capture_len):
    """
    A three byte encoded remaining length is properly parsed.
    """
    data = bytearray()
    data.extend(
        binascii.unhexlify(b'30ffff7f1a')
    )
    msgs = []
    _parsing.parse(data, msgs)
    assert capture_len[0] == 2097151

def test_parse_four_byte(capture_len):
    """
    A four byte encoded remaining length is properly parsed.
    """
    data = bytearray()
    data.extend(
        binascii.unhexlify(b'30ffffff7f1a')
    )
    msgs = []
    _parsing.parse(data, msgs)
    assert capture_len[0] == 268435455


def test_parse_five_byte(capture_len):
    """
    A five byte encoded remaining length is considered an error.
    """
    data = bytearray()
    data.extend(
        binascii.unhexlify(b'30ffffffff7f')
    )
    msgs = []
    with pytest.raises(MQTTParseError):
        _parsing.parse(data, msgs)
