#!/bin/bash

read -r v < "/sys/class/power_supply/BAT0/voltage_now"
read -r s < "/sys/class/power_supply/BAT0/status"
read -r i < "/sys/class/power_supply/BAT0/current_now"
read -r c < "/sys/class/power_supply/BAT0/capacity"

echo "Battery 0:"
echo "  Voltage: $((v)) uV"
echo "  Current: $i uA ($s)"
echo "  SOC: $c %"

read -r v < "/sys/class/power_supply/BAT1/voltage_now"
read -r s < "/sys/class/power_supply/BAT1/status"
read -r i < "/sys/class/power_supply/BAT1/current_now"
read -r c < "/sys/class/power_supply/BAT1/capacity"

echo "Battery 1:"
echo "  Voltage: $v uV"
echo "  Current: $i uA ($s)"
echo "  SOC: $c %"
