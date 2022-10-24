pymodaq_plugins_hamamatsu (Hamamatsu)
#############################################

PyMoDAQ plugin for capturing images with Hamamatsu cameras.
The plugin is based on `this script`__.
Tested with a C11440-36U on PyMoDAQ 3.5.6. The plugin should work on other cameras, see `DCAM-API`__ for compatibility information.

__ https://github.com/ZhuangLab/storm-control/blob/master/storm_control/sc_hardware/hamamatsu/hamamatsu_camera.py
__ https://dcam-api.com/downloads/

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
===============

The acquisition frame rate is lower than what is obtained with the constructor software. On the camera used for testing, the frame rate is limited to a few FPS in full frame. This is because so far, images are only captured in 'snap' mode. A 'stream' mode looks available, and could be implemented in the future.
