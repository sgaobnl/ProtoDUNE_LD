# -*- coding: utf-8 -*-
"""
File Name: fe_adc_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 1/11/2018 10:15:08 AM
Last modified: 2/22/2018 2:40:14 PM
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl
import sys
import string
class FE_ADC_MAPPING:
    def set_board(self,fe_regs, adc_regs):
        chips = 8
        if (self.COTSADC == False):
            self.REGS = [0x00000000]*(8+1)*8
            for chip in range(chips):
                chip_bits_len = 8*(16+2)
                chip_fe_regs = fe_regs[   chip*chip_bits_len: (chip+1)* chip_bits_len]
                chip_adc_regs = adc_regs[ chip*chip_bits_len: (chip+1)*chip_bits_len]
                chip_regs = []
                for onebit in chip_adc_regs:
                    chip_regs.append(onebit)
                for onebit in chip_fe_regs:
                    chip_regs.append(onebit)
                len32 = len(chip_regs)//32
                if (len32 != 9):
                    print "ERROR FE and ADC register mapping"
                else:
                    for i in range(len32):
                        bits32 = chip_regs[i*32: (i+1)*32]
                        self.REGS[chip*len32 + i ] = (sum(v<<j for j, v in enumerate(bits32)))
        else:
            print "COTS ADC chips are in used"
            self.REGS = [0x00000000]*(8+1)*4
            for chip in [0,2,4,6]:
                chip_bits_len = 8*(16+2)
                chip_fe_regs0 = fe_regs[   chip*chip_bits_len: (chip+1)* chip_bits_len]
                chip_fe_regs1 = fe_regs[   (chip+1)*chip_bits_len: (chip+2)* chip_bits_len]
                chip_regs = []
                for onebit in chip_fe_regs0:
                    chip_regs.append(onebit)
                for onebit in chip_fe_regs1:
                    chip_regs.append(onebit)
                len32 = len(chip_regs)//32
                if (len32 != 9):
                    print "ERROR FE register mapping"
                else:
                    for i in range(len32):
                        if ( i*32 <= len(chip_regs) ):
                            bits32 = chip_regs[i*32: (i+1)*32]
                            self.REGS[chip/2*len32 + i ] = (sum(v<<j for j, v in enumerate(bits32)))
    #__INIT__#
    def __init__(self):
        #self.REGS = [0x00000000]*(8+1)*8
        self.REGS = []
        self.COTSADC = False

#from fe_asic_reg_mapping import FE_ASIC_REG_MAPPING
#b = FE_ASIC_REG_MAPPING()
#b.set_fe_board(snc=1)
#
#
#a = FE_ADC_MAPPING()
#a.COTSADC = True
#
#a.set_board(b.REGS,[])
#
#print a.REGS[0:36]
#print a.REGS[36:]
#print len(a.REGS)
