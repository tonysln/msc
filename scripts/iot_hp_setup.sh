#!/bin/bash


# hostapd AP setup with steps.
# Based on accesspoint script in IoTempower, 
# adjusted for interactive use

nname=$1
npass=$2
baseip=$3


# Prepare for hostapd use after (presumably) NM
sudo systemctl enable wpa_supplicant.service
sudo systemctl enable wpa_supplicant@wlan0.service


export IOTEMPOWER_AP_NAME=$nname
export IOTEMPOWER_AP_PASSWORD=$npass
export IOTEMPOWER_AP_IP=$baseip
export IOTEMPOWER_AP_ADDID="no"

# Save to IoTempower config file as well
cat << EOF > $IOTEMPOWER_ROOT/etc/wifi_credentials
SSID=$nname
Password=$npass
GatewayIP=$baseip
EOF


# Call the iotempower script from bin/,
# iot env must be activated!
echo $(accesspoint)
