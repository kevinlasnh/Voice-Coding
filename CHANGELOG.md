# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.3.0] - 2026-02-04

### 🎨 品牌更新

- **应用重命名：Voice Coding → Voicing** 🎯
  - 更现代、简洁的品牌名称
  - **Android 端**：
    - `AndroidManifest.xml` 应用标签更新
    - `pubspec.yaml` 包名更新
    - `main.dart` 应用标题更新
  - **PC 端**：
    - 应用名称、互斥锁名称、日志目录全部更新
    - 托盘提示文字更新
    - 错误消息更新

### 🔧 构建修复

- **Flutter 构建 Java 版本问题修复**
  - 问题：系统 JAVA_HOME 指向 Java 25，导致 Gradle 构建失败
  - 错误特征：`Error resolving plugin > 25.0.1`
  - 解决：在 `gradle.properties` 中指定 Java 21 路径
  - 新增规则到 `CLAUDE.md` 防止再次发生

- **Windows EXE 图标修复** 🎯
  - 问题：GitHub Actions 构建的 EXE 缺少图标资源
  - 表现：EXE 文件图标为默认图标，托盘图标显示为纯蓝色
  - 解决：PyInstaller 添加 `--icon` 和 `--add-data` 参数
  - 新增 PNG 转 ICO 步骤

- **Android 网络权限修复** 🔥
  - 问题：AndroidManifest.xml 缺少网络权限声明
  - 表现：APK 无法连接 PC 端
  - 解决：添加 INTERNET、ACCESS_NETWORK_STATE、ACCESS_WIFI_STATE 权限

### 🎯 PC 端托盘图标优化

- **圆形图标**：托盘图标改为圆形外轮廓，与微信等主流应用风格一致
- **图标放大**：256px 高清图标，系统自动缩放
- **悬停提示**：鼠标悬停显示 "Voicing" 提示窗口
- **只响应右键**：左键不再触发菜单，只有右键才显示菜单

### 🐛 Bug 修复

- **闪烁均匀化**：预缓存所有图标状态，解决闪烁时快时慢的问题
- **首次菜单加速**：预加载菜单组件，首次打开不再卡顿
- **闪烁速度**：调整为 200ms 间隔

### 📝 文档更新

- `CLAUDE.md` 新增 Flutter 构建 Java 版本规则
- 记录本机 Java 21 路径：`C:\dev\java21\jdk-21.0.2`
- 记录 Flutter 启动命令
- **README 添加应用图标** - 在标题区域展示 128px 应用图标

---

## [2.2.1] - 2026-02-04

### 🎨 优化改进

- **PC 端托盘图标优化** 🎯
  - 透明背景：去掉深蓝色底色，改为透明背景
  - 放大图标：麦克风占满更多空间，托盘中更清晰
  - 简化状态逻辑：
    - 已连接：正常彩色图标（去掉绿色边框）
    - 等待连接：图标闪烁（透明度变化）
    - 暂停：灰色图标（去掉暂停条）

### 🔧 技术改进

- 重新生成 `pc/assets/icon_1024.png` 为透明背景版本
- 简化 `create_icon_connected()` 函数，直接返回原图
- 简化 `create_icon_paused()` 函数，只做灰度转换

---

## [2.2.0] - 2026-02-04

### 🎨 新增功能

- **自定义应用图标** 🎯
  - 设计了专属 Voice Coding 图标（麦克风+声波元素）
  - 蓝色渐变配色（#4A90E2 → #00D4FF）
  - 深色背景（#1A1A2E）
  - **Android 端**：支持自适应图标（Adaptive Icon）
  - **PC 端**：托盘图标同步更新为新设计
    - 已连接：图标 + 绿色边框
    - 等待连接：正常图标（闪烁动画）
    - 暂停：灰度图标 + 暂停条标记

### 🔧 技术改进

- **Android 端**
  - 添加 `flutter_launcher_icons` 依赖自动生成各尺寸图标
  - 配置 `assets/icons/` 目录存放原始图标资源
  - 生成完整 mipmap 资源集（mdpi ~ xxxhdpi）
  - 配置 `mipmap-anydpi-v26` 自适应图标 XML

- **PC 端**
  - 新增 `load_base_icon()` 函数加载 PNG 图标
  - 重写 `create_icon_*()` 系列函数使用新图标
  - 更新 `ModernTrayIcon` 类使用新图标
  - 更新 `VoiceCoding.spec` 打包配置

### 📁 新增文件

- `android/voice_coding/assets/icons/icon_1024.png` - Android 原始设计稿
- `pc/assets/icon_1024.png` - PC 端图标资源
- `drawable-*/ic_launcher_foreground.png` - 前景图层
- `mipmap-anydpi-v26/ic_launcher.xml` - 自适应图标配置
- `values/colors.xml` - 背景色定义

---

## [2.1.0] - 2026-02-03

### ✨ 新增功能

- **自动发送** 🎯
  - 语音输入实时同步到电脑
  - 智能检测输入法 composing 状态（下划线）
  - 下划线消失时自动发送（输入法完成优化后）
  - 增量发送：只发送新增内容，不影响已有文本
  - 支持连续多段语音输入
  - 开关状态记忆：重启APP后保持上次的开关状态

### 🔧 技术改进

- 使用 `TextEditingController.addListener()` 监听文本状态变化
- 检测 `composing.isValid` 判断输入法是否正在组合文本
- 自动重置 `_lastSentLength` 防止发送失败

---

## [2.0.1] - 2026-02-03

### 🐛 修复问题

- **GitHub Actions 构建修复** - 修复 Android APK 构建失败问题
  - 移除 gradle.properties 中的本地代理配置
  - 修正 Gradle wrapper 配置

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

- [Android APK](https://github.com/kevinlasnh/Voicing/releases/latest) - 安装到手机
- [Windows EXE](https://github.com/kevinlasnh/Voicing/releases/latest) - 电脑端运行

---

## [1.8.0] - 2026-02-03

### ✨ 新增功能

- **Windows 11 Fluent Design 风格托盘菜单** 🎨
  - 深色半透明背景
  - 圆角设计 + 柔和阴影
  - 滑出动画效果
  - 悬停高亮效果

- **日志系统** 📋
  - 日志文件位置：`%APPDATA%\Voicing\logs\`
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
