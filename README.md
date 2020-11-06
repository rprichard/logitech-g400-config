# logitech-g400-config

A command-line program for setting the sampling rate and DPI settings of the
Logitech G400 gaming mouse.

The program uses the hidapi library (http://www.signal11.us/oss/hidapi/) for
reading/writing the HID "feature reports" of the G400 mouse.

The tool is written in Python (either 2.7 or 3.x) and uses ctypes to access the
native hidapi library.

NOTE: This program works with the G400 mouse, *not* the G400s mouse.  See
https://github.com/rprichard/logitech-g400-config/issues/3 for some details,
or https://tnsp.org/~ccr/files/g400s_hack.c for something that works with the
G400s.

## Prerequisites

### Ubuntu

`sudo apt-get install libhidapi-libusb0`

See the security HOWTO for instructions on making the USB devices accessible
to this script without needing root.

### macOS

Follow instructions here: https://github.com/libusb/hidapi

## Usage

```
usage: logitech-g400-config.py [show]
  Prints the current mouse settings

usage: logitech-g400-config.py set [options]
  -rRATE
    RATE is in Hz and is one of: 125, 250, 500, or 1000.  The Windows driver
    defaults to 500 Hz.
  -dDPI
    DPI is one of: 400, 800, 1800, 3600, or 3600_frozen.  With 3600_frozen, the
    DPI+/DPI- buttons no longer change the DPI and instead are treated as
    any other ordinary mouse button.

usage: logitech-g400-config.py trace
    Read mouse press/release interrupts from the Logitech-proprietary G400 USB
    interface.  This interface will report DPI+/DPI- presses/releases even with
    ordinary DPI settings.  End the tracing with Ctrl-C.
```

## Linux Security HOWTO

Add a file, `/etc/udev/rules.d/10-logitech-g400-config.rules`, with contents:
```
SUBSYSTEM=="usb", ATTRS{idVendor}=="046d", ATTRS{idProduct}=="c245", MODE:="660", GROUP="plugdev"
```

Run `sudo udevadm control --reload-rules`.

Add your user account to the `plugdev` group (this has no effect if you're already in the group):
```
$ sudo usermod -a -G plugdev $USER
$ groups
rprichard adm cdrom sudo dip plugdev lpadmin sambashare vboxusers wireshark
```
Log out and back in to make sure group membership takes effect.

Unplug the mouse and plug it back in.  The udev rule only applies when the
operating system initializes a device.
