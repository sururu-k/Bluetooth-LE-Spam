import Foundation
import CoreBluetooth

class BLEManager: NSObject, ObservableObject, CBPeripheralManagerDelegate {
    @Published var isAdvertising = false
    @Published var statusMessage = "待機中"
    @Published var sentCount = 0
    @Published var bluetoothReady = false

    private var peripheralManager: CBPeripheralManager?
    private var timer: Timer?
    private var currentTypes: [PayloadType] = []
    var intervalMs: Int = 100

    override init() {
        super.init()
        peripheralManager = CBPeripheralManager(delegate: self, queue: nil)
    }

    // MARK: - CBPeripheralManagerDelegate

    func peripheralManagerDidUpdateState(_ peripheral: CBPeripheralManager) {
        switch peripheral.state {
        case .poweredOn:
            bluetoothReady = true
            statusMessage = "Bluetooth ON - 準備完了"
        case .poweredOff:
            bluetoothReady = false
            statusMessage = "Bluetooth OFF"
        case .unauthorized:
            statusMessage = "Bluetooth 権限なし"
        case .unsupported:
            statusMessage = "BLE 未対応デバイス"
        default:
            statusMessage = "Bluetooth 初期化中..."
        }
    }

    // MARK: - Advertising Control

    func startSpam(types: [PayloadType]) {
        guard bluetoothReady else {
            statusMessage = "Bluetooth が準備できていません"
            return
        }
        currentTypes = types
        isAdvertising = true
        sentCount = 0
        scheduleNext()
    }

    func stopSpam() {
        isAdvertising = false
        timer?.invalidate()
        timer = nil
        peripheralManager?.stopAdvertising()
        statusMessage = "停止 (送信数: \(sentCount))"
    }

    private func scheduleNext() {
        guard isAdvertising else { return }

        let type = currentTypes.randomElement()!
        let payload = generatePayload(type)
        advertise(payload: payload)

        timer = Timer.scheduledTimer(withTimeInterval: Double(intervalMs) / 1000.0,
                                     repeats: false) { [weak self] _ in
            self?.peripheralManager?.stopAdvertising()
            self?.scheduleNext()
        }
    }

    private func advertise(payload: BLEPayload) {
        var adDict: [String: Any] = [:]

        /*
         iOS制約:
         CBPeripheralManager.startAdvertising() は以下のキーのみサポート:
         - CBAdvertisementDataLocalNameKey
         - CBAdvertisementDataServiceUUIDsKey

         CBAdvertisementDataManufacturerDataKey は iOS では無視される。
         macOS では使用可能な場合がある。

         そのため iOS では service-based advertising (Google Fast Pair) が
         最も確実に動作する。manufacturer-specific data (Apple/Microsoft/Samsung)
         は macOS ビルドでのみ動作する可能性が高い。
        */

        #if os(macOS)
        // macOS: manufacturer data をサポート
        if let mfrId = payload.manufacturerId, let mfrData = payload.manufacturerData {
            var fullData = Data()
            // manufacturer ID (little-endian)
            fullData.append(UInt8(mfrId & 0xFF))
            fullData.append(UInt8((mfrId >> 8) & 0xFF))
            fullData.append(mfrData)
            // macOS の private key を使用
            adDict["kCBAdvDataManufacturerData"] = fullData
        }
        #endif

        if let serviceUUID = payload.serviceUUID {
            let uuid = CBUUID(string: serviceUUID)
            adDict[CBAdvertisementDataServiceUUIDsKey] = [uuid]
        }

        // Local name (Swift Pair のデバイス名など)
        if payload.type == .microsoftSwiftPair || payload.type == .microsoftSwiftPairHeadphone {
            let name = swiftPairNames.randomElement() ?? "Device"
            adDict[CBAdvertisementDataLocalNameKey] = name
        }

        // Name Flood: advertise a random name as the local name
        if payload.type == .nameflood, let data = payload.manufacturerData {
            adDict[CBAdvertisementDataLocalNameKey] = String(data: data, encoding: .utf8) ?? "Device"
        }

        peripheralManager?.startAdvertising(adDict)
        sentCount += 1
        statusMessage = "送信中 #\(sentCount) [\(payload.type.rawValue)]"
    }
}
