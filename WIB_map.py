# -*- coding: utf-8 -*-
"""
File Name: Main.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 1/13/2018 3:05:03 PM
Last modified: Mon Jul 23 14:28:42 2018
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

logs = []

#for lastip in ["203", "206"]:
for lastip in ["11"]:
#for lastip in ["206"]:
    if lastip == "203":
        wib_pos = 0
    else:
        wib_pos = 1

    wib.UDP_IP = "192.168.100." +  lastip
    runtime =  datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    logs.append ( "BNL_check_time >> " + runtime )
    print ( "BNL_check_time >> " + runtime )
    version = wib.read_reg_wib(0xFF)
    print hex(version)
    time.sleep(1)

    for fembno in range(4):
        version = wib.read_reg_femb (fembno, 0x101)
        print "FEMB%d"%fembno
        print hex(version)
        lar_fembno = (((wib_pos*4 + fembno)&0x0F)<<4) + 3
        wib.write_reg_femb (fembno, 42, 0 )
        time.sleep(1)
        b = wib.read_reg_femb (fembno, 42 )
        time.sleep(1)


