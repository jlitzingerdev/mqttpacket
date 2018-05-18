"""
Copyright 2018 Jason Litzinger
See LICENSE for details
"""
import attr


MQTT_PACKET_INVALID = 0
MQTT_PACKET_CONNECT = 1
MQTT_PACKET_CONNACK = 2
MQTT_PACKET_PUBLISH = 3
MQTT_PACKET_PUBACK = 4
MQTT_PACKET_PUBREC = 5
MQTT_PACKET_PUBREL = 6
MQTT_PACKET_PUBCOMP = 7
MQTT_PACKET_SUBSCRIBE = 8
MQTT_PACKET_SUBACK = 9
MQTT_PACKET_UNSUBSCRIBE = 10
MQTT_PACKET_UNSUBACK = 11
MQTT_PACKET_PINGREQ = 12
MQTT_PACKET_PINGRESP = 13
MQTT_PACKET_DISCONNECT = 14
MQTT_PACKET_MAX = MQTT_PACKET_DISCONNECT + 1

PROTOCOL_LEVEL = 4 # MQTT 3.1.1


@attr.s
class ConnackPacket(object):
    """Parsed CONNACK packet

    :ivar return_code: Return code from the connect operation.

    :ivar session_present: Whether stored session state exists.

    :ivar pkt_type: MQTT_PACKET_CONNACK
    """
    return_code = attr.ib()
    session_present = attr.ib()
    pkt_type = attr.ib(default=MQTT_PACKET_CONNACK)


@attr.s
class SubackPacket(object):
    """Parsed SUBACK packet

    """
    packet_id = attr.ib()
    return_codes = attr.ib()
    pkt_type = attr.ib(default=MQTT_PACKET_SUBACK)


@attr.s(slots=True)
class PublishPacket(object):
    """
    Packet representing an incoming publish message.
    """
    dup = attr.ib()
    qos = attr.ib(
        validator=attr.validators.in_(VALID_QOS)
    )
    retain = attr.ib()
    topic = attr.ib()
    packetid = attr.ib()
    payload = attr.ib()
    pkt_type = attr.ib(default=MQTT_PACKET_PUBLISH)
