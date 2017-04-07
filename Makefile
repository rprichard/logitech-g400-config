CXXFLAGS := $$(pkg-config --cflags libusb-1.0) -std=c++11 -Wall
PROG := logitech-g400-config
PREFIX := /usr/local

all : $(PROG)

$(PROG).o : usb_wrapper.h
usb_wrapper.o : usb_wrapper.h

$(PROG) : $(PROG).o usb_wrapper.o
	$(CXX) -Wall -o $@ $^ $$(pkg-config --libs libusb-1.0)

install :
	mkdir -p $(PREFIX)/bin
	install -m 755 -p -s $(PROG) $(PREFIX)/bin
