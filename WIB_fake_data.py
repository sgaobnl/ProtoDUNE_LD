# -*- coding: utf-8 -*-
"""
File Name: Main.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 1/13/2018 3:05:03 PM
Last modified: Tue Jun 26 15:06:06 2018
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
for lastip in ["203", "206"]:
    if lastip == "203":
        wibno = 0
    else:
        wibno = 1
    wib.UDP_IP = "131.225.150." +  lastip
    runtime =  datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    print  "BNL_WIB%d_IP >> "%wibno +wib.UDP_IP 
    print ( "BNL_check_time >> " + runtime )
    print ( "WIB fake data mode. Power for FEMBs will be turned off!!!" )
    wib.write_reg_wib(9, 0x20)
    wib.write_reg_wib(8, 0x0)
    print ("DONE")


