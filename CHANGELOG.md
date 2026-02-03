# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-02-03

> **重大更新** - 架构简化，专注 PC + Android 双端体验

### ✨ 新增功能

- **UDP 自动发现** 📡
  - 手机 APK 自动发现并连接 PC 服务器
  - PC 端每 2 秒广播服务器信息（IP、端口、设备名）
  - Android 端监听 UDP 广播端口 9530
  - 无需手动配置 IP 地址，支持任意网段
  - 兼容非默认热点 IP（如 192.168.0.1、10.0.0.1 等）

- **撤回功能** 🔄
  - Android 端可恢复最近发送的文本
  - 点击"撤回上次输入"即可恢复

### 🗑️ 移除功能

- Web 端功能（HTTP/HTTPS 服务器和 Web UI）
- PWA 安装支持
- ngrok 隧道功能

### 🔧 变更优化

- **架构简化** - 专注于 PC EXE + Android APK 双端
- **依赖精简** - 移除 cryptography、pyngrok、pyyaml
- **包名更新** - Android 应用 ID: `com.voicecoding.app`
- **构建优化** - GitHub Actions 配置更新

### 📦 下载

- [Android APK](https://github.com/kevinlasnh/Voice-Coding/releases/latest) - 安装到手机
- [Windows EXE](https://github.com/kevinlasnh/Voice-Coding/releases/latest) - 电脑端运行

---

## [1.8.0] - 2026-02-03

### ✨ 新增功能

- **Windows 11 Fluent Design 风格托盘菜单** 🎨
  - 深色半透明背景
  - 圆角设计 + 柔和阴影
  - 滑出动画效果
  - 悬停高亮效果

- **日志系统** 📋
  - 日志文件位置：`%APPDATA%\VoiceCoding\logs\`
  - 托盘菜单"打开日志"快捷入口

### 🐛 修复问题

- PyQt5 菜单悬停高亮效果
- 菜单点击崩溃问题
- 菜单位置对齐问题

---

## [1.6.0] - 2026-02-02

### ✨ 新增功能

- **手动刷新连接** - Android 端新增"刷新连接"按钮
- **PC 热重启脚本** - 开发快速重启

### 🎨 UI 重新设计

- 状态栏连接状态 + 刷新按钮分栏显示
- 输入框配色与状态栏统一
- 移除输入框边框，简洁统一

---

## [1.0.0] - 2026-01-21

### 🎉 首次发布

- **PC 端**：系统托盘应用，接收手机文本并在光标处输入
- **Android 端**：Flutter 原生应用
- **WebSocket** 实时通信
- **开机自启**功能
- **自动断线重连**
- **Anthropic 风格 UI 设计**
