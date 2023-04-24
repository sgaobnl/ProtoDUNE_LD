# -*- coding: utf-8 -*-
"""
File Name: Main.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 1/13/2018 3:05:03 PM
Last modified: 4/24/2023 5:14:25 PM
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl

import os
import sys
import copy
from datetime import datetime
import numpy as np
import time
from timeit import default_timer as timer

###############################################################################
from femb_udp_cmdline import FEMB_UDP
wib= FEMB_UDP()
#for lastip in ["11", "12"]:
for lastip in ["50"]:
    if lastip == "1":
        wibno = 0
    else:
        wibno = 1
    wib.UDP_IP = "192.168.230." +  lastip
    runtime =  datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    print  "BNL_WIB%d_IP >> "%wibno +wib.UDP_IP 
    print ( "BNL_check_time >> " + runtime )
    print ( "WIB fake data mode. Power for FEMBs will be turned off!!!" )

    ver_value = wib.read_reg_wib (0xFF)
    print ("WIB Version: " + hex(ver_value))


    print ("0x0 (default): data from FEMB")
    print ("0x1: sawtooth waveform generated from WIB for even channels, fake pulse data for odd channels")
    print ("0x2: channel-mapping number = FEMB#N(0-3) * 256 + ASIC#M(0-7) * 16 + FE_chn#X(0-15)")
    print ("Please input 0, 1, 2 to select data mode")
    datamode = int(raw_input ("1, 2 (exit fake data mode with anyother values): "))

    if datamode == 1:
        wfs = [ 0x2FF, 0x2FE, 0x2FB, 0x2FF, 0x300, 0x303, 0x301, 0x301,
                0x2FF, 0x2FE, 0x2FF, 0x2FF, 0x2FF, 0x2FF, 0x2FF, 0x2FF,
                0x301, 0x301, 0x301, 0x301, 0x301, 0x301, 0x300, 0x301,
                0x301, 0x301, 0x2FF, 0x2FF, 0x2FF, 0x2FF, 0x2FF, 0x2FF,
                0x2FF, 0x2FF, 0x300, 0x2FF, 0x2FF, 0x2FF, 0x2FF, 0x300,
                0x2FF, 0x300, 0x301, 0x301, 0x301, 0x2FF, 0x2FF, 0x2FF,
                0x2FE, 0x2FE, 0x301, 0x302, 0x303, 0x301, 0x2FF, 0x2FB,
                0x2FE, 0x2FF, 0x301, 0x306, 0x304, 0x321, 0x39D, 0x455,
                0x4DF, 0x501, 0x4C1, 0x454, 0x3DF, 0x37F, 0x340, 0x31A,
                0x308, 0x300, 0x2FF, 0x2FF, 0x2FF, 0x2FF, 0x300, 0x300,
                0x2FF, 0x300, 0x301, 0x300, 0x2FF, 0x2FF, 0x2FF, 0x2FF,
                0x300, 0x2FF, 0x303, 0x301, 0x302, 0x301, 0x300, 0x2FF,
                0x2FF, 0x300, 0x2FF, 0x2FF, 0x2FF, 0x2DF, 0x264, 0x1B9,
                0x13F, 0x122, 0x150, 0x1B8, 0x228, 0x281, 0x2C3, 0x2E8,
                0x2FB, 0x2FF, 0x2FF, 0x300, 0x300, 0x301, 0x301, 0x2FF,
                0x2FF, 0x2FF, 0x300, 0x300, 0x300, 0x2FF, 0x2FF, 0x2FF,
                0x2FE, 0x2FF, 0x2FF, 0x300, 0x2FF, 0x302, 0x302, 0x301,
                0x301, 0x2FF, 0x2FE, 0x2FE, 0x2FE, 0x2FE, 0x2FD, 0x2FF,
                0x2FF, 0x2FF, 0x2FF, 0x2FE, 0x2FE, 0x2FF, 0x301, 0x304,
                0x304, 0x302, 0x2FF, 0x2FB, 0x2FA, 0x2FF, 0x300, 0x301,
                0x302, 0x301, 0x301, 0x301, 0x301, 0x301, 0x301, 0x301,
                0x301, 0x301, 0x301, 0x302, 0x301, 0x301, 0x300, 0x301,
                0x301, 0x300, 0x301, 0x301, 0x300, 0x2FF, 0x2FF, 0x2FF,
                0x301, 0x301, 0x301, 0x301, 0x301, 0x303, 0x302, 0x300,
                0x301, 0x2FF, 0x2FF, 0x2FF, 0x2FF, 0x300, 0x301, 0x301,
                0x2FF, 0x2FE, 0x2FE, 0x2FF, 0x300, 0x303, 0x306, 0x304,
                0x302, 0x2FF, 0x2FF, 0x2FF, 0x2FF, 0x2FF, 0x2FF, 0x2FF,
                0x2FF, 0x2FF, 0x301, 0x300, 0x2FF, 0x2FF, 0x301, 0x301,
                0x300, 0x2FF, 0x2FF, 0x2FF, 0x2FF, 0x2FF, 0x2FF, 0x301,
                0x303, 0x306, 0x303, 0x302, 0x2FF, 0x2FF, 0x2FF, 0x300,
                0x2FF, 0x2FF, 0x2FF, 0x301, 0x301, 0x303, 0x301, 0x2FF,
                0x2FF, 0x2FF, 0x301, 0x302, 0x304, 0x2FF, 0x2FF, 0x2FB]
        datas = []
        for i in range(256):    
            datas.append( (wfs[i]<<12) + ((i&0xfff)<<4))
        for i in range(256):
            print (i)
            adr1 = i + 0x300
            wib.write_reg_wib(adr1, datas[i])
            adr2 = i + 0x200
            wib.write_reg_wib(adr2, datas[i])
        
        wib.write_reg_wib_checked(9, 0x10)
    elif datamode == 2:
        wib.write_reg_wib_checked(9, 0x20)
    else:
        wib.write_reg_wib_checked(9, 0x0)
        print ("Back to normal mode!")
        exit()
    time.sleep(0.1)
    wib.write_reg_wib_checked(8, 0x0)
    time.sleep(0.1)
    while True:
        synflg = str(raw_input("Want to perform Nevis SYNC (Y/N)? : "))
        if  "Y" in synflg or "y" in synflg:
            wib.write_reg_wib_checked(20, 0)
            time.sleep(0.1)
            wib.write_reg_wib_checked(20, 2)
            time.sleep(0.1)
            wib.write_reg_wib_checked(20, 0)
            time.sleep(0.1)
            print ("Nevis SYNC is sent")
        else:
            quitflg = str(raw_input("Quit (Y/N)? : "))
            if  "Y" in synflg or "y" in quitflg:
                break

    print ("DONE")


