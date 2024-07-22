#!/bin/bash


# hostapd AP setup with steps.
# Based on accesspoint script in IoTempower, 
# adjusted for interactive use

nname=$1
npass=$2
baseip=$3

export IOTEMPOWER_AP_NAME=$nname
export IOTEMPOWER_AP_PASSWORD=$npass
export IOTEMPOWER_AP_IP=$baseip
export IOTEMPOWER_AP_ADDID="no"

# Call the iotempower script from bin/,
# iot env must be activated!
echo $(accesspoint)
