<div align="center">

<img src="android/voice_coding/assets/icons/icon_1024.png" width="120" alt="Voicing" style="border-radius: 50%;">

# Voicing

**Pipe your phone's voice-to-text straight into your desktop AI agent**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/kevinlasnh/Voicing)](https://github.com/kevinlasnh/Voicing/releases/latest)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux%20%7C%20Android-blueviolet)](#)
[![Version](https://img.shields.io/badge/version-2.9.10-green)](#)

**English** | [简体中文](README.zh-CN.md)

Tired of typing while talking to AI? Voicing lets your mouth replace your hands.

</div>

---

> **Note**: macOS and Linux desktop builds are still in beta. Stability is not yet guaranteed.

## What it does

Voicing turns your phone's voice keyboard into your computer's "mouth" — speak on your phone, and the text lands directly at the cursor on your computer.

- **QR pairing** — scan the desktop's QR code once and the device is remembered
- **Cross-subnet auto-recovery** — multiple candidate IPs are saved per PC, so switching between hotspot, office, and school LANs reconnects automatically
- **No broadcast required** — after launch, the phone tries the saved IP pool directly; no UDP discovery
- **PC runtime network refresh** — when the desktop switches to a new LAN, the QR code and WebSocket listener refresh on the fly with no app restart
- **Bound-IP QR safety** — once the listener is up, QR codes advertise only the IPs the desktop actually bound successfully
- **Physical NIC priority** — both ends try to bypass VPN/proxy virtual adapters and prefer real WiFi/LAN
- **Auto-send on speech end** — finished sentences are sent automatically; no manual confirm
- **Auto Enter (optional)** — submit to the agent as soon as you stop speaking
- **Manual Enter still works** — press Enter to submit, useful when you want to edit first
- **Undo** — accidentally sent something? One tap to take it back
- **Auto reconnect** — wakes from screen-off and prefers showing "connected" while reconnecting
- **Stable terminal-aware Linux paste** — GNOME Wayland Auto paste follows the current ACTIVE window, uses Ctrl+V for normal windows, Ctrl+Shift+V for terminals, and safely cancels unresolved attempts
- **Cross-platform** — Windows / macOS / Linux desktop, plus Android phone client
- **Compact** — ~32 MB APK and ~50–60 MB desktop bundles; the Linux DEB installs its declared desktop-integration dependencies

## Quick start

### 1. Download

Grab the right file from [Releases](https://github.com/kevinlasnh/Voicing/releases/latest):

| Platform | File | Requirements |
|------|------|------|
| Windows | `voicing-windows-x64.exe` | Win 10/11 (64-bit) |
| macOS | `voicing-macos-arm64.dmg` | Apple Silicon (M1+) |
| Linux | `voicing-linux-amd64.deb` or `voicing-linux-x86_64` | Ubuntu 22.04+ GNOME X11, or GNOME Wayland with RemoteDesktop portal |
| Android | `voicing.apk` | Android 5.0+ |

Each release also ships `SHA256SUMS.txt` so you can verify the SHA-256 digest before installing.

### 2. Connect

```
Run the desktop app → start a hotspot / Internet sharing / join the same LAN → desktop shows the QR code → scan with the phone
```

- **Windows**: run `voicing-windows-x64.exe` and turn on "Mobile hotspot"
- **macOS**: open `voicing-macos-arm64.dmg`, drag to Applications (right-click → Open the first time), enable "Internet Sharing" or join the same LAN
- **Linux**: install `voicing-linux-amd64.deb`, or run the standalone binary with `chmod +x voicing-linux-x86_64`; start a Wi-Fi hotspot or join the same LAN. The DEB installs the required AT-SPI, Python GI, and `wl-clipboard` packages. Standalone-binary users must provide them separately. GNOME Wayland may ask you to approve a RemoteDesktop keyboard session when Voicing starts or when text is pasted.

When the status bar shows "Connected" you're good to go.

After a successful scan the phone remembers this PC and its candidate IP pool. On the next launch it tries those saved addresses directly — even if the corporate / school / dorm network blocks broadcast, as long as device-to-device unicast works the connection comes back automatically. When the desktop switches to a new LAN, the QR code and WebSocket listener refresh in place; no need to restart the desktop app. Re-scanning the same PC on a new LAN merges the new IP into the candidate pool without dropping the old LAN address.

### 3. Use it

1. On the computer, click the cursor where you want text to appear
2. On the phone, switch to a voice keyboard and start talking
3. The text appears on the computer

On Linux/GNOME Wayland, keep the desktop paste mode on **Auto paste** for normal use. Auto paste samples the current ACTIVE window, sends Ctrl+V to normal input fields, and switches to Ctrl+Shift+V for terminals. Terminals such as Ghostty that expose a generic `Unnamed` AT-SPI frame are identified from the process executable basename, never from window titles or clipboard text. If focus evidence remains sparse or conflicting, Voicing sends no shortcut and returns a failed ACK so the phone keeps the text for retry instead of risking a paste into the wrong app. Switch to Terminal paste only if a specific terminal cannot expose reliable AT-SPI state.

> **Recommended setup**: [Doubao Input](https://shurufa.doubao.com/) + [DJI Mic Mini](https://www.dji.com/mic-mini) + [DJI Mic Mobile Receiver](https://store.dji.com/product/dji-mic-series-mobile-receiver) — accurate ASR, lavalier mic plugged straight into the phone, best overall experience.

## Features

### Phone

- Auto-send to the computer once a voice utterance is finished
- Press Enter to send manually
- "Auto Enter" toggle: with chunked voice input, only one Enter is fired after silence (off by default)
- "Undo last input" restores the previously sent text
- "Refresh connection" forces a manual reconnect

### Desktop

Tray icon menu (right-click on Windows; left-click on macOS; left-click or right-click on Linux):

| Item | Function |
|--------|------|
| Show QR code | Display the current pairing QR for this PC |
| Sync input | Toggle whether phone text is accepted |
| Paste mode | Switch Auto / Normal / Terminal / Compatibility paste modes; Auto is recommended |
| Auto-start | Register at login via the OS mechanism: Windows Run key, macOS LaunchAgent, Linux GNOME autostart `.desktop` |
| Open log | Open today's log in the default text editor |
| Quit | Exit the app |

Tray icon states:
- Blinking = waiting for the phone to connect
- Solid = connected
- Greyed = sync disabled

## How it works

1. The desktop displays a pairing QR with `device_id/ip/ips/port/name/os`, refreshing the physical IPv4 address pool at runtime and preferring the WebSocket listener's actually bound IPs
2. The phone scans the QR and runs a WebSocket (port 9527) connectivity probe; on success it saves this PC
3. The phone persists multiple candidate IPs for the same PC — hotspot and various LAN addresses are all kept; re-scanning the same `device_id` merges the candidate pool rather than overwriting it
4. On later launches or manual refresh, the phone tries the saved IP pool one by one; UDP discovery is no longer used
5. The PC WebSocket server rebinds to the current LAN IP whenever the address pool changes, so it never lingers on stale addresses
6. QR payloads avoid advertising addresses that failed to bind; macOS interface names are handled conservatively instead of assuming `en0` is WiFi
7. The Android WebSocket prefers binding to the physical WiFi `Network`; the PC filters VPN / virtual adapters, and Android explicitly requires a non-VPN WiFi Network
8. Phone text (voice or typed) streams to the desktop in real time
9. The desktop pastes via the clipboard and emits an Enter when needed; Linux X11 uses the normal Ctrl+V path, while GNOME Wayland uses the RemoteDesktop portal keyboard permission
10. GNOME Wayland defaults to Auto paste: normal windows receive Ctrl+V, detected terminal focus receives Ctrl+Shift+V, unresolved focus cancels safely while preserving phone input, and the tray menu can switch manually to normal, terminal, or compatibility paste modes

## Development

### Setup

```bash
git clone https://github.com/kevinlasnh/Voicing.git
cd Voicing

# Desktop (Windows / macOS / Linux)
cd pc
pip install -r requirements.txt
python voice_coding.py --dev

# Android
cd android/voice_coding
flutter pub get
flutter run
```

### Project layout

```
Voicing/
├── pc/                          # Desktop (Python + PyQt5)
│   ├── voice_coding.py          # Main program
│   ├── device_identity.py       # PC device_id / name / os persistence
│   ├── platform_utils.py        # Platform detection and shared utilities
│   ├── platform_keyboard.py     # Keyboard simulation abstraction
│   ├── platform_autostart.py    # Auto-start abstraction
│   ├── platform_instance.py     # Single-instance detection
│   ├── voicing_protocol.py      # Protocol constants
│   ├── network_recovery.py      # Network recovery helpers
│   └── requirements.txt         # Python dependencies
├── android/voice_coding/        # Android (Flutter)
│   ├── lib/
│   │   ├── main.dart            # UI layer
│   │   ├── voicing_connection_controller.dart  # Connection state machine
│   │   ├── voicing_protocol.dart               # Protocol constants
│   │   ├── saved_server.dart    # Paired-PC persistence
│   │   ├── voicing_websocket.dart # Android WiFi-bound WebSocket / Dart fallback
│   │   ├── app_theme.dart       # Theme and design tokens
│   │   └── app_logger.dart      # Logging wrapper
│   └── pubspec.yaml             # Flutter dependencies
├── protocol/                    # Shared protocol contract
│   └── voicing_protocol_contract.json
├── .github/workflows/
│   └── release.yml              # Automated build & release
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

### Build & release

Production releases run through GitHub Actions, building all four platforms (Android / Windows / macOS / Linux):

```bash
git tag v2.9.10
git push origin v2.9.10
```

Local debug builds:

```bash
# Windows
cd pc && pyinstaller --onefile --windowed --name=Voicing \
  --icon=assets/icon.ico --add-data "assets;assets" voice_coding.py

# macOS (.app bundle)
cd pc && pyinstaller --windowed --name=Voicing \
  --icon=assets/icon.icns --add-data "assets:assets" voice_coding.py

# Linux
cd pc && pyinstaller --onefile --name=Voicing \
  --add-data "assets:assets" voice_coding.py

# Android
cd android/voice_coding && flutter build apk --release
```

Note: a local Android release build needs a compatible JDK 17/21 and a valid signing config. The GitHub Actions release pipeline pins Java 17 and enforces release-signing secrets. Android Gradle resolves dependencies through the official `google()` / `mavenCentral()` first, with the Aliyun mirror as a fallback only.

## FAQ

**Phone can't connect to the PC?**
1. Check that both are on the same WiFi hotspot or LAN
2. Make sure the PC firewall allows TCP 9527
3. First-time setup or a new PC: run "Show QR code" on the desktop and "Scan to connect" on the phone
4. After the screen wakes up the phone enters fast-reconnect mode automatically — usually no manual refresh is needed
5. Right after switching to a new LAN, the desktop refreshes the QR and listener automatically; if it still fails, tap "Refresh connection" on the phone or re-scan the desktop QR to merge the new IP into the candidate pool
6. If the PC is on macOS, make sure Voicing has been restarted after updating to v2.9.4 or later so QR codes no longer prefer a misclassified `en0/en1` interface

**Local Flutter APK build fails with a Java / Gradle error?**
If your default Java is 25, `flutter build apk --release` will fail. Install JDK 17/21 and set `org.gradle.java.home=...` in `android/voice_coding/android/local.properties`. Production releases use the Java 17 environment in GitHub Actions.

**Text landed in the wrong place?**
Make sure the cursor is in the right input field before you start speaking.

**Which Linux paste mode should I use?**
Use **Auto paste** by default. It handles regular input fields and terminals automatically. Switch to **Terminal paste** only if your terminal is not detected, or **Compatibility paste** for apps that prefer Shift+Insert.

**Does Auto-start work on Linux?**
On Ubuntu GNOME, yes. Voicing writes `~/.config/autostart/voicing.desktop` and GNOME launches it after login. On GNOME Wayland, the app can auto-start, but the RemoteDesktop keyboard permission is still controlled by GNOME; approve the prompt after login or app start if it appears.

**Where are the logs?**
Open the tray icon menu → "Open log".
- Windows: `%APPDATA%\Voicing\logs\`
- macOS: `~/Library/Logs/Voicing/`
- Linux: `~/.local/share/Voicing/logs/`

## Contributing

Issues and Pull Requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT License](LICENSE)
