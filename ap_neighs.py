from sys import argv, exit
import subprocess
import os

"""
AP connected clients viewer

Anton Slavin
2024
"""

def run_iw_scan(dev):
    result = subprocess.run(['iw', 'dev', dev, 'station', 'dump'], stdout=subprocess.PIPE)
    res_list = result.stdout.decode().split('Station ')

    c = 0
    for item in res_list:
        if not item:
            continue

        item_s = item.split('\n\t')
        mac = item_s[0].split(' ')[0]
        print(c+1, mac)
        c += 1

    return c


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
    for i,m in enumerate(macs):
        row = m.split('\t')
        print(f'{i+1})\t{row[0]}\t{row[1]}')

    return len(macs)


def run_mqtt_count(dev, addr):
    return 0


if __name__ == '__main__':
    device = 'wlan0'
    type = 'iw'

    if '-dev' in argv:
        device = argv[argv.index('-dev')+1]
    if '-type' in argv:
        type = argv[argv.index('-type')+1]
    if '-cls' in argv:
        os.system('clear')

    print('Device:', device)

    c = -1
    if type == 'arp':
        c = run_arp_scan(device)
    elif type == 'iw':
        c = run_iw_scan(device)
    elif type == 'mqtt':
        c = run_mqtt_count(device, '192.168.12.4')
    else:
        print('[!] Unknown type specified:', type)
        exit(1)

    # TODO: reading /tmp/dhcp.leases
