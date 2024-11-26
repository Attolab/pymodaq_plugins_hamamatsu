# import pyvisa
# import pylablib as pll
# import logging

# logging.basicConfig(level=logging.DEBUG)

# rm = pyvisa.ResourceManager()


# print(rm.list_resources())

import usb.core
import usb.util

# find our device
# while dev is None:
#     dev = usb.core.find()

# print(dev)

# vid, pid = 0x0bda, 0x5558  # ?
# vid, pid = 0x413c, 0x301a  # Dell USB Optical Mouse
vid, pid = 0x0661, 0x2909   # Hamamatsu Mini-spectrometer C10083CA


dev = usb.core.find(idVendor=vid, idProduct=pid)   # idVendor=0x0661, idProduct=0x2909

print(dev)
# was it found?
# if dev is None:
#     raise ValueError('Device not found')

# for cfg in dev:
#     for intf in cfg:
#         for ep in intf:
#             print(f"Endpoint Address: {hex(ep.bEndpointAddress)}, Direction: {'IN' if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN else 'OUT'}")


# set the active configuration. With no arguments, the first
# configuration will be the active one
# dev.set_configuration()

# # get an endpoint instance
# cfg = dev.get_active_configuration()
# intf = cfg[(0,0)]

# ep = usb.util.find_descriptor(
#     intf,
#     # match the first OUT endpoint
#     custom_match = \
#     lambda e: \
#         usb.util.endpoint_direction(e.bEndpointAddress) == \
#         usb.util.ENDPOINT_OUT)

# assert ep is not None

# # write the data
# ep.write('test')