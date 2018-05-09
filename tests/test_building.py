"""
Copyright 2018 Jason Litzinger
See LICENSE for details.
"""
import pytest

import mqttpacket


def test_connect_basic():
    """
    A connect packet with only a client id is properly constructed.
    """
    packet = mqttpacket.connect(u'Foobar')
    assert isinstance(packet, bytes)
    assert len(packet) == 20
    assert packet[0] == 16
    assert packet[9] == 0x02
    assert packet[14:].decode('utf-8') == u'Foobar'


def test_will_requirements():
    """
    Will topic and will message must be set together.
    """
    with pytest.raises(ValueError):
        mqttpacket.ConnectSpec(
            will_topic=u'foo',
        )

    with pytest.raises(ValueError):
        mqttpacket.ConnectSpec(
            will_message=u'my message',
        )

    cs = mqttpacket.ConnectSpec(
        will_topic=u'my_will_topic',
        will_message=u'my_will_message'
    )

    assert cs.will_topic == u'my_will_topic'
    assert cs.will_message == u'my_will_message'


def test_default_spec():
    """
    A default spec has a remaining length of zero and
    a clean session.
    """
    cs = mqttpacket.ConnectSpec()
    assert cs.remaining_length() == 0
    assert cs.flags() == 0x02


def test_will_must_be_unicode():
    """
    Will topic and will message must be unicode.
    """
    with pytest.raises(TypeError):
        mqttpacket.ConnectSpec(
            will_topic=b'foo',
            will_message=u'bar'
        )

    with pytest.raises(TypeError):
        mqttpacket.ConnectSpec(
            will_topic=u'biz',
            will_message=b'baz'
        )

def test_will_qos_values():
    """
    Will QOS can only be 0 - 2
    """
    with pytest.raises(ValueError):
        mqttpacket.ConnectSpec(
            will_topic=u'biz',
            will_message=u'baz',
            will_qos=3
        )

    mqttpacket.ConnectSpec(
        will_topic=u'my_will_topic',
        will_message=u'my_will_message',
        will_qos=1
    )

    mqttpacket.ConnectSpec(
        will_topic=u'my_will_topic',
        will_message=u'my_will_message',
        will_qos=2
    )
