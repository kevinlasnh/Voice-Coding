# 发现与决策

## 需求
- 用户要求全面检查当前仓库是在做什么，需要输出仓库用途、主要组成、运行方式和风险点。

## 研究发现
- 初始顶层结构显示仓库包含 `pc/`、`android/`、`protocol/` 三个主要目录，并有中英文 README、CHANGELOG、CONTRIBUTING、LICENSE。
- PC 端目录包含 Python 文件：`voice_coding.py`、`voicing_protocol.py`、`network_recovery.py`、`platform_*` 等。
- Android 端目录包含 `voice_coding` 工程。
- 协议目录包含 `voicing_protocol_contract.json`。
- ByteRover 长期记忆对 `Voicing 仓库 用途 架构`、`voice coding PC Android protocol`、`Voicing voicing_protocol network recovery` 三个查询均无匹配记录，说明当前主题尚未沉淀到长期知识库。
- README 明确项目定位：Voicing 将手机语音输入法输出实时发送到电脑光标处，面向和桌面 AI Agent 对话时减少打字。
- 当前版本号为 2.9.4；桌面端支持 Windows/macOS/Linux，手机端为 Android；README 明确 macOS 和 Linux 桌面端仍处内测。
- PC 端是 Python + PyQt5 托盘应用：后台启动 WebSocket server，托盘菜单提供显示 QR、同步输入、开机自启、打开日志、退出。
- Android 端是 Flutter 应用：扫码 PC QR 后做 WebSocket probe，保存 `device_id` 和候选 IP 池；启动、恢复前台、手动刷新时按保存的 IP 候选重连，不再依赖 UDP 自动发现。
- 双端协议由 `protocol/voicing_protocol_contract.json` 固化：WebSocket 端口 9527，历史 UDP discovery 端口 9530，消息类型包括 `text`、`ping`、`connected`、`ack`、`pong`、`sync_state`、`sync_disabled`。
- PC 端收到文本后通过剪贴板粘贴到当前光标处；`auto_enter` 为真时延迟后补发 Enter。
- Android 端有 shadow/commit 发送模式：语音输入组合结束后发送增量文本，静默窗口后 finalize；Auto Enter 通过空内容 commit 消息触发。
- Android 原生层使用 OkHttp，并尝试绑定物理且非 VPN 的 WiFi Network，同时通过 EventChannel 回传键盘高度。
- Release 流程由 GitHub Actions tag `v*` 触发，构建 Android APK、Windows EXE、macOS DMG、Linux binary，并生成 SHA256SUMS。
- 当前本地环境缺少 `python` 命令、Java、Flutter/Dart；`python3` 可用。
- `python3 -m py_compile` 对 PC 端主要 Python 文件通过。
- `python3 -m unittest discover -s pc/tests` 运行 29 个测试，其中 27 个通过，2 个因当前环境缺少 `PyQt5` 导致导入失败。
- `.gitignore` 当前忽略 `findings.md`、`progress.md`、`task_plan.md`、`CLAUDE.md`、`AGENTS.md`，这与本仓 AGENTS 中“PWF 可本地 Git 跟踪、远端 push 拦截”的策略存在不一致。
- 已根据仓库用途初始化根目录 `CLAUDE.md` 与 `AGENTS.md`；两份文件均 165 行，除第一行 H1 外正文通过 `diff` 校验一致。
- Ubuntu/Linux review：当前系统是 Ubuntu 24.04.4 LTS、GNOME、Wayland 会话；仓库文档要求 Ubuntu 22.04+ GNOME X11，代码也会在 Linux Wayland 下主动拒绝启动。
- 当前系统已安装 `Ubuntu on Xorg` 会话入口，因此可以通过登出后选择 Xorg 会话满足会话前提。
- 当前全局 Python 环境缺少 `PyQt5`、`websockets`、`pyautogui`、`pyperclip`、`qrcode`、`psutil`；`python3 pc/voice_coding.py --dev` 直接失败于 `ModuleNotFoundError: No module named 'PyQt5'`。
- 当前系统没有 `python3 -m pip` / `ensurepip`，但 `venv` 模块存在；若走源码开发，需要先补 pip/依赖安装路径。
- 当前系统缺少 Linux CI 中安装的 `libxcb-cursor0`；`libegl1`、`libdbus-1-3`、`libxkbcommon-x11-0` 已安装。
- 当前系统有 `ip`、`xdg-open`、`wl-copy`、`gnome-shell`、`gsettings`、`loginctl`；没有 `xclip` / `xsel`。在 X11 下 `pyperclip` 通常需要 `xclip` 或 `xsel`，否则剪贴板粘贴路径可能失败。
- 当前网络接口 `wlp0s20f3` 有私有 IPv4 `192.168.43.3/24` 和 broadcast，符合代码对 Linux 可广播私有 IPv4 的筛选前提。
- Linux 相关且不依赖 PyQt 导入 `voice_coding.py` 的单元测试通过：`test_platform_utils`、`test_platform_autostart`、`test_platform_keyboard`、`test_network_recovery`、`test_device_identity`、`test_protocol_contract` 共 27 个测试通过。
- 下次继续任务已明确为“Ubuntu 实机可用性修复”：先切到 `Ubuntu on Xorg`，再补系统依赖和 Python runtime，最后做 PC 启动与 Android 扫码端到端验证。
- 2026-06-17 环境复查：`python3-pip`、`python3-venv`、`python3-pyqt5`、`python3-psutil`、`python3-pil` 已安装；`python3 -m pip` 可用；`PyQt5` 已可导入。
- 2026-06-17 环境复查：当前 shell 仍是 `XDG_SESSION_TYPE=wayland`，`platform_utils.ensure_runtime_supported()` 仍会阻止 Linux 桌面端启动，需切换到 `Ubuntu on Xorg`。
- 2026-06-17 环境复查：系统包仍缺 `libxcb-cursor0`、`xclip`、`xsel`；`libegl1`、`libdbus-1-3`、`libxkbcommon-x11-0` 已安装。
- 2026-06-17 环境复查：当前 Python 环境能导入 `PyQt5`、`psutil`、`PIL`，但缺少 `websockets`、`pyautogui`、`pyperclip`、`qrcode`；`pyinstaller` 也未安装。
- 2026-06-17 环境复查：按 `pc/requirements.txt` 版本约束，apt 版本的 `Pillow 10.2.0`、`PyQt5 5.15.10`、`psutil 5.9.8` 低于项目要求的 `Pillow~=12.2.0`、`PyQt5~=5.15.11`、`psutil~=7.2.0`，建议用项目 venv 安装 `pc/requirements.txt`，不要依赖系统 Python 包。
- 2026-06-17 代码层面检查：若目标是让 Voicing 在当前 Linux/Wayland 桌面上运行，主要改动集中在 PC 端后端/平台适配层，不需要修改 Android Flutter 前端或双端协议；PC 端 PyQt 托盘/QR UI 理论上可继续复用。
- 2026-06-17 代码层面检查：当前 Linux 阻断来自 `pc/platform_utils.py::ensure_runtime_supported()` 对 Wayland 的硬拒绝，以及 `pc/voice_coding.py::type_text()` 依赖 `pyperclip.copy/paste` + `pc/platform_keyboard.py::paste_from_clipboard()/press_enter()` 的 `pyautogui` 全局按键模拟路径。
- 2026-06-17 代码层面检查：若移除 Wayland 启动门禁而不替换输入后端，WebSocket/QR/托盘可能启动，但“文字进入当前光标”和 Auto Enter 仍很可能失败；真正需要设计的是 Linux Wayland 文本注入后端，而不是手机端 UI。
- 2026-06-17 GNOME Wayland 方案调研：当前系统是 Ubuntu 24.04.4 LTS、GNOME Shell 46.0、`XDG_SESSION_TYPE=wayland`；`xdg-desktop-portal`、`xdg-desktop-portal-gnome`、`xdg-desktop-portal-gtk` 均在运行。
- 2026-06-17 GNOME Wayland 方案调研：本机 `org.freedesktop.portal.RemoteDesktop` 暴露 `AvailableDeviceTypes=7`、`version=2`，包含 `NotifyKeyboardKeycode`、`NotifyKeyboardKeysym` 和 `ConnectToEIS`；键盘设备类型 bitmask 为 `1`。
- 2026-06-17 GNOME Wayland 方案调研：XDG RemoteDesktop portal 官方文档说明键盘事件必须在 Start 后且获得 KEYBOARD 权限后调用；`ConnectToEIS` 可返回 EIS fd，建立 EIS 后 Notify* 事件不可混用。
- 2026-06-17 GNOME Wayland 方案调研：Ubuntu 24.04 仓库包含 `libei1 1.2.1-1` 和 `liboeffis1 1.2.1-1`；包说明称 libei 面向 Wayland emulated input，oeffis 用于 XDG RemoteDesktop portal D-Bus 通信。
- 2026-06-17 GNOME Wayland 方案调研：`wtype` 只适用于支持 `virtual-keyboard` Wayland 协议的 compositor；GNOME Mutter 相关 issue 与搜索结果显示 GNOME 不支持该协议，因此不适合作为当前系统主方案。
- 2026-06-17 GNOME Wayland 方案调研：`ydotool` 通过 Linux `/dev/uinput` 创建设备，理论上可在 GNOME Wayland 下模拟 Ctrl+V/Enter，实现效果接近 Windows，但需要 `ydotoold` 和 `/dev/uinput` 权限/服务配置，安全边界更粗。
- 2026-06-17 推荐方向：长期/产品化优先使用 RemoteDesktop portal 的键盘权限来实现 GNOME Wayland 输入后端；快速本机可用可先实现 `wl-copy`/剪贴板 + `ydotool` 键盘事件 fallback。
- 2026-06-17 代码范围判断：改造应集中在 PC 端 `platform_keyboard.py`、`platform_utils.py`，并把 `voice_coding.py::type_text()` 里的剪贴板操作抽到平台输入后端；Android Flutter UI、协议 contract、QR/WebSocket 连接状态机无需先改。
- 2026-06-18 实现结果：已在 `pc/platform_keyboard.py` 落地 GNOME Wayland RemoteDesktop portal 键盘后端，Wayland 下粘贴与回车走 portal `NotifyKeyboardKeysym`，Windows/macOS/Linux X11 保持原有快捷键路径。
- 2026-06-18 实现结果：`pc/platform_utils.py` 的启动检查已改为能力检测；当前 GNOME Wayland 会话在 portal 键盘能力可用时可正常启动，不再被一刀切阻断。
- 2026-06-18 实现结果：`pc/voice_coding.py` 已把文本注入收口到平台键盘层，业务层不再直接操作 `pyperclip`。
- 2026-06-18 验证结果：`.venv/bin/python -m unittest discover -s pc/tests` 通过 63 项测试；`flutter analyze --no-fatal-infos --no-fatal-warnings` 与 `flutter test` 通过。
- 2026-06-18 验证结果：`timeout 5s .venv/bin/python pc/voice_coding.py --dev` 在当前 GNOME Wayland 会话下成功启动到 WebSocket 监听阶段，说明 Wayland 前置已具备可运行性。
- 2026-06-18 环境变更：已安装 `.venv`、`libxcb-cursor0`、`xclip`、`xsel`、Flutter 3.27.0 与 Android SDK command-line tools / platform-tools / android-35 / build-tools 35.0.0。

## 技术决策
| 决策 | 理由 |
|------|------|
| 先读 README/依赖/入口，再读核心代码 | 可以先建立项目边界，避免直接陷入实现细节 |
| 不安装缺失依赖 | 用户请求是仓库用途检查，不是环境修复；缺失依赖已作为验证限制记录 |
| `CLAUDE.md` 与 `AGENTS.md` 使用同一正文 | 满足仓库级跨工具同步约束，并让 Claude Code / Codex 读取到一致的项目规则 |
| 当前不安装依赖、不切换桌面会话 | 本次是 review；系统级安装和注销切换会话需要用户主动操作 |
| 将 Ubuntu 修复留作 Phase 8 pending | 用户要求下次再完成这些任务，当前只记录进度不做系统级改动 |

## 遇到的问题
| 问题 | 解决方案 |
|------|---------|
| 当前环境缺少 PyQt5 等 PC runtime 依赖，完整 PC 单元测试无法全部导入 | 记录失败原因；语法编译已通过，未做环境安装 |
| 当前环境缺少 Java、Flutter/Dart，无法本地执行 Android 测试和构建 | 记录环境限制；依据项目配置和 CI 工作流判断构建路径 |
| 当前 Ubuntu 会话是 Wayland | 切换到 `Ubuntu on Xorg`，否则 `ensure_runtime_supported()` 会主动报错 |
| 当前源码开发环境缺少 pip 和 PC runtime 依赖 | 安装 `python3-pip` 或创建可用 venv 后安装 `pc/requirements.txt` |
| 当前缺少 `xclip` / `xsel` | 在 X11 下补装其一，降低 `pyperclip` 剪贴板失败概率 |
| Android debug APK 构建缺 Android SDK | 已补 SDK；用户确认本次未改 Android native/Gradle，无需继续 APK 构建，因此中止构建并还原工具造成的 lock/权限变化 |

## 资源
- 本地仓库：`/home/kevinlasnh/Projects/Voicing`
- ByteRover 查询：无相关历史召回。

## 视觉/浏览器发现
- 未使用视觉或浏览器工具。

---
*每执行2次查看/浏览器/搜索操作后更新此文件*
*防止视觉信息丢失*

## 2026-07-21 冷启动 terminal 首次粘贴误判待验证现象

- 用户现场现象：GNOME Wayland 登录/开机后的首次手机语音文本，如果此前没有在 terminal 手动执行过 Ctrl+Shift+V，会被 Voicing 按 Ctrl+V 路径发送；同一会话后续第二、第三次仍持续误判。
- 用户观察到的恢复条件：先在 terminal 手动执行一次 Ctrl+Shift+V 并粘贴任意文本后，再使用 Voicing 时可正确走 terminal 粘贴行为。
- 当前仅把上述内容视为待验证现场证据；需要分别排查 AT-SPI 可访问性就绪、焦点/active fallback、500ms 投票、terminal cache、RemoteDesktop portal modifier 状态及剪贴板首次 owner 建立等机制。

## 2026-06-18 GNOME Wayland 托盘改造与 portal 输入修复

- 决策：Linux 托盘改用系统原生 `QMenu`，自定义 Fluent 菜单仅 Windows/macOS 保留。原因：自定义 `Qt.Popup` 菜单在 GNOME/Wayland 下有定位（GNOME 顶栏方向与 Windows 底部任务栏相反）、半透明+`QGraphicsDropShadowEffect` 黑块、Esc 失焦、`QSystemTrayIcon.geometry()` 无效等一堆问题；上次 `c2bcf71` 同时设 `setContextMenu` + Context 触发自定义菜单导致右键弹两个菜单。改原生菜单后这些问题随架构切换自动消失。
- 关键：Linux 右键（Context）必须交给 `setContextMenu`/宿主，不能在 `activated` 里再 `_popup_native_menu()`，否则双菜单叠加；左键/双击才手动 `native_menu.popup(QCursor.pos())`。
- Linux SNI/AppIndicator 宿主每次 `setIcon` 都可能重建图标 → 已连接后图标每 200ms 抖动。修法：`update_icon` 记录 `_current_icon_key`，状态未变跳过 `setIcon`。
- Wayland 禁止客户端自由定位顶层窗口，`move(-10000,-10000)+show()+hide()` 预热会让窗口短暂可见闪在左上角。Linux 改为 `ensurePolished()` + `layout().activate()`，不 `show()`。
- PyQt5 D-Bus uint32 序列化：Python `int` 默认序列化成 `'i'`；XDG portal 多个字段要 `'u'`。强制 uint32：`QDBusArgument.add(value, QMetaType.UInt)`。顶层参数用裸 `QDBusArgument`；`a{sv}` map 值用 `QVariant(QDBusArgument)`。已对 live GNOME portal 验证：`SelectDevices.types` 与 `NotifyKeyboardKeysym.state` 用此法通过；keysym 保持普通 int（本机 portal 内省期望 `(oa{sv}iu)`，而非 spec 的 `(oa{sv}uu)`）。
- GNOME RemoteDesktop portal **不能**持久授权：每次启动/重启必弹授权，无 `persist_mode`/预授权 API（GNOME issue #175）。这是 GNOME 安全设计，非 bug。当前"每次启动授权一次、退出自动失效"已是 portal 极限。
- 决策：保持 portal 默认。ydotool（绕开 portal，`/dev/uinput`）可在无弹窗一项上占优，但代价是系统级虚拟键盘权限降级 + 每用户都要配 + 不可分发；Voicing 是已发布应用，综合选 portal。ydotool 仅作可选 opt-in 留记，未实现。
- tvly SSL 根因不是 tvly 配置：`api.tavily.com` 直连可达，但 clash-verge 分流劫持到坏出口导致 SSL EOF。修法：`~/.bashrc` 加 `tvly()` 去掉代理变量直连。

## 2026-06-18 自定义菜单宽度特性 + QR 动画与 Wayland surface

- **Linux 托盘用系统原生 `QMenu`（上轮已切）**：对 `ModernMenuWidget` 的宽度/分隔条改动在 Linux 不可见；Linux 的分隔条来自 `_setup_native_context_menu` 的 `addSeparator()`，已删除。GNOME 原生 QMenu 宽度理论按文字自适应，但用户反馈仍"不自适应"，需复核具体表现。
- **PyQt5 顶层 Popup 窗口 adjustSize 宽度偏大**：实测 `ModernMenuWidget` `sizeHint=164`、`minimumSizeHint=164`、`minimumSize=0`，但 `adjustSize()` 给出 `200`（多约 36px，原因疑似 Qt 对顶层 Popup 窗口的调整逻辑）。修法：`show_at_position` 里 `adjustSize()` 后追加 `self.setFixedWidth(self.sizeHint().width())` 强制收紧，宽度随最长文字自适应。offscreen 实测收紧到 164。
- **QR 弹窗"下方第二个 QR"闪动根因（Wayland/Mutter）**：打开动画期间顶层窗口是大 `canvas_rect`（横跨托盘锚点→屏幕中心），动画 pixmap 的 QR 位于该旧缓冲**中部**（约 y400）。收尾 `_finish_open_animation` 要从 `canvas_rect` 切到 `end_rect`（原点从托盘→中心），若在**可见状态下** resize+move，Mutter 会把上一帧旧缓冲按**新原点**重显 → QR 出现在「中心 + y400 偏移」= 中心下方。修法：收尾先 `hide()` 解除 surface 映射（unmap），在不可见时完成 resize/move，再 `show()` 出最终容器画面——Mutter 只显示最终一帧。需注意：hide/show 抖动可能触发 `focusOutEvent` → `_maybe_close_on_focus_loss`；修法里收尾期间保持 `_animation_mode=True` 让该检查直接 return（`_animation_mode` 判断在 `_maybe_close_on_focus_loss` 开头）。
- **遗留**：第二版修法消除"下方第二个 QR"，但用户反馈 QR 到达中心时**自身闪动一次**（pixmap→container 切换那一帧，或 hide/show 引入的再显）。待定位：可能是 hide/show 本身的再显、或 pixmap（全对话框渲染）与最终 container 在中心位置不完全对齐导致的一帧跳变。
- **QR 闪动整体结论（重读 QRSuccessOverlay + QRCodeDialog 全生命周期后）**：两个闪动同根——"从右上角飞入"效果要求打开动画期顶层窗口是大 `canvas_rect`（横跨托盘→中心），收尾从 canvas 缩到 `end_rect`；而 Wayland/Mutter 上**任何收尾的 resize（可见→下方重影）或 hide/show remap（→自身闪动）都会闪**，二者是同一根问题的两面。根治只能从架构上消除收尾几何变化：窗口恒定 end_rect 尺寸，动画只做位置移动+内容缩放+淡入（A 方案，保留飞入）；或砍飞入改原地缩放淡入（B 方案，最稳）。待用户选。
- **GNOME 原生 QMenu 宽度偏大根因**：`actionGeometry` 显示每项占满整菜单宽（实测 `sizeHint=168` vs 最长文本"显示 QR 码"仅 84px），是默认 QMenu item 水平 padding（左勾选框位 + 右留白）过大。修法：stylesheet 仅收紧 item 内边距（`QMenu::item { padding: 6px 12px 6px 20px; }`），不改 QMenu 背景边框以保 GTK 原生外观；offscreen 实测 168→134。注：offscreen 用 Qt 默认 style，GNOME GTK 实际宽度不同，但收紧幅度应一致。

## 2026-06-19 QR 弹窗中心直接出现

- 用户选择 B 方案：不保留 QR 从托盘/右上角飞入。产品行为改为点击「显示 QR 码」后，QR 弹窗直接出现在屏幕中心。
- 实现决策：`QRCodeDialog` 不再使用跨锚点和中心的大 `canvas_rect`，也不再在打开/关闭时做 widget 快照缩放动画。这样从根上避开 Wayland/Mutter 对可见 resize、hide/show remap、旧 buffer 重显的处理差异。
- 代码清理：移除 QR 弹窗旧飞行动画相关状态和方法，包括 start rect、动画 pixmap、`contentRect` 属性、快照捕获、`_start_dialog_animation()` 与 `_finish_open_animation()`；保留 `QRSuccessOverlay` 的扫码成功对勾动画。
- 焦点边界：打开后短暂设置 `_ignore_focus_loss`，120ms 后通过 generation 校验解除，避免 Wayland show/activate 过程中的 focus-out 把刚出现的弹窗关闭；若弹窗已关闭或新一轮打开，旧 timer 不会影响当前状态。
- 验证：`py_compile`、`unittest discover -s pc/tests`（72 OK）、`git diff --check` 均通过。视觉闪动仍需用户在真实 GNOME Wayland 会话中手动确认。

## 2026-06-19 整体前端逻辑 Review

- **Android native WebSocket 发送失败不可被上层捕获**：`VoicingWebSocketSink.add()` 接口是 `void`，native 实现 `_NativeWifiWebSocketSink.add()` 内部 `unawaited(_idFuture.then(... MethodChannel.invokeMethod('sendWebSocketMessage') ...))`。Kotlin `sendWebSocketMessage` 在未连接时会 `result.error("not_connected", ...)`，`webSocket.send(message)` 也可能返回 `false`；但 Dart 上层 `sendText()`、`_sendPing()`、`_sendShadowIncrement()`、commit 发送周围的 `try/catch` 都只包住同步调用，捕不到这些异步失败。结果是 UI/controller 可能记录已发送、清空输入或继续保持连接状态，但 native 实际未发出消息。
- **PC 同步开关即时广播有跨 event loop 风险**：`ModernMenuWidget.toggle_sync()` 开新线程和新 asyncio loop 调 `broadcast_sync_state()`，而 `state.connected_clients` 里的 websockets 连接对象由 server 线程/loop 创建。对这些对象在另一个 loop 调 `client.send()` 在 websockets 12 下不是可靠模型，可能抛异常后被静默吞掉，导致手机端不会立即收到 `sync_state`。不过 PC 端处理文本时仍会返回 `sync_disabled`，心跳 pong 也会带 `sync_enabled`，所以这是即时状态同步风险，不是核心输入路径完全失效。
- **Android QR 替换设备确认的时序语义不严谨**：`_finishQrPairing()` 在连通性 probe 成功后先设置 `_qrPairingSucceeded=true` 并展示成功态，再等待 `_qrSuccessHoldDelay` 后调用 `_confirmScannedServer()`。若扫到不同 `device_id` 且用户取消替换，会出现“先成功、再取消”的体验。数据不会被保存，属于 UX/状态语义问题；更严谨的流程是先确认替换，再展示最终成功态。
- **菜单宽度/居中检查结论**：Linux 当前走原生 `QMenu`，实际宽度约 110px；`QMenu::item { text-align: center; }` 不改变实际文字绘制位置。真正居中需要 `QWidgetAction` 或自绘项，会牺牲当前 Linux 托盘宿主兼容性，用户已决定暂不改。
- **验证状态**：PC 72 个单元测试通过；Android 22 个 Flutter tests 通过；Flutter analyze 仅报告既有 4 个 `withOpacity` info。当前 review 没有发现协议字段不一致或 QR-only reconnect 模型被破坏。

## 2026-06-19 整体前端 Review 问题修复决策

- **Android WebSocket 发送语义**：`VoicingWebSocketSink.add()` 改为 `Future<void>` 是必要的接口变化。原因是 native MethodChannel 发送本来就是异步边界，保持 `void` 会让 controller 的 `try/catch` 形成虚假保护，导致 UI 认为发送成功但 native 实际失败。Dart IO sink 虽然底层 `WebSocketSink.add()` 仍是同步 API，也用 `async` 包成同一接口，保持上层发送路径一致。
- **发送后状态更新顺序**：`sendText()`、shadow increment、commit auto-enter 必须在 `await sink.add()` 成功后再记录历史、推进 `_lastSentLength` 或清空输入。发送失败时保留输入并断开/重连，比“清空但未到达 PC”更符合用户可恢复性。
- **PC 同步广播 event loop**：`websockets` 连接对象由 server loop 创建，托盘 UI 线程切换同步状态时应使用 `asyncio.run_coroutine_threadsafe()` 投递回 `state.server_loop`。新建 event loop 后直接 `client.send()` 属于跨 loop 操作，不能作为即时状态同步实现。
- **QR 替换确认时序**：扫码 probe 成功不等于用户已接受替换已保存设备。对不同 `device_id` 的替换，应先确认，再展示最终成功态和保存重连；取消时应直接退出扫码锁定态，不展示“成功后取消”的矛盾状态。
- **验证边界**：本轮只做源码与单元/静态验证，按用户要求未编译 APK 或 deb。

## 2026-06-19 Linux terminal 输入失效调查

- **根因判断**：当前 GNOME Wayland portal 后端固定发送 `Ctrl+V`（`KEYSYM_CTRL_L + KEYSYM_V`）。普通 GTK/浏览器输入框会把 `Ctrl+V` 解释为粘贴；GNOME Terminal 默认粘贴快捷键是 `Ctrl+Shift+V`，所以终端里不触发粘贴。这与用户现象“普通输入框生效，terminal 不生效”一致。
- **本机证据**：`/usr/share/glib-2.0/schemas/org.gnome.Terminal.gschema.xml` 中 `org.gnome.Terminal.Legacy.Keybindings paste` 默认值为 `<Control><Shift>v`；`gsettings list-recursively` 也显示 `org.gnome.Terminal.Legacy.Keybindings paste '<Control><Shift>v'`。
- **联网证据**：GNOME Terminal 官方帮助页 `help.gnome.org/gnome-terminal/adv-keyboard-shortcuts.html` 记录 Edit/Paste 默认是 `Shift + Ctrl + V`；XDG RemoteDesktop portal 官方文档说明 `NotifyKeyboardKeysym` 只是发送键盘事件，不提供“粘贴文本到焦点应用”的高级 API。
- **窗口识别限制**：尝试调用 GNOME Shell `org.gnome.Shell.Introspect.GetWindows` / `GetRunningApplications` 返回 `AccessDenied: GetWindows is not allowed`。联网结果也说明普通进程不能直接访问该私有窗口 introspection，除非 unsafe mode/扩展/patch。因此不能把“自动检测当前焦点是不是 terminal”作为默认产品方案。
- **AT-SPI 探测**：本机 `gi.repository.Atspi` 可用，能列出应用并看到 `ghostty`，但当前焦点状态可能落在 `gnome-shell` window，不能作为无需授权且稳定的 terminal 检测依据。它可以作为后续增强/heuristic，但不应作为唯一修复。
- **wl-clipboard 探测**：`wl-copy --primary` 与 `wl-paste --primary` 在本机可用。`Shift+Insert` 在 Linux/终端生态中常用于粘贴 PRIMARY 或 CLIPBOARD，行为跨应用不完全一致；如果同时写 CLIPBOARD 和 PRIMARY，可作为 terminal 兼容 fallback，但相比直接按 terminal 配置发送 `Ctrl+Shift+V` 更像广义兼容策略。
- **推荐修复路径**：第一版优先在 Linux Wayland portal 后端增加“terminal 粘贴快捷键”能力：默认仍保留普通 `Ctrl+V`，但提供可切换策略或 heuristic；若要立即解决用户当前 terminal，最小改动是把 Wayland portal 粘贴序列改为 `Ctrl+Shift+V` 或增加一个 terminal 模式。更稳的产品化方案是：写剪贴板时同时写 CLIPBOARD/PRIMARY，然后在 portal 后端支持三种 paste strategy：`ctrl-v`、`ctrl-shift-v`、`shift-insert`，由配置/菜单/环境变量选择，后续再加 AT-SPI heuristic 自动选择。

## 2026-06-19 GNOME Wayland Terminal 粘贴模式实现发现

- **实现选择**：默认使用 Auto 模式，不强行把所有 Wayland 粘贴改成 `Ctrl+Shift+V`。理由：普通输入框仍以 `Ctrl+V` 最稳；只有检测到 terminal 时才切到 `Ctrl+Shift+V`。
- **手动兜底**：Auto 检测不是 100% 稳定，因此托盘新增可见“粘贴模式”项：自动粘贴 / 普通粘贴 / 终端粘贴 / 兼容粘贴。用户可在 Auto 未识别 terminal 时手动切到终端模式。
- **AT-SPI 运行环境**：项目 venv 缺少 `gi`，但系统 `/usr/bin/python3` 有 `gi.repository.Atspi`。检测器先尝试当前进程，失败后以 `/usr/bin/python3 -c` 执行只读查询；若失败或超时，回退普通 `Ctrl+V`。
- **焦点兜底**：GNOME Wayland 上当前 `FOCUSED` accessible 有时落到 `gnome-shell` window。实现中若 focused 对象不是 terminal，会继续扫描 `ACTIVE` 且 app/role 命中 terminal 的窗口，提升 Ghostty/GNOME terminal 等实际窗口识别概率。
- **PRIMARY 处理**：为了支持 `Shift+Insert` 兼容模式，Wayland 下会同时写 CLIPBOARD 和 PRIMARY。写入前尝试读取旧 PRIMARY，粘贴后尽量恢复；若读取失败则不恢复，避免阻断主粘贴路径。
- **实测结果**：用户在当前 Linux/GNOME Wayland 环境手动启动测试后确认，普通输入框和 terminal 均可自动输入；AT-SPI Auto 检测 + terminal `Ctrl+Shift+V` 路径在该环境下有效。

## 2026-06-19 最新 PC / Android 逻辑复查发现

- **PC 输入失败恢复**：`type_text_at_cursor()` 原先在剪贴板写入新文本后，如果 `paste_from_clipboard()` 或 `press_enter()` 抛异常，会跳过旧剪贴板/PRIMARY 恢复。修复为 `finally` 恢复，避免失败后污染用户剪贴板。
- **PC ACK 清空语义**：`handle_client()` 原先不区分 `type_text()` 是否真正注入成功，submit 文本失败后仍可能返回 `clear_input=true`。修复为 `type_text()` 返回 bool，只有成功注入时才让 Android 清空输入，失败时保留手机端文本便于重发。
- **Android native close 语义**：`_NativeWifiWebSocketSink.close()` 原先等待 `_idFuture`；如果 native 连接还没返回 id 或已经失败，重连/释放路径可能留下未处理 Future 错误。修复为 best-effort close，id 不可用时静默完成。

## 2026-06-19 v2.9.5 Release workflow 失败根因

- `v2.9.5` tag 已触发 release workflow，旧 run `27815558477` 中 Android APK、Windows EXE、macOS DMG 均构建成功，但 Linux job 在 `Run desktop validation` 阶段失败，导致最终 `Publish GitHub Release` 被跳过。
- Linux 失败根因不是打包脚本或 DEB 逻辑，而是 `python -m unittest discover -s tests` 在 GitHub `ubuntu-22.04` headless runner 中创建 `QApplication` 时尝试加载 Qt `xcb` 平台插件，因无图形会话 abort：`Could not load the Qt platform plugin "xcb"`。
- 修复决策：Linux release job 显式设置 `QT_QPA_PLATFORM=offscreen`，并在 `pc/tests/test_voice_coding_tray.py` 导入 PyQt 前设置同样默认值。该改动仅影响 CI/headless 测试环境，不改变用户机器上发布应用的运行平台选择。
- 发布策略：GitHub 上尚未创建 `v2.9.5` release，因此可把失败构建用过的 `v2.9.5` tag 移到修复提交后重新触发同版本 release workflow，避免为 CI 环境变量修复单独升版本。
- 最终结果：新 run `27815951469` 全部成功，GitHub Release `v2.9.5` 已发布，包含 Android APK、Linux DEB、Linux standalone binary、Windows EXE、macOS DMG 和 SHA256 校验文件。

## 2026-06-19 v2.9.5 Linux deb 运行时误报 portal 不可用

- 用户安装 `v2.9.5` 的 `voicing-linux-amd64.deb` 后，在 GNOME Wayland 启动时弹出“没有可用的 RemoteDesktop portal 键盘能力”。同一系统中 `/usr/bin/gdbus ... AvailableDeviceTypes` 返回 `(<uint32 7>,)`，portal 服务也在运行，说明 portal 本身正常。
- 本机复现 `/opt/voicing/voicing --dev`：打包版误报 portal 不可用；源码版和系统 `gdbus` 检测正常。根因是 PyInstaller frozen app 会把自身解包目录注入 `LD_LIBRARY_PATH`，外部系统命令 `gdbus` 被迫加载打包应用自带/不匹配的动态库后失败，而错误被 `has_remote_desktop_keyboard_portal()` 捕获为 false。
- 修复决策：新增 `system_subprocess_env()`，调用系统命令时恢复 `LD_LIBRARY_PATH_ORIG`，无原始值时在 frozen app 中移除 `LD_LIBRARY_PATH`。该环境清理用于 `gdbus` portal 探测、`wl-copy` / `wl-paste` Wayland 剪贴板，以及系统 Python AT-SPI helper，避免打包态后续输入路径继续受同一问题影响。
- 本机已用 `sudo -n apt-get remove -y voicing` 卸载错误的 `voicing 2.9.5` deb；未清理用户数据 `~/.local/share/Voicing`。
- 本地 frozen smoke test 结果：临时 PyInstaller 二进制在 GNOME Wayland 上能进入 WebSocket 监听阶段，不再失败于 portal 能力检查；`QT_QPA_PLATFORM=offscreen` 下的系统托盘不可用错误是无界面测试环境预期结果。
- `v2.9.6` 发布确认：GitHub Actions run `27817118952` 首次只有 macOS `Create DMG` 因 `hdiutil: create failed - Resource busy` 失败，failed-job rerun 后全部通过。Release 已发布，`voicing-linux-amd64.deb` 资产存在，GitHub 给出的 asset digest 为 `sha256:1e08c2bad8a068f74b776dee4f84d0eb27efff6376fb4d4b06bf69a4ea37558a`。

## 2026-06-19 公开文档同步 Linux 自动粘贴与自启边界

- 公开文档需要明确：Linux/GNOME Wayland 下日常推荐使用"自动粘贴"，它会在普通输入框使用 Ctrl+V，在 terminal 焦点使用 Ctrl+Shift+V；手动终端/兼容模式只是兜底。
- Linux 开机自启不是 Windows 注册表路径，而是 GNOME autostart `.desktop`；公开中文 README 原先"注册表方式"的泛化描述会误导 Linux 用户，已改为按系统机制分别说明。
- GNOME Wayland 的 RemoteDesktop 键盘授权无法静默永久保存，因此自启只保证程序登录后启动；输入前仍可能需要用户允许 GNOME 的授权提示。

## 2026-06-19 GNOME Wayland Auto 粘贴稳定性修复

- 用户反馈 terminal 内仍偶发执行 `Ctrl+V`，而不是 `Ctrl+Shift+V`。复查后确认问题不在 RemoteDesktop portal 发送键位，而在 Auto 模式每次粘贴前只做一次 AT-SPI 焦点判断；AT-SPI 查询偶发返回 `None` 时，旧逻辑会把未知状态当普通输入框处理。
- 本机复现：连续调用当前 AT-SPI 查询时，`_get_focused_accessible_info()` 可间歇返回 `None`，同一 terminal 焦点下 `is_current_focus_terminal()` 因第二次查询失败返回 `False`。将 helper timeout 从 `0.35s` 提高到 `0.8s` 后稳定性改善，但空缓存第一次判断仍可能遇到未知状态。
- 修复决策按用户要求以“稳定识别 terminal”为最高优先级：Auto 模式现在最多重试 3 次焦点检测；明确识别 terminal 时记入短期缓存；明确识别普通 app 时清缓存并走 `Ctrl+V`；如果焦点无法可靠确认，则走终端安全的 `Ctrl+Shift+V`，避免 terminal 内再次误发 `Ctrl+V`。
- 取舍：未知焦点改为 terminal-safe 可能让少数普通应用收到 `Ctrl+Shift+V`；公开文档已说明可手动切到“普通粘贴”。这个取舍优先避免 terminal 输入失败。
- 同步扩展 terminal app 名称集合（如 Black Box、Foot、Rio、Tabby、generic terminal/console 等），并保持主进程和系统 Python AT-SPI helper 的识别表一致。
- 验证：`py_compile` 通过；`pc.tests.test_platform_keyboard` 39 项通过；`unittest discover -s pc/tests` 97 项通过；`git diff --check` 通过；本机 GNOME Wayland terminal 焦点压力测试连续 12 次均解析为 terminal。

## 2026-06-19 v2.9.7 Release 发布结果

- `v2.9.7` tag 指向 commit `30854a1 Improve Linux terminal paste detection`，已推送并触发 GitHub Actions release workflow。
- GitHub Actions run `27824263798` 成功完成，URL：`https://github.com/kevinlasnh/Voicing/actions/runs/27824263798`。
- GitHub Release 已发布：`https://github.com/kevinlasnh/Voicing/releases/tag/v2.9.7`。
- Release 资产已确认齐全：`voicing.apk`、`voicing-linux-amd64.deb`、`voicing-linux-x86_64`、`voicing-windows-x64.exe`、`voicing-macos-arm64.dmg`、`SHA256SUMS.txt`。

## 2026-06-19 Auto Enter 可靠性修复

- PC 端 commit 分支旧行为：收到 Android 空 commit 且 `auto_enter=true` 时直接调用 `press_enter()`，随后固定回 `clear_input=false`。如果 `press_enter()` 抛异常，WebSocket handler 会退出；如果成功，Android 也无法通过 ACK 判断 Enter 已经成功。
- Android 端 `_finalizeShadowInput(forceEnter: true)` 旧行为：只等待 WebSocket `sink.add()` 成功就立即 `_recordSentText()`、重置 shadow 状态并 `textController.clear()`，没有等待 PC ACK。因此 PC 没有按出 Enter 时，手机端仍可能清空输入，用户很难重试。
- 修复决策：PC 新增 `press_enter_after_settle()`，粘贴后等待 `0.35s` 再发送 Enter，并把成功/失败转换成 ACK：成功 `clear_input=true`，失败 `clear_input=false` 且记录错误。Android forceEnter commit 发出后不再本地清空，等待 PC ACK 走现有 `_handleMessage()` 清空。
- 取舍：Android forceEnter 成功后的输入框清空现在依赖 PC ACK；若连接异常或 PC Enter 失败，手机端保留文本，便于用户手动重发或排查。
- 验证：PC `py_compile` 通过；PC `unittest discover -s pc/tests` 99 项通过；Flutter analyze 退出码 0（仅既有 `withOpacity` info）；Flutter test 24 项通过；`git diff --check` 通过。

## 2026-06-19 Android 到 PC 发送核心链路最终审查

- 发送链路结论：Android `sendText()` 只在 connected 且 sync enabled 时发送；shadow increment 只推进 `_lastSentLength` 于 `sink.add()` 成功之后；native WiFi sink 等待 Kotlin `sendWebSocketMessage` 返回 true，发送失败会抛回 controller；PC WebSocket handler 只有注入成功才 ACK `clear_input=true`。
- Auto Enter 结论：submit 模式由 PC 在粘贴后按 Enter；shadow 模式由 Android 发送空 commit，PC Enter 成功后 ACK 清空，失败 ACK 保留输入。当前未发现“PC 未成功但手机误清空”的核心逻辑漏洞。
- 断线/重连结论：Dart controller 使用 connection generation 丢弃旧连接消息；native WebSocket failure/closed 会移除 controller 并触发 reconnect；旧连接的 onDone/onError 不会污染新连接。
- 协议结论：Android/Python/protocol contract 中 `text` message 的 `content`、`auto_enter`、`send_mode` 和 `ack.clear_input` 字段一致，无需改协议。
- 残余非阻断点：Android forceEnter commit 发送成功后会先记录 sent history，再等 PC ACK 清空；如果 PC ACK false 后用户重试，历史可能重复，但文本不会丢失，发送核心语义正确。

## 2026-06-19 GNOME Wayland Auto 粘贴普通窗口误判修复

- 用户反馈：自动粘贴模式下 terminal 可以粘贴，但普通窗口不能粘贴。根因是上一轮为稳定 terminal，将“AT-SPI 焦点完全无法确认且无近期 terminal 缓存”的情况也默认判为 `PasteMode.TERMINAL`，普通窗口在焦点检测短暂失败时会收到 `Ctrl+Shift+V`。
- 修复决策：Auto 模式只在明确 terminal 或近期 terminal 缓存仍有效时走 `Ctrl+Shift+V`；完全未知且没有近期 terminal 命中时回到普通 `Ctrl+V`，避免普通窗口被未知焦点误伤。
- AT-SPI fallback 需要返回 active 窗口本身，而不是只查找 active terminal。这样 GNOME Shell/desktop frame 等不可靠 focused accessible 出现时，如果真实 active 窗口是 Chrome/普通输入框，就能明确返回普通 app 信息并清空 terminal 缓存。
- 系统 Python AT-SPI helper 与主进程扫描逻辑必须保持一致：focused 不可靠时打印 active accessible 的信息，active 是 terminal 才由上层判为终端，否则普通 app 走 Ctrl+V。

## 2026-06-19 v2.9.8 Release 准备

- 发布内容包含两组未发布修复：Auto Enter ACK/清空语义修复，以及 GNOME Wayland Auto 粘贴普通窗口误判修复。
- 版本同步：PC `APP_VERSION` 升到 `2.9.8`；Android `pubspec.yaml` 升到 `2.9.8+9`；README 版本徽章和 tag 示例升到 `v2.9.8`。
- Flutter 3.27.0 在本地 analyze/test 前执行依赖解析时刷新了 `pubspec.lock` 中 8 个 SDK/test 相关传递依赖；该锁文件更新随发布提交保留，以匹配当前发布验证工具链。
- 发布结果：GitHub Actions run `27833313385` 成功；Release `v2.9.8` 已发布，包含 `voicing.apk`、`voicing-windows-x64.exe`、`voicing-macos-arm64.dmg`、`voicing-linux-amd64.deb`、`voicing-linux-x86_64` 和 `SHA256SUMS.txt`。

## 2026-06-20 本机 v2.9.8 deb 安装与 GNOME 自启确认

- 本机旧 `voicing 2.9.7` deb 包已通过 `sudo -n apt-get remove -y voicing` 卸载；未删除用户数据和日志。
- 用户从 GitHub 安装最新 deb 后，本机 `dpkg-query` 显示 `voicing 2.9.8 install ok installed`，GitHub latest release 也是 `v2.9.8`。
- 当前安装入口为 `/usr/bin/voicing -> /opt/voicing/voicing`，`/opt/voicing/voicing` 存在且可执行。
- GNOME 用户级自启文件存在：`~/.config/autostart/voicing.desktop`，内容包含 `Exec=/opt/voicing/voicing`、`TryExec=/opt/voicing/voicing`、`OnlyShowIn=GNOME;`、`X-GNOME-Autostart-enabled=true`。
- 当前桌面环境为 `XDG_CURRENT_DESKTOP=ubuntu:GNOME`、`DESKTOP_SESSION=ubuntu`、`XDG_SESSION_TYPE=wayland`，因此该自启文件会在 GNOME 登录后生效。GNOME Wayland RemoteDesktop 键盘授权仍可能需要用户在启动后允许。

## 2026-06-22 GNOME Wayland Auto 粘贴 AT-SPI 稳定性调研

- 本机原始 AT-SPI 采样显示：当前 Chrome 前台时，`FOCUSED` 连续 20 次返回 `gnome-shell/window`，真实窗口只能从 `ACTIVE` fallback 取得 Chrome。因此不能把 raw focused accessible 当作可靠焦点来源。
- 当前 `pc/platform_keyboard.py` 封装后的 `_get_focused_accessible_info()` 会在 focused 为 shell/desktop/空 app 时扫描 active 窗口；本机 Chrome 前台 20/20 次返回 Chrome 并判定 normal，Ghostty 前台 80/80 次返回 `ghostty/frame` 并判定 terminal。
- 现有 `_resolve_auto_paste_mode()` 是“一次明确结果立刻决策”：明确 terminal 立即返回 terminal；明确 normal 立即清 terminal cache 并返回 normal；只有 uncertain 才重试。这会让一次短暂旧窗口/错误窗口样本直接决定快捷键。
- 推荐改造方向：用 300-500ms 小时间窗口进行多次采样，按归一化类别投票，而不是按窗口标题投票。窗口标题会变化，例如 Ghostty title 中 spinner 字符每次不同。
- 推荐分类：`terminal`（role terminal 或 app_name 命中终端名单）、`normal`（app/role 明确且不是 shell/desktop/空值）、`uncertain`（None、gnome-shell、desktop frame/icon、空 app_name）。
- 推荐决策：terminal 达到最小置信票数且不低于 normal 时判 terminal；normal 达到最小置信票数且高于 terminal 时判 normal；票数打平或全 uncertain 时才使用 3 秒 terminal cache，否则默认 normal。这样避免 terminal cache 覆盖已经明确识别出的普通窗口。
- RemoteDesktop portal 官方能力只发送键盘事件，不提供“当前目标窗口/控件类型”接口；窗口类型判断仍必须来自 AT-SPI、桌面环境私有 API 或用户显式模式。GNOME Shell introspection 普通进程通常不可用，因此短期最现实方案是改进 AT-SPI 采样策略。
- 实现时发现 venv/packaged app 通常无法 in-process 导入 `gi`，会走 `/usr/bin/python3` helper。若每个样本都启动一次系统 Python，500ms 窗口通常只能拿到 1-2 个样本；因此最终实现必须让系统 Python helper 在单个子进程内部循环采样并输出 JSON list，才是真正的窗口内多样本投票。

## 2026-06-22 v2.9.9 Release 发布结果

- `v2.9.9` tag 指向 commit `d57313b Release v2.9.9 paste stability`，已推送并触发 GitHub Actions release workflow。
- GitHub Actions run `27927791710` 成功完成，URL：`https://github.com/kevinlasnh/Voicing/actions/runs/27927791710`。
- GitHub Release 已发布：`https://github.com/kevinlasnh/Voicing/releases/tag/v2.9.9`。
- Release 资产已确认齐全：`voicing.apk`、`voicing-linux-amd64.deb`、`voicing-linux-x86_64`、`voicing-windows-x64.exe`、`voicing-macos-arm64.dmg`、`SHA256SUMS.txt`。
- Android 业务代码本次未更新；Android 侧只同步了 README 文档和 `pubspec.yaml` 版本元数据到 `2.9.9+10`。

## 2026-06-22 本机 v2.9.9 deb 安装状态

- 本机旧 `voicing 2.9.8` deb 包已通过 `sudo -n apt-get remove -y voicing` 卸载；卸载时先停止了旧的 `/opt/voicing/voicing` 进程，并删除旧的 GNOME 用户级自启文件。
- 记录进度前复核显示本机已经安装新版：`dpkg-query` 为 `voicing 2.9.9 install ok installed`，`/usr/bin/voicing` 可用，`/opt/voicing` 存在。
- 当前有新版 `/opt/voicing/voicing` 进程在运行，GNOME 用户级自启文件已恢复并指向 `/opt/voicing/voicing`。
- 用户数据和日志未被删除。

## 2026-07-21 冷启动 terminal 粘贴误判 Heavy Research 综合发现

- 当前源码没有 normal 判定的持久缓存：每次发送都会重新采样；只有 terminal-majority 会建立约 3 秒 terminal cache。后续持续 Ctrl+V 更可能是每轮重复得到稀疏 normal/uncertain，或故障位于 portal modifier/terminal 消费层。
- AUTO 投票会忽略 uncertain：1 个 normal 加 7 个 uncertain 仍返回 NORMAL，全 uncertain 且无 terminal cache 也返回 NORMAL。最多 8 个样本、40ms 间隔在快速扫描时约 280ms 即结束，500ms 只是上限。
- 首次 portal backend 会先完成 CreateSession/SelectDevices/Start，再执行 AUTO 焦点采样；首次授权或 GNOME Shell 接管焦点可能形成首发专属竞争窗口。
- in-process AT-SPI 返回 8 个 `None` 时不会尝试 system Python；system helper 的 import、超时、stderr、return code 和 JSON 错误又会静默折叠为空样本。打包 DEB 未声明 `python3-gi`/AT-SPI GIR 依赖，自启动也没有 readiness gate。
- 手动物理 Ctrl+Shift+V 不经过 Voicing listener，不能直接修改粘贴模式、terminal cache 或 portal session；它更可能间接改变焦点、AT-SPI accessible 状态或只是消耗了就绪时间，但当前证据无法确定真正刺激。
- 外部平台资料确认 AT-SPI cold readiness 涉及 accessibility bus、registry、应用注册、cache 和焦点事件；RemoteDesktop portal 只逐键发送事件，不提供目标控件类型，也没有官方要求先人工粘贴一次。
- 首选解决路线不是简单延长 500ms，也不是 unknown 全部改成 terminal，更不能先发 Ctrl+V 再补发 Ctrl+Shift+V。应先增加 attempt 级诊断，再把 AUTO 保留为 terminal/normal/unresolved 三态，在 unresolved 时做有界 readiness 重采样，并比较 portal Start 前后焦点。
- 关键未裁决点：失败时最终 sequence 究竟是 Ctrl+V，还是 Ctrl+Shift+V 已选择但 Shift 未生效。deployment plan 必须先采集 raw samples、helper 状态、最终 mode、portal press/release 序列和冷启动对照，不能把单一根因当成已确认事实。
- 用户已接受上述关键缺口。最终 deployment plan 将修复拆成互斥证据分支：日志确认 Ctrl+V 才改 classifier，确认 Ctrl+Shift+V 但 Shift 未生效才改 portal chord，确认 selection owner 失败才改 clipboard。
- AUTO 目标策略确定为三态：可靠 terminal、可靠 normal、unresolved。unresolved 在总预算内重采样，超时不发任何粘贴快捷键，并沿现有失败 ACK 保留 Android 端文本。
- 发布门槛确定为至少 10 次干净 GNOME 登录零误判，同时保护普通窗口、剪贴板恢复、modifier 释放和非 Wayland 平台行为。

## 2026-07-28 全仓逐文件审查：初始状态

- 仓库根目录为 `/home/kevinlasnh/Projects/Voicing`，不在 Second Brain 保护目录内。
- 当前 Git 分支为 `main`，启动时工作区干净并与 `origin/main` 同步；唯一 worktree 即当前主 worktree。
- PWF 三件套存在且已被历史任务持续维护；session catchup 未报告遗漏上下文。
- 根目录当前没有 `AGENTS.md` / `CLAUDE.md`，但历史进度曾记录创建过被 `.gitignore` 忽略的本地副本，说明这些文件未进入版本历史、后来已不在工作区。
- 本次“每一个文件”的审查边界为仓库工作树内所有实际文件（含隐藏和忽略文件），排除 Git 自身的 `.git/` 对象数据库；二进制文件检查类型、尺寸、摘要和可提取元数据，文本文件检查实际内容。

### 清单与顶层工作流

- 当前工作树共有 86 个实际文件，总大小约 2.21 MB；所有文件在会话开始时均已被 Git 跟踪。
- `.claude/settings.local.json` 是 Claude Code 本机权限白名单；`.claude/skills/pc-hot-restart/` 是 Windows PowerShell 热重启 Skill，但其文档示例仍硬编码旧路径 `C:\Zero\Doc\Cloud\GitHub\Voice-Coding`，脚本本身则能从 `$PSScriptRoot` 正确反推仓库根目录。
- `.github/workflows/release.yml` 由 `v*` tag 触发，固定 Flutter 3.27.0、Java 17、Python 3.12，先做 Android/PC 测试，再并行构建 APK、Windows EXE、macOS DMG、Linux standalone/DEB，最后生成 SHA256SUMS 并发布 GitHub Release；第三方 Actions 均使用 commit SHA 固定版本。
- `.gitignore` 已忽略根目录 `AGENTS.md` / `CLAUDE.md`、`.brv/`、`.workflows/`、`.tmp/` 和常见构建产物；PWF 三件套未被忽略且当前已跟踪，符合当前全局策略。它尚未声明一般性的 `.claude/` / `.agents/` 隐藏目录规则，而 `.claude/` 当前已有被跟踪内容，需在仓库级 Agent Markdown 中明确其历史例外与同步边界。
- 中英文根 README 与 Android README 一致描述当前版本 `2.9.9`：Android 手机把语音/文本经 TCP 9527 WebSocket 发到 Python/PyQt5 桌面端，扫码保存同一 PC 的多 IP 候选并自动恢复；Linux GNOME Wayland 通过 RemoteDesktop portal 和终端感知粘贴模式输入。
- `CONTRIBUTING.md` 要求 Python 遵循 PEP 8、Dart 保持现有主题与 controller 分层；用户可见行为必须同步 CHANGELOG、根 README 和相关子目录文档；Android 原生层改动必须重新安装完整 APK 验证，不能只做 Flutter hot restart。

### CHANGELOG 当前架构演进（上半部分）

- 当前 `Unreleased` 为空；最新发布为 2.9.9（2026-06-22）。Agent 规则应把版本更新视为 PC `APP_VERSION`、Android `pubspec.yaml`、README 徽章/示例和 CHANGELOG 发布块的联动操作。
- 2.5.0 起双端协议常量从 UI/主程序中抽离，并新增 `protocol/voicing_protocol_contract.json` 及双端契约测试；协议修改必须三处同步。
- 2.6.x 引入 `send_mode=submit/shadow/commit`、`auto_enter` 与 `ack.clear_input`，核心不变量是：桌面注入/Enter 真正成功后才允许手机端清空文本。
- 2.7.x 建立 Windows/macOS/Linux 平台抽象、四平台 Release、SHA256 校验和第三方 Action SHA 固定；Android 原生 release signing 不允许静默退回 debug。
- 2.9.x 从 UDP discovery 迁移到 QR-only 保存设备与多 IP 候选恢复；PC 端运行时重绑监听地址，二维码优先发布实际绑定成功 IP；同一 `device_id` 重扫合并候选池，不同设备替换不得混合旧地址。
- 2.9.5—2.9.9 的 Linux 主路径为 GNOME Wayland RemoteDesktop portal + Wayland clipboard + AT-SPI 终端识别；历史版本说明存在策略迭代，仓库级规则应以当前源码、2.9.9 文档和测试为准，不复制已被后续版本推翻的旧行为。

### Android 工程配置与依赖

- Flutter 工程版本为 `2.9.9+10`，Dart SDK 约束 `^3.5.4`；直接依赖为 `web_socket_channel 2.4.5`、`shared_preferences`、`mobile_scanner` 和 `cupertino_icons`，锁文件固定了完整传递依赖与摘要。
- Android applicationId/namespace 为 `com.voicecoding.app`，min/target/compile SDK 跟随 Flutter，NDK 固定 `27.0.12077973`，AGP 8.7.0、Kotlin 1.9.22、Gradle wrapper 8.12、JVM target 1.8。
- Release 构建有显式签名门禁：若缺少 `key.properties`，只有传入 `-Pvoicing.allowDebugReleaseSigning=true` 才允许本地 release 测试；CI 则注入正式 keystore。
- Manifest 允许局域网明文 WebSocket，声明网络/WiFi/相机权限；主 Activity 使用 `singleTop`、`adjustNothing`，键盘高度由 native bridge 自行上报。相机是可选硬件，扫码插件注册文件由 Flutter 生成。
- Android Maven 仓库顺序为 `google()` / `mavenCentral()` / Flutter 官方存储优先，阿里云镜像仅 fallback；本地 Java 路径应写 `android/local.properties`，不得提交。
- Flutter/Android 子目录 `.gitignore` 包含生成产物、IDE、签名材料和 local.properties；Gradle wrapper 与 GeneratedPluginRegistrant 虽匹配子目录忽略规则，但已作为历史生成文件被 Git 跟踪，修改时应优先由 Flutter/Gradle 工具再生成，而非手工维护。
- 启动图、主题和 adaptive icon XML 均是标准 Flutter/Android 资源；亮色 splash 为白色、暗色 splash 随系统暗色背景，launcher adaptive background 为 `#1A1A2E`。

### Android 业务代码（基础模块与 UI 前半）

- `main.dart` 主要负责 Material 3 UI、菜单/动画、扫码视图、键盘 inset 布局与用户确认；网络/发送/持久化状态集中在 `VoicingConnectionController`，修改时应保持这一分层，避免把连接逻辑重新塞回 Widget。
- `AppTheme` 集中维护 4px 间距体系、颜色和文字样式；现有 UI 使用深色主题。界面改动应复用 token，避免新增散落 magic numbers/颜色。
- `SavedServer` schema v1 保存 device_id、主 IP、候选 IP、端口、名称、系统和最近连接时间；同设备重扫合并候选池并保持主 IP 优先，legacy 无 device_id 数据允许升级合并，持久化落在 SharedPreferences 的单一 JSON key。
- `VoicingProtocol` 保留 UDP discovery 常量/解析器用于兼容与契约，但当前公开流程是 QR-only；WebSocket 客户端消息为 text/ping，服务端消息为 connected/ack/pong/sync_state/sync_disabled，text 含 auto_enter 与 submit/shadow/commit。
- `VoicingWebSocketConnector` 在 Android 优先走 MethodChannel/EventChannel 的 native WiFi-bound WebSocket，非 Android 或关闭偏好时才走 Dart `IOWebSocketChannel`；native sink 的发送必须等待 Kotlin 返回 true，close 是 best-effort，连接 generation/pending event 由 id 映射隔离。
- UI 初始化时注册 lifecycle observer、controller listener、native IME inset EventChannel 和 QR scanner；菜单预绘用于规避首次绘制卡顿，扫码前先收键盘并等待 280ms，扫码器进入后还设 1 秒稳定窗口再锁定 QR。
- 手机端输入框 `TextInputAction.send` 直接调用 controller `sendText()`；“自动 Enter”只是 controller 状态开关，发送语义不能在 UI 层另行实现。

### Android 扫码与连接状态机（已读部分）

- QR UI 先校验 `type=voicing`、`v=1`，对非 Voicing、版本不兼容和损坏 payload 分别提示；相机权限/设备错误可退回手动 IP。二维码角点会从 capture 坐标映射到预览 cover 坐标，并以 CustomPainter 做待机、锁定、成功/失败动画。
- Controller 对每次扫码使用 `_qrPairingGeneration` 取消旧异步流程；按 QR 候选 IP 顺序逐个做 3 秒 WebSocket probe，收到 connected 后发送 `ping(source=qr_scan)`，只有收到 pong 才视为连通。
- 扫码成功后先确认是否替换不同 `device_id` 的现有设备；用户确认后才保存与重连。保存同设备时合并旧候选 IP，且新连接成功 IP 保持主地址优先。这个“probe → 用户确认 → save → force reconnect”顺序是防止错误替换和候选池污染的关键不变量。
- QR probe 与正式连接都优先 Android native WiFi-bound channel；subscription、timeout 和 probe channel 在 finally 中清理，generation 变化或退出扫码模式会终止旧结果回写。

### Android 正式连接、恢复与发送语义

- App 初始化只加载 Auto Enter 与 `saved_server`；没有保存设备时明确保持 disconnected，不启动 UDP 自动发现。保存设备后按 `candidateIps` 逐一以 2 秒超时连接，全部失败才进入 3/6/12…最多 30 秒退避。
- 每次连接递增 `_connectionGeneration`，旧 socket 的 message/error/done 回调必须先比对 generation；前台恢复使用 12 秒快速窗口、500ms 重试和 2 秒连接超时，并可暂时保持“已连接”显示，成功 connected 后结束恢复窗口。
- 心跳每 15 秒发 ping，30 秒无 pong/sync state 即判死；connected 消息会校验/补全保存设备身份、提升当前成功 IP 为主 IP并持久化，若服务端 device_id 与已保存身份冲突则拒绝更新元数据。
- 手动 submit 只在 connected 且 sync enabled 时发送；若当前文本已通过 shadow 增量完整发送，则手动提交会进入 finalize，避免重复发送内容。
- 语音 composing 结束时只发送相对 `_lastSentLength` 的 shadow 增量，发送成功后才推进长度；700ms 静默后 finalize。Auto Enter 关闭时本地记录并清空，开启时发送空 content 的 commit 并等待桌面 ACK 决定是否清空。
- 服务端 ACK 的 `clear_input=false` 会保留手机文本；字段缺失则为兼容旧服务端默认清空。发送或 ping 异常会进入统一断连/重连路径。最近发送历史最多 20 条，撤回按历史向前遍历。
- Controller `dispose()` 会取消所有 timers/listener、递增 generation 并关闭 channel；后续修改连接路径必须继续保持 timer、subscription、generation 和 native channel 的成对清理。

### Android native bridge 与测试边界

- `MainActivity.kt` 提供两个 EventChannel（network events、keyboard insets）和一个 MethodChannel（connect/send/close）。IME inset 通过 `WindowInsetsAnimationCompat` 逐帧换算为 dp，Flutter 主界面配合 `adjustNothing` 自行移动输入区。
- Native WebSocket 从 `ConnectivityManager.allNetworks` 中选择 `TRANSPORT_WIFI + NOT_VPN` 网络；若目标是 IPv4，会优先选择其 link subnet 能覆盖目标地址的 WiFi，否则取首个物理 WiFi fallback。OkHttp 同时绑定该 Network 的 socketFactory 和 DNS。
- Kotlin 侧用并发 map 持有 connection，事件切回 main thread；Flutter EventSink 尚未监听时先排队，close/failure 后移除连接、cancel socket、关闭 dispatcher 并清空 connection pool。修改 native 桥接必须完整安装 APK 验证，hot restart 不足以覆盖 Kotlin/Manifest/Gradle。
- Android 现有测试覆盖恢复策略、saved_server 序列化/迁移/同设备候选合并、共享协议契约、native WebSocket close 行为；没有直接覆盖 1164 行 controller 的扫码 probe、generation、shadow/commit/ACK 和候选轮询，也没有 Kotlin instrumentation/unit test，因此这些路径变更需要增加 Dart controller 测试并做真机端到端验证。
- `connection_recovery_policy_test.dart` 仍保留 UDP 命名与旧策略测试，说明兼容代码尚未清理；不要仅因当前 UI 为 QR-only 就删除 UDP contract/解析器或测试，除非明确做协议兼容性迁移。

### PC 平台基础层与输入入口

- PC 运行依赖固定到兼容小版本：Pillow 12.2、websockets 12、PyAutoGUI 0.9.54、pyperclip 1.11、PyInstaller 6.19、PyQt5 5.15.11、qrcode 8、psutil 7.2。macOS spec 构建无 Dock 图标的 `LSUIElement` app bundle，bundle id 为 `com.kevinlasnh.voicing`。
- `device_identity.py` 在平台数据目录的 `device.json` 维护 UUID hex device_id，采用 `.tmp` + replace 原子写入；设备名优先配置值再回退 hostname，`darwin` 对外协议名映射为 `macos`。
- `platform_autostart.py` 分别使用 Windows Run registry、macOS LaunchAgent、Linux GNOME autostart `.desktop`；源码模式启动命令是当前 Python + `voice_coding.py`，frozen 模式是可执行文件本身。
- 单实例：Windows 用 named mutex，macOS/Linux 用数据目录 `voicing.lock` + `fcntl.flock`；重复启动时显示原生/Qt 提示。
- `platform_utils.py` 统一平台数据/日志目录、默认热点地址、Wayland 判断和 RemoteDesktop portal 能力探测；frozen app 调用 `gdbus` 等系统工具时必须使用 `system_subprocess_env()` 清除 PyInstaller 污染的 `LD_LIBRARY_PATH`。
- PC 协议 builder 与 Android 常量一致，并额外负责 QR payload、connected/ack/sync 消息构造。`network_recovery.py` 仍保留 UDP 广播 payload 和接口变化辅助，属于兼容/测试代码。
- `platform_keyboard.py` 是所有文本注入的唯一平台层：Windows/macOS/X11 使用 pyautogui/原生 Enter，GNOME Wayland 使用 RemoteDesktop portal；`type_text_at_cursor()` 负责保存剪贴板与 PRIMARY、写入、粘贴、可选 Enter，并在 `finally` 中恢复。
- Wayland clipboard 优先 `wl-copy`/`wl-paste`，外部命令同样必须使用清理后的系统环境；粘贴模式为 Auto/Normal/Terminal/Compat，当前 AT-SPI 采样参数为 500ms 窗口、40ms 间隔、最多 8 样本，terminal fallback cache 为 3 秒。

### PC GNOME Wayland portal 与焦点判定

- `RemoteDesktopPortalKeyboardBackend` 以线程锁保护单例 session，依次执行 CreateSession → SelectDevices(KEYBOARD uint32) → Start；每个 portal request 通过唯一 handle_token 监听异步 Response，默认 60 秒超时。任何拒绝、超时或键盘事件错误都会抛错，键盘事件错误还会清空 session 以便下次重建。
- PyQt5 会把普通 Python int 序列化为 D-Bus `i`，portal 的 `types/state` 必须通过 `_dbus_uint()`/variant 强制为 `u`；这类 typed argument 不可简化回普通 int。
- Wayland 发送序列严格成对释放 modifier：Normal=`Ctrl down,V down,V up,Ctrl up`，Terminal 再包 Shift，Compat=`Shift+Insert`，Enter 单独 down/up。任何修改都必须验证 press/release 顺序和异常后的 modifier 释放风险。
- Auto 模式先取最多 8 个 AT-SPI 样本，terminal/normal 计票、uncertain 不计票；terminal 多则缓存并走 Ctrl+Shift+V，normal 多则清缓存并走 Ctrl+V，平票只在 3 秒内近期 terminal 命中时走 terminal，否则 normal。
- AT-SPI 优先当前 Python 进程的 `gi.repository.Atspi`，不可用时启动系统 Python；system helper 会在单个进程内批量采样，避免每个样本重复启动解释器。focused 为 shell/desktop/空 app 时会扫描 ACTIVE accessible fallback。
- 终端名单、焦点扫描逻辑和采样常量在主进程代码与内嵌 system-Python helper 中有重复实现；增删终端、修改 fallback 或采样策略时必须同步两份并扩展 `test_platform_keyboard.py`。
- Windows Enter 优先 Win32 `SendInput`，失败才回退 pyautogui；不要把普通平台输入路径与 Wayland portal session 混在一起。

### PC 主程序：网络发现与 WebSocket 输入入口

- `voice_coding.py` 当前 `APP_VERSION=2.9.9`，全局 `AppState` 用 `threading.Lock` 保护 connected clients、实际绑定 IP 与 server loop，并以 Qt signal 把 WebSocket 线程的 QR probe 成功事件送回 UI。
- 网络枚举优先 psutil，fallback 为 Windows PowerShell JSON、Linux `ip -j -4 addr`、macOS `ifconfig`；只接受 private、非 loopback/link-local/multicast、prefix 1—30 且非 VPN/虚拟网卡的 IPv4。
- 排序规则优先 Windows hotspot `192.168.137.*`，再按 Ethernet/WiFi/unknown 与平台 hotspot 前缀；macOS 不假设 `en0/en1` 的固定角色。接口快照每次刷新记录候选，QR 在 server 已启动后优先发布实际绑定成功 IP。
- `type_text()` 是 WebSocket handler 的 bool 语义适配层：sync 关闭或空文本直接 false，真正注入成功才 true；`press_enter_after_settle()` 独立用于空 commit。
- WebSocket 收到 text 时先检查 sync；submit 的 auto_enter 随粘贴执行，shadow 文本只注入不清手机输入，commit 只按 Enter。ACK `clear_input` 仅在 submit 注入成功或 commit Enter 成功时为 true，阻塞桌面注入始终通过 `asyncio.to_thread()` 脱离 event loop。

### PC server 生命周期与托盘/QR 前端（已读部分）

- QR scan probe 的 ping 会通过 Qt signal 触发桌面 QR 成功态；普通 ping 返回带当前 sync state 的 pong。非 JSON 消息仍作为 legacy plain text 输入处理，但不会回 ACK。
- sync 开关广播必须通过 `asyncio.run_coroutine_threadsafe()` 调度到 `state.server_loop`，不能从 Qt 线程直接 await/操作 WebSocket event loop。
- server 为每个物理候选 IP 分别创建 listener；全部绑定失败时清空 bound IP、每 2 秒重试；监听期间每 1 秒刷新接口集合，变化即关闭全部旧 listener 并按新地址重建。QR 只在 listener 存在时使用 bound hosts。
- Windows/macOS 自定义 Fluent menu 包含 QR、sync、paste mode、autostart、日志、退出；sync 切换同时更新图标、关闭菜单并广播状态，paste mode 按 Auto→Normal→Terminal→Compat 循环。
- 自定义 Popup 菜单宽度强制收紧到 sizeHint，并补偿阴影 margins 与平台展开方向；Windows 连续右键托盘图标有专门的关闭后重开处理。UI 布局与这些坐标补偿耦合，调整 margins/高度时要同步验证定位。
- QR dialog 固定 282×308、QR 230，直接居中出现而不做跨窗口飞入；payload 每 5 秒刷新，包含 device identity、实际监听 IP 池和端口。二维码 pixmap 按 payload 缓存，成功 overlay 与 close/focus generation 防止旧动画回写。

### PC 主程序收尾与共享协议

- QR 成功态播放一次后约 1150ms 直接关闭；成功/关闭期间忽略 focus-out，普通状态点击窗口外才关闭。Linux 预热 QR 时只 polish/layout，不 `show()`，避免 Wayland 左上角黑闪。
- Linux 托盘强制使用系统原生 `QMenu`：右键完全交给 `setContextMenu` 宿主，左键/双击手动 popup；Windows/macOS 才用自定义 Popup。两套菜单共用 `ModernMenuWidget` 的业务 action，并在显示前同步 sync/paste/autostart 状态。
- 托盘图标预生成 normal/dim/paused 三态并缓存，`_current_icon_key` 去重 `setIcon`；200ms timer 只切等待连接的亮暗状态，Linux SNI/AppIndicator 下不可恢复无条件 setIcon。
- 主入口顺序为 logging → runtime/portal 能力检查 → 初始网络接口刷新 → daemon WebSocket thread → Qt tray loop；生产模式先做单实例检查，`--dev` 明确跳过，适合本地热重启。
- 共享 protocol contract 固定 TCP 9527、历史 UDP 9530、QR v1/type voicing、text/ping 与 connected/ack/pong/sync_state/sync_disabled 的字段集合。任何字段增删都必须同步 JSON contract、Python builder/constants、Dart constants/parser 及两端契约测试。

### PC 测试覆盖（第一组）

- 单元测试通过临时目录验证 device_id 创建/复用/名称与 macOS 映射，自启 `.desktop` 写入/删除与路径空格转义，UDP legacy payload/interface change，以及平台命令 IP 解析。
- `test_voice_coding_server.py` 明确锁定核心 ACK 不变量：注入失败不清手机文本；commit Enter 成功才 clear，失败保留。修改 handler 或 ACK builder 时这些测试必须继续通过。
- 网络接口测试覆盖 Windows/Linux/macOS 解析、VPN/Tailscale/link-local//31//32 过滤、hotspot 排序、psutil 路径、运行时替换旧接口、QR bound hosts 优先但不隐藏 fresh candidate pool。
- 平台工具测试覆盖三平台数据目录、Wayland portal allow/block、AvailableDeviceTypes keyboard bit、gdbus uint 解析和 PyInstaller `LD_LIBRARY_PATH` 修复；修改打包态系统子进程环境时必须运行这一组。

### PC 键盘/Wayland 测试覆盖

- `test_platform_keyboard.py` 直接锁定 macOS/普通平台快捷键、Wayland portal dispatch、剪贴板与 PRIMARY 在成功/失败时恢复、Auto Enter 延迟、portal session 三步流程与 D-Bus uint 类型。
- 键序列测试覆盖 Normal/Terminal/Compat/Enter 的精确 press/release 元组，portal event 错误必须清 session；Wayland `wl-copy`/`wl-paste` 和 system Python AT-SPI 都必须使用 `system_subprocess_env()`。
- Auto 投票测试覆盖 terminal/normal 多数、平票近期 terminal cache、全 unresolved 默认 normal、normal 明确信号清 cache、500ms/8 样本窗口、shell focused → active terminal/normal fallback。
- 测试同时覆盖 clipboard backend fallback 与 Windows SendInput→pyautogui fallback。修改 `platform_keyboard.py` 时应至少单跑该文件，再跑全 PC suite；涉及 GNOME Wayland 仍需实机 portal/terminal/普通窗口验证。

### PC 其余测试与二进制资源

- PC protocol contract 测试检查端口、消息类型/字段、ACK clear_input、QR required/optional 字段与版本；tray 测试在 `QT_QPA_PLATFORM=offscreen` 下覆盖 Linux 右键不双弹、左键/双击 popup、自定义菜单无分隔/宽度、paste mode 循环、QR 直接居中和 sync 广播使用 server loop。
- 仓库共有 14 个二进制文件：10 个 Android launcher PNG、Android/PC 各 1 个 1024×1024 RGBA 源图、1 个 6-size Windows ICO、1 个 Gradle wrapper JAR；均可被 `file` 正常识别并已记录 SHA-256。
- Android foreground PNG 尺寸按 mdpi→xxxhdpi 为 108/162/216/324/432，legacy mipmap launcher 为 48/72/96/144/192；源图和 PC 图标源均为 1024×1024 RGBA，但摘要不同，不能假定可互换。
- `gradle-wrapper.properties` 指向 Gradle 8.12，但现有 `gradle-wrapper.jar` manifest 标记 Implementation-Version 2.10（2015，49 个 class/resource entry）。本次不擅自替换生成物；若未来升级 wrapper，应使用 Gradle wrapper 任务同时重生成 jar/scripts/properties并验证构建，而非只改 distributionUrl。

### PWF 历史复核（中段）

- 补读的历史进度与当前源码一致：Wayland portal、typed D-Bus uint、Linux 原生 QMenu、图标 setIcon 去重、QR 直接居中、native WebSocket await、server-loop sync 广播、terminal paste modes、ACK/clipboard 修复均有对应测试与实机验证记录。
- 历史记录也明确多次区分“源码/单测已通过”和“仍需 Windows/macOS/Linux/Android 实机肉眼或完整 APK 验证”；仓库级规则应保留这种按改动范围分层验证的表达，不能把 headless/unit 结果冒充平台实机验收。

### 编码、权限与凭据卫生

- 最终分类为 72 个文本文件 + 14 个二进制文件（共 86 个）；此前口头更新中的 71/15 为预估，现已按 MIME 逐文件复核纠正。
- 72 个文本文件全部可按 UTF-8 解码，未发现 CRLF；仅 `android/voice_coding/android/app/src/main/res/values/colors.xml` 缺少文件末尾换行。本次不改无关资源格式。
- 工作树没有软链接，也没有 Git mode 100755 文件；因此 `android/voice_coding/android/gradlew` 当前被跟踪为不可执行，Unix 下直接 `./gradlew` 会受权限影响，日常优先通过 Flutter 命令或显式 `bash android/gradlew`，若修复 mode 应单独验证并提交。
- 未发现 private-key header、keystore/key.properties/PEM/key 文件或 credential/secret 命名文件；GitHub workflow 仅引用仓库 Secrets，不含明文签名凭据。
- 根 `AGENTS.md` / `CLAUDE.md` 已由 `.gitignore` 明确忽略；PWF 三件套明确未忽略。`.claude/` 当前属于已跟踪历史例外，仓库级 Agent Markdown 必须显式说明，避免未来误把本机权限或凭据写入其中。

### 仓库级 Agent Markdown 最终结构

- 新建的根 `AGENTS.md` 与 `CLAUDE.md` 已全文同步，H1 同为 `# Repository Agent Markdown`；两份文件属于本地配置，不进入 Git 提交。
- 配置把本次审查中最值得跨 session 保留的约束集中为八类：仓库定位与目录职责、核心数据流/ACK 不变量、Android 分层、PC/Wayland/托盘平台边界、编辑规则、验证矩阵、Release 同步规则、PWF/Git/凭据卫生。
- 协议同步清单明确覆盖 JSON contract、Python、Dart 与双端契约测试；Android native 改动明确要求完整重装 APK；Wayland 明确保留 D-Bus uint、成对 modifier、双份 AT-SPI helper 同步和诊断优先原则。
- Git 规则明确保留根 Agent Markdown 的本地 ignore，同时把现有 `.claude/settings.local.json`、`.claude/skills/pc-hot-restart/` 以及未来成对维护的 `.claude/skills/` / `.agents/skills/` 声明为受控隐藏目录例外。
- 根 `.gitignore` 当前已满足本任务要求，无需产生额外 diff；最终应提交和推送的只有本次增量更新后的 `task_plan.md`、`progress.md`、`findings.md`。
- 由于本次不涉及可执行源码，完整 PC/Flutter suite 不提供额外风险覆盖；配置一致性、编码/换行、ignore 命中和 `git diff --check` 是本轮适当验证。

## 2026-07-28 Ubuntu 22.04 terminal 自动粘贴修复：恢复基线

- 当前 `main` 为 `f53b198`，业务代码仍是 v2.9.9；用户要求本轮最终发布新的 deb 和 apk，因此计划采用下一补丁版本 `v2.9.10`，发布前仍需依据实际改动同步全部版本与文档位置。
- 阶段 31 的 `.workflows/2026-07-21-175636/` 本地调研目录当前已不存在，但调研综合结论、互斥根因分支和至少 10 次干净 GNOME 登录门槛已持久化在 PWF 与提交 `6fd3902` 中，可作为本轮实现依据。
- 启动工作区没有用户未提交的源码改动，可以直接从当前 `main` 建立复现与诊断基线。
- 本轮完成证据不能只依靠现有单测：必须验证日志能够证明最终选择的粘贴模式和 portal press/release 序列，并在实际 GNOME Wayland terminal 与普通窗口中重复验证文本结果。

### 当前系统与日志证据

- 当前机器正是问题目标环境：Ubuntu 22.04、GNOME Shell 42.9、Wayland (`wayland-0`)、Python 3.10.12；本机安装的是 `voicing 2.9.9`。
- `python3-gi`、`gir1.2-atspi-2.0`、`at-spi2-core` 已安装，系统 Python 可成功导入 `Atspi 2.0`；因此 system-Python helper 理论上可用。
- 本机没有 `wl-copy` / `wl-paste`、`xclip` 或 `xsel`。当前源码会回退到 Pyperclip；这不是本轮“Ctrl+V 被 terminal 内 TUI 当成图片粘贴”的直接分类根因，但需要继续验证文本写入剪贴板确实成功，避免把旧图片内容与快捷键误判混淆。
- v2.9.9 当日日志只记录启动、网络和 WebSocket 生命周期，没有任何 AT-SPI raw sample、helper 来源/错误、AUTO 投票结果、最终键序列或 portal 事件信息；现场失败后无法从日志判断是 classifier 选择 Ctrl+V，还是 Ctrl+Shift+V 的 Shift 事件未生效。
- 现有日志缺口直接印证阶段 31 的诊断优先结论：修复必须让每次 paste attempt 可追踪，但日志不得记录用户实际文本或剪贴板内容。

### 当前源码的确定性缺陷

- `RemoteDesktopPortalKeyboardBackend.paste_from_clipboard()` 先 `_ensure_started()` 再调用 `_resolve_wayland_paste_sequence()`；首次授权后只采“portal Start 之后”的焦点，没有保留授权前用户真实目标窗口证据。如果 portal/桌面壳层在建会话期间改变焦点，首发分类会被污染。
- `_resolve_auto_paste_mode()` 只返回 terminal/normal 两态：1 个 normal + 7 个 uncertain 会直接判 normal；全 uncertain 且无 3 秒 terminal cache 也会清 cache 并判 normal。该行为会把“没有可靠证据”错误降级为 Ctrl+V，正好能触发 terminal 内 TUI 的图片粘贴处理。
- `_sample_focus_infos()` 只要 in-process 采样列表非空就直接采用，即使内容全部为 `None`；这种情况下不会尝试可用的 system-Python helper。helper 的异常、超时、非零退出码、stderr 和 JSON 失败也全部静默折叠为空列表。
- `_find_focused_accessible()` 在整棵 AT-SPI desktop tree 中返回 DFS 遇到的第一个 `FOCUSED` 节点；如果多个应用残留 FOCUSED 状态，它没有先约束到 `ACTIVE` 顶层窗口。只有 focused 结果为 shell/desktop/空值时才扫描 ACTIVE，因此“旧普通窗口 focused + 当前 terminal active”会被明确误判为 normal，而不是 uncertain。
- portal `_send_key_sequence()` 虽然正常序列成对释放 modifier，但中途任一 D-Bus event 失败就立即抛出，未 best-effort 释放已经按下的 Ctrl/Shift；这不是当前 Ctrl+V 分类主因，却会造成后续输入状态风险，修复时应补偿释放并记录每个 event。
- 当前 `type_text_at_cursor()` 在复制后没有回读验证 clipboard 是否确实变成待发送文本；在本机缺少 wl-clipboard/xclip/xsel 的环境下，应增加不记录正文的长度/摘要级验证或至少明确 backend/失败诊断。

### 现有测试与发布包缺口

- 现有测试把错误策略固化为预期：`test_auto_paste_mode_treats_unresolved_focus_as_normal_without_terminal_cache` 明确要求全 unresolved 返回 NORMAL，必须改为安全的 unresolved/失败行为并补 readiness 重采样测试。
- `test_scan_atspi_desktop_does_not_override_normal_focused_app` 明确禁止在“找到普通 focused 节点”后检查 ACTIVE；这会保护 stale-focused 误判。新实现应按 ACTIVE 顶层窗口约束 focused 子树或至少对 focused/active 冲突判 unresolved，而不是继续信任任意 DFS 首项。
- portal 测试只验证完整成功序列和“错误后 session 清空”，没有验证部分按键成功后的 modifier 补偿释放、attempt 日志或首次 session 前后焦点证据选择。
- clipboard 测试只验证调用顺序，没有验证 copy 后回读、backend 诊断或复制失败时绝不发送快捷键。
- Linux deb 的 `Depends` 当前仅有 Qt/XCB 运行库，没有 `wl-clipboard`、`python3-gi`、`gir1.2-atspi-2.0` 或 `at-spi2-core`；这使干净 Ubuntu 22.04 安装不能由包管理器保证稳定分类与 Wayland clipboard 依赖。发布 workflow 也未在构建 runner 安装/验证这些运行依赖。

### 实机 AT-SPI 已复现 stale-focused 根因

- 在当前 Ubuntu 22.04 Wayland 会话直接运行 v2.9.9 的 `_sample_focus_infos_in_process()`，同一轮先后返回钉钉文档、`Unnamed/frame/Voicing` 等不同应用；`_resolve_auto_paste_mode()` 最终为 NORMAL。
- 枚举整棵 AT-SPI desktop tree 时，同时观察到：钉钉应用存在 `FOCUSED document web`，而另一个 `Unnamed` 应用存在 `ACTIVE frame`；GNOME Shell 自身也有 ACTIVE window。也就是说，桌面上确实同时存在跨应用的 stale FOCUSED 与真实 ACTIVE 状态。
- 当前 `_scan_atspi_desktop()` 会先拿整棵树 DFS 的钉钉 FOCUSED，并因它是“明确普通窗口”而完全不检查另一个应用的 ACTIVE frame。这不是理论风险，而是本机实时证据，足以解释用户点击 terminal 后仍被旧普通应用样本投票成 Ctrl+V。
- 修复方向因此可以裁决为 classifier 主分支：优先选择非 shell 的 ACTIVE 顶层窗口，并只在该 ACTIVE 子树内寻找 focused 控件；跨应用 focused/active 冲突不得把 stale focused 当作明确 normal。Portal modifier 与 clipboard 仍需同时加诊断和防护，但不是当前已复现的首要根因。

### 第一轮修复后的实机采样

- ACTIVE-window-first 实现后，在同一桌面状态连续采样 5 次均返回 `Google Chrome/frame` 且 `source=active_window`；旧算法同一环境曾在钉钉 FOCUSED、Unnamed ACTIVE 和 GNOME Shell 之间跳动。
- 新投票摘要在该普通窗口为 normal=5、terminal=0、uncertain=0，说明修复不是简单把 unknown 改成 terminal，而是从真实 ACTIVE 证据稳定得到普通窗口结论。
- 当前直接以 `/usr/bin/python3` 运行源码时不会再启动“alternate system Python”，因为当前解释器本身已经可导入 AT-SPI；打包后的 `/opt/voicing/voicing` 则会使用 `/usr/bin/python3` helper。该差异是预期行为，后续需通过 PyInstaller/DEB 产物验证 helper 分支。

### 新测试契约

- 自动模式只有达到至少 2 个可靠同类票，或在存在冲突时领先至少 2 票，才允许选择 terminal/normal；单个 normal、全 uncertain、1:1 冲突均为 unresolved。
- unresolved 不再借 terminal cache 或默认 normal 发键；`_resolve_wayland_paste_sequence()` 会抛错，WebSocket ACK 因注入失败保持 `clear_input=false`。
- 首次 portal 会话使用 pre/post 两份判定：一侧可靠而另一侧 unresolved 时使用可靠证据；两侧可靠且冲突时取消，避免授权交互期间焦点变化导致误发。
- portal 中途失败后会按逆序 best-effort 释放已确认按下的键；测试已锁定 Ctrl press 成功、V press 失败时仍补发 Ctrl release。

### 环境与 helper 验证

- 新建 `.venv` 安装锁定依赖后完整 PC suite 已达到 112 tests OK，说明本轮平台层重构没有破坏 server ACK、网络、协议或托盘回归。
- 从 `.venv/bin/python` 调用时无法 in-process 导入 `gi`，代码成功自动切到 `/usr/bin/python3` helper；helper 输出与主进程新 ACTIVE-first 算法一致，连续 5 个样本均为同一真实 active window。这直接覆盖打包应用最关键的 helper 路径。
- 当前 clipboard 只读 MIME 列表包含 `text/plain;charset=utf-8`、`UTF8_STRING` 等文本类型，因此可以安全地把原文本只保存在进程内，短暂写入测试 token 后再恢复，不需要把用户剪贴板正文写入日志或文件。
- 真实 clipboard roundtrip 已通过：写入随机 token、回读相等、恢复旧文本、再次回读相等；这排除了安装 `wl-clipboard` 后仍发送旧图片内容的路径。
- 普通窗口 20 轮 helper 压力结果是 20/20 normal、116/116 样本同一 ACTIVE Chrome、0 reason；ACTIVE-first 对此前已复现的跨应用 stale focus 抖动产生了稳定改善。

### 终端实机验证的焦点控制限制

- 仅调用 `gnome-terminal` 新建窗口不会可靠抢占 GNOME Wayland 当前焦点；随后 20 轮采样继续稳定报告 Chrome，这证明分类器没有因为“存在一个 terminal 窗口”就误判 terminal，但该轮不是终端前台验收。
- 临时窗口在 AT-SPI 树中以 `gnome-terminal-server/frame/Voicing-Terminal-Test` 出现；某次局部枚举短暂显示 ACTIVE，下一次全局枚举又只显示 Chrome ACTIVE，说明测试必须在采样前明确验证目标 frame 当前 ACTIVE，不能把“窗口已创建”当作“窗口已聚焦”。

### 第二轮稳健性收紧

- ACTIVE 候选排序改为 dialog/alert > frame > window > 其他；同一最高优先级若仍有多个真实窗口，直接 unresolved。这样既能忽略底层 stale application/window，又不会在两个并存 frame 间任意选一个。
- terminal 名单现只保留在主进程分类器；system helper 负责返回带 `source/reason` 的原始 active/focused 证据，避免未来新增 terminal 时两份名单不一致。
- 诊断日志测试确认不会记录 AT-SPI window `name`，因此不会把文档标题、terminal title 或用户文本泄漏到日志；仅记录 app、role、证据来源与原因。

### 阶段 33 续接基线与启动预热决策

- 当前修改后的键盘专项为 55 项、完整 PC suite 为 115 项，续接后重跑均通过；`git diff --check` 也通过。
- 根 `AGENTS.md` / `CLAUDE.md` 仍保留“terminal 名单在主进程和 helper 重复”及“阶段 31 修复尚未实施”的旧描述，与当前实现不符，发布前必须两份同步修正。
- 当前首次实际粘贴会在 pre-portal 阶段才首次启动 AT-SPI/system-Python helper 探测。新增后台只读预热具有低风险价值：可提前初始化/诊断 AT-SPI 路径，但必须严格禁止创建 RemoteDesktop Portal session、缓存 terminal/normal 决策或发送任何按键。
- 预热实现已在真实 Wayland 会话验证：后台 probe 得到 6 个一致的 ACTIVE Chrome 样本并正常退出，进程内 `_PORTAL_BACKEND` 仍为 `None`；说明预热与授权/输入注入边界保持隔离。

### 发布配置与公开文档复核

- `.github/workflows/release.yml` 的 Ubuntu 22.04 job 已同步安装 `at-spi2-core`、`gir1.2-atspi-2.0`、`python3-gi`、`wl-clipboard`，DEB `Depends` 也包含同一组运行时依赖；该修改能让干净安装具备分类和 Wayland 文本剪贴板前提。
- 根中英文 README 与 Android 中英文 README 仍描述“焦点 unresolved 时回退 Ctrl+V/近期 terminal cache”，与当前三态安全取消、无 terminal cache 实现相反；v2.9.10 文档必须明确 unresolved 不发送快捷键且手机输入由 ACK 语义保留。
- 仓库记录中的 `/home/kevinlasnh/development/flutter-3.27.0/bin/flutter` 当前不存在且 `flutter` 不在 PATH；需要继续寻找本机 SDK或恢复固定 3.27.0 工具链后再执行 Android 验证。
- 本地严格复现 workflow 的 `dpkg-deb --build` 后，包内容保留构建用户 UID/GID，desktop 文件也随本机 umask 成为 0664；CI runner 会有同类风险。使用 `chmod 0644` 和 `dpkg-deb --root-owner-group` 后，包内目录/文件/链接全部为标准 `root/root` 与预期 mode。
- 官方 Flutter 3.27.0 archive MD5 与 HTTP 元数据一致，Android command-line tools ZIP 完整性校验通过；Flutter 3.27.0 默认 compileSdk/targetSdk 均为 35，项目另行锁定 NDK `27.0.12077973`。
- 底层 `type_text_at_cursor()` 虽已把 Wayland 默认恢复延迟设为 350ms，但正式入口 `voice_coding.type_text()` 仍传入 100ms，导致真实 WebSocket 路径绕过修复。删除显式参数后，Wayland 使用 350ms，其他平台仍使用底层 100ms 默认；新增双层测试锁定该不变量。
- 恢复工具链后 Android 本地 debug 与显式 debug-signing 豁免的 release APK 均可构建；release APK manifest 为 `2.9.10` / versionCode `11`，压缩包与签名结构校验通过。正式签名材料未写入本机或仓库，仍只由 Actions Secrets 提供。
- 最终 20 轮普通窗口采样再次全部选中同一 ACTIVE Chrome，且无 uncertain；结合此前 stale FOCUSED 复现，说明 ACTIVE-first 在普通窗口侧的稳定性已重复成立。
- 最终 PyInstaller frozen smoke 也通过 system-Python helper 得到 ACTIVE Chrome readiness，证明新启动预热已进入实际 onefile 产物；offscreen 无托盘和 9527 被已安装版占用属于受控 smoke 环境限制，不是新产物启动回归。

### 续接时的人工焦点协调证据

- 在用户尚未于真实终端建立 ACTIVE 焦点时，新增的验收脚本连续 20 轮都稳定识别为 Google Chrome normal，并因 terminal 全通过门槛未满足而明确输出 `FAILED_NO_KEYS_SENT`；这再次证明安全取消路径不会把普通窗口误当 terminal，也不会为了完成测试而发送快捷键。
- 仅靠聊天中的倒计时提示不足以建立终端焦点；更可靠的协调方式是由用户在目标终端执行唯一 sentinel `touch` 命令，令 shell 执行完成后自然保持 terminal ACTIVE，再由后台测试进程采样和粘贴。
- 本次 sentinel 在约 90 秒内未出现，后台进程已被中断；这不是实现失败，也没有产生 clipboard/Portal/键盘副作用。发布门槛仍要求用户实际触发该握手后取得 terminal 20/20、`portal_sequence=ctrl_shift_v`、成对 release、剪贴板恢复和可见文本证据。
- 当前源码的最终 PC 回归基线已提升为 122 tests OK，且语法与 diff 校验通过；剩余不确定性不在单元测试覆盖，而在 GNOME Wayland 的真实前台焦点与 Portal 投递时序，因此不能用更多 mocked tests 替代双场景实机门槛。
- v2.9.10 本地 release APK 实际大小为 31.7 MB，根 README 原有的约 21 MB 已过时；公开体积说明应写约 32 MB，避免发布页面与真实资产明显不一致。
- 真实 terminal ACTIVE 焦点无法由 GNOME Wayland 后台自动化可靠建立，且用户 sentinel 连续三个目标回合未触发；继续自动重试只会重复同一失败条件。必须由用户恢复目标后，在空白终端执行新的就绪握手，才能取得发布所需的 terminal/normal 双场景直接证据。

### Ghostty 的实际 AT-SPI 身份缺口

- 用户真实聚焦 Ghostty 后，分类器连续 20 轮都获得同一个可靠 ACTIVE frame，但 `app_name=Unnamed`、`role=frame`，因此旧逻辑确定性判 normal；这不是采样抖动，也不是 stale focus。
- 该 ACTIVE accessible 的 AT-SPI process ID 可可靠映射到 `/proc/<pid>/exe`、`comm` 与 `cmdline[0]` basename `ghostty`；应用 toolkit 为 GTK 4.14.5。子树只有 frame/panel，无 focused、editable 或 terminal 角色，说明继续扩大角色扫描也无法识别。
- 窗口标题可能包含用户路径或会话内容，不能用于 terminal 识别或日志；可执行文件 basename 是隐私风险更低、跨 Ghostty 标题变化稳定、且能复用现有 terminal 名单的身份信号。主进程和打包态 system-Python helper 必须同时输出 `process_name`，最终分类统一在主进程完成。
- `process_name` 修复在同一真实现场立即把 Ghostty 从 20/20 normal 翻转为 20/20 terminal，且所有样本仍来自同一 ACTIVE frame；这直接证明修复命中了身份根因，而不是依靠宽泛“unknown 即 terminal”或缓存掩盖问题。
- Portal 的独立测试进程必须像产品一样持有全局 Qt application；否则 `is_available()` 使用的临时 `QCoreApplication` 生命周期结束后可能让后续 Qt D-Bus request 超时。真实 `voice_coding.main()` 已始终持有 `QApplication`，无需因此修改产品代码。
- 在真实产品生命周期下，Chrome 与 Ghostty 两侧都已取得 Portal 的完整结构化证据：分别为 `ctrl_v` 4 事件和 `ctrl_shift_v` 6 事件，所有 modifier 均释放且 clipboard restore 均 MATCH。剩余非空内容 proof 应复用同一已授权 backend，而不是为每次断言新建 Portal session。
- GNOME 42 RemoteDesktop `Start` chooser 在无人值守状态下既不通过 AT-SPI 暴露可操作 action/坐标，也不接受临时 ydotool 的三种确认序列；继续盲试会增加误输入风险。非空 proof 因授权 UI 无法自动化而缺失，但实际 clipboard roundtrip、normal/terminal Portal 键序列和 modifier 释放已分别取得直接证据。
- `dpkg-deb --root-owner-group` 只规范 owner，不规范源目录 mode；即使 CI 常见 umask 为 022，workflow 仍应显式把 package root 目录设为 0755，才能保证本地与 CI 构建一致。

### v2.9.10 发布前门槛裁决

- 原故障链路已由直接证据闭环：旧实现把真实 Ghostty 的 `Unnamed/frame` 连续 20/20 判为 normal；加入 `process_name=ghostty` 后同一 ACTIVE 身份连续 20/20 判为 terminal，说明修复命中了身份根因而非依赖缓存或 unknown 猜测。
- Chrome 与 Ghostty 的真实 Portal 键序列、modifier 成对释放、Wayland clipboard 写入回读和恢复均已独立验证；结合 129 项 PC 回归与 24 项 Flutter 测试，现有证据足以完成原“稳定识别并稳定粘贴”的发布门槛。GNOME 42 chooser 阻止无人值守非空 proof 属于授权 UI 自动化限制，不能冒充产品输入失败，也不应继续以盲发按键绕过。
- `process_name` 只能保存和记录 basename；不得扩展为 PID、完整路径、命令行、窗口标题或正文。`Unnamed` 且没有可靠进程身份时必须保持 unresolved，不得恢复默认 Ctrl+V。
- Linux 发布包的可复现权限必须显式声明：`dpkg-deb --root-owner-group` 负责 root/root，workflow 的 `find ... chmod 0755` 负责目录，安装步骤/显式 chmod 负责可执行文件 0755 与元数据 0644；不能依赖构建机 umask。

### GitHub Release checksum 文件名契约

- `softprops/action-gh-release` 上传 `release-assets/<platform>/<filename>` 后，Release 页面只保留 `<filename>` basename；因此 `SHA256SUMS.txt` 也必须使用扁平 basename。若保留 CI artifact 子目录，哈希数值仍可正确，但用户在同一目录下载资产后无法直接运行 `sha256sum -c`。
- 发布后校验不能只比较 GitHub API 的 digest 或手工去前缀；验收门槛应实际下载全部资产，并在不改写 checksum 文件的情况下运行原生 `sha256sum -c SHA256SUMS.txt`。workflow 同时应断言固定条目数和文件名无 `/`，避免以后目录结构调整再次引入同类问题。

## 2026-07-28 最终交接结论

- 本次进度记录没有产生新的技术发现、实现变更或阻断项；阶段 33 与 `v2.9.10` 发布闭环保持完成状态。
- 本次 checkpoint 前的可恢复 Git 基线为 `e0c0074fd6f9a62ec725636e0d10be92d6f9b162`，对应已推送的 checksum workflow 防回归修复；`v2.9.10` tag 继续固定指向发布提交 `fa09391`，无需移动或重建。
- 对外最终交付基线为 GitHub Actions run `30330984843` 成功、Release `v2.9.10` 六个资产齐全，且修正版 `SHA256SUMS.txt` 可在扁平下载目录直接验证五个 payload。
