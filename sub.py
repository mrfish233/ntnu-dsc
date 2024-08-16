# The following example is derived from
# the official example at https://pypi.org/project/paho-mqtt/
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    payload_string = str(msg.payload, encoding='utf8')
    print(payload_string)

print("A simple subscriber.")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,"")
client.on_message = on_message

# client.username_pw_set("your group username", "your group password")
# client.connect("140.122.185.98", 1883, 60)
client.connect("localhost", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
client.subscribe("example-topic", 0)
client.loop_forever()
