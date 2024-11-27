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

from specu1b_DLL import specu1b, UNIT_PARAMETER, UNIT_INFORMATION  # Loading DLL

import numpy as np
import matplotlib.pyplot as plt
import System

DLL = specu1b()     # Class instantiation
unit_param = UNIT_PARAMETER()
unit_info = UNIT_INFORMATION()

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

        self._check = DLL.USB_CheckDevice(self._handle)
        print('check = ', self._check)

        self._pipe = DLL.USB_OpenPipe(self._handle)
        print('device_pipe =', self._pipe)

        self._c_array = System.Array[System.Double]([0.0 for _ in range(6)])
        self._origin_c_array = System.Array[System.Double]([206.6901787, 
                                                            0.3771377233, 
                                                            3.669128424e-5, 
                                                            -1.287399061e-8,
                                                            5.788371505e-12,
                                                            -1.2738255e-15])
        
        self.buffer_array = System.Array[System.UInt16]([0 for _ in range(2048)])

        self.read_unit_information()
        self.get_parameter()
        self.read_calibration_value()
    
    def get_parameter(self):
        """
        Get currently set parameters.

        Parameters
        ----------
        integration_time: int
            Range is 5000µs-10000000µs (5ms-10s). The minimum integration times
            differ depending on the model. Minimum is 10000 µs for C10083CA.
        gain: hex
            0x00 (Low gain)
            0x01 (High gain)
            0xFF (Gain switching function is unavailable)
        trigger_edge: hex
            0x00 (Rising edge (H level))
            0x01 (Falling edge (L level))
            0xFF (External trigger function is unavailable)
        trigger_mode: hex
            0x00 (Rising edge (H level))
            0x01 (Falling edge (L level))
            0xFF (External trigger function is unavailable)
        reserved_param:
            Reserved byte
        """
        DLL.USB_GetParameter(self._handle, unit_param)
        self.integration_time = unit_param.unIntegrationTime
        self.gain = hex(unit_param.byGain)
        self.trigger_edge = hex(unit_param.byTriggerEdge)
        self.trigger_mode = hex(unit_param.byTriggerMode)
        self.reserved_param = unit_param.byReserved
    
    # # Read current parameters
    # print('Integration time =', get_parameter[1].unIntegrationTime, 'µs')

    def set_parameter(self, integ_time=None, gain=None, trigger_edge=None, trigger_mode=None):
        """
        Set specified parameter with specified value
        """
        if integ_time is not None:
            DLL.USB_GetParameter(self._handle, unit_param)[1].unIntegrationTime = integ_time
        elif gain is not None:
            DLL.USB_GetParameter(self._handle, unit_param)[1].byGain = gain
        elif trigger_edge is not None:
            DLL.USB_GetParameter(self._handle, unit_param)[1].byTriggerEdge = trigger_edge
        elif trigger_mode is not None:
            DLL.USB_GetParameter(self._handle, unit_param)[1].byTriggerMode = trigger_mode
        DLL.USB_SetParameter(self._handle, unit_param)
    
    def set_default(self):
        """
        Set all parameters to default
        """
        DLL.USB_SetEepromDefaultParameter(self._handle, 0)
    
    def read_unit_information(self):
        DLL.USB_ReadUnitInformation(self._handle, unit_info)[0]
        self.unit_id = bytearray(unit_info.arybyUnitID).decode('ascii')
        self.sensor_name = bytearray(unit_info.arybySensorName).decode('ascii')
        self.serial_number = bytearray(unit_info.arybySerialNumber).decode('ascii')
        self.reserved = bytearray(unit_info.arybyReserved)
        self.wl_upper = unit_info.usWaveLengthUpper
        self.wl_lower = unit_info.usWaveLengthLower
    
    def write_unit_information(self, flag=None):
        """
        Writes information into USB device. Unit ID, sensor name, serial number and 
        spectral response range (upper and lower limits) can be written.

        Parameters
        ----------
        flag: hex
            The flag value needs to be 0xAA to allow writing to device.
        """
        DLL.USB_WriteUnitInformation(self._handle, unit_info, flag)

    def read_calibration_value(self):
        DLL.USB_ReadCalibrationValue(self._handle, self._c_array)
        self.calibration_list = list(self._c_array)

    def write_calibration_value(self, flag=None):
        """
        Write calibration values with original values. flag need to be 0xAA
        """
        DLL.USB_WriteCalibrationValue(self._handle, self._origin_c_array, flag)

    def get_sensor_data(self):
        x = np.linspace(0, 2047, 2048)
        y = list(DLL.USB_GetSensorData(self._handle, self._pipe, 2048, self.buffer_array)[1])
        return x, y

    def close(self):
        DLL.USB_ClosePipe(self._handle)
        DLL.USB_CloseDevice(self._handle)


if __name__ == "__main__":
    spectro = MiniSpectro('tm_ccd')
    x, y = spectro.get_sensor_data()

    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(1, 1, 1)

    print(x)
    print(y)

    ax.plot(x , y)

    plt.tight_layout()
    plt.show()

    spectro.close()


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
