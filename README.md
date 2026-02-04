# Voicing

<div align="center">

**手机语音输入，电脑光标输出** 📱💻

将手机变成电脑的无线语音输入设备

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/kevinlasnh/Voice-Coding)](https://github.com/kevinlasnh/Voice-Coding/releases/latest)

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [下载](#-下载) • [常见问题](#-常见问题)

</div>

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 📡 **UDP 自动发现** | 手机自动发现并连接电脑，无需配置 IP |
| 📱 **手机输入** | 支持文字输入、语音输入、撤回功能 |
| 🎯 **自动发送** | 语音输入实时同步到电脑，下划线消失自动发送 |
| 💻 **电脑输出** | 文本瞬间出现在电脑光标处 |
| 🔗 **局域网直连** | 无需云端、无需服务器，端对端直连 |
| 🖥️ **系统托盘** | Windows 11 Fluent Design 风格托盘菜单 |
| 📋 **日志系统** | 完整的运行日志，方便排查问题 |
| 🔄 **自动重连** | 断线自动重连，稳定可靠 |
| 🚀 **开机自启** | 支持设置开机自动启动 |

---

## 🚀 快速开始

### 1️⃣ 下载安装

从 [GitHub Releases](https://github.com/kevinlasnh/Voice-Coding/releases/latest) 下载：

- **Windows 电脑端**: `voicing.exe`
- **Android 手机端**: `voicing.apk`

### 2️⃣ 启动电脑端

1. 双击运行 `voicing.exe`
2. 系统托盘出现 Voicing 图标 ✅
3. 程序自动启动 UDP 广播服务

### 3️⃣ 安装手机端

1. 将 `voicing.apk` 传输到 Android 手机
2. 安装 APK
3. **开启 Windows 移动热点**
4. 手机连接电脑热点
5. 打开 Voicing App → **自动连接** ✅

### 4️⃣ 开始使用

1. 在电脑上点击输入位置（VS Code、Word、浏览器等）
2. 在手机 App 中输入文字
3. 按回车键发送
4. 文字自动出现在电脑光标处！

---

## 📥 下载

| 平台 | 文件 | 下载 |
|------|------|------|
| Windows | voicing.exe | [Releases](https://github.com/kevinlasnh/Voice-Coding/releases/latest) |
| Android | voicing.apk | [Releases](https://github.com/kevinlasnh/Voice-Coding/releases/latest) |

---

## 📸 使用界面

### 电脑端托盘菜单

- 📡 同步输入 - 开关同步功能
- 🚀 开机自启 - 设置开机启动
- 📋 打开日志 - 查看运行日志
- 🚪 退出应用 - 关闭程序

### 手机端功能

- 自动连接电脑（UDP 发现）
- 文字输入 + 回车发送
- 🎯 **自动发送** - 语音输入实时同步
- 撤回上次输入
- 刷新连接

---

## 🎯 使用场景

| 场景 | 说明 |
|------|------|
| 🎤 **语音编程** | 用手机语音输入写代码注释、文档 |
| 📝 **长文输入** | 躺在沙发上用手机给电脑打字 |
| 🌍 **多语言输入** | 利用手机更好的输入法输入各种语言 |
| 🎮 **游戏聊天** | 全屏游戏时用手机打字 |

---

## 🔧 系统要求

### 电脑端
- Windows 10/11 (64位)
- 无需安装额外运行时

### 手机端
- Android 5.0+ (API 21+)
- 与电脑在同一移动热点下

---

## 📁 项目结构

```
Voicing/
├── pc/                     # PC 端源码 (Python)
│   ├── voice_coding.py     # 主程序
│   └── requirements.txt    # Python 依赖
├── android/voice_coding/   # Android 端 (Flutter)
│   ├── lib/main.dart       # 主程序
│   └── pubspec.yaml        # Flutter 依赖
├── .github/workflows/      # GitHub Actions CI/CD
│   └── release.yml         # 自动构建发布
├── CHANGELOG.md            # 更新日志
├── LICENSE                 # MIT 许可证
└── README.md               # 本文件
```

---

## 🛠️ 开发

### 环境准备

```bash
# 克隆仓库
git clone https://github.com/kevinlasnh/Voice-Coding.git
cd Voice-Coding

# PC 端
cd pc
pip install -r requirements.txt
python voice_coding.py --dev

# Android 端
cd android/voice_coding
flutter pub get
flutter run
```

### 打包发布

```bash
# PC 端打包
cd pc
pyinstaller --onefile --windowed --name=VoiceCoding voice_coding.py

# Android 端打包
cd android/voice_coding
flutter build apk --release
```

---

## ❓ 常见问题

### Q: 手机无法自动连接电脑？

1. 确保电脑和手机在**同一移动热点**下
2. 检查电脑防火墙是否允许 UDP 端口 9530
3. 点击手机端"刷新连接"手动重试

### Q: 如何查看日志？

右键托盘图标 → 点击"打开日志" → 自动打开当天日志文件

日志位置：`%APPDATA%\Voicing\logs\`

### Q: 文字输入到了错误的位置？

确保在按回车发送前，电脑上的光标已经在正确的输入位置。

---

## 📝 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

[MIT License](LICENSE)

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/kevinlasnh">kevinlasnh</a>
</div>
