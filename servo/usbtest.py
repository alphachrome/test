#!/usr/local/conda2/bin/python
import os, sys
from time import sleep, time
import subprocess
from random import random
import serial

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
        
def run_testscript1():
    n=0
    while True:
        n=n+1
        serv.delay=int(random()*20)
        slp = random()*1
        print "Test #{}: sleep={:.0f}ms".format(n, slp*1000)
        serv.up()
        sleep(random()*5)
        serv.dn()
        sleep(0.25)
        while True:
            lsusb = subprocess.check_output('lsusb', shell=True)
            if lsusb.find("18d1:502d"):
                break
            
serv = Servo(110,96,75,88,delay=5)
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
    elif cmd=='t1':
                run_testscript1()        
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
                
            elif c=='q':
                
                break
