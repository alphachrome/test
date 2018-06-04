# Efficiency versus Load Current, given Vin and Vout
#
#  Input parameters:
#    DUT: use for filename prefix
#    VIN: Will program the DP71x to VIN for all test points
#    VOUT: VSYS voltage of DUT (set by other software)
#  Calculated:
#    NUM_OF_PTS: Number of test points
#  Outputs:
#    {DUT}_Vin{VIN)V_Vout{VOUT}.csv
#    {DUT}_Vin{VIN)V_Vout{VOUT}.png 
#
#  Setup:
#     DP71x => VIN => DUT => VOUT => BK8600
#     DP71x power to VIN of DUT
#     BK8600 load to VOUT of DUT
#     BK8600 remote sense to VOUT
#     DM3058E meter to VIN of DUT

import time
import numpy as np
import serial
import usbtmc
from matplotlib import pyplot as plt
from myinstruments import GPD, BK8600, KS34470

#DUT="ISL9238B_CMGB102T-2R2MS_1MHz"
DUT="OCTOPUS_ITE_LAIRD"

#DUT="back-to-back"
VOUT = 12
VIN = 15

IIN_MAX = 2.95

# Vin: Iout_Max
##IOUT_MAX = {
##    5: PMAX/5,
##    9: PMAX/9,
##    12: PMAX/12,
##    15: PMAX/15,
##    20: PMAX/20
##    }

ILOAD_START = 0.1
#ILOAD_END = 2
ILOAD_END = float(VIN)*IIN_MAX/VOUT


NUM_OF_PTS = 21

#ILOAD_END = IOUT_MAX[VIN]
#NUM_OF_PTS = (ILOAD_END-ILOAD_START-0.5)*10+1

print "Testing: VIN={}V, VOUT={}V, ILOAD={}A-{}A, NUM_OF_PTS={}".format(VIN,VOUT,ILOAD_START,ILOAD_END,NUM_OF_PTS)


# Start testing...
power = GPD()
#meter = DM3058()
meter = KS34470()
#meter = BK2831()
load = BK8600()
l1= np.linspace(0,0.2,num=6)
l2= np.linspace(0.2, ILOAD_END*0.8, num=NUM_OF_PTS)
Iload_scan = l1.tolist()[:-2] + l2.tolist()

#Iload_scan = np.linspace(0,0.5,num=10)
#Iload_scan = np.concatenate((Iload_scan[:-2], np.linspace(0.5, ILOAD_END, num=NUM_OF_PTS))) 
#Iload_scan += numpy.linspace(ILOAD_START, ILOAD_END, num=NUM_OF_PTS)

Iload_scan = np.linspace(ILOAD_START,ILOAD_END, num=int(ILOAD_END/0.1))
print Iload_scan

power.set_volt(1,VIN)
power.set_curr(1,3.1)
power.set_output(1)

load.set_cc(0.01)
load.set_input('ON')
load.set_remsens('ON')

plt.axis([ILOAD_START, ILOAD_END, 85, 99])
plt.xlabel('IOUT (A)')
plt.ylabel('EFFICIENCY (%)')
plt.grid()
plt.ion()

vin_l=[]
pin_l=[]
pout_l=[]
eff_l=[]
loss_l=[]

with open("{}_Vin{}V_Vout{}V.csv".format(DUT, VIN, VOUT), "w") as f:

    f.write("Vin_V,Vout_V,Iin_A,Iout_A,Pin_W,Pout_W,Eff_%\n")

    for Iload in Iload_scan:
        
        print "I_LOAD: {:.2f}A-->".format(Iload)
        load.set_cc(Iload)
        time.sleep(2.5)
        
        vout= float(load.get_volt())
        iout= float(load.get_curr())
        pout = vout*iout
        
        vin = float(meter.get_volt())
        iin = float(power.get_curr(1))

        pin = vin*iin
        eff = pout/pin*100
        loss = (100-eff)/100*pin

        vin_l.append(vin)
        pin_l.append(pin)
        pout_l.append(pout)
        eff_l.append(eff)
        loss_l.append(loss)
        
        print "      --Vin:{:.2f}V--Iin:{:.2f}A--Vout:{:.2f}V--Iout:{:.3f}A--Pin:{:.3f}W--Pout:{:.3f}--Loss:{:.2f}--Eff:{:.2f}%".format(vin, iin, vout, iout, pin, pout, loss,eff)
        plt.scatter(Iload, eff, marker='s', alpha=0.5)
        plt.pause(0.05)

        f.write("{},{},{},{},{},{},{}\n".format(vin,vout,iin,iout,pin,pout,eff))

        if iin>=IIN_MAX or iout>=7:
            Iload_scan = np.array(Iload_scan)
            Iload_scan = Iload_scan[Iload_scan <= Iload]
            print "Input overcurrent!"
            break

print "Done!"
load.set_cc(0)

plt.ioff()
plt.close()

## Plot and save figures
fig, ax = plt.subplots(2, figsize=(8,12))

ax[0].plot(Iload_scan, eff_l, 'b-x')    
#ax[0].set_xlabel('Iout (A)')
ax[0].set_ylabel('EFFICIENCY (%)', color='b')

ax[0].axis([ILOAD_START, ILOAD_END, 85, 99])

major_ticks = np.arange(80, 101, 5)
minor_ticks = np.arange(80, 101, 1)
ax[0].set_yticks(major_ticks)
ax[0].set_yticks(minor_ticks, minor=True)

ax[0].grid(which='minor', alpha=0.7)
ax[0].grid(which='major')

ax[1].plot(Iload_scan, loss_l, 'r:x')
ax[1].set_xlabel('IOUT (A)')
ax[1].set_ylabel('LOSS (W)', color='r')

ax[1].axis([ILOAD_START, ILOAD_END, 0, 5])

major_ticks = np.arange(0, 5.1, 0.5)
minor_ticks = np.arange(0, 5, 0.1)
ax[1].set_yticks(major_ticks)   
ax[1].set_yticks(minor_ticks, minor=True)


ax[1].grid(which='minor', alpha=0.7)
ax[1].grid(which='major')

#fig.tight_layout()
plt.savefig("{}_Vin{}V_Vout{}V.png".format(DUT, VIN, VOUT))
plt.show()
