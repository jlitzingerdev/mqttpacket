"""
Copyright 2018 Jason Litzinger
See LICENSE for details.
"""
import struct

import attr

from . import _packet

_CONNECT_REMAINING_LENGTH = 10

PROTOCOL_NAME = 'MQTT'.encode('utf-8')


@attr.s
class ConnectSpec(object):
    """
    Data class for connection related options.
    """
    username = attr.ib(default=None)
    password = attr.ib(default=None)
    will_topic = attr.ib(default=None)
    will_message = attr.ib(default=None)

    def remaining_length(self):
        """Return the length of the connect options."""
        rem_len = 0
        if self.username:
            rem_len += 2
            rem_len += len(self.username)
        elif self.password:
            rem_len += 2
            rem_len += len(self.password)
        elif self.will_topic:
            rem_len += 2
            rem_len += len(self.will_topic)
        elif self.will_message:
            rem_len += 2
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
        0x04,
        0x02,
        keepalive,
        len(client_id)
    )

    parts = [msg, client_id]
    if connect_spec is not None:
        parts.append(connect_spec.payload())

    msg = b''.join(parts)
    #TODO: Will Topic, Will Message, User Name, Password
    return msg
