# BLE Spam - Cross Platform

元の Android アプリを iOS / Windows / macOS に移植したもの。

## 構成

```
desktop/          # Python (Windows EXE / macOS / Linux)
ios/              # Swift (iOS IPA / macOS Catalyst)
```

---

## Desktop (Windows EXE / macOS)

### 依存関係

```bash
cd desktop
pip install -r requirements.txt
```

### 実行

```bash
python ble_spam.py                  # インタラクティブメニュー
python ble_spam.py --target apple   # Apple系のみ
python ble_spam.py --target all     # 全種類ランダム
python ble_spam.py --interval 50    # 50ms間隔
```

### Windows EXE ビルド

```bat
build_exe.bat
# -> dist/BLESpam.exe
```

### macOS ビルド

```bash
./build_mac.sh
# -> dist/BLESpam
```

### プラットフォーム別の必要パッケージ

| OS | パッケージ |
|-----|-----------|
| Windows | `winrt-Windows.Devices.Bluetooth.Advertisement` |
| macOS | `pyobjc-framework-CoreBluetooth` |
| Linux | `bluez` (hcitool) |

---

## iOS / macOS (Swift)

### ビルド方法

1. `ios/BLESpam.xcodeproj` を Xcode で開く
2. Signing で自分の Apple ID を設定
3. ターゲットを iPhone / Mac Catalyst に変更してビルド

### IPA 作成 (サイドロード用)

```bash
# Xcode でアーカイブ
# Product > Archive > Distribute App > Ad Hoc / Development

# または CLI:
cd ios
xcodebuild archive \
  -project BLESpam.xcodeproj \
  -scheme BLESpam \
  -archivePath build/BLESpam.xcarchive

xcodebuild -exportArchive \
  -archivePath build/BLESpam.xcarchive \
  -exportPath build/ \
  -exportOptionsPlist ExportOptions.plist
```

サイドロードには以下を使用:
- **AltStore** / **AltServer**
- **Sideloadly**
- **TrollStore** (対応iOS版のみ)

### iOS の制約

iOS の CoreBluetooth は `CBAdvertisementDataManufacturerDataKey` を
`startAdvertising()` でサポートしていない。そのため:

- **Google Fast Pair** (service-based) → 動作する
- **Apple / Microsoft / Samsung** (manufacturer data) → iOS では動作しない
- **macOS Catalyst** ビルドなら manufacturer data も動作する可能性あり
