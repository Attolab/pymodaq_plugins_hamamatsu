# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 08:51:38 2018

@author: AAA
"""

import clr
import sys

driver_dir = r"C:\\Program Files\\Hamamatsu\\TokuSpec"
sys.path.append(driver_dir)

clr.AddReference("specu1b")  # Enter driver name without .dll

from specu1b_DLL import specu1b, UNIT_PARAMETER  # Loading DLL

# from time import sleep
# from decimal import *
# import numpy as np
# import matplotlib.pyplot as plt
# import System

DLL = specu1b()     # Class instantiation
unit_param = UNIT_PARAMETER()

# sid = 0
# frame = System.Int64(0)
# index = 0
# x = 0
# y = 0

class MiniSpectro:
    """
    Hamamatsu Minispectrometers class

    Attributes
    ----------
    device_name: str
        Name of the target Hamamatsu Minispectrometer
    
    Methods
    -------
    get_parameter()
        Get parameters from target device
    ...

    """
    
    def __init__(self, device_name='tm_ccd'):

        _pids = {
            'proto': 0x2900,        # Old TG Series
            'tg': 0x2905,           # *[C9404MC], *[C9405MC], C9406GC
            'tg_cooled': 0x2907,    # C9913GC, C9914GB
            'tm': 0x2908,           # C10082MD, C10083MD
            'tg_ccd': 0x290D,       # C9404CA, C9404CAH, C9405CB, *[C9405CA]
            'tm_ccd': 0x2909,       # C10082CA, C10083CA, C10082CAH, C10083CAH
            'tg_raman1': 0x2909,    # C11713CA
            'tg_raman2': 0x290D     # C11714CA, C11714CB
        }

        self._handle = DLL.USB_OpenDevice(_pids[device_name])
        print('handle = ', self._handle)

        _check = DLL.USB_CheckDevice(self._handle)
        print('check = ', _check)

        _pipe = DLL.USB_OpenPipe(self._handle)
        print('device_pipe =', _pipe)
    
    def integration_time(self):
        """
        Get integration time

        Returns
        -------
        integ_time: int
            Range is 5000µs-10000000µs (5ms-10s). The minimum integration times
            differ depending on the model
        """
        integ_time = DLL.USB_GetParameter(self._handle, unit_param)[1].unIntegrationTime
        return integ_time

    def gain(self):
        """
        Get the gain status

        Returns
        -------
        gain: hex
            0x00 (Low gain)
            0x01 (High gain)
            0xFF (Gain switching function is unavailable)
        """
        gain = hex(DLL.USB_GetParameter(self._handle, unit_param)[1].byGain)
        return gain

    def trigger_edge(self):
        """
        Get trigger edge setting

        Returns
        -------
        trig_edge: hex
            0x00 (Rising edge (H level))
            0x01 (Falling edge (L level))
            0xFF (External trigger function is unavailable)
        """
        trig_edge = hex(DLL.USB_GetParameter(self._handle, unit_param)[1].byTriggerEdge)
        return trig_edge

    def trigger_mode(self):
        """
        Get trigger mode setting

        Return
        ------
        trig_mode: hex
            0x00 (Internal trigger mode (free run))
            0x01 (External trigger mode1 (edge trigger detection))
            0xFF (External trigger mode2 (gate trigger mode))
        """
        trig_mode = hex(DLL.USB_GetParameter(self._handle, unit_param)[1].byTriggerMode)
        return trig_mode
    
    # # Read current parameters
    # print('Integration time =', get_parameter[1].unIntegrationTime, 'µs')

    # # Adjust and set new parameters values
    # get_parameter[1].unIntegrationTime = 20000
    # set_parameter = DLL.USB_SetParameter(handle, unit_param)

    # # Read new parameters values
    # print('Integration time =', get_parameter[1].unIntegrationTime, 'µs')

    # # Set default
    # set_default = DLL.USB_SetEepromDefaultParameter(handle, 0)

    def close(self):
        DLL.USB_ClosePipe(self._handle)
        DLL.USB_CloseDevice(self._handle)


if __name__ == "__main__":
    spectro = MiniSpectro('tm_ccd')
    # print(spectro.integration_time())
    spectro.close()


# mlist = System.Array[System.Int16]([9 for _ in range(4)])  # Define as an array that can be used in .NET
# mnum = 1
# r = DLL.USB2_getModuleConnectionList(mlist,mnum)  # Get USB module list
# print(r)

# mspec = Str.CSpectroInformation()  # Get structure
# r = DLL.USB2_getSpectroInformation(sid,mspec)  # Get module information
# print(r[1].unit)
# print(mspec.sensor)

# r = DLL.USB2_open(sid)  # Open device
# print(r)

# mode = 0  # Set capture mode (specified no. of times measurement)
# r = DLL.USB2_setCaptureMode(sid,mode)  #Set capture mode
# print(r)

# position = 1  # Set data position
# r = DLL.USB2_setDataPosition(sid,position)
# #print(r)

# count = 1  # Set specified no. of times
# r = DLL.USB2_setDataCount(sid, count)
# #print(r)

# transmit = 1  # Set data transmit number
# r = DLL.USB2_setDataTransmit(sid, transmit)
# #print(r)

# cycle = 12000  # Set exposure cycle
# r = DLL.USB2_setExposureCycle(sid, cycle)
# #print(r)

# sec = 10000  # Set exposure time
# r = DLL.USB2_setExposureTime(sid, sec)
# #print(r)

# mode = 0  # Sensor gain mode 
# gain = 0  # High gain
# r = DLL.USB2_setGain(sid,mode,gain)  # Set gain
# #print(r)

# offset = 0
# r = DLL.USB2_setAdOffset(sid,offset)  # Set A/D offset
# #print(r)

# r = DLL.USB2_getImageSize(sid,x,y)  # Get pixel size after bening. Note that value of x,y  are initial value.
# x = r[1]
# y = r[2]


# time = System.Array[System.UInt64]([0] * x * y)#Define as an array that can be used in .NET
# cdata = System.Array[float]([0.0 for _ in range(6)])#Match the data type to the DLL side
# pixel = np.arange(1, x + 1, 1) 
# wavelen = [0.0] * 512
# print(r)#Output (0,512,1)


# r = DLL.USB2_allocateBuffer(sid,10)#Allocate a buffer to capture

# image0 = System.Array[float]([0] * x * y)

# i = 0
# repeatcount = 10
# while i < repeatcount:
    

#     r = DLL.USB2_captureStart(sid,1)#Start capture mode
#     #print(r)
#     image = System.Array[System.UInt16]([0] * x * y)#Define as types that can be used in .NET
#     #print(list(image))
    
#     err = 1
#     while err != 0:
#         sleep(0.001)
#         r = DLL.USB2_getCaptureStatus(sid,frame,index)#Get the capture status, note that frame and index contain only initial values.
#         err = r[0]
#         frame = r[1]
#         index = r[2]
#        # print(r)
#    # print('c')
    
        
    
#     header = System.Array[System.UInt16]([0] * 256)#Specify the type as an array so that it can be used with .net，Value of headder size is 256.
#     r = DLL.USB2_getImageHeaderData(sid,header,image,index,frame,time)#Get the latest captured data from the buffer.
    
    
    
#     #print(r)
#     print(list(image))
#     #print(id(image))
#     #print(list(time))
    
#     r = DLL.USB2_captureStop(sid)#Stop capture mode
#     #print(r)
    

    
    
#     for a in range(x): 
    
#         image0[a] = image0[a] + image[a]
        
    

#     print(list(image0))
    
    
#     i +=1
    
# for b in range(x):
#     image0[b] = image0[b]/repeatcount
    

# print(list(image0))

# r = DLL.USB2_releaseBuffer(sid)#Release allocate buffer.




# DLL.USB2_close(sid)#Close device.
# #print(r)

# DLL.USB2_uninitialize()#Uninitialize device driver and library
# #print(r)

# plt.figure(figsize=(12,6))
# plt.plot(pixel,list(image))#.NET array, you need to call the contents with list(array).

# #If the argument doesn't contain any data, it might be because the type is not correct.
# #In python, there are some data types whose arguments can't be changed in the function, so it might be related to that....（For more information, search Immutable and Mutable.）
