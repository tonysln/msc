#!/usr/bin/python3

# Anton Slavin
# 2024

import subprocess
import socket
from tabulate import tabulate
from sys import argv, exit
import os

try:
    device = argv[1]
except:
    device = "wlap0"

print('Device:', device)

result = subprocess.run(['iw', 'dev', device, 'station', 'dump'], stdout=subprocess.PIPE)
res_list = result.stdout.decode().split('Station ')

c = 0
headers = ['#', 'MAC', 'Tx Failed', 'Tx Bitrate', 'Rx Bitrate', 'Authr', 'Authc', 'Assoc', 'Con Time']
table = []
for item in res_list:
    if not item:
        continue
    
    item_s = item.split('\n\t')
    mac = item_s[0].split(' ')[0]
    row = [c+1, mac]
    
    for i in item_s:
        for w in ['authenticated', 'associated', 'connected time', 'tx failed', \
                  'tx bitrate', 'rx bitrate', 'authorized']:
            if w in i:
                row.append(i.split('\t')[1])
    
    table.append(row)
    c += 1
    
#os.system('clear')
print(tabulate(table, headers=headers, tablefmt="psql"))
print('Connected clients:', c)
