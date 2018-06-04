import serial
from collections import namedtuple
PTS="/dev/pts/29"

DEBUG=0

ser = serial.Serial(PTS, 115200, timeout=0.1)
ser.write("\nchan 0\n")

def reg_read8(port, addr, reg):
    for line in ser:
        continue
    cmd = "i2cxfer r {} {} {}\n".format(port, hex(addr), hex(reg))
    if DEBUG:
        print "  READ: {}".format(cmd)
    ser.write(cmd)
    ser.readline()
    retval = ser.readline().split(" ")[0]
    return retval

def reg_write8(port, addr, reg, val):
    cmd = "i2cxfer w16 {} {} {} {}\n".format(port, hex(addr), hex(reg), val)
    if DEBUG:
        print "  WRITE: {}".format(cmd)
    ser.write(cmd)
    for line in ser:
        continue

def reg_read16(port, addr, reg):
    for line in ser:
        continue
    cmd = "i2cxfer r16 {} {} {}\n".format(port, hex(addr), hex(reg))
    if DEBUG:
        print "  READ: {}".format(cmd)
    ser.write(cmd)
    ser.readline()
    retval = ser.readline().split(" ")[0]
    return retval

def reg_write16(port, addr, reg, val):
    cmd = "i2cxfer w16 {} {} {} {}\n".format(port, hex(addr), hex(reg), val)
    if DEBUG:
        print "  WRITE: {}".format(cmd)
    ser.write(cmd)
    for line in ser:
        continue

class Charger:
    def __init__(self, port, addr):
        self.port = port
        self.addr = addr
    def read(self, reg):
        return reg_read8(self.port, self.addr, reg)
    
    def read16(self, reg):
        return int(reg_read16(self.port, self.addr, reg),0)

#### BQ25703 specific #####
chg = Charger(0, 0xd6)

REG = [
    ("Charge Option 0", 0),
    ("Charge Current", 2),
    ("Charge Voltage", 4),
    ("OTG Voltage", 6),
    ("OTG Current", 8),
    ("Input Voltage", 0xA),
    ("Minimum Vsys", 0xC),
    ("Input Current", 0xE),
    ("Charge Status", 0x20),
    ("Prochot Status", 0x22),
    ("IIN Limit", 0x24),
    ("VBUS and PSYS", 0x26),
    ("I_bat", 0x28),
    ("V_sys and V_bat", 0x2A),
    ("Mfg and Dev Id", 0x2E),
    ("CHARGE_OPTION1", 0x30),
    ("CHARGE_OPTION2", 0x32),
    ("CHARGE_OPTION3", 0x34),
    ("PROCHOT_OPTION0", 0x36),
    ("PROCHOT_OPTION1", 0x38),
    ("ADC_OPTION", 0x3A)
]

def print_chg_regs():
    for reg in REG:
        print "{:>15} ({:>4}): {}".format(reg[0], hex(reg[1]), hex(chg.read16(reg[1])))

def print_chg_info():
    reg = chg.read16(0x2)
    print "Charge Current: {} ({}A)".format(hex(reg), (reg>>6)*0.064)
    reg = chg.read16(0x4)
    print "Max Charge Voltage: {} ({}V)".format((reg), (reg>>4)*0.016)
    reg = chg.read16(0xc)
    print "Min Charge Voltage: {} ({}V)".format((reg), (reg>>8)*0.256)
      

class Cmd:
    def __init__(self, name, desc, func):
        self.name = name 
        self.desc = desc
        self.func = func
        
cmd_list = [
    Cmd('c', 'Print all charger registers', print_chg_regs),
    Cmd('i', 'Pring charge info', print_chg_info)
]

def run_cmd(cmd):

    if cmd =='c*?':
        for reg in CTRL_LIST:
            print_spec(reg)

    elif cmd[0:3]=='set':
        cmd_list = cmd.split(' ')
        name = cmd_list[1]
        value = uint16(cmd_list[2])
        set_bits(name, value)
    else:
        print "Invalid command!"

def console():
    while True:
        req_cmd = raw_input("[console] >> ")
        if req_cmd == '':
            continue
        elif req_cmd == '.exit':
            break
        elif req_cmd in ('.help', '.h', '.?', '.'):
            for cmd in cmd_list:
                print "  .{} - {}".format(cmd.name, cmd.desc)
            print "  .exit - Exit"
            print "  .help"
        elif req_cmd[0]=='.':      
            req_cmd = req_cmd[1:].split(' ')
            for cmd in cmd_list:
                if req_cmd[0] == cmd.name:
                    if len(req_cmd)==1:
                        cmd.func()
                    else:
                        para = req_cmd[1:]
                        cmd.func(para)
                        break
        else:
            ser.write(req_cmd+"\n")
            for line in ser:
                print line
if __name__ == "__main__":
    console()

