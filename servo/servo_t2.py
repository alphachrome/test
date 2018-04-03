#!/usr/local/conda2/bin/python
import os, sys
from time import sleep, time
import subprocess
from random import random
import serial
import numpy as np

class Getch:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
getch = Getch()

def sysvar(filename):
    try:
        with open(filename, 'r') as fd:
            s = fd.readline().rstrip()
            return int(s) if s.isdigit() else s
    except:
        return 0

dev_path="/dev/serial/by-id/"
try:
    ser_dev_list = [dev_path+f for f in os.listdir(dev_path)]
except:
    print "{}: No file found!".format(dev_path)
    quit()

ser=None
if len(ser_dev_list)>0:
    for ser_dev in ser_dev_list:
        print ("Found {}".format(ser_dev))
        if ser_dev.find("Arduino"):
            print ser_dev
            ser = serial.Serial(ser_dev, baudrate=9600, timeout=0.1)
            break

if ser==None:
    print ("Usb-Arduino not found!")
    quit()

class Servo:
    def __init__(self, a_up=80, a_dn=100, b_up=80, b_dn=100, delay=0):
        self.delay = delay
        self.pos_a = a_dn
        self.pos_b = b_dn
        self.A_UP = a_up
        self.A_DN = a_dn
        self.B_UP = b_up
        self.B_DN = b_dn

    def update(self):
        print '   ser.write("{},{},{}\\r")'.format(self.delay, self.pos_a, self.pos_b)
        ser.write("{},{},{}\r".format(self.delay, self.pos_a, self.pos_b))
                  
    def a_up(self):
        self.pos_a = self.A_UP
        self.update()

    def a_dn(self):
        self.pos_a = self.A_DN
        self.update()                

    def b_up(self):
        self.pos_b = self.B_UP
        self.update()

    def b_dn(self):
        self.pos_b = self.B_DN
        self.update()

    def dn(self):
        self.pos_a = self.A_DN
        self.pos_b = self.B_DN
        self.update()

    def up(self):
        self.pos_a = self.A_UP
        self.pos_b = self.B_UP
        self.update()

def test_kbd():
    """return only after keyboard found"""
    while True:
        lsusb = subprocess.check_output('lsusb', shell=True)
        if lsusb.find("18d1:502d"):
            print "   Found base keyboard!"
            break 

def bat1_presence():
    return os.path.exists("/sys/class/power_supply/BAT1")
            
def test_bat1():
    """return only after BAT1 found"""
    while not bat1_presence():
        sleep(0.1)
    print "   Found BAT1!"

def batinfo():
    print "   BAT0:"
    print "      status="+sysvar('/sys/class/power_supply/BAT0/status')
    print "      voltage_now={:.3f}V".format(sysvar('/sys/class/power_supply/BAT0/voltage_now')/1e6)
    print "      current_now={:.3f}A".format(sysvar('/sys/class/power_supply/BAT0/current_now')/1e6)
    print "      capacity={}%".format(sysvar('/sys/class/power_supply/BAT0/capacity'))    
    print "   BAT1:"
    print "      status="+sysvar('/sys/class/power_supply/BAT1/status')
    print "      voltage_now={:.3f}V".format(sysvar('/sys/class/power_supply/BAT1/voltage_now')/1e6)
    print "      current_now={:.3f}A".format(sysvar('/sys/class/power_supply/BAT1/current_now')/1e6)
    print "      capacity={}%".format(sysvar('/sys/class/power_supply/BAT1/capacity'))

 
SERV_DELAY_MAX=20
UP_SLEEP_MAX=2.5
DN_SLEEP_MAX=10
def run_testscript2():
    n=0
    while True:
        if True:
            n=n+1
            serv.delay=int(random()*SERV_DELAY_MAX)
            slp = random()*UP_SLEEP_MAX
            print "Test #{}: servo.delay={}".format(n,serv.delay)
            serv.up()
            print "   Sleep for {:.0f}ms".format(slp*1000)        
            sleep(slp)
            serv.dn()
            test_kbd()
            test_bat1()
            slp = random()*DN_SLEEP_MAX
            print "   Sleep for {:.0f}ms".format(slp*1000)
            sleep(slp)
            batinfo()
        if True:
            n=n+1
            serv.delay=int(random()*SERV_DELAY_MAX)
            slp = random()*UP_SLEEP_MAX

            print "Test #{}: servo.delay={}".format(n,serv.delay)
            serv.a_up()
            print "   Sleep for {:.0f}ms".format(slp*1000)
            sleep(slp)
            serv.a_dn()
            test_kbd()
            test_bat1()
            slp = random()*DN_SLEEP_MAX
            print "   Sleep for {:.0f}ms".format(slp*1000)
            sleep(slp)
            batinfo()
            
        if True:
            n=n+1
            serv.delay=int(random()*SERV_DELAY_MAX)
            slp = random()*UP_SLEEP_MAX
            print "Test #{}: servo.delay={}".format(n,serv.delay)

            serv.b_up()
            print "   Sleep for {:.0f}ms".format(slp*1000)        
            sleep(slp)
            serv.b_dn()
            test_kbd()
            test_bat1()
            slp = random()*DN_SLEEP_MAX
            print "   Sleep for {:.0f}ms".format(slp*1000)
            sleep(slp) 
            batinfo()
            
def run_testscript3():
    serv.delay=17
    n=0
    while True:
        # a
        n=n+1
        slp = 2+random()*0.255     
        print "Test {}: Attached for {:.4f}s".format(n,slp)       
        serv.a_up()
        sleep(2)
        serv.a_dn()
        test_bat1()       
        sleep(slp)
        serv.a_up()
        while bat1_presence():
            pass
        sleep(2)
        serv.a_dn()
        test_bat1()
        # b
        n=n+1
        slp = 2+random()*0.255     
        print "Test {}: Attached for {:.4f}s".format(n,slp)     
        serv.b_up()
        sleep(2)
        serv.b_dn()
        test_bat1()       
        sleep(slp)
        serv.b_up()
        while bat1_presence():
            pass       
        sleep(2)
        serv.b_dn()
        test_bat1()
        # ab
        n=n+1
        slp = 2+random()*0.255     
        print "Test {}: Attached for {:.4f}s".format(n,slp)      
        serv.up()
        sleep(2)
        serv.dn()
        test_bat1()       
        sleep(slp)
        serv.up()
        while bat1_presence():
            pass       
        sleep(2)
        serv.dn()
        test_bat1()

serv = Servo(115,96,70,88,delay=5)
serv.a_dn()
serv.b_dn()

d=15
while True:
    
    cmd = raw_input('RC> ')
    
    if cmd=='q':
        ser.close()
        break
    elif cmd=='ad':
        serv.a_dn()
    elif cmd=='au':
        serv.a_up()
    elif cmd=='bd':
        serv.b_dn()
    elif cmd=='bu':
        serv.b_up()
    elif cmd[0:2]=='aa':
        ser.write("{},{},{}\r".format(serv.delay,cmd[2:],serv.pos_b))
    elif cmd[0:2]=='bb':
        ser.write("{},{},{}\r".format(serv.delay,serv.pos_a,cmd[2:]))
    elif cmd=='t2':
        run_testscript2()     
    elif cmd=='t3':
        run_testscript3()
    elif cmd=='s':
        while True:
            c = getch()
            if c=='1':
                serv.delay = 0
                if serv.pos_a==serv.A_DN:
                    serv.a_up()
                else:
                    serv.a_dn()
            elif c=='2':
                serv.delay = 0
                if serv.pos_a==serv.A_DN:
                    serv.up()
                else:
                    serv.dn()
            elif c=='3':
                serv.delay = 0
                if serv.pos_b==serv.B_DN:
                    serv.b_up()
                else:
                    serv.b_dn()
            elif c=='4':
                serv.delay = d
                if serv.pos_a==serv.A_DN:
                    serv.a_up()
                else:
                    serv.a_dn()
            elif c=='5':
                serv.delay = d
                if serv.pos_a==serv.A_DN:
                    serv.up()
                else:
                    serv.dn()
            elif c=='6':
                serv.delay = d
                if serv.pos_b==serv.B_DN:
                    serv.b_up()
                else:
                    serv.b_dn()  
            elif c=='+':
                d=d+1
                print "  d={}".format(d)
            elif c=='-':
                d=d-1
                print "  d={}".format(d)
            elif c=='8':
                print "A_UP=",serv.A_UP
                serv.A_UP=serv.A_UP-1
                serv.a_up()
            elif c=='/':
                print "A_UP=",serv.A_UP
                serv.A_UP=serv.A_UP+1
                serv.a_up()
            elif c=='9':
                print "B_UP=",serv.B_UP
                serv.B_UP=serv.B_UP-1
                serv.b_up()
            elif c=='*':
                print "B_UP=",serv.B_UP
                serv.B_UP=serv.B_UP+1
                serv.b_up()                
                
            elif c=='q':
                
                break
