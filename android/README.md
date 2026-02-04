# Voicing Android App

Android 原生应用，用于将手机输入的文字发送到电脑。

## 功能特性

- WebSocket 实时通信
- 自动连接电脑
- 连接状态显示
- 文字输入和发送
- 深色主题 UI

## 安装方法

### 方式一：下载 APK（推荐）

1. 访问 [GitHub Releases](https://github.com/kevinlasnh/Voice-Coding/releases)
2. 下载最新的 `voicing.apk` 文件
3. 传输到 Android 手机并安装

### 方式二：自行编译

```bash
cd voice_coding
flutter pub get
flutter build apk --release
```

## 使用说明

1. 确保手机和电脑在同一局域网
2. 电脑运行 Voicing 程序（`Voicing.exe`）
3. 打开手机应用，自动连接到 `192.168.137.1:9527`
4. 输入文字后点击"发送到电脑"

## 技术栈

- Flutter 3.27.0
- Dart 3.6.0
- WebSocket
- Material Design 3
