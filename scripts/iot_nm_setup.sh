#!/bin/bash


# NetworkManager AP setup with steps.
# Based on accesspoint-nm script in IoTempower, 
# adjusted for interactive use

nname=$1
npass=$2
baseip=$3
netmask=$4


# Prepare for NM use after (presumably) hostapd

echo 'polkit.addRule(function(action, subject) {
    if (action.id.indexOf("org.freedesktop.NetworkManager.") == 0 && subject.user == "iot") {
        return polkit.Result.YES;
    }
});' | sudo tee /etc/polkit-1/rules.d/50-nmcli.rules > /dev/null

sudo sed -i '/^\[ifupdown\]/{N;s/managed=false/managed=true/;}' "/etc/NetworkManager/NetworkManager.conf"

sudo service NetworkManager restart


# Call the iotempower script from bin/,
# iot env must be activated!
echo $(accesspoint-nm create --ssid $nname --password $npass --ip $baseip --netmask $netmask)
