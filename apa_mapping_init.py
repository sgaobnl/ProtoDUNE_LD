# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Tue Jun 12 09:48:09 2018
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl

from apa_mapping import APA_MAP
apa = APA_MAP()
a = apa.apa_femb_mapping()
print "Initize LArIAT mapping is done"
#print len(a[0]), len(a[1]), len(a[2]), len(a[3])
