import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Connected OK")
    else:
        print(f"Bad connection, returned code: {rc}")

def on_message(client, userdata, msg):
    time.sleep(0.5)

    payload_string = str(msg.payload, encoding='utf8')
    print(f"{msg.topic}: {payload_string}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "")
client.on_connect = on_connect
client.on_message = on_message

# client.username_pw_set("wildcard", "")
client.connect("test.mosquitto.org")

client.subscribe("#", 0)
client.loop_forever()
