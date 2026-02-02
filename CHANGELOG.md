# Changelog / 更新日志

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
