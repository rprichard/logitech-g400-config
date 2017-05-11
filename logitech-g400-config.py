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

VIDPID_G400  = (0x046d, 0xc245)
VIDPID_G400s = (0x046d, 0xc24c)

DPI_LIST_G400 = [
    ("400", 3),
    ("800", 4),
    ("1800", 5),
    ("3600", 6),
    ("3600_locked", 7),
]

DPI_LIST_G400s = [
    ("400",         3),
    ("800",         4),
    ("1800",        5),
    ("3600",        6),
    ("400_locked",  0x83),
    ("800_locked",  0x84),
    ("1800_locked", 0x85),
    ("3600_locked", 0x86),
]

def usage(err=0):
    print(
"""usage: logitech-g400-config.py [show]
  Prints the current mouse settings

usage: logitech-g400-config.py set [options]
  -rRATE
    RATE is in Hz and is one of: 125, 250, 500, or 1000.  The Windows driver
    defaults to 500 Hz.
  -dDPI
    DPI is one of:
        400             [G400 and G400s]
        800             [G400 and G400s]
        1800            [G400 and G400s]
        3600            [G400 and G400s]
        400_locked      [G400s only]
        800_locked      [G400s only]
        1800_locked     [G400s only]
        3600_locked     [G400 and G400s]
    With the "locked" settings, the DPI+/DPI- buttons no longer change the DPI
    and instead are treated as any other ordinary mouse button.

usage: logitech-g400-config.py trace
    Read mouse press/release interrupts from the Logitech-proprietary USB
    interface.  This interface will report DPI+/DPI- presses/releases even with
    ordinary DPI settings.  End the tracing with Ctrl-C.
""")
    sys.exit(err)

def info_vidpid(info):
    return (info["vendor_id"], info["product_id"])

class Device:
    pass

def open_device():
    global hid
    import hid

    info_good = []
    info_skip = []

    for info in hid.enumerate():
        if info_vidpid(info) not in set({ VIDPID_G400, VIDPID_G400s }):
            continue
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
        info = info_good[0]
        vidpid = info_vidpid(info)
        ret = Device()
        ret.hid_device = hid.Device(path=info["path"])
        ret.model = { VIDPID_G400:"G400", VIDPID_G400s:"G400s" }[vidpid]
        ret.dpi_list = { VIDPID_G400:DPI_LIST_G400, VIDPID_G400s:DPI_LIST_G400s }[vidpid]
        return ret
    elif len(info_good) != len(info_skip):
        sys.exit("error: unexpected USB interfaces while querying for a G400 mouse")
    elif len(info_good) == 0:
        sys.exit("error: no G400 mouse attached")
    else:
        sys.exit("error: multiple G400 mice detected -- this script only supports one")

def set_var(hid_device, var, val):
    hid_device.send_feature_report(bytes(bytearray((var, val))))

def get_var(hid_device, var):
    return bytearray(hid_device.get_feature_report(var, 2))[1]

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
    rate_str = None
    dpi_str = None
    for arg in subargs:
        arg_val = arg[2:]
        if arg.startswith("-r"):
            rate_str = arg_val
        elif arg.startswith("-d"):
            dpi_str = arg_val
        elif arg == "--help":
            usage(0)
        else:
            usage("error: unrecognized argument: " + arg)

    dev = open_device()
    rate_val = None
    dpi_val = None

    if rate_str is not None:
        rate_val = map_pair_list(RATE_LIST, rate_str)
        if rate_val is None:
            usage("error: invalid RATE setting: " + rate_str)

    if dpi_str is not None:
        dpi_val = map_pair_list(dev.dpi_list, dpi_str)
        if dpi_val is None:
            usage("error: invalid DPI setting: " + dpi_str)

    if rate_val is not None:
        set_var(dev.hid_device, FEATURE_RATE, rate_val)
    if dpi_val is not None:
        set_var(dev.hid_device, FEATURE_DPI, dpi_val)

def do_trace_cmd():
    dev = open_device()
    while True:
        data = bytearray(dev.hid_device.read(2, 1000))
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
    rate = get_var(dev.hid_device, FEATURE_RATE)
    rate = map_pair_list(RATE_LIST, rate, True) or ("unknown(%s)" % rate)
    dpi = get_var(dev.hid_device, FEATURE_DPI)
    dpi = map_pair_list(dev.dpi_list, dpi, True) or ("unknown(%s)" % dpi)
    print("model: %s" % dev.model)
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
