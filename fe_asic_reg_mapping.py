#!/usr/bin/env python33

import string

class FE_ASIC_REG_MAPPING:

####sec_chn_reg only sets a channel register, the other registers remains as before
    def set_fechn_reg(self, chip=0, chn=0, sts=0, snc=0, sg=0, st=0, smn=0, sdf=1 ):
        snc = 0
        chn_reg = ((sts&0x01)<<7) + ((snc&0x01)<<6) + ((sg&0x03)<<4) + ((st&0x03)<<2)  + ((smn&0x01)<<1) + ((sdf&0x01)<<0) 
        chn_reg_bool = []
        for j in range(8):
            chn_reg_bool.append ( bool( (chn_reg>>j)%2 ) )
        start_pos = (8*16+16)*chip + (16-chn)*8
        self.REGS[start_pos-8 : start_pos] = chn_reg_bool



####sec_chip_global only sets a chip global register, the other registers remains as before
    def set_fechip_global(self, chip=0, slk0 = 0, stb1 = 0, stb = 0, s16=0, slk1=0, sdc = 0, swdac=0, dac=0):
        global_reg = ((slk0&0x01)<<0) + ((stb1&0x01)<<1) + ((stb&0x01)<<2)+ ((s16&0x01)<<3) + ((slk1&0x01)<<4) + ((sdc&0x01)<<5) +((00&0x03)<<6)
        dac_reg = (((dac&0x01)//0x01)<<7)+(((dac&0x02)//0x02)<<6)+\
                  (((dac&0x04)//0x04)<<5)+(((dac&0x08)//0x08)<<4)+\
                  (((dac&0x10)//0x10)<<3)+(((dac&0x20)//0x20)<<2)+\
                  (((swdac&0x03))<<0) 

        global_reg_bool = []
        for j in range(8):
            global_reg_bool.append ( bool( (global_reg>>j)%2 ) )
        for j in range(8):
            global_reg_bool.append ( bool( (dac_reg>>j)%2 ) )

        start_pos = (8*16+16)*chip + 16*8
        self.REGS[start_pos : start_pos+16] = global_reg_bool


####sec_chip sets registers of a whole chip, registers of the other chips remains as before
    def set_fechip(self, chip=0,
                 sts=0, snc=0, sg=0, st=0, smn=0, sdf=1,
                 slk0=0, stb1=0, stb=0, s16=0, slk1=0, sdc=0, swdac=0, dac=0):
        for chn in range(16):
            self.set_fechn_reg(chip=chip, chn=chn, sts=sts, snc=snc, sg=sg, st=st, smn=smn, sdf=sdf)     

        self.set_fechip_global (chip, slk0, stb1, stb, s16, slk1, sdc, swdac, dac)

####sec_board sets registers of a whole board 
    def set_fe_board(self, sts=0, snc=0, sg=0, st=0, smn=0, sdf=1, 
                       slk0 = 0, stb1 = 0, stb = 0, s16=0, slk1=0, sdc=0, swdac=0, dac=0):
        for chip in range(8):
            self.set_fechip( chip, sts, snc, sg, st, smn, sdf, slk0, stb1, stb, s16, slk1, sdc, swdac, dac)

    #__INIT__#
    def __init__(self):
	#declare board specific registers
        self.REGS = [False]*(8*16+16)*8 

