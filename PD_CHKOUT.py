# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Sun Feb 25 20:01:01 2018
"""
import matplotlib
matplotlib.use('Agg')
#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl
#from openpyxl import Workbook
import numpy as np
#import struct
import os
from sys import exit
import os.path
import math
from matplotlib.backends.backend_pdf import PdfPages
from timeit import default_timer as timer

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches

from Avg_FEMB_results import Avg_FEMB_results

def plots(plt, plot_en, apa_results, pp, cycle ):
    cebox_prefix         = []
    apainfo         = []
    ped_np         = []
    rms_np         = []
    sf_ped_np      = []
    sf_rms_np      = []
    sf_ratio_np    = []
    chn_peakp_avg  = []
    chn_peakn_avg  = []
    chn_wave       = []
    chn_peakp_ped  = []
    chn_peakn_ped  = []
    chn_avg_data  = []
    chn_avg_noped  = []
    smp_lengths = []
    chnwib_np =[]
    chnfemb_np =[]
    chnasic_np =[]
    chnchn_np =[]
   
    for chndata in apa_results:
        cebox_prefix.append(chndata[0])
        apainfo.append(chndata[1])
        chnwib_np.append(chndata[2])
        chnfemb_np.append(chndata[3])
        chnasic_np.append(chndata[4])
        chnchn_np.append(chndata[5])
        ped_np.append(chndata[6])
        rms_np.append(chndata[7])
        sf_ped_np.append(chndata[8])
        sf_rms_np.append(chndata[9])
        sf_ratio_np.append(chndata[10])
        chn_peakp_ped.append(chndata[11])
        chn_peakn_ped.append(chndata[12])
        chn_peakp_avg.append(chndata[11] -  chndata[6])
        chn_peakn_avg.append(chndata[12] -  chndata[6])
        smp_lengths.append( len(chndata[13]) )
        chn_wave.append(chndata[14][ chndata[15][1] : chndata[15][1]+100])
        chn_avg_data.append(chndata[18])
        chn_avg_noped.append(chndata[19])

    chn_np = np.arange(len(ped_np))

    if ( (plot_en&0x01) != 0 ):
        fig = plt.figure(figsize=(16,9))
        ax = plt
        total_chn = len(chn_np)
        title = "Pulse Waveform Overlap of %d after averaging with %d cycles"%( total_chn, cycle)
        ylabel = "ADC output /bin"
        print "Pulse Waveform--> %d channels in total"%(total_chn)
        for chn in chn_np:
            y_np = np.array(chn_avg_noped[chn])
            y_max = np.max(y_np)
            y_pos = np.where(y_np == y_max)
            y_pos0 = y_pos[0][0]
            smps_np = np.arange(len(chn_avg_noped[chn])) 
            x_np = smps_np * 0.5
            ax.scatter( x_np, y_np)
            ax.plot( x_np, y_np)
        ax.tick_params(labelsize=8)
        ax.xlim([0,50])
        ax.ylim([-2000,2000])
        ax.ylabel(ylabel, fontsize=12 )
        ax.xlabel("Time / us", fontsize=12 )
        ax.title(title , fontsize=12 )
        ax.grid()
        ax.tight_layout( rect=[0, 0.05, 1, 0.95])
        ax.savefig(pp, format='pdf')
        ax.close()
    
    if ( (plot_en&0x02) != 0 ):
        fig = plt.figure(figsize=(16,9))
        ax = plt
    
        total_chn = len(chn_np)
        print total_chn
        title = "Pulse Waveform Overlap of %d after averaging with %d cycles"%( total_chn, cycle)
        ylabel = "ADC output /bin"
        print "Pulse Waveform-->%d channels in total"%(total_chn)
        for chn in chn_np:
            y_np = np.array(chn_avg_data[chn])
            y_max = np.max(y_np)
            y_pos = np.where(y_np == y_max)
            y_pos0 = y_pos[0][0]
            smps_np = np.arange(len(chn_avg_data[chn])) 
            x_np = smps_np * 0.5
            ax.scatter( x_np, y_np)
            ax.plot( x_np, y_np)
    
        ax.tick_params(labelsize=8)
        ax.xlim([0,50])
        ax.ylim([-100,4100])
        ax.ylabel(ylabel, fontsize=12 )
        ax.xlabel("Time / us", fontsize=12 )
        ax.title(title , fontsize=12 )
        ax.grid()
        ax.tight_layout( rect=[0, 0.05, 1, 0.95])
        ax.savefig(pp, format='pdf')
        ax.close()

    if ( (plot_en&0x04) != 0 ):
        fig = plt.figure(figsize=(16,9))
        ax = plt
        ped_np = np.array(ped_np)
        chn_peakp_ped = np.array( chn_peakp_ped )
        patch = []
        label = []
        title = "Pedestal Measurement "
        ylabel = "ADC output /bin"
        total_chn = len(chn_np)
        print "Pedestal Measurement-->%d channels in total"%(total_chn)
        for i in range(1):
            if ( i == 0 ):
                color = 'r'
                ped_label = "Pedestal / ADC bin"
                y_np = ped_np
            elif ( i == 1 ):
                color = 'b'
                ped_label = "Pulse Peak / ADC bin"
                y_np = chn_peakp_ped
        
            ax.scatter( chn_np, y_np, color = color)
            ax.plot( chn_np, y_np, color = color)
            patch.append( mpatches.Patch(color=color))
            label.append(ped_label)
            ax.legend(patch, label, loc=1, fontsize=12 )
        for chn in range(0,128,16):
            ax.plot((chn,chn), (0, 4100), color = 'm')
            ax.text(chn+6, 300, "ASIC%d"%(chn//16))
        ax.tick_params(labelsize=8)
        ax.xlim([0,total_chn])
        ax.ylim([0,4100])
        ax.ylabel(ylabel, fontsize=12 )
        ax.xlabel("Channel No.", fontsize=12 )
        ax.title(title , fontsize=12 )
        ax.grid()
        ax.tight_layout( rect=[0, 0.05, 1, 0.95])
        ax.savefig(pp, format='pdf')
        ax.close()

    if ( (plot_en&0x08) != 0 ):
        fig = plt.figure(figsize=(16,9))
        ax = plt
        rms_np = np.array(rms_np)
        sf_rms_np = np.array(sf_rms_np)
        patch = []
        label = []
        title = "Noise Measurement" 
        ylabel = "RMS noise / ADC bin"
        total_chn = len(chn_np)
        print "Noise Measurement-->%d channels in total"%(total_chn)
        for i in range(2):
            if ( i == 0 ):
                color = 'r'
                plabel = "RMS Noise / ADC bin"
                y_np = rms_np
                rmsmax = max(y_np)
            elif ( i == 1 ):
                color = 'b'
                plabel = "SF RMS Noise / ADC bin"
                y_np = sf_rms_np
                if max(y_np) > rmsmax :
                    rmsmax = max(y_np)
            ax.scatter( chn_np, y_np, color = color)
            ax.plot( chn_np, y_np, color = color)
            patch.append( mpatches.Patch(color=color))
            label.append(plabel)
            ax.legend(patch, label, loc=1, fontsize=12 )
        for chn in range(0,128,16):
            ax.plot((chn,chn), (0, rmsmax *1.5), color = 'm')
            ax.text(chn+6, rmsmax *1.3, "ASIC%d"%(chn//16))
        ax.tick_params(labelsize=8)
        ax.xlim([0,total_chn])
        ax.ylim([0,rmsmax*1.5])
        ax.ylabel(ylabel, fontsize=12 )
        ax.xlabel("APA Channel No.", fontsize=12 )
        ax.title(title , fontsize=12 )
        ax.grid()
        ax.tight_layout( rect=[0, 0.05, 1, 0.95])
        ax.savefig(pp, format='pdf')
        ax.close()

    if ( (plot_en&0x10) != 0 ):
        fig = plt.figure(figsize=(16,9))
        ax = plt
        chn_peakp_avg = np.array( chn_peakp_avg )
        chn_peakn_avg = np.array( chn_peakn_avg )
        patch = []
        label = []
        title = "Pulse Amplitude "
        ylabel = "ADC output /bin"
        total_chn = len(chn_np)
        print "Pulse Amplitude--> %d channels in total"%(total_chn)
        for i in range(2):
            if ( i == 0 ):
                color = 'r'
                ped_label = "Positive Pulse Amplitude / ADC bin"
                y_np = chn_peakp_avg 
            elif ( i == 1 ):
                color = 'b'
                ped_label = "Negative Pulse Amplitude / ADC bin"
                y_np = chn_peakn_avg 
        
            ax.scatter( chn_np, y_np, color = color)
            ax.plot( chn_np, y_np, color = color)
            patch.append( mpatches.Patch(color=color))
            label.append(ped_label)
            ax.legend(patch, label, loc=1, fontsize=12 )
        for chn in range(0,128,16):
            ax.plot((chn,chn), (-2000, 3000), color = 'm')
            ax.text(chn+6, -1800, "ASIC%d"%(chn//16))
        ax.tick_params(labelsize=8)
        ax.xlim([0,total_chn])
        ax.ylim([-2000,3000])
        ax.ylabel(ylabel, fontsize=12 )
        ax.xlabel("APA Channel No.", fontsize=12 )
        ax.title(title , fontsize=12 )
        ax.grid()
        ax.tight_layout( rect=[0, 0.05, 1, 0.95])
        ax.savefig(pp, format='pdf')
        ax.close()

    if ( (plot_en&0x20) != 0 ):
        fig = plt.figure(figsize=(16,9))
        ax = plt
        total_chn = len(chn_np)
        title = "Pulse Waveform Overlap of %d (without averaging) "%(total_chn)
        ylabel = "ADC output /bin"
        print "Pulse Waveform-->%d channels in total"%(total_chn)
        for chn in chn_np:
            y_np = np.array(chn_wave[chn])
            smps_np = np.arange(len(chn_wave[chn])) 
            x_np = smps_np * 0.5
            ax.scatter( x_np, y_np)
            ax.plot( x_np, y_np)
        ax.tick_params(labelsize=8)
        ax.xlim([0,50])
        ax.ylim([0,4100])
        ax.ylabel(ylabel, fontsize=12 )
        ax.xlabel("Time / us", fontsize=12 )
        ax.title(title , fontsize=12 )
        ax.grid()
        ax.tight_layout( rect=[0, 0.05, 1, 0.95])
        ax.savefig(pp, format='pdf')
        ax.close()


def PD_CHKOUT (datapath, step, plot_en=0x2F,  avg_cycle=300, jumbo_flag=True ):
    result_pdfpath = datapath + step + 'results.pdf'
    pp = PdfPages(result_pdfpath)
    feed_freq=500
    wibsdata = Avg_FEMB_results(datapath, step, jumbo_flag =jumbo_flag, feed_freq =feed_freq, avg_cycle= avg_cycle)
    fig = plt.figure(figsize=(16,9))
    plots(plt, plot_en, wibsdata, pp, avg_cycle)
    pp.close()

#datapath = "D:/testtemp/Rawdata/Rawdata_02_25_2018/run01avg/CEbox001WIB00step2A/"
#step = "CEbox001WIB00step2A_"
#PD_CHKOUT (datapath, step, plot_en=0x3F,  avg_cycle=10, jumbo_flag=True )

