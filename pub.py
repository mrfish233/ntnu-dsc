# The following example is derived from
# the official example at https://pypi.org/project/paho-mqtt/
import paho.mqtt.client as mqtt
import sys

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,"")

# client.username_pw_set("your group username", "your group password")
# client.connect("140.122.185.98", 1883, 60)
client.connect("localhost", 1883, 60)

msg = sys.argv[1]
client.publish("example-topic", msg, 0)
print("Publishing message '" + msg + "'")
