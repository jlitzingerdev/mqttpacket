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


@attr.s(slots=True)
class MQTTPacket(object):
    """
    A packet received from the MQTT broker.  It has
    a type and an opaque payload that is specific to
    the packet type.

    :ivar pkt_type: The type of the packet

    :ivar payload: An opaque payload specific to the packet type.

    """
    pkt_type = attr.ib()
    payload = attr.ib()
