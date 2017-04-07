# logitech-g400-config

A command-line program for setting the sampling rate and DPI settings of the
Logitech G400 gaming mouse.

The program uses the hidapi library (http://www.signal11.us/oss/hidapi/) for
reading/writing the HID "feature reports" of the G400 mouse.  On Linux, this
library uses the hidraw ("HID raw") driver.  I believe hidapi also uses udev
and/or sysfs for querying the USB devices.

The tool is written in Python3 and uses a CFFI-based module to access hidapi.
The CFFI-hidapi bridge module is less active/stable, so a copy lives in this
repository.

## Prerequisites

On Ubuntu: `sudo apt-get install python3 python3-cffi libhidapi-dev libhidapi-hidraw0 libhidapi-libusb0`

## Usage

The script prints the current/final settings, and has two options for changing
the settings.  See the Python script for more detail.

```
usage: logitech-g400-config.py [-rRATE] [-dDPI]
```

## Security HOWTO

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
