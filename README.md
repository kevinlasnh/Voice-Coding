# Voice Coding 语音编程

<p align="center">
  <strong>手机输入，电脑打字</strong><br>
  轻量级手机-电脑文本桥接工具
</p>

<p align="center">
  <a href="#功能特性">功能</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#使用场景">场景</a> •
  <a href="#开发">开发</a> •
  <a href="#许可证">许可证</a>
</p>

---

## 功能特性

| 功能 | 描述 |
|------|------|
| 📱 **手机输入** | 在手机上打字或使用语音输入 |
| 💻 **电脑输出** | 文本瞬间出现在电脑光标处 |
| 🔗 **局域网直连** | 无需云端，无需服务器，端对端直连 |
| 📦 **整包传输** | 文本整包发送，顺序保证 |
| 🖥️ **系统托盘** | 静默后台运行，托盘图标控制 |
| 🌐 **Web 客户端** | 手机端无需安装 App，浏览器直接访问 |
| 🔄 **自动重连** | 断线自动重连，稳定可靠 |
| ⚡ **开机自启** | 支持设置开机自动启动 |

## 系统要求

### PC 端
- Windows 10/11
- 无需安装额外运行时

### 手机端
- 任意现代浏览器（推荐 Edge/Chrome）
- 与电脑在同一局域网/热点下

## 快速开始

### 1️⃣ 启动电脑端

1. 运行 `VoiceCoding.exe`
2. 系统托盘出现图标，表示服务已启动
3. 右键托盘图标可查看本机 IP 地址

### 2️⃣ 手机连接

1. 确保手机和电脑在**同一网络**下（WiFi 或手机热点）
2. 手机浏览器访问：`http://<电脑IP>:9527`
   - 例如：`http://192.168.1.100:9527`
3. 页面显示"已连接"即可使用

### 3️⃣ 开始使用

1. 在电脑上点击你想输入文字的位置（如 VS Code、Word、浏览器等）
2. 在手机网页输入框中输入文字（支持语音输入）
3. 点击"发送到电脑"
4. 文字自动出现在电脑光标处！

## 使用场景

- 🎤 **语音编程** - 用手机语音输入写代码注释
- 📝 **长文输入** - 躺在沙发上用手机给电脑打字
- 🌍 **多语言输入** - 利用手机更好的输入法输入各种语言
- 🎮 **游戏聊天** - 全屏游戏时用手机打字

## 托盘菜单

右键点击系统托盘图标：

| 菜单项 | 功能 |
|--------|------|
| **IP 地址** | 显示本机 IP，点击可复制 |
| **启用/禁用同步** | 临时开关文本同步功能 |
| **开机自启** | 设置是否开机自动启动 |
| **退出** | 关闭程序 |

## 项目结构

```
Voice-Coding/
├── pc/                     # PC 端源码
│   ├── voice_coding.py     # 主程序
│   ├── requirements.txt    # Python 依赖
│   └── web/               # Web 前端
│       ├── index.html     # 手机端页面
│       ├── manifest.json  # PWA 配置
│       └── sw.js          # Service Worker
├── CHANGELOG.md          # 更新日志
├── LICENSE               # 许可证
└── README.md             # 本文件
```

## 开发

### 环境准备

```bash
# 克隆仓库
git clone https://github.com/kevinlasnh/Voice-Coding.git
cd Voice-Coding/pc

# 安装依赖
pip install -r requirements.txt

# 运行开发版本
python voice_coding.py
```

### 打包发布

```bash
# 使用 PyInstaller 打包
pyinstaller --onefile --noconsole --name VoiceCoding --add-data "web;web" voice_coding.py
```

打包后的可执行文件位于 `dist/VoiceCoding.exe`

### 技术栈

- **后端**: Python 3.10+, WebSocket, HTTP Server
- **前端**: HTML5, CSS3, JavaScript (原生)
- **打包**: PyInstaller
- **依赖**: websockets, pyautogui, pystray, Pillow

## 常见问题

### Q: 手机无法连接电脑？

1. 确保手机和电脑在同一网络
2. 检查电脑防火墙是否阻止了 9527 端口
3. 尝试关闭电脑防火墙测试

### Q: 文字输入到了错误的位置？

确保在点击"发送"前，电脑上的光标已经在正确的输入位置。

### Q: 如何使用手机热点连接？

1. 开启手机热点
2. 电脑连接手机热点
3. 访问热点网关地址（通常是 `192.168.43.1:9527`）

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

[MIT License](LICENSE)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/kevinlasnh">kevinlasnh</a>
</p>
