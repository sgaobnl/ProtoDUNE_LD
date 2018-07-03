# -*- coding: utf-8 -*-
"""
File Name: Main.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 1/13/2018 3:05:03 PM
Last modified: Mon Jul  2 14:01:56 2018
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

for lastip in ["203", "206"]:
    wib.UDP_IP = "131.225.150." +  lastip
    time.sleep(1)
    print wib.read_reg_wib(0x100)
    time.sleep(1)
    wib.write_reg_wib(20, 2)
    time.sleep(1)
    wib.write_reg_wib(20, 2)
    time.sleep(1)
    print wib.read_reg_wib(20)

print "Wait 300seconds"
time.sleep(300)

for lastip in ["203", "206"]:
    wib.UDP_IP = "131.225.150." +  lastip
    time.sleep(1)
    wib.write_reg_wib(20, 0)
    time.sleep(1)
    wib.write_reg_wib(20, 0)
    time.sleep(1)
    print wib.read_reg_wib(20)


