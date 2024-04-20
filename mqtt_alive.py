from paho.mqtt import client as mqtt
import subprocess
import threading
import time
import os

broker = '192.168.12.1'
port = 1883
topic = "#"
active_clients = {}
dead_clients = {}
lock = threading.Lock()


def run_arp_scan(dev):
    command = ['sudo', 'arp-scan', '--localnet', f'--interface={dev}']
    result = subprocess.run(command, capture_output=True, text=True)

    lines = result.stdout.split('\n')
    start_index = -1
    end_index = -1

    for index, line in enumerate(lines):
        if line.startswith('Starting arp-scan'):
            start_index = index
        elif line.endswith('packets dropped by kernel'):
            end_index = index
            break

    macs = lines[start_index+1:end_index-1] if start_index != -1 and end_index != -1 else []
    out = {}
    for m in macs:
        row = m.split('\t')
        out[row[0]] = row[1] # IP, MAC

    return out


def run_get_ips(dev):
    # NB! IoTempower must be active
    command = ['get_ips']
    result = subprocess.run(command, capture_output=True, text=True)
    lines = result.stdout.split('\n')

    macs = run_arp_scan(dev)
    out = {}
    for line in lines[1:]:
        if not line: 
            continue
        line = line.split(': ')
        ip = line[1]
        name = line[0]
        if ip in macs.keys():
            out[name] = [ip, macs[ip]]
        else:
            print('IP mismatch:', ip)

    return out
    

def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to IoTempower MQTT broker" if reason_code == 0 else f"Failed to connect, return code {reason_code}\n")
    client.subscribe(topic)


def on_message(client, userdata, message):
    client_id = str(message.topic).split('/')[0] 
    with lock:
        if not client_id == 'iotempower':
            active_clients[client_id] = time.time()
            if client_id in dead_clients.keys():
                del dead_clients[client_id]


def prune_active_clients():
    while True:
        time.sleep(10)
        current_time = time.time()
        with lock:
            for k, v in active_clients.items():
                if (current_time - v) > 15:
                    dead_clients[k] = current_time
                    del active_clients[k]

        lookup = run_get_ips('wlan0')
                
        os.system('clear')
        print(f"Active clients: {len(active_clients)}")
        for k in active_clients.keys():
            if k in lookup.keys():
                print(f'{k}:\t{lookup[k][0]}\t{lookup[k][1]}')
            else:
                print(f'{k}:\t==IP lookup failed==')
            
        print('\n')

        print(f'Dead clients: {len(dead_clients)}')
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
