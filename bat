#! /usr/local/conda2/bin/python

def read(filename, t='int'):
    with open(filename, 'r') as fd:
        val = fd.readline().rstrip()
    return int(val) if val.isdigit() else val


print "BAT0:"
try:
    c0 = read('/sys/class/power_supply/BAT0/capacity')
    v0 = read('/sys/class/power_supply/BAT0/voltage_now')
    i0 = read('/sys/class/power_supply/BAT0/current_now')
    s0 = read('/sys/class/power_supply/BAT0/status')
    print "  Voltage = {:.3f}V".format(v0/1e6)
    print "  Current = {:.3f}A ({})".format(i0/1e6,s0)
    print "  SOC     = {}%".format(c0)
except:
    print "  ---"

print "BAT1:"
try:
    c1 = read('/sys/class/power_supply/BAT1/capacity')
    v1 = read('/sys/class/power_supply/BAT1/voltage_now')
    i1 = read('/sys/class/power_supply/BAT1/current_now')
    s1 = read('/sys/class/power_supply/BAT1/status')
    print "  Voltage = {:.3f}V".format(v1/1e6)
    print "  Current = {:.3f}A ({})".format(i1/1e6,s1)
    print "  SOC     = {}%".format(c1)
except:
    print "  ---"
