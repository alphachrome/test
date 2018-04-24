#/usr/local/conda2/bin/python
import subprocess

PAGE = 0x00
READ_VOUT = 0x8B
READ_IOUT = 0x8C
READ_TEMPERATURE = 0x8D
READ_PIN = 0x97
READ_POUT = 0x96
MFR_FS_VBOOT = 0xE5
OC_LIMIT_ICC_MAX = 0xEF


def read(bits, addr):
    cmd = "sudo ectool i2cread {} 3 0x40 {}".format(bits, addr)
    result = subprocess.check_output(cmd, shell=True)
    return int(result.split('=')[1],0)


def write(bits, addr, value):
    cmd = "sudo ectool i2cwrite {} 3 0x40 {} {}".format(bits, addr,value)
    result = subprocess.check_output(cmd, shell=True)
    return result

def read8(addr):
    return read(8, addr)

def read16(addr):
    return read(16, addr)

def write8(addr, value):
    return write(8, addr, value)

def write16(addr, value):
    return write(16, addr, value)

Rails = ["Rail A", "Rail B", "Rail C"]

write8(PAGE,0)
print "Global:"
print "  SW_FREQ = {}kHz".format(50*(read16(MFR_FS_VBOOT)&0x7FFF)>>8)
print "     PSYS = {}W".format(0.5*(read16(READ_PIN)&0x1F))
print "     TEMP = {}C".format(read16(READ_TEMPERATURE)&0xF)

for n, rail in enumerate(Rails):
    write8(PAGE,n)
    print "{}:".format(rail)
    print "  ICC_MAX = {}A".format(read16(OC_LIMIT_ICC_MAX)&0xFF)
    print "     VOUT = {}V".format(1.52/255*(read16(READ_VOUT)&0xF))
    print "     IOUT = {}A".format(0.25*(read16(READ_IOUT)&0x7F))
    print "     POUT = {}W".format(0.5*(read16(READ_POUT)&0x1F))
    

