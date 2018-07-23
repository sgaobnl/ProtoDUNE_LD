# -*- coding: utf-8 -*-
"""
File Name: Main.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 1/13/2018 3:05:03 PM
Last modified: Fri Jul  6 18:56:03 2018
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


for i in range(1):
    for lastip in ["11", "12"]:
        wib.UDP_IP = "192.168.100." +  lastip
        print wib.UDP_IP
        time.sleep(1)
        print wib.read_reg_wib(0xFF)
        wib.write_reg_wib(20, 0)
        wib.write_reg_wib(20, 0)
        print wib.read_reg_wib(20)
        time.sleep(0.1)
        wib.write_reg_wib(20, 2)
        wib.write_reg_wib(20, 2)
        print wib.read_reg_wib(20)
        time.sleep(0.1)
        wib.write_reg_wib(20, 0)
        wib.write_reg_wib(20, 0)
        time.sleep(0.1)
        print wib.read_reg_wib(20)

