import numpy as np
from easydict import EasyDict as edict
from pymodaq.daq_utils.daq_utils import ThreadCommand, getLineInfo, DataFromPlugins, Axis
from pymodaq.daq_viewer.utility_classes import DAQ_Viewer_base, comon_parameters
from ...hardware.Hamamatsu_camera_dom import HamamatsuCamera


class DAQ_2DViewer_Hamamatsu(DAQ_Viewer_base):
    """
    """
    params = comon_parameters + [{'title': 'Camera Model:', 'name': 'camera_model', 'type': 'list', 'value': [],
                                  'readonly': True},
                                 {'title': 'Exposure time (ms):', 'name': 'exp_time', 'type': 'int', 'value': 100,
                                  'default': 100, 'min': 0.1, 'max': 10000},
                                 {'title': 'Horizontal Size (px):', 'name': 'hsize', 'type': 'int',
                                  'value': 1920, 'min': 2, 'max': 1920},
                                 {'title': 'Vertical Size (px):', 'name': 'vsize', 'type': 'int',
                                  'value': 1920, 'min': 2, 'max': 1200},
                                 {'title': 'Horizontal Position (px):', 'name': 'hpos', 'type': 'int',
                                  'value': 0, 'min': 0, 'max': 1918},
                                 {'title': 'Vertical Position (px):', 'name': 'vpos', 'type': 'int',
                                  'value': 0, 'min': 0, 'max': 1198},
                                 {'title': 'Acquisition Mode:', 'name': 'acq_mode', 'type': 'list',
                                  'values': ['Continuous', 'Single shot'], 'value': 'Single shot'},
                                 ]
    MODE_CONTINUOUS = 1
    MODE_SINGLE_SHOT = 0

    def __init__(self, parent=None, params_state=None):
        super().__init__(parent, params_state)

        self.x_axis = None
        self.y_axis = None
        self.mode = self.MODE_SINGLE_SHOT

    def commit_settings(self, param):
        """
        """
        if param.name() == "exp_time":
            self.controller.setPropertyValue('exposure_time', param.value()/1000)
        elif param.name() == "hsize":
            self.controller.setPropertyValue('subarray_hsize', param.value())
        elif param.name() == "vsize":
            self.controller.setPropertyValue('subarray_vsize', param.value())
        elif param.name() == "hpos":
            self.controller.setPropertyValue('subarray_hpos', param.value())
        elif param.name() == "vpos":
            self.controller.setPropertyValue('subarray_vpos', param.value())
        elif param.name() == "acq_mode":
            if param.value() == "Continuous":
                self.setAcquisitionMode(self.MODE_CONTINUOUS)
            elif param.value() == "Single shot":
                self.setAcquisitionMode(self.MODE_SINGLE_SHOT)



    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object) custom object of a PyMoDAQ plugin (Slave case). None if only one detector by controller (Master case)

        Returns
        -------
        self.status (edict): with initialization status: three fields:
            * info (str)
            * controller (object) initialized controller
            *initialized: (bool): False if initialization failed otherwise True
        """

        try:
            self.status.update(edict(initialized=False, info="", x_axis=None, y_axis=None, controller=None))
            if self.settings.child(('controller_status')).value() == "Slave":
                if controller is None:
                    raise Exception('no controller has been defined externally while this detector is a slave one')
                else:
                    self.controller = controller
            else:
                self.controller = HamamatsuCamera(0)  # any object that will control the stages
                self.controller.initCamera()
                self.controller.setPropertyValue("readout_speed", 1)
                self.controller.setPropertyValue("defect_correct_mode", 1)
                self.setAcquisitionMode(self.MODE_SINGLE_SHOT)

                self.settings.child("camera_model").setValue(
                    self.controller.getModelInfo(0).decode()
                )
                self.settings.child("exp_time").setValue(
                    float(self.controller.getPropertyValue('exposure_time')[0] * 1000)
                )
                self.settings.child("hsize").setValue(
                    int(self.controller.getPropertyValue('subarray_hsize')[0])
                )
                self.settings.child("vsize").setValue(
                    int(self.controller.getPropertyValue('subarray_vsize')[0])
                )
                self.settings.child("hpos").setValue(
                    int(self.controller.getPropertyValue('subarray_hpos')[0])
                )
                self.settings.child("vpos").setValue(
                    int(self.controller.getPropertyValue('subarray_vpos')[0])
                )


            # get the x_axis
            self.x_axis = self.get_xaxis()
            self.y_axis = self.get_yaxis()
            self.status.x_axis = self.x_axis
            self.status.y_axis = self.y_axis

            self.status.info = "Initialized XY axes"
            self.status.initialized = True
            self.status.controller = self.controller
            return self.status

        except Exception as e:
            self.emit_status(ThreadCommand('Update_Status', [getLineInfo() + str(e), 'log']))
            self.status.info = getLineInfo() + str(e)
            self.status.initialized = False
            return self.status

    def get_xaxis(self):
        """
            Obtain the horizontal axis of the image.
            Returns
            -------
            1D numpy array
                Contains a vector of integer corresponding to the horizontal camera pixels.
        """
        if self.controller is not None:
            Nx = self.settings.child('hsize').value()
            self.x_axis = Axis(data=np.linspace(0, Nx - 1, Nx, dtype=np.int), label='Pixels')

            self.emit_x_axis()
        else:
            raise(Exception('controller not defined'))
        return self.x_axis

    def get_yaxis(self):
        """
            Obtain the horizontal axis of the image.
            Returns
            -------
            1D numpy array
                Contains a vector of integer corresponding to the horizontal camera pixels.
        """
        if self.controller is not None:
            Ny = self.settings.child('vsize').value()
            self.y_axis = Axis(data=np.linspace(0, Ny - 1, Ny, dtype=np.int), label='Pixels')

            self.emit_y_axis()
        else:
            raise(Exception('controller not defined'))
        return self.x_axis

    def setAcquisitionMode(self, mode):
        """
        Set the readout mode of the camera: Single or continuous.
        Parameters
        mode : int
        One of self.MODE_CONTINUOUS, self.MODE_SINGLE_SHOT
        """
        self.mode = mode
        if mode == self.MODE_CONTINUOUS:
            self.controller.settrigger(1)
            self.controller.setmode(self.controller.CAPTUREMODE_SEQUENCE)
        elif mode == self.MODE_SINGLE_SHOT:
            self.controller.settrigger(1)
            self.controller.setmode(self.controller.CAPTUREMODE_SNAP)
        return self.getAcquisitionMode()

    def getAcquisitionMode(self):
        """Returns the acquisition mode, either continuous or single shot.
        """
        return self.mode

    def close(self):
        """
        Terminate the communication protocol
        """
        self.controller.shutdown()

    def grab_data(self, Naverage=1, **kwargs):
        """

        Parameters
        ----------
        Naverage: (int) Number of hardware averaging
        kwargs: (dict) of others optionals arguments
        """

        try:
            # if self.getAcquisitionMode() == self.MODE_CONTINUOUS:
                # self.controller.startAcquisition()
                # data = self.controller.getFrames()

            # elif self.getAcquisitionMode() == self.MODE_SINGLE_SHOT:

            self.controller.startAcquisition()
            data = self.controller.getFrames()
            self.controller.stopAcquisition()

            im_data = data[0][0]
            im = im_data.getData()
            im2 = [np.reshape(im, (data[1][1], data[1][0]))]
            self.data_grabed_signal.emit([DataFromPlugins(name='Camera Image', data=im2,
                                                              dim='Data2D', labels=['camera_image'])])

        except Exception as e:
            self.emit_status(ThreadCommand('Update_Status', [getLineInfo() + str(e), 'log']))
            self.status.info = getLineInfo() + str(e)
            return self.status
        # finally:
        #     # prevents unending acquisition if there is an error in the 'try' block
        #     self.controller.stopAcquisition()

    def stop(self):
        self.controller.stopAcquisition()
        return
