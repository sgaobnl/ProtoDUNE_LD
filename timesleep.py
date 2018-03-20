#!/usr/bin/env python33

import sys 
import time
from datetime import datetime

t_sleep = int(sys.argv[1])
t_min = t_sleep/60
runtime =  datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
print "sleep %d minutes starting from %s"%(t_min,runtime)
time.sleep(t_sleep)
