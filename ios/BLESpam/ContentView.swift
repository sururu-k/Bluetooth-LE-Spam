import SwiftUI

struct ContentView: View {
    @StateObject private var bleManager = BLEManager()
    @State private var selectedTypes: Set<PayloadType> = Set(PayloadType.allCases)
    @State private var interval: Double = 100

    var body: some View {
        NavigationView {
            VStack(spacing: 16) {
                // Status
                HStack {
                    Circle()
                        .fill(bleManager.bluetoothReady ? Color.green : Color.red)
                        .frame(width: 12, height: 12)
                    Text(bleManager.statusMessage)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding(.horizontal)

                // Interval slider
                VStack(alignment: .leading) {
                    Text("Interval: \(Int(interval))ms")
                        .font(.caption)
                    Slider(value: $interval, in: 20...500, step: 10)
                }
                .padding(.horizontal)

                // Target selection
                List {
                    Section("Targets") {
                        ForEach(PayloadType.allCases, id: \.self) { type in
                            HStack {
                                Text(type.rawValue)
                                Spacer()
                                if selectedTypes.contains(type) {
                                    Image(systemName: "checkmark")
                                        .foregroundColor(.blue)
                                }
                            }
                            .contentShape(Rectangle())
                            .onTapGesture {
                                if selectedTypes.contains(type) {
                                    selectedTypes.remove(type)
                                } else {
                                    selectedTypes.insert(type)
                                }
                            }
                        }
                    }

                    #if os(iOS)
                    Section {
                        Text("iOS ではmanufacturer dataの送信に制限があります。Google Fast Pair (service-based) が最も確実です。")
                            .font(.caption2)
                            .foregroundColor(.orange)
                    }
                    #endif
                }

                // Control buttons
                HStack(spacing: 20) {
                    Button(action: {
                        bleManager.intervalMs = Int(interval)
                        bleManager.startSpam(types: Array(selectedTypes))
                    }) {
                        Label("開始", systemImage: "play.fill")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.green)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                    .disabled(bleManager.isAdvertising || selectedTypes.isEmpty)

                    Button(action: {
                        bleManager.stopSpam()
                    }) {
                        Label("停止", systemImage: "stop.fill")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.red)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                    .disabled(!bleManager.isAdvertising)
                }
                .padding(.horizontal)

                // Counter
                Text("送信数: \(bleManager.sentCount)")
                    .font(.headline)
                    .padding(.bottom)
            }
            .navigationTitle("BLE Spam")
        }
    }
}
