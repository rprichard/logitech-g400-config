#pragma once

#include <assert.h>
#include <stdint.h>

#include <libusb.h>

#include <string>
#include <tuple>
#include <utility>
#include <vector>

#define DEF_MOVE_ASSIGNMENT(Type)           \
    Type &operator=(Type &&other) {         \
        this->~Type();                      \
        new (this) Type(std::move(other));  \
        return *this;                       \
    }

#define DEF_COPY_ASSIGNMENT(Type)           \
    Type &operator=(const Type &other) {    \
        this->~Type();                      \
        new (this) Type(other);             \
        return *this;                       \
    }

template <typename T>
T check_libusb(T val) {
    if (val < 0) {
        throw std::string(libusb_strerror(static_cast<libusb_error>(val)));
    }
    return val;
}

// C++ wrapper for libusb_context* type.
class UsbContext {
    libusb_context *ctx_ = nullptr;
public:
    UsbContext() { check_libusb(libusb_init(&ctx_)); }
    UsbContext(UsbContext &&other) {
        ctx_ = other.ctx_;
        other.ctx_ = nullptr;
    }
    ~UsbContext() {
        if (ctx_ != nullptr) {
            libusb_exit(ctx_);
        }
    }
    DEF_MOVE_ASSIGNMENT(UsbContext)
    libusb_context *get() const {
        assert(ctx_ != nullptr && "UsbContext::get called on moved-from UsbContext object");
        return ctx_;
    }
};

class UsbDevice;
class UsbDeviceHandle;

struct UsbAddress {
    uint8_t bus;
    uint8_t dev;

    std::string to_string() const {
        return std::to_string(bus) + "." + std::to_string(dev);
    }
    bool operator==(const UsbAddress &other) { return bus == other.bus && dev == other.dev;     }
    bool operator!=(const UsbAddress &other) { return !(*this == other);                        }
};

// C++ wrapper for reference-counted libusb_device* type.
class UsbDevice {
    libusb_device *dev_ = nullptr;
public:
    UsbDevice() {}
    explicit UsbDevice(libusb_device *dev) : dev_(dev) {}
    UsbDevice(const UsbDevice &other) : dev_(other.dev_) {
        if (dev_ != nullptr) { libusb_ref_device(dev_); }
    }
    ~UsbDevice() {
        if (dev_ != nullptr) { libusb_unref_device(dev_); }
    }
    DEF_COPY_ASSIGNMENT(UsbDevice)
    libusb_device *get() const { assert(dev_ != nullptr); return dev_; }
    uint8_t bus_number() const { assert(dev_ != nullptr); return libusb_get_bus_number(dev_); }
    uint8_t dev_number() const { assert(dev_ != nullptr); return libusb_get_device_address(dev_); }
    libusb_device_descriptor desc() const {
        assert(dev_ != nullptr);
        libusb_device_descriptor ret {};
        check_libusb(libusb_get_device_descriptor(dev_, &ret));
        return ret;
    }
    UsbAddress address() const {
        assert(dev_ != nullptr);
        return UsbAddress { bus_number(), dev_number() };
    }
    std::tuple<uint16_t, uint16_t> product() const {
        assert(dev_ != nullptr);
        return std::make_tuple(desc().idVendor, desc().idProduct);
    }
    UsbDeviceHandle open() const;
};

class UsbDeviceHandle {
    libusb_device_handle *dev_handle_ = nullptr;
public:
    UsbDeviceHandle() {}
    explicit UsbDeviceHandle(libusb_device_handle *dev_handle) : dev_handle_(dev_handle) {}
    UsbDeviceHandle(UsbDeviceHandle &&other) : dev_handle_(other.dev_handle_) {
        other.dev_handle_ = nullptr;
    }
    ~UsbDeviceHandle() {
        close();
    }
    DEF_MOVE_ASSIGNMENT(UsbDeviceHandle)
    libusb_device_handle *get() const { assert(dev_handle_ != nullptr); return dev_handle_; }
    void close() {
        if (dev_handle_ != nullptr) {
            // libusb_close is void; there is no error code to check for.
            libusb_close(dev_handle_);
            dev_handle_ = nullptr;
        }
    }
    UsbDevice device() const;
};

std::vector<UsbDevice> get_device_list(const UsbContext &ctx);
