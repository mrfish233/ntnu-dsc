import paho.mqtt.client as mqtt
import ssl
import struct
import time

import route

to_client = "cli"
to_server = "srv"

# Route flag, check if it is finding a route
route_state = False

# Storing coordinates
start_coords = None
end_coords = None
weight_tolerance = -1

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Connected to the broker.")
    else:
        print(f"Bad connection, returned code: {rc}")

def on_message(client, userdata, msg):
    payload_str = str(msg.payload, encoding='utf8')

    time.sleep(0.5)

    global route_state
    global start_coords
    global end_coords
    global weight_tolerance

    # If route flag is True
    if route_state:
        # Save into start coordinates and end coordinates
        if start_coords is None:
            start_coords = route.get_coordinates(payload_str)

            if (start_coords is None):
                client.publish(to_client, "Can't find location, please try again.", 0)
            else:
                client.publish(to_client, "Please input end location.", 0)
        elif end_coords is None:
            end_coords = route.get_coordinates(payload_str)

            if (end_coords is None):
                client.publish(to_client, "Can't find location, please try again.", 0)
            else:
                client.publish(to_client, "Please input weight tolerance (1-10).", 0)
        elif weight_tolerance == -1:
            try:
                weight_tolerance = int(payload_str)

                if (weight_tolerance < 1 or weight_tolerance > 10):
                    raise Exception("Invalid input")
            except:
                client.publish(to_client, "Invalid input, please try again.", 0)

        # Find route when both coordinates are generated
        if (start_coords is not None and end_coords is not None and weight_tolerance != -1):
            client.publish(to_client, "Finding best route, please wait.", 0)

            link = route.generate_route(start_coords, end_coords, weight_tolerance)

            if (link is None):
                client.publish(to_client, "Can't find a route. Please try again.", 0)
            else:
                client.publish(to_client, f"Route found, link: {link}", 0)

            # Reset coordinates and state
            start_coords = None
            end_coords = None
            route_state = False
            weight_tolerance = -1

        return

    match payload_str:
        case "menu":
            client.publish(to_client, "\
                --- menu ---\n\
                0: Get the server local time\n\
                1: Find the commute route", 0)
        case "0":
            client.publish(to_client, time.strftime("%a, %d %b %Y %H:%M:%S %z", time.localtime(time.time())))
        case "1":
            # Toggle state flag
            route_state = True
            client.publish(to_client, "Please input start location.", 0)
        case _:
            client.publish(to_client, "Unknown request. Try 'menu'.", 0)

print("This runs a stateful broker.")

route.init()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,"")
client.on_connect = on_connect
client.on_message = on_message

client.connect("127.0.0.1", 1883, 60)
client.subscribe(to_server, 0)
client.loop_forever()
