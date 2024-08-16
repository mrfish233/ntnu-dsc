import paho.mqtt.client as mqtt
import ssl
import struct
import time

def on_connect(client, userdata, flags, rc, properties):
    print("Connected with result code = "+str(rc))

def on_message(client, userdata, msg):
    print(str(msg.payload, encoding='utf8'))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "")
client.on_connect = on_connect
client.on_message = on_message

# client.username_pw_set("your group username", "your group passwd")
# client.connect("140.122.185.98", 1883, 60)
client.connect("localhost", 1883, 60)

client.loop_start()
time.sleep(1)
print("Enter topic-to-subscribe: ", end='')
tp_sub = input()
client.subscribe(tp_sub, 0)
print("Enter topic-to-publish: ", end='')
tp_pub = input()
while True:
    msg = input()
    client.publish(tp_pub, msg, 0)
client.loop_stop()
