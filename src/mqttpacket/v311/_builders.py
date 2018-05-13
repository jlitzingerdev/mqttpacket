"""
Copyright 2018 Jason Litzinger
See LICENSE for details.
"""
import struct

import attr
import six

from . import _packet

_CONNECT_REMAINING_LENGTH = 10

PROTOCOL_NAME = 'MQTT'.encode('utf-8')

def _check_none_or_text(_instance, attribute, value):
    if value is not None and not isinstance(value, six.text_type):
        raise TypeError('{} must be None or text'.format(attribute))

def _check_will_message(instance, _attribute, value):
    if value is not None and instance.will_topic is None:
        raise ValueError('Will topic must be set with will message')

def _check_will_topic(instance, _attribute, value):
    if value is not None and instance.will_message is None:
        raise ValueError('Will message must be set with will topic')

def _check_password(instance, _attribute, value):
    if value is not None and instance.username is None:
        raise ValueError('Password requires username.')

def _check_will_qos(instance, _attribute, value):
    if value != 0x00 and instance.will_topic is None:
        raise ValueError('Will QOS requires topic/message')

@attr.s
class ConnectSpec(object):
    """
    Data class for connection related options.
    """
    username = attr.ib(
        default=None,
        validator=_check_none_or_text,
    )
    password = attr.ib(
        default=None,
        validator=[
            _check_none_or_text,
            _check_password,
        ],
    )
    will_topic = attr.ib(
        default=None,
        validator=[
            _check_none_or_text,
            _check_will_topic
        ],
    )
    will_message = attr.ib(
        default=None,
        validator=[
            _check_none_or_text,
            _check_will_message
        ]
    )
    will_qos = attr.ib(
        default=0x00,
        validator=[
            attr.validators.in_((0x00, 0x01, 0x02)),
            _check_will_qos,
        ]
    )

    def flags(self):
        """Get the flags for this connect spec."""
        flags = 0x02

        if self.will_topic:
            flags |= 0x04
            flags |= (self.will_qos << 3)

        if self.username:
            flags |= 0x80

        if self.password:
            flags |= 0x40

        return flags

    def remaining_length(self):
        """Return the length of the connect options."""
        rem_len = 0
        if self.username:
            rem_len += 2
            rem_len += len(self.username)

        if self.password:
            rem_len += 2
            rem_len += len(self.password)

        if self.will_topic:
            rem_len += 4
            rem_len += len(self.will_topic)
            rem_len += len(self.will_message)

        return rem_len


def connect(client_id, keepalive=60, connect_spec=None):
    """Create a CONNECT packet

    :param client_id: The id of the client.
    :type client_id: unicode

    :param keepalive (optional): How long to keep the network alive, default
        60s.
    :type keepalive: int

    :param connect_spec (optional): The spec for this connection or None
    :type connect_spec: mqttpacket.ConnectSpec

    :returns: A connect packet.
    :rtype: bytes

    """
    client_id = client_id.encode('utf-8')
    # TODO: Remaining len can be multibyte
    remaining_length = _CONNECT_REMAINING_LENGTH

    if client_id:
        remaining_length += len(client_id) + 2

    if connect_spec is not None:
        remaining_length += connect_spec.remaining_length()

    msg = struct.pack(
        "!BBH4sBBHH",
        (_packet.MQTT_PACKET_CONNECT << 4),
        remaining_length,
        0x0004,
        PROTOCOL_NAME,
        _packet.PROTOCOL_LEVEL,
        0x02,
        keepalive,
        len(client_id)
    )

    parts = [msg, client_id]
    if connect_spec is not None:
        parts.append(connect_spec.payload())

    msg = b''.join(parts)
    return msg


def pingreq():
    """
    Create a PINGREQ packet.
    """
    return struct.pack(
        '!BB',
        (_packet.MQTT_PACKET_PINGREQ << 4),
        0
    )


def _validate_qos(_instance, _attribute, value):
    if not 0 <= value < 3:
        raise ValueError('qos must be 0 <= qos < 3')


@attr.s(slots=True)
class SubscriptionSpec(object):
    """
    A data class for a topicfilter qos pair.
    """
    topicfilter = attr.ib(
        validator=attr.validators.instance_of(six.text_type),
    )

    qos = attr.ib(
        validator=_validate_qos,
    )

    def remaining_len(self):
        """
        Length for this spec.
        """
        return 3 + len(self.topicfilter)

    def to_bytes(self):
        """Encode this spec as bytes"""
        return b''.join([
            struct.pack('!H', len(self.topicfilter)),
            self.topicfilter.encode('utf-8'),
            struct.pack('!B', self.qos)
        ])


def subscribe(packetid, topicspecs):
    """Create a subscribe packet.

    :param topicfilter: The list of topicfilter specs.

    :param qos: The QoS level to use.

    """
    if not 0 < packetid < 65535:
        raise ValueError('Packetid must be 0 < packetid < 65535')

    remaining_len = 2
    for spec in topicspecs:
        remaining_len += spec.remaining_len()

    # TODO: Remaining len can be multibyte
    msg = struct.pack(
        '!BBH',
        (_packet.MQTT_PACKET_SUBSCRIBE << 4) | 0x02,
        remaining_len,
        packetid
    )

    encoded_specs = [msg]
    encoded_specs.extend(
        [s.to_bytes() for s in topicspecs]
    )

    msg = b''.join(encoded_specs)

    return msg
