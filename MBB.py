# -*- coding: utf-8 -*-
"""
File Name: Main.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 1/13/2018 3:05:03 PM
Last modified: Thu May  9 14:48:02 2019
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
    #for lastip in ["209"]:
    for lastip in ["11"]:
        wib.UDP_IP = "192.168.121." +  lastip
        #wib.UDP_IP = "131.225.150." +  lastip
        print wib.UDP_IP
        time.sleep(1)
        print wib.read_reg_wib(1)
        print wib.read_reg_wib(2)
        wib.write_reg_wib(1, 2)
        time.sleep(1)
        print wib.read_reg_wib(1)
        wib.write_reg_wib(1, 0)
        time.sleep(1)
        print wib.read_reg_wib(1)
 

