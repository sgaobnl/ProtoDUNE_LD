#!/bin/bash
#####python
#####argv[0]  --> "./MainCOTS.py" --> top file
#####argv[1]  --> LArIAT --> TPC name
####
#####argv[2]  --> 0x00:  turn FEMBs on
#####argv[2]  --> 0x80:  turn FEMBs off
#####argv[2]  --> 0x20: configuration for DAQ, 0x10:check run, 0x01: noise, 0x02: fpga-dac calibration, 0x04: asic-dac calibration 
####
#####argv[3]  --> True or False, jumbo frame size,
#####argv[4]  --> ADC phase set, default 0, no need to change

#python "./MainCOTS.py" LArIAT 0x00 False 0 
#python "./MainCOTS.py" LArIAT 0x10 False 0 
#python "./MainCOTS.py" LArIAT 0x80 False 0
#python "./MainCOTS.py" LArIAT 0x01 True 0 
#python "./MainCOTS.py" LArIAT 0x02 False 0 
#python "./MainCOTS.py" LArIAT 0x04 False 0 
#python "./MainCOTS.py" LArIAT 0x80 False 0

####argvp5] to argv[10] need to be set only when argv[2] is 0x20
####argv[5]  --> gain setting 0 = 4.7mV/fC, 1 = 14, 2=7.8, 3 = 25.0
####argv[6]  --> shaping time setting 0 = 1.0us, 1 = 3.0us, 2 = 0.5us, 3=2.0us

####argv[7]  --> source of pluse, 0: disable, 1: internal pulse(pulse from FPGA or WIB)k 2: external pulse, 3: both 
####argv[8]  --> bit[7:0], bit[7] fpgadac enable flag (1 enable, 0 disable)
####argv[8]  --> bit[7:0], bit[6] asicdac enable flag (1 enable, 0 disable)
####argv[8]  --> bit[7:0], bit[5:0] dac value 0x00 ~ 0x3F
####argv[9]  --> leakage current setting, 0x00 --> 500pA, 0x01--> 100pA, 0x10-->5nA, 0x11-->1nA
####argv[10] --> mbb configuration bit[8:0], bit[8] --> MBB active flag (if there is a MBB)
####argv[10] --> mbb configuration bit[8:0], bit[7] --> MBB start daq enalbe (0enable, 1disable)
####argv[10] --> mbb configuration bit[8:0], bit[6] --> MBB stop daq enalbe (0enable, 1disable)
####argv[10] --> mbb configuration bit[8:0], bit[6] --> MBB timestampe reset enalbe (0enable, 1disable)
####argv[10] --> mbb configuration bit[8:0], bit[4] --> MBB calibration pulse enalbe (0enable, 1disable)
####argv[10] --> mbb configuration bit[8:0], bit[3] --> MBB start daq
####argv[10] --> mbb configuration bit[8:0], bit[2] --> MBB stop daq
####argv[10] --> mbb configuration bit[8:0], bit[1] --> MBB timestampe reset
####argv[10] --> mbb configuration bit[8:0], bit[0] --> MBB calibration pulse

#python "./MainCOTS.py" LArIAT 0x00 False 0
#python "./MainCOTS.py" LArIAT 0x20 False 0 1 3 0 0x00 0 0x102

####argvp5] to argv[6] need to be set only when argv[2] is 0x20
####argv[5]  --> how many times you want to get local diagnositcs data 
####argv[6]  --> gap between two sets of local diagnositcs data 
#python "./MainCOTS.py" LArIAT 0x40 False 0 1 10
#python "./MainCOTS.py" LArIAT 0x80 False 0


python "./MainCOTS.py" LArIAT 0x20 False 0 1 0 1 0x8D 0 0x102
python "./MainCOTS.py" LArIAT 0x40 False 0 1 10

python "./MainCOTS.py" LArIAT 0x20 False 0 1 1 1 0x8D 0 0x102
python "./MainCOTS.py" LArIAT 0x40 False 0 1 10

python "./MainCOTS.py" LArIAT 0x20 False 0 1 2 1 0x8D 0 0x102
python "./MainCOTS.py" LArIAT 0x40 False 0 1 10

python "./MainCOTS.py" LArIAT 0x20 False 0 1 3 1 0x8D 0 0x102
python "./MainCOTS.py" LArIAT 0x40 False 0 1 10

#python "./MainCOTS.py" LArIAT 0x20 False 0 1 3 0 0x00 0 0x102
#python "./MainCOTS.py" LArIAT 0x40 False 0 1 10


