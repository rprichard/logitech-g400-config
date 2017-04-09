# logitech-g400-config

A command-line program for setting the sampling rate and DPI settings of the
Logitech G400 gaming mouse.

The program uses the hidapi library (http://www.signal11.us/oss/hidapi/) for
reading/writing the HID "feature reports" of the G400 mouse.

The tool is written in Python (either 2.7 or 3.x) and uses ctypes to access the
native hidapi library.

## Prerequisites

### Ubuntu

`sudo apt-get install libhidapi-dev libhidapi-libusb0`

See the security HOWTO for instructions on making the USB devices accessible
to this script without needing root.

### macOS

Build `libhidapi.dylib` with this command:
```
clang -Inative/hidapi native/mac/hid.c -o libhidapi.dylib \
    -arch i386 -arch x86_64 \
    -Os -shared \
    -framework CoreFoundation -framework IOKit
```
Unlike Linux, macOS apparently requires no security configuration.

## Usage

The script prints the current/final settings, and has two options for changing
the settings.  See the Python script for more detail.

```
usage: logitech-g400-config.py [-rRATE] [-dDPI]
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
