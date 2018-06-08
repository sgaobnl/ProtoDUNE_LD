# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Fri Jun  8 14:43:24 2018
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl
import numpy as np
import struct

def raw_convertor_feedloc(raw_data, smps, jumbo_flag = False):
    dataNtuple =struct.unpack_from(">%dH"%(smps*16),raw_data)
    chn_data=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],]
    feed_loc=[]

    if (jumbo_flag == True):
        pkg_len = 0x1E06/2
    else:
        pkg_len = 0x406/2
    pkg_index  = []
    datalength = long( (len(dataNtuple) // pkg_len) -3) * (pkg_len) 

    i = 0 
    k = []
    j = 0
    while (i <= datalength ):
        data_a =  ((dataNtuple[i+0]<<16)&0x00FFFFFFFF) + (dataNtuple[i+1]& 0x00FFFFFFFF) + 0x0000000001
        data_b =  ((dataNtuple[i+0+pkg_len]<<16)&0x00FFFFFFFF) + (dataNtuple[i+1+pkg_len]& 0x00FFFFFFFF)
        acc_flg = ( data_a  == data_b )
        face_flg = ((dataNtuple[i+2+6] == 0xface) or (dataNtuple[i+2+6] == 0xfeed))

        if (face_flg == True ) and ( acc_flg == True ) :
            pkg_index.append(i)
            i = i + pkg_len
        else:
            i = i + 1 
            k.append(i)

        if ( acc_flg == False ) :
            j = j + 1
    
    if ( len(k) != 0 ):
        print "raw_convertor_m.py: There are defective packages start at %d"%k[0] 
    if j != 0 :
        print "raw_convertor_m.py: drop %d packages"%(j)

    tmpa = pkg_index[0]
    tmpb = pkg_index[-1]
    data_a = ((dataNtuple[tmpa+0]<<16)&0x00FFFFFFFF) + (dataNtuple[tmpa+1]&0x00FFFFFFFF) 
    data_b = ((dataNtuple[tmpb+0]<<16)&0x00FFFFFFFF) + (dataNtuple[tmpb+1]&0x00FFFFFFFF) 
    if ( data_b > data_a ):
        pkg_sum = data_b - data_a + 1
    else:
        pkg_sum = (0x100000000 + data_b) - data_a + 1
    missed_pkgs = 0
    for i in range(len(pkg_index)-1):
        tmpa = pkg_index[i]
        tmpb = pkg_index[i+1]
        data_a = ((dataNtuple[tmpa+0]<<16)&0x00FFFFFFFF) + (dataNtuple[tmpa+1]&0x00FFFFFFFF)
        data_b = ((dataNtuple[tmpb+0]<<16)&0x00FFFFFFFF) + (dataNtuple[tmpb+1]&0x00FFFFFFFF) 
        if ( data_b > data_a ):
            add1 = data_b - data_a 
        else:
            add1 = (0x100000000 + data_b) - data_a 
        missed_pkgs = missed_pkgs + add1 -1

    if (missed_pkgs > 0 ):
        print "raw_convertor_m.py: missing udp pkgs = %d, total pkgs = %d "%(missed_pkgs, pkg_sum)
        print "raw_convertor_m.py: missing %.8f%% udp packages"%(100.0*missed_pkgs/pkg_sum)
    else:
        pass

    smps_num = 0
    for onepkg_index in pkg_index:
        onepkgdata = dataNtuple[onepkg_index : onepkg_index + pkg_len]
        i = 8
        peak_len = 100
        while i < len(onepkgdata) :
            if (onepkgdata[i] == 0xface ) or (onepkgdata[i] == 0xfeed ):
                chn_data[7].append( ((onepkgdata[i+1] & 0X0FFF)<<0 ))
                chn_data[6].append( ((onepkgdata[i+2] & 0X00FF)<<4)+ ((onepkgdata[i+1] & 0XF000) >> 12))
                chn_data[5].append( ((onepkgdata[i+3] & 0X000F)<<8) +((onepkgdata[i+2] & 0XFF00) >> 8 ))
                chn_data[4].append( ((onepkgdata[i+3] & 0XFFF0)>>4 ))

                chn_data[3].append( (onepkgdata[i+3+1] & 0X0FFF)<<0 )
                chn_data[2].append( ((onepkgdata[i+3+2] & 0X00FF)<<4) + ((onepkgdata[i+3+1] & 0XF000) >> 12))
                chn_data[1].append( ((onepkgdata[i+3+3] & 0X000F)<<8) + ((onepkgdata[i+3+2] & 0XFF00) >> 8 ))
                chn_data[0].append( ((onepkgdata[i+3+3] & 0XFFF0)>>4) )

                chn_data[15].append( ((onepkgdata[i+6+1] & 0X0FFF)<<0 ))
                chn_data[14].append( ((onepkgdata[i+6+2] & 0X00FF)<<4 )+ ((onepkgdata[i+6+1] & 0XF000) >> 12))
                chn_data[13].append( ((onepkgdata[i+6+3] & 0X000F)<<8 )+ ((onepkgdata[i+6+2] & 0XFF00) >> 8 ))
                chn_data[12].append( ((onepkgdata[i+6+3] & 0XFFF0)>>4 ))

                chn_data[11].append( ((onepkgdata[i+9+1] & 0X0FFF)<<0 ))
                chn_data[10].append( ((onepkgdata[i+9+2] & 0X00FF)<<4 )+ ((onepkgdata[i+9+1] & 0XF000) >> 12))
                chn_data[9].append(  ((onepkgdata[i+9+3] & 0X000F)<<8 )+ ((onepkgdata[i+9+2] & 0XFF00) >> 8 ))
                chn_data[8].append(  ((onepkgdata[i+9+3] & 0XFFF0)>>4 ))
                if (onepkgdata[i] == 0xfeed ):
                    feed_loc.append(smps_num)
                smps_num = smps_num + 1
            else:
                pass
            i = i + 13 

    return chn_data, feed_loc

def raw_convertor(raw_data, smps, jumbo_flag = False):
    chn_data, feed_loc = raw_convertor_feedloc(raw_data, smps, jumbo_flag)
    return chn_data

def raw_convertor_peak(raw_data, smps, jumbo_flag = False):
    chn_data, feed_loc = raw_convertor_feedloc(raw_data, smps, jumbo_flag)
    if ( len(feed_loc)  ) > 2 :
        chn_peakp=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],]
        chn_peakn=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],]
        for tmp in range(len(feed_loc)-1):
            for chn in range(16):
                chn_peakp[chn].append ( np.max(chn_data[chn][feed_loc[ tmp]:feed_loc[tmp]+100 ]) )
                chn_peakn[chn].append ( np.min(chn_data[chn][feed_loc[ tmp]:feed_loc[tmp]+100 ]) )
    else:
        chn_peakp = None
        chn_peakn = None
    return  chn_data, feed_loc, chn_peakp, chn_peakn


