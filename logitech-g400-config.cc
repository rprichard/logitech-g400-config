#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include <libusb.h>

#include <array>
#include <iostream>
#include <list>
#include <string>
#include <tuple>
#include <vector>

#include "usb_wrapper.h"

const char *const kVersion = "0.1";
const uint16_t kMouseVendorId = 0x046d;
const uint16_t kMouseProductId = 0xc245;
const std::tuple<uint16_t, uint16_t> kMouseProduct { kMouseVendorId, kMouseProductId };
const char *const kMouseProductName = "Logitech Gaming Mouse G400";

static std::vector<UsbDevice> get_mouse_devices(UsbContext &ctx) {
    std::vector<UsbDevice> ret;
    for (const auto &dev : get_device_list(ctx)) {
        if (dev.product() == kMouseProduct) {
            ret.push_back(dev);
        }
    }
    return ret;
}

static UsbDevice find_device_by_address(UsbContext &ctx, UsbAddress address) {
    for (const auto &dev : get_device_list(ctx)) {
        if (dev.address() != address) {
            continue;
        }
        if (dev.product() != kMouseProduct) {
            throw "device " + address.to_string() + " is not a " + kMouseProductName;
        }
        return dev;
    }
    throw "could not find device " + address.to_string();
}

static UsbDevice find_sole_device(UsbContext &ctx) {
    const auto dev_list = get_mouse_devices(ctx);
    if (dev_list.size() == 0) {
        throw std::string("could not find a ") + kMouseProductName + " device";
    } else if (dev_list.size() == 1) {
        return dev_list[0];
    } else {
        throw std::string("multiple ") + kMouseProductName + " devices exist: specify --address BUS.DEV";
    }
}

static bool match_strval_arg(const char *match, std::list<std::string> &arg_list, std::string &out) {
    if (arg_list.empty()) { return false; }
    const auto &front = arg_list.front();
    if (front == match && arg_list.size() >= 2) {
        arg_list.pop_front();
        out = std::move(arg_list.front());
        arg_list.pop_front();
        return true;
    }
    const auto match_len = strlen(match);
    if (front.size() <= match_len) {
        return false;
    }
    if (!front.compare(0, match_len, match) && front[match_len] == '=') {
        out = front.substr(match_len + 1);
        arg_list.pop_front();
        return true;
    }
    return false;
}

static bool parse_address(const std::string &address, UsbAddress &out) {
    char *endptr = nullptr;
    errno = 0;
    const long bus = strtol(address.c_str(), &endptr, 10);
    if (errno != 0 || endptr == nullptr || *endptr != '.' || bus < 0 || bus > 255) {
        return false;
    }
    const long dev = strtol(endptr + 1, &endptr, 10);
    if (errno != 0 || endptr == nullptr || *endptr != '\0' || dev < 0 || dev > 255) {
        return false;
    }
    out.bus = bus;
    out.dev = dev;
    return true;
}

enum SampleRate {
    SampleRateUnset = -1,
    SampleRate1000 = 0,
    SampleRate500 = 1,
    SampleRate250 = 2,
    SampleRate125 = 3,
};

static void show_usage() {
    std::cout << "usage:\n";
    std::cout << "  logitech-g400-config list\n";
    std::cout << "    Lists the connected BUS.DEV devices that match the VID:PID of the\n";
    std::cout << "    " << kMouseProductName << ".\n";
    std::cout << "  logitech-g400-config set [options]\n";
    std::cout << "    [--address BUS.DEV]\n";
    std::cout << "    [--sample-rate SAMPLE_RATE]\n";
    std::cout << "        SAMPLE_RATE is one of: 125, 250, 500, 1000.  The Windows software\n";
    std::cout << "        defaults to 500 Hz.\n";
    std::cout << "    [--dpi-level DPI_LEVEL]\n";
    std::cout << "        DPI_LEVEL is an integer between 1 and 4.  It seems to correspond\n";
    std::cout << "        to DPIs of 400, 800, 1800, 3600.  The Windows software defaults to\n";
    std::cout << "        800 DPI and level 2.\n";
}

static void do_list_command() {
    UsbContext ctx;
    const auto dev_list = get_mouse_devices(ctx);
    for (const auto &dev : dev_list) {
        std::cout << dev.address().to_string() << "\n";
    }
    if (dev_list.empty()) {
        std::cout << "none\n";
    }
}

static void do_set_command(std::list<std::string> arg_list) {
    bool address_set = false;
    UsbAddress address {};
    SampleRate sample_rate = SampleRateUnset;
    int dpi_level = -1;

    while (!arg_list.empty()) {
        std::string arg;
        if (match_strval_arg("--address", arg_list, arg)) {
            if (!parse_address(arg, address)) {
                std::cerr << "error: invalid --address argument: '" << arg << "'\n";
                exit(1);
            }
            address_set = true;
            continue;
        }
        if (match_strval_arg("--sample-rate", arg_list, arg)) {
            if (arg == "125") {         sample_rate = SampleRate125;    }
            else if (arg == "250") {    sample_rate = SampleRate250;    }
            else if (arg == "500") {    sample_rate = SampleRate500;    }
            else if (arg == "1000") {   sample_rate = SampleRate1000;   }
            else {
                std::cerr << "error: invalid --sample-rate argument: '" << arg << "'\n";
                exit(1);
            }
            continue;
        }
        if (match_strval_arg("--dpi-level", arg_list, arg)) {
            errno = 0;
            char *endptr = nullptr;
            const long level = strtol(arg.c_str(), &endptr, 10);
            if (errno != 0 || endptr == nullptr || *endptr != '\0' || level < 1 || level > 4) {
                std::cerr << "error: invalid --dpi-level argument: '" << arg << "'\n";
                exit(1);
            }
            dpi_level = level;
            continue;
        }
        std::cerr << "error: unrecognized argument: '" << arg_list.front() << "'\n";
        show_usage();
        exit(1);
    }

    UsbContext ctx;
    const auto dev = address_set ? find_device_by_address(ctx, address)
                                 : find_sole_device(ctx);

    auto devhnd = dev.open();

    // This API call should succeed on Linux and fail on platforms where
    // it isn't supported (e.g. Windows and OS X).
    libusb_set_auto_detach_kernel_driver(devhnd.get(), 1);

    check_libusb(libusb_claim_interface(devhnd.get(), 0));
    check_libusb(libusb_claim_interface(devhnd.get(), 1));

    if (sample_rate != SampleRateUnset) {
        std::array<uint8_t, 2> ctrl { 0x20, static_cast<uint8_t>(sample_rate) };
        const int count = check_libusb(libusb_control_transfer(
            devhnd.get(),
            /*bmRequestType=*/  0x21,
            /*bRequest=*/       9,
            /*wValue=*/         0x320,
            /*wIndex=*/         1,
            ctrl.data(), ctrl.size(),
            /*timeout(ms)=*/    5000));
        assert(count == 2 && "incorrect number of bytes transferred to mouse");
    }

    if (dpi_level != -1) {
        std::array<uint8_t, 2> ctrl { 0x8e, static_cast<uint8_t>(0x03 + dpi_level - 1) };
        const int count = check_libusb(libusb_control_transfer(
            devhnd.get(),
            /*bmRequestType=*/  0x21,
            /*bRequest=*/       9,
            /*wValue=*/         0x38e,
            /*wIndex=*/         1,
            ctrl.data(), ctrl.size(),
            /*timeout(ms)=*/    5000));
        assert(count == 2 && "incorrect number of bytes transferred to mouse");
    }

    check_libusb(libusb_release_interface(devhnd.get(), 0));
    check_libusb(libusb_release_interface(devhnd.get(), 1));
}

static std::list<std::string> make_arg_list(int argc, char *argv[]) {
    std::list<std::string> ret;
    for (int i = 1; i < argc; ++i) {
        ret.push_back(argv[i]);
    }
    return ret;
}

int main(int argc, char *argv[]) {
    try {
        auto arg_list = make_arg_list(argc, argv);
        if (arg_list.empty() || arg_list.front() == "--help") {
            show_usage();
            exit(0);
        }
        if (arg_list.front() == "--version") {
            std::cout << kVersion << "\n";
            exit(0);
        }
        const auto cmd = arg_list.front();
        arg_list.pop_front();
        if (cmd == "list") {
            if (!arg_list.empty()) {
                std::cerr << "error: 'list' command takes no arguments\n";
                exit(1);
            }
            do_list_command();
        } else if (cmd == "set") {
            do_set_command(std::move(arg_list));
        } else {
            std::cerr << "error: unrecognized command: '" << cmd << "'\n";
            show_usage();
            exit(1);
        }
    } catch (const std::string &err) {
        std::cerr << "error: " << err << "\n";
        exit(1);
    }
    return 0;
}
