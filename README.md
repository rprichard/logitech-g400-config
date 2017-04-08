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
clang -Inative/hidapi native/mac/hid.c -o libhidapi.dylib -arch i386 -arch x86_64 -Os -shared -framework CoreFoundation -framework IOKit
cp libhidapi.dylib /usr/local/lib
```
(The dylib can be placed anywhere so long as `hid/__init__.py` can find it.)
Unlike Linux, macOS apparently requires no security adjustments.

## Usage

The script prints the current/final settings, and has two options for changing
the settings.  See the Python script for more detail.

```
usage: logitech-g400-config.py [-rRATE] [-dDPI]
```

## Linux Security HOWTO

Add a file, `/etc/udev/rules.d/10-logitech-g400-config.rules`, with contents:
```
SUBSYSTEM=="hidraw", MODE:="660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="046d", ATTRS{idProduct}=="c245", MODE:="660", GROUP="plugdev"
```

Run `sudo udevadm control --reload-rules`.

Unplug/replug mouse, then verify that these files are plugdev now:
```
$ ls -l /dev/hidraw*
crw-rw---- 1 root plugdev 248, 3 Apr  7 16:02 /dev/hidraw3
crw-rw---- 1 root plugdev 248, 4 Apr  7 16:02 /dev/hidraw4
```
Add your user account to the `plugdev` group (this has no effect if you're already in the group):
```
$ sudo usermod -a -G plugdev $USER
$ groups
rprichard adm cdrom sudo dip plugdev lpadmin sambashare vboxusers wireshark
```
Log out and back in to make sure group membership takes effect.
