# -*- coding: utf-8 -*-
"""
File Name: Main.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 1/13/2018 3:05:03 PM
Last modified: Tue Mar 20 17:37:02 2018
"""

import os
import sys
import copy
from datetime import datetime
import numpy as np
import time
from timeit import default_timer as timer

###############################################################################
from femb_udp_cmdline import FEMB_UDP
#wib_lastbyte = sys.argv[1]
wib= FEMB_UDP()

wib.UDP_IP = "192.168.121.1" 

wib.write_reg_femb(0, 13, 1)
wib.write_reg_femb(0, 11, 256*20000)
wib.write_reg_femb(0, 10, 3) 
wib.write_reg_femb(0, 10, 0x103) 
wib.write_reg_femb(0, 10, 0x3) 

for i in range(16)
    a = wib.read_reg_femb(0, 0x240 + i )
    print a

