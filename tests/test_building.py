"""
Copyright 2018 Jason Litzinger
See LICENSE for details.
"""
import mqttpacket


def test_connect_basic():
    """
    A connect packet with only a client id is properly constructed.
    """
    packet = mqttpacket.connect(u'Foobar')
    assert isinstance(packet, bytes)
    assert len(packet) == 20
    assert packet[0] == 16
    assert packet[14:].decode('utf-8') == u'Foobar'
