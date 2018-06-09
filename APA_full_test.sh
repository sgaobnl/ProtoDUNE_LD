#!/bin/bash

#check APA one by one, if WIEC is off, please comment corresponding APA
#check APA1
python Main.py APA1 0x00 True server 
python Main.py APA1 0x13 False server 
python Main.py APA1 0x80 True server 
#check APA2
python Main.py APA2 0x00 True server 
python Main.py APA2 0x13 False server 
python Main.py APA2 0x80 True server 
#check APA3
python Main.py APA3 0x00 True server 
python Main.py APA3 0x13 False server 
python Main.py APA3 0x80 True server 
#check APA4
python Main.py APA4 0x00 True server 
python Main.py APA4 0x13 False server 
python Main.py APA4 0x80 True server 
#check APA5
python Main.py APA5 0x00 True server 
python Main.py APA5 0x13 False server 
python Main.py APA5 0x80 True server 
#check APA6
python Main.py APA6 0x00 True server 
python Main.py APA6 0x13 False server 
python Main.py APA6 0x80 True server 

####    #check all APA together
####    #step 1--> All WIEC are powered, turn CE boxes on one APA by one APA
####    python Main.py APA1 0x00 True server 
####    python Main.py APA2 0x00 True server 
####    python Main.py APA3 0x00 True server 
####    python Main.py APA4 0x00 True server 
####    python Main.py APA5 0x00 True server 
####    python Main.py APA6 0x00 True server 
####    
####    #step 2--> checkout test 
####    python Main.py APA1 0x13 False server 
####    python Main.py APA2 0x13 False server 
####    python Main.py APA3 0x13 False server 
####    python Main.py APA4 0x13 False server 
####    python Main.py APA5 0x13 False server 
####    python Main.py APA6 0x13 False server 
####    
####    #step 3 --> Trun all CE boxes off
####    python Main.py APA1 0x80 True server 
####    python Main.py APA2 0x80 True server 
####    python Main.py APA3 0x80 True server 
####    python Main.py APA4 0x80 True server 
####    python Main.py APA5 0x80 True server 
####    python Main.py APA6 0x80 True server 


