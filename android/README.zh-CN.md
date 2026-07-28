# Voicing Android App

[English](README.md) | [简体中文](README.zh-CN.md)

Android 端应用，通过手机语音输入将文字实时发送到电脑。

## 功能

- 语音输入完成后自动发送到电脑（始终启用）
- 按回车手动发送
- "自动 Enter"开关：语音分段输入静默后统一按一次回车（默认关闭，状态持久化）
- "撤回上次输入"恢复刚才的文本
- "刷新连接"手动重连
- 更多功能操作里的"扫码连接"支持扫描 PC 端二维码配对
- `saved_server` 会记住已配对 PC 的 `device_id`、最近成功 IP 和多个候选 IP
- 启动、恢复前台和手动刷新时直接按保存过的 IP 候选重连，支持热点和公司/学校局域网来回切换
- 同一 PC 重新扫码时会合并新旧候选 IP，不会因为在新局域网扫码而丢掉旧局域网地址
- PC 端会在运行中刷新 QR 码和 WebSocket 监听地址，切换局域网后无需重启桌面端再扫码
- PC 端监听启动后，QR payload 会优先使用实际绑定成功的 IP
- Android 原生 WiFi-bound WebSocket 优先走物理且非 VPN 的 WiFi Network，降低 VPN/代理虚拟网卡影响
- Android 原生 IME 高度监听让输入框实时跟随键盘展开/收起
- 息屏/亮屏后快速重连，并优先保持"已连接"状态显示
- 连接状态实时显示（已连接/连接中.../未连接）
- 深色主题 UI（Material Design 3）
- 协议契约测试覆盖

## 安装

从 [GitHub Releases](https://github.com/kevinlasnh/Voicing/releases/latest) 下载 `voicing.apk`，安装到手机。
建议同时下载 `SHA256SUMS.txt`，先校验摘要再安装。

或自行编译：

```bash
cd android/voice_coding
flutter pub get
flutter build apk --release
```

## 使用

1. 电脑运行桌面端程序，开启热点或连接同一局域网
2. 电脑端托盘菜单点击"显示 QR 码"
3. 手机连接同一网络，打开 Voicing
4. 首次使用或换电脑后，点击手机端"更多功能操作"里的"扫码连接"，扫描 PC 端二维码保存这台电脑
5. 状态栏显示"已连接"即可使用；后续启动会直接尝试保存过的 IP 候选。若电脑和手机一起切换到新局域网，等待 PC 端刷新 QR 码后重新扫码即可把新 IP 合并进候选池，无需重启桌面端；再切回旧局域网时会继续尝试旧候选 IP。v2.9.4 起，QR payload 不再优先发布桌面端绑定失败的地址
6. 切换到语音输入法，说话，文字自动出现在电脑光标处
7. Linux/GNOME Wayland 桌面端日常保持托盘里的"自动粘贴"即可；自动粘贴会采样当前 ACTIVE 窗口，对普通窗口发送 Ctrl+V，对终端发送 Ctrl+Shift+V；证据持续稀疏或冲突时 PC 不发送快捷键，并通过失败 ACK 让手机保留文本供重试。如果 GNOME 在登录或 Voicing 启动后弹出 RemoteDesktop 键盘授权，请先允许再发送文字
8. 点击"更多功能操作"可开启"自动 Enter"（适合聊天场景，语音分段输入只会补一次 Enter）

## 构建说明

- GitHub Actions 发布环境使用 Java 17，可正常产出 `voicing.apk`
- 本地如果默认 Java 指向 25，`flutter build apk --release` 会失败；请在 `android/local.properties` 中通过 `org.gradle.java.home` 指向兼容的 JDK 17/21
- 改动 `MainActivity.kt`、Manifest 或 Gradle 配置后必须完整重新安装 APK；Flutter hot restart 不会更新原生层
- 改动键盘高度、WiFi-bound WebSocket 等原生桥接逻辑后，必须用完整 APK 重新安装验证
- 正式 release 现在必须配置 `key.properties`；若只做本地调试验证，可显式传入 `-Pvoicing.allowDebugReleaseSigning=true` 作为临时豁免，默认不再静默退回 debug signing
- Android Gradle 仓库顺序为官方 `google()` / `mavenCentral()` 优先，阿里云镜像仅作 fallback，避免镜像临时 502 阻断 GitHub Actions release 构建

## 技术栈

- Flutter 3.27.0 (CI)
- Dart SDK: `^3.5.4`
- web_socket_channel: `^2.4.5`
- shared_preferences: `^2.3.3`
- mobile_scanner: `^5.2.3`
- OkHttp: `4.12.0`（Android 原生 WiFi-bound WebSocket）
- Material Design 3
