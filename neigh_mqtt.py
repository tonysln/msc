import time
import paho.mqtt.client as mqtt


# Define MQTT broker and topic
broker_address = "192.168.12.1"
topic = "keep_alive"

# Callback function to be called when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print("Connection failed with result code " + str(rc))

# Create an MQTT client
client = mqtt.Client()

# Set the callback function
client.on_connect = on_connect

# Connect to the broker
client.connect(broker_address)

# Loop to keep the script running
while True:
    # Check if the client is still connected
    if not client.is_connected():
        print("MQTT client is not connected. Reconnecting...")
        client.reconnect()

    # Publish a test message to the topic
    client.publish(topic, "ping")

    # Wait for a while before checking the connection again
    time.sleep(10)

