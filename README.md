This is a library for serializing and parsing MQTT packets.  It is intentionally transport agnostic, in the hopes that it is useful in building new libraries on "fancy-framework" without having to re-implement MQTT.

The original motivation was to write a native Twisted protocol for use with AWS IoT, specifically using ALPN on 443.  I quickly discovered that most existing MQTT code embedded the building/parsing into their libraries, keeping it coupled to the framework.  While this is a reasonable choice, I preferred keeping the two separate.

AS OF NOW, THIS IS PRE-ALPHA AND YOU SHOULD NOT USE IT.
