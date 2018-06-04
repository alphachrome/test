import time
from os import listdir

import serial
import usbtmc


def get_serial_dev():
    dev_path="/dev/serial/by-id/"
    try:
        retval = [dev_path+f for f in listdir(dev_path)]
        return retval
    except:
        return []

# Digital Meter
class Prova803:
    def __init__(self): 
        self.instr = serial.Serial("/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0", 9600, timeout=0.5)
        time.sleep(0.5)
        self.instr.write("?")
        time.sleep(1)
        
        v = self.instr.readline().rstrip().split(' ')
        if v==[""]:
            print ("[ERROR] Prova 803 no response!")

    # Get voltage, ch='1' or '2' for CH1 or CH2
    def get_volt(self, ch):
        for i in range(5):
            v = self.instr.readline().rstrip().split(' ')
            print (v)
            if v[0]=="CH{}".format(ch):
                if v[2]=="OL":
                    return -9999
                else:
                    if v[3]=="mV":
                        return float(v[2])*0.001
                    else:
                        return float(v[2])
            
    def ask(self,cmd):
        self.write(cmd)
        return self.instr.readline()

    def write(self, cmd):
        self.instr.write(cmd+'\n')
        
if False:
    dm=Prova803()
    print ("CH1: {}V".format(dm.get_volt(1)))
    print ("CH2: {}V".format(dm.get_volt(2)))

# Power Supply (Tested: GPD-4303S)
class GPD:
    def __init__(self):

        self.instr = serial.Serial("/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A105VUF2-if00-port0", 9600, timeout=0.5)        
        #self.instr = serial.Serial("/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A602R300-if00-port0", 9600, timeout=0.5)        
        #self.instr = serial.Serial("/dev/ttyUSB1", 9600, timeout=0.5)
        #self.instr = serial.Serial("/dev/ttyS1", 9600, timeout=0.5)
        print (">>",self.ask("*IDN?"))
        print (self.write("ISET1:2.50"))
    

    def set_curr(self, ch, curr):
        self.write("ISET{}:{}".format(ch,curr))

    def set_volt(self, ch, volt):
        self.write("VSET{}:{}".format(ch,volt))
        
    def get_curr(self, ch):
        return float(self.ask("IOUT{}?".format(ch)).rstrip()[:-1])

    def set_output(self, onoff):
        self.write("OUT{}".format(onoff))        

    def ask(self,cmd):
        self.write(cmd)
        return self.instr.readline()

    def write(self, cmd):
        self.instr.write(cmd+'\n')


## Testing...
if False:
    power = GPD()
    power.set_curr(1,1.10)
    power.set_curr(2,2.2)
    for i in range(4):
        print (power.get_curr(i+1))

# Multimeter
IDN_BK2831="2831E  Multimeter"
class BK2831:
    def __init__(self):
        for ser_dev in get_serial_dev():
            self.instr = serial.Serial(ser_dev, 9600, timeout=0.1)
            self.instr.flush()
            self.instr.close()
            self.instr = serial.Serial(ser_dev, 9600, timeout=0.1)
            
            try:
                idn = self.ask("*IDN?")
            except:
                self.instr.close()
                continue
            
            if idn != None:        
                if idn[0:len(IDN_BK2831)]==IDN_BK2831:
                    print (">> Found MM: {}".format(idn))
                    self.write(":VOLT:DC:NPLC 1")
                    self.write("FUNC VOLT:DC")
                    self.write("VOLT:DC:STAT ON")
                    return                    

            self.instr.close()
            
        print ("BK2831 not found!")

    def close(self):
        self.instr.close()

    def ask(self,cmd):
        for i in range(3):
            self.instr.write(cmd+"\n")
            time.sleep(0.1)
            retval = self.instr.readline()
            if retval:
                return retval

        if cmd!="*IDN?":
            print ("BK2831 no response!")
            raise

    def write(self,cmd):
        self.instr.flush()
        self.instr.write(cmd+"\n")
        self.instr.flush()
        
    def get_volt(self):
        self.ask(":VOLT:DC:REF?")
        self.ask(":VOLT:DC:REF?")
        self.write("VOLT:DC:REF:ACQ")
        time.sleep(0.5)   # Need 0.5sec for ACQ...
        self.ask(":VOLT:DC:REF?")
        self.ask(":VOLT:DC:REF?")
        return self.ask(":VOLT:DC:REF?")

# Scope
class DS1000:
    def __init__(self):
        self.instr = usbtmc.Instrument(0x1ab1,0x0588)
        self.MEAS = ['VPP', 'VMAX', 'VMIN', 'VAMP', 'VTOP', 'VBAS', 'VAV', 'VRMS',
                     'OVER', 'PRES', 'FREQ', 'RIS', 'FALL', 'PER', 'PWID', 'NWID',
                     'PDUT', 'NDUT', 'PDEL', 'NDEL']
        print ("=> Multimeter: {}".format(self.instr.ask("*IDN?")))
    def meas(self, m):
        return self.instr.ask(":MEAS:{}?".format(m))
    def get_vpp(self):
        return self.instr.ask(":MEAS:VPP?")
    def get_duty(self):
        return self.instr.ask(":MEAS:PDUT?")
    def scpi(self, cmd):
        return self.instr.ask(cmd)
    def set_time(self, div):
        self.instr.write(":TIM:SCAL {}".format(div))
    def set_vdiv(self, ch, rng):
        self.instr.write(":CHAN{}:SCAL {}".format(ch, rng))
    def set_offset(self, ch, offset):
        self.instr.write(":CHAN{}:OFFS {}".format(ch, offset))
    def run(self):
        self.instr.write(":RUN")
    def stop(self):
        self.instr.write(":STOP")
    def auto(self):
        self.instr.write(":AUTO")
if False:
    scope=DS1000()
    scope.set_time("10u")
    

class DS1054Z():
    def __init__(self):
        self.instr = usbtmc.Instrument(0x1ab1,0x04ce)
        self.MEAS = ['VPP', 'VMAX', 'VMIN', 'VAMP', 'VTOP', 'VBAS', 'VAV', 'VRMS',
                     'OVER', 'PRES', 'FREQ', 'RIS', 'FALL', 'PER', 'PWID', 'NWID',
                     'PDUT', 'NDUT', 'PDEL', 'NDEL']
        print ("=> Scope: {}".format(self.instr.ask("*IDN?")))

if False:
    scope=DS1054Z()
    scope.set_time("10u")


# Power supply DP71x
IDN_DP71x="RIGOL TECHNOLOGIES,DP71"
class DP71x:
    def __init__(self): 
        for ser_dev in get_serial_dev():
            print ("Trying: {}".format(ser_dev))
            
            try:
                for i in range(5):
                    self.instr = serial.Serial(ser_dev, 14400, timeout=0.5)
                    idn = self.ask("*IDN?")
                    print ("Try #{}: {}".format(i, idn))
                    if idn!=None:        
                        if idn[0:len(IDN_DP71x)]==IDN_DP71x:
                            print (">> Found PS: {}".format(idn))
                            self.write(":SYST:REM")
                            time.sleep(0.5)
                            return
            except:
                print ("exception!")
                self.instr.close()
                continue
            self.instr.close()
            
        print ("DP71x not found!")

    def ask(self,cmd):
        for i in range(3):
            self.instr.flush()
            self.instr.write(cmd+"\n")
            self.instr.flush()
            time.sleep(0.1)
            retval = self.instr.readline()
            if retval:
                return retval
        if cmd!="*IDN?":
            print ("DP71x no response!")
            raise
    
    def write(self,cmd):
        self.instr.flush()
        self.instr.write(cmd+"\n")
        self.instr.flush()
    
    def set_output(self, onoff):
        self.write("OUTP:STAT {}".format(onoff))
        time.sleep(0.1)

    def set_volt(self, volt, check=True):
        self.write(":SOUR:VOLT:LEV {}".format(volt))

    def set_volt_check(self, volt, check=True):
        if check:
            for i in range(10):
                print ("{}".format('.'))
                self.write(":SOUR:VOLT:LEV {}".format(volt))
                #self.write(":APPL {}".format(volt))
                time.sleep(0.5)
                v = float(self.ask(":MEAS:VOLT?"))
                if abs(v-volt) < 0.005:
                    return
                else:
                    time.sleep(0.1)
                    self.write(":SOUR:VOLT?")
                    time.sleep(1)
            else:
                self.write(":SOUR:VOLT:LEV {}".format(volt))
                
    def set_curr(self, curr):
        self.write(":SOUR:CURR:LEV {}".format(curr))

    def get_curr(self):
        for i in range(10):
            self.ask(":MEAS:CURR?")
            curr1 = float(self.ask(":MEAS:CURR?"))
            time.sleep(1)
            curr2 = float(self.ask(":MEAS:CURR?"))
            if abs(curr1-curr2)< 0.005:
                return curr2
            time.sleep(0.1)
            self.ask(":MEAS:CURR?")
            time.sleep(1)
            print ("[WARNING] DP71x: get_curr()")
        print ("[WARNING] DP71x: Output current is not stable!")
        return curr2
    def close(self):
        self.instr.close()
    
# Rigol DM3058E Multimeter
class DM3058:
    def __init__(self):
        # Digital multimeter DM3058E
        self.instr = usbtmc.Instrument(0x1ab1, 0x09c4)
        print ("=> Multimeter: {}".format(self.instr.ask("*IDN?")))
        self.instr.write(":FUNC:VOLT:DC")
    def get_volt(self):
        return float(self.instr.ask(":MEAS:VOLT:DC?"))

# Keysight 34470A Multimeter
class KS34470:
    def __init__(self):
        # Digital multimeter DM3058E
        self.instr = usbtmc.Instrument(0x2a8d, 0x0201)
        print ("=> Multimeter: {}".format(self.instr.ask("*IDN?")))
        self.instr.write(":FUNC:VOLT:DC")
    def get_volt(self):
        return float(self.instr.ask(":MEAS:VOLT:DC?"))


# DC Electrical Load
class BK8600:
    def __init__(self):
        self.instr = usbtmc.Instrument(0xffff,0x8800)
        print("=> Dcload: {}".format(self.instr.ask("*IDN?")))
        self.instr.write(":SYST:REM")
    def scpi_ask(self, cmd):
        self.instr.ask(cmd)
    def scpi_write(self, cmd):
        self.instr.write(cmd)
    def set_remsens(self, onoff):
        self.instr.write("REM:SENS {}".format(onoff))
    def set_input(self, onoff):
        self.instr.write(":SOUR:INP:STAT {}".format(onoff))
    def set_cc(self, curr):
        self.instr.write("FUNC CURR")
        self.instr.write(":SOUR:CURR:LEV {:.3f}".format(curr))
    def set_cw(self, pwr):
        self.instr.write("FUNC POW")
        self.instr.write(":SOUR:POW:LEV {:.2f}".format(pwr))
    def set_cr(self, res):
        self.instr.write("FUNC RES")
        self.instr.write(":SOUR:RES:LEV {:.2f}".format(res))
    def trigger(self):
        self.instr.write("*TRG")

    def set_tran_off(self):
        self.instr.write(":SOUR:TRAN OFF")
         
    # awid/bwid: 20us to 3600s (unit: S)
    # rise/fall: (unit: A/us)
    def set_tran(self, alev=1, blev=0.5, awid=0.05, bwid=0.05, pos=1, neg=1, mode="CONT"):
        self.instr.write(":CURR:TRAN:MODE {}".format(mode))
        self.instr.write(":CURR:TRAN:ALEV {}".format(alev))
        self.instr.write(":CURR:TRAN:BLEV {}".format(blev))
        self.instr.write(":CURR:TRAN:AWID {}".format(awid))
        self.instr.write(":CURR:TRAN:BWID {}".format(bwid))
        self.instr.write(":CURR:SLEW:POS {}".format(pos))
        self.instr.write(":CURR:SLEW:NEG {}".format(neg))
        self.instr.write(":TRIG:SOUR BUS")
        self.instr.write(":SOUR:TRAN ON") 
        print ("[DP71x] Set Transient: ALEV={}A, BLEV={}A, AWID={}s, BWID={}s, SLEW_POS={}A/us, SLEW_NEG={}A/us; FREQ={}Hz, DUTY={:.1f}%"
               .format(alev, blev, awid, bwid, pos, neg, 1/(awid+bwid), awid/(awid+bwid)))

    def get_volt(self):
        for i in range(10):
            v1 = float(self.instr.ask(":MEAS:VOLT?"))
            time.sleep(0.5)
            v2 = float(self.instr.ask(":MEAS:VOLT?"))
            if abs(v2-v2)<0.005:
                return v2
        print ("[WARNING] BK8600: Load voltage is not stable!")
    def get_curr(self):
        return float(self.instr.ask(":MEAS:CURR?"))

# Rigol DL3021A DC Electrical Load
IDN_DL3021="RIGOL TECHNOLOGIES"

class DL3021:
    def __init__(self):
        self.instr = usbtmc.Instrument('USB::6833::3601::INSTR')
        print("=> Dcload: {}".format(self.instr.ask("*IDN?")))
    #def __init__(self): 
        for ser_dev in get_serial_dev():
            print ("Trying: {}".format(ser_dev))
            
            try:
                for i in range(5):
                    self.instr = serial.Serial(ser_dev, 19200, timeout=1)
                    idn = self.ask("*IDN?")
                    print (idn)
                    if idn:
                        continue
            except:
                self.instr.close()
                continue
            print (idn)

            if idn:        
                if idn[0:len(IDN_DL3021)]==IDN_DP71x:
                    print (">> Found PS: {}".format(idn))
                    self.write(":SYST:REM")
                    time.sleep(0.5)
                    return

            self.instr.close()
            
        print ("DL3021 not found!")
    def ask(self,cmd):
        for i in range(3):
            self.instr.write(cmd+'\n')
            time.sleep(0.1)
            retval = self.instr.readline()
            if retval:
                return retval
        
    def scpi_ask(self, cmd):
        self.instr.ask(cmd)
    def scpi_write(self, cmd):
        self.instr.write(cmd)
    def set_remsens(self, onoff):
        self.instr.write("REM:SENS {}".format(onoff))
    def set_input(self, onoff):
        self.instr.write(":SOUR:INP:STAT {}".format(onoff))
    def set_cc(self, curr):
        self.instr.write("FUNC CURR")
        self.instr.write(":SOUR:CURR:LEV {:.3f}".format(curr))
    def set_cw(self, pwr):
        self.instr.write("FUNC POW")
        self.instr.write(":SOUR:POW:LEV {:.2f}".format(pwr))

    def get_volt(self):
        for i in range(10):
            v1 = float(self.instr.ask(":MEAS:VOLT?"))
            time.sleep(0.5)
            v2 = float(self.instr.ask(":MEAS:VOLT?"))
            if abs(v2-v2)<0.005:
                return v2
        print ("[WARNING] BK8600: Load voltage is not stable!")
    def get_curr(self):
        return float(self.instr.ask(":MEAS:CURR?"))

if __name__ == "__main__":
    
    print ("")

if False:
    #dm = KS34470()
    load = BK8600()
    load.set_cc(1)
    print (load.get_curr())
    print (load.get_volt())
    #dm = BK2831()
    power = DP71x()
    #dm = BK2831()
    #istofdev = usbtmc.list_devices()
    #print listofdev
    
    #load = DL3021()

if False:
    load = BK8600()
    load.set_tran(alev=2, blev=1, awid=0.003, bwid=0.003, pos=2, neg=2)
    load.set_input("ON")
    time.sleep(0.5)
    load.trigger()
    load.trigger()

if False:
    #ps = DP71x()
    #mm = BK2831()
    #print "mm",mm.get_volt()
    ps.set_volt(15)
    print ("ps",ps.get_curr())
    while True:
       for i in range(5,20):
           ps.set_volt(i)
           #print "set to", i
           time.sleep(0.5)
           print (i, ps.get_curr())
      #mm = DM3058()
      #print mm.get_volt()
##
##    load = BK8600()
##    print load.get_volt()
##    print load.get_curr()
##
##    ps = DP71x()
##    print ps.get_curr()
