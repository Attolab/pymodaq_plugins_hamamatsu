pymodaq_plugins_hamamatsu (Hamamatsu)
#############################################

PyMoDAQ plugin for Hamamatsu instruments. Currently supports Hamamatsu cameras using
DCAM API with PyLabLib (Viewer2D) and Hamamatsu minispectrometers using .NET driver
with pythonnet (Viewer1D).


Authors
=======

* Romain Géneaux (romain.geneaux@cea.fr)
* Bastien Bégon (bastien.begon@crpp.cnrs.fr)

Instruments
===========

Below is the list of instruments included in this plugin

Viewer1D
++++++++

* **Mini-spectrometers**: USB spectrometers from the Hamamatsu Mini-spectrometers series.

Viewer2D
++++++++

* **Cameras using DCAM-API**: Hardware ROI (region of interest) and binning (1x or 2x)
  are supported. To use ROIs, click on "Show/Hide ROI selection area" in the viewer panel
  (icon with dashed rectangle). Position the rectangle as you wish, either with mouse or 
  by entering coordinates, then click "Update ROI" button.

Installation instructions
=========================

Mini-spectrometers
++++++++++++++++++

The `specu1b.dll` driver (.NET) file only is necessary for interfacing mini-spectrometers. It
can be obtained either by installing `Tokuspec`__ software (default driver location is in
``C:\Program Files\Hamamatsu\TokuSpec``) or from the originally supplied device CD.

The default driver location is used in this plugin, make sure to update its path in the
python wrapper ``hardware/minispectro.py`` if you store it somewhere else.

Tested with C10083CA (TM-CCD) and C9913GC (TG-cooled NIR-I) mini-spectrometers with PyMoDAQ 4.4.7 on Windows 11.

__ https://hamamatsu-software.de/index.php?l=int&u=tokuspec

Cameras
+++++++

This part of the plugin is based on `pylablib`__. Here are the installation instructions
as explained on `the library page`__:

  These cameras require ``dcamapi.dll``, which is installed with most of Hamamatsu
  software (such as HoKaWo or HiPic), as well as with the freely available DCAM API
  <https://dcam-api.com/>`__, which also includes all the necessary drivers. Keep
  in mind, that you also need to install the drivers for required corresponding
  camera type (USB, Ethernet, IEEE 1394). These drivers are in the same installer,
  but need to be installed separately. You should also pay attention to the cameras
  supported by the given DCAM driver version, since newer version do not support
  older cameras (e.g., ImageEM C9100 cameras are only supported up to version 15).
  After installation, the DLL is automatically added to the ``System32`` folder,
  where pylablib looks for it by default.

Currently this plugin will look for the DLL in its default location. Using another
location is not implemented yet, but would be straightforward.

Tested with a C11440-36U on PyMoDAQ 3.6.13 on Windows, with DCAM-API v23.6.6644. Achieving 
frame rates up to 64 FPS in full frame, 200 FPS by restricting the region of interest.
The plugin should work on other cameras, see `DCAM-API`__ for compatibility information.

__ https://pylablib.readthedocs.io/en/latest/
__ https://pylablib.readthedocs.io/en/latest/devices/DCAM.html
__ https://www.hamamatsu.com/eu/en/product/cameras/software/driver-software.html



