# -*- coding: utf-8 -*-
"""
File Name: Main.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 1/13/2018 3:05:03 PM
Last modified: Mon 04 Jun 2018 04:46:19 PM CEST
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

logs = []
for lastip in ["31", "32", "33", "34", "35"]:
#for lastip in [ wib_lastbyte,]:
    wib.UDP_IP = "10.73.137." +  lastip
    runtime =  datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    logs.append ( runtime )
    version = wib.read_reg_wib(0xFF)
    if ((version &0xFFF) == 0x116) and (version != -1) :
        logs.append ( wib.UDP_IP +": Addr(0xFF) =  " + format(version, "08X") )
        print wib.UDP_IP , hex(version)
        tmp1 = wib.read_reg_wib(0x100)
        logs.append ( "Addr(0x100) = " + format(tmp1, "08X") ) 
        
        wib.write_reg_wib(18, 0x100)
        for addr in [32,33,34,35,36,37,38,39]:
            b =  wib.read_reg_wib(addr)
            print addr, hex(b)
            logs.append ( "Addr(0x%X) = "%addr + format(b, "08X") ) 
        
        logs.append ( "##########################")  
        for i in range(16):
            wib.write_reg_wib(18, i)
            b =  wib.read_reg_wib(34)
            print 34, hex(b)
            logs.append ( "Addr(0x%X) = "%(34) + format(b, "08X") ) 
        logs.append ( "##########################\n")  

        logs.append ( "########CURRENT##############")  
        for j in range(3):
            wib.write_reg_wib(5, 0x00000)
            wib.write_reg_wib(5, 0x00000 | 0x10000)
            wib.write_reg_wib(5, 0x00000)
            time.sleep(0.1)
            vcts =[]
            for i in range(30):
                wib.write_reg_wib(5, i)
                time.sleep(0.001)
                vcts.append(  wib.read_reg_wib(6) & 0x0000FFFFFFFF )
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

            print ( "FEMB%d " %fembno   ) 
            print ( "Temperature = %3.5f " %temp   ) 
            print ( "BIAS 5V : %3.5fV, %3.5fA" %(vs[4], cs[4]) ) 
            print ( "FM 4.2V : %3.5fV, %3.5fA" %(vs[0], cs[0]) ) 
            print ( "FM 3.0V : %3.5fV, %3.5fA" %(vs[1], cs[1]) ) 
            print ( "FM 1.5V : %3.5fV, %3.5fA" %(vs[3], cs[3]) ) 
            print ( "AM 2.5V : %3.5fV, %3.5fA" %(vs[2], cs[2]) ) 

            #logs.append ( "Supply IN   = %3.5f \n" %spl_in ) 
            logs.append ( "FEMB%d " %fembno   ) 
            logs.append ( "Temperature = %3.5f " %temp   ) 
            logs.append ( "BIAS 5V : %3.5fV, %3.5fA" %(vs[4], cs[4]) ) 
            logs.append ( "FM 4.2V : %3.5fV, %3.5fA" %(vs[0], cs[0]) ) 
            logs.append ( "FM 3.0V : %3.5fV, %3.5fA" %(vs[1], cs[1]) ) 
            logs.append ( "FM 1.5V : %3.5fV, %3.5fA" %(vs[3], cs[3]) ) 
            logs.append ( "AM 2.5V : %3.5fV, %3.5fA" %(vs[2], cs[2]) ) 
        logs.append ( "##########################\n")  

    else:
        print "WIB (%s)  doesn't exist or wrong firmware version!)"%(wib.UDP_IP)

logfile =    "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA2/" + "/WIB_lins_chk.log"
with open(logfile, "a+") as f:
    f.write( "Begin\n" ) 
    f.write( "WIB LINKs check\n" ) 
    runtime =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    f.write( runtime + "\n" )
    for onelog in logs:
        f.write( "%s\n"%onelog ) 
    f.write ("There are %d times WIB UDP Registers Write Error"%wib.wib_wrerr_cnt )
    f.write ("There are %d times FEMB UDP Registers Write Error"%wib.femb_wrerr_cnt )
    f.write ("There are %d times UDP timeouts"%wib.udp_timeout_cnt )
    f.write ("There are %d times UDP High Speed links timeouts"%wib.udp_hstimeout_cnt )
    f.write( "End\n") 
    f.write( "\n") 

