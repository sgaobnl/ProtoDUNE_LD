# -*- coding: utf-8 -*-
"""
File Name: Main.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 1/13/2018 3:05:03 PM
Last modified: Wed Jun 27 10:07:52 2018
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
    runtime =  datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    logs.append ( "BNL_check_time >> " + runtime )
    print ( "BNL_check_time >> " + runtime )
    version = wib.read_reg_wib(0xFF)

    if lastip == "203":
        wibno = 0
    else:
        wibno = 1
    if ((version &0xFFF) == 0x104) and (version != -1) :
        logs.append (  "BNL_WIB%d_IP >> "%wibno +wib.UDP_IP  )
        print (  "BNL_WIB%d_IP >> "%wibno +wib.UDP_IP  )
        logs.append (  "BNL_WIB%d_Version >> "%wibno + format(version, "08X") )
        print (  "BNL_WIB%d_Version >> "%wibno + format(version, "08X") )
        tmp1 = wib.read_reg_wib(0x100)
        undefno = 1
        logs.append ( "BNL_WIB%d_Undef%d >> "%(wibno, undefno) +"Addr(0x100) = " + format(tmp1, "08X") ) 
        print ( "BNL_WIB%d_Undef%d >> "%(wibno, undefno) +"Addr(0x100) = " + format(tmp1, "08X") ) 
        undefno = undefno + 1 
        
        wib.write_reg_wib(18, 0x100)
        for addr in [32,33,34,35,36,37,38,39]:
            b =  wib.read_reg_wib(addr)
            if addr == 33:
                logs.append ( "BNL_WIB%d_Link >> "%(wibno) + "Addr(0x%X) = "%addr + format(b, "08X") ) 
                print ( "BNL_WIB%d_Link >> "%(wibno) + "Addr(0x%X) = "%addr + format(b, "08X") ) 
            elif addr == 36:
                logs.append ( "BNL_WIB%d_EQ >> "%(wibno) +  "Addr(0x%X) = "%addr + format(b, "08X") ) 
                print ( "BNL_WIB%d_EQ >> "%(wibno) +  "Addr(0x%X) = "%addr + format(b, "08X") ) 
            else:
                logs.append ("BNL_WIB%d_Undef%d >> "%(wibno, undefno) + "Addr(0x%X) = "%addr + format(b, "08X") ) 
                print ("BNL_WIB%d_Undef%d >> "%(wibno, undefno) + "Addr(0x%X) = "%addr + format(b, "08X") ) 
                undefno = undefno + 1 
        
        for i in range(16):
            wib.write_reg_wib(18, i)
            b =  wib.read_reg_wib(34)
            logs.append ( "BNL_WIB%d_Timestamp%d >> "%(wibno, i+1) + "Addr(0x%X) = "%(34) + format(b, "08X") ) 
            print ( "BNL_WIB%d_Timestamp%d >> "%(wibno, i+1) + "Addr(0x%X) = "%(34) + format(b, "08X") ) 

        for j in range(3):
            wib.write_reg_wib(5, 0x00000)
            wib.write_reg_wib(5, 0x00000 | 0x10000)
            wib.write_reg_wib(5, 0x00000)
            time.sleep(0.1)
            vcts =[]
            for i in range(35):
                wib.write_reg_wib(5, i)
                time.sleep(0.001)
                vcts.append(  wib.read_reg_wib(6) & 0x0000FFFFFFFF )
                time.sleep(0.001)

        for fembno in range(4):
            femb_vcts=vcts[fembno*6+1: fembno*6+7]
            vct = []
            vcs = []
            vs  = []
            cs  = []

            vct = np.array(femb_vcts)
            vc25 = vcts[31+fembno]
            vcs = np.append(vct[1:6], vc25) 

            vcsh = (vcs&0x0FFFF0000) >> 16 
            vcshx = vcsh & 0x4000
            for i in range(len(vcsh)):
                if (vcshx[i] == 0 ):
                    vs.append(vcsh[i])
                else:
                    vs.append(0)
            vs = ((np.array(vs) & 0x3FFF) * 305.18) * 0.000001
 
            vcsl = (vcs&0x0FFFF) 
            cs = ((vcsl & 0x3FFF) * 19.075) * 0.000001 / 0.1
            cs[2] = cs[2] / 0.1
            cs[5] = cs[5] / 0.1
            cs_tmp =[]
            for csi in cs:
                if csi < 3.1 :
                    cs_tmp.append(csi)
                else:
                    cs_tmp.append(0)
            cs = np.array(cs_tmp)

            spl_in = (((vct[0]&0x0FFFF0000) >> 16) & 0x3FFF) * 305.18 * 0.000001 + 2.5
            temp = (((vct[0]&0x0FFFF) & 0x3FFF) * 62.5) * 0.001

            logs.append ("BNL_WIB%d_FEMB%d_Tempe>> "%(wibno, fembno) + "Temperature : %3.3f " %temp   ) 
            logs.append ("BNL_WIB%d_FEMB%d_BS50V>> "%(wibno, fembno) + "BIAS 5V : %3.3fV, %3.3fA" %(vs[4], cs[4]) ) 
            logs.append ("BNL_WIB%d_FEMB%d_FM42V>> "%(wibno, fembno) + "FM 4.2V : %3.3fV, %3.3fA" %(vs[0], cs[0]) ) 
            logs.append ("BNL_WIB%d_FEMB%d_FM30V>> "%(wibno, fembno) + "FM 3.0V : %3.3fV, %3.3fA" %(vs[1], cs[1]) ) 
            logs.append ("BNL_WIB%d_FEMB%d_FM15V>> "%(wibno, fembno) + "FM 1.5V : %3.3fV, %3.3fA" %(vs[3], cs[3]) ) 
            logs.append ("BNL_WIB%d_FEMB%d_AM36V>> "%(wibno, fembno) + "AM 3.6V : %3.3fV, %3.3fA" %(vs[2], cs[2]) ) 
            logs.append ("BNL_WIB%d_FEMB%d_AM25V>> "%(wibno, fembno) + "AM 2.5V : %3.3fV, %3.3fA" %(vs[5], cs[5]) ) 
            print ("BNL_WIB%d_FEMB%d_Tempe>> "%(wibno, fembno) + "Temperature : %3.3f " %temp   ) 
            print ("BNL_WIB%d_FEMB%d_BS50V>> "%(wibno, fembno) + "BIAS 5V : %3.3fV, %3.3fA" %(vs[4], cs[4]) ) 
            print ("BNL_WIB%d_FEMB%d_FM42V>> "%(wibno, fembno) + "FM 4.2V : %3.3fV, %3.3fA" %(vs[0], cs[0]) ) 
            print ("BNL_WIB%d_FEMB%d_FM30V>> "%(wibno, fembno) + "FM 3.0V : %3.3fV, %3.3fA" %(vs[1], cs[1]) ) 
            print ("BNL_WIB%d_FEMB%d_FM15V>> "%(wibno, fembno) + "FM 1.5V : %3.3fV, %3.3fA" %(vs[3], cs[3]) ) 
            print ("BNL_WIB%d_FEMB%d_AM36V>> "%(wibno, fembno) + "AM 3.6V : %3.3fV, %3.3fA" %(vs[2], cs[2]) ) 
            print ("BNL_WIB%d_FEMB%d_AM25V>> "%(wibno, fembno) + "AM 2.5V : %3.3fV, %3.3fA" %(vs[5], cs[5]) ) 
    else:
        print "WIB (%s)  doesn't exist or wrong firmware version!)"%(wib.UDP_IP)

logfile =    "/daqdata/BNL_LD_data" + "/WIB_lins_chk.log"
with open(logfile, "a+") as f:
    f.write( "####Begin\n" ) 
    f.write( "####WIB LINKs and Votages and Currents Checkout\n" ) 
    f.write( runtime + "\n" )
    for onelog in logs:
        f.write( "%s\n"%onelog ) 
    f.write ("####There are %d times WIB UDP Registers Write Error"%wib.wib_wrerr_cnt )
    f.write ("####There are %d times FEMB UDP Registers Write Error"%wib.femb_wrerr_cnt )
    f.write ("####There are %d times UDP timeouts"%wib.udp_timeout_cnt )
    f.write ("####There are %d times UDP High Speed links timeouts"%wib.udp_hstimeout_cnt )
    f.write( "####End\n") 
    f.write( "\n") 

