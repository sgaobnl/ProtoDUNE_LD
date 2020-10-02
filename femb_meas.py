# -*- coding: utf-8 -*-
"""
File Name: femb_meas.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/12/2016 9:30:27 PM
Last modified: 5/2/2020 1:41:59 AM
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl

import matplotlib
matplotlib.use('Agg')

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
import pickle
from apa_mapping import APA_MAP
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches


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

    def fe_regs_bias_config(self, fe_regs, yuv_bias_regs ): #one FEMB
        femb_fe_regs = []
        for tmp_r in range(len(fe_regs)):
            femb_fe_regs.append( fe_regs[tmp_r] | yuv_bias_regs[tmp_r]) 
        return copy.deepcopy(femb_fe_regs)

    def yuv_bias_set (self, femb_addr):
        yuv_bias_class = FE_ASIC_REG_MAPPING()
        yuv_bias_class.set_fe_board()
        for chip in range (8):
            chip_means = []
            for chn in range (16):
                chipchn = (chip*16) + chn
                apa_yuv, apa_y, apa_u, apa_v = self.apamap.apa_mapping()
                bias = 0
                y_wire = np.where(chipchn == np.array(apa_y))
                if (len(y_wire[0]) > 0 ):
                    if (apa_y[y_wire[0][0]] == chipchn):
                        bias = 1   #200mV
                u_wire = np.where(chipchn == np.array(apa_u))
                if (len(u_wire[0]) > 0 ):
                    if (apa_u[u_wire[0][0]] == chipchn):
                        bias = 0  #900mV
                v_wire = np.where(chipchn == np.array(apa_v))
                if (len(v_wire[0]) > 0 ):
                    if (apa_v[v_wire[0][0]] == chipchn):
                        bias = 0  #900mV
                yuv_bias_class.set_fechn_reg(chip=chip, chn=chn, snc=bias )
        yuv_bias_regs = copy.deepcopy(yuv_bias_class.REGS)
        return yuv_bias_regs

    def adc_oft_set(self, femb_addr, en_oft=True):
        clk_cs = 1
        adc_en_gr = 1
        snc_cs = 0
        pls_cs = 1
        dac_sel = 0
        fpga_dac = 0
        asic_dac = 0
        sg = 0 #sg_tuple[0] #4.7mV/fC
        tp = 1 #st_tuple[3] #3us
    
        adc_oft_regs = []
        val = 25 
        if (not(self.jumbo_flag)):
            self.femb_config.femb.write_reg_wib_checked (0x1F, 0x1FB)
            val = val*8
        else:
            self.femb_config.femb.write_reg_wib_checked (0x1F, 0xEFB)
            val = val
    
        if ( en_oft ):
            oft_mean_chns = []
            print "Pedestal configuration starts..."
            for adc_oft in range(4):
                print "FEMB%d, EN_GR = 1, ADC_Offset = %d"%(femb_addr, adc_oft)
                self.fe_reg.set_fe_board() # reset the registers value
                self.fe_reg.set_fe_board (sts=0,sg=sg, st=tp, smn=0, sdf=0, slk0=0, slk1=0, swdac =0, dac=0)
                fe_regs = copy.deepcopy(self.fe_reg.REGS)
        
                if (clk_cs == 1):
                    self.adc_reg.set_adc_board(clk0=1,f0 =0) #external clk
                    adc_clk_regs = copy.deepcopy(self.adc_reg.REGS)
                else:
                    self.adc_reg.set_adc_board(clk0=0,f0 =0) #internal clk
                    adc_clk_regs = copy.deepcopy(self.adc_reg.REGS)
            
                if (adc_en_gr == 1):
                    self.adc_reg.set_adc_board(d=adc_oft, engr=adc_en_gr)
                    adc_engr_regs = copy.deepcopy(self.adc_reg.REGS)
                else:
                    self.adc_reg.set_adc_board(engr=adc_en_gr) 
                    adc_engr_regs = copy.deepcopy(self.adc_reg.REGS)
            
                adc_regs = []
                for tmpi in range(len(adc_clk_regs)):
                    adc_regs.append(adc_clk_regs[tmpi] | adc_engr_regs[tmpi])
        
                self.fe_adc_reg.set_board(fe_regs,adc_regs)
                fe_adc_regs = copy.deepcopy (self.fe_adc_reg.REGS)
                self.femb_config.config_femb(femb_addr, fe_adc_regs, clk_cs, pls_cs, dac_sel, fpga_dac, asic_dac)
                self.reg_5_value = (self.reg_5_value&0xFFFFFF00) + (0x00&0xFF)
                self.femb_config.femb.write_reg_femb_checked (femb_addr, 5, self.reg_5_value)
                self.femb_config.config_femb_mode(femb_addr,  pls_cs, dac_sel, fpga_dac, asic_dac)
        
                mean_chns = []
                for asic in range (8):
                    rawdata = self.femb_config.get_rawdata_packets_femb(femb_addr,asic, val)
                    smps = (len(rawdata)-1024)//2//16
                    if (smps > 5000):
                        smps = 5000
                    chn_data = raw_convertor(rawdata, smps, self.jumbo_flag)
                    for chn in range(16):
                        np_data = np.array(chn_data[chn])
                        np_tmp_data = []
                        for k in np_data:
                            m = k % 64
                            if ( m == 62 ) or (m == 63) or (m == 0) or (m == 1) or (m == 2) :
                                pass
                            else:
                                np_tmp_data.append(k)
                        if (len(np_tmp_data) < 2 ):
                            np_tmp_data = np_data
                        pedvalue = int(np.mean(np_tmp_data))
                        mean_chns.append(pedvalue)
                oft_mean_chns.append(mean_chns)
    
        ##################################################################################
            adc_oft_class = ADC_ASIC_REG_MAPPING()
            adc_oft_class.set_adc_board()
        
            brd_means = []
            for chip in range (8):
                chip_means = []
                for chn in range (16):
                    chipchn = (chip*16) + chn
                    oftmod64 = []
                    for adc_oft in range(4):
                        oftmod64.append( abs(((oft_mean_chns[adc_oft][chipchn])%64)-32) )
                    oftmod64 = np.array(oftmod64)
                    tmp = np.where(oftmod64 == (np.min(oftmod64)))
                    adc_oft_class.set_chn_reg(chip=chip, chn=chn, d=tmp[0][0] )
                    chip_means.append(oft_mean_chns[tmp[0][0]][chipchn])
                brd_means.append(chip_means)
    
        adc_oft_regs = copy.deepcopy(adc_oft_class.REGS)
        return adc_oft_regs

    def adc_clk_engr_config (self, adc_oft_regs, clk_cs = 1, adc_en_gr = 1, adc_offset = 0 ): 
        if (clk_cs == 1):
            self.adc_reg.set_adc_board(clk0=1,f0 =0) #external clk
            adc_clk_regs = copy.deepcopy(self.adc_reg.REGS)
        else:
            self.adc_reg.set_adc_board(clk0=0,f0 =0) #internal clk
            adc_clk_regs = copy.deepcopy(self.adc_reg.REGS)
    
        if (adc_en_gr == 1):
            self.adc_reg.set_adc_board(d=adc_offset, engr=adc_en_gr)
            adc_engr_regs = copy.deepcopy(self.adc_reg.REGS)
        else:
            self.adc_reg.set_adc_board(engr=adc_en_gr) 
            adc_engr_regs = copy.deepcopy(self.adc_reg.REGS)
    
        adc_regs = []
        for tmpi in range(len(adc_clk_regs)):
            adc_regs.append(adc_clk_regs[tmpi] | adc_engr_regs[tmpi])
    
        femb_adc_regs = []
        for tmp_r in range(len(adc_regs)):
            if (adc_oft_regs == None):
                femb_adc_regs.append( adc_regs[tmp_r]  ) 
            else:
                femb_adc_regs.append( adc_regs[tmp_r] | adc_oft_regs[tmp_r] ) 
        return copy.deepcopy(femb_adc_regs)
    
#    def fe_regs_bias_config(self, fe_regs,  yuv_bias_regs ):
#        femb_fe_regs = []
#        for tmp_r in range(len(fe_regs)):
#            femb_fe_regs.append( fe_regs[tmp_r] | yuv_bias_regs[tmp_r]) 
#        return copy.deepcopy(femb_fe_regs)

    def femb_oft_set(self, femb_addr, jumob_flag = True, en_oft = True ): 
        adc_oft_regs = self.adc_oft_set(femb_addr,  en_oft=True)
        yuv_bias_regs = self.yuv_bias_set (femb_addr )
        return femb_addr, adc_oft_regs, yuv_bias_regs

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

    def save_chkout(self, path, step, femb_addr, sg, tp, adc_oft_regs, yuv_bias_regs, clk_cs=1, pls_cs = 1, dac_sel=1, \
                    fpga_dac=1, asic_dac=0, slk0 = 0, slk1= 0, val=100*10):
        print "FEMB_DAQ-->Quick measurement start"

        savepath = self.wib_savepath (path, step)
        file_setadc_rec = savepath + step +"_FEMB" + str(femb_addr)+ str(sg) + str(tp) + "CHK_FE_ADC.txt"
        if os.path.isfile(file_setadc_rec):
            print "%s, file exist!!!"%file_setadc_rec
            sys.exit()
        else:
            self.fe_reg.set_fe_board() # reset the registers value
            self.fe_reg.set_fe_board(sg=sg, st=tp, sts=1, smn=0, sdf=0, slk0=slk0, slk1=slk1, swdac =2, dac=0 )
            fe_regs = copy.deepcopy(self.fe_reg.REGS)
            adc_regs = self.adc_clk_engr_config (adc_oft_regs, clk_cs = clk_cs, adc_en_gr = 1, adc_offset = 0 )
            fe_bias_regs = self.fe_regs_bias_config(fe_regs, yuv_bias_regs ) #one FEMB
            self.fe_adc_reg.set_board(fe_bias_regs,adc_regs)
            fe_adc_regs = copy.deepcopy(self.fe_adc_reg.REGS)

            if sg == 3: #25mV/fC
                self.ampl = 4
            elif sg == 1: #"14_0mV_"
                self.ampl = 8
            elif sg == 2: #"07_8mV_":
                self.ampl = 12
            elif sg == 0: #"04_7mV_":
                self.ampl = 20
            else:
                self.ampl = 4
            self.dly  = 10
            self.reg_5_value = (self.reg_5_value&0xFFFFFF00) + (self.ampl&0xFF)
            self.reg_5_value = (self.reg_5_value&0xFFFF00FF) + ((self.dly<<8)&0xFF00)
            self.femb_config.femb.write_reg_femb_checked (femb_addr, 5, self.reg_5_value)
            self.femb_config.config_femb(femb_addr, fe_adc_regs ,clk_cs, pls_cs, dac_sel, fpga_dac, asic_dac)
            self.femb_config.config_femb_mode(femb_addr,  pls_cs, dac_sel, fpga_dac, asic_dac)

            self.recfile_save(file_setadc_rec, step, femb_addr, fe_adc_regs) 

            for chip in range(8):
                rawdata = ""
                fe_cfg = int((fe_adc_regs[5])&0xFF)
                fe_cfg_r = int('{:08b}'.format(fe_cfg)[::-1], 2)
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
        file_setadc_rec = savepath+ step +"_FEMB" + str(femb_addr)+ str(sg) + str(tp) + "ped_FE_ADC.txt"
        if os.path.isfile(file_setadc_rec):
            print "%s, file exist!!!"%file_setadc_rec
            sys.exit()
        else:
            self.fe_reg.set_fe_board() # reset the registers value
            self.fe_reg.set_fe_board(sg=sg, st=tp, sts=1, smn=0, sdf=0, slk0=slk0, slk1=slk1, swdac =0, dac=0 )
            fe_regs = copy.deepcopy(self.fe_reg.REGS)
            adc_regs = self.adc_clk_engr_config (adc_oft_regs, clk_cs = clk_cs, adc_en_gr = 1, adc_offset = 0 )
            fe_bias_regs = self.fe_regs_bias_config(fe_regs, yuv_bias_regs ) #one FEMB
            self.fe_adc_reg.set_board(fe_bias_regs,adc_regs)
            fe_adc_regs = copy.deepcopy(self.fe_adc_reg.REGS)

            self.ampl = 0
            self.dly  = 10
            self.reg_5_value = (self.reg_5_value&0xFFFFFF00) + (self.ampl&0xFF)
            self.reg_5_value = (self.reg_5_value&0xFFFF00FF) + ((self.dly<<8)&0xFF00)
            self.femb_config.femb.write_reg_femb_checked (femb_addr, 5, self.reg_5_value)
            self.femb_config.config_femb(femb_addr, fe_adc_regs ,clk_cs, pls_cs, dac_sel, fpga_dac, asic_dac)
            self.femb_config.config_femb_mode(femb_addr,  pls_cs, dac_sel, fpga_dac, asic_dac)

            self.recfile_save(file_setadc_rec, step, femb_addr, fe_adc_regs) 

            for chip in range(8):
                rawdata = ""
                fe_cfg = int((fe_adc_regs[5])&0xFF)
                fe_cfg_r = int('{:08b}'.format(fe_cfg)[::-1], 2)
                filename = savepath+ step +"_FEMB" + str(femb_addr) + "CHIP" + str(chip) + "_" + format(fe_cfg_r,'02X') + "_RMS.bin"
                print filename
                rawdata = self.femb_config.get_rawdata_packets_femb(femb_addr, chip, val)
                if rawdata != None:
                    with open(filename,"wb") as f:
                        f.write(rawdata) 

    def ext_dly_search(self, femb_addr, pls_cs = 1, dac_sel=1, fpga_dac=1, asic_dac=0):
        print "FEMB_DAQ-->Start to find proper DLY to locate the peak of shaper"
        #set proper ampl, which will let ADC value fall between 0x7ff and 0xb00
        ampl = 1
        while ( ampl < 32 ): 
            self.reg_5_value = (self.reg_5_value&0xFFFFFF00) + (ampl&0xFF)
            self.femb_config.femb.write_reg_femb_checked (femb_addr, 5, self.reg_5_value)

            self.femb_config.config_femb_mode(femb_addr,  pls_cs, dac_sel, fpga_dac, asic_dac)

            asic = 0
            val = 20
            if (not(self.jumbo_flag) ):
                val = val*8
            else:
                val = val

            rawdata = self.femb_config.get_rawdata_packets_femb(femb_addr,asic, val)

            smps = (len(rawdata)-1024)//2//16
            chn_data = raw_convertor(rawdata, smps, self.jumbo_flag)
            chn_peakmean=[]

            np_data = np.array(chn_data[self.peak_chn])
            pedvalue = np.mean(np_data)
            maxvalue = np.max(np_data)
            peaks_index = detect_peaks(x=np_data, mph=pedvalue + abs((maxvalue-pedvalue)*2/3), mpd=800) 
            peaks_value = []
            for i in peaks_index :
                peaks_value.append(np_data[i])

            peaksmean = np.mean(peaks_value)
            if ( math.isnan(peaksmean)):
                peaksmean = 0
            else:
                print "FPGA DAC = %d gets maximum ADC bin = %d"%(ampl, peaksmean)
            if (peaksmean > 3000 ):
                break
            else:
                ampl = ampl + 1 

        dly_pos = []
        self.dly = 1
        for dly in range(self.dly, self.dly+20,1):
            self.reg_5_value = (self.reg_5_value&0xFFFF00FF) + ((dly<<8)&0xFF00)
            self.femb_config.femb.write_reg_femb_checked (femb_addr, 5, self.reg_5_value)
            self.femb_config.config_femb_mode(femb_addr,  pls_cs, dac_sel, fpga_dac, asic_dac)

            val = 20
            if (not(self.jumbo_flag) ):
                val = val*8
            else:
                val = val

            rawdata = self.femb_config.get_rawdata_packets_femb(femb_addr,asic, val)

            smps = (len(rawdata)-1024)//2//16
            chn_data = raw_convertor(rawdata, smps,self.jumbo_flag)
            chn_peakmean=[]

            for chn in [self.peak_chn]:
                np_data = np.array(chn_data[chn])
                pedvalue = np.mean(np_data)
                maxvalue = np.max(np_data)
                peaks_index = detect_peaks(x=np_data, mph=pedvalue + abs((maxvalue-pedvalue)*2/3), mpd=800) 
                peaks_value = []
                for i in peaks_index :
                    peaks_value.append(np_data[i])
                peaksmean = np.mean(peaks_value)
                if ( math.isnan(peaksmean)):
                        peaksmean = 0
                dly_pos.append(peaksmean)
        
        max_peak = max(dly_pos)
        max_ind = np.where(dly_pos==max_peak)
        self.dly = self.dly + max_ind[0][0]
        self.reg_5_value = (self.reg_5_value&0xFFFF00FF) + ((self.dly<<8)&0xFF00)
        self.femb_config.femb.write_reg_femb_checked (femb_addr, 5, self.reg_5_value)
        self.femb_config.config_femb_mode(femb_addr,  pls_cs, dac_sel, fpga_dac, asic_dac)

        print "FEMB_DAQ-->Dly search"
        print "FEMB_DAQ-->Best DLY for current configuration is: %d"%self.dly

    def fpga_dac_cali(self, path, step, femb_addr,  sg, tp, adc_oft_regs, yuv_bias_regs, clk_cs=1, pls_cs = 1, dac_sel=1, \
                      fpga_dac=1, asic_dac=0, slk0 = 0, slk1= 0,  val=100):
        print "FEMB_DAQ-->Calibration measurement with FPGA \"DAC\" starts"
        savepath = self.wib_savepath (path, step)

        file_setadc_rec = savepath  + step +"_FEMB" + str(femb_addr)+ str(sg) + str(tp) + "FPGADAC_FE_ADC.txt"
        if os.path.isfile(file_setadc_rec):
            print "%s, file exist!!!"%file_setadc_rec
            sys.exit()
        else:
            self.fe_reg.set_fe_board() # reset the registers value
            self.fe_reg.set_fe_board(sg=sg, st=tp, sts=1, smn=0, sdf=0, slk0=slk0, slk1=slk1, swdac =2, dac=0 )
            fe_regs = copy.deepcopy(self.fe_reg.REGS)
            adc_regs = self.adc_clk_engr_config (adc_oft_regs, clk_cs = clk_cs, adc_en_gr = 1, adc_offset = 0 )
            fe_bias_regs = self.fe_regs_bias_config(fe_regs, yuv_bias_regs ) #one FEMB
            self.fe_adc_reg.set_board(fe_bias_regs,adc_regs)
            fe_adc_regs = copy.deepcopy(self.fe_adc_reg.REGS)
            self.femb_config.config_femb(femb_addr, fe_adc_regs ,clk_cs, pls_cs, dac_sel, fpga_dac, asic_dac)
    
            self.recfile_save(file_setadc_rec, step, femb_addr, fe_adc_regs) 

            self.ext_dly_search(femb_addr, pls_cs, dac_sel, fpga_dac, asic_dac )

            if sg == 0: #4.7mV/fC
                dac_value_np = range(1,64,1)
            elif sg == 2: #7.8mV/fC
                dac_value_np = range(1,32,1)
            elif sg == 1: #14mV/fC
                dac_value_np = range(1,14,1)
            elif sg == 3: #25mV/fC
                dac_value_np = range(1,10,1)

            for dac in dac_value_np:
                self.ampl = dac 
                self.reg_5_value = (self.reg_5_value&0xFFFFFF00) + (self.ampl&0xFF)
                self.femb_config.femb.write_reg_femb_checked (femb_addr, 5, self.reg_5_value)
                self.femb_config.config_femb_mode(femb_addr,  pls_cs, dac_sel, fpga_dac, asic_dac)
    
                for chip in range(8):
                    rawdata = ""
                    fe_cfg = int((fe_adc_regs[5])&0xFF)
                    fe_cfg_r = int('{:08b}'.format(fe_cfg)[::-1], 2)
                    filename = savepath  + step +"_FEMB" + str(femb_addr) + "CHIP" + str(chip) + "_" + format(fe_cfg_r,'02X') + "_FPGADAC" + format(dac,'02X')+ ".bin"
                    print filename
                    rawdata = self.femb_config.get_rawdata_packets_femb(femb_addr, chip, val)
                    if rawdata != None:
                        with open(filename,"wb") as f:
                            f.write(rawdata) 

    def asic_dac_cali(self, path, step, femb_addr,  sg, tp, adc_oft_regs, yuv_bias_regs, clk_cs=1, pls_cs = 1, dac_sel=1, \
                      fpga_dac=0, asic_dac=1, slk0 = 0, slk1= 0,  val=100):
        print "FEMB_DAQ-->Calibration measurement with ASIC \"DAC\" starts"
        savepath = self.wib_savepath (path, step)
        file_setadc_rec = savepath + step +"_FEMB" + str(femb_addr)+ str(sg) + str(tp) + "ASICDAC_FE_ADC.txt"
        if os.path.isfile(file_setadc_rec):
            print "%s, file exist!!!"%file_setadc_rec
            sys.exit()
        else:
            for dac in range(3,64,1):
                self.fe_reg.set_fe_board() # reset the registers value
                self.fe_reg.set_fe_board (sts=1,sg=sg, st=tp, smn=0, sdf=0, slk0=slk0, slk1=slk1, swdac =1, dac=dac)
                fe_regs = copy.deepcopy(self.fe_reg.REGS)
                adc_regs = self.adc_clk_engr_config (adc_oft_regs, clk_cs = clk_cs, adc_en_gr = 1, adc_offset = 0 )
                fe_bias_regs = self.fe_regs_bias_config(fe_regs, yuv_bias_regs ) #one FEMB
                self.fe_adc_reg.set_board(fe_bias_regs,adc_regs)
                fe_adc_regs = copy.deepcopy(self.fe_adc_reg.REGS)
                self.femb_config.config_femb(femb_addr, fe_adc_regs, clk_cs, pls_cs, dac_sel, fpga_dac, asic_dac)

                self.reg_5_value = (self.reg_5_value&0xFFFFFF00) + (0x00&0xFF)
                self.femb_config.femb.write_reg_femb_checked (femb_addr, 5, self.reg_5_value)
                self.femb_config.config_femb_mode(femb_addr,  pls_cs, dac_sel, fpga_dac, asic_dac)
  
                rawdata = self.femb_config.get_rawdata_packets_femb(femb_addr,asic=0, val=100)
            
                smps = (len(rawdata)-1024)//2//16
                chn_data = raw_convertor(rawdata, smps, self.jumbo_flag)
                chn_peakmean=[]
    
                np_data = np.array(chn_data[self.peak_chn])
                pedvalue = np.mean(np_data)
                maxvalue = np.max(np_data)
                peaks_index = detect_peaks(x=np_data, mph=pedvalue + abs((maxvalue-pedvalue)*2/3), mpd=800) 
                peaks_value = []
                for i in peaks_index :
                    peaks_value.append(np_data[i])
            
                peaksmean = np.mean(peaks_value)
                if ( math.isnan(peaksmean)):
                    peaksmean = 0
                else:
                    print "ASIC DAC = %d gets maximum ADC bin = %d"%(dac, peaksmean)
                if (peaksmean > 3000 ):
                    break
    
            dly_pos = []
            self.dly = 1
            for dly in range(self.dly, self.dly+20,1):
                self.reg_5_value = (self.reg_5_value&0xFFFF00FF) + ((dly<<8)&0xFF00)
                self.femb_config.femb.write_reg_femb_checked (femb_addr, 5, self.reg_5_value)
                self.femb_config.config_femb_mode(femb_addr, pls_cs, dac_sel, fpga_dac, asic_dac)
    
                rawdata = self.femb_config.get_rawdata_packets_femb(femb_addr,asic=0, val=100)
            
                smps = (len(rawdata)-1024)//2//16
                chn_data = raw_convertor(rawdata, smps, self.jumbo_flag)
                chn_peakmean=[]
            
                for chn in [self.peak_chn]:
                    np_data = np.array(chn_data[chn])
                    pedvalue = np.mean(np_data)
                    maxvalue = np.max(np_data)
                    peaks_index = detect_peaks(x=np_data, mph=pedvalue + abs((maxvalue-pedvalue)*2/3), mpd=800) 
                    peaks_value = []
                    for i in peaks_index :
                        peaks_value.append(np_data[i])
                    peaksmean = np.mean(peaks_value)
                    if ( math.isnan(peaksmean)):
                            peaksmean = 0
                    dly_pos.append(peaksmean)
            max_peak = max(dly_pos)
            max_ind = np.where(dly_pos==max_peak)
            self.dly = self.dly + max_ind[0][0]
            self.reg_5_value = (self.reg_5_value&0xFFFF00FF) + ((self.dly<<8)&0xFF00)
            self.femb_config.femb.write_reg_femb_checked (femb_addr, 5, self.reg_5_value)
            self.femb_config.config_femb_mode(femb_addr,  pls_cs, dac_sel, fpga_dac, asic_dac)
            print "FEMB_DAQ-->Dly search"
            print "FEMB_DAQ-->Best DLY for current configuration is: %d"%self.dly

            if sg == 0: #4.7mV/fC
                dac_value_np = range(2,64,1)
            elif sg == 2: #7.8mV/fC
                dac_value_np = range(2,32,1)
            elif sg == 1: #14mV/fC
                dac_value_np = range(2,12,1)
            elif sg == 3: #25mV/fC
                dac_value_np = range(2,10,1)
    
            for dac in dac_value_np:
                self.fe_reg.set_fe_board() # reset the registers value
                self.fe_reg.set_fe_board (sts=1,sg=sg, st=tp, smn=0, sdf=0, slk0=slk0, slk1=slk1, swdac =1, dac=dac)
                fe_regs = copy.deepcopy(self.fe_reg.REGS)
                adc_regs = self.adc_clk_engr_config (adc_oft_regs, clk_cs = clk_cs, adc_en_gr = 1, adc_offset = 0 )
                fe_bias_regs = self.fe_regs_bias_config(fe_regs, yuv_bias_regs ) #one FEMB
                self.fe_adc_reg.set_board(fe_bias_regs,adc_regs)
                fe_adc_regs = copy.deepcopy(self.fe_adc_reg.REGS)
                self.femb_config.config_femb(femb_addr, fe_adc_regs, clk_cs, pls_cs, dac_sel, fpga_dac, asic_dac)
                self.reg_5_value = (self.reg_5_value&0xFFFFFF00) + (0x00&0xFF)
                self.femb_config.femb.write_reg_femb_checked (femb_addr, 5, self.reg_5_value)
                self.femb_config.config_femb_mode(femb_addr,  pls_cs, dac_sel, fpga_dac, asic_dac)

                self.recfile_save(file_setadc_rec, step, femb_addr, fe_adc_regs) 

                for chip in range(8):
                    rawdata = ""
                    fe_cfg = int((self.fe_adc_reg.REGS[5])&0xFF)
                    fe_cfg_r = int('{:08b}'.format(fe_cfg)[::-1], 2)
                    filename = savepath + step +"_FEMB" + str(femb_addr) + "CHIP" + str(chip) + "_" + format(fe_cfg_r,'02X') + "_ASICDAC" + format(dac,'02X')+ ".bin"
                    print filename
                    if os.path.isfile(filename):
                        print "%s, file exist!!!"%filename
                        sys.exit()
                    else:
                        rawdata = self.femb_config.get_rawdata_packets_femb(femb_addr, chip, val)
                        if (rawdata != None ):
                            with open(filename,"wb") as f:
                                f.write(rawdata)

    #brombreg mode read one WIB, not one FEMB
    def wib_brombreg_acq(self, path, step, femb_on_wib, sg, tp, adc_oft_regs_np, yuv_bias_regs_np, clk_cs=1, pls_cs = 1, dac_sel=0, \
                      fpga_dac=0, asic_dac=0, slk0 = 0, slk1= 0, cycle=150):
        savepath = self.wib_savepath (path, step)
        fembs_np = femb_on_wib #[0,1,2,3]
        print "Brombreg starts, please wait"

        if (not(self.jumbo_flag)):
            self.femb_config.femb.write_reg_wib_checked (0x1F, 0x1FB)
        else:
            self.femb_config.femb.write_reg_wib_checked (0x1F, 0xEFB)

        for femb_addr in fembs_np:
            self.fe_reg.set_fe_board() # reset the registers value
            self.fe_reg.set_fe_board(sg=sg, st=tp, sts=0, smn=0, sdf=0, slk0=slk0, slk1=slk1 )
            fe_regs = copy.deepcopy(self.fe_reg.REGS)
            adc_regs = self.adc_clk_engr_config (adc_oft_regs_np[femb_addr], clk_cs = clk_cs, adc_en_gr = 1, adc_offset = 0 )
            fe_bias_regs = self.fe_regs_bias_config(fe_regs, yuv_bias_regs_np[femb_addr] ) #one FEMB
            self.fe_adc_reg.set_board(fe_bias_regs, adc_regs)

            if sg == "25_0mV_":
                self.ampl = 4
            elif sg == "14_0mV_":
                self.ampl = 8
            elif sg == "07_8mV_":
                self.ampl = 12
            elif sg == "04_7mV_":
                self.ampl = 20
            else:
                self.ampl = 4
            self.reg_5_value = (self.reg_5_value&0xFFFFFF00) + (self.ampl&0xFF)
            self.dly  = 10
            self.reg_5_value = (self.reg_5_value&0xFFFF00FF) + ((self.dly<<8)&0xFF00)
            self.freq = 201
            self.reg_5_value = ((self.freq<<16)&0xFFFF0000) + (self.reg_5_value& 0xFFFF )                

            file_setadc_rec = savepath + step +"_FEMB" + str(femb_addr)+ str(sg) + str(tp) + "BB_FE_ADC.txt"
            if os.path.isfile(file_setadc_rec):
                print "%s, file exist!!!"%file_setadc_rec
                sys.exit()
            else:
                self.femb_config.femb.write_reg_femb_checked (femb_addr, 5, self.reg_5_value)
                fe_adc_regs = self.fe_adc_reg.REGS
                self.femb_config.config_femb(femb_addr, fe_adc_regs, clk_cs, pls_cs, dac_sel, fpga_dac, asic_dac)

            self.recfile_save(file_setadc_rec, step, femb_addr, fe_adc_regs) 

            fe_cfg = int((fe_adc_regs[5])&0xFF)
            fe_cfg_r = int('{:08b}'.format(fe_cfg)[::-1], 2)
        self.femb_config.femb.get_rawdata_packets_bromberg(path=path, step=step, fe_cfg_r=fe_cfg_r, fembs_np=fembs_np , cycle=cycle)

    def FEMB_MON(self,femb_addr=0):
        time.sleep(0.5)
        self.femb_config.femb.write_reg_wib (38, 0)
        self.femb_config.femb.write_reg_wib (38, 1)
        self.femb_config.femb.write_reg_wib (38, 0)
        self.femb_config.femb.write_reg_wib (38, 1)
        self.femb_config.femb.write_reg_wib (38, 0)
        self.femb_config.femb.write_reg_wib (38, 1)
        self.femb_config.femb.write_reg_wib (38, 0)
        rinc = int (femb_addr // 2)
        rloc =  int (femb_addr % 2)
        tmp = self.femb_config.femb.read_reg_wib (38+rinc)
        mondac_v = (tmp&0x0000FFFF) if rloc == 1 else ((tmp>>16)&0x0000FFFF)
        return mondac_v

    def FEMB_MON_N(self,femb_addr=0, N=10000):
        time.sleep(0.5)
        vs =[]
        for i in xrange(N):
            self.femb_config.femb.write_reg_wib (38, 0)
            self.femb_config.femb.write_reg_wib (38, 1)
            self.femb_config.femb.write_reg_wib (38, 0)
            self.femb_config.femb.write_reg_wib (38, 1)
            self.femb_config.femb.write_reg_wib (38, 0)
            self.femb_config.femb.write_reg_wib (38, 1)
            self.femb_config.femb.write_reg_wib (38, 0)
            rinc = int (femb_addr // 2)
            rloc =  int (femb_addr % 2)
            tmp = self.femb_config.femb.read_reg_wib (38+rinc)
            mondac_v = (tmp&0x0000FFFF) if rloc == 1 else ((tmp>>16)&0x0000FFFF)
            vs.append(mondac_v)
        return vs


    #for one WIB operation
    def wib_monitor_spot(self, runpath, femb_on_wib=[1], fembchns = [14, 15, 16*3 + 4, 16*3 + 5]):
        mon_paras = []
        clk_cs = 1
        adc_en_gr = 1

        pls_cs = 1
        dac_sel = 1

        adc_oft = 0
        fpga_dac = 0
        asic_dac = 1
        dac = 0x10
        fembs_np = femb_on_wib #[0,1,2,3]
        #fembs_np = [0]

        for monitor_out in ["pulse"]:
            tvalue_np = []
            if (monitor_out == "pulse"):
                chns = 16
                sncs =[0,1] 
            #    tps = [0,1,2,3] 
                tps = [3] 
            #    gs =[0,1,2,3]
                gs =[1]
            #    slk0s = [0,1]
                slk0s = [0]
            #    slk1s = [0,1]
                slk1s = [0]
            #    sdfs = [0,1]
                sdfs = [0]
            else:
                chns = 1
                sncs =[0] 
                tps = [3] 
                gs =[1]
            #    slk0s = [0,1]
                slk0s = [0]
            #    slk1s = [0,1]
                slk1s = [0]
            #    sdfs = [0,1]
                sdfs = [0]
            for slk0 in slk0s:
               for slk1 in slk1s:
                   for sdf in sdfs:
                        for sg in gs:
                            for tp in tps:
                                for femb_addr in fembs_np:
                                    for snc in sncs:
                                        fig = plt.figure(figsize=(12,8))
                                        plt.rcParams.update({'font.size': 14})
                                        for chip in range(8):
                                            for chn in range(chns):
                                                if (chip*16 + chn) in fembchns:
                                                    val = 25 
                                                    if (not(self.jumbo_flag)):
                                                        self.femb_config.femb.write_reg_wib_checked (0x1F, 0x1FB)
                                                        val = val*8
                                                    else:
                                                        self.femb_config.femb.write_reg_wib_checked (0x1F, 0xEFB)
                                                    self.fe_reg.set_fe_board() # reset the registers value
                    
                                                    #set registers for FEMB
                                                    self.fe_reg.set_fe_board(sg=sg, st=tp, sts=0, snc=snc, smn=0, sdf=sdf, slk0=slk0, slk1=slk1, swdac =1, dac=dac )
                                                    #set global registers for FE
                                                    if (monitor_out == "pulse" ):
                                                        self.fe_reg.set_fechip_global(chip=chip, slk0=slk0, stb1 = 0, stb = 0, slk1=slk1, swdac=1, dac=dac)
                                                    #set chn registers for FE
                                                    self.fe_reg.set_fechn_reg(chip=chip, chn=chn, sts=1, snc=snc, sg=sg, st=tp, smn=1, sdf=sdf )
                                                    #self.fe_reg.set_fechn_reg(chip=chip, chn=chn, sts=0, snc=snc, sg=sg, st=tp, smn=1, sdf=sdf )
                                                    fe_regs = copy.deepcopy(self.fe_reg.REGS)
                    
                                                    self.adc_reg.set_adc_board(clk0=1,f0 =0) #external clk
                                                    adc_clk_regs = copy.deepcopy(self.adc_reg.REGS)
                                                    self.adc_reg.set_adc_board(d=adc_oft, engr=adc_en_gr)
                                                    adc_engr_regs = copy.deepcopy(self.adc_reg.REGS)
                                                    adc_regs = []
                                                    for tmpi in range(len(adc_clk_regs)):
                                                        adc_regs.append(adc_clk_regs[tmpi] | adc_engr_regs[tmpi])
                                                    self.fe_adc_reg.set_board(fe_regs,adc_regs)
                                                    fe_adc_regs = copy.deepcopy (self.fe_adc_reg.REGS)
                    
                                                    mon_cs = 1
                                                    self.dly  = 10
                                                    self.ampl = 0
                                                    self.freq = 100
                                                    self.reg_5_value = (self.reg_5_value&0xFFFFFF00) + (self.ampl&0xFF)
                                                    self.reg_5_value = (self.reg_5_value&0xFFFF00FF) + ((self.dly<<8)&0xFF00)
                                                    self.femb_config.femb.write_reg_femb_checked (femb_addr, 5, self.reg_5_value)
                                                    self.femb_config.config_femb(femb_addr, fe_adc_regs, clk_cs, pls_cs, dac_sel, fpga_dac, asic_dac, mon_cs = mon_cs)
                                                    self.femb_config.config_femb_mode(femb_addr,  pls_cs, dac_sel, fpga_dac, asic_dac, mon_cs=mon_cs)

                                                    mondac_vs = self.FEMB_MON_N(femb_addr, N=10000)
                                                    x = [fembchn]*len(mondac_vs)

                                                    if (snc ==0 ):
                                                        snc_str = "BL = 200 mV"
                                                    else:
                                                        snc_str = "BL = 900 mV"
                                                    plt.scatter(x, mondac_vs, marker = '.', label = "FEMB%d_ASIC%d_CHN%d : "%(femb_addr, chip, chn) + snc_str )
                                        plt.title("FEMB%d"%femb_addr + sg_str + tp_str + sdf_str + Leak_Cur)
                                        plt.xlabel ("Channel no.")
                                        plt.ylabel ("MONITOR ADC output / bit")
                                        plt.ylim ((0,2**14))
                                        plt.legend()
                                        plt.grid()
                                        plt.savefig(runpath + "/%s_slk0%d_slk1%d_sdf%d_sg%d_tp%d_femb%d_snc%d"%(monitor_out, slk0, slk1, sdf, sg, tp, femb_addr,snc))
                                        plt.close()


        runtime = int(time.time()) 
        monfile = runpath + "/" + "mon_record_" + str(runtime) +".pickle"

        with open(monfile, "wb") as fp:
            pickle.dump(mon_paras, fp)
        return None


    #for one WIB operation
    def wib_monitor(self, runpath, femb_on_wib):
        mon_paras = []
        clk_cs = 1
        adc_en_gr = 1

        pls_cs = 1
        dac_sel = 1

        adc_oft = 0
        fpga_dac = 0
        asic_dac = 1
        dac = 00
        fembs_np = femb_on_wib #[0,1,2,3]
        #fembs_np = [0]

        for monitor_out in ["pulse",  "bandgap", "temperature"]:
            tvalue_np = []
            if (monitor_out == "pulse"):
                chns = 16
                sncs =[0,1] 
            #    tps = [0,1,2,3] 
                tps = [3] 
            #    gs =[0,1,2,3]
                gs =[1]
            #    slk0s = [0,1]
                slk0s = [0]
            #    slk1s = [0,1]
                slk1s = [0]
            #    sdfs = [0,1]
                sdfs = [0]
            else:
                chns = 1
                sncs =[0] 
                tps = [3] 
                gs =[1]
            #    slk0s = [0,1]
                slk0s = [0]
            #    slk1s = [0,1]
                slk1s = [0]
            #    sdfs = [0,1]
                sdfs = [0]
            for slk0 in slk0s:
               for slk1 in slk1s:
                   for sdf in sdfs:
                        for sg in gs:
                            for tp in tps:
                                for femb_addr in fembs_np:
                                    fig = plt.figure(figsize=(12,8))
                                    plt.rcParams.update({'font.size': 14})
                                    for snc in sncs:
                                        plt_chns = []
                                        plt_mons = []
                                        for chip in range(8):
                                            for chn in range(chns):
                                                val = 25 
                                                if (not(self.jumbo_flag)):
                                                    self.femb_config.femb.write_reg_wib_checked (0x1F, 0x1FB)
                                                    val = val*8
                                                else:
                                                    self.femb_config.femb.write_reg_wib_checked (0x1F, 0xEFB)
                                                self.fe_reg.set_fe_board() # reset the registers value
                    
                                                #set registers for FEMB
                                                self.fe_reg.set_fe_board(sg=sg, st=tp, sts=0, snc=snc, smn=0, sdf=sdf, slk0=slk0, slk1=slk1, swdac =1, dac=dac )
                                                #set global registers for FE
                                                if (monitor_out == "pulse" ):
                                                    self.fe_reg.set_fechip_global(chip=chip, slk0=slk0, stb1 = 0, stb = 0, slk1=slk1, swdac=1, dac=dac)
                                                elif (monitor_out == "bandgap" ):
                                                    self.fe_reg.set_fechip_global(chip=chip, slk0=slk0, stb1 = 1, stb = 1, slk1=slk1, swdac=1, dac=dac)
                                                else:
                                                    self.fe_reg.set_fechip_global(chip=chip, slk0=slk0, stb1 = 0, stb = 1, slk1=slk1, swdac=1, dac=dac)
                                                #set chn registers for FE
                                                if (chip == femb_addr):
                                                    if (snc == 0):
                                                        self.fe_reg.set_fechn_reg(chip=chip, chn=chn, sts=0, snc=1, sg=sg, st=tp, smn=1, sdf=sdf )
                                                    else:
                                                        self.fe_reg.set_fechn_reg(chip=chip, chn=chn, sts=0, snc=0, sg=sg, st=tp, smn=1, sdf=sdf )
                                                else:
                                                    self.fe_reg.set_fechn_reg(chip=chip, chn=chn, sts=0, snc=snc, sg=sg, st=tp, smn=1, sdf=sdf )
                                                #self.fe_reg.set_fechn_reg(chip=chip, chn=chn, sts=0, snc=snc, sg=sg, st=tp, smn=1, sdf=sdf )
                                                fe_regs = copy.deepcopy(self.fe_reg.REGS)
                    
                                                self.adc_reg.set_adc_board(clk0=1,f0 =0) #external clk
                                                adc_clk_regs = copy.deepcopy(self.adc_reg.REGS)
                                                self.adc_reg.set_adc_board(d=adc_oft, engr=adc_en_gr)
                                                adc_engr_regs = copy.deepcopy(self.adc_reg.REGS)
                                                adc_regs = []
                                                for tmpi in range(len(adc_clk_regs)):
                                                    adc_regs.append(adc_clk_regs[tmpi] | adc_engr_regs[tmpi])
                                                self.fe_adc_reg.set_board(fe_regs,adc_regs)
                                                fe_adc_regs = copy.deepcopy (self.fe_adc_reg.REGS)
                    
                                                mon_cs = 1
                                                self.dly  = 10
                                                self.ampl = 0
                                                self.reg_5_value = (self.reg_5_value&0xFFFFFF00) + (self.ampl&0xFF)
                                                self.reg_5_value = (self.reg_5_value&0xFFFF00FF) + ((self.dly<<8)&0xFF00)
                                                self.femb_config.femb.write_reg_femb_checked (femb_addr, 5, self.reg_5_value)
                                                self.femb_config.config_femb(femb_addr, fe_adc_regs, clk_cs, pls_cs, dac_sel, fpga_dac, asic_dac, mon_cs = mon_cs)
                                                self.femb_config.config_femb_mode(femb_addr,  pls_cs, dac_sel, fpga_dac, asic_dac, mon_cs=mon_cs)

                                                mondac_v = self.FEMB_MON(femb_addr)

                                                mon_para = [monitor_out, femb_addr, chip, chn, snc, tp, sg, slk0, slk1, sdf, mondac_v]
                                                print( [monitor_out, femb_addr, chip, chn, snc, tp, sg, slk0, slk1, sdf, mondac_v] )
                                                mon_paras.append(mon_para)
                                                plt_chns.append(chip*16 + chn)
                                                plt_mons.append(mondac_v)
                                        if "pulse" in monitor_out:
                                            if (snc ==0 ):
                                                snc_str = "BL = 200 mV"
                                            else:
                                                snc_str = "BL = 900 mV"
                                        else:
                                            snc_str = monitor_out

                                        if slk0 == 0:
                                            if slk1 == 0: 
                                                Leak_Cur = "Leak_Cur = 500pA, "
                                            else:
                                                Leak_Cur = "Leak_Cur = 5000pA, "
                                        else:
                                            if slk1 == 0: 
                                                Leak_Cur = "Leak_Cur = 100pA, "
                                            else:
                                                Leak_Cur = "Leak_Cur = 1000pA, "

                                        if sdf == 0:
                                            sdf_str = "Buf OFF, "
                                        else:
                                            sdf_str = "Buf ON, "

                                        if sg == 0:
                                            sg_str = "4.7 mV/fC, "
                                        elif sg == 1:
                                            sg_str = "14.0 mV/fC, "
                                        elif sg == 2:
                                            sg_str = "7.8 mV/fC, "
                                        else:
                                            sg_str = "25.0 mV/fC, "

                                        if (tp == 0):
                                            tp_str = "1.0 us, "
                                        elif (tp == 1):
                                            tp_str = "3.0 us, "
                                        elif (tp == 2):
                                            tp_str = "0.5 us, "
                                        elif (tp == 3):
                                            tp_str = "2.0 us, "
 
                                        plt.plot(plt_chns, plt_mons, marker = '.', label = snc_str)
                                    plt.title("FEMB%d"%femb_addr + sg_str + tp_str + sdf_str + Leak_Cur)
                                    plt.xlabel ("Channel no.")
                                    plt.ylabel ("MONITOR ADC output / bit")
                                    plt.ylim ((0,2**14))
                                    plt.legend()
                                    plt.grid()
                                    fn =  runpath + "/%s_slk0%d_slk1%d_sdf%d_sg%d_tp%d_femb%d"%(monitor_out, slk0, slk1, sdf, sg, tp, femb_addr)
                                    print fn
                                    plt.savefig(fn)
                                    plt.close()


        runtime = int(time.time()) 
        monfile = runpath + "/" + "mon_record_" + str(runtime) +".pickle"

        with open(monfile, "wb") as fp:
            pickle.dump(mon_paras, fp)
        return None

    def avg_chkout(self, path, step, femb_addr, sg=2, tp=1, clk_cs=1, pls_cs = 1, dac_sel=1, \
                    fpga_dac=1, asic_dac=0, slk0 = 0, slk1= 0, val=1600):
        print "FEMB_DAQ-->Avergae Check out"
        savepath = self.wib_savepath (path, step)
        file_setadc_rec = savepath + step +"_FEMB" + str(femb_addr)+ str(sg) + str(tp) + "Avg_FE_ADC.txt"
        if os.path.isfile(file_setadc_rec):
            print "%s, file exist!!!"%file_setadc_rec
            sys.exit()
        else:
            self.fe_reg.set_fe_board() # reset the registers value
            self.fe_reg.set_fe_board(sg=sg, st=tp, sts=1, smn=0, sdf=0, slk0=slk0, slk1=slk1, swdac =2, dac=0 )
            fe_regs = copy.deepcopy(self.fe_reg.REGS)
            self.adc_reg.set_adc_board(clk0=1,f0 =0) #external clk
            adc_regs = copy.deepcopy(self.adc_reg.REGS)
            yuv_bias_regs = self.yuv_bias_set(femb_addr)
            fe_bias_regs = self.fe_regs_bias_config(fe_regs, yuv_bias_regs ) #one FEMB
            self.fe_adc_reg.set_board(fe_bias_regs,adc_regs)
            fe_adc_regs = copy.deepcopy(self.fe_adc_reg.REGS)

            if sg == 3: #25mV/fC
                self.ampl = 4
            elif sg == 1: #"14_0mV_"
                self.ampl = 9
            elif sg == 2: #"07_8mV_":
                self.ampl = 15
            elif sg == 0: #"04_7mV_":
                self.ampl = 20
            else:
                self.ampl = 4
            self.dly  = 10
            self.reg_5_value = (self.reg_5_value&0xFFFFFF00) + (self.ampl&0xFF)
            self.reg_5_value = (self.reg_5_value&0xFFFF00FF) + ((self.dly<<8)&0xFF00)
            self.femb_config.femb.write_reg_femb_checked (femb_addr, 5, self.reg_5_value)
            self.femb_config.config_femb(femb_addr, fe_adc_regs ,clk_cs, pls_cs, dac_sel, fpga_dac, asic_dac)
            self.femb_config.config_femb_mode(femb_addr,  pls_cs, dac_sel, fpga_dac, asic_dac)

            self.recfile_save(file_setadc_rec, step, femb_addr, fe_adc_regs) 

            for chip in range(8):
                rawdata = ""
                fe_cfg = int((fe_adc_regs[5])&0xFF)
                fe_cfg_r = int('{:08b}'.format(fe_cfg)[::-1], 2)
                filename = savepath + step +"_FEMB" + str(femb_addr) + "CHIP" + str(chip) + "_" + format(fe_cfg_r,'02X') + "_FPGADAC" + str(self.ampl) + ".bin"
                print filename
                rawdata = self.femb_config.get_rawdata_packets_femb(femb_addr, chip, val)
                if rawdata != None:
                    with open(filename,"wb") as f:
                        f.write(rawdata) 
        return savepath

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

