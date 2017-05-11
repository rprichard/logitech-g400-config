#!/usr/bin/python -B
#
# (Use -B to suppress __pycache__/pyc/pyo creation.  Those files can break
# things, e.g. when I run a script as sudo and get root-owned files in my home
# directory.)
#

from __future__ import absolute_import, print_function, unicode_literals

import sys
import os

FEATURE_RATE = 0x20
FEATURE_DPI  = 0x8e
RATE_LIST = [("1000", 0), ("500", 1), ("250", 2), ("125", 3)]
DPI_LIST = [("400", 3), ("800", 4), ("1800", 5), ("3600", 6), ("3600_frozen", 7)]

def usage(err=0):
    print("usage: logitech-g400-config.py [show]")
    print("  Prints the current mouse settings")
    print("")
    print("usage: logitech-g400-config.py set [options]")
    print("  -rRATE")
    print("    RATE is in Hz and is one of: 125, 250, 500, or 1000.  The Windows driver")
    print("    defaults to 500 Hz.")
    print("  -dDPI")
    print("    DPI is one of: 400, 800, 1800, 3600, or 3600_frozen.  With 3600_frozen, the")
    print("    DPI+/DPI- buttons no longer change the DPI and instead are treated as")
    print("    any other ordinary mouse button.")
    print("")
    print("usage: logitech-g400-config.py trace")
    print("    Read mouse press/release interrupts from the Logitech-proprietary G400 USB")
    print("    interface.  This interface will report DPI+/DPI- presses/releases even with")
    print("    ordinary DPI settings.  End the tracing with Ctrl-C.")
    print("")
    sys.exit(err)

def open_device():
    global hid
    import hid

    info_good = []
    info_skip = []

    device_list = hid.enumerate(0x046d, 0xc245)
    for info in device_list:
        # The mouse should have two interfaces, #0 and #1.  We need
        # interface #1.  Linux uses the `interface_number` field.  macOS uses
        # an IOKit IOService path, which includes a string like
        # "/IOUSBHostInterface@0/".
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

def map_pair_list(lst, val, reversed=False):
    for pair in lst:
        if val == pair[1 - (not reversed)]:
            return pair[1 - reversed]
    return None

def reject_cmd_subargs(subargs):
    for arg in subargs:
        if arg == "--help":
            usage(0)
        else:
            usage("error: unrecognized argument: " + arg)

def do_set_cmd(subargs):
    rate = None
    dpi = None
    for arg in subargs:
        arg_val = arg[2:]
        if arg.startswith("-r"):
            rate = map_pair_list(RATE_LIST, arg_val)
            if rate is None:
                usage("error: invalid RATE setting: " + arg_val)
        elif arg.startswith("-d"):
            dpi = map_pair_list(DPI_LIST, arg_val)
            if dpi is None:
                usage("error: invalid DPI setting: " + arg_val)
        elif arg == "--help":
            usage(0)
        else:
            usage("error: unrecognized argument: " + arg)
    dev = open_device()
    if rate is not None:
        set_var(dev, FEATURE_RATE, rate)
    if dpi is not None:
        set_var(dev, FEATURE_DPI, dpi)

def do_trace_cmd():
    dev = open_device()
    while True:
        data = bytearray(dev.read(2, 1000))
        if len(data) == 0:
            continue
        if data[0] == 0x80 and len(data) == 2:
            buttonbits = bytearray(data)[1]
            buttons = [" %s" % i for i in range(8) if (buttonbits & (1 << i)) != 0]
            print("pressed:" + "".join(buttons))
        else:
            print("unknown:" + "".join([" %02x" % x for x in data]))

def do_show_cmd():
    dev = open_device()
    rate = get_var(dev, FEATURE_RATE)
    rate = map_pair_list(RATE_LIST, rate, True) or ("unknown(%s)" % rate)
    dpi = get_var(dev, FEATURE_DPI)
    dpi = map_pair_list(DPI_LIST, dpi, True) or ("unknown(%s)" % dpi)
    print("sampling_rate: %s" % rate)
    print("dpi_level: %s" % dpi)

def main():
    cmd = sys.argv[1] if len(sys.argv) >= 2 else None
    subargs = sys.argv[2:]
    if cmd == "set":
        do_set_cmd(subargs)
    elif cmd == "trace":
        reject_cmd_subargs(subargs)
        do_trace_cmd()
    elif cmd in [None, "show"]:
        reject_cmd_subargs(subargs)
        do_show_cmd()
    elif cmd == "--help":
        usage(0)
    else:
        usage("error: unrecognized command: " + cmd)

if __name__ == "__main__":
    main()
