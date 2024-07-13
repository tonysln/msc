#!/bin/sh


# TODO something along the lines of declare -A newmap,
# but more generally a separate file (csv perhaps?)
# for the supported chips DB

filter_msg() {
  # Arg $1 - Provided msg

  local filter_str="wifi|wireless|802.11|wlan|ath|broadcom|intel|realtek|qualcomm|mediatek|brcm|bcm|b43|mt76|iwlwifi|rtl"
  local output=$(echo $1 | grep -i -E $filter_str)
  echo output
}

check_lshw() {
  local output=$(sudo lshw -C network)
  # Find "Wireless interface" and collect 
  # product, vendor, bus info, logical name, 
  # serial, capabilities and configuration.
  # Might have multiple
}

check_lspci() {
  local output=$(sudo lspci)
  # Lookup from known/supported chips/vendors
}

check_lsusb() {
  local output=$(sudo lsusb)
  # Lookup from known/supported chips/vendors
  # from connected USB devices
}

check_iwconfig() {
  local output=$(sudo iwconfig)
  # Gather status and capabilities,
  # join with lshw "logical name"
}

check_dmesg() {
  local output=$(sudo dmesg)
  # Can get the richest output, but need to throw
  # everything at it first from list of supported
  # chips and models
}
