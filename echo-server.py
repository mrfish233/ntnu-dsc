import paho.mqtt.client as mqtt
import ssl
import struct
import time

to_client = "123a"
to_server = "b123"

def on_message(client, userdata, msg):
    payload_string = str(msg.payload, encoding='utf8')
    print("Received (topic '" + msg.topic + "'): " + payload_string)
    time.sleep(1)
    client.publish(to_client, "server: You typed '" + payload_string +"'", 0)

print("This runs a simple server to echo client string.")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,"")
client.on_message = on_message

# client.username_pw_set("your group username", "your group passwd")
# client.connect("140.122.185.98", 1883, 60)
client.connect("localhost", 1883, 60)

client.subscribe(to_server, 0)
client.loop_forever()
