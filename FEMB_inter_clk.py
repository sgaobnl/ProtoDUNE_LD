# -*- coding: utf-8 -*-
"""
File Name: Main.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 1/13/2018 3:05:03 PM
Last modified: Wed Sep  5 17:51:02 2018
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

wib.UDP_IP = "192.168.100." + "11"  
print hex(wib.read_reg_wib (0xFF ) )
time.sleep(0.1) 
for femb_addr in range(4):
    print hex( wib.read_reg_femb (femb_addr, 0x101 ) )
    time.sleep(0.1) 
    wib.write_reg_femb (femb_addr, 8, 0x10010 ) 
    time.sleep(5) 
    print femb_addr, hex(wib.read_reg_femb (femb_addr, 8 )) 

wib.UDP_IP = "192.168.100." + "12"  
print hex(wib.read_reg_wib (0xFF ) )
time.sleep(0.1) 
for femb_addr in range(1):
    print hex( wib.read_reg_femb (femb_addr, 0x101 ) )
    time.sleep(0.1) 
    wib.write_reg_femb (femb_addr, 8, 0x10010 ) 
    time.sleep(5) 
    print femb_addr, hex(wib.read_reg_femb (femb_addr, 8 )) 


