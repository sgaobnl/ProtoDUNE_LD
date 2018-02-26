# -*- coding: utf-8 -*-
"""
File Name: set_path.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: Sun Feb 25 20:58:38 2018
Last modified: Sun Feb 25 21:05:47 2018
"""

###############################################################################

def set_path(os="mac"):
    if os == "linux" :
        rawpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/" 
    elif os == "mac" :
        rawpath = "~/ProtoDUNE/Rawdata/" 
    elif os == "windows" :
        rawpath = "D:/APA/Rawdata/" 
    else:
        rawpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/" 
    return rawpath
 

