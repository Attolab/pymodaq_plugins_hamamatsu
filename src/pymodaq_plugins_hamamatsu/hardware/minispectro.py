# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 14:20:19 2024

@author: Bastien Bégon
"""

import clr
import sys

driver_dir = r"C:\\Program Files\\Hamamatsu\\TokuSpec"  # Path to specu1b.dll file folder
sys.path.append(driver_dir)

clr.AddReference("specu1b")

from specu1b_DLL import specu1b, UNIT_PARAMETER, UNIT_INFORMATION

import usb.core
import usb.util

import time
import numpy as np
import System

DLL = specu1b()
unit_param = UNIT_PARAMETER()
unit_info = UNIT_INFORMATION()

class MiniSpectro:
    """
    Hamamatsu Minispectrometers class
    
    Methods
    -------
    get_parameter()
        Get currently set parameters (integration time, gain, trigger modes).
    set_parameter(integ_time, gain, trigger_edge, trigger_mode)
        Set specified parameter with specified value.
    set_default()
        Set all parameters to default.
    read_unit_information()
        Read device information.
    write_unit_information()
        Write information into USB device.
    read_calibration_value()
        Write calibration values with original values.
    get_sensor_data()
        Get sensor data currently in buffer and wipe buffer.
    close()
        Close device.
    """
    
    def __init__(self):
        for dev in usb.core.find(find_all=True):
            if hex(dev.idProduct).find("0x290") == 0:       # We make the assumption only Mini-spectrometers
                print("Hamamatsu Mini-spectrometer found")  # devices have a pid starting with 0x290
                pid = dev.idProduct

        self._handle = DLL.USB_OpenDevice(pid)  # Get index of spectrometer from pid

        if DLL.USB_CheckDevice(self._handle) == 11:
            print('Check connection success')
        else:
            raise ValueError('Check connection failed, please close or reconnect device')

        self._pipe = DLL.USB_OpenPipe(self._handle)

        self._c_array = System.Array[System.Double]([0.0 for _ in range(6)])    # 6 calibration values
        self._origin_c_array = System.Array[System.Double]([206.6901787,        # Values from TokusPec at 1st boot
                                                            0.3771377233, 
                                                            3.669128424e-5, 
                                                            -1.287399061e-8,
                                                            5.788371505e-12,
                                                            -1.2738255e-15])
        
        self.read_unit_information()
        self.get_parameter()
        self.read_calibration_value()

        self.buffer_array = System.Array[System.UInt16]([0 for _ in range(self.sensor_size)])

    def get_parameter(self):
        """
        Get currently set parameters.

        Returns
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
            0x00 (Internal trigger mode (freerun))
            0x01 (External trigger mode 1 (edge trigger detection))
            0x02 (External trigger mode 2 (gate trigger mode))
        reserved_param:
            Reserved byte
        """
        DLL.USB_GetParameter(self._handle, unit_param)
        self.integration_time = unit_param.unIntegrationTime
        self.gain = hex(unit_param.byGain)
        self.trigger_edge = hex(unit_param.byTriggerEdge)
        self.trigger_mode = hex(unit_param.byTriggerMode)
        self.reserved_param = unit_param.byReserved

    def set_parameter(self, integ_time=None, gain=None, trigger_edge=None, trigger_mode=None):
        """
        Set specified parameter with specified value.
        Integration time, gain, trigger edge and trigger mode can be set

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
            0x00 (Internal trigger mode (freerun))
            0x01 (External trigger mode 1 (edge trigger detection))
            0x02 (External trigger mode 2 (gate trigger mode))
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
        Set all parameters to default.
        """
        DLL.USB_SetEepromDefaultParameter(self._handle, 0)
    
    def read_unit_information(self):
        """
        Read device information.

        Returns
        -------
        unit_id: str
            The Hamamatsu device ID starting with 1 letter and 1 number.
        sensor_name: str
            The name of the sensor used in the spectrometer
        serial_number: str
            Serial number of the device.
        reserved: str
            Reserved and unused bytes according to .DLL documentation
        wl_lower: int
            Lower wavelength the spectrometer is set to detect. Makes it
            possible to bound to the lower/first pixel on device sensor.
        wl_upper: int
            Upper wavelength the spectrometer is set to detect. Makes it
            possible to bound to the upper/last pixel on device sensor.
        """
        DLL.USB_ReadUnitInformation(self._handle, unit_info)[0]
        self.unit_id = bytearray(unit_info.arybyUnitID).decode('ascii')
        self.sensor_name = bytearray(unit_info.arybySensorName).decode('ascii')
        self.serial_number = bytearray(unit_info.arybySerialNumber).decode('ascii')
        self.reserved = bytearray(unit_info.arybyReserved)
        self.lower_wl = unit_info.usWaveLengthLower
        self.upper_wl = unit_info.usWaveLengthUpper

        if self.unit_id.find('1') == 1:  # Check 2nd character in unit_id string
            self.sensor_size = 256       # to determine sensor size
        elif self.unit_id.find('2') == 1:
            self.sensor_size = 512
        elif self.unit_id.find('3') == 1:
            self.sensor_size = 1024
        elif self.unit_id.find('4') == 1:
            self.sensor_size = 2048
    
    def write_unit_information(self, flag=None):
        """
        Write information into USB device. Unit ID, sensor name, serial number and 
        spectral response range (upper and lower limits) are written.

        Parameters
        ----------
        flag: hex
            The flag value needs to be 0xAA to allow writing to device.
        """
        DLL.USB_WriteUnitInformation(self._handle, unit_info, flag)

    def read_calibration_value(self):
        """
        Reads calibration coefficients saved in device

        Returns
        -------
        calibration_list: list(float)
            List of 6 float values corresponding to A, B1, B2, B3, B4 and B5 calibration coefficients.
            λ(nm) = A + B1*pix + B2*pix² + B3*pix³ + B4*pix⁴ + B5*pix⁵ with pix any pixel on sensor.
        """
        DLL.USB_ReadCalibrationValue(self._handle, self._c_array)
        self.calibration_list = list(self._c_array)

    def write_calibration_value(self, flag=None):
        """
        Write calibration values with original values.
        
        Parameters
        ----------
        flag: hex
            The flag value needs to be 0xAA to allow writing to device.
        """
        DLL.USB_WriteCalibrationValue(self._handle, self._origin_c_array, flag)

    def get_sensor_data(self):
        """
        Get sensor data currently in buffer and wipe buffer.

        Returns
        -------
        pixel_array: numpy.array()
            1D pixel array of device sensor
        wl_array: numpy.array()
            1D array of wavelengths from lower_wl to upper_wl
        intensity: numpy.array()
            1D measured intensity array with values between 0 and 2^16-1 (65535)
        """
        pixel_array = np.linspace(0, self.sensor_size-1, self.sensor_size)
        wl_array = np.linspace(self.lower_wl, self.upper_wl, self.sensor_size)
        intensity = np.array(DLL.USB_GetSensorData(self._handle, self._pipe, self.sensor_size, self.buffer_array)[1])

        return pixel_array, wl_array, intensity

    def close(self):
        """
        Close device.
        """
        DLL.USB_ClosePipe(self._handle)
        DLL.USB_CloseDevice(self._handle)


if __name__ == "__main__":
    spectro = MiniSpectro()