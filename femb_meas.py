# -*- coding: utf-8 -*-
"""
File Name: femb_meas.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/12/2016 9:30:27 PM
Last modified: Thu 20 Sep 2018 07:15:22 PM CEST
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl

import struct
import time
from datetime import datetime
from femb_config import FEMB_CONFIG
from adc_asic_reg_mapping import ADC_ASIC_REG_MAPPING
from fe_asic_reg_mapping import FE_ASIC_REG_MAPPING
from fe_adc_config import FE_ADC_MAPPING
from detect_peaks import detect_peaks
from raw_convertor_m import raw_convertor
import numpy as np
import sys
import os
import copy
import math
from apa_mapping import APA_MAP

class FEMB_MEAS: #for one FEMB
    def FEMB_STREAM_CTL(self, switch=True, one_femb_stream_en=False):
        if (one_femb_stream_en):
            #Enable stream data
            reg_9_value = self.femb_config.femb.read_reg_femb(femb_addr, 9)
            reg_9_value = self.femb_config.femb.read_reg_femb(femb_addr, 9)
            if (switch):
                reg_9_value = reg_9_value | 0x00000001
            else:
                reg_9_value = reg_9_value & 0xFFFFFFFE
            self.femb_config.femb.write_reg_femb_checked (femb_addr, 9, reg_9_value)
        else:
            pass

    def recfile_save(self,file_setadc_rec, step, femb_addr, fe_adc_regs ): 
        with open(file_setadc_rec,"a+") as f:
            runtime =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(runtime + "\n") 
            f.write(step +"_FEMB" + str(femb_addr)+"\n") 
            f.write("Phase0 = " + format(self.femb_config.REG_CLKPHASE_data0, '08X') +"\n" )
            f.write("Phase1 = " + format(self.femb_config.REG_CLKPHASE_data1, '08X') +"\n" )
            for i in fe_adc_regs:
                f.write(format(i,"08X")+"\n") 
            f.write("\n")

    def wib_savepath (self, path, step):
        savepath = path + "/" + step + "/"
        if (os.path.exists(savepath)):
            pass
        else:
            try: 
                os.makedirs(savepath)
            except OSError:
                print "femb_meas.py: Cann't create a folder, exit"
                sys.exit()
        return savepath

    def femb_regs_cfg(self, csvf, ai, wi, fi, savepath, fe_cfg=0x3B):
            fembcfgs = []
            with open(csvf, 'r') as cf:
                i = 0
                for cl in cf:
                    if (i > 0):
                        a = cl.split(",")
                        aai = int(a[0])
                        awi = int(a[1])
                        afi = int(a[2])
                        aseq = int(a[4])
                        awr_addr = int(a[5],16)
                        awr_wr = int(a[6],16)
                        arb_flg =  (a[7].find("0x") >=0)
                        if (aai == ai) and (awi == wi) and (afi == fi) :
                            fembcfgs.append([aseq, awr_addr, awr_wr, arb_flg, ai, wi, fi])
                    i = i + 1
            fembcfgs = sorted(fembcfgs, key= lambda i : i[0])
            fembloc =  "APA%dWIB%dFEMB%d"%(ai, wi,fi)
            print fembloc

            for fembcfg in fembcfgs:
                if fembcfg[3] :
                    self.femb_config.femb.write_reg_femb_checked (fi, fembcfg[1], fembcfg[2] )
                else:
                    self.femb_config.femb.write_reg_femb (fi, fembcfg[1], fembcfg[2] )
                    time.sleep(0.01)

            savecfgfile = fembloc + "_" + hex(fe_cfg) + "_" + "CFG.csv"
            print savecfgfile
            with open(savepath + savecfgfile, 'w') as fp:
                fp.write(",".join(["APA(1-6)", "WIB(0-4)", "FEMB(0-3)", "Wr_Seq","WR_ADDR", "WR_Value"]) + ","  + "\n" )
                for x in fembcfgs:
                    strx = [str(x[4]), str(x[5]), str(x[6]), str(x[0]), str(hex(x[1])), str(hex(x[2]))]
                    fp.write(",".join( i for i in strx) + ","  + "\n")

    def save_chkout(self, path, step, femb_addr, sg, tp, adc_oft_regs, yuv_bias_regs, clk_cs=1, pls_cs = 1, dac_sel=1, \
                    fpga_dac=1, asic_dac=0, slk0 = 0, slk1= 0, val=100*10):
        print "FEMB_DAQ-->Quick measurement start"
        savepath = self.wib_savepath (path, step)
        if (True):
            ai = adc_oft_regs
            wi = yuv_bias_regs
            fi = femb_addr

            if sg == 3:
                csvf = self.csvpath + "ProtoDUNE_SP_FEMBs_Config_fpgadac4_25.csv"
                fe_cfg = 0x3F
            else:
                csvf = self.csvpath + "ProtoDUNE_SP_FEMBs_Config_fpgadac8_14.csv"
                fe_cfg = 0x3B
            self.femb_regs_cfg(csvf, ai, wi, fi, savepath, fe_cfg)

            for chip in range(8):
                rawdata = ""
                #fe_cfg_r = int('{:08b}'.format(fe_cfg)[::-1], 2)
                fe_cfg_r = fe_cfg
                filename = savepath + step +"_FEMB" + str(femb_addr) + "CHIP" + str(chip) + "_" + format(fe_cfg_r,'02X') + "_FPGADAC" + str(self.ampl) + ".bin"
                print filename
                rawdata = self.femb_config.get_rawdata_packets_femb(femb_addr, chip, val)
                if rawdata != None:
                    with open(filename,"wb") as f:
                        f.write(rawdata) 

    def save_rms_noise(self, path, step, femb_addr, sg, tp, adc_oft_regs, yuv_bias_regs, clk_cs=1, pls_cs = 1, dac_sel=0, \
                       fpga_dac=0, asic_dac=0, slk0 = 0, slk1= 0, val=1600*10):
        print "FEMB_DAQ-->RMS measurement start"
        savepath = self.wib_savepath (path, step)
        if (True):
            ai = adc_oft_regs
            wi = yuv_bias_regs
            fi = femb_addr

            csvf = self.csvpath + "ProtoDUNE_SP_FEMBs_Config_rms.csv"
            fe_cfg = 0x3B
            self.femb_regs_cfg(csvf, ai, wi, fi, savepath, fe_cfg)

            for chip in range(8):
                rawdata = ""
                fe_cfg = 0x3B
                fe_cfg_r = fe_cfg
                filename = savepath+ step +"_FEMB" + str(femb_addr) + "CHIP" + str(chip) + "_" + format(fe_cfg_r,'02X') + "_RMS.bin"
                print filename
                rawdata = self.femb_config.get_rawdata_packets_femb(femb_addr, chip, val)
                if rawdata != None:
                    with open(filename,"wb") as f:
                        f.write(rawdata) 

    def __init__(self):
        self.freq = 500
        self.dly = 10 
        self.peak_chn = 11
        self.ampl = 0 #% 32
        self.int_dac = 0 # or 0xA1
        self.dac_meas = self.int_dac  # or 60
        self.reg_5_value = ((self.freq<<16)&0xFFFF0000) + ((self.dly<<8)&0xFF00) + ( (self.dac_meas|self.ampl)& 0xFF )
        self.femb_config = FEMB_CONFIG()
        self.adc_reg = ADC_ASIC_REG_MAPPING()
        self.fe_reg = FE_ASIC_REG_MAPPING() 
        self.fe_adc_reg = FE_ADC_MAPPING()
        self.jumbo_flag = True
        self.APA = "ProtoDUNE"
        self.apamap = APA_MAP()
        self.apamap.APA = self.APA 

        self.csvpath = "/Users/shanshangao/Documents/GitHub/ProtoDUNE_LD/"
        self.csvpath = "D:/APA/ProtoDUNE_LD_CFG/"
        self.csvpath = "/nfs/home/shanshan/PD_LD_CFG/"

