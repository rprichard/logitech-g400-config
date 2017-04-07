#include "usb_wrapper.h"

#include <stdlib.h>

#include <algorithm>

UsbDeviceHandle UsbDevice::open() const {
    libusb_device_handle *dev_handle = nullptr;
    check_libusb(libusb_open(get(), &dev_handle));
    return UsbDeviceHandle { dev_handle };
}

UsbDevice UsbDeviceHandle::device() const {
    libusb_device *dev = libusb_get_device(get());
    return UsbDevice { libusb_ref_device(dev) };
}

std::vector<UsbDevice> get_device_list(const UsbContext &ctx) {
    std::vector<UsbDevice> ret;
    libusb_device **dev_list = nullptr;
    auto count = libusb_get_device_list(ctx.get(), &dev_list);
    check_libusb(count);
    for (decltype(count) i = 0; i < count; ++i) {
        ret.push_back(UsbDevice { dev_list[i] });
    }
    libusb_free_device_list(dev_list, 0);
    std::sort(ret.begin(), ret.end(), [](UsbDevice &x, UsbDevice &y) {
        return (x.bus_number() * 0x10000 + x.dev_number()) <
               (y.bus_number() * 0x10000 + y.dev_number());
    });
    return ret;
}
