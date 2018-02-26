#!/usr/bin/env python33

import string

class ADC_ASIC_REG_MAPPING:

####sec_chn_reg only sets a channel register, the other registers remains as before
    def set_chn_reg(self, chip=0, chn=0, d=0, pcsr=0, pdsr=0, slp=0, tstin=0 ):
        tmp_d = ((d<<4)&0xF0)
        tmp_d0 = (tmp_d & 0x80)>>3
        tmp_d1 = (tmp_d & 0x40)>>1
        tmp_d2 = (tmp_d & 0x20)<<1
        tmp_d3 = (tmp_d & 0x10)<<3
        tmp_d = tmp_d0 + tmp_d1 + tmp_d2 + tmp_d3

        chn_reg = (tmp_d&0xF0) + ((pcsr&0x01)<<3) + ((pdsr&0x01)<<2) + ((slp&0x01)<<1) + ((tstin&0x01)<<0)

        chn_reg_bool = []
        for j in range(8):
            chn_reg_bool.append ( bool( (chn_reg>>j)%2 ) )

        start_pos = (8*16+16)*chip + (16-chn)*8
        self.REGS[start_pos-8 : start_pos] = chn_reg_bool

####sec_chip_global only sets a chip global register, the other registers remains as before
    def set_chip_global(self, chip, 
                        f4=0, f5=0, slsb=0, res4=0, res3=0, res2=0, res1=0, res0=0,
                        clk0=0, clk1=0, frqc=0, engr=0, f0=0, f1=0, f2=0, f3=0):
        global_reg = [False] * 16
        global_reg[ 0] = (bool(res0))
        global_reg[ 1] = (bool(res1))
        global_reg[ 2] = (bool(res2))
        global_reg[ 3] = (bool(res3)) 
        global_reg[ 4] = (bool(res4))
        global_reg[ 5] = (bool(slsb))
        global_reg[ 6] = (bool(f5  ))
        global_reg[ 7] = (bool(f4  ))
        global_reg[ 8] = (bool(f3  ))
        global_reg[ 9] = (bool(f2  ))
        global_reg[10] = (bool(f1  ))
        global_reg[11] = (bool(f0  ))
        global_reg[12] = (bool(engr))
        global_reg[13] = (bool(frqc))
        global_reg[14] = (bool(clk1))
        global_reg[15] = (bool(clk0))

        start_pos = (8*16+16)*chip + 16*8
        self.REGS[start_pos : start_pos+16] = global_reg

####sec_chip sets registers of a whole chip, registers of the other chips remains as before
    def set_chip(self, chip=0,
                 d=0, pcsr=0, pdsr=0, slp=0, tstin=0,
                 f4=0, f5=0, slsb=0, res4=0, res3=0, res2=0, res1=0, res0=0,
                 clk0=0, clk1=0, frqc=0, engr=0, f0=0, f1=0, f2=0, f3=0):
        for chn in range(16):
            self.set_chn_reg(chip, chn, d, pcsr, pdsr, slp, tstin )     

        self.set_chip_global( chip, 
                              f4, f5, slsb, res4, res3, res2, res1, res0,
                              clk0, clk1, frqc, engr, f0, f1, f2, f3)

####sec_board sets registers of a whole board 
    def set_adc_board(self,  
                 d=0, pcsr=0, pdsr=0, slp=0, tstin=0,
                 f4=0, f5=0, slsb=0, res4=0, res3=0, res2=0, res1=0, res0=0,
                 clk0=0, clk1=0, frqc=0, engr=0, f0=0, f1=0, f2=0, f3=0):
        for chip in range(8):
            self.set_chip(chip,
                        d, pcsr, pdsr, slp, tstin,
                        f4, f5, slsb, res4, res3, res2, res1, res0,
                        clk0, clk1, frqc, engr, f0, f1, f2, f3)

    #__INIT__#
    def __init__(self):
	#declare board specific registers
        self.REGS = [False]*(8*16+16)*8 

