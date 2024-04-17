from paho.mqtt import client as mqtt
import threading
import time
import os

broker = '192.168.12.1'
port = 1883
topic = "#"
active_clients = {}
dead_clients = {}
lock = threading.Lock()


def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to IoTempower MQTT broker" if reason_code == 0 else f"Failed to connect, return code {reason_code}\n")
    client.subscribe(topic)


def on_message(client, userdata, message):
    client_id = str(message.topic).split('/')[0] 
    with lock:
        if not client_id == 'iotempower':
            active_clients[client_id] = time.time()
            dead_clients.pop(key)


def prune_active_clients():
    while True:
        time.sleep(5)
        current_time = time.time()
        with lock:
            for k, v in active_clients.items():
                if (current_time - v) > 10:
                    dead_clients[key] = current_time
                    active_clients.pop(key)
                
        os.system('clear')
        for k in active_clients.keys():
            print(k)
            
        print(f"Active clients: {len(active_clients)}")

        print('Dead clients:')
        for k in dead_clients.keys():
            print(k)


def run():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    threading.Thread(target=prune_active_clients, daemon=True).start()
    client.loop_forever()


if __name__ == "__main__":
    run()
