logitech-g400-config : logitech-g400-config.cc usb_wrapper.cc usb_wrapper.h
	g++ -Wall -std=c++11 -Os logitech-g400-config.cc usb_wrapper.cc -o logitech-g400-config $$(pkg-config --cflags --libs libusb-1.0)

install : logitech-g400-config
	echo INSTALLING
