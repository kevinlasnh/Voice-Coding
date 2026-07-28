<div align="center">

<img src="android/voice_coding/assets/icons/icon_1024.png" width="120" alt="Voicing" style="border-radius: 50%;">

# Voicing

**把手机语音输入法的输出结果塞进电脑 Agent 的嘴里**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/kevinlasnh/Voicing)](https://github.com/kevinlasnh/Voicing/releases/latest)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux%20%7C%20Android-blueviolet)](#)
[![Version](https://img.shields.io/badge/version-2.9.10-green)](#)

[English](README.md) | **简体中文**

和 AI 对话时打字太慢？Voicing 让你用嘴代替手

</div>

---

> **说明**：macOS 和 Linux 桌面端目前仍处于内测阶段，正在持续测试中，稳定性暂时无法保证。

## 它能做什么

Voicing 把手机的语音输入法变成电脑的"嘴"——你在手机上说话，文字直接出现在电脑光标处

- **扫码配对连接** — 首次扫描 PC 端二维码即可保存设备
- **跨子网自动恢复** — 扫码保存同一台 PC 的多个候选 IP，热点和公司/学校局域网来回切换后自动重连
- **无广播依赖** — 手机端启动后直接尝试已保存设备的 IP 池，不再依赖 UDP 广播发现
- **PC 端运行时刷新网络地址** — 电脑切换到新局域网后，QR 码和 WebSocket 监听会自动刷新，无需重启桌面端
- **QR 只发布实际监听 IP** — WebSocket 监听启动后，二维码只优先展示桌面端实际绑定成功的地址
- **物理网卡优先** — 双端尽量绕开 VPN/代理虚拟网卡，优先走真实 WiFi/LAN
- **语音自动发送** — 说完话文字自动打过去，不需要手动操作
- **自动 Enter** — 可选开关，开启后说完话文字就被自动提交给 Agent 执行，无需手动在键盘上按回车键
- **手动发送也行** — 按回车手动发送，适合需要编辑的场景
- **撤回支持** — 发错了？一键撤回上次输入
- **断线自动恢复** — 手机息屏再亮屏，优先保持已连接显示并快速恢复
- **稳定的 Linux 终端感知粘贴** — GNOME Wayland 自动粘贴跟随当前 ACTIVE 窗口，普通窗口发送 Ctrl+V，终端发送 Ctrl+Shift+V，无法可靠判断时安全取消
- **跨平台** — 支持 Windows / macOS / Linux 桌面端，Android 手机端
- **体积小巧** — APK 约 32MB、桌面端约 50–60MB；Linux DEB 会自动安装声明的桌面集成依赖

## 快速开始

### 1. 下载

从 [Releases](https://github.com/kevinlasnh/Voicing/releases/latest) 下载对应平台文件：

| 平台 | 文件 | 要求 |
|------|------|------|
| Windows | `voicing-windows-x64.exe` | Win 10/11 (64-bit) |
| macOS | `voicing-macos-arm64.dmg` | Apple Silicon (M1+) |
| Linux | `voicing-linux-amd64.deb` 或 `voicing-linux-x86_64` | Ubuntu 22.04+ GNOME X11，或具备 RemoteDesktop portal 的 GNOME Wayland |
| Android | `voicing.apk` | Android 5.0+ |

Release 里同时提供 `SHA256SUMS.txt`，下载后可先校验 SHA-256 摘要再安装或运行。

### 2. 连接

```
电脑运行桌面端程序 → 开启热点 / 互联网共享 / 同一局域网 → 电脑端显示 QR 码 → 手机扫码连接
```

- **Windows**：运行 `voicing-windows-x64.exe`，开启"移动热点"
- **macOS**：打开 `voicing-macos-arm64.dmg`，拖入 Applications（首次打开需右键→打开），开启"互联网共享"或连接同一局域网
- **Linux**：安装 `voicing-linux-amd64.deb`，或对独立二进制执行 `chmod +x voicing-linux-x86_64` 后运行；开启 Wi-Fi 热点或连接同一局域网。DEB 会安装所需的 AT-SPI、Python GI 和 `wl-clipboard` 依赖，独立二进制用户需要自行提供。GNOME Wayland 在 Voicing 启动或首次粘贴文字时可能会要求授权 RemoteDesktop 键盘会话

状态栏显示"已连接"就说明连上了

扫码成功后手机会记住这台电脑及其候选 IP 池。下次启动时，手机会直接尝试保存过的地址候选；即使公司、学校或宿舍网络隔离广播，只要设备间单播可达，也能自动连回。电脑端切换到新局域网后会自动刷新 QR 码和 WebSocket 监听地址，不需要重启桌面端软件。手机在新局域网重新扫码同一台 PC 时，会把新 IP 合并进已有候选池，不会丢掉旧局域网地址。

### 3. 使用

1. 电脑上把光标点到要输入的位置
2. 手机上切换到语音输入法，开始说话
3. 文字自动出现在电脑上

Linux/GNOME Wayland 日常使用保持桌面端"自动粘贴"即可。自动粘贴会采样当前 ACTIVE 窗口，对普通输入框发送 Ctrl+V，检测到终端时自动切到 Ctrl+Shift+V。Ghostty 这类只暴露通用 `Unnamed` AT-SPI frame 的终端会通过进程可执行文件 basename 识别，不读取窗口标题或剪贴板正文。如果焦点证据持续稀疏或冲突，Voicing 不会发送任何快捷键，并通过失败 ACK 让手机保留文本供重试，避免粘贴到错误应用；只有特定终端无法提供可靠 AT-SPI 状态时再手动切到"终端粘贴"。

> **推荐搭配**：[豆包输入法](https://shurufa.doubao.com/) + [大疆 Mic Mini](https://www.dji.com/cn/mic-mini) + [DJI Mic 系列手机接收器](https://store.dji.com/cn/product/dji-mic-series-mobile-receiver?vid=200571) —— 语音识别准确，领夹麦克风直连手机，体验最佳

## 功能一览

### 手机端

- 语音输入完成后自动发送到电脑
- 按回车手动发送
- "自动 Enter"开关：语音分段输入时只在静默后统一按一次回车（默认关闭）
- "撤回上次输入"恢复刚才的文本
- "刷新连接"手动重连

### 电脑端

托盘图标菜单（Windows 右键 / macOS 左键 / Linux 左键或右键）：

| 菜单项 | 功能 |
|--------|------|
| 显示 QR 码 | 展示当前电脑的 Voicing 配对二维码 |
| 同步输入 | 开关是否接收手机文字 |
| 粘贴模式 | 在自动 / 普通 / 终端 / 兼容粘贴模式之间切换；日常推荐自动粘贴 |
| 开机自启 | 通过系统机制登录后自动启动：Windows Run 注册表、macOS LaunchAgent、Linux GNOME autostart `.desktop` |
| 打开日志 | 用记事本打开当天日志 |
| 退出应用 | 关闭程序 |

托盘图标状态：
- 闪烁 = 等待手机连接
- 常亮 = 已连接
- 灰色 = 同步已关闭

## 工作原理

1. 桌面端展示包含 `device_id/ip/ips/port/name/os` 的配对二维码，运行中会刷新当前物理 IPv4 地址池，并优先使用 WebSocket 实际绑定成功的 IP
2. 手机扫描二维码后做 WebSocket（端口 9527）连通性 probe，成功后保存这台 PC
3. 手机端持久化同一台 PC 的多个候选 IP，热点和不同局域网地址都会保留；同一 `device_id` 重新扫码只合并候选池，不覆盖旧地址
4. 后续启动或手动刷新时，手机直接按保存的 IP 池逐个尝试连接，不再依赖 UDP 广播发现
5. PC 端 WebSocket server 会在地址池变化后重新绑定当前局域网 IP，避免继续监听旧网络地址
6. QR payload 避免发布绑定失败的地址；macOS 网卡命名按保守策略处理，不再假设 `en0` 一定是 WiFi
7. Android 端 WebSocket 优先绑定物理 WiFi Network，PC 端过滤 VPN/虚拟网卡，Android 端显式要求非 VPN 的 WiFi Network，降低双端开代理时的误路由
8. 手机上的文字（语音输入或手动输入）实时发送到桌面端
9. 桌面端通过剪贴板粘贴文本，并在需要时补发一次 Enter；Linux X11 走常规 Ctrl+V 路径，GNOME Wayland 走 RemoteDesktop portal 键盘授权
10. GNOME Wayland 默认使用自动粘贴：普通窗口发送 Ctrl+V，检测到的终端焦点发送 Ctrl+Shift+V，无法可靠判断时安全取消并保留手机输入；托盘菜单可手动切换为普通、终端或兼容粘贴模式

## 开发

### 环境准备

```bash
git clone https://github.com/kevinlasnh/Voicing.git
cd Voicing

# 桌面端（Windows / macOS / Linux）
cd pc
pip install -r requirements.txt
python voice_coding.py --dev

# Android 端
cd android/voice_coding
flutter pub get
flutter run
```

### 项目结构

```
Voicing/
├── pc/                          # 桌面端 (Python + PyQt5)
│   ├── voice_coding.py          # 主程序
│   ├── device_identity.py       # PC device_id / name / os 持久化
│   ├── platform_utils.py        # 平台检测与通用工具
│   ├── platform_keyboard.py     # 键盘模拟抽象
│   ├── platform_autostart.py    # 开机自启抽象
│   ├── platform_instance.py     # 单实例检测抽象
│   ├── voicing_protocol.py      # 协议常量
│   ├── network_recovery.py      # 网络恢复策略辅助
│   └── requirements.txt         # Python 依赖
├── android/voice_coding/        # Android 端 (Flutter)
│   ├── lib/
│   │   ├── main.dart            # UI 层
│   │   ├── voicing_connection_controller.dart  # 连接状态机
│   │   ├── voicing_protocol.dart               # 协议常量
│   │   ├── saved_server.dart    # 已配对 PC 持久化
│   │   ├── voicing_websocket.dart # Android WiFi-bound WebSocket / Dart fallback
│   │   ├── app_theme.dart       # 主题与设计 token
│   │   └── app_logger.dart      # 日志封装
│   └── pubspec.yaml             # Flutter 依赖
├── protocol/                    # 双端共享协议契约
│   └── voicing_protocol_contract.json
├── .github/workflows/
│   └── release.yml              # 自动构建发布
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

### 打包发布

正式发布通过 GitHub Actions 自动构建（四平台：Android / Windows / macOS / Linux）：

```bash
git tag v2.9.10
git push origin v2.9.10
```

本地调试用：

```bash
# Windows
cd pc && pyinstaller --onefile --windowed --name=Voicing \
  --icon=assets/icon.ico --add-data "assets;assets" voice_coding.py

# macOS（生成 .app bundle）
cd pc && pyinstaller --windowed --name=Voicing \
  --icon=assets/icon.icns --add-data "assets:assets" voice_coding.py

# Linux
cd pc && pyinstaller --onefile --name=Voicing \
  --add-data "assets:assets" voice_coding.py

# Android
cd android/voice_coding && flutter build apk --release
```

注意：本地 Android release 构建需要兼容的 JDK 17/21，并配置正式签名；当前 GitHub Actions 发布环境固定使用 Java 17，正式 Release 也会强制校验签名 secrets。Android Gradle 仓库解析优先使用官方 `google()` / `mavenCentral()`，阿里云镜像仅作为 fallback。

## 常见问题

**手机无法连接电脑？**
1. 确认电脑和手机在同一个 WiFi 热点或局域网下
2. 检查电脑防火墙是否放行 TCP 9527
3. 首次使用或换电脑后，用电脑端"显示 QR 码"和手机端"扫码连接"配对一次
4. 手机息屏恢复后会立即进入快速重连，通常无需手动刷新
5. 刚切换到新局域网后，PC 端会自动刷新 QR 码和监听地址；仍然不行就点手机端"刷新连接"，或重新扫描 PC 端二维码把新 IP 合并进候选池
6. 如果电脑端是 macOS，请确认已更新并重启到 v2.9.4 或更新版本，这些版本不再因为 `en0/en1` 网卡命名误判而优先发布错误地址

**本地 Flutter 打 APK 失败，提示 Java / Gradle 不兼容？**
本机如果默认使用 Java 25，`flutter build apk --release` 会失败。请安装 JDK 17/21，并在 `android/voice_coding/android/local.properties` 中设置 `org.gradle.java.home=...`；正式 release 走 GitHub Actions 的 Java 17 环境。

**文字打到了错误位置？**
发送前确保电脑光标在正确的输入框里

**Linux 应该用哪个粘贴模式？**
默认使用"自动粘贴"。它会自动处理普通输入框和终端。只有终端未被识别时才切到"终端粘贴"，或者在某些偏好 Shift+Insert 的软件里切到"兼容粘贴"。

**Linux 开机自启正常吗？**
Ubuntu GNOME 下正常。Voicing 会写入 `~/.config/autostart/voicing.desktop`，由 GNOME 在登录后启动。GNOME Wayland 下程序可以自启，但 RemoteDesktop 键盘授权仍由 GNOME 控制；登录或启动后如果弹出授权提示，需要手动允许。

**日志在哪？**
打开托盘图标菜单 → "打开日志"
- Windows: `%APPDATA%\Voicing\logs\`
- macOS: `~/Library/Logs/Voicing/`
- Linux: `~/.local/share/Voicing/logs/`

## 贡献

欢迎提交 Issue 和 Pull Request，请看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 许可证

[MIT License](LICENSE)
