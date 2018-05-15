"""
Copyright 2018 Jason Litzinger
See LICENSE for details.
"""
import binascii
import json

from mqttpacket.v311 import _parsing, _packet

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
