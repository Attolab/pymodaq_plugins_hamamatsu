pymodaq_plugins_hamamatsu (Hamamatsu)
#############################################

PyMoDAQ plugin for capturing images with Hamamatsu cameras.
The plugin is based on [this script](https://github.com/ZhuangLab/storm-control/blob/master/storm_control/sc_hardware/hamamatsu/hamamatsu_camera.py).
Tested with a C11440-36U on PyMoDAQ 3.5.6. Should work on other cameras, see [https://dcam-api.com/downloads/](https://dcam-api.com/downloads/) for compatibility information.
Authors
=======

* Romain Géneaux (romain.geneaux@cea.fr)


Instruments
===========

Below is the list of instruments included in this plugin

Viewers
+++++++++

* **Hamamatsu** All cameras using the DCAM-API.

Known issues
++++++++++++++++++++++++++++++++++++++++++++++++++

The acquisition frame rate is lower than what is obtained with the constructor software. On our camera the frame rate is limited to a few FPS in full frame. This might be improved by implementing the grab_data differently, perhaps using this available package (https://pypi.org/project/hamamatsu/).