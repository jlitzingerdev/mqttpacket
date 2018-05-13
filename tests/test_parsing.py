"""
Copyright 2018 Jason Litzinger
See LICENSE for details.
"""
import binascii
import json

from mqttpacket.v311 import _parsing

def test_parse_publish_simple():
    """
    A simple publish with QoS of 0 is successfully parsed.
    """
    data = bytearray()
    data.extend(
        binascii.unhexlify(b'31150004746573747b2274657374223a2274657374227d')
    )
    msgs = []
    c = _parsing.parse_publish(data, msgs)
    assert len(data) == c
    assert len(msgs) == 1
    payload = msgs[0].payload.payload.decode('utf-8')
    res = json.loads(payload)
    assert res == {"test": "test"}
    assert msgs[0].payload.packetid is None
    assert msgs[0].payload.topic == u'test'
