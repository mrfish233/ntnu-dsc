import paho.mqtt.client as mqtt
import ssl
import struct
import time
import random

magic_list = []

to_client = "cli"
to_server = "srv"

def on_connect(client, userdata, flags, rc, properties):
    print("Connected to the broker.")

def on_message(client, userdata, msg):
    payload_string = str(msg.payload, encoding='utf8')
    time.sleep(0.5)
    global magic_list
    match payload_string:
        case "menu":
            client.publish(to_client, "\
                --- menu ---\n\
                0: Get the server local time\n\
                1: Show the current magic list\n\
                2: Append a magic number to magic list", 0)
        case "0":
            client.publish(to_client, time.strftime("%a, %d %b %Y %H:%M:%S %z", time.localtime(time.time())))
        case "1":
            lists = 'Lists: ' + ' '.join(magic_list)

            print(lists)
            client.publish(to_client, lists)
        case "2":
            magic_number = random.randint(1, 100)
            magic_list.append(str(magic_number))

            print(f"Magic number to append: {magic_number}")
            client.publish(to_client, "A magic number was appended.")
        case _:
            client.publish(to_client, "Unknown request. Try 'menu'.", 0)

print("This runs a stateful broker.")

random.seed()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,"")
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set("team3", "asdfghjkl")
client.connect("127.0.0.1", 1883, 60)
client.subscribe(to_server, 0)
client.loop_forever()
