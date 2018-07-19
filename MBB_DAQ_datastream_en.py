# -*- coding: utf-8 -*-
"""
File Name: Main.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 1/13/2018 3:05:03 PM
Last modified: Sat Jul  7 13:25:21 2018
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

for lastip in ["209"]:
    print ("Enable data stream to DAQ from MBB")
    wib.UDP_IP = "131.225.150." +  lastip
    print wib.UDP_IP
    time.sleep(0.5)
    a =  wib.read_reg_wib(0x1)
    a =  wib.read_reg_wib(0x1)
    if ( a & 0x04 == 0):
        time.sleep(0.5)
        wib.write_reg_wib(1, 8)
        wib.write_reg_wib(1, 8)


    wib.write_reg_wib(1, 4)
    time.sleep(1)
    wib.write_reg_wib(1, 4)
    time.sleep(1)
    print wib.read_reg_wib(1)



