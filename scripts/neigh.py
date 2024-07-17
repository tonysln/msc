#!/usr/bin/python3

import subprocess
import socket
from sys import argv, exit


def check_device_availability(device_ip, timeout=1):
    try:
        # Use a non-blocking socket to check the device's reachability
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect_ex((device_ip, 80))
            return True
    except (socket.timeout, socket.error):
        return False


try:
    device = argv[1]
except:
    device = "wlap0"

result = subprocess.run(['ip', 'neigh', 'show', 'dev', device, 'nud', 'reachable', 'nud', 'stale'], stdout=subprocess.PIPE)
outp = result.stdout.decode('utf-8').split('\n')
outp = list(filter(lambda el: len(el) > 0, outp))

print(f'Available: {len(outp)} device(s)')
print('Pinging...')
c = 0
for i,el in enumerate(outp):
    o = el.split()
    pout = int(subprocess.run(['ping', '-c', '2', o[0]], stdout=subprocess.PIPE).returncode)
    #pout = check_device_availability(o[0], timeout=5)
    status = 'OK' if not pout else 'FAIL'
    if status == 'OK':
        c += 1
    print(f'{str(i+1).rjust(2, "0")}   {str(o[0]).ljust(15, " ")}   {o[-2]}   {status}')

print(f'Alive: {c} device(s)')
