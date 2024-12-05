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
    .NET libraries to communicate with the device). It has been tested with C10083CA (TM-CCD series) and C9913GC (TG-cooled NIR-I)
    mini-spectrometers.

    Tested with PyMoDAQ 4.4.7 on Windows 11.

    The "specu1b.dll" driver is required and is obtained through the installation of Hamamatsu Tokuspec software. This plugin
    should work with the .dll file in its default location (C:\Program Files\Hamamatsu\TokuSpec) but make sure to change its
    path in the python wrapper "minispectro.py" in the case you place it somewhere else. This .dll file can also be found in
    the installation files of the Hamamatsu Evaluation Software originally provided with the device CD.
    """
    params = comon_parameters+[
        ## TODO for your custom plugin
        # elements to be added here as dicts in order to control your custom stage
        ############
        ]

    def ini_attributes(self):
        self.controller: MiniSpectro = None

        # TODO declare here attributes you want/need to init with a default value

        self.x_axis = None

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        ## TODO for your custom plugin
        if param.name() == "a_parameter_you've_added_in_self.params":
           self.controller.your_method_to_apply_this_param_change()


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
            self.controller = MiniSpectro()  #instantiate you driver with whatever arguments are needed

        data_x_axis = self.controller.get_sensor_data()[0]  # if possible
        self.x_axis = Axis(data=data_x_axis, label='Pixels', units='', index=0)

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
        data_tot = self.controller.get_sensor_data()[1]
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