# Voicing Android App

[English](README.md) | [简体中文](README.zh-CN.md)

The Android client. Streams text from the phone's voice keyboard to the desktop in real time.

## Features

- Auto-send to the computer after voice input finishes (always on)
- Press Enter to send manually
- "Auto Enter" toggle: with chunked voice input, fires Enter only once after a silence window (off by default, persisted across launches)
- "Undo last input" restores the previously sent text
- "Refresh connection" forces a manual reconnect
- "Scan to connect" under the More menu — pairs with the PC by scanning its QR code
- `saved_server` remembers each paired PC's `device_id`, the most recent successful IP, and the full candidate-IP pool
- On launch, foreground resume, and manual refresh, reconnects directly via the saved IP candidates — handles hotspot ↔ office/school LAN switching
- Re-scanning the same PC merges new and old candidate IPs, so scanning on a new LAN does not drop the old LAN address
- The PC refreshes its QR and WebSocket listener at runtime, so the desktop app does not need a restart after a LAN switch
- After the desktop listener is up, QR payloads prefer the IPs that the PC actually bound successfully
- Android-native WiFi-bound WebSocket prefers a physical, non-VPN WiFi `Network`, reducing VPN/proxy adapter interference
- Android-native IME-height listener keeps the input field tracking the keyboard as it expands/collapses
- Fast reconnect after screen-off / screen-on, prefers showing "Connected" while reconnecting
- Live connection status (Connected / Connecting… / Disconnected)
- Dark Material Design 3 theme
- Protocol-contract test coverage

## Install

Download `voicing.apk` from [GitHub Releases](https://github.com/kevinlasnh/Voicing/releases/latest) and install it.
You can also fetch `SHA256SUMS.txt` and verify the digest before installing.

Or build it yourself:

```bash
cd android/voice_coding
flutter pub get
flutter build apk --release
```

## Usage

1. Run the desktop app on the computer; start a hotspot or join the same LAN
2. From the desktop tray menu, click "Show QR code"
3. Connect the phone to the same network and open Voicing
4. First use or new PC: tap "More → Scan to connect" on the phone and scan the desktop's QR
5. Once the status bar reads "Connected" you're set; later launches will try the saved IP candidates directly. After both ends switch to a new LAN, wait for the desktop to refresh its QR, then re-scan to merge the new IP into the candidate pool — no desktop restart needed. Switching back to the old LAN keeps trying the older candidate IPs. On v2.9.4+, QR payloads avoid preferring desktop addresses that failed to bind
6. Switch to a voice keyboard, talk, and the text shows up at the cursor on the computer
7. On Linux/GNOME Wayland desktops, leave the PC tray paste mode on Auto paste unless a specific app needs a manual mode. Auto paste samples the current ACTIVE window, uses Ctrl+V for normal windows, and switches to Ctrl+Shift+V for terminals. If evidence stays sparse or conflicting, the PC sends no shortcut and returns a failed ACK so this app keeps the text for retry. If GNOME asks for RemoteDesktop keyboard permission after login or app start, approve it before sending text
8. Open "More" to enable "Auto Enter" (good for chat scenarios — only one Enter is fired per chunked voice utterance)

## Build notes

- The GitHub Actions release pipeline uses Java 17 and produces `voicing.apk` as expected
- If your local default Java points to 25, `flutter build apk --release` will fail; set `org.gradle.java.home` in `android/local.properties` to a compatible JDK 17/21
- After changes to `MainActivity.kt`, the Manifest, or Gradle config, you must reinstall the full APK — Flutter hot restart does not refresh the native layer
- The same applies to native bridges like keyboard-height handling and the WiFi-bound WebSocket — verify with a fresh APK install
- Production releases now require `key.properties`; for local debug verification you can pass `-Pvoicing.allowDebugReleaseSigning=true` as an explicit override. Silent fallback to debug signing is no longer allowed
- Android Gradle resolves dependencies through the official `google()` / `mavenCentral()` first, with the Aliyun mirror as a fallback only — this avoids transient mirror 502s from blocking the GitHub Actions release build

## Tech stack

- Flutter 3.27.0 (CI)
- Dart SDK: `^3.5.4`
- web_socket_channel: `^2.4.5`
- shared_preferences: `^2.3.3`
- mobile_scanner: `^5.2.3`
- OkHttp: `4.12.0` (Android-native WiFi-bound WebSocket)
- Material Design 3
