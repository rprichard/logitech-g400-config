#!/usr/bin/python -B
#
# (Use -B to suppress __pycache__/pyc/pyo creation.  Those files can break
# things, e.g. when I run a script as sudo and get root-owned files in my home
# directory.)
#

from __future__ import absolute_import, print_function, unicode_literals

import sys
import os

import hid

FEATURE_RATE = 0x20
FEATURE_DPI  = 0x8e

def usage(err=0):
    print("usage: logitech-g400-config.py [-rRATE] [-dDPI]")
    print("")
    print("  RATE is in Hz and is one of: 125, 250, 500, or 1000.  The Windows driver")
    print("  defaults to 500 Hz.")
    print("")
    print("  DPI is an integer between 3 and 7 inclusive.  The Windows driver defaults to")
    print("  four DPI settings, each of which configures a different DPI level:")
    print("  400=>3, 800=>4, 1800=>5, 3600=>6.  It never uses 7, but the device seems OK with")
    print("  that value.")
    print("")
    sys.exit(err)

def open_device():
    info_good = []
    info_skip = []

    device_list = hid.enumerate(0x046d, 0xc245)
    for info in device_list:
        # The mouse should have two interfaces, #0 and #1.  We need interface #1.
        # Linux hidraw uses `interface_number`.
        # OSX uses a IOService paths, which includes a string like "/IOUSBHostInterface@0/".
        if b"/IOUSBHostInterface@0/" in info["path"] or info["interface_number"] == 0:
            info_skip.append(info)
        elif b"/IOUSBHostInterface@1/" in info["path"] or info["interface_number"] == 1:
            info_good.append(info)
        else:
            print("unexpected G400 USB device: " + info["path"])

    if len(info_good) == 1:
        return hid.Device(path=info_good[0]["path"])
    elif len(info_good) != len(info_skip):
        sys.exit("error: unexpected USB interfaces while querying for a G400 mouse")
    elif len(info_good) == 0:
        sys.exit("error: no G400 mouse attached")
    else:
        sys.exit("error: multiple G400 mice detected -- this script only supports one")

def set_var(dev, var, val):
    dev.send_feature_report(bytes(bytearray((var, val))))

def get_var(dev, var):
    return bytearray(dev.get_feature_report(var, 2))[1]

def main():
    dev = open_device()
    for arg in sys.argv[1:]:
        {
            "-r125":  lambda: set_var(dev, FEATURE_RATE, 3),
            "-r250":  lambda: set_var(dev, FEATURE_RATE, 2),
            "-r500":  lambda: set_var(dev, FEATURE_RATE, 1),
            "-r1000": lambda: set_var(dev, FEATURE_RATE, 0),
            "-d3":    lambda: set_var(dev, FEATURE_DPI, 3),
            "-d4":    lambda: set_var(dev, FEATURE_DPI, 4),
            "-d5":    lambda: set_var(dev, FEATURE_DPI, 5),
            "-d6":    lambda: set_var(dev, FEATURE_DPI, 6),
            "-d7":    lambda: set_var(dev, FEATURE_DPI, 7),
            "--help": lambda: usage(),
        }.get(arg, lambda: usage("error: unrecognized argument: " + arg))()

    rate = get_var(dev, FEATURE_RATE)
    rate = {
        3: "125",
        2: "250",
        1: "500",
        0: "1000",
    }.get(rate, "unknown(%s)" % rate)

    print("sampling_rate: %s" % rate)
    print("dpi_level: %s" % get_var(dev, FEATURE_DPI))

main()
