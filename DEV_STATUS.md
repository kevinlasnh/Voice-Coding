# 开发状态 (Development Status)

> 最后更新：2026-02-03

---

## 🎉 v2.0.1 发布成功！

**最新 Release**: [v2.0.1](https://github.com/kevinlasnh/Voice-Coding/releases/tag/v2.0.1)

包含文件：
- ✅ `voice-coding.apk` - Android 安装包
- ✅ `voice-coding.exe` - Windows 电脑端

---

## ✅ 已完成功能

### 核心功能
- [x] WebSocket 实时通信 (PC:9527)
- [x] UDP 自动发现 (端口 9530)
- [x] Android 文字输入 + 发送
- [x] Android 撤回功能
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

### 文档
- [x] README.md 重写
- [x] CHANGELOG.md 更新

---

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
Voice-Coding/
├── pc/                     # PC 端 (Python)
│   ├── voice_coding.py     # 主程序
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

| 端 | 技术 |
|---|------|
| PC | Python 3.14, PyQt5, websockets, pyautogui |
| Android | Flutter 3.27.0, Dart, WebSocket |
| CI/CD | GitHub Actions ✅ |

---

## 📅 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v2.0.1 | 2026-02-03 | 修复 CI/CD 构建 |
| v2.0.0 | 2026-02-03 | UDP 自动发现 + 架构简化 |
| v1.8.0 | 2026-02-03 | Windows 11 Fluent Design |
