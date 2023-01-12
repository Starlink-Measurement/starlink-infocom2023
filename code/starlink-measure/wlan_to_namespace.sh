#!/usr/bin/env bash
set -x
ip netns add net_remote_ns

# Set namespace to use wlan0, after this point wlan0 is not usable by programs
# outside the namespace
iw phy phy0 set netns "$(ip netns exec net_remote_ns sh -c 'sleep 1 >&- & echo "$!"')"

# This one only works for ethernet
#ip link set wlan0 netns net_remote_ns

ip netns exec net_remote_ns ip link set wlan0 up
ip netns exec net_remote_ns ip link set lo up

ip netns exec net_remote_ns dhclient wlan0

ip netns exec net_remote_ns ping -c 3 google.ca

# Move back to root namespace
# ip netns exec net_remote_ns iw phy phy0 set netns 1
