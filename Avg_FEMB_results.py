# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Tue Jun 19 09:57:33 2018
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl
#from openpyxl import Workbook
import numpy as np
import struct
import os
from sys import exit
import os.path
import math
from matplotlib.backends.backend_pdf import PdfPages
from timeit import default_timer as timer

from raw_convertor_m import raw_convertor_peak

def Avg_FEMB_results(datapath, step, jumbo_flag = False, feed_freq = 500, avg_cycle = 300, apa_n="LArIAT", femb_n = 0):
    start = timer()
    alldata = []
        
    for root1, dirs1, rawfiles in os.walk(datapath):
        break

    from apa_mapping import APA_MAP
    apa = APA_MAP()
    apa.APA = apa_n
    apa.femb = femb_n
    apa_femb_loc, X_sort, V_sort, U_sort = apa.apa_femb_mapping()
    for rawfile in rawfiles:
        rawfilep = datapath + rawfile
        if (rawfilep.find(".bin") >= 0 ):
            if os.path.isfile(rawfilep):
                with open(rawfilep, 'rb') as f:
                    raw_data = f.read()                
                    len_file = len(raw_data) 
    
                wib  = int( rawfilep[rawfilep.find("WIB") + 3])
                femb = int( rawfilep[rawfilep.find("FEMB") + 4])
                chip = int( rawfilep[rawfilep.find("CHIP") + 4])

                smps = (len_file-1024)/2/16 
                if (smps > (avg_cycle+10)*500 ):
                    smps = (avg_cycle+10)*500  
                else:
                    pass

                chn_data, feed_loc, chn_peakp, chn_peakn = raw_convertor_peak(raw_data, smps, jumbo_flag)

                print "%s, Next chip..., Wait a while"%rawfilep

                for chn in range(16):
                    fembchn = chip*16+chn
                    for apa_info in apa_femb_loc:
                        if int(apa_info[1]) == fembchn :
                            break

                    rms_data = []
                    avg_data = []
                    avg_cnt = 0
                    if (len(feed_loc) < avg_cycle ):
                        avg_cycle = len(feed_loc) 

                    if (len(feed_loc) > 0 ):
                        for oneloc in feed_loc[0:avg_cycle]:
                            rms_data = rms_data + chn_data[chn][oneloc+100: oneloc+feed_freq]
                            if (avg_cnt == 0 ):
                                avg_cnt = avg_cnt + 1
                                chntmp = []
                                for tmpi in chn_data[chn][oneloc: oneloc+feed_freq] :
                                    chntmp.append( long(0xFFFFFFFF & tmpi) )
                                avg_data = np.array ( chntmp )
                            elif (avg_cnt < avg_cycle):
                                avg_data =avg_data +  np.array (chn_data[chn][oneloc: oneloc+feed_freq] )
                    else:
                        rms_data = chn_data[chn][0:100000]
                        avg_data = np.array ( chn_data[chn][0: feed_freq] )
 
                    avg_data = avg_data / avg_cycle


                    raw_mean = np.mean(rms_data)
                    avg_data_noped = (avg_data-raw_mean) 

                    raw_rms  = np.std (rms_data)
                    sf_raw_rms = []
                    for tmp in rms_data:
                        if ( tmp % 64 == 63 ) or ( tmp % 64 == 0 ) or ( tmp % 64 == 1 ) or ( tmp % 64 == 62 )  or ( tmp % 64 == 2 ):
                            pass
                        else:
                            sf_raw_rms.append(tmp)
                    if (len(sf_raw_rms) > 2 ):
                        sf_mean = np.mean(sf_raw_rms)
                        sf_rms  = np.std(sf_raw_rms)
                        sf_ratio = (len(sf_raw_rms))*1.0/(len(rms_data) )

                    chn_peakp_avg = np.mean(chn_peakp[chn])
                    chn_peakn_avg = np.mean(chn_peakn[chn])
                    alldata.append( [step, apa_info, wib, femb, chip, \
                                     chn, raw_mean, raw_rms, sf_mean, sf_rms, \
                                     sf_ratio, chn_peakp_avg, chn_peakn_avg, rms_data, chn_data[chn], \
                                     feed_loc, chn_peakp[chn], chn_peakn[chn], avg_data, avg_data_noped] )

                    pulsemax_data = np.max(chn_data[chn][feed_loc[0]:feed_loc[0]+100])
                    pulsemax_data_loc =np.where ( chn_data[chn][feed_loc[0]:feed_loc[0]+100] == pulsemax_data)
                    ppeak_oft_feed = pulsemax_data_loc[0][0] 

                    pulsemin_data = np.min(chn_data[chn][feed_loc[0]:feed_loc[0]+100])
                    pulsemin_data_loc =np.where ( chn_data[chn][feed_loc[0]:feed_loc[0]+100] == pulsemin_data)
                    npeak_oft_feed = pulsemin_data_loc[0][0]

            else:
                print "%s, file doesn't exist!!!"%rawfilep
                exit()
    print "time passed = %d"% (timer()-start)

    return alldata


