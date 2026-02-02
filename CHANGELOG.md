# Changelog / 更新日志

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.3] - 2026-02-02

### Fixed / 修复
- 🐛 **WebSocket 连接** - 修复 `Uri.parse()` 调用，移除不必要的 `requestFocus()`

### Changed / 变更
- 📄 **CLAUDE.md** - 完善开发规范文档，明确 CHANGELOG 更新流程

---

## [1.3.2] - 2026-02-02

### Changed / 变更
- ↩️ **UI 回退** - 回退到原始橙色主题设计
- 📦 安装 ui-ux-pro-max Skill 作为设计参考

---

## [1.3.1] - 2026-02-02

### Added / 新增
- 📄 **CLAUDE.md** - 开发规范文档

### Changed / 变更
- ✨ **输入框优化** - 文字靠上对齐，5行最小高度
- 🧹 **仓库清理** - 移除 IDE 文件和生成产物
- ⚙️ **Gradle 配置** - 升级到 8.11.1，配置代理支持

### Fixed / 修复
- 🐛 修复 Dart 编译错误（Uri.parse 和 FocusNode）
- 🐛 配置 Java 21 解决 Gradle 兼容性问题

---

## [1.3.0] - 2026-02-02

### Added / 新增
- 📱 **Android 原生应用** - Flutter 开发
  - WebSocket 实时通信
  - 自动重连机制
  - 连接状态显示
  - Anthropic 风格深色主题 UI
- 🤖 **GitHub Actions 自动构建**
  - 每次提交自动构建 APK
  - 自动发布到 GitHub Releases
  - 无需本地安装 Android SDK

### Changed / 变更
- 📦 新增 `android/` 目录存放 Flutter 项目
- 📁 APK 构建产物存放于 `android/apk/` 目录

### Technical / 技术
- Flutter 3.24.5 + Dart 3.5.4
- Material Design 3 深色主题
- WebSocket 通信协议

---

## [1.2.0] - 2026-02-02

### Added / 新增
- 🌐 **ngrok 隧道支持** - 解决移动端 PWA 安装问题
  - 使用 ngrok 提供的 HTTPS 隧道和有效 SSL 证书
  - 托盘菜单新增 ngrok 开关选项
  - 自动复制 ngrok URL 到剪贴板
  - 显示更清晰的连接状态信息
- 📦 新增 pyngrok 和 pyyaml 依赖

### Fixed / 修复
- 🐛 修复证书生成中 `ipaddress.IPv4Address()` 使用问题
- 🐛 修复 HTTPS 服务器启动时的证书加载问题

### Changed / 变更
- 🔄 菜单项重新排序：ngrok 选项置顶以便快速访问
- 📝 "Enable HTTPS" 改名为 "Enable HTTPS (local)" 以区分本地和 ngrok HTTPS

### Technical / 技术
- ngrok 隧道使用 `bind_tls=True` 强制 HTTPS 连接
- 支持动态 URL 获取和显示

---

## [1.1.0] - 2026-02-02

### Added / 新增
- 🔒 HTTPS 服务器支持（自签名证书），启用 PWA 安装功能
- 📲 PWA (Progressive Web App) 完整支持
  - Service Worker 注册和缓存
  - beforeinstallprompt 事件处理
  - 应用安装监听
- 🔐 托盘菜单新增 HTTPS 开关选项
- 📜 自动生成自签名 SSL 证书（支持常见局域网 IP）

### Changed / 变更
- ✨ manifest.json 新增 `id` 字段，提升浏览器识别能力
- 🌐 显示 IP 时优先显示 HTTPS 地址（如已启用）
- 📦 新增 cryptography 依赖用于证书生成

### Fixed / 修复
- 🐛 修复 Service Worker 未注册导致 PWA 无法安装的问题
- 🐛 修复移动端浏览器因缺少 HTTPS 而拒绝安装 PWA 的问题

### Technical / 技术
- 证书支持多种常见内网 IP（192.168.137.1, 192.168.0.1, 192.168.1.1, 10.0.0.1）
- 证书有效期 10 年，自动生成并复用
- 支持 OpenSSL 和 cryptography 两种证书生成方式

---

## [1.0.0] - 2026-01-21

### Added / 新增
- 🎉 初始版本发布
- 📱 Web 客户端：手机浏览器直接访问，无需安装 App
- 💻 PC 端系统托盘应用
- 🔗 WebSocket 实时通信
- 📝 文本整包传输到电脑光标处
- ⚡ 开机自启功能
- 🔄 自动断线重连
- 🎨 Anthropic 风格 UI 设计
- 📊 连接状态实时显示
- 🖥️ 设备名称显示

### Features / 功能
- 单实例运行保护
- 托盘菜单：IP 显示、同步开关、开机自启
- 固定高度 Panel，适配手机浏览器
- 深色主题界面

### Technical / 技术
- Python 后端 + 原生 JavaScript 前端
- PyInstaller 单文件打包
- HTTP + WebSocket 双协议服务

---

## [Unreleased] - 开发中

### Planned / 计划中
- [ ] 多语言支持
- [ ] 自定义快捷键
- [ ] 历史记录功能
- [ ] 剪贴板同步
- [ ] macOS 支持
