# 开发状态 (Development Status)

> 最后更新：2026-02-04

## 🎉 v2.3.1 已发布！

**最新 Release**: [v2.3.1](https://github.com/kevinlasnh/Voicing/releases/tag/v2.3.1)

包含文件：
- ✅ `voicing.apk` - Android 安装包（网络权限已修复，可正常连接）
- ✅ `voicing.exe` - Windows 电脑端（EXE图标 + 托盘图标正常显示）

---

## ✅ 已完成功能

### 核心功能
- [x] WebSocket 实时通信 (PC:9527)
- [x] UDP 自动发现 (端口 9530)
- [x] Android 文字输入 + 发送
- [x] Android 撤回功能
- [x] **自动发送** 🎯 - 语音输入实时同步
- [x] PC 端自动输入到光标位置
- [x] Windows 11 Fluent Design 托盘菜单
- [x] 日志系统
- [x] 开机自启
- [x] 自动断线重连

### 架构优化
- [x] 移除 Web 端功能
- [x] 精简依赖 (移除 cryptography, pyngrok, pyyaml)
- [x] 包名更新：`com.voicecoding.app`
- [x] Gradle wrapper 文件已添加到仓库
- [x] **GitHub Actions CI/CD 正常工作** 🎉

### 构建修复 (v2.3.1)
- [x] **Android 网络权限** - 添加 INTERNET 等权限，修复 APK 无法连接
- [x] **EXE 图标打包** - PyInstaller 添加 `--icon` 和 `--add-data`
- [x] **ICO 多尺寸** - 包含 256/128/64/48/32/16px

### UI/UX
- [x] **自定义应用图标** 🎨 - 麦克风+声波设计，蓝色渐变
- [x] 自适应图标（Adaptive Icon）支持
- [x] flutter_launcher_icons 自动化配置
- [x] **PC 端托盘图标优化** ✅
  - 圆形外轮廓，与微信风格一致
  - 256px 高清图标
  - 悬停提示（tooltip）
  - 只响应右键菜单
  - 图标缓存，闪烁均匀
  - 菜单预加载，首次打开快速

### 文档
- [x] README.md 重写
- [x] CHANGELOG.md 更新

---

## 🚧 待完成任务 (TODO)

暂无待完成任务。

## 🚀 本地构建命令

### PC 端
```bash
cd pc
pip install -r requirements.txt
pyinstaller --onefile --windowed --name=VoiceCoding voice_coding.py
```

### Android 端
```bash
cd android/voice_coding
flutter pub get
flutter build apk --release
# 输出: build/app/outputs/flutter-apk/app-release.apk
```

---

## 📁 项目结构

```
Voicing/
├── pc/                     # PC 端 (Python)
│   ├── voice_coding.py     # 主程序
│   ├── assets/
│   │   ├── icon_1024.png   # 原始图标
│   │   └── icon.ico        # EXE 图标
│   └── requirements.txt
├── android/voice_coding/   # Android 端 (Flutter)
│   ├── lib/main.dart
│   └── pubspec.yaml
├── .github/workflows/
│   └── release.yml         # CI/CD 配置 ✅
├── CHANGELOG.md
├── README.md
└── DEV_STATUS.md           # 本文件
```

---

## 📝 技术栈

| 端      | 技术                                      |
| ------- | ----------------------------------------- |
| PC      | Python 3.14, PyQt5, websockets, pyautogui |
| Android | Flutter 3.27.0, Dart, WebSocket           |
| CI/CD   | GitHub Actions ✅                          |

---

## 📅 版本历史

| 版本   | 日期       | 说明                     |
| ------ | ---------- | ------------------------ |
| v2.3.1 | 2026-02-04 | 网络权限 + EXE图标修复 🔥 |
| v2.3.0 | 2026-02-04 | 重命名 Voicing + 托盘优化 |
| v2.2.0 | 2026-02-04 | 自定义应用图标 🎨         |
| v2.1.0 | 2026-02-03 | 自动发送 - 语音实时同步  |
| v2.0.1 | 2026-02-03 | 修复 CI/CD 构建          |
| v2.0.0 | 2026-02-03 | UDP 自动发现 + 架构简化  |
| v1.8.0 | 2026-02-03 | Windows 11 Fluent Design |
