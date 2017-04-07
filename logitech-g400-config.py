#!/usr/bin/python -B
#
# (Use -B to suppress __pycache__/pyc/pyo creation.  Those files can break
# things, e.g. when I run a script as sudo and get root-owned files in my home
# directory.)
#

import argparse
import sys
import os
sys.path.insert(1, os.path.join(os.path.dirname(os.path.realpath(__file__)), "hidapi_cffi"))
import hidapi

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

def enum_hidapi_mice():
    for info in hidapi.enumerate(0x046d, 0xc245):
        if info.interface_number == 1:
            yield info

def open_device():
    info = list(enum_hidapi_mice())
    if len(info) == 0:
        sys.exit("No G400 attached")
    elif len(info) > 1:
        sys.exit("Only one G400 supported")
    else:
        info = info[0]
    return hidapi.Device(info)

def bytechr(val):
    return chr(val) if str is bytes else bytes([val])

def set_var(dev, var, val):
    dev.send_feature_report(bytechr(val), bytechr(var))

def get_var(dev, var):
    return ord(dev.get_feature_report(bytechr(var), 1))

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
