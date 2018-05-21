"""
Copyright 2018 Jason Litzinger
See LICENSE for details.

Various constants useful in parsing and serializing.  There should never
be imports in this module.
"""
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

VALID_QOS = (0x00, 0x01, 0x02)
PACKET_ID_LEN = 2
STRING_LENGTH_BYTES = 2
