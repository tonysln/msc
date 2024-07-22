#!/bin/bash


# NetworkManager AP setup with steps.
# Based on accesspoint-nm script in IoTempower, 
# adjusted for interactive use

nname=$1
npass=$2
baseip=$3
netmask=$4

# Call the iotempower script from bin/,
# iot env must be activated!
accesspoint-nm create --ssid $nname --password $npass --ip $baseip --netmask $netmask
