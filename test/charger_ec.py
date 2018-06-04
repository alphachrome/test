#import Adafruit_GPIO.FT232H as FT232H
import time
import serial
from numpy import uint16

DEBUG_I2C=True
CHG_ADDR = 0x12
BAT_ADDR = 0x16

global ser, PTS

ser=None
PTS=None
chg=None
bat=None
DUT=""

def init(dut):
    global ser, chg, bat, PTS, DUT
    DUT=dut
    if dut=='Lux':
        f = open('/home/cros/cros/chroot/tmp/lux_pts.txt', 'r')
        I2C_PORT=2
    elif dut=='Wand':
        f = open('/home/cros/cros/chroot/tmp/wand_pts.txt', 'r')
        I2C_PORT=1
    else:
        print "Invalid DUT"
    PTS = f.readline().split(':')[1].strip()
    ser = serial.Serial("{}".format(PTS), 115200, timeout=0.1)
    ser.write("\nchan 0\n")

    chg = i2c_dev(I2C_PORT, CHG_ADDR)
    bat = i2c_dev(I2C_PORT, BAT_ADDR)

class i2c_dev:
    def __init__(self, port, addr):
        self.port = port
        self.addr = addr
    def readU16(self, offset):
        for line in ser:
            continue
        cmd = "i2cxfer r16 {} {} {}\n".format(self.port, self.addr, offset)
        if DEBUG_I2C:
            print 'i2c_dev.readU16: "{}"'.format(cmd.rstrip())
        ser.write(cmd)
        ser.readline()
        retval = ser.readline().split("[")[1]
        return int(retval.split("]")[0])
    def write16(self, offset, value):
        cmd = "i2cxfer w16 {} {} {} {}\n".format(self.port, self.addr, offset, value)
        if DEBUG_I2C:
            print 'i2c_dev.write16: "{}"'.format(cmd.rstrip())
        ser.write(cmd)
        for line in ser:
            continue

# Bits Specs
class Bits:
    def __init__(self, bitname, lsb=0, mask=0xFFFF, description='', option=''):
        self.name = bitname
        self.lsb = lsb
        self.mask = mask
        self.desc = description
        self.opt = option
        
### Smart Battery Registers ###
class SB:
    def __init__(self, name, address, unit='', bits=None):
        self.name = name
        self.addr = address
        self.unit = unit
        self.bits = bits
        
    def read(self):
        return bat.readU16(self.addr)

    def write(self, addr, value16):
        bat.write16(addr, value16)


SB_MODE_BITS = [
    (1<<0, "MODE_INTERNAL_CHARGE_CONTROLLER"),
    (1<<1, "MODE_PRIMARY_BATTERY_SUPPORT"),
    (1<<7, "MODE_CONDITION_CYCLE"),
    (1<<8, "MODE_CHARGE_CONTROLLER_ENABLED"),
    (1<<9, "MODE_PRIMARY_BATTERY"),
    (1<<13, "MODE_ALARM"),
    (1<<14, "MODE_CHARGER"),
    (1<<15, "MODE_CAPACITY")]


SB_STATUS_BITS = [
    (0xf, "ERROR_MASK"),
    (0, "ERROR_OK"),
    (1, "ERROR_BUSY"),        
    (2, "ERROR_RESERVED"),     
    (3, "CODE_UNSUPPORTED"),  
    (4, "ERROR_ACCESS_DENIED"),
    (5, "ERROR_OVERUNDERFLOW"),
    (6, "ERROR_BADSIZE"),
    (7, "ERROR_UNKNOWN"),
    (1<<4, "STATUS_FULLY_DISCHARGED"),
    (1<<5, "STATUS_FULLY_CHARGED"),
    (1<<6, "STATUS_DISCHARGING"),
    (1<<7, "STATUS_INITIALIZED"),
    (1<<8, "ALARM_REMAINING_TIME"),
    (1<<9, "ALARM_REMAINING_CAPACITY"),
    (1<<11, "ALARM_TERMINATE_DISCHARGE"),
    (1<<12, "ALARM_OVERTEMP"),
    (1<<14, "ALARM_TERMINATE_CHARGE"),
    (1<<15, "ALARM_OVERCHARGED")]

SB_MODE     = SB("MODE", 0x03, bits=SB_MODE_BITS)
SB_STATUS   = SB("STATUS", 0x16, bits=SB_STATUS_BITS)
SB_V        = SB("VOLTAGE", 0x09, 'mV')
SB_I        = SB("CURRENT", 0x0A, 'mA')
SB_I_CHG    = SB("CHARGING_CURRENT", 0x14, 'mA')
SB_V_CHG    = SB("CHARGING_VOLTAGE", 0x15, 'mV')

SB_I_AVG    = SB("AVERAGE_CURRENT", 0x0B, 'mA')

SB_REL_SOC  = SB("RELATIVE_SOC", 0x0D, '%')
SB_ABS_SOC  = SB("ABS_SOC", 0x0E, '%')

SB_REM_CAP  = SB("REMAINING_CAPACITY", 0x0F, 'mAh')
SB_FULL_CAP = SB("FULL_CHARGE_CAPACITY", 0x10, 'mAh')

SB_T_RUN2EMPTY = SB("RUN_TIME_TO_EMPTY", 0x11, 'min')
SB_T_AVG2EMPTY = SB("AVERAGE_TIME_TO_EMPTY", 0x12, 'min')
SB_T_AVG2FULL = SB("AVERAGE_TIME_TO_FULL", 0x13, 'min')

SB_R        = SB("AT_RATE", 0x04)
SB_R_TFULL   = SB("AT_RATE_TIME_TO_FULL", 0x05, 'min')
SB_R_TEMPTY  = SB("AT_RATE_TIME_TO_EMPTY", 0x06, 'min')
SB_R_OK     = SB("AT_RATE_OK", 0x07)
SB_TEMP     = SB("TEMPERATURE", 0x08, '*0.1K')

SB_DESIGN_CAP = SB("DESIGN_CAPACITY", 0x18, 'mAh')
SB_DESIGN_V = SB("DESIGN_VOLTAGE", 0x19, 'mV')
SB_MAX_ERROR = SB("MAX_ERROR", 0x0c, '%')

##
SB_CYC_CNT  = SB("CYCLE_COUNT",0x17)

## SB_SPECIFICATION_INFO           0x1a
## SB_MANUFACTURER_DATE            0x1b
## SB_SERIAL_NUMBER                0x1c
## SB_MANUFACTURER_NAME            0x20
## SB_DEVICE_NAME                  0x21
## SB_DEVICE_CHEMISTRY             0x22
## SB_MANUFACTURER_DATA            0x23

SB_LIST = [ SB_TEMP, SB_MODE, SB_STATUS, SB_V, SB_I, SB_V_CHG, SB_I_CHG, SB_I_AVG, SB_REL_SOC, SB_ABS_SOC, SB_REM_CAP, SB_FULL_CAP,
            #SB_T_RUN2EMPTY,
            SB_T_AVG2FULL,
            #SB_R, SB_R_TFULL, SB_R_TEMPTY,SB_R_OK,
             SB_CYC_CNT, SB_DESIGN_CAP, SB_DESIGN_V, SB_MAX_ERROR,]

### Charger Registers ### 
class Info:
    def __init__(self, name, address, spec=''):
        self.name = name        # Register Name
        self.addr = address     # Register Address
    def refresh(self):
        self.value = chg.readU16(self.addr)

class Ctrl:
    def __init__(self, name, address, spec=''):
        self.name = name        # Register Name
        self.addr = address     # Register Address
        self.spec = spec        # Register Specification
        self.value = -1
    def refresh(self):
        self.value = chg.readU16(self.addr)

    def write(self, name, value16):
        # to be implemented...
        return
    # Return option by bits value
    def read(self, bits_name):
        for bits in self.spec:
            if bits.name == bits_name:
                opt_i = (self.value&(bits.mask<<bits.lsb))>>bits.lsb
                return bits.opt[opt_i]
        return "No found!"

    # Return numerical value
    def readnum(self, bits_name):
        for bits in self.spec:
            if bits.name == bits_name:
                return (self.value&(bits.mask<<bits.lsb))>>bits.lsb
        return -1

class Reg:
    def __init__(self, name, address, lsb=0, lsb_size=1, unit=''):
        self.name = name
        self.addr = address
        self.lsb = lsb
        self.lsb_size = lsb_size
        self.unit = unit
        
    def read(self):
        self.value = chg.readU16(self.addr)
        return (self.value >> self.lsb) * self.lsb_size
        
    def write(self, value):
        self.value = uint16(value / self.lsb_size) << self.lsb
        chg.write16(self.addr, self.value)

CTRL_0_SPEC = [
    Bits("CTRL_0"),
    Bits("CPM_FWD_OFFSET", 13, 0b111, "FWD Buck/Buck-Boost Comparator offset", ("0mV","0.5mV","1mV","1.5mV","-2mV","-1.5mV","-1mV","-0.5mV")),
    Bits("CPM_BST_OFFSET", 10, 0b111, "FWD/REV Boost Comparator offset", ("0mV","0.5mV","1mV","1.5mV","-2mV","-1.5mV","-1mV","-0.5mV")),
    Bits("CPM_BCK_OFFSET", 8, 0b11, "REV Buck/Buck-Boost Comparator offset", ("0mV", "1mV", "-2mV", "-1mV")),
    Bits("SMB_TIMEOUT",  7, 1, "SMBus Timeout", ("Enable", "Disable")),
    Bits("HSFET_SHORT", 5, 0b11, "High-Side FET Short Detection Threshold", ("400mV", "500mV", "600mV", "800mV")),
    Bits("BAT_LP_THRSHLD", 3, 0b11, "Battery-Only Low-Power Mode Dcprochot# threshold", ("12A", "10A", "8A", "6A")),
    Bits("VIN_REG", 2, 1, "Input Voltage Regulation Loop", ("Enable", "Disable"))
]

CTRL_1_SPEC = [
    Bits("CTRL_1"),    
    Bits("CMP_DEBOUNCE", 14, 0b11, "GP Comparator Debounce Time", ("2us", "12us", "2ms", "5s")),
    Bits("EXIT_LEARN", 13, 1, "Exit Learn Mode Option", ("Stay if VBAT < MinSystemVoltage", "Exit if VBAT < MinSystemVoltage")),
    Bits("LEARN", 12, 1, "Learn Mode", ("Disable", "Enable")),
    Bits("OTG", 11, 1, "OTG Function", ("Disable", "Enable")),
    Bits("AUDIO_FILTER", 10, 1, "Audio Filter", ("Disable", "Enable")),
    Bits("SW_FREQ", 8, 0b11, "Switching Frequency ", ("PROG pin", "839kHz", "723kHz", "635kHz")),
    Bits("TURBO", 6, 1, "Turbo", ("Enable", "Disable")),
    Bits("ABMON_FUNC", 5, 1, "AMON/BMON Function", ("Enable", "Disable")),
    Bits("ABMON", 4, 1, "AMON or AMON ", ("AMON", "BMON")),
    Bits("PSYS", 3, 1, "PSYS function", ("Disable", "Enable")),
    Bits("VSYS", 2, 1, "VSYS output", ("Enable", "Disable")),
    Bits("LOW_VSYS_THRSHLD", 0, 0b11, "Low_VSYS PROCHOT threshold", ("6V", "6.3V", "6.6V", "6.9V"))
]

CTRL_2_SPEC= [
    Bits("CTRL_2"),
    Bits("TRICKLE_ICHRG", 14, 0b11, "Tickle Charging Current", ("256mA", "128mA", "62mA", "512mA")),
    Bits("OTG_DEBOUNCE", 13, 1, "OTG Function Enable Debounce Time", ("1.3s", "150ms")),
    Bits("2LVL_CURR_LIMIT", 12, 1, "Two-Level Adapter Current Limit Function", ("Disable", "Enable")),
    Bits("ADP_INS_DEBOUNCE", 11, 1, "Adapter Insertion to Switching Debounce", ("1.3s", "150ms")),
    Bits("PROCHOT_DEBOUNCE", 9, 0b11, "PROCHOT Debounce", ("7us", "100us", "500us", "1ms")),
    Bits("PROCHOT_DURATION", 6, 0b111, "PROCHOT Duration", ("10ms", "20ms", "15ms", "5ms", "1ms", "500us", "100us", "0s")),
    Bits("ASGATE_IN_OTG", 5, 1, "ASGATE in OTG Mode", ("Turn On", "Turn Off")),
    Bits("CMIN_REF", 4, 1, "GP Comparator Reference Voltage", ("1.2V", "2V")),
    Bits("GP_CMP", 3, 1, "General Purpose Comparator", ("Enable", "Disable")),
    Bits("CMOUT_POLARITY", 2, 1, "GP Comparator Output Polarity", ("High", "Low")),
    Bits("WOCP", 1, 1, "Way Overcurrent Function", ("Enable", "Disable")),
    Bits("BAT_OVP", 0, 1, "Battery Overvoltage Function", ("Disable", "Enable"))
]
                                                    
CTRL_3_SPEC = [
    Bits("CTRL_3"),
    Bits("REREAD_PROG", 15, 1, "Reread PROG Pin Resistor", ("Yes", "No")),
    Bits("RELOAD_ACLIM", 14, 1, "Reload ACLIM when Adapter is plugged in", ("Yes", "No")),
    Bits("AUTOCHRG_TERM", 13, 1, "Autonomous Charging Termination Time", ("20ms", "200ms")),
    Bits("CHARGE_TIMEOUT", 12, 0b11, "Charger Timeout", ("175s", "87.5s", "43.75s", "5s")),
    Bits("BGATE_OFF", 10, 1, "Battery Ship mode", ("Disable", "Force BGATE Off (Enable Ship mode)")),
    Bits("PSYS_GAIN", 9, 1, "System Power Monitor PSYS output gain", ("1.44uA/W", "0.723uA/W")),
    Bits("EXIT_IDM", 8, 1, "Ideal Diode mode exit timer when discharge < 300mA", ("40ms", "80ms")),
    Bits("AUTOCHARGE", 7, 1, "Autonomous Charging Mode", ("Enable", "Charging current control thru SMBUS")),
    Bits("AC_CC_Feedback", 6, 1, "AC and CC Feedback Gain", ("Idle", "x0.5")),
    Bits("IIN_LIM_CTRL", 5, 1, "Input Current Limit Loop", ("Enable", "Disable")),
    Bits("IIN_LIM_CTRL_NOBAT", 4, 1, "Input Current Limit Loop when BATGONE=1", ("Enable", "Disable")),
    Bits("ABMON_DIR", 3, 1, "AMON/BMON Direction", ("I_ADP/I_CHRG", "I_OTG/I_DISCHRS")),
    Bits("D_RESET", 2, 1, "Reset all SMBus register value", ("Idle", "Reset")),
    Bits("SW_PERIOD", 1, 1, "Switching period in Buck-Boost mode", ("x1", "x2 (half switching frequency)")),
    Bits("OTG_DELAY", 0, 1, "Shorts OTG Start-up time", ("Idle", "Short from 150ms to 1ms (when CTRL2.B13=150ms)"))   
]

CTRL_4_SPEC = [
    Bits("CTRL_4"),
    Bits("IOTG_PROCHOT", 7, 1, "Trigger PROCHOT with OTGCURRENT", ("Disable", "Enable")),
    Bits("BATGONE_PROCHOT", 6, 1, "Tirgger PROCHOT with BATGONE", ("Disable", "Enable")),
    Bits("ACOK_PROCHOT", 5, 1, "Trigger PROCHOT with ACOK", ("Disable", "Enable")),
    Bits("CMP_PROCHOT", 4, 1, "Trigger PROCHOT with GP Comparator rising", ("Disable", "Enable")),
    Bits("ACOK_BATGONE_DEBOUNCE", 2, 0b11, "ACOK falling or BATGONE rising debounce", ("2us", "25us", "125us", "250us")),
    Bits("PROCHOT_CLR", 1, 1, "Clear PROCHOT", ("Idle", "Clear")),
    Bits("PROCHOT_Latch", 0, 1, "Manually reset PROCHOT", ("Auto-clear", "Latch"))
]

INFO1_TRICKLE = ('Not active', 'Active')
INFO1_CTRL = ('MaxSystemVoltage', 'Charging', 'Adapter Current Limit', 'Input Voltage')
INFO1_REF = ('Not active', 'Active')

INFO2_PROG_FREQ = ('733kHz', '1MHz')
INFO2_PROG_AUTOCHRG = ('Yes', 'No')
INFO2_PROG_ACLIM1 = ('1.5A', '0.476A')
INFO2_MODE = ('Unknown', 'Boost', 'Buck', 'Buck-Boost', "Unknown", 'OTG Boost', 'OTG Buck', 'OTG Buck-Boost') 
INFO2_STATUS = ('OFF', 'BATTERY', 'ADAPTER', 'ACOK', 'VSYS', 'CHARGE', 'ENOTG', 'OTG',
                'ENLDO5', 'N/A', 'TRIM/ENCHREF', 'ACHRG', 'CAL', 'AGON/AGONTG', 'WAIT/PSYS', 'ADPPSYS')
INFO2_BATGONE = ('Present', 'Gone')
INFO2_CMPOUT = ('Low', 'High')
INFO2_ACOK = ('No Adapter', 'Adapter is present')


I_CHG_LIM    = Reg("I_CHG_LIM",    0x14, 2, 4, "mA")  # lsb_size depends on RS2 (on EVM RS2=0.01ohm)
V_SYS_MAX    = Reg("V_SYS_MAX",    0x15, 3, 8, "mV")
V_SYS_MIN    = Reg("V_SYS_MIN",    0x3E, 8, 256, "mV")
V_OTG        = Reg("V_OTG",        0x49, 3, 12, "mV")
I_OTG        = Reg("I_OTG",        0x4A, 7, 128, "mA")
I_AC_PROCHOT = Reg("I_AC_PROCHOT", 0x47, 7, 128, "mA")
I_DC_PROCHOT = Reg("I_DC_PROCHOT", 0x48, 8, 256, "mA")
V_IN         = Reg("V_IN",         0x4B, 8, 341.3, "mV")
I_ADP_LIM1   = Reg("I_ADP_LIM1",   0x3F, 2, 4, "mA") # lsb_size depends on RS1 (on EVM RS1=0.02ohm)
I_ADP_LIM2   = Reg("I_ADP_LIM2",   0x3B, 2, 4, "mA") # lsb_size depends on RS1 (on EVM RS1=0.02ohm)

CTRL_0 = Ctrl("CTRL_0", 0x39, CTRL_0_SPEC)
CTRL_1 = Ctrl("CTRL_1", 0x3C, CTRL_1_SPEC)
CTRL_2 = Ctrl("CTRL_2", 0x3D, CTRL_2_SPEC)
CTRL_3 = Ctrl("CTRL_3", 0x4C, CTRL_3_SPEC)
CTRL_4 = Ctrl("CTRL_4", 0x4E, CTRL_4_SPEC)

INFO_1 = Info("INFO_1", 0x3A)
INFO_2 = Info("INFO_2", 0x4D)
MFG_ID = Info("MFG_ID", 0xFE)
DEV_ID = Info("DEV_ID", 0xFF)

T1_T2 = Reg("T1_T2", 0x38) 

REG_LIST = [I_CHG_LIM, V_SYS_MAX, V_SYS_MIN, V_OTG, I_OTG, I_AC_PROCHOT, I_DC_PROCHOT, V_IN, I_ADP_LIM1, I_ADP_LIM2]
CTRL_LIST = [CTRL_0, CTRL_1, CTRL_2, CTRL_3, CTRL_4]


def print_bits(val, BITS):
    for bit in BITS:
        if val&bit[0]:
            print "   + "+bit[1]

def print_bat_mode():
    print_bits(SB_MODE.read(), SB_MODE_BITS)

def print_bat_status():
    print_bits(SB_STATUS.read(), SB_STATUS_BITS)


def print_bat():
    for reg in SB_LIST:
        val = reg.read()
        if reg.unit == "":
            print (">> {} = {} ({}) [{}]".format(reg.name, val, bin(val), hex(reg.addr)))
        else:
            print (">> {} = {} {} [{}]".format(reg.name, val, reg.unit, hex(reg.addr)))
        if reg.bits:
            print_bits(val,reg.bits)
        
        
def print_ctrl_spec(reg):
    print(">> {} ({}):".format(reg.name, hex(reg.addr)))
    for bits in reg.spec:
        if bits.opt != '':
            print ("  {} <{}-{}> : {}".format(bits.name, bits.lsb, bin(bits.mask), bits.desc))
            for bit_n, option in enumerate(bits.opt):
                print ("     {} = {}   ".format(bin(bit_n), option))

def print_ctrl_spec_all():
    for ctrl in CTRL_LIST:
        print_ctrl_spec(ctrl)

def print_ctrl(reg):
    reg.refresh()
    print ">> {} = {}".format(reg.name, bin(reg.value))
    for bits in reg.spec:
        option = bits.opt
        if option=='':
            continue
        print ("  + {} = {} ({})".format(bits.name, reg.read(bits.name), str(bin(reg.readnum(bits.name)))))

def print_ctrl0():
    print_ctrl(CTRL_0)
    
def print_ctrl1():
    print_ctrl(CTRL_1)

def print_ctrl2():
    print_ctrl(CTRL_2)

def print_ctrl3():
    print_ctrl(CTRL_3)

def print_ctrl4():
    print_ctrl(CTRL_4)

def print_ctrl_all():
    for ctrl in CTRL_LIST:
        print_ctrl(ctrl)

def set_bits(_name, _value):
    for reg in REG_LIST:
        if reg.name == _name:
            reg.write(_value)
            return

    for reg in CTRL_LIST:
        for bits in reg.spec:
            if bits.name == _name:
                old_value = uint16(chg.readU16(reg.addr))
                _value &= bits.mask
                new_value = old_value & uint16(~(bits.mask<<bits.lsb))
                new_value |= uint16(_value<<bits.lsb)
                chg.write16(reg.addr, new_value)
                print "Write: reg {} = {} (old value = {})".format(reg.name, bin(new_value), bin(old_value))
                return

    print "Invalid Bits Name!"

def cmd_set_bits(para):
    print(para)
    if len(para)==2:
        set_bits(para[0], uint16(para[1]))
    else:
        print "Invalid commnad!"
    
def print_info1():
    INFO_1.refresh()
    info = INFO_1.value
    print '>> INFO1 =', bin(info)
    print '  + Trickle Charging :', INFO1_TRICKLE[(info & 2**4)>>4]
    print '  + TRIP bits :', bin((info & (7<<10))>>10)
    print '  + Active Control Loop :', INFO1_CTRL[(info & (3<<13))>>13]
    print '  + Reference :', INFO1_REF[(info & 2**15)>>15]

def print_info2():
    INFO_2.refresh()
    info = INFO_2.value
    print '>> INFO2 =', bin(info)
    print '  + PROG-#CELL :', ((info & (3<<3))>>3)+1
    print '  + PROG-Freq :', INFO2_PROG_FREQ[(info & (1<<2))>>2]
    print '  + PROG-Autocharge :', INFO2_PROG_AUTOCHRG[(info & (1<<1))>>1]
    print '  + PROG-ACLIM1 :', INFO2_PROG_ACLIM1[info & 1]
    print '  + Mode :', INFO2_MODE[(info & (7<<5)) >> 5]
    print '  + Status :', INFO2_STATUS[(info & (15<<8)) >> 8]
    print '  + Battery :', INFO2_BATGONE[(info & 2**12) >> 12]
    print '  + Camparator output is :', INFO2_CMPOUT[(info & 2**13) >> 13]
    print '  + ACOK :', INFO2_ACOK[(info & 2**14) >> 14]

def print_info():
    print_info1()
    print_info2()

def print_iv_reg(reg):
    print(">> {} = {} {}".format( reg.name, reg.read(), reg.unit ))

def print_iv_reg_all():
    for reg in REG_LIST:
        print_iv_reg(reg)

def print_main():
    print (">> I_CHG_LIM = {} {}".format(I_CHG_LIM.read(), I_CHG_LIM.unit))
    print (">> V_SYS_MAX = {} {}".format(V_SYS_MAX.read(), V_SYS_MAX.unit))
    print (">> V_SYS_MIN = {} {}".format(V_SYS_MIN.read(), V_SYS_MIN.unit))
    print (">> I_ADP_LIM1 = {} {}".format(I_ADP_LIM1.read(), I_ADP_LIM1.unit))
    print (">> V_OTG = {} {}".format(V_OTG.read(), V_OTG.unit))
    print (">> I_OTG = {} {}".format(I_OTG.read(), I_OTG.unit))

    CTRL_1.refresh()
    print(">> OTG = {} ({})".format(CTRL_1.read("OTG"), CTRL_1.readnum("OTG")))
    print(">> VSYS = {} ({})".format(CTRL_1.read("VSYS"), CTRL_1.readnum("VSYS")))
    
    CTRL_0.refresh()
    print(">> VIN_REG = {} ({})".format(CTRL_0.read("VIN_REG"), CTRL_0.readnum("VIN_REG")))
    
    INFO_2.refresh()
    info=INFO_2.value
    print('>> Mode = {}'.format(INFO2_MODE[(info & (7<<5)) >> 5]))

class Cmd:
    def __init__(self, name, desc, func):
        self.name = name 
        self.desc = desc
        self.func = func

def cmd_otg():
    set_bits('V_OTG',15000)
    set_bits('I_OTG',2200)
    set_bits('OTG',1)

def cmd_chg():
    set_bits('I_ADP_LIM1', 2100)
    set_bits('I_CHG_LIM', 2500)
    set_bits('V_SYS_MAX', 8400)
    set_bits('I_ADP_LIM1', 3100)
    set_bits('SMB_TIMEOUT', 1)

def cmd_lux():
    chg.port = 2
    bat.port = 2
    print "Set I2C_Port to 2"

def cmd_wand():
    chg.port = 1
    bat.port = 1
    print "Set I2C_Port to 1"

cmd_list = [
    Cmd('b', 'Battery registers', print_bat),
    Cmd('bs', 'Battery status', print_bat_status),
    Cmd('bm', 'Battery mode', print_bat_mode),
    Cmd('iv', 'Charger operating point settings', print_iv_reg_all),
    Cmd('m', 'Print main paramaters', print_main),
    Cmd('c0', 'Charger Control0 Register', print_ctrl0),
    Cmd('c1', 'Charger Control1 Register', print_ctrl1),
    Cmd('c2', 'Charger Control2 Register', print_ctrl2),
    Cmd('c3', 'Charger Control3 Register', print_ctrl3),
    Cmd('c4', 'Charger Control4 Register', print_ctrl4),
    Cmd('c', 'Charger Control0-4 Registers', print_ctrl_all),
    Cmd('c?', 'Charger Contorl Register Fields', print_ctrl_spec_all),
    Cmd('i1', 'Charger Info1 Register', print_info1),
    Cmd('i2', 'Charger Info2 Register', print_info2),
    Cmd('i', 'Charger Info1-2 Registers', print_info),
    Cmd('set', 'Set <FIELD_NAME> <VALUE>', cmd_set_bits),
    Cmd('otg', 'Enable OTG, V_otg=12V, I_otg=2.2A', cmd_otg),
    Cmd('chg', 'Enable Charge, I_adp=3.3A, I_chg=2.5A', cmd_chg),
    Cmd('lux', 'Lux (I2C Port set to 2)', cmd_lux),
    Cmd('wand', 'Wand (I2C Port set to 1)', cmd_wand)
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
        req_cmd = raw_input("[{}-{}] >> ".format(DUT,PTS))
        try:
            if req_cmd == '':
                continue
            elif req_cmd == 'exit':
                break
            elif req_cmd in ('.help', '.?', '.'):
                for cmd in cmd_list:
                    print "  .{} - {}".format(cmd.name, cmd.desc)
                print "  exit - Exit"
                print "  help"
            elif req_cmd[0]=='.':
                req_cmd = req_cmd[1:].split(' ')
                
                for cmd in cmd_list:
                    if req_cmd[0] == cmd.name:
                        if len(req_cmd)==1:
                            cmd.func()
                            break
                        else:
                            para = req_cmd[1:]
                            cmd.func(para)
                            break
            else:
                ser.write(req_cmd+"\n")
                for line in ser:
                    print line
        except:
            print "ERROR!"


if __name__ == "__main__":
    console()
