# The following example is derived from
# the official example at https://pypi.org/project/paho-mqtt/
import paho.mqtt.client as mqtt
import ssl
import struct
import time

to_client = "123a"
to_server = "b123"

def on_connect(client, userdata, flags, rc, properties):
    print("Connected to the broker.")
    client.subscribe(to_client, 0)

def on_message(client, userdata, msg):
    message = str(msg.payload, encoding='utf8')
    s = message
    print("\r"+s.rjust(60) + "\nType your message: ", end='')

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,"")
client.on_connect = on_connect
client.on_message = on_message

# client.username_pw_set("your group username", "your group passwd")
# client.connect("140.122.185.98", 1883, 60)
client.connect("localhost", 1883, 60)

# Initiate a dedicated thread of execution for network activities
client.loop_start()
time.sleep(1)
while True:
    print("Type your message: ", end='')
    msg = input()
    client.publish(to_server, msg, 0)
client.loop_stop() # Will not arrive here if we kill the program manually
