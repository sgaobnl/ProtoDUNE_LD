# -*- coding: utf-8 -*-
"""
File Name: sbnd_femb_meas.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/12/2016 9:30:27 PM
Last modified: Mon Jun 18 16:12:53 2018
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
import pickle
from femb_meas import FEMB_MEAS
from PD_CHKOUT import PD_CHKOUT

###############################################################################
class CE_RUNS:
    def jumbo_flag_set (self ):
        self.femb_meas.jumbo_flag = self.jumbo_flag
        self.femb_meas.femb_config.jumbo_flag = self.jumbo_flag
        self.femb_meas.femb_config.femb.jumbo_flag = self.jumbo_flag

    def WIB_UDP_CTL(self, wib_ip, WIB_UDP_EN = False):
        self.femb_meas.femb_config.femb.UDP_IP = wib_ip 
        wib_reg_7_value = self.femb_meas.femb_config.femb.read_reg_wib (7)
        time.sleep(0.001)
        wib_reg_7_value = self.femb_meas.femb_config.femb.read_reg_wib (7)
        if (WIB_UDP_EN): #enable UDP output
            wib_reg_7_value = wib_reg_7_value & 0x00000000 #bit31 of reg 7 for disable wib udp control
        else: #disable WIB UDP output
            wib_reg_7_value = wib_reg_7_value | 0x80000000 #bit31 of reg 7 for disable wib udp control
        self.femb_meas.femb_config.femb.write_reg_wib_checked (7, wib_reg_7_value)
        #self.femb_meas.femb_config.femb.write_reg_wib_checked (40, 0)
        #self.femb_meas.femb_config.femb.write_reg_wib_checked (41, 0)

    def WIB_self_chk(self ):
        #turn power on
        wib_ips_removed = []
        for wib_ip in self.wib_ips:
            self.femb_meas.femb_config.femb.UDP_IP = wib_ip
            ver_value = self.femb_meas.femb_config.femb.read_reg_wib (0x100)
            ver_value = self.femb_meas.femb_config.femb.read_reg_wib (0xFF)
            ver_value = self.femb_meas.femb_config.femb.read_reg_wib (0xFF)

            if ( (ver_value&0x0FFF) == self.wib_version_id) and (ver_value != -1) :
                print "WIB(%s) passed self check!"%(wib_ip)
            else:
                print "WIB%s fails, mask this WIB!!!"%wib_ip
                wib_ips_removed.append(wib_ip)
                continue
    
            if (self.jumbo_flag):
                jumbo_size = 0xEFB
            else:
                jumbo_size = 0x1FB
            self.femb_meas.femb_config.femb.write_reg_wib_checked (0x1F, jumbo_size)
            #set external clk
            self.femb_meas.femb_config.femb.write_reg_wib_checked (0x4, 8)
            #set normal mode
            self.femb_meas.femb_config.femb.write_reg_wib_checked (16, 0x7F00)
            self.femb_meas.femb_config.femb.write_reg_wib_checked (15, 0)

            #self.femb_meas.femb_config.femb.write_reg_wib_checked (40, 0)
            #self.femb_meas.femb_config.femb.write_reg_wib_checked (41, 0)

        for wib_ip in wib_ips_removed:
                self.wib_ips.remove(wib_ip)

        print self.wib_ips

    def WIB_PLL_wr(self, wib_ip, addr, din):
        self.femb_meas.femb_config.femb.UDP_IP = wib_ip
        value = 0x01 + ((addr&0xFF)<<8) + ((din&0x00FF)<<16)
        self.femb_meas.femb_config.femb.write_reg_wib (11,value)
        time.sleep(0.01)
        self.femb_meas.femb_config.femb.write_reg_wib (10,1)
        time.sleep(0.01)
        self.femb_meas.femb_config.femb.write_reg_wib (10,0)
        time.sleep(0.02)

    def WIB_PLL_cfg(self ):
        with open(self.pllfile,"r") as f:
            line = f.readline()
            adrs_h = []
            adrs_l = []
            datass = []
            cnt = 0
            while line:
                cnt = cnt + 1
                line = f.readline()
                tmp = line.find(",")
                if tmp > 0:
                    adr = int(line[2:tmp],16)
                    adrs_h.append((adr&0xFF00)>>8)
                    adrs_l.append((adr&0xFF))
                    datass.append((int(line[tmp+3:-2],16))&0xFF)
        for wib_ip in self.wib_ips:
            print "configurate PLL of WIB (%s), please wait..."%wib_ip
            p_addr = 1
            #step1
            page4 = adrs_h[0]
            self.WIB_PLL_wr( wib_ip, p_addr, page4)
            self.WIB_PLL_wr( wib_ip, adrs_l[0], datass[0])
            #step2
            page4 = adrs_h[1]
            self.WIB_PLL_wr( wib_ip, p_addr, page4)
            self.WIB_PLL_wr( wib_ip, adrs_l[1], datass[1])
            #step3
            page4 = adrs_h[2]
            self.WIB_PLL_wr( wib_ip, p_addr, page4)
            self.WIB_PLL_wr( wib_ip, adrs_l[2], datass[2])
            time.sleep(0.5)
            #step4
            for cnt in range(len(adrs_h)):
                if (page4 == adrs_h[cnt]):
                    tmpadr = adrs_l[2]
                    self.WIB_PLL_wr(wib_ip, adrs_l[cnt], datass[cnt])
                else:
                    page4 = adrs_h[cnt]
                    self.WIB_PLL_wr( wib_ip, p_addr, page4)
                    self.WIB_PLL_wr(wib_ip, adrs_l[cnt], datass[cnt])

            for i in range(10):
                time.sleep(3)
                print "check PLL status, please wait..."
                self.femb_meas.femb_config.femb.UDP_IP = wib_ip
                ver_value = self.femb_meas.femb_config.femb.read_reg_wib (12)
                ver_value = self.femb_meas.femb_config.femb.read_reg_wib (12)
                lol = (ver_value & 0x10000)>>16
                lolXAXB = (ver_value & 0x20000)>>17
                INTR = (ver_value & 0x40000)>>18
                if (lol == 1):
                    print "PLL of WIB(%s) is locked"%wib_ip
                    break
                if (i ==9):
                    print "Fail to configurate PLL of WIB(%s), please check "%wib_ip
                    print "Exit anyway"
                    sys.exit()

    def WIB_LINK_CUR(self):
        logs = []
        runtime =  datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        logs.append ( runtime + "--> Link and current check" )
        #link
        tmp1 = self.femb_meas.femb_config.femb.read_reg_wib(0x100)
        logs.append ( "Addr(0x100) = " + format(tmp1, "08X") ) 
        self.femb_meas.femb_config.femb.write_reg_wib(18, 0x100)
        for addr in [32,33,34,35,36,37,38,39]:
            b =  self.femb_meas.femb_config.femb.read_reg_wib(addr)
            logs.append ( "Addr(0x%X) = "%addr + format(b, "08X") ) 
 
        for i in range(16):
            self.femb_meas.femb_config.femb.write_reg_wib(18, i)
            b =  self.femb_meas.femb_config.femb.read_reg_wib(34)
            logs.append ( "Addr(0x%X) = "%(34) + format(b, "08X") ) 
        #current 
        for j in range(3):
            self.femb_meas.femb_config.femb.write_reg_wib(5, 0x00000)
            self.femb_meas.femb_config.femb.write_reg_wib(5, 0x00000 | 0x10000)
            self.femb_meas.femb_config.femb.write_reg_wib(5, 0x00000)
            time.sleep(0.1)
            vcts =[]
            for i in range(30):
                self.femb_meas.femb_config.femb.write_reg_wib(5, i)
                time.sleep(0.001)
                vcts.append(  self.femb_meas.femb_config.femb.read_reg_wib(6) & 0x0000FFFFFFFF )
                time.sleep(0.001)

        for fembno in range(4):
            femb_vcts=vcts[fembno*6+1: fembno*6+7]
            vcs = np.array(femb_vcts)
            vcsh = (vcs[1:6]&0x0FFFF0000) >> 16 
            vcshx = vcsh & 0x4000
            vs = []
            for i in range(len(vcsh)):
                if (vcshx[i] == 0 ):
                    vs.append(vcsh[i])
                else:
                    vs.append(0)
            vs = ((np.array(vs) & 0x3FFF) * 305.18) * 0.000001
            vcsl = (vcs[1:6]&0x0FFFF) 
            cs = ((vcsl & 0x3FFF) * 19.075) * 0.000001 / 0.1
            cs[2] = cs[2] / 0.1
            cs_tmp =[]
            for csi in cs:
                if csi < 3.1 :
                    cs_tmp.append(csi)
                else:
                    cs_tmp.append(0)
            cs = np.array(cs_tmp)

            spl_in = (((vcs[0]&0x0FFFF0000) >> 16) & 0x3FFF) * 305.18 * 0.000001 + 2.5
            temp = (((vcs[0]&0x0FFFF) & 0x3FFF) * 62.5) * 0.001

            logs.append ( "FEMB%d " %fembno   ) 
            logs.append ( "Temperature = %3.5f " %temp   ) 
            logs.append ( "BIAS 5V : %3.5fV, %3.5fA" %(vs[4], cs[4]) ) 
            logs.append ( "FM 4.2V : %3.5fV, %3.5fA" %(vs[0], cs[0]) ) 
            logs.append ( "FM 3.0V : %3.5fV, %3.5fA" %(vs[1], cs[1]) ) 
            logs.append ( "FM 1.5V : %3.5fV, %3.5fA" %(vs[3], cs[3]) ) 
            logs.append ( "AM 2.5V : %3.5fV, %3.5fA" %(vs[2], cs[2]) ) 
        logs.append ( "--> Link and current check done" )
        self.linkcurs = self.linkcurs + logs

    def FEMBs_PWR_SW(self, SW = "ON"):
        run_code, val, runpath = self.save_setting(run_code="C", val=100) 
        self.run_code = run_code
        self.runpath = runpath
        self.runtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        self.linkcurs = []
        for wib_addr in range(len(self.wib_ips)):
            wib_ip = self.wib_ips[wib_addr]
            wib_pos = wib_addr
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = True)
            self.WIB_LINK_CUR( )
            femb_pwr = self.wib_pwr_femb[wib_pos]
            if (femb_pwr[0] == 1 ):
                fe0_pwr = 0x31000F
            else:
                fe0_pwr = 0x00000
            if (femb_pwr[1] == 1 ):
                fe1_pwr = 0x5200F0
            else:
                fe1_pwr = 0x00000
            if (femb_pwr[2] == 1 ):
                fe2_pwr = 0x940F00
            else:
                fe2_pwr = 0x000000
            
            if (femb_pwr[3] == 1 ):
                fe3_pwr = 0x118F000
            else:
                fe3_pwr = 0x000000
            self.femb_meas.femb_config.femb.write_reg_wib_checked (8, 0)
            time.sleep(3)
            if ( SW == "ON"):
                print "turn on power supply on WIB(IP=%s)"%(wib_ip)
                pwr_value = long (0x1000000)| fe0_pwr| fe1_pwr| fe2_pwr| fe3_pwr
                #pwr_value = long (0xFFFE00000) | pwr_value #SBND WIB
                self.femb_meas.femb_config.femb.write_reg_wib_checked (8, pwr_value)
                time.sleep(5)
                print "All FEMBs have been turned on"
                time.sleep(5)
            else:
                print "All FEMBs have been turned off"
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = False)

    def FEMBs_Self_CHK(self):
        run_code, val, runpath = self.save_setting(run_code="D", val=100) 
        self.run_code = run_code
        self.runpath = runpath
        self.runtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

        if (self.COTSADC):
            print "COTS ADC in use"
            self.en_oft = False #COTS ADC
        else:
            print "P1 ADC in use"
            self.en_oft = True #P1 ADC
        self.femb_meas.fe_adc_reg.COTSADC = self.COTSADC
        self.femb_meas.femb_config.COTSADC = self.COTSADC

        mask_femb = []
        for wib_addr in range(len(self.wib_ips)):
            wib_ip = self.wib_ips[wib_addr]
            wib_pos = wib_addr
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = True)
            print "Start FEMBs of WIB(IP=%s) self-check"%(wib_ip)
            self.femb_on_apa ()
            femb_on_wib = self.alive_fembs[wib_pos] 
            for femb_addr in femb_on_wib:
                self.femb_meas.femb_n = wib_addr * 4 + femb_addr
                udp_errcnt_pre = self.femb_meas.femb_config.femb.femb_wrerr_cnt
                ver_value = self.femb_meas.femb_config.femb.read_reg_femb(femb_addr, 0x102)
                ver_value = self.femb_meas.femb_config.femb.read_reg_femb(femb_addr, 0x101)
                ver_value = self.femb_meas.femb_config.femb.read_reg_femb(femb_addr, 0x101)
                print "WIB%dFEMB%d firmware version: %X"%((wib_pos+1), femb_addr, ver_value )
                if ( (ver_value &0xFFF) == self.femb_ver_id ) and (ver_value != -1) :
                    print "WIB%dFEMB%d is good"%((wib_pos+1), femb_addr)
                    self.femb_mask[wib_pos][femb_addr]  = 0
                else:
                    self.femb_mask[wib_pos][femb_addr]  = 1
                    mask_femb.append( "WIB%d(IP%s)FEMB%d is masked"%((wib_pos+1), wib_ip, femb_addr) )
                    print "WIB%dFEMB%d version value(%x) is wrong , mask it"%((wib_pos+1), femb_addr, ver_value)
                udp_errcnt_post = self.femb_meas.femb_config.femb.femb_wrerr_cnt
                self.udp_err_np.append([wib_ip, wib_pos, femb_addr, udp_errcnt_post, udp_errcnt_pre, self.run_code] )
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = False)
        return mask_femb

    def oft_run(self): 
        run_code, val, runpath = self.save_setting(run_code="B", val=100) 
        self.run_code = run_code
        apa_oft_info = [[]]*20
        for wib_addr in range(len(self.wib_ips)):
            wib_ip = self.wib_ips[wib_addr]
            wib_pos = wib_addr
            print "WIB%d (IP=%s) OFT running"%((wib_pos+1), wib_ip)
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = True)
            self.femb_on_apa ()
            femb_on_wib = self.alive_fembs[wib_pos] 
            for femb_addr in femb_on_wib:
                self.femb_meas.femb_n = wib_addr * 4 + femb_addr
                self.femb_meas.femb_n = wib_addr * 4 + femb_addr
                udp_errcnt_pre = self.femb_meas.femb_config.femb.femb_wrerr_cnt
                apaloc = wib_pos*4 + femb_addr
                self.en_oft = False
                print "Ingore oft (only for P1 ADC)"
                femb_addr, adc_oft_regs, yuv_bias_regs = self.femb_meas.femb_oft_set(femb_addr, en_oft = self.en_oft ) 
                apa_oft_info[apaloc] = [wib_ip, femb_addr, copy.deepcopy(adc_oft_regs), copy.deepcopy(yuv_bias_regs)]
                udp_errcnt_post = self.femb_meas.femb_config.femb.femb_wrerr_cnt
                self.udp_err_np.append([wib_ip, wib_pos, femb_addr, udp_errcnt_post, udp_errcnt_pre, self.run_code] )
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = False)
        timestampe =  datetime.now().strftime('%m%d%Y_%H%M%S')
        savefile = runpath +  "APA_ADC_OFT_" + timestampe + '.bin'
        if (os.path.isfile(savefile)): 
            print "%s, file exist!!!"%savefile
            sys.exit()
        else:
            with open(savefile, "wb") as fp:
                pickle.dump(apa_oft_info, fp)
        self.runpath = runpath
        self.runtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        return apa_oft_info

    def femb_oft_bias_regs (self, apa_oft_info, wib_ip, femb_addr):
        adc_oft_regs = []
        yuv_bias_regs = [] 
        for oneinfo in apa_oft_info:
            if oneinfo != [] :
                if (oneinfo[0] ==wib_ip) and (oneinfo[1] ==femb_addr):
                    adc_oft_regs = oneinfo[2]
                    yuv_bias_regs = oneinfo[3] 
                    break
        return adc_oft_regs, yuv_bias_regs

    def femb_on_apa (self):
        apa_fembs = []
        i = 0
        for wibfemb_pwr in self.wib_pwr_femb:
            femb_on_wib = []
            for femb_no in range(len(wibfemb_pwr)):
                if (wibfemb_pwr[femb_no] == 1 ) and ( self.femb_mask[i][femb_no] == 0 ):
                    femb_on_wib.append(femb_no)
            apa_fembs.append(femb_on_wib)
            i = i + 1
        print "FEMBs alive: "
        print apa_fembs
        self.alive_fembs = apa_fembs

    def save_setting(self,  run_code="0", val=100): 
        runtime =  datetime.now().strftime('%m_%d_%Y')
        run_cycle = 1
        run_no = "run" + format(run_cycle,'02d')
        if (run_code == "0" ):
            run_type = "chk"
        elif (run_code == "1" ):
            run_type = "rms"
        elif (run_code == "2" ):
            run_type = "fpg"
        elif (run_code == "4" ):
            run_type = "asi"
        elif (run_code == "8" ):
            run_type = "bbm"
        elif (run_code == "9" ):
            run_type = "tmp"
        elif (run_code == "A" ):
            run_type = "avg"
        elif (run_code == "B" ):
            run_type = "oft"
        elif (run_code == "C" ):
            run_type = "pwr"
        elif (run_code == "D" ):
            run_type = "msk"
        elif (run_code == "E" ):
            run_type = "cfg"
        else:
            run_type = "und"

        runpath = self.path + "Rawdata_" + runtime + "/" + run_no + run_type + "/"
        while ( os.path.exists(runpath) ):
            run_cycle = run_cycle + 1
            run_no = "run" + format(run_cycle,'02d')
            runpath = self.path + "Rawdata_" + runtime + "/" + run_no + run_type + "/"
        try: 
            os.makedirs(runpath)
        except OSError:
            if os.path.exists(runpath):
                pass

        if (not(self.jumbo_flag)):
            self.femb_meas.femb_config.femb.write_reg_wib_checked (0x1F, 0x1FB)
            val = val*8
        else:
            self.femb_meas.femb_config.femb.write_reg_wib_checked (0x1F, 0xEFB)
            val = val        
        return run_code, val, runpath

    def larcfg_run(self, apa_oft_info, sgs = [3], tps =[0,1,2,3], pls_cs=0, dac_sel=1, fpgadac_en=0, asicdac_en=0, vdac = 0, val = 1000, mbb =0, datamode=0): 
        run_code, val, runpath = self.save_setting(run_code="E", val=val) 
        self.run_code = run_code
        mbb_en = (mbb & 0x100)>>8
        PLL_cfgflg = True
        for wib_addr in range(len(self.wib_ips)):
            wib_ip = self.wib_ips[wib_addr]
            wib_pos = wib_addr

            if (mbb_en ==1):
                if (PLL_cfgflg):
                    self.WIB_PLL_cfg( )
                    PLL_cfgflg = False
                self.femb_meas.femb_config.femb.UDP_IP = wib_ip
                self.femb_meas.femb_config.femb.write_reg_wib (4, 0x03)
                time.sleep(0.01)
                self.femb_meas.femb_config.femb.write_reg_wib (4, 0x00)
                time.sleep(0.01)
                self.femb_meas.femb_config.femb.write_reg_wib (4, 0x03)

            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = True)
            self.femb_on_apa ()
            femb_on_wib = self.alive_fembs[wib_pos] 
            for femb_addr in femb_on_wib:
                self.femb_meas.femb_config.femb.write_reg_femb_checked (femb_addr, 42, 0 )
                self.femb_meas.femb_n = wib_addr * 4 + femb_addr
                udp_errcnt_pre = self.femb_meas.femb_config.femb.femb_wrerr_cnt
                adc_oft_regs, yuv_bias_regs = self.femb_oft_bias_regs (apa_oft_info, wib_ip, femb_addr)
                for sg in sgs:
                    for tp in tps:
                        step = "WIB" + format(wib_pos, '02d') + "step" + str(sg) + run_code
                        self.femb_meas.lar_cfg(runpath, step, femb_addr, sg, tp, adc_oft_regs, yuv_bias_regs, \
                                               pls_cs = pls_cs, dac_sel=dac_sel, fpga_dac_en=fpgadac_en, \
                                               asic_dac_en=asicdac_en, dac_val = vdac, slk0 = self.slk0, slk1= self.slk1, val=val)
                        #sync nevis daq
                        self.femb_meas.femb_config.femb.UDP_IP = wib_ip
                        self.femb_meas.femb_config.femb.write_reg_wib (20, 0x00)
                        self.femb_meas.femb_config.femb.write_reg_wib (20, 0x00)
                        time.sleep(0.1)
                        self.femb_meas.femb_config.femb.write_reg_wib (20, 0x02)
                        self.femb_meas.femb_config.femb.write_reg_wib (20, 0x02)
                        time.sleep(0.1)
                        self.femb_meas.femb_config.femb.write_reg_wib (20, 0x00)
                        self.femb_meas.femb_config.femb.write_reg_wib (20, 0x00)

		if datamode == 3:
                    lar_fembno = (((wib_pos + femb_addr)&0x0F)<<4) + datamode
                    self.femb_meas.femb_config.femb.write_reg_femb_checked (femb_addr, 42,lar_fembno )
                udp_errcnt_post = self.femb_meas.femb_config.femb.femb_wrerr_cnt
                self.udp_err_np.append([wib_ip, wib_pos, femb_addr, udp_errcnt_post, udp_errcnt_pre, self.run_code] )
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = False)

            #sync nevis daq
            self.femb_meas.femb_config.femb.UDP_IP = wib_ip
            self.femb_meas.femb_config.femb.write_reg_wib (20, 0x00)
            self.femb_meas.femb_config.femb.write_reg_wib (20, 0x00)
            time.sleep(0.1)
            self.femb_meas.femb_config.femb.write_reg_wib (20, 0x02)
            self.femb_meas.femb_config.femb.write_reg_wib (20, 0x02)
            time.sleep(0.1)
            self.femb_meas.femb_config.femb.write_reg_wib (20, 0x00)
            self.femb_meas.femb_config.femb.write_reg_wib (20, 0x00)

        if (mbb_en):
            self.mbb_run(mbb)

        for wib_addr in range(len(self.wib_ips)):
            wib_ip = self.wib_ips[wib_addr]
            wib_pos = wib_addr
            #sync nevis daq
            time.sleep(2)
            self.femb_meas.femb_config.femb.UDP_IP = wib_ip
            self.femb_meas.femb_config.femb.write_reg_wib (20, 0x00)
            self.femb_meas.femb_config.femb.write_reg_wib (20, 0x00)
            time.sleep(0.1)
            self.femb_meas.femb_config.femb.write_reg_wib (20, 0x02)
            self.femb_meas.femb_config.femb.write_reg_wib (20, 0x02)
            time.sleep(0.1)
            self.femb_meas.femb_config.femb.write_reg_wib (20, 0x00)
            self.femb_meas.femb_config.femb.write_reg_wib (20, 0x00)

        self.runpath = runpath
        self.runtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

    def mbb_run(self, mbb=0 ): 
        mbb_en = (mbb & 0x100)>>8
        mbb_cal = (mbb & 0x1)>>0
        mbb_trst = (mbb & 0x2)>>1
        mbb_stopdaq = (mbb & 0x4)>>2
        mbb_startdaq = (mbb & 0x8)>>3
        mbb_cal_en = (mbb & 0x10)>>4
        mbb_trst_en = (mbb & 0x20)>>5
        mbb_stopdaq_en = (mbb & 0x40)>>6
        mbb_startdaq_en = (mbb & 0x80)>>7

        self.femb_meas.femb_config.femb.UDP_IP = self.mbb_ip
        mbb_tmp1=0
        if (mbb_cal == 1):
            mbb_tmp1 = mbb_tmp1 | 0x01
        if (mbb_trst == 1):
            mbb_tmp1 = mbb_tmp1 | 0x02
        if (mbb_stopdaq == 1):
            mbb_tmp1 = mbb_tmp1 | 0x04
        if (mbb_startdaq == 1):
            mbb_tmp1 = mbb_tmp1 | 0x08
        self.femb_meas.femb_config.femb.write_reg_wib (1, mbb_tmp1)
        self.femb_meas.femb_config.femb.write_reg_wib (1, mbb_tmp1)
        time.sleep(0.01)
        self.femb_meas.femb_config.femb.write_reg_wib (1, 0)
        self.femb_meas.femb_config.femb.write_reg_wib (1, 0)

        mbb_tmp2 = 0
        if (mbb_cal_en == 1):
            mbb_tmp2 = mbb_tmp2 | 0x01
        if (mbb_trst_en == 1):
            mbb_tmp2 = mbb_tmp2 | 0x02
        if (mbb_stopdaq_en == 1):
            mbb_tmp2 = mbb_tmp2 | 0x04
        if (mbb_startdaq_en == 1):
            mbb_tmp2 = mbb_tmp2 | 0x08
        self.femb_meas.femb_config.femb.write_reg_wib (2, mbb_tmp2)
        self.femb_meas.femb_config.femb.write_reg_wib (2, mbb_tmp2)
        time.sleep(0.01)

        time.sleep(1)


    def qc_run(self, apa_oft_info, sgs = [3], tps =[0,1,2,3], val = 100): 
        run_code, val, runpath = self.save_setting(run_code="0", val=val) 
        self.run_code = run_code
        for wib_addr in range(len(self.wib_ips)):
            wib_ip = self.wib_ips[wib_addr]
            wib_pos = wib_addr
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = True)
            self.femb_on_apa ()
            femb_on_wib = self.alive_fembs[wib_pos] 
            for femb_addr in femb_on_wib:
                self.femb_meas.femb_n = wib_addr * 4 + femb_addr
                udp_errcnt_pre = self.femb_meas.femb_config.femb.femb_wrerr_cnt
                adc_oft_regs, yuv_bias_regs = self.femb_oft_bias_regs (apa_oft_info, wib_ip, femb_addr)
                for sg in sgs:
                    for tp in tps:
                        step = "WIB" + format(wib_pos, '02d') + "step" + str(sg) + run_code
                        self.femb_meas.save_chkout(runpath, step, femb_addr, sg, tp, adc_oft_regs, yuv_bias_regs, clk_cs=1, pls_cs = 1, \
                                                   dac_sel=1, fpga_dac=1, asic_dac=0, slk0 = self.slk0, slk1= self.slk1,  val=val)
                udp_errcnt_post = self.femb_meas.femb_config.femb.femb_wrerr_cnt
                self.udp_err_np.append([wib_ip, wib_pos, femb_addr, udp_errcnt_post, udp_errcnt_pre, self.run_code] )
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = False)
        self.runpath = runpath
        self.runtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

    def rms_run(self, apa_oft_info, sgs = [1,3], tps =[0,1,2,3], val=1600): 
        run_code, val, runpath = self.save_setting(run_code="1", val=val) 
        self.run_code = run_code
        for wib_addr in range(len(self.wib_ips)):
            wib_ip = self.wib_ips[wib_addr]
            wib_pos = wib_addr
            print "WIB%d (IP=%s)"%((wib_pos+1), wib_ip)
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = True)
            self.femb_on_apa ()
            femb_on_wib = self.alive_fembs[wib_pos] 
            for femb_addr in femb_on_wib:
                self.femb_meas.femb_n = wib_addr * 4 + femb_addr
                udp_errcnt_pre = self.femb_meas.femb_config.femb.femb_wrerr_cnt
                adc_oft_regs, yuv_bias_regs = self.femb_oft_bias_regs (apa_oft_info, wib_ip, femb_addr)
                for sg in sgs:
                    for tp in tps:
                        step = "WIB" + format(wib_pos, '02d')  + "step" + str(sg) + run_code
                        self.femb_meas.save_rms_noise(runpath, step, femb_addr, sg, tp, adc_oft_regs, yuv_bias_regs, clk_cs=1, pls_cs = 1, \
                                               dac_sel=0, fpga_dac=0, asic_dac=0, slk0 = self.slk0, slk1= self.slk1,  val=val)
                udp_errcnt_post = self.femb_meas.femb_config.femb.femb_wrerr_cnt
                self.udp_err_np.append([wib_ip, wib_pos, femb_addr, udp_errcnt_post, udp_errcnt_pre, self.run_code] )
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = False)
        self.runpath = runpath
        self.runtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

    def fpgadac_run(self, apa_oft_info, sgs = [1,3], tps =[0,1,2,3], val=100): 
        run_code, val, runpath = self.save_setting(run_code="2", val=val) 
        self.run_code = run_code
        for wib_addr in range(len(self.wib_ips)):
            wib_ip = self.wib_ips[wib_addr]
            wib_pos = wib_addr
            print "WIB%d (IP=%s)"%((wib_pos+1), wib_ip)
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = True)
            self.femb_on_apa ()
            femb_on_wib = self.alive_fembs[wib_pos] 
            for femb_addr in femb_on_wib:
                self.femb_meas.femb_n = wib_addr * 4 + femb_addr
                udp_errcnt_pre = self.femb_meas.femb_config.femb.femb_wrerr_cnt
                adc_oft_regs, yuv_bias_regs = self.femb_oft_bias_regs (apa_oft_info, wib_ip, femb_addr)
                for sg in sgs:
                    for tp in tps:
                        step = "WIB" + format(wib_pos, '02d')  + "step" + str(sg) + run_code
                        self.femb_meas.fpga_dac_cali(runpath, step, femb_addr,  sg, tp, adc_oft_regs, yuv_bias_regs, clk_cs=1, pls_cs = 1, \
                                dac_sel=1, fpga_dac=1, asic_dac=0, slk0 = self.slk0, slk1= self.slk1,  val=val)
                udp_errcnt_post = self.femb_meas.femb_config.femb.femb_wrerr_cnt
                self.udp_err_np.append([wib_ip, wib_pos, femb_addr, udp_errcnt_post, udp_errcnt_pre, self.run_code] )
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = False)
        self.runpath = runpath
        self.runtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 


    def asicdac_run(self, apa_oft_info, sgs = [1,3], tps =[0,1,2,3], val=100): 
        run_code, val, runpath = self.save_setting(run_code="4", val=val) 
        self.run_code = run_code
        for wib_addr in range(len(self.wib_ips)):
            wib_ip = self.wib_ips[wib_addr]
            wib_pos = wib_addr
            print "WIB%d (IP=%s)"%((wib_pos+1), wib_ip)
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = True)
            self.femb_on_apa ()
            femb_on_wib = self.alive_fembs[wib_pos] 
            for femb_addr in femb_on_wib:
                self.femb_meas.femb_n = wib_addr * 4 + femb_addr
                udp_errcnt_pre = self.femb_meas.femb_config.femb.femb_wrerr_cnt
                adc_oft_regs, yuv_bias_regs = self.femb_oft_bias_regs (apa_oft_info, wib_ip, femb_addr)
                for sg in sgs:
                    for tp in tps:
                        step = "WIB" + format(wib_pos, '02d')  + "step" + str(sg) + run_code
                        self.femb_meas.asic_dac_cali(runpath, step, femb_addr,  sg, tp, adc_oft_regs, yuv_bias_regs, clk_cs=1, pls_cs = 1, \
                                dac_sel=1, fpga_dac=0, asic_dac=1, slk0 = self.slk0, slk1= self.slk1,  val=val)
                udp_errcnt_post = self.femb_meas.femb_config.femb.femb_wrerr_cnt
                self.udp_err_np.append([wib_ip, wib_pos, femb_addr, udp_errcnt_post, udp_errcnt_pre, self.run_code] )
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = False)
        self.runpath = runpath
        self.runtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

    def brombreg_run(self, apa_oft_info, sgs = [1,3], tps =[0,1,2,3], cycle=150): 
        run_code, val, runpath = self.save_setting(run_code="8", val=100) 
        for bbwib_pos in range(len(self.bbwib_ips)):
            wib_ip = self.bbwib_ips[bbwib_pos]
            print "WIB%d (IP=%s)"%((bbwib_pos+1), wib_ip)
            for wib_addr in range(len(self.wib_ips)):
                if (wib_ip == self.wib_ips[wib_addr]):
                    break
            wib_pos = wib_addr
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = True)

#            self.femb_meas.femb_config.femb.write_reg_wib_checked (40, 1)
#            self.femb_meas.femb_config.femb.write_reg_wib_checked (41, 6400)

            self.femb_on_apa ()
            femb_on_wib = self.alive_fembs[wib_pos] 
            #if (femb_on_wib != [0,1,2,3] ):
            #    print "Brombreg mode asks for 4 FEMB on the same WIB,  anyway!!"
                #sys.exit()

            adc_oft_regs_np = [[], [], [], []]
            yuv_bias_regs_np = [[], [], [], []]
            for femb_addr in femb_on_wib:
                self.femb_meas.femb_n = wib_addr * 4 + femb_addr
                adc_oft_regs, yuv_bias_regs = self.femb_oft_bias_regs (apa_oft_info, wib_ip, femb_addr)
                adc_oft_regs_np[femb_addr] = adc_oft_regs
                yuv_bias_regs_np[femb_addr] = yuv_bias_regs

            for sg in sgs:
                for tp in tps:
                    step = "WIB" + format(wib_pos, '02d') + "step" + str(sg) + run_code
                    self.femb_meas.wib_brombreg_acq(runpath, step, femb_on_wib, sg, tp, adc_oft_regs_np, yuv_bias_regs_np, clk_cs=1, pls_cs = 1, dac_sel=0, \
                                     fpga_dac=0, asic_dac=0, slk0 = self.slk0, slk1= self.slk1, cycle=cycle)

            #self.femb_meas.femb_config.femb.write_reg_wib_checked (40, 0)
            #self.femb_meas.femb_config.femb.write_reg_wib_checked (41, 0)
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = False)
        self.run_code = run_code
        self.runpath = runpath
        self.runtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

    def monitor_run(self, temp_or_pluse = "temp", chn=0): 
        #temp_or_pluse: temp, pulse, banggap
        run_code, val, runpath = self.save_setting(run_code="9", val=100) 
        for tmpwib_pos in range(len(self.tmp_wib_ips)):
            wib_ip = self.tmp_wib_ips[tmpwib_pos]
            print "WIB%d (IP=%s)"%((tmpwib_pos+1), wib_ip)
            for wib_addr in range(len(self.wib_ips)):
                if (wib_ip == self.wib_ips[wib_addr]):
                    break
            wib_pos = wib_addr
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = True)
            self.femb_on_apa ()
            femb_on_wib = self.alive_fembs[wib_pos] 
            if (femb_on_wib != [0,1,2,3] ):
                "Monitor mode asks for 4 FEMBs on the same WIB with JTAG test board, eixt anyway!!"
                sys.exit()
            self.femb_meas.wib_monitor(runpath, temp_or_pluse = temp_or_pluse, chn=chn )
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = False)
        self.run_code = run_code
        self.runpath = runpath
        self.runtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

    def avg_run(self, val = 1600, avg_cycle=300): 

        run_code, val, runpath = self.save_setting(run_code="A", val=val) 
        resultpaths = []
        for wib_pos in range(len(self.wib_ips)):
            wib_ip = self.wib_ips[wib_pos]
            print "WIB (IP=%s)"%(wib_ip)
            for wib_addr in range(len(self.wib_ips)):
                if (wib_ip == self.wib_ips[wib_addr]):
                    break
            wib_pos = wib_addr
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = True)
            self.femb_on_apa ()
            femb_on_wib = self.alive_fembs[wib_pos] 
            for femb_addr in femb_on_wib:
                self.femb_meas.femb_n = wib_addr * 4 + femb_addr
                sg=2
                tp=1
                step = self.ceboxes[femb_addr] + "WIB" + format(wib_pos, '02d') +  "step" + str(sg) + run_code
                datapath= self.femb_meas.avg_chkout(runpath, step, femb_addr, sg=sg, tp=tp, clk_cs=1, pls_cs = 1, dac_sel=1, \
                                          fpga_dac=1, asic_dac=0, slk0 = self.slk0, slk1= self.slk1, val=val)
                
                PD_CHKOUT (datapath, step, plot_en=0x3F,  avg_cycle=avg_cycle, jumbo_flag=self.jumbo_flag )
                resultpaths.append(datapath)
            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = False)
        print "Please check the pdf format files in the folder below: "
        for onepath in resultpaths:
            print onepath
        self.run_code = run_code
        self.runpath = runpath
        self.runtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

    def __init__(self):
        self.path = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/" 
        self.wib_ips = ["10.73.137.20", "10.73.137.21", "10.73.137.22", "10.73.137.23", "10.73.137.24"]  
        self.wib_version_id = 0x116
        self.femb_ver_id = 0x323
        self.wib_pwr_femb = [[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1]]
        self.femb_mask    = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        self.alive_fembs =  [[0,1,2,3],[0,1,2,3],[0,1,2,3],[0,1,2,3],[0,1,2,3]]
        self.env = "RT"
        self.bbwib_ips = ["10.73.137.24"] 
        self.tmp_wib_ips = ["10.73.137.24"] 
        self.jumbo_flag = True
        self.runpath = ""
        self.runtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        self.run_code = "0"
        self.udp_err_np = []
        self.ceboxes = []
        self.linkcurs = []

        self.avg_wib_ips = ["10.73.137.20"] 
        self.avg_wib_pwr_femb = [[1,0,0,0]]
        self.avg_femb_on_wib = [0]
        self.en_oft = False #COTS ADC

        self.sts_tuple = ((0,"CapOff_"), (1,"CapOnn_"))
        self.snc_tuple = ((0,"900mV_"), (1,"200mV_"))
        self.sg_tuple  = ((0,"04_7mV_"), (2,"07_8mV_"), (1,"14_0mV_"), (3,"25_0mV_"))
        self.st_tuple  = ((2,"0_5us_"), (0,"1_0us_"), (3,"2_0us_"), (1,"3_0us_"))
        self.smn_tuple = ((0, "MOFF"), (1, "M_ON"))
        self.sdf_tuple = ((0, "BufOff_" ), (1, "BufOnn_" )) 
        self.slk0_tuple = ((0,"500pA_"), (1, "100pA_"))
        self.slk1_tuple = ((0,"pAx10Dis_"), (1, "pAx10Enn_"))
        self.slk0 = 0
        self.slk1 = 0
        self.APA = "LArIAT"
        self.femb_meas = FEMB_MEAS()
        self.COTSADC = False
        self.pllfile = "./Si5344-RevD-SBND_V3.txt"
        self.mbb_ip = "131.225.150.209"
            
