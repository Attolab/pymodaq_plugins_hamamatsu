import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, Axis, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter

from pymodaq_plugins_hamamatsu.hardware.minispectro import MiniSpectro


class DAQ_1DViewer_MiniSpectro(DAQ_Viewer_base):
    """ Instrument plugin class for Hamamatsu USB Mini-spectrometers.
    
    This object inherits all functionalities to communicate with PyMoDAQ's DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

    This plugin should work with Hamamatsu mini-spectrometers connected with USB on Windows machines only (Python wrapper uses
    .NET libraries to communicate with the device). It has been tested with C10083CA (TM-CCD) and C9913GC (TG-cooled NIR-I)
    mini-spectrometers.

    Tested with PyMoDAQ 4.4.7 on Windows 11.

    The "specu1b.dll" driver is required and is obtained through the installation of Hamamatsu Tokuspec software. This plugin
    should work with the .dll file in its default location (C:\Program Files\Hamamatsu\TokuSpec) but make sure to change its
    path in the python wrapper "minispectro.py" in the case you place it somewhere else. This .dll file can also be found in
    the installation files of the Hamamatsu Evaluation Software originally provided with the device CD.
    """
    params = comon_parameters + [
        {'title': 'Device ID', 'name': 'unit_id', 'type': 'str', 'value': '', 'readonly': True},
        {'title': 'Sensor name', 'name': 'sensor_name', 'type': 'str', 'value': '', 'readonly': True},
        {'title': 'Serial number', 'name': 'serial_number', 'type': 'str', 'value': '', 'readonly': True},
        {'title': 'Lower λ', 'name': 'lower_wl', 'type': 'int', 'value': 0, 'suffix': 'nm', 'readonly': True},
        {'title': 'Upper λ', 'name': 'upper_wl', 'type': 'int', 'value': 0, 'suffix': 'nm', 'readonly': True},
        {'title': 'Pixels', 'name': 'pixel_nb', 'type': 'str', 'value': '', 'readonly': True},
        {'title': 'Trigger mode:', 'name': 'trig_mode', 'type': 'list',
                        'limits': ['Internal', 'External (edge)', 'External (gate)'], 'value': 'Internal'},
        {'title': 'Trigger edge:', 'name': 'trig_edge', 'type': 'list',
                        'limits': ['Rising edge', 'Falling edge'], 'value': 'Rising edge'},
        {'title': 'Gain mode', 'name': 'gain', 'type': 'list', 'limits': ['Low gain', 'High gain', 'None'], 'value': ''},
        {'title': 'Integration time', 'name': 'integration_time', 'type': 'int', 'value': 100, 'min': 5, 'max': 10000,
                        'siPrefix': True, 'suffix': 'ms', 'tip': 'MIN = 5 ms, MAX = 10000 ms'}
        ]

    def ini_attributes(self):
        self.controller: MiniSpectro = None
        self.x_axis = None

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == "integration_time":
            self.controller.set_parameter(integ_time=int(self.settings['integration_time']*1e3))  # Convert from ms to µs
        if param.name() == 'trig_mode':
            if param.value() == 'Internal':
                self.controller.set_parameter(trigger_mode=0x00)
            elif param.value() == 'External (edge)':
                self.controller.set_parameter(trigger_mode=0x01)
            elif param.value() == 'External (gate)':
                self.controller.set_parameter(trigger_mode=0x02)
        if param.name() == 'trig_edge':
            if param.value() == 'Rising edge':
                self.controller.set_parameter(trigger_mode=0x00)
            elif param.value() == 'Falling edge':
                self.controller.set_parameter(trigger_mode=0x01)


    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """
        self.ini_detector_init(slave_controller=controller)

        if self.is_master:
            self.controller = MiniSpectro()

        self.settings.child('unit_id').setValue(self.controller.unit_id)
        self.settings.child('sensor_name').setValue(self.controller.sensor_name)
        self.settings.child('serial_number').setValue(self.controller.serial_number)
        self.settings.child('lower_wl').setValue(self.controller.lower_wl)
        self.settings.child('upper_wl').setValue(self.controller.upper_wl)
        self.settings.child('pixel_nb').setValue(self.controller.sensor_size)

        # Check if device handles external trigger
        if '0xff' in self.controller.trigger_edge:
            self.settings.child('trig_mode').setValue('Internal')
            self.settings.child('trig_mode').setReadonly()
        
        if '0xff' in self.controller.gain:
            self.settings.child('gain').setValue('None')
            self.settings.child('gain').setReadonly()

        data_x_axis = self.controller.get_sensor_data()[1]*1e-9
        self.x_axis = Axis(data=data_x_axis, label='Wavelength', units='m', index=0)

        # Initialize viewers panel with the future type of data
        self.dte_signal_temp.emit(DataToExport(name='MiniSpectro',
                                               data=[DataFromPlugins(name='Mini-spectrometer',
                                                                     data=[np.array([0 for _ in range(self.controller.sensor_size)])],
                                                                     dim='Data1D', labels=['Spectrometer'],
                                                                     axes=[self.x_axis])]))

        info = "Whatever info you want to log"
        initialized = True
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        if self.controller is not None:
            self.controller.close()

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        # Synchrone version (blocking function)
        data_tot = self.controller.get_sensor_data()[2]
        self.dte_signal.emit(DataToExport(name='MiniSpectro',
                                          data=[DataFromPlugins(name='Mini-spectrometer',
                                                                data=data_tot,
                                                                dim='Data1D',
                                                                labels=['Spectrometer'],
                                                                axes=[self.x_axis])]))

    def stop(self):
        """
        Stop the current grab by emitting a status. Works by stopping to call get_sensor_data() function)
        """
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))


if __name__ == '__main__':
    main(__file__)