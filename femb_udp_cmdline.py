##!/usr/bin/env python33

import struct
import sys 
import string
import socket
import time
import copy
from socket import AF_INET, SOCK_DGRAM

class FEMB_UDP:
    def write_reg(self, reg , data ):
        regVal = int(reg)
        if (regVal < 0) or (regVal > self.MAX_REG_NUM):
            #print "FEMB_UDP--> Error write_reg: Invalid register number"
            return None
        dataVal = int(data)
        if (dataVal < 0) or (dataVal > self.MAX_REG_VAL):
            #print "FEMB_UDP--> Error write_reg: Invalid data value"
            return None
        
        #crazy packet structure require for UDP interface
        dataValMSB = ((dataVal >> 16) & 0xFFFF)
        dataValLSB = dataVal & 0xFFFF
        WRITE_MESSAGE = struct.pack('HHHHHHHHH',socket.htons( self.KEY1  ), socket.htons( self.KEY2 ),socket.htons(regVal),socket.htons(dataValMSB),
                socket.htons(dataValLSB),socket.htons( self.FOOTER  ), 0x0, 0x0, 0x0  )
        
        #send packet to board, don't do any checks
        sock_write = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
        sock_write.setblocking(0)
        sock_write.sendto(WRITE_MESSAGE,(self.UDP_IP, self.UDP_PORT_WREG ))
        sock_write.close()
        #print "FEMB_UDP--> Write: reg=%x,value=%x"%(reg,data)

    def write_reg_wib(self, reg , data ):
        self.write_reg( reg,data )

    def write_reg_femb(self, femb_addr, reg , data ):
        regVal = int(reg)
        if (regVal < 0) or (regVal > self.MAX_REG_NUM):
            #print "FEMB_UDP--> Error write_reg: Invalid register number"
            return None
        dataVal = int(data)
        if (dataVal < 0) or (dataVal > self.MAX_REG_VAL):
            #print "FEMB_UDP--> Error write_reg: Invalid data value"
            return None
        #crazy packet structure require for UDP interface
        dataValMSB = ((dataVal >> 16) & 0xFFFF)
        dataValLSB = dataVal & 0xFFFF
        WRITE_MESSAGE = struct.pack('HHHHHHHHH',socket.htons( self.KEY1  ), socket.htons( self.KEY2 ),socket.htons(regVal),socket.htons(dataValMSB),
                socket.htons(dataValLSB),socket.htons( self.FOOTER  ), 0x0, 0x0, 0x0  )
        
        #send packet to board, don't do any checks
        sock_write = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
        sock_write.setblocking(0)
        if (femb_addr == 0 ):
            sock_write.sendto(WRITE_MESSAGE,(self.UDP_IP, self.UDPFEMB0_PORT_WREG  ))
        elif (femb_addr == 1 ):
            sock_write.sendto(WRITE_MESSAGE,(self.UDP_IP, self.UDPFEMB1_PORT_WREG  ))
        elif (femb_addr == 2 ):
            sock_write.sendto(WRITE_MESSAGE,(self.UDP_IP, self.UDPFEMB2_PORT_WREG  ))
        elif (femb_addr == 3 ):
            sock_write.sendto(WRITE_MESSAGE,(self.UDP_IP, self.UDPFEMB3_PORT_WREG  ))

        sock_write.close()

    def read_reg(self, reg ):
        regVal = int(reg)
        if (regVal < 0) or (regVal > self.MAX_REG_NUM):
                #print "FEMB_UDP--> Error read_reg: Invalid register number"
                return None

        #set up listening socket, do before sending read request
        sock_readresp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
        sock_readresp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_readresp.bind(('', self.UDP_PORT_RREGRESP ))
        sock_readresp.settimeout(2)

        #crazy packet structure require for UDP interface
        READ_MESSAGE = struct.pack('HHHHHHHHH',socket.htons(self.KEY1), socket.htons(self.KEY2),socket.htons(regVal),0,0,socket.htons(self.FOOTER),0,0,0)
        sock_read = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
        sock_read.setblocking(0)
        sock_read.sendto(READ_MESSAGE,(self.UDP_IP,self.UDP_PORT_RREG))
        sock_read.close()

        #try to receive response packet from board, store in hex
        data = []
        try:
                data = sock_readresp.recv(4*1024)
        except socket.timeout:
                self.udp_timeout_cnt = self.udp_timeout_cnt  + 1
                #print "FEMB_UDP--> Error read_reg: No read packet received from board, quitting"
                sock_readresp.close()
                return -1        
        dataHex = data.encode('hex')
        sock_readresp.close()

        #extract register value from response
        if int(dataHex[0:4],16) != regVal :
                #print "FEMB_UDP--> Error read_reg: Invalid response packet"
                return None
        dataHexVal = long(dataHex[4:12],16)
        #print "FEMB_UDP--> Write: reg=%x,value=%x"%(reg,dataHexVal)
        return dataHexVal

    def write_reg_femb_checked (self, femb_addr, reg , data ):
        i = 0
        while (i < 10 ):
            time.sleep(0.001)
            self.write_reg_femb(femb_addr, reg , data )
            self.femb_wr_cnt = self.femb_wr_cnt + 1
            time.sleep(0.001)
            rdata = self.read_reg_femb(femb_addr,  reg)
            time.sleep(0.001)
            rdata = self.read_reg_femb(femb_addr,  reg)
            time.sleep(0.001)
            if (data == rdata ):
                break
            else:
                i = i + 1
                self.femb_wrerr_cnt = self.femb_wrerr_cnt + 1
                self.femb_wrerr_log.append([femb_addr,reg, data])
                time.sleep(abs(i -1 + 0.001))
        if i >= 10 :
            print "readback value is different from written data, %d, %x, %x"%(reg, data, rdata)
            sys.exit()

    def read_reg_femb(self, femb_addr, reg ):
        regVal = int(reg)
        if (regVal < 0) or (regVal > self.MAX_REG_NUM):
                #print "FEMB_UDP--> Error read_reg: Invalid register number"
                return None

        #set up listening socket, do before sending read request
        sock_readresp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
        sock_readresp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if (femb_addr == 0 ):
            sock_readresp.bind(('', self.UDPFEMB0_PORT_RREGRESP ))
        elif (femb_addr == 1 ):
            sock_readresp.bind(('', self.UDPFEMB1_PORT_RREGRESP ))
        elif (femb_addr == 2 ):
            sock_readresp.bind(('', self.UDPFEMB2_PORT_RREGRESP ))
        elif (femb_addr == 3 ):
            sock_readresp.bind(('', self.UDPFEMB3_PORT_RREGRESP ))
        sock_readresp.settimeout(2)

        #crazy packet structure require for UDP interface
        READ_MESSAGE = struct.pack('HHHHHHHHH',socket.htons(self.KEY1), socket.htons(self.KEY2),socket.htons(regVal),0,0,socket.htons(self.FOOTER),0,0,0)
        sock_read = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
        sock_read.setblocking(0)
        if (femb_addr == 0 ):
            sock_read.sendto(READ_MESSAGE,(self.UDP_IP,self.UDPFEMB0_PORT_RREG))
        elif (femb_addr == 1 ):
            sock_read.sendto(READ_MESSAGE,(self.UDP_IP,self.UDPFEMB1_PORT_RREG))
        elif (femb_addr == 2 ):
            sock_read.sendto(READ_MESSAGE,(self.UDP_IP,self.UDPFEMB2_PORT_RREG))
        elif (femb_addr == 3 ):
            sock_read.sendto(READ_MESSAGE,(self.UDP_IP,self.UDPFEMB3_PORT_RREG))

        sock_read.close()

        #try to receive response packet from board, store in hex
        data = []
        try:
                data = sock_readresp.recv(4*1024)
        except socket.timeout:
                self.udp_timeout_cnt = self.udp_timeout_cnt  + 1
                #print "FEMB_UDP--> Error read_reg: No read packet received from board, quitting"
                sock_readresp.close()
                return -1        
        dataHex = data.encode('hex')
        sock_readresp.close()

        #extract register value from response
        if int(dataHex[0:4],16) != regVal :
                #print "FEMB_UDP--> Error read_reg: Invalid response packet"
                return None
        dataHexVal = int(dataHex[4:12],16)
        #print "FEMB_UDP--> Write: reg=%x,value=%x"%(reg,dataHexVal)
        return dataHexVal

    def read_reg_wib(self, reg ):
        dataHex = self.read_reg( reg)
        return dataHex

    def write_reg_wib_checked (self, reg , data ):
        i = 0
        while (i < 10 ):
            time.sleep(0.001)
            self.write_reg_wib(reg , data )
            self.wib_wr_cnt = self.wib_wr_cnt + 1
            time.sleep(0.001)
            rdata = self.read_reg_wib(reg)
            time.sleep(0.001)
            rdata = self.read_reg_wib(reg)
            time.sleep(0.001)
            if (data == rdata ):
                break
            else:
                i = i + 1
                self.wib_wrerr_cnt = self.wib_wrerr_cnt + 1
                time.sleep(abs(i -1 + 0.001))
        if i >= 10 :
            print "readback value is different from written data, %d, %x, %x"%(reg, data, rdata)
            sys.exit()

    def get_rawdata(self):
        #set up listening socket
        sock_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
        sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_data.bind(('', self.UDP_PORT_HSDATA))
        sock_data.settimeout(2)

        #receive data, don't pause if no response
        try:
            #data = sock_data.recv(8*1024)
            data = sock_data.recv(9014)
        except socket.timeout:
            self.udp_hstimeout_cnt = self.udp_hstimeout_cnt  + 1
            print "FEMB_UDP--> Error get_data: No data packet received from board, quitting"
            sock_data.close()
            return []
        return data

    def get_rawdata_packets(self, val):
        numVal = int(val)
        #if (numVal < 0) or (numVal > self.MAX_NUM_PACKETS):
        if (numVal < 0) :
            print "FEMB_UDP--> Error record_hs_data: Invalid number of data packets requested"
            return None

        try_n = 0
        timeout_cnt = 0
        defe_pkg_cnt = 0
        lost_pkg_fg  = True
        while ( lost_pkg_fg == True ):
            #set up listening socket
            sock_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
            sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#            sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 81920000)
            sock_data.bind(('',self.UDP_PORT_HSDATA))
            sock_data.settimeout(3)
            #write N data packets to file
            rawdataPackets = [] 
            for packet in range(0,numVal,1):
                data = None
                try:
                    data = sock_data.recv(8192)
                except socket.timeout:
                    self.udp_hstimeout_cnt = self.udp_hstimeout_cnt  + 1
                    if (timeout_cnt == 10):
                        sock_data.close()
                        print "ERROR: UDP timeout, Please check if there is any conflict (someone else try to control WIB at the same time), continue anyway"
                        return None
                    else:
                        timeout_cnt = timeout_cnt + 1
                        self.write_reg_wib_checked (15, 0) 
                        print "ERROR: UDP timeout,  Please check if there is any conflict, Try again in 10 seconds"
                        time.sleep(0.1)
                        continue
                if data != None :
                    rawdataPackets.append(data)
            sock_data.close()

            rawdata_str = ''.join(rawdataPackets)
            pkg_chk = True
            if (pkg_chk):
                try_n = try_n + 1
                lost_pkg_fg = False
                #check data 
                smps = len(rawdata_str) / 2 / 16
                dataNtuple =struct.unpack_from(">%dH"%(smps*16),rawdata_str)
                if (self.jumbo_flag):
                    pkg_len = 0x1E06/2
                else:
                    pkg_len = 0x406/2
                pkg_index  = []
                datalength = long( (len(dataNtuple) // pkg_len) -3) * (pkg_len) 
                i = 0 
                while (i <= datalength ):
                    pkg_cnt0 =  ((dataNtuple[i+0]<<16)&0x00FFFFFFFF) + (dataNtuple[i+1]& 0x00FFFFFFFF) + 0x00000001
                    pkg_cnt1 =  ((dataNtuple[i+0+pkg_len]<<16)&0x00FFFFFFFF) + (dataNtuple[i+1+pkg_len]& 0x00FFFFFFFF)
                    acc_flag = (pkg_cnt0 == pkg_cnt1)
                    face_flg = ((dataNtuple[i+2+6] == 0xface) or (dataNtuple[i+2+6] == 0xfeed))

                    if (acc_flag == True) and (face_flg == True) :
                        pkg_index.append(i)
                        i = i + pkg_len
                    else:
                        lost_pkg_fg = True
                        defe_pkg_cnt = defe_pkg_cnt + 1
                        time.sleep(0.1)
                        break
                if (lost_pkg_fg == True):
                    if  (defe_pkg_cnt <10):
                        continue
                    else:
                        print "defective packages in the %dth try were found!!!, try again"%defe_pkg_cnt
                        pass
                else:
                    pass
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
                    if (try_n > 8 ):
                        print "UDP. missing udp pkgs = %d, total pkgs = %d "%(missed_pkgs, pkg_sum)
                        print "UDP. missing %.8f%% udp packages"%(100.0*missed_pkgs/pkg_sum)
                    lost_pkg_fg = True
                    time.sleep(0.1)
                else:
                    lost_pkg_fg = False

                if (try_n > 10 ):
                    print "defective packages or missing packages at 10th attempts, pass anyway"
                    lost_pkg_fg = False

            else:
                lost_pkg_fg = False
        return rawdata_str

    def write_reg_send(self, sock_write, WRITE_MESSAGE, wib=True, femb = 0):
        if (wib == True):
            sock_write.sendto(WRITE_MESSAGE,(self.UDP_IP, self.UDP_PORT_WREG ))
        else:
            if (femb == 0 ):
                sock_write.sendto(WRITE_MESSAGE,(self.UDP_IP, self.UDPFEMB0_PORT_WREG  ))
            elif (femb == 1 ):
                sock_write.sendto(WRITE_MESSAGE,(self.UDP_IP, self.UDPFEMB1_PORT_WREG  ))
            elif (femb == 2 ):
                sock_write.sendto(WRITE_MESSAGE,(self.UDP_IP, self.UDPFEMB2_PORT_WREG  ))
            elif (femb == 3 ):
                sock_write.sendto(WRITE_MESSAGE,(self.UDP_IP, self.UDPFEMB3_PORT_WREG  ))

    def reg_data_gen(self, reg , data ):
        regVal = int(reg)
        if (regVal < 0) or (regVal > self.MAX_REG_NUM):
            #print "FEMB_UDP--> Error write_reg: Invalid register number"
            return None
        dataVal = int(data)
        if (dataVal < 0) or (dataVal > self.MAX_REG_VAL):
            #print "FEMB_UDP--> Error write_reg: Invalid data value"
            return None
        #crazy packet structure require for UDP interface
        dataValMSB = ((dataVal >> 16) & 0xFFFF)
        dataValLSB = dataVal & 0xFFFF
        WRITE_MESSAGE = struct.pack('HHHHHHHHH',socket.htons( self.KEY1  ), socket.htons( self.KEY2 ),socket.htons(regVal),socket.htons(dataValMSB),
                socket.htons(dataValLSB),socket.htons( self.FOOTER  ), 0x0, 0x0, 0x0  )
        return WRITE_MESSAGE

    def select_femb_asic_bromberg(self, sock_write, femb = 0, asic = 0 ):
        #write wib
        wib_femb_cs = self.reg_data_gen(reg=7,data=0x80000000)
        self.write_reg_send(sock_write, wib_femb_cs, wib=True) #
        #write femb 
        asic_cs = asic & 0x0F
        asic_cs = self.reg_data_gen(reg=7,data=asic_cs)
        self.write_reg_send(sock_write, asic_cs, wib=False, femb=femb) #
        #write femb 
        hs = self.reg_data_gen(reg=17,data=1)
        self.write_reg_send(sock_write, hs, wib=False, femb=femb) #
        #write wib
        wib_asic =  ( ((femb << 16)&0x000F0000) + ((asic << 8) &0xFF00) ) 
        wib_femb_cs = self.reg_data_gen(reg=7,data= wib_asic | 0x80000000)
        self.write_reg_send(sock_write, wib_femb_cs, wib=True) #
        wib_femb_cs = self.reg_data_gen(reg=7,data= wib_asic )
        self.write_reg_send(sock_write, wib_femb_cs, wib=True) #

    def write_reg_init(self ):
        sock_write = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
        sock_write.setblocking(0)
        return sock_write

    def write_reg_close(self, sock_write):
        sock_write.close()

    def get_rawdata_packets_bromberg(self, path, step, fe_cfg_r, fembs_np = [0,1,2,3], cycle=100):
        numVal = int(cycle)
        if (numVal < 0) :
            print "FEMB_UDP--> Error record_hs_data: Invalid number of data packets requested"
            return None

        buf_size = self.reg_data_gen(reg=16,data=0x7F00)
        nor_mode = self.reg_data_gen(reg=15,data=0)
        fifo_clr_mode = self.reg_data_gen(reg=15,data=3)
        acq_mode = self.reg_data_gen(reg=15,data=1)
        stopacq_mode = self.reg_data_gen(reg=15,data=2)
        read_mode = self.reg_data_gen(reg=15,data=0x12)

        #set up listening socket
        sock_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
        sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_data.bind(('',self.UDP_PORT_HSDATA))
        sock_data.settimeout(0.05)

        sock_write = self.write_reg_init()
        self.write_reg_send(sock_write, buf_size, wib=True) #set buffer size


        for read_no in range(0,numVal,1):
            print "Read cycle = %d "%read_no
            self.write_reg_send(sock_write, nor_mode, wib=True) #
            time.sleep(0.001)
            self.write_reg_send(sock_write, fifo_clr_mode, wib=True) #

            empty_udp = False
            while ( empty_udp != True ):
                try:
                    data = sock_data.recv(8192)
                except socket.timeout:
                    self.udp_hstimeout_cnt = self.udp_hstimeout_cnt  + 1
                    #print "Empty UDP buffer"
                    empty_udp = True 
                    break

            self.write_reg_send(sock_write, acq_mode, wib=True) #
            time.sleep(0.01) #10ms
            self.write_reg_send(sock_write, stopacq_mode, wib=True) #

            for femb in fembs_np:
                for asic in range(0,8,2):
                    self.select_femb_asic_bromberg(sock_write, femb, asic )
                    rawdataPackets = [] 
                    filename = path + "/" + step +"_FEMB" + str(femb) + "CHIP" + str(asic) + "_" + format(fe_cfg_r,'02X') + "_" + format(read_no,'04d') + ".bin"

                    self.write_reg_send(sock_write, read_mode, wib=True) #
                    for packet in range(0,1000,1):
                        data = None
                        timeout_flg = False
                        try:
                            data = sock_data.recv(8192)
                        except socket.timeout:
                            self.udp_hstimeout_cnt = self.udp_hstimeout_cnt  + 1
                            timeout_flg = True
                        if data != None :
                            rawdataPackets.append(data)
                        if (timeout_flg):
                            break
        
                    rawdata_str = ''.join(rawdataPackets)
                    with open(filename,"wb") as f:
                        f.write(rawdata_str) 

        self.write_reg_send(sock_write, nor_mode, wib=True) #
        time.sleep(0.1)
        empty_udp = False
        data = None
        while ( empty_udp != True ):
            try:
                data = sock_data.recv(8192)
            except socket.timeout:
                self.udp_hstimeout_cnt = self.udp_hstimeout_cnt  + 1
                print "Can't return to normal mode"
                sys.exit()
            if data!= None: 
                print "Brombreg mode is DONE, return to normal mode sucessfully"
                empty_udp = True 
                break

        sock_data.close()
        self.write_reg_close(sock_write)


    #__INIT__#
    def __init__(self):
        #self.UDP_IP = "192.168.121.1"
        self.UDP_IP = "10.73.136.36"
        self.jumbo_flag = True
        self.wib_wr_cnt = 0
        self.wib_wrerr_cnt = 0
        self.femb_wr_cnt = 0
        self.femb_wrerr_cnt = 0
        self.femb_wrerr_log = []
        self.udp_timeout_cnt = 0
        self.udp_hstimeout_cnt = 0
        self.KEY1 = 0xDEAD
        self.KEY2 = 0xBEEF
        self.FOOTER = 0xFFFF
        self.UDP_PORT_WREG = 32000
        self.UDP_PORT_RREG = 32001
        self.UDP_PORT_RREGRESP = 32002
        self.UDP_PORT_HSDATA = 32003
        self.MAX_REG_NUM = 0x666
        self.MAX_REG_VAL = 0xFFFFFFFF
        self.MAX_NUM_PACKETS = 1000000

        self.UDPFEMB0_PORT_WREG =     32016
        self.UDPFEMB0_PORT_RREG =     32017
        self.UDPFEMB0_PORT_RREGRESP = 32018

        self.UDPFEMB1_PORT_WREG =     32032
        self.UDPFEMB1_PORT_RREG =     32033
        self.UDPFEMB1_PORT_RREGRESP = 32034

        self.UDPFEMB2_PORT_WREG =     32048
        self.UDPFEMB2_PORT_RREG =     32049
        self.UDPFEMB2_PORT_RREGRESP = 32050

        self.UDPFEMB3_PORT_WREG =     32064
        self.UDPFEMB3_PORT_RREG =     32065
        self.UDPFEMB3_PORT_RREGRESP = 32066

