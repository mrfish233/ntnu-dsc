# The following example is derived from
# the official example at https://pypi.org/project/paho-mqtt/
import paho.mqtt.client as mqtt
import ssl
import struct
import time

to_client = "cli"
to_server = "srv"

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

client.connect("127.0.0.1", 1883, 60)

# Initiate a dedicated thread of execution for network activities
client.loop_start()
time.sleep(0.5)

while True:
    print("Type your message: ", end='')
    msg = input()
    client.publish(to_server, msg, 0)

client.loop_stop() # Will not arrive here if we kill the program manually
