import paho.mqtt.client as mqtt
import ssl
import struct
import time
import random

magic_number = 0
to_client = "123a"
to_server = "b123"

def on_connect(client, userdata, flags, rc, properties):
    print("Connected to the broker.")

def on_message(client, userdata, msg):
    payload_string = str(msg.payload, encoding='utf8')
    time.sleep(1)
    global magic_number
    match payload_string:
        case "menu":
            client.publish(to_client, "\
                --- menu ---\n\
                0: Get the server local time\n\
                1: Show the current value of the magic number\n\
                2: Increment the magic number by one", 0)
        case "0":
            client.publish(to_client, time.strftime("%a, %d %b %Y %H:%M:%S %z", time.localtime(time.time())))
        case "1":
            client.publish(to_client, str(magic_number))
        case "2":
            magic_number += 1
        case _:
            client.publish(to_client, "Unknown request. Try 'menu'.", 0)

print("This runs a stateful broker.")

random.seed()
magic_number = random.randint(7,100)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,"")
client.on_connect = on_connect
client.on_message = on_message

# client.username_pw_set("your group username", "your group password")
# client.connect("140.122.185.98", 1883, 60)
client.connect("localhost", 1883, 60)

client.subscribe(to_server, 0)
client.loop_forever()
