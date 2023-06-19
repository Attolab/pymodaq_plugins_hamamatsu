pymodaq_plugins_hamamatsu (Hamamatsu)
#############################################

PyMoDAQ plugin for capturing images with Hamamatsu cameras.
The plugin is based on `pylablib`__. Here are the installation instructions as explained on `the library page`__:

  These cameras require ``dcamapi.dll``, which is installed with most of Hamamatsu software (such as HoKaWo or HiPic), as well as with the freely available `DCAM API <https://dcam-api.com/>`__, which also includes all the necessary drivers. Keep in mind, that you also need to install the drivers for required corresponding camera type (USB, Ethernet, IEEE 1394). These drivers are in the same installer, but need to be installed separately. You should also pay attention to the cameras supported by the given DCAM driver version, since newer version do not support older cameras (e.g., ImageEM C9100 cameras are only supported up to version 15). After installation, the DLL is automatically added to the ``System32`` folder, where pylablib looks for it by default.

Currently this plugin will look for the DLL in its default location. Using another location is not implemented yet, but would be straightforward.

Tested with a C11440-36U on PyMoDAQ 3.6.13 on Windows, with DCAM-API v23.6.6644. Achieving frame rates up to 64 FPS in full frame, 200 FPS by restricting the region of interest.
The plugin should work on other cameras, see `DCAM-API`__ for compatibility information.

__ https://pylablib.readthedocs.io/en/latest/
__ https://pylablib.readthedocs.io/en/latest/devices/DCAM.html
__ https://dcam-api.com/downloads/

Authors
=======

* Romain Géneaux (romain.geneaux@cea.fr)


Instruments
===========

Below is the list of instruments included in this plugin

Viewer2D
++++++++

* **Hamamatsu** All cameras using the DCAM-API. Hardware ROI (region of interest) and binning (1x or 2x) are supported. To use ROIs, click on "Show/Hide ROI selection area" in the viewer panel (icon with dashed rectangle). Position the rectangle as you wish, either with mouse or by entering coordinates, then click "Update ROI" button.