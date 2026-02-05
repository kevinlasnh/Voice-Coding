<div align="center">

<h1>Voicing</h1>

<img src="android/voice_coding/assets/icons/icon_1024.png" width="180" alt="Voicing App Icon" style="border-radius: 50%;">

<br>

**和 AI 吵架，嘴比手快**

用手机语音输入，让文字直接出现在电脑光标处

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/kevinlasnh/Voicing)](https://github.com/kevinlasnh/Voicing/releases/latest)

[为什么需要](#-为什么需要) • [快速开始](#-快速开始) • [下载](#-下载)

</div>

## 💡 为什么需要

和 AI 对话时，打字太慢？思路被键盘打断？

**Voicing** 让你用手机语音输入，文字实时出现在电脑的任意光标位置。

- 在 Claude Code 里用语音写 prompt
- 在 ChatGPT 网页里用语音提问
- 在任何需要打字的地方，用嘴代替手

手机语音输入法（讯飞、搜狗、百度）的识别准确率已经很高了，为什么不用起来？

## 🚀 快速开始

### 1️⃣ 下载安装

从 [GitHub Releases](https://github.com/kevinlasnh/Voicing/releases/latest) 下载：

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

## 📥 下载

| 平台 | 文件 | 下载 |
|------|------|------|
| Windows | voicing.exe | [Releases](https://github.com/kevinlasnh/Voicing/releases/latest) |
| Android | voicing.apk | [Releases](https://github.com/kevinlasnh/Voicing/releases/latest) |

## 📱 手机端使用

1. 打开 App，等待自动连接电脑（状态栏显示"已连接"）
2. 点击输入框，切换到语音输入法
3. 说话，文字会出现在输入框中
4. **自动发送模式**：语音输入完成后自动发送到电脑
5. **手动发送模式**：按回车键发送

**菜单功能**（点击右上角"更多功能操作"）：
- 刷新连接 - 重新连接电脑
- 撤回上次输入 - 恢复刚才发送的文字
- 自动发送 - 开关自动发送模式

## 💻 电脑端使用

运行 `voicing.exe` 后，程序在系统托盘运行。

**右键托盘图标**：
- 同步输入 - 开关接收手机文字
- 开机自启 - 设置开机自动启动
- 打开日志 - 查看运行日志
- 退出应用 - 关闭程序

**图标状态**：
- 🔵 闪烁 = 等待手机连接
- 🟢 常亮 = 已连接
- ⚫ 灰色 = 同步已关闭

## 🎯 使用场景

| 场景 | 说明 |
|------|------|
| 🤖 **和 AI 对话** | Claude、ChatGPT、Copilot...用嘴比用手快 |
| 💻 **写代码注释** | 语音输入比打字轻松多了 |
| 📝 **长文输入** | 躺在沙发上用手机给电脑打字 |

## 🔧 系统要求

### 电脑端
- Windows 10/11 (64位)
- 无需安装额外运行时

### 手机端
- Android 5.0+ (API 21+)
- 与电脑在同一移动热点下

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

## 🛠️ 开发

### 环境准备

```bash
# 克隆仓库
git clone https://github.com/kevinlasnh/Voicing.git
cd Voicing

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

## 📝 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

[MIT License](LICENSE)

<div align="center">
  Made with ❤️ by <a href="https://github.com/kevinlasnh">kevinlasnh</a>
</div>
