"""
Copyright 2018 Jason Litzinger
See LICENSE for details.
"""
import six
import pytest

import mqttpacket.v311 as mqttpacket


def test_connect_basic():
    """
    A connect packet with only a client id is properly constructed.
    """
    packet = mqttpacket.connect(u'Foobar')
    assert isinstance(packet, bytes)
    assert len(packet) == 20
    assert six.indexbytes(packet, 0) == 16
    assert six.indexbytes(packet, 9) == 0x02
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


def test_valid_will():
    """
    A valid will topic/message spec sets flags and payload.
    """
    cs = mqttpacket.ConnectSpec(
        will_topic=u'my_will_topic',
        will_message=u'my_will_message',
        will_qos=1,
    )

    wt = u'my_will_topic'
    wm = u'my_will_message'
    assert cs.will_topic == wt
    assert cs.will_message == wm
    assert cs.flags() == 0x0e
    assert cs.remaining_length() == (4 + len(wt) + len(wm))

    cs = mqttpacket.ConnectSpec(
        will_topic=u'wt2',
        will_message=u'wm2',
        will_qos=2,
    )

    assert cs.will_topic == u'wt2'
    assert cs.will_message == u'wm2'
    assert cs.flags() == 0x16


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


def test_build_subscription_multiple():
    """
    Multiple topic filters can be properly encoded.

    This example is from the MQTT specification.
    """
    specs = [
        mqttpacket.SubscriptionSpec(u'a/b', 0x01),
        mqttpacket.SubscriptionSpec(u'c/d', 0x02),
    ]
    packet = mqttpacket.subscribe(10, specs)
    assert isinstance(packet, bytes)
    assert six.indexbytes(packet, 0) == 0x82
    assert six.indexbytes(packet, 1) == 14
    assert six.indexbytes(packet, 2) << 8 | six.indexbytes(packet, 3) == 10
    assert six.indexbytes(packet, 4) << 8 | six.indexbytes(packet, 5) == 3
    assert packet[6:9].decode('utf-8') == u'a/b'
    assert six.indexbytes(packet, 9) == 0x01
    assert six.indexbytes(packet, 10) << 8 | six.indexbytes(packet, 11) == 3
    assert packet[12:15].decode('utf-8') == u'c/d'
    assert six.indexbytes(packet, 15) == 0x02


def test_build_subscription_single():
    """
    Multiple topic filters can be properly encoded.

    This example is from the MQTT specification.
    """
    specs = [
        mqttpacket.SubscriptionSpec(u'test/1', 0x00),
    ]
    packet = mqttpacket.subscribe(10, specs)
    assert isinstance(packet, bytes)
    assert six.indexbytes(packet, 0) == 0x82
    assert six.indexbytes(packet, 1) == 11
    assert six.indexbytes(packet, 2) << 8 | six.indexbytes(packet, 3) == 10
    assert six.indexbytes(packet, 4) << 8 | six.indexbytes(packet, 5) == 6
    assert packet[6:12].decode('utf-8') == u'test/1'
    assert six.indexbytes(packet, 12) == 0x00


def test_encode_single_byte_length():
    """
    A length < 128 is encoded in a single byte.
    """
    r = mqttpacket.encode_remainining_length(127)
    assert r == b'\x7f'
    r = mqttpacket.encode_remainining_length(0)
    assert r == b'\x00'


def test_encode_two_byte_length():
    """
    A length over 127 is encoded with two bytes.
    """
    r = mqttpacket.encode_remainining_length(128)
    assert r == b'\x80\x01'
    r = mqttpacket.encode_remainining_length(16383)
    assert r == b'\xff\x7f'


def test_encode_three_byte_length():
    """
    A length over 16383 is encoded with three bytes.
    """
    r = mqttpacket.encode_remainining_length(16384)
    assert r == b'\x80\x80\x01'
    r = mqttpacket.encode_remainining_length(2097151)
    assert r == b'\xff\xff\x7f'


def test_encode_four_byte_length():
    """
    A length over 2097151 is encoded with four bytes.
    """
    r = mqttpacket.encode_remainining_length(2097152)
    assert r == b'\x80\x80\x80\x01'
    r = mqttpacket.encode_remainining_length(268435455)
    assert r == b'\xff\xff\xff\x7f'
