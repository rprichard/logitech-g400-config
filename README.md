# logitech-g400-config

A command-line program for setting the sampling rate and DPI settings of the
Logitech G400 gaming mouse.

The program depends only on libusb-1.0 and C++11.  It's tested on Linux, where
the program uses libusb to detach and reattach the Linux kernel driver.  In
principle, the program could run on Windows and OS X, too, if the OS doesn't
block libusb from accessing the device.

Run the program with --help for usage details.

The Makefile finds libusb-1.0 using `pkg-config libusb-1.0`.  On Ubuntu,
install the package `libusb-1.0-0-dev` (and probably `g++` and `make` too).
