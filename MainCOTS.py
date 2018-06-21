# -*- coding: utf-8 -*-
"""
File Name: Main.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 1/13/2018 3:05:03 PM
Last modified: Thu Jun 21 13:46:19 2018
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
from timeit import default_timer as timer

###############################################################################
from ce_runs import CE_RUNS
ceruns = CE_RUNS()

start = timer()
ceruns.APA = sys.argv[1]
ceruns.femb_meas.APA = ceruns.APA 
ceruns.env = ""
test_runs = int(sys.argv[2],16)
#RTD_flg = (sys.argv[3] == "True")
RTD_flg = False
jumbo_flag = (sys.argv[3] == "True")
phase_set = int(sys.argv[4])

if (ceruns.APA == "APA40"):
    print ceruns.APA
    ceruns.wib_version_id = 0x101
    ceruns.femb_ver_id = 0x405
    ceruns.path = "D:/APA40/Rawdata/" 
    ceruns.wib_ips = [  "192.168.121.1"  ]
    ceruns.wib_pwr_femb = [[1,1,1,1],]
    ceruns.femb_mask    = [[0,0,0,0]]
    ceruns.bbwib_ips = [ "192.168.121.1"] 
    ceruns.tmp_wib_ips = ["192.168.121.1"] 
    ceruns.avg_wib_ips = ["192.168.121.1"] 
    ceruns.avg_wib_pwr_femb = [[1,1,1,0]]
    ceruns.avg_femb_on_wib = [0] 
    ceruns.jumbo_flag = True
    ceruns.COTSADC = True
    ceruns.femb_meas.femb_config.phase_set = phase_set
elif (ceruns.APA == "LArIAT"):
    print ceruns.APA
    ceruns.wib_version_id = 0x104
    ceruns.femb_ver_id = 0x405
    #ceruns.path = "D:/APA40/Rawdata/" 
    #ceruns.path = "D:/APA40/Rawdata/" 
    #ceruns.path = "/Users/shanshangao/LArIAT/Rawdata/" 
    ceruns.path = "/daqdata/BNL_LD_data/LArIAT/Rawdata/" 
    ceruns.wib_ips = [  "131.225.150.203",  "131.225.150.206" ]
    ceruns.wib_pwr_femb = [[1,1,1,1], [1,0,0,0]]
    ceruns.femb_mask    = [[0,0,0,0], [0,0,0,0]]
#    ceruns.bbwib_ips = [ "192.168.121.1"] 
#   ceruns.tmp_wib_ips = ["192.168.121.1"] 
#   ceruns.avg_wib_ips = ["192.168.121.1"] 
#   ceruns.avg_wib_pwr_femb = [[1,1,1,1]]
#   ceruns.avg_femb_on_wib = [0] 
    ceruns.jumbo_flag = jumbo_flag
    ceruns.COTSADC = True
    ceruns.femb_meas.femb_config.phase_set = phase_set
elif (ceruns.APA == "ProtoDUNE"): 
    print ceruns.APA
    ceruns.path = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA3/" 
    ceruns.wib_ips = ["10.73.137.20", "10.73.137.21", "10.73.137.22", "10.73.137.23", "10.73.137.24"]  
    ceruns.wib_pwr_femb = [[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1]]
    ceruns.femb_mask    = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    ceruns.bbwib_ips =  ["10.73.137.20", "10.73.137.21", "10.73.137.22", "10.73.137.23", "10.73.137.24"] 
    ceruns.tmp_wib_ips = ["10.73.137.24"] 
    ceruns.jumbo_flag = False
    ceruns.avg_wib_ips = ["10.73.137.20"] 
    ceruns.avg_wib_pwr_femb = [[1,0,0,0]]
    ceruns.avg_femb_on_wib = [0]
elif (ceruns.APA == "CHKOUT"): 
    print ceruns.APA
    ceruns.path = "D:/PD_CHKOUT/Rawdata/" 
    ceruns.wib_ips = [ "192.168.121.1" ]
    ceruns.avg_wib_ips = ["192.168.121.1"] 
    ceruns.avg_wib_pwr_femb = [[1,0,0,0]]
    ceruns.avg_femb_on_wib = [0] 
    ceruns.jumbo_flag = True

ceruns.jumbo_flag_set( )
if (os.path.exists(ceruns.path)):
    pass
else:
    try: 
        os.makedirs(ceruns.path)
    except OSError:
        print "Can't create a folder, exit"
        sys.exit()

logfile = ceruns.path +  ceruns.APA + "readme.log"

print "WIEC self check"
print "time cost = %.3f seconds"%(timer()-start)
ceruns.WIB_self_chk()

if (test_runs == 0x0 ):
    print "Power FEMBs ON"
    print "time cost = %.3f seconds"%(timer()-start)

    ceruns.FEMBs_PWR_SW(SW = "ON")
    with open(logfile, "a+") as f:
        f.write( "Begin\n") 
        f.write( "Turn PS on\n" ) 
        f.write (ceruns.runpath + "\n" )
        f.write (ceruns.runtime + "\n" )
        f.write ("Alive FEMBs: " + str(ceruns.alive_fembs) + "\n" )

        wib_wrerr_cnt = ceruns.femb_meas.femb_config.femb.wib_wrerr_cnt
        wib_wr_cnt = ceruns.femb_meas.femb_config.femb.wib_wr_cnt
        femb_wrerr_cnt = ceruns.femb_meas.femb_config.femb.femb_wrerr_cnt
        femb_wr_cnt = ceruns.femb_meas.femb_config.femb.femb_wr_cnt
        udp_timeout_cnt = ceruns.femb_meas.femb_config.femb.udp_timeout_cnt
        udp_hstimeout_cnt = ceruns.femb_meas.femb_config.femb.udp_hstimeout_cnt
        f.write ("There are %d times WIB UDP Registers Write\n"%wib_wr_cnt )
        f.write ("There are %d times WIB UDP Registers Write Error\n"%wib_wrerr_cnt )
        f.write ("There are %d times FEMB UDP Registers Write\n"%femb_wr_cnt )
        f.write ("There are %d times FEMB UDP Registers Write Error\n"%femb_wrerr_cnt )
        f.write ("There are %d times UDP timeouts\n"%udp_timeout_cnt )
        f.write ("There are %d times UDP High Speed links timeouts\n"%udp_hstimeout_cnt )
        udp_err_np = ceruns.udp_err_np
        for oneerr in udp_err_np:
            if (oneerr[4] - oneerr[3] != 0) : 
                f.write ("RUNcode(%s)WIB%d(%s)FEMB%d: UDP Reg Write Error count = (%d-%d) = %d\n" \
                        %(oneerr[5], oneerr[1], oneerr[0], oneerr[2], oneerr[4], oneerr[3], oneerr[3] - oneerr[4] ))
        femb_wrerr_log = ceruns.femb_meas.femb_config.femb.femb_wrerr_log
        if len(femb_wrerr_log) != 0 :
            f.write ("Write ERROR happens at FEMB%d, Addr=%x, Value=%x"%(femb_wrerr_log[0], femb_wrerr_log[1],femb_wrerr_log[2]) )
            for logn in range(len(femb_wrerr_log)-1):
                log0 = femb_wrerr_log[logn]
                log1 = femb_wrerr_log[logn+1]
                if log0 != log1 :
                    f.write ("Write ERROR happens at FEMB%d, Addr=%x, Value=%x"%(log1[0], log1[1],log1[2]) )
        f.write( "End\n") 
        f.write( "\n") 

print "FEMBs self-check"
mask_femb = ceruns.FEMBs_Self_CHK()
print ceruns.COTSADC
with open(logfile, "a+") as f:
    f.write( "Begin\n") 
    f.write( "Broken FEMBs are masked\n" ) 
    f.write (ceruns.runpath + "\n" )
    f.write (ceruns.runtime + "\n" )
    f.write ("Alive FEMBs: " + str(ceruns.alive_fembs) + "\n" )
    f.write ("ADC Phase: " + str(ceruns.femb_meas.femb_config.phase_set) + "\n" )
    for onemaskfemb in mask_femb:
        f.write (onemaskfemb + "\n" )
    f.write( "End\n") 
    f.write( "\n") 

if (test_runs&0x7F != 0x0 ):
    #if (RTD_flg == True):
    #if (test_runs&0x7F != 0x40):
    if (False):
        print "Please write a sentence to describe the test purpose: "
        test_note = raw_input("Please input: ")
        #print "Please input temperatures measured by RTDs (leave blank if RTD disconnected) "
        #rtd_temp = raw_input("TT0206 to TT0200: ")
    else:
        test_note = "Continuate test..."
    rtd_temp = " "
    rundate =  datetime.now().strftime('%m_%d_%Y')
    runtime =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(logfile, "a+") as f:
        f.write( "Begin\n") 
        f.write(runtime + "\n") 
        f.write(ceruns.APA + "\n") 
        f.write(ceruns.env + "\n") 
        f.write("Test Code = 0X" + format(test_runs,"02X")+ "\n")  
        f.write(test_note + "\n") 
        f.write("RTDs(TT0206 to TT0200): %s"%rtd_temp + "\n")  
        f.write ("Alive FEMBs: " + str(ceruns.alive_fembs) + "\n" )

    print "FEMB ADC offset calibration"
    print "time cost = %.3f seconds"%(timer()-start)

    if (test_runs&0x7F == 0x40):
#    if (True):
        oft_file = "./APA_ADC_OFT_06202018_121405.bin"
        with open (oft_file, 'rb') as fp:
            apa_oft_info = pickle.load(fp)
    else:
        apa_oft_info = ceruns.oft_run( ) 

    with open(logfile, "a+") as f:
        f.write( "FEMB ADC offset calibration\n" ) 
        f.write (ceruns.runpath + "\n" )
        f.write (ceruns.runtime + "\n" )
        f.write ("Alive FEMBs: " + str(ceruns.alive_fembs) + "\n" )

if (test_runs&0x20 != 0x0 ):
    print "LArIAT Configuration"
    sgs = [int(sys.argv[5])]
    tps = [int(sys.argv[6])]
    pls_source = (int(sys.argv[7]))&0x3
    dac_source = int(sys.argv[8],16)
    fpgadac_en = (dac_source  & 0x80)>>7
    asicdac_en = (dac_source  & 0x40)>>6
    vdac = dac_source  & 0x3F
    ceruns.slk0 = (int(sys.argv[9]))&0x01
    ceruns.slk1 = (int(sys.argv[9]))&0x02
    mbb = (int(sys.argv[10],16))&0x1FF
    dac_sel = 1 #1 DAC on FEMB, 0 DAC on WIB(don't use)
    datamode = 0
 
    ceruns.larcfg_run(apa_oft_info, sgs = sgs, tps =tps, pls_cs=pls_source, dac_sel=dac_sel, fpgadac_en=fpgadac_en, asicdac_en=asicdac_en, vdac = vdac, val = 1000, mbb=mbb, datamode=datamode) 

    with open(logfile, "a+") as f:
        f.write( "%2X: Configuration \n" %(test_runs&0x20) ) 
        f.write (ceruns.runpath + "\n" )
        f.write (ceruns.runtime + "\n" )
        f.write ("Alive FEMBs: " + str(ceruns.alive_fembs) + "\n" )
    print "time cost = %.3f seconds"%(timer()-start)

if (test_runs&0x10 != 0x0 ):
    print "Quick Checkout Test"
    print "time cost = %.3f seconds"%(timer()-start)
    ceruns.qc_run(apa_oft_info, sgs=[1,3], tps =[0,1,2,3], val = 100) 
    with open(logfile, "a+") as f:
        f.write( "%2X: Quick Checkout Test\n" %(test_runs&0x10) ) 
        f.write (ceruns.runpath + "\n" )
        f.write (ceruns.runtime + "\n" )
        f.write ("Alive FEMBs: " + str(ceruns.alive_fembs) + "\n" )

if (test_runs&0x01 != 0x0 ):
    print "Noise Measurement Test"
    print "time cost = %.3f seconds"%(timer()-start)
    ceruns.rms_run(apa_oft_info, sgs = [1,3], tps =[0,1,2,3], val=1600) 
    with open(logfile, "a+") as f:
        f.write( "%2X: Noise Measurement Test\n" %(test_runs&0x01) ) 
        f.write (ceruns.runpath + "\n" )
        f.write (ceruns.runtime + "\n" )
        f.write ("Alive FEMBs: " + str(ceruns.alive_fembs) + "\n" )

if (test_runs&0x02 != 0x0 ):
    print "FPGA DAC Calibration Test"
    print "time cost = %.3f seconds"%(timer()-start)
    ceruns.fpgadac_run(apa_oft_info, sgs = [1,3], tps =[0,1,2,3], val=100)
    with open(logfile, "a+") as f:
        f.write( "%2X: FPGA DAC Calibration Test\n" %(test_runs&0x02) ) 
        f.write (ceruns.runpath + "\n" )
        f.write (ceruns.runtime + "\n" )
        f.write ("Alive FEMBs: " + str(ceruns.alive_fembs) + "\n" )

if (test_runs&0x04 != 0x0 ):
    print "ASIC DAC Calibration Test"
    print "time cost = %.3f seconds"%(timer()-start)
    ceruns.asicdac_run(apa_oft_info, sgs = [1], tps =[0,1,2,3], val=100)
    with open(logfile, "a+") as f:
        f.write( "%2X: ASIC DAC Calibration Test\n" %(test_runs&0x04) ) 
        f.write (ceruns.runpath + "\n" )
        f.write (ceruns.runtime + "\n" )
        f.write ("Alive FEMBs: " + str(ceruns.alive_fembs) + "\n" )

if (test_runs&0x08 != 0x0 ):
    print "LArIAT Configuration"
    sgs = [int(sys.argv[5])]
    tps = [int(sys.argv[6])]
    pls_source = (int(sys.argv[7]))&0x3
    dac_source = int(sys.argv[8],16)
    fpgadac_en = (dac_source  & 0x80)>>7
    asicdac_en = (dac_source  & 0x40)>>6
    vdac = dac_source  & 0x3F
    ceruns.slk0 = (int(sys.argv[9]))&0x01
    ceruns.slk1 = (int(sys.argv[9]))&0x02
    mbb = (int(sys.argv[10],16))&0x1FF
    dac_sel = 1 #1 DAC on FEMB, 0 DAC on WIB(don't use)

    datamode = 3
    ceruns.larcfg_run(apa_oft_info, sgs = sgs, tps =tps, pls_cs=pls_source, dac_sel=dac_sel, fpgadac_en=fpgadac_en, asicdac_en=asicdac_en, vdac = vdac, val = 1000, mbb=mbb, datamode=datamode) 

    with open(logfile, "a+") as f:
        f.write( "%2X: Configuration \n" %(test_runs&0x08) ) 
        f.write (ceruns.runpath + "\n" )
        f.write (ceruns.runtime + "\n" )
        f.write ("Alive FEMBs: " + str(ceruns.alive_fembs) + "\n" )
    print "time cost = %.3f seconds"%(timer()-start)

if (test_runs&0x40 != 0x0 ):
    run_cnt = int(sys.argv[5])
    for i in range(run_cnt):
        if i > 0:
            t_sleep = int(sys.argv[6])
            t_min = t_sleep/60
            runtime =  datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
            print "sleep %d minutes starting from %s"%(t_min,runtime)
            print "Ctrl-C to if you want to stop the script before it finishes"
            time.sleep(t_sleep)
        print "LArIAT DATA collectting during DAQ running"
        ceruns.larcfg_getdata(val=1000) 
        with open(logfile, "a+") as f:
            f.write( "%2X: Configuration \n" %(test_runs&0x40) ) 
            f.write (ceruns.runpath + "\n" )
            f.write (ceruns.runtime + "\n" )
            f.write ("Alive FEMBs: " + str(ceruns.alive_fembs) + "\n" )
        print "time cost = %.3f seconds"%(timer()-start)
        

if (test_runs&0x80 != 0x0 ):
    print "Turn FEMBs OFF"
    print "time cost = %.3f seconds"%(timer()-start)
    ceruns.FEMBs_PWR_SW(SW = "OFF")
    with open(logfile, "a+") as f:
        f.write( "Begin\n") 
        f.write( "Turn PS OFF\n" ) 
        f.write (ceruns.runpath + "\n" )
        f.write (ceruns.runtime + "\n" )
        f.write ("Alive FEMBs: " + str(ceruns.alive_fembs) + "\n" )
        f.write( "End\n") 
        f.write( "\n") 

if (test_runs&0x7F != 0x0 ):
    with open(logfile, "a+") as f:
        wib_wrerr_cnt = ceruns.femb_meas.femb_config.femb.wib_wrerr_cnt
        wib_wr_cnt = ceruns.femb_meas.femb_config.femb.wib_wr_cnt
        femb_wrerr_cnt = ceruns.femb_meas.femb_config.femb.femb_wrerr_cnt
        femb_wr_cnt = ceruns.femb_meas.femb_config.femb.femb_wr_cnt
        udp_timeout_cnt = ceruns.femb_meas.femb_config.femb.udp_timeout_cnt
        udp_hstimeout_cnt = ceruns.femb_meas.femb_config.femb.udp_hstimeout_cnt
        f.write ("There are %d times WIB UDP Registers Write\n"%wib_wr_cnt )
        f.write ("There are %d times WIB UDP Registers Write Error\n"%wib_wrerr_cnt )
        f.write ("There are %d times FEMB UDP Registers Write\n"%femb_wr_cnt )
        f.write ("There are %d times FEMB UDP Registers Write Error\n"%femb_wrerr_cnt )
        f.write ("There are %d times UDP timeouts\n"%udp_timeout_cnt )
        f.write ("There are %d times UDP High Speed links timeouts\n"%udp_hstimeout_cnt )
        udp_err_np = ceruns.udp_err_np
        for oneerr in udp_err_np:
            if (oneerr[4] - oneerr[3] != 0) : 
                f.write ("RUNcode(%s)WIB%d(%s)FEMB%d: UDP Reg Write Error count = (%d-%d) = %d\n" \
                        %(oneerr[5], oneerr[1], oneerr[0], oneerr[2], oneerr[4], oneerr[3], oneerr[3] - oneerr[4] ))

        femb_wrerr_log = ceruns.femb_meas.femb_config.femb.femb_wrerr_log
        if len(femb_wrerr_log) != 0 :
            f.write ("Write ERROR happens at FEMB%d, Addr=%x, Value=%x\n"%(femb_wrerr_log[0][0], femb_wrerr_log[0][1],femb_wrerr_log[0][2]) )
            for logn in range(len(femb_wrerr_log)-1):
                log0 = femb_wrerr_log[logn]
                log1 = femb_wrerr_log[logn+1]
                if log0 != log1 :
                    f.write ("Write ERROR happens at FEMB%d, Addr=%x, Value=%x\n"%(log1[0], log1[1],log1[2]) )
        f.write( "End\n") 
        f.write( "\n") 

print "Well Done"

#if (test_runs&0x08 != 0x0 ):
#    print "Brombreg Mode Noise Measurement Test"
#    print "time cost = %.3f seconds"%(timer()-start)
#    #ceruns.brombreg_run(apa_oft_info, sgs = [1,3], tps =[0,1,2,3], cycle=5) 
#    ceruns.brombreg_run(apa_oft_info, sgs = [3], tps =[0,1,2,3], cycle=150) 
#    with open(logfile, "a+") as f:
#        f.write( "%2X: Brombreg Mode Noise Measurement Test\n" %(test_runs&0x08) ) 
#        f.write (ceruns.runpath + "\n" )
#        f.write (ceruns.runtime + "\n" )
#        f.write ("Alive FEMBs: " + str(ceruns.alive_fembs) + "\n" )

#if (test_runs&0x20 != 0x0 ):
#    print "Temperature Monitoring"
#    print "time cost = %.3f seconds"%(timer()-start)
#    ceruns.monitor_run(temp_or_pluse = "temp")
#    with open(logfile, "a+") as f:
#        f.write( "%2X: Temperature Monitoring\n" %(test_runs&0x20) ) 
#        f.write (ceruns.runpath + "\n" )
#        f.write (ceruns.runtime + "\n" )
#        f.write ("Alive FEMBs: " + str(ceruns.alive_fembs) + "\n" )

#if (test_runs&0x40 != 0x0 ):
#    if (ceruns.APA == "CHKOUT"): 
#        print "Average Checkout"
#        print "time cost = %.3f seconds"%(timer()-start)
#        ceruns.avg_run(val = 1600)
#    with open(logfile, "a+") as f:
#        f.write( "%2X: Average Checkout\n" %(test_runs&0x40) ) 
#        f.write (ceruns.runpath + "\n" )
#        f.write (ceruns.runtime + "\n" )
#        f.write ("Alive FEMBs: " + str(ceruns.alive_fembs) + "\n" )


