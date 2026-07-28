# 进度日志

## 会话：2026-06-13 18:25 CST

### 阶段 1：仓库元信息与长期记忆
- **状态：** complete
- **开始时间：** 2026-06-13 18:25 CST
- 执行的操作：
  - 按启动规则确认当前目录不在 L2 vault 下。
  - 读取 planning-with-files-zh skill 说明。
  - 检查仓库根目录，确认此前缺少 `task_plan.md`、`progress.md`、`findings.md`。
  - 读取 PWF 模板并查看仓库顶层结构。
  - 查询 ByteRover 长期记忆，未找到相关仓库背景。
- 创建/修改的文件：
  - 新增 `task_plan.md`
  - 新增 `findings.md`
  - 新增 `progress.md`

## 测试结果
| 测试 | 输入 | 预期结果 | 实际结果 | 状态 |
|------|------|---------|---------|------|
| Python 语法编译 | `python3 -m py_compile pc/voice_coding.py pc/voicing_protocol.py pc/device_identity.py pc/network_recovery.py pc/platform_utils.py pc/platform_keyboard.py pc/platform_autostart.py pc/platform_instance.py` | 无语法错误 | 通过，无输出 | pass |
| PC 单元测试 | `python3 -m unittest discover -s pc/tests` | 全部测试通过 | 29 个测试运行，27 个通过，2 个因缺少 `PyQt5` 导入失败 | blocked |
| Android 本地测试环境 | `command -v flutter` / `command -v dart` / `java -version` | 工具链可用 | Flutter、Dart、Java 未在 PATH 中发现 | blocked |

## 错误日志
| 时间戳 | 错误 | 尝试次数 | 解决方案 |
|--------|------|---------|---------|
| 2026-06-13 18:25 CST | 更新 PWF 时补丁上下文未匹配 | 1 | 重新读取三件套后使用更精确补丁 |
| 2026-06-13 18:25 CST | PC 单元测试导入 `voice_coding.py` 时缺少 `PyQt5` | 1 | 未安装依赖；记录为当前环境限制 |

## 五问重启检查
| 问题 | 答案 |
|------|------|
| 我在哪里？ | 阶段 5：交付总结 |
| 我要去哪里？ | 目录结构、核心代码、验证与总结 |
| 目标是什么？ | 全面说明当前仓库是在做什么 |
| 我学到了什么？ | 见 findings.md |
| 我做了什么？ | 见上方记录 |

### 阶段 2：目录结构与依赖梳理
- **状态：** complete
- 执行的操作：
  - 读取 `README.md`、`README.zh-CN.md`、`android/README.md`、`android/README.zh-CN.md`。
  - 读取 `pc/requirements.txt`、`android/voice_coding/pubspec.yaml`、`android/voice_coding/android/app/build.gradle`。
  - 读取 `protocol/voicing_protocol_contract.json`。
  - 查看 Android、PC 顶层文件列表和代码行数。
- 创建/修改的文件：
  - 更新 `findings.md`
  - 更新 `progress.md`
  - 更新 `task_plan.md`

### 阶段 3：核心代码阅读
- **状态：** complete
- 执行的操作：
  - 阅读 PC 端 `voice_coding.py` 中文本输入、WebSocket server、QR payload、主入口相关逻辑。
  - 阅读 PC 端 `voicing_protocol.py`、`device_identity.py`、`network_recovery.py`、`platform_utils.py`。
  - 阅读 Android 端 `voicing_connection_controller.dart`、`saved_server.dart`、`voicing_websocket.dart`、`connection_recovery_policy.dart`。
  - 阅读 Android 原生层 `MainActivity.kt` 和 Manifest。
  - 阅读协议契约测试、网络接口测试、保存设备测试。

### 阶段 4：验证与风险检查
- **状态：** complete
- 执行的操作：
  - 检查本地工具链：`python3` 可用；`python`、Java、Flutter/Dart 未在 PATH 中发现。
  - 检查 Python 依赖：当前环境缺少 `PyQt5`、`websockets`、`pyautogui`、`pyperclip`、`qrcode`、`psutil`，`PIL` 可用。
  - 执行 `python3 -m py_compile`，PC 端主要 Python 文件语法编译通过。
  - 执行 `python3 -m unittest discover -s pc/tests`，29 个测试中 27 个通过，2 个因缺少 `PyQt5` 导入失败。
  - 检查 `.gitignore`，发现 PWF 和仓库 agent markdown 当前被忽略。

### 阶段 5：交付总结
- **状态：** complete
- 执行的操作：
  - 准备向用户汇总项目用途、架构、运行方式、验证结果和风险点。
  - 完成中文总结交付。

### 阶段 6：初始化仓库级 Agent 配置
- **状态：** complete
- 执行的操作：
  - 确认仓库根此前没有 `CLAUDE.md` / `AGENTS.md`。
  - 新增 `CLAUDE.md` 与 `AGENTS.md`，内容基于已完成的仓库检查结果。
  - 配置内容覆盖项目定位、目录结构、核心运行行为、协议、开发命令、测试期望、发布规则和 agent 工作注意事项。
  - 运行 `diff -u <(tail -n +2 CLAUDE.md) <(tail -n +2 AGENTS.md)`，确认除 H1 外正文一致。
  - 运行 `git status --short --ignored --untracked-files=all`，确认两份文件当前被 `.gitignore` 忽略。
- 创建/修改的文件：
  - 新增 `CLAUDE.md`
  - 新增 `AGENTS.md`
  - 更新 `task_plan.md`
  - 更新 `findings.md`
  - 更新 `progress.md`

### 阶段 7：Ubuntu/Linux 可用性 Review
- **状态：** complete
- 执行的操作：
  - 阅读 `pc/platform_utils.py`、`pc/platform_keyboard.py`、`pc/platform_autostart.py`、`pc/voice_coding.py` 中 Linux 相关逻辑。
  - 阅读 README 中 Linux 支持说明和 GitHub Actions Linux 构建步骤。
  - 检查当前系统：Ubuntu 24.04.4 LTS、GNOME、Wayland，会话不满足项目当前 X11 运行前提。
  - 检查 X11 登录项，确认系统存在 `Ubuntu on Xorg`。
  - 检查 Python 依赖，确认当前环境缺少 PC 端 runtime 依赖且没有 `python3 -m pip`。
  - 检查系统依赖，确认 `libxcb-cursor0`、`xclip`、`xsel` 缺失。
  - 执行 `python3 pc/voice_coding.py --dev`，失败于缺少 `PyQt5`。
  - 执行 `PYTHONPATH=pc python3` 调用 `ensure_runtime_supported()`，确认 Wayland 下会主动报错。
  - 执行 Linux 相关纯单元测试 27 个，通过。
- 测试结果：
  - `python3 pc/voice_coding.py --dev`：blocked，缺少 `PyQt5`。
  - `ensure_runtime_supported()`：blocked，当前会话是 Wayland。
  - `python3 -m unittest pc.tests.test_platform_utils pc.tests.test_platform_autostart pc.tests.test_platform_keyboard pc.tests.test_network_recovery pc.tests.test_device_identity pc.tests.test_protocol_contract`：27 tests OK。

### 阶段 8：下次继续 Ubuntu 实机可用性修复
- **状态：** pending
- **记录时间：** 2026-06-13 19:28 CST
- 待做事项：
  - 用户决定本次先记录进度，下次继续完成 Ubuntu 可用性修复。
  - 下次应先让用户切换到 `Ubuntu on Xorg` 会话，再验证 `XDG_SESSION_TYPE=x11`。
  - 需要补齐系统依赖：至少 `libxcb-cursor0`，建议同时安装 `xclip` 或 `xsel`。
  - 需要建立可用 Python 运行环境并安装 `pc/requirements.txt`。
  - 完成后运行 `python3 pc/voice_coding.py --dev`，再用 Android 端扫码配对做端到端验证。
- 本次未执行的操作：
  - 未使用 sudo 安装系统包。
  - 未修改系统登录会话。
  - 未创建 Python 虚拟环境或安装 Python 包。

### 阶段 8：Ubuntu 环境复查
- **状态：** in_progress
- **记录时间：** 2026-06-17 CST
- 执行的操作：
  - 检查当前桌面会话变量，确认仍为 `XDG_SESSION_TYPE=wayland`、`DESKTOP_SESSION=ubuntu`。
  - 检查 Python 工具链，确认 `python3`、`pip3`、`python3 -m pip` 已可用。
  - 检查系统包，确认 `python3-pip`、`python3-venv`、`python3-pyqt5`、`python3-psutil`、`python3-pil` 已安装。
  - 检查 Linux 运行依赖，确认 `libxcb-cursor0`、`xclip`、`xsel` 仍未安装。
  - 检查 `pc/requirements.txt` 对应 Python 包导入和版本约束。
- 当前结论：
  - 仍需切换到 X11 会话。
  - 仍建议建立项目 venv 并安装 `pc/requirements.txt`，当前系统 Python 包版本与项目约束不完全一致。

### 阶段 8：Linux 当前系统代码适配讨论
- **状态：** in_progress
- **记录时间：** 2026-06-17 CST
- 执行的操作：
  - 阅读 `pc/platform_utils.py`，确认 Wayland 启动门禁集中在 `ensure_runtime_supported()`。
  - 阅读 `pc/platform_keyboard.py`，确认粘贴和 Enter 当前走 `pyautogui` 模拟按键。
  - 阅读 `pc/voice_coding.py::type_text()` 和 WebSocket 文本处理路径，确认手机端发送协议无需改动。
  - 搜索 README 和 Android 目录，确认现有文档明确 Linux 为 `Ubuntu 22.04+ GNOME X11`，Android 前端不参与桌面输入实现。
- 当前结论：
  - 为当前 Linux/Wayland 运行而改动时，优先范围是 PC 端后端/平台适配层。
  - 不应先动 Android Flutter UI 或协议。
  - 仅删除 Wayland 检查不够，必须替换或扩展 Linux 文本注入实现。

### 阶段 9：GNOME Wayland 同等 Windows 体验改造方案
- **状态：** in_progress
- **记录时间：** 2026-06-17 CST
- 执行的操作：
  - 使用 plan 工具拆解任务：现状确认、网络调研、方案对比、改造计划、PWF 同步。
  - 采样当前系统：Ubuntu 24.04.4 LTS、GNOME Shell 46.0、Wayland；portal 服务均已运行。
  - 通过 D-Bus introspection 确认 RemoteDesktop portal 支持键盘/鼠标/触摸，版本为 2。
  - 使用宿主 Web Search 与 `tavily-search` fallback 检索 XDG RemoteDesktop portal、libei、ydotool、wtype、GNOME Remote Desktop 相关资料。
  - 对照当前代码行号，确认现有输入链路为 `pyperclip` 写剪贴板 + `pyautogui` 触发 Ctrl+V/Enter。
- 当前结论：
  - Windows 同等效果要求自动写入当前光标、可自动 Enter、对 Android 端透明。
  - GNOME Wayland 下不应只删除启动门禁；必须引入新的 Linux 输入后端。
  - 推荐产品化方案是 RemoteDesktop portal 键盘会话；快速本机方案是 `wl-copy` + `ydotool` fallback。

#### 阶段 9 详细方案记录：让 Voicing 在当前 GNOME Wayland 上达到 Windows 同等效果
- **目标定义：**
  - 手机端扫码、连接、发送文本的行为保持不变。
  - PC 端在当前光标所在应用中自动输入手机发来的中文/英文文本。
  - Android 端 Auto Enter 语义保持不变：需要提交时，PC 端自动补发一次 Enter。
  - 尽量保持现有剪贴板恢复行为：写入临时文本、粘贴、短暂等待后恢复原剪贴板。
  - 对 Android Flutter UI、双端协议和 WebSocket/QR 连接模型透明，不引入新的手机端交互。

- **为什么不能只删除 Wayland 检查：**
  - 当前 `pc/platform_utils.py::ensure_runtime_supported()` 会在 Wayland 下直接阻断启动。
  - 即便删除这个阻断，`pc/voice_coding.py::type_text()` 仍依赖 `pyperclip.copy/paste` 写剪贴板，并调用 `platform_keyboard.paste_from_clipboard()`。
  - `pc/platform_keyboard.py` 当前用 `pyautogui.hotkey("ctrl", "v")` 和 `pyautogui.press("enter")` 模拟全局按键；这条路径适合 X11/Windows/macOS，但在 GNOME Wayland 下不可靠。
  - 因此核心不是“允许程序启动”，而是“替换 Linux Wayland 文本注入后端”。

- **代码改造边界：**
  - 主要修改 PC 端：
    - `pc/platform_utils.py`：把 Wayland 一刀切拒绝改为输入后端能力检测。
    - `pc/platform_keyboard.py`：从固定 `pyautogui` 改为可选择的输入 backend。
    - `pc/voice_coding.py::type_text()`：把剪贴板写入、粘贴、回车、恢复剪贴板封装到平台输入层，避免主业务函数知道 X11/Wayland 差异。
    - `pc/tests/test_platform_utils.py`、`pc/tests/test_platform_keyboard.py`：更新 Wayland 测试预期和新增 backend 选择测试。
  - 暂不修改：
    - Android Flutter UI。
    - Android 连接状态机。
    - `protocol/voicing_protocol_contract.json`。
    - QR payload/WebSocket 消息结构。

- **推荐架构：输入后端分层：**
  - 新增或重构为 `TextInputBackend`/`ClipboardBackend`/`KeyboardBackend` 组合。
  - 提供统一能力：
    - `type_text(text: str, auto_enter: bool)`
    - `paste_from_clipboard()`
    - `press_enter()`
    - `is_available()`
    - `describe_unavailable_reason()`
  - 后端选择顺序建议：
    - Windows：保留现有剪贴板 + Windows SendInput/pyautogui fallback。
    - macOS：保留现有剪贴板 + Command+V/Enter。
    - Linux X11：保留现有 `pyperclip + pyautogui`。
    - Linux GNOME Wayland：优先 RemoteDesktop portal keyboard backend。
    - Linux GNOME Wayland fallback：可选 `wl-copy`/剪贴板 + `ydotool` 发送 Ctrl+V/Enter。

- **产品化首选方案：XDG RemoteDesktop portal backend：**
  - 当前系统已经暴露 `org.freedesktop.portal.RemoteDesktop`，`AvailableDeviceTypes=7`，其中 bitmask `1` 是 KEYBOARD。
  - RemoteDesktop portal 支持 `NotifyKeyboardKeycode`、`NotifyKeyboardKeysym` 和 `ConnectToEIS`。
  - 第一版可优先使用 portal 的 `NotifyKeyboardKeycode`/`NotifyKeyboardKeysym` 发送 Ctrl+V 与 Enter，不直接接入 libei。
  - 典型流程：
    - 创建 RemoteDesktop session。
    - `SelectDevices` 请求 KEYBOARD。
    - `Start` session，接受 GNOME 授权提示。
    - 持有 session handle，后续粘贴时发送 Ctrl 按下、V 按下、V 释放、Ctrl 释放；Auto Enter 时发送 Enter 按下/释放。
  - 优点：
    - 符合 GNOME Wayland 安全模型。
    - 不需要 root，也不需要全局 `/dev/uinput` 权限。
    - 更适合作为 Voicing 的正式 Linux Wayland 支持方向。
  - 风险：
    - 首次启动或首次输入可能出现 GNOME 授权提示。
    - session 生命周期要处理好：portal session 被关闭、用户拒绝授权、锁屏/注销后断开。
    - D-Bus Request/Response 是异步模型，Python 实现要谨慎处理超时和错误。
    - `NotifyKeyboardKeysym`/`NotifyKeyboardKeycode` 对组合键和键码映射要做实机验证。

- **后续增强方案：libei / ConnectToEIS：**
  - 当前系统已有 `libei1` 和 `liboeffis1`，Ubuntu 包说明里 `libei` 是 Wayland emulated input client library，`oeffis` 用于 XDG RemoteDesktop portal D-Bus 通信。
  - `ConnectToEIS` 是更现代的输入事件通道；官方文档说明建立 EIS connection 后应只通过 EIS 发送输入事件，不能再混用 Notify*。
  - 不建议第一版直接做，因为 Python binding/ctypes/cffi 接入成本更高，测试面更大。
  - 可在 portal Notify* 后端跑通后作为第二阶段优化。

- **快速本机 fallback：`wl-copy` + `ydotool`：**
  - `wl-copy` 已存在，可用于 Wayland 剪贴板写入。
  - Ubuntu 仓库有 `ydotool`，它通过 Linux `/dev/uinput` 创建设备，能在 X11/Wayland 上模拟键盘输入。
  - 使用方式上可以让 Voicing 写剪贴板，然后调用 `ydotool key` 发送 Ctrl+V，Auto Enter 时发送 Enter。
  - 优点：
    - 实现快。
    - 效果最接近 Windows：全局当前焦点、自动粘贴、自动回车。
  - 风险：
    - 需要 `ydotoold` 常驻。
    - `ydotoold` 通常需要 `/dev/uinput` 权限，可能涉及 root、udev/group 或 systemd service 配置。
    - 安全边界较粗，因为它是系统级虚拟输入设备。
    - 不适合作为默认产品方案，但适合当前本机快速验证。

- **不推荐方案：`wtype`：**
  - `wtype` 依赖 Wayland compositor 支持 `virtual-keyboard` 协议。
  - 当前资料和 GNOME Mutter issue 均显示 GNOME 不支持该协议，因此不适合作为 Ubuntu GNOME 46 的主路径。

- **剪贴板实现建议：**
  - 第一版可以保留 `pyperclip`，但 Wayland 下优先探测 `wl-copy`/`wl-paste` 或 Qt Clipboard。
  - 更理想是把剪贴板读写抽象进 PC 平台层：
    - X11/Windows/macOS：现有 `pyperclip`。
    - Wayland：优先 `wl-copy`/`wl-paste` 或 Qt clipboard。
    - 若读取旧剪贴板失败，只记录 warning，不影响输入。
  - 粘贴本身不应由剪贴板模块触发，而应由 keyboard backend 负责。

- **启动检查改造建议：**
  - 当前 `ensure_runtime_supported()` 不应继续表达为“Wayland 不支持”。
  - 改为：
    - 检测当前平台和 session。
    - 在 Linux Wayland 下检查是否存在可用输入后端：RemoteDesktop portal 可用，或 fallback `ydotool` 可用。
    - 若没有可用后端，报明确错误：当前是 Wayland，但未能初始化 RemoteDesktop portal 键盘授权，也未找到可用 fallback。
  - 错误信息应指导用户如何处理，但不再默认要求切 X11。

- **测试计划：**
  - 单元测试：
    - Wayland 不再直接触发 RuntimeError。
    - RemoteDesktop portal 可用时 backend 选择 portal。
    - portal 不可用但 `ydotool` 可用时选择 fallback。
    - 两者都不可用时返回明确不可用原因。
    - `paste_from_clipboard()` 对不同 backend 调用正确。
    - `press_enter()` 对不同 backend 调用正确。
  - 本机集成测试：
    - 启动 PC 端，不再因 Wayland 直接退出。
    - Android 扫码连接成功。
    - VS Code 输入框、浏览器输入框、终端至少各测试一次文本输入。
    - 中文文本、英文文本、标点、换行/Auto Enter 分别测试。
    - 剪贴板恢复测试：输入前复制一段文本，Voicing 输入后确认剪贴板内容恢复。
    - 锁屏/解锁或 portal session 失效后，确认能重新初始化或给出清晰错误。

- **执行顺序建议：**
  - 第一步：先做输入后端抽象，不改变 Android 和协议。
  - 第二步：实现并 mock 测试 RemoteDesktop portal backend。
  - 第三步：实现 `ydotool` fallback，作为本机验证和失败兜底。
  - 第四步：修改 `ensure_runtime_supported()` 为能力检测。
  - 第五步：实机跑 PC 端 + Android 端端到端验证。
  - 第六步：若确认体验达标，再更新 README/CHANGELOG，把 Linux 支持从 “GNOME X11” 调整为 “GNOME X11 + GNOME Wayland beta” 或类似表述。

### 阶段 9：记录方案后准备提交与推送
- **状态：** in_progress
- **记录时间：** 2026-06-17 CST
- 执行的操作：
  - 用户要求“完成之后 push”。
  - 检查 Git 状态，确认当前 `task_plan.md`、`progress.md`、`findings.md` 被 `.gitignore` 忽略且未被 Git 跟踪。
  - 根据仓库全局 PWF 规则和本次 push 要求，准备从 `.gitignore` 中移除 PWF 三件套忽略规则。
  - 保持 `CLAUDE.md`、`AGENTS.md`、`.brv/`、Python cache 等本地 agent/config/artifact 文件继续忽略，不纳入提交。

### 阶段 9：GNOME Wayland 输入后端实现
- **状态：** complete
- **记录时间：** 2026-06-18 CST
- 执行的操作：
  - 按用户确认的稳定推荐方案，在 PC 端实现 GNOME Wayland RemoteDesktop portal 键盘后端。
  - `pc/platform_keyboard.py` 新增统一 `type_text_at_cursor()`、Wayland `wl-copy`/`wl-paste` 剪贴板路径、RemoteDesktop portal Ctrl+V/Enter 后端。
  - `pc/platform_utils.py` 将 Wayland 启动门禁改为 RemoteDesktop portal 键盘能力检测，不再一刀切阻断 Wayland。
  - `pc/voice_coding.py` 移除业务层直接 `pyperclip` 操作，改为调用平台输入层。
  - 更新 `pc/tests/test_platform_keyboard.py`、`pc/tests/test_platform_utils.py` 覆盖 Wayland portal、剪贴板恢复、后端分支和启动能力检测。
  - 更新 `README.md`、`README.zh-CN.md`、`CHANGELOG.md` 记录 GNOME Wayland 支持与首次 RemoteDesktop 授权提示。
  - 建立 `.venv` 并安装 `pc/requirements.txt`；系统级安装 `libxcb-cursor0`、`xclip`、`xsel`。
  - 安装 Flutter 3.27.0 到 `~/development/flutter-3.27.0`，安装 Android SDK 到 `~/Android/Sdk`。
- 测试结果：
  - `.venv/bin/python -m py_compile pc/voice_coding.py pc/platform_utils.py pc/platform_keyboard.py pc/platform_autostart.py pc/platform_instance.py pc/network_recovery.py pc/voicing_protocol.py pc/device_identity.py`：通过。
  - `.venv/bin/python -m unittest discover -s pc/tests`：63 tests OK。
  - `flutter analyze --no-fatal-infos --no-fatal-warnings`：通过，仍有 4 个既有 `withOpacity` info。
  - `flutter test`：通过。
  - `timeout 5s .venv/bin/python pc/voice_coding.py --dev`：启动到 WebSocket 监听 `192.168.50.113:9527` 后被 timeout 主动结束，证明当前 Wayland 会话下启动前置已通过。
  - `git diff --check`：通过。
  - `flutter build apk --debug`：用户询问后确认本次未改 Android native/Gradle，不需要继续；后台构建已停止，并还原由工具造成的 `pubspec.lock` 与 `gradlew` 权限变化。
- 当前结论：
  - 代码与前置验证已到 Android 实机扫码配对测试之前的状态。
  - 下一步应运行 PC 端常驻进程，并用 Android 手机验证扫码连接、文本输入、Auto Enter 与剪贴板恢复。

### 阶段 10：Android 实机扫码与端到端输入验证
- **状态：** pending
- **记录时间：** 2026-06-18 CST
- 待做事项：
  - 启动 `.venv/bin/python pc/voice_coding.py --dev` 并保持运行。
  - Android 端扫码当前 PC QR 或使用已保存设备连接。
  - 验证普通文本、中文文本、Auto Enter、空 commit 回车与剪贴板恢复。
  - 首次 Wayland 输入时如出现 GNOME RemoteDesktop 键盘授权提示，需要用户批准。

### 阶段 10：托盘菜单弹出修复
- **状态：** complete
- **记录时间：** 2026-06-18 CST
- 问题：
  - 用户反馈 PC 端启动后右键托盘不弹菜单。
- 执行的操作：
  - 检查 `ModernTrayIcon`，发现此前只在 `QSystemTrayIcon.Context` 激活原因下弹出自定义菜单。
  - GNOME/Ubuntu 托盘宿主不稳定地把托盘点击映射为 `Trigger` / `DoubleClick` / `Context`，只监听 `Context` 会导致右键或点击完全无反应。
  - 在 Linux 下为 `QSystemTrayIcon` 设置原生 `QMenu` 作为右键 fallback。
  - 将自定义菜单触发兼容 `Trigger`、`DoubleClick`、`Context`。
  - 新增 `pc/tests/test_voice_coding_tray.py` 覆盖托盘激活原因判断。
- 测试结果：
  - `.venv/bin/python -m py_compile pc/voice_coding.py pc/tests/test_voice_coding_tray.py`：通过。
  - `.venv/bin/python -m unittest pc.tests.test_voice_coding_tray pc.tests.test_platform_keyboard pc.tests.test_platform_utils`：37 tests OK。
  - `.venv/bin/python -m unittest discover -s pc/tests`：65 tests OK。
  - `git diff --check`：通过。
- 注意：
  - 当前 9527 端口被 `python` pid 136115 占用，说明已有旧 PC 端实例在运行；需要重启 PC 端才能加载托盘修复。

### 阶段 10：记录进度并准备提交推送
- **状态：** in_progress
- **记录时间：** 2026-06-18 CST
- 执行的操作：
  - 用户要求先记录进度，然后 push。
  - 检查当前分支为 `main`，远端为 `origin`。
  - 检查待提交改动集中在 GNOME Wayland 输入后端、托盘菜单 fallback、测试、README/CHANGELOG 和 PWF 三件套。
  - 运行 `git diff --check`，结果通过。
- 待完成：
  - 创建 Git commit。
  - 推送到 `origin/main`。

## 会话：2026-06-18（晚）CST

### Linux 托盘前端交互修复（自定义菜单 → 原生菜单）
- **状态：** complete
- 问题：GNOME Wayland 上托盘右键弹两个菜单、图标每 200ms 抖动、启动左上角闪黑框。
- 执行的操作：
  - 细颗粒度审查 `pc/voice_coding.py` 托盘链路；定位 P0 双菜单回归来自上次 `c2bcf71` 同时设 `setContextMenu` + Context 触发自定义菜单。
  - 决策（用户选定）：Linux 改用系统原生 `QMenu`，自定义 Fluent 菜单仅 Windows/macOS 保留。
  - `on_tray_activated` 平台分流：Linux 右键交给 `setContextMenu`/宿主，左键/双击才 `_popup_native_menu()`，杜绝双菜单。
  - `update_icon` 加 `_current_icon_key` 去重，状态未变不 `setIcon`，消除 Linux SNI/AppIndicator 每 200ms 抖动。
  - Linux 跳过自定义菜单预热；QR 预热改为 `ensurePolished()` 不 `show()`，消除 Wayland 启动黑闪。
- 测试结果：
  - `unittest discover -s pc/tests` 69 OK；新增/更新托盘原生菜单路径测试。
  - 用户实机确认托盘交互正常（右键单菜单、左键同菜单、无黑闪）。

### GNOME Wayland portal 输入修复（D-Bus uint32 序列化）
- **状态：** complete
- 问题：手机端发文本触发 `RuntimeError: RemoteDesktop portal SelectDevices 调用失败: Expected type 'u' for option 'types', got 'i'`；后续 `NotifyKeyboardKeysym` 的 `state` 也有同样 `'u' vs 'i'` 问题。
- 执行的操作：
  - 探测 PyQt5 QtDBus：`QDBusArgument.add(value, QMetaType.UInt)` 生成 uint32。
  - 实证（对 live portal）：`SelectDevices.types` 用 `QVariant(QDBusArgument(uint))`；`NotifyKeyboardKeysym.state` 用裸 `QDBusArgument(uint)`，keysym 保持普通 int（本机 portal 内省期望 `(oa{sv}iu)`）。两者均经 live portal 验证通过。
  - 新增 `_dbus_uint()` / `_dbus_uint_variant()` 助手；更新 `pc/tests/test_platform_keyboard.py` 锁定新的类型化传参。
- 测试结果：
  - `py_compile` 通过；`unittest discover -s pc/tests` 69 OK。
  - 实机：portal 授权弹窗出现 = SelectDevices→Start 链路成功，uint 修复有效。

### GNOME portal 永久授权调研与决策
- **状态：** complete
- 调研（修好 tvly SSL 后联网）：GNOME `xdg-desktop-portal-gnome` 不保留 RemoteDesktop 授权，每次启动/重启必弹授权；无 `persist_mode`、无预授权 API（`persist_mode` 只对屏幕捕获生效）。GNOME 官方 issue #175 确认；KDE Plasma 6.3+ 已有预授权；GNOME 尚无，Chrome Remote Desktop 团队在推进标准 API。
- 决策（用户选定）：保持 portal 原样，接受每次启动一次授权点击。综合评估 portal 全面优于 ydotool（安全/零部署/可分发/跨发行版/前瞻性）；ydotool 仅"无弹窗"占优，代价是 `/dev/uinput` 权限降级 + 每用户都要配，不可作为已发布应用默认。ydotool 仅作可选 opt-in 留记，未实现。

### tvly CLI 代理修复（仓库外）
- 现象：宿主自带 WebSearch 实际未联网；tavily 走 clash-verge（127.0.0.1:7897）对 `api.tavily.com` SSL EOF（分流劫持到坏出口），但 tavily 直连本就可达。
- 修复：`~/.bashrc` 增加 `tvly()` 包装函数去掉代理变量直连 tavily；不影响其他工具走代理。

## 会话：2026-06-18（深夜）CST — 自定义菜单美化 + 原生菜单分隔条 + QR 闪烁修复迭代

### 自定义 Fluent 菜单（Windows/macOS）美化
- **状态：** complete（代码已落地；本机 Linux 走原生菜单，无法在当前环境肉眼确认，待 Windows 实机复核）
- 问题：菜单宽度偏大与文字不匹配；项之间有横条分隔。
- 执行的操作：
  - 实测 `ModernMenuWidget`：`sizeHint=164`，但 `adjustSize()` 给出 `200`（多约 36px）→ 右侧留白。
  - `show_at_position` 增加 `self.setFixedWidth(self.sizeHint().width())`，宽度收紧到 164（随最长文字自适应）。
  - `setup_ui` 删除 4 个 separator（qr/sync、sync/startup、startup/log、log/quit 之间）。
  - `_finish_open_animation` 第一版尝试 reorder（先 resize 再 show container）→ **未解决 QR 闪烁**（假设错根因）。
- 测试：新增 `CustomMenuLayoutTests`（无分隔条恰好 5 项、宽度收紧到 sizeHint）；`unittest discover` 71 OK。
- 注意：这些改动对 Linux 原生菜单无效（Linux 不走 ModernMenuWidget）。

### Linux 原生菜单分隔条
- **状态：** complete + 用户实机确认
- 问题：用户在 Linux 看到的分隔条来自 `_setup_native_context_menu` 的 4 个 `addSeparator()`。
- 修复：删除原生菜单 4 个 `addSeparator()`，菜单变平铺无横条。
- 用户确认：菜单正常，无分隔符。✅

### QR 弹窗闪烁修复（迭代两版）
- **状态：** in_progress（第一版无效；第二版消除"下方第二个 QR"，但"到达中心时自身闪动"仍存）
- 现象：点「显示 QR 码」→ QR 从右上角飞到中心，到达瞬间在中心 QR 下方闪出第二个 QR 再消失。
- **第一版（无效）**：`_finish_open_animation` reorder（先 `_restore_dialog_geometry` 再 `container.show()`）→ 用户反馈仍闪，假设错根因。
- **第二版（部分成功）**：新理论——打开动画期间顶层窗口是大 `canvas_rect`（QR 在旧缓冲中部约 y400），收尾时窗口**可见状态下** resize+move（原点从托盘→中心），Mutter 把上一帧旧缓冲按**新原点**重显 → QR 出现在「中心+偏移」= 中心下方。
  - 修法：收尾先 `hide()` 解除 surface 映射，不可见时 `_restore_dialog_geometry`，再 `show()` 出容器；期间保持 `_animation_mode=True` 让 `focusOutEvent` 延迟关闭检查直接 return。
  - 用户确认：**下方第二个 QR 不再闪** ✅，但**到达中心时自身会闪动一次**（新现象，待继续处理）。

### 待办（本次未解决）
- [ ] Linux 原生菜单宽度仍不自适应（用户反馈"宽度没有自适应"）。注：GNOME QMenu 理论上按文字自适应，需复核用户看到的具体表现（是否文字被截断 / 有多余留白 / emoji 导致偏宽）。
- [ ] QR 到达中心时自身闪动一次（第二版修复引入或暴露的新现象）。

### 原生菜单宽度收紧（用户反馈"右边空白多"）
- **状态：** complete（代码落地，待用户肉眼确认；padding 值可微调）
- 诊断：`actionGeometry` 显示每项占满整菜单宽（168px），但文本仅 84px → 默认 QMenu item 水平 padding 过大。
- 修复：`_setup_native_context_menu` 给 `native_menu` 加 `QMenu::item { padding: 6px 12px 6px 20px; }`（左 20 留勾选框位、右 12 收窄；不改颜色/边框，保留 GTK 原生外观）。offscreen 实测 168→134。
- 测试：`unittest discover` 71 OK。

### QR 自身闪动 — 整体梳理完成，方案待用户定（A/B）
- **状态：** in_progress（仅梳理，未改码；太晚了留到下次）
- 整体梳理结论：两个闪动同根——"从右上角飞入"效果要求动画期窗口是大 canvas（托盘→中心），收尾缩到 end_rect；而 Wayland 上**任何收尾的 resize 或 hide/show remap 都会闪**（可见 resize 闪重影 / hide-show 闪自身）。
- 两条整体改造路：A 改成"窗口恒定 end_rect 尺寸 + 位置移动 + 内容缩放 + 淡入"（无 resize，保留飞入，中等改动需重写动画）；B 砍飞入改"原地缩放+淡入"（最稳，无飞入）。待用户选。

## 会话：2026-06-19 CST — QR 弹窗改为中心直接出现

### QR 飞入动画移除
- **状态：** implemented，待用户手动启动肉眼确认
- 用户选择 B 方案：砍掉从托盘/右上角飞入，QR 弹窗直接在屏幕中心出现即可。
- 执行的操作：
  - `QRCodeDialog.show_from()` 不再构造 start rect，也不再调用旧 `_start_dialog_animation()`。
  - QR 窗口始终保持最终尺寸和中心几何，直接 `show()`，避免 Wayland/Mutter 上跨 canvas resize/remap 带来的重影和自身闪动。
  - 关闭路径也改为直接隐藏，不再飞回托盘锚点，避免关闭时复用同类几何动画问题。
  - 清理 `QRCodeDialog` 中旧飞行动画、快照 pixmap、`contentRect`、收尾 hide/show remap 等遗留代码；保留扫码成功态对勾动画。
  - 新增 `QRCodeDialogOpenTests`，锁定 QR 打开直接落在中心 rect，不走旧动画路径。
- 测试结果：
  - `.venv/bin/python -m py_compile pc/voice_coding.py pc/tests/test_voice_coding_tray.py`：通过。
  - `.venv/bin/python -m unittest discover -s pc/tests`：72 tests OK。
  - `git diff --check`：通过。
- 待确认：
  - 用户手动启动 PC 端，检查「显示 QR 码」是否直接在中心出现且无闪动。
  - 顺便复核 Linux 原生菜单宽度收紧是否满足视觉预期。

## 会话：2026-06-19 CST — 整体前端逻辑 Review

### PC + Android 前端审查
- **状态：** complete
- 用户要求不继续改托盘，全面 review 整体前端代码是否还有逻辑错误。
- 检查范围：
  - PC：`pc/voice_coding.py` 的 PyQt 托盘、自定义菜单、Linux 原生菜单、QR 弹窗、QR 成功态、同步开关广播、run_tray UI 信号。
  - Android：`lib/main.dart`、`voicing_connection_controller.dart`、`voicing_websocket.dart`、`saved_server.dart`、`connection_recovery_policy.dart` 与 Kotlin native WebSocket bridge。
- 验证结果：
  - `.venv/bin/python -m unittest discover -s pc/tests`：72 tests OK。
  - `flutter test`：22 tests OK。
  - `flutter analyze --no-fatal-infos --no-fatal-warnings`：通过；仅 4 个既有 `withOpacity` info。
- 主要 review 发现：
  - Android native WebSocket `sink.add()` 是 fire-and-forget MethodChannel 调用，上层 `sendText()`/ping/shadow 的 try/catch 捕不到异步发送失败；可能出现输入被记录/清空但消息未发送到 PC。
  - PC 同步开关广播在新的 asyncio loop/thread 中对 `websockets` 连接对象执行 `send()`，这些连接对象属于 server loop；跨 loop 发送有兼容风险，可能导致 Android 端收不到即时 `sync_state`，只能等下一次 pong/文本响应同步。
  - Android QR 新设备替换确认发生在成功态展示之后；用户取消替换时，体验上会先看到成功再取消退出，语义不严谨但不是数据破坏问题。
  - PC QR 弹窗中心直接出现路径代码上成立，但仍待用户真实 GNOME Wayland 手测视觉效果。

## 会话：2026-06-19 CST — 整体前端 Review 问题修复

### 修复 review 发现的前端逻辑问题
- **状态：** implemented + verified，待 push
- 执行的操作：
  - Android `VoicingWebSocketSink.add()` 改为 `Future<void>`；native WiFi WebSocket 发送现在等待 MethodChannel 返回，`sendWebSocketMessage` 返回非 `true` 或 native 报错时会向上抛异常。
  - Kotlin `sendWebSocketMessage` 在 OkHttp `webSocket.send(message)` 返回 `false` 时返回 `send_failed`，成功时明确返回 `true`。
  - Android controller 的 `sendText()`、ping、shadow increment、commit auto-enter 路径改为 await 发送；发送失败时不再记录/清空已发送文本，必要时触发断开重连。
  - QR 连通性 probe 的探测消息发送改为处理 nullable future，并把发送失败记录为 probe 失败，避免未捕获异步错误。
  - Android QR 替换设备流程改为先执行 `_confirmScannedServer()`，用户接受后才展示扫码成功态、保存并重连；取消时不再先展示成功。
  - PC `AppState` 记录 WebSocket server 所属 `asyncio` event loop；同步开关即时广播用 `asyncio.run_coroutine_threadsafe()` 投递回 server loop，不再新建 loop/thread 操作已有 websocket 连接。
  - 新增 PC tray 测试覆盖 QR 中心直接打开，以及同步状态广播使用 server loop/loop 缺失时跳过。
- 测试结果：
  - `.venv/bin/python -m py_compile pc/voice_coding.py pc/tests/test_voice_coding_tray.py`：通过。
  - `.venv/bin/python -m unittest discover -s pc/tests`：74 tests OK。
  - `~/development/flutter-3.27.0/bin/flutter analyze --no-fatal-infos --no-fatal-warnings`：退出码 0；仅保留既有 4 个 `withOpacity` info。
  - `~/development/flutter-3.27.0/bin/flutter test`：22 tests passed。
  - `git diff --check`：通过。
- 用户约束：
  - 本轮未执行 APK 编译。
  - 本轮未执行 deb 编译。

### 提交与推送
- **状态：** complete
- Git commit：`0349c64 Fix frontend send and sync state handling`
- Push 结果：已推送 `main -> origin/main`

## 会话：2026-06-19 CST — Linux terminal 输入失效调查

### 普通输入框可输入但 terminal 不生效
- **状态：** investigation complete，待用户确认修复策略
- 执行的操作：
  - 阅读 `pc/platform_keyboard.py`，确认 GNOME Wayland 当前通过 RemoteDesktop portal 发送 `Ctrl+V` 来触发剪贴板粘贴。
  - 检查本机 GNOME Terminal schema，确认默认 paste keybinding 是 `<Control><Shift>v`。
  - 联网检索 GNOME Terminal 官方快捷键、XDG RemoteDesktop portal `NotifyKeyboardKeysym` 文档、GNOME Shell Introspect 权限限制。
  - 本机调用 GNOME Shell `GetWindows` / `GetRunningApplications`，均返回 `AccessDenied`，说明不能默认依赖该私有接口识别当前焦点窗口。
  - 探测 AT-SPI 和 wl-clipboard primary selection：AT-SPI 可列出应用但焦点识别不够稳定；`wl-copy --primary` / `wl-paste --primary` 可用。
- 结论：
  - 根因是 terminal 默认粘贴快捷键不是 `Ctrl+V`，而是 `Ctrl+Shift+V`；当前程序对所有 Wayland 目标都只发 `Ctrl+V`。
  - 推荐后续修复：为 Linux Wayland portal 后端增加 paste strategy（`ctrl-v` / `ctrl-shift-v` / `shift-insert`），并在写剪贴板时同时写 CLIPBOARD 与 PRIMARY。短期若只修用户当前 terminal，可让 Wayland terminal 模式发送 `Ctrl+Shift+V`。

## 会话：2026-06-19 CST — GNOME Wayland Terminal 粘贴模式实现

### AT-SPI Auto 检测 + 手动粘贴模式
- **状态：** implemented + verified，待用户手动启动测试
- 执行的操作：
  - `pc/platform_keyboard.py` 新增 `PasteMode`：`AUTO` / `NORMAL` / `TERMINAL` / `COMPAT`。
  - GNOME Wayland RemoteDesktop portal 粘贴序列改为按模式选择：
    - Auto：通过 AT-SPI 读取焦点 accessible；role/app 命中 terminal 时发送 `Ctrl+Shift+V`，否则发送 `Ctrl+V`。
    - 普通：固定 `Ctrl+V`。
    - 终端：固定 `Ctrl+Shift+V`。
    - 兼容：固定 `Shift+Insert`。
  - 当前 venv 没有 `gi`，因此检测器先尝试当前进程，失败后调用 `/usr/bin/python3` 只读查询 AT-SPI；查询失败时静默回退普通 `Ctrl+V`。
  - Wayland 写剪贴板时同时写 CLIPBOARD 和 PRIMARY，以支持 `Shift+Insert` 兼容模式；粘贴后尽量恢复原 PRIMARY。
  - Linux 原生托盘菜单和 Windows/macOS 自定义菜单都新增“粘贴模式”项，点击按自动 → 普通 → 终端 → 兼容循环。
  - 更新 README / README.zh-CN / CHANGELOG 的 GNOME Wayland 粘贴说明。
  - 新增/更新 `pc/tests/test_platform_keyboard.py` 和 `pc/tests/test_voice_coding_tray.py` 测试。
- 验证结果：
  - `.venv/bin/python -m py_compile pc/voice_coding.py pc/platform_keyboard.py pc/tests/test_platform_keyboard.py pc/tests/test_voice_coding_tray.py`：通过。
  - `.venv/bin/python -m unittest discover -s pc/tests`：85 tests OK。
  - `git diff --check`：通过。
  - 本轮未执行 APK 编译。
  - 本轮未执行 deb 编译。
- 待用户手测：
  - 启动 PC 端后，默认粘贴模式显示“自动粘贴”。
  - 在普通输入框接收手机文本，应继续粘贴成功。
  - 在 terminal 接收手机文本，Auto 若识别到 terminal 应自动走 `Ctrl+Shift+V`；若未识别，托盘切到“终端粘贴”再测。
  - Auto Enter 仍由手机端设置控制，粘贴后再触发 Enter。

### 收尾复核
- **状态：** ready for manual test，未提交
- 收紧 AT-SPI fallback：只有 focused 对象缺失或明显落在 `gnome-shell` / 桌面壳层时，才扫描 ACTIVE terminal 兜底；若 focused 已是 Chrome/编辑器等普通应用，则按普通输入框处理，避免误发 `Ctrl+Shift+V`。
- 新增单元测试覆盖普通 focused app 不被 ACTIVE terminal 覆盖。
- 最终验证：
  - `.venv/bin/python -m py_compile pc/voice_coding.py pc/platform_keyboard.py pc/tests/test_platform_keyboard.py pc/tests/test_voice_coding_tray.py`：通过。
  - `.venv/bin/python -m unittest discover -s pc/tests`：86 tests OK。
  - `git diff --check`：通过。
  - 本轮未执行 APK 编译。
  - 本轮未执行 deb 编译。

### 用户实测确认
- **状态：** complete，准备提交并 push
- 用户手动启动 PC 端测试后确认：当前版本在 terminal 里面也能自动输入。
- 该结果说明 GNOME Wayland Auto 粘贴模式在用户当前 terminal 环境中可识别 terminal 焦点并正确走 `Ctrl+Shift+V` 路径；普通输入框路径此前保持可用。

## 会话：2026-06-19 CST — 最新 PC / Android 代码全面逻辑复查

### 全面 review 与边界修复
- **状态：** implemented + verified，待用户确认是否提交/push
- 复查范围：
  - PC：`voice_coding.py` WebSocket 消息处理、ACK 清空策略、同步状态广播、托盘/QR、`platform_keyboard.py` 剪贴板/Wayland portal 粘贴路径。
  - Android：`voicing_connection_controller.dart` 连接/重连/扫码/shadow/commit 状态机、`voicing_websocket.dart` native WiFi WebSocket wrapper、Kotlin native bridge、主 UI 绑定。
- 修复的确定问题：
  - PC 输入层：若剪贴板已写入新文本后粘贴或 Auto Enter 失败，旧剪贴板/PRIMARY 可能不恢复；已将恢复逻辑放入 `finally`。
  - PC WebSocket ACK：文本注入失败时仍可能返回默认 `clear_input=true`，导致手机端清空尚未成功到达 PC 的输入；已改为仅注入成功时清空。
  - Android native WebSocket：重连/释放时调用 `close()`，若 native 连接尚未返回 id 或连接已失败，可能留下未处理 Future 错误；已改为 best-effort 幂等关闭。
- 新增测试：
  - `pc/tests/test_platform_keyboard.py` 覆盖粘贴失败仍恢复剪贴板。
  - `pc/tests/test_voice_coding_server.py` 覆盖 PC 注入失败时 ACK 不清空手机输入。
  - `android/voice_coding/test/voicing_websocket_test.dart` 覆盖 native sink `close()` 在 id 失败和 id 可用两种情况下的行为。
- 验证结果：
  - `.venv/bin/python -m py_compile pc/voice_coding.py pc/platform_utils.py pc/platform_keyboard.py pc/platform_autostart.py pc/platform_instance.py pc/network_recovery.py pc/voicing_protocol.py pc/device_identity.py pc/tests/test_platform_keyboard.py pc/tests/test_voice_coding_server.py`：通过。
  - `.venv/bin/python -m unittest discover -s pc/tests`：88 tests OK。
  - `~/development/flutter-3.27.0/bin/flutter test`：24 tests passed。
  - `~/development/flutter-3.27.0/bin/flutter analyze --no-fatal-infos --no-fatal-warnings`：退出码 0；仍只有既有 4 个 `withOpacity` info。
  - `git diff --check`：通过。
  - `dart format --output=none --set-exit-if-changed lib/voicing_websocket.dart test/voicing_websocket_test.dart`：通过。
- 本轮未执行 APK 编译。
- 本轮未执行 deb 编译。

## 会话：2026-06-19 CST — v2.9.5 Release 触发准备

### GitHub Actions APK / DEB 构建触发
- **状态：** ready to commit and push tag
- 确认 `.github/workflows/release.yml` 仅在推送 `v*` tag 时触发 release 构建；直接 push `main` 不会编 APK / Linux 包。
- 准备新版本 `v2.9.5`，因为现有最新 tag `v2.9.4` 已存在，不能复用。
- 已更新版本号：
  - PC `APP_VERSION=2.9.5`
  - Android `pubspec.yaml version=2.9.5+6`
  - README / README.zh-CN 徽章与 release tag 示例更新为 `2.9.5`
  - CHANGELOG 增加 `2.9.5` bilingual release block
- 已补 GitHub Actions Linux `.deb` 打包：
  - `build-linux` 继续上传 `voicing-linux-x86_64`
  - 新增 `voicing-linux-amd64.deb`
  - Release notes、SHA256SUMS 和 GitHub Release assets 均加入 `.deb`
- 本地验证：
  - `py_compile`：通过
  - `flutter analyze --no-fatal-infos --no-fatal-warnings`：退出码 0，仅既有 4 个 `withOpacity` info
  - `flutter test`：24 tests passed
  - `dart format --output=none --set-exit-if-changed lib/voicing_websocket.dart test/voicing_websocket_test.dart`：通过
  - `git diff --check`：通过
- 按用户要求，本地未编 APK / deb；将通过 GitHub Actions 编译。

### GitHub Actions Linux CI 修复
- **状态：** implemented + verified，准备提交并重新触发 release workflow
- 已推送 `v2.9.5` tag 并触发 GitHub Actions run `27815558477`。
- 旧 run 结果：
  - Android APK：成功，release APK 已构建并上传 workflow artifact。
  - Windows EXE：成功。
  - macOS DMG：成功。
  - Linux binary / DEB：失败前被跳过。
  - Publish GitHub Release：因 Linux job failure 被跳过。
- 失败根因：
  - Linux job 在 `Run desktop validation` 执行 `python -m unittest discover -s tests` 时，headless runner 无图形会话，Qt 尝试加载 `xcb` 平台插件并 abort。
- 修复内容：
  - `.github/workflows/release.yml` 的 `build-linux` job 增加 `QT_QPA_PLATFORM=offscreen`。
  - `pc/tests/test_voice_coding_tray.py` 在导入 PyQt 前设置 `os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")`。
- 本地验证：
  - `../.venv/bin/python -m py_compile ... tests/test_voice_coding_tray.py`：通过。
  - `QT_QPA_PLATFORM=offscreen ../.venv/bin/python -m unittest discover -s tests`：88 tests OK。
  - `QT_QPA_PLATFORM=offscreen ../.venv/bin/python -c "from voice_coding import calculate_broadcast_addresses, get_all_local_interfaces; ..."`：通过。
  - `git diff --check`：通过。
- 本轮仍未在本地编译 APK 或 deb。

### v2.9.5 Release 发布完成
- **状态：** complete
- 已提交并推送 `ab749bf Fix Linux release validation on headless CI` 到 `main`。
- 已将 `v2.9.5` tag 更新到 `ab749bf` 并 force push 重新触发 release workflow；原因是旧 tag run 失败且 GitHub Release 尚未创建。
- 新 GitHub Actions run：
  - Run ID：`27815951469`
  - URL：`https://github.com/kevinlasnh/Voicing/actions/runs/27815951469`
  - 结论：success
- 发布页面：
  - `https://github.com/kevinlasnh/Voicing/releases/tag/v2.9.5`
- 已确认 Release assets：
  - `voicing.apk`
  - `voicing-linux-amd64.deb`
  - `voicing-linux-x86_64`
  - `voicing-windows-x64.exe`
  - `voicing-macos-arm64.dmg`
  - `SHA256SUMS.txt`
- 本轮没有在本地执行 APK 或 DEB 编译，所有发布产物均由 GitHub Actions 构建。

## 会话：2026-06-19 CST — v2.9.6 Linux deb 启动修复

### deb 运行时误报修复
- **状态：** implemented + verified，准备提交并触发 `v2.9.6`
- 用户反馈：安装 `v2.9.5` 的 `voicing-linux-amd64.deb` 后，GNOME Wayland 启动弹出“没有可用的 RemoteDesktop portal 键盘能力”。
- 本机确认：
  - `dpkg -s voicing` 显示已安装版本为 `2.9.5`。
  - `/usr/bin/gdbus ... AvailableDeviceTypes` 返回 `(<uint32 7>,)`，portal 键盘能力本身可用。
  - `/opt/voicing/voicing --dev` 可复现打包版误报。
- 已按用户要求卸载错误 deb：
  - `sudo -n apt-get remove -y voicing`
  - 卸载后 `/opt/voicing` 与 `/usr/bin/voicing` 不再存在。
  - 未清理用户配置、日志或源码目录。
- 修复内容：
  - 新增 `platform_utils.system_subprocess_env()`，用于恢复/清理 PyInstaller frozen app 的 `LD_LIBRARY_PATH`。
  - `platform_utils` 的 `gdbus` portal 能力探测改用系统命令环境。
  - `platform_keyboard` 的 `wl-copy`、`wl-paste` 和系统 Python AT-SPI helper 也改用系统命令环境。
  - 版本更新到 `2.9.6`：PC `APP_VERSION=2.9.6`，Android `pubspec.yaml version=2.9.6+7`，README / README.zh-CN / CHANGELOG 对齐。
- 验证结果：
  - `../.venv/bin/python -m py_compile ...`：通过。
  - `QT_QPA_PLATFORM=offscreen ../.venv/bin/python -m unittest discover -s tests`：92 tests OK。
  - `~/development/flutter-3.27.0/bin/flutter analyze --no-fatal-infos --no-fatal-warnings`：No issues found。
  - `~/development/flutter-3.27.0/bin/flutter test`：24 tests passed。
  - 本地临时 PyInstaller frozen smoke test：能进入 WebSocket 监听阶段，不再报 portal 键盘能力不可用；offscreen 下系统托盘不可用为预期。
  - `git diff --check`：通过。
- 本轮未在本地打 APK 或 DEB；后续通过 GitHub Actions 产出 `v2.9.6`。

### v2.9.6 Release 发布完成
- **状态：** complete
- 已提交并推送 `cb12a21 Fix packaged Linux portal detection` 到 `main`。
- 已推送 `v2.9.6` tag 触发 GitHub Actions release workflow。
- GitHub Actions run：
  - Run ID：`27817118952`
  - URL：`https://github.com/kevinlasnh/Voicing/actions/runs/27817118952`
  - 首次结果：macOS `Create DMG` 因 `hdiutil: create failed - Resource busy` 失败；Android、Linux、Windows 均成功。
  - 处理方式：执行 failed-job rerun。
  - 最终结论：success。
- 发布页面：
  - `https://github.com/kevinlasnh/Voicing/releases/tag/v2.9.6`
- 已确认 Release assets：
  - `voicing.apk`
  - `voicing-linux-amd64.deb`
  - `voicing-linux-x86_64`
  - `voicing-windows-x64.exe`
  - `voicing-macos-arm64.dmg`
  - `SHA256SUMS.txt`
- 已复核本机错误 deb 卸载状态：`dpkg-query` 无 `voicing` 包记录，`/opt/voicing` 和 `voicing` 命令入口均不存在；未清理用户配置、日志或源码目录。
- 本轮没有在本地执行 APK 或 DEB 编译，所有发布产物均由 GitHub Actions 构建。

## 会话：2026-06-19 17:42 CST — 公开文档同步 Linux 使用说明

### README / Android README / CHANGELOG 更新
- **状态：** complete
- 按用户要求更新公开文档，范围：
  - `README.md`
  - `README.zh-CN.md`
  - `android/README.md`
  - `android/README.zh-CN.md`
  - `CHANGELOG.md`
- 更新内容：
  - 说明 Linux/GNOME Wayland 日常推荐保持桌面端"自动粘贴"。
  - 说明自动粘贴会对普通输入框发送 Ctrl+V，对 terminal 焦点发送 Ctrl+Shift+V。
  - 说明托盘菜单包含粘贴模式，可手动切换自动 / 普通 / 终端 / 兼容。
  - 修正 Linux 开机自启说明：Ubuntu GNOME 通过 `~/.config/autostart/voicing.desktop` 登录后启动，不是 Windows 注册表。
  - 说明 GNOME Wayland 下程序可以自启，但 RemoteDesktop 键盘授权仍可能在登录或启动后要求用户手动允许。
  - Android README 补充手机端用户在 Linux/GNOME Wayland 桌面端配合使用时需要知道的自动粘贴与授权提示。
- 验证结果：
  - `git diff --check -- README.md README.zh-CN.md android/README.md android/README.zh-CN.md CHANGELOG.md`：通过。
  - `rg` 检查确认旧的"注册表方式" Linux 自启描述已移除。

## 会话：2026-06-19 CST — GNOME Wayland Auto 粘贴稳定性修复

### Terminal 偶发退回 Ctrl+V 调查与修复
- **状态：** complete
- 用户反馈：PC 端输入在 terminal 里仍偶发执行 `Ctrl+V`，没有稳定使用 `Ctrl+Shift+V`。
- 执行的操作：
  - 恢复 PWF 上下文，确认此前阶段 16 已实现 AT-SPI Auto terminal 检测和手动粘贴模式。
  - 复查 `pc/platform_keyboard.py`、`pc/voice_coding.py`、`pc/tests/test_platform_keyboard.py` 中 Auto 粘贴分支。
  - 本机 GNOME Wayland 下连续探测 `_get_focused_accessible_info()`，复现 AT-SPI 查询偶发 `None`，导致旧 Auto 逻辑把未知状态当普通输入框并发送 `Ctrl+V`。
  - 按用户“稳定识别最高优先级”的要求修改 `pc/platform_keyboard.py`：
    - AT-SPI helper timeout 从 `0.35s` 提高到 `0.8s`。
    - Auto 模式最多重试 3 次焦点检测。
    - 最近确认过 terminal 时保留短期 terminal 记忆。
    - 明确普通 app 才走 `Ctrl+V`；焦点未知或不可靠时走终端安全的 `Ctrl+Shift+V`。
    - 扩展 terminal app 名称集合，并同步系统 Python AT-SPI helper 内的识别表。
  - 更新 `README.md`、`README.zh-CN.md`、`android/README.md`、`android/README.zh-CN.md`、`CHANGELOG.md`，说明 Auto 模式在无法稳定确认焦点时会优先使用 terminal-safe `Ctrl+Shift+V`。
  - 补充 `pc/tests/test_platform_keyboard.py`，覆盖 retry、terminal cache、明确普通 app 清缓存、未知焦点 terminal-safe 等行为。
- 验证结果：
  - `.venv/bin/python -m py_compile pc/voice_coding.py pc/platform_utils.py pc/platform_keyboard.py pc/platform_autostart.py pc/platform_instance.py pc/network_recovery.py pc/voicing_protocol.py pc/device_identity.py pc/tests/test_platform_keyboard.py`：通过。
  - `.venv/bin/python -m unittest pc.tests.test_platform_keyboard`：39 tests OK。
  - `.venv/bin/python -m unittest discover -s pc/tests`：97 tests OK。
  - `git diff --check`：通过。
  - 本机 GNOME Wayland terminal 焦点压力测试：连续 12 次 `_resolve_auto_paste_mode()` 均返回 `terminal`。
- 本轮未执行 Android analyze/test，也未执行 APK 或 DEB 编译。

## 会话：2026-06-19 CST — v2.9.7 Release 发布

### GitHub Actions release workflow
- **状态：** complete
- 执行的操作：
  - 更新版本号：PC `APP_VERSION=2.9.7`，Android `pubspec.yaml version=2.9.7+8`。
  - 更新 README / README.zh-CN 的版本徽章与 release tag 示例。
  - 将 CHANGELOG 的 Unreleased 修复说明落到 `2.9.7` 发布块。
  - 本地验证：
    - `.venv/bin/python -m py_compile ...`：通过。
    - `.venv/bin/python -m unittest discover -s pc/tests`：97 tests OK。
    - `~/development/flutter-3.27.0/bin/flutter analyze --no-fatal-infos --no-fatal-warnings`：退出码 0，仍有既有 4 个 `withOpacity` info。
    - `~/development/flutter-3.27.0/bin/flutter test`：24 tests passed。
    - `git diff --check`：通过。
  - 提交并推送 `30854a1 Improve Linux terminal paste detection` 到 `origin/main`。
  - 推送 `v2.9.7` tag 触发 GitHub Actions。
- Actions 结果：
  - Run ID：`27824263798`
  - URL：`https://github.com/kevinlasnh/Voicing/actions/runs/27824263798`
  - 结论：success。
  - Windows EXE、macOS DMG、Linux binary/DEB、Android APK 和 Publish GitHub Release jobs 均成功。
- 发布页面：
  - `https://github.com/kevinlasnh/Voicing/releases/tag/v2.9.7`
- 已确认 Release assets：
  - `voicing.apk`
  - `voicing-linux-amd64.deb`
  - `voicing-linux-x86_64`
  - `voicing-windows-x64.exe`
  - `voicing-macos-arm64.dmg`
  - `SHA256SUMS.txt`
- 本轮没有在本地执行 APK 或 DEB 编译，所有发布产物均由 GitHub Actions 构建。

## 会话：2026-06-19 CST — Auto Enter 可靠性修复

### Android commit / PC Enter ACK 链路修复
- **状态：** complete，未提交
- 用户反馈：自动 Enter 仍有问题，要求再次检查代码。
- 执行的操作：
  - 复查 PC `handle_client()`、`type_text()`、`press_enter()`、Wayland portal Enter 发送路径。
  - 复查 Android `sendText()`、shadow increment、`_finalizeShadowInput(forceEnter:)` 和 ACK 处理路径。
  - 查看本机 PC 日志，未发现近期 `press_enter` 相关异常；日志主要是此前 portal 能力探测和无托盘环境错误。
  - 修复 PC：
    - `AUTO_ENTER_SETTLE_DELAY_SEC` 从 `0.15` 提高到 `0.35`。
    - 新增 `press_enter_after_settle()`，粘贴稳定窗口后再发送 Enter，并把异常转换为 `False`。
    - WebSocket commit 分支现在 Enter 成功才 ACK `clear_input=true`；失败 ACK `clear_input=false`，不再让异常直接打断 handler。
  - 修复 Android：
    - `_finalizeShadowInput(forceEnter: true)` 发出空 commit 后不再立即清空输入框。
    - 成功清空改为等待 PC ACK，复用现有 `_handleMessage()` 对 `clear_input=true` 的清空逻辑。
  - 更新 `CHANGELOG.md` 的 Unreleased 修复说明。
  - 补充 `pc/tests/test_voice_coding_server.py` 覆盖 commit Auto Enter 成功/失败 ACK。
- 验证结果：
  - `.venv/bin/python -m py_compile pc/voice_coding.py pc/tests/test_voice_coding_server.py`：通过。
  - `.venv/bin/python -m unittest pc.tests.test_voice_coding_server pc.tests.test_platform_keyboard`：42 tests OK。
  - `.venv/bin/python -m unittest discover -s pc/tests`：99 tests OK。
  - `~/development/flutter-3.27.0/bin/dart format --output=none --set-exit-if-changed lib/voicing_connection_controller.dart`：通过。
  - `~/development/flutter-3.27.0/bin/flutter analyze --no-fatal-infos --no-fatal-warnings`：退出码 0，仍只有既有 4 个 `withOpacity` info。
  - `~/development/flutter-3.27.0/bin/flutter test`：24 tests passed。
  - `git diff --check`：通过。
- 本轮未执行 APK 或 DEB 编译。

## 会话：2026-06-19 CST — Android 到 PC 发送核心链路最终审查

### 发送后端审查
- **状态：** complete，未提交
- 用户实测 Auto Enter “还算不错”后，要求最终检查 Android 到 PC 的发送核心后端逻辑。
- 审查范围：
  - Android controller：`sendText()`、`_sendShadowIncrement()`、`_finalizeShadowInput()`、`_handleMessage()`、断线重连。
  - Android WebSocket：Dart `VoicingWebSocketSink`、native WiFi WebSocket wrapper。
  - Kotlin native bridge：`connectWifiWebSocket`、`sendWebSocketMessage`、OkHttp listener 事件回传。
  - PC：`handle_client()`、`type_text()`、`press_enter_after_settle()`、平台输入层 Enter/Paste。
  - 协议：Android/Python constants 与 `protocol/voicing_protocol_contract.json`。
- 审查结论：
  - Submit 发送：Android 发送成功后等待 PC ACK 清空；PC 注入失败时 ACK `clear_input=false`，不会误清手机输入。
  - Shadow 发送：increment 发送成功后才推进 `_lastSentLength`；PC 对 shadow ACK 不清空。
  - Auto Enter commit：Android 发送空 commit 后等待 PC ACK；PC Enter 成功才 ACK 清空，失败保留输入。
  - Native 发送：Kotlin `webSocket.send()` 返回 false 或未连接时会报错，Dart `sink.add()` 可捕获；不再 fire-and-forget。
  - 断线：connection generation 会丢弃旧连接消息，failure/closed 会触发重连路径。
  - 协议字段一致，无需更新 contract。
- 发现：
  - 未发现新的阻断级发送核心逻辑问题。
  - 残余非阻断点：commit 发送成功后 Android 会先记录 sent history，再等 PC ACK；如果 PC ACK false 后用户重试，历史可能重复，但不会丢文本。
- 本轮复用此前刚完成的验证结果：
  - PC `unittest discover -s pc/tests`：99 tests OK。
  - Flutter analyze：退出码 0，仍只有既有 `withOpacity` info。
  - Flutter test：24 tests passed。
  - `git diff --check`：通过。

## 会话：2026-06-19 CST — GNOME Wayland Auto 粘贴普通窗口误判修复

### 自动粘贴普通窗口回归修复
- **状态：** complete，未提交
- 用户反馈：自动粘贴模式下 terminal 能粘贴，但普通窗口不能粘贴。
- 执行的操作：
  - 复查 `pc/platform_keyboard.py` 的 `_resolve_auto_paste_mode()`、AT-SPI focused/active fallback 和系统 Python helper。
  - 确认根因：未知焦点无近期 terminal 缓存时仍默认返回 `PasteMode.TERMINAL`，导致普通窗口收到 `Ctrl+Shift+V`。
  - 修改 `pc/platform_keyboard.py`：
    - `_scan_atspi_desktop()` 在 focused 信息不可靠时返回 active accessible 信息，不再只找 active terminal。
    - `_resolve_auto_paste_mode()` 仅在明确 terminal 或近期 terminal 缓存有效时走终端粘贴；完全未知且无 terminal 缓存时走普通粘贴。
    - 同步 `_ATSPI_FOCUS_HELPER`，让系统 Python helper 也返回 active 普通窗口信息。
  - 更新 `pc/tests/test_platform_keyboard.py`，覆盖未知焦点默认普通、近期 terminal 缓存仍走终端、shell 焦点下 active 普通窗口走普通等路径。
  - 更新 `README.md`、`README.zh-CN.md`、`android/README.md`、`android/README.zh-CN.md`、`CHANGELOG.md` 的当前行为说明。
- 验证结果：
  - `.venv/bin/python -m py_compile pc/voice_coding.py pc/platform_utils.py pc/platform_keyboard.py pc/platform_autostart.py pc/platform_instance.py pc/network_recovery.py pc/voicing_protocol.py pc/device_identity.py pc/tests/test_platform_keyboard.py pc/tests/test_voice_coding_server.py`：通过。
  - `.venv/bin/python -m unittest pc.tests.test_platform_keyboard pc.tests.test_voice_coding_server`：44 tests OK。
  - `.venv/bin/python -m unittest discover -s pc/tests`：101 tests OK。
  - `git diff --check`：通过。

## 会话：2026-06-19 CST — v2.9.8 Release 发布

### 发布前版本与验证
- **状态：** complete
- 用户要求更新并推送新的 GitHub Actions release。
- 执行的操作：
  - 检查 `.github/workflows/release.yml`，确认 release workflow 由 `v*` tag 触发，且要求 `CHANGELOG.md` 中存在对应版本块。
  - 将 `CHANGELOG.md` 的 Unreleased 内容落到 `2.9.8`。
  - 更新 `pc/voice_coding.py` 的 `APP_VERSION` 到 `2.9.8`。
  - 更新 `android/voice_coding/pubspec.yaml` 到 `2.9.8+9`。
  - 更新 README / README.zh-CN 的版本徽章和 release tag 示例到 `v2.9.8`。
  - 保留 Flutter 3.27.0 刷新的 `android/voice_coding/pubspec.lock`。
- 发布前验证结果：
  - `.venv/bin/python -m py_compile pc/voice_coding.py pc/platform_utils.py pc/platform_keyboard.py pc/platform_autostart.py pc/platform_instance.py pc/network_recovery.py pc/voicing_protocol.py pc/device_identity.py pc/tests/test_platform_keyboard.py pc/tests/test_voice_coding_server.py`：通过。
  - `.venv/bin/python -m unittest discover -s pc/tests`：101 tests OK。
  - `~/development/flutter-3.27.0/bin/dart format --output=none --set-exit-if-changed lib/voicing_connection_controller.dart`：通过，0 changed。
  - `~/development/flutter-3.27.0/bin/flutter analyze --no-fatal-infos --no-fatal-warnings`：退出码 0，仅既有 4 个 `withOpacity` info。
  - `~/development/flutter-3.27.0/bin/flutter test`：24 tests passed。
- 提交与推送：
  - 提交：`b80a398 Release v2.9.8 input fixes`
  - 已推送 `main`：`4733cce..b80a398`
  - 已推送 tag：`v2.9.8`
- Actions 结果：
  - Run ID：`27833313385`
  - URL：`https://github.com/kevinlasnh/Voicing/actions/runs/27833313385`
  - 结论：success。
  - Android APK、Windows EXE、macOS DMG、Linux binary/DEB 和 Publish GitHub Release jobs 均成功。
- 发布页面：
  - `https://github.com/kevinlasnh/Voicing/releases/tag/v2.9.8`
- 已确认 Release assets：
  - `voicing.apk`
  - `voicing-linux-amd64.deb`
  - `voicing-linux-x86_64`
  - `voicing-windows-x64.exe`
  - `voicing-macos-arm64.dmg`
  - `SHA256SUMS.txt`

## 会话：2026-06-20 CST — 本机安装与自启验证记录

### v2.9.8 deb 与 GNOME autostart 检查
- **状态：** complete
- 用户要求卸载当前电脑上的 Voicing：
  - 检测到本机安装 `voicing 2.9.7 install ok installed`，入口 `/usr/bin/voicing`，实际文件 `/opt/voicing/voicing`。
  - 未发现正在运行的 Voicing 进程，未发现用户自启项。
  - 执行 `sudo -n apt-get remove -y voicing` 成功卸载旧 deb 包。
  - 复查确认 `dpkg-query` 无 `voicing` 记录，`command -v voicing` 无输出，`/opt/voicing` 不存在，未清理用户数据/日志。
- 用户随后安装从 GitHub 下载的最新 deb，并要求检查版本和开机自启：
  - `dpkg-query` 确认本机为 `voicing 2.9.8 install ok installed`。
  - GitHub latest release 确认为 `v2.9.8`。
  - `/usr/bin/voicing` 指向 `/opt/voicing/voicing`，实际二进制存在且可执行。
  - `~/.config/autostart/voicing.desktop` 存在，启用 `X-GNOME-Autostart-enabled=true`，并指向 `/opt/voicing/voicing`。
  - 当前桌面为 `ubuntu:GNOME` / Wayland，匹配 `OnlyShowIn=GNOME;`。
- 结论：
  - 本机已安装最新 `v2.9.8` deb。
  - GNOME 登录后自动启动已配置好；这不是系统服务级开机前启动，仍属于用户登录后的 autostart。

## 会话：2026-06-22 CST — Auto 粘贴 AT-SPI 稳定性调研

### GNOME Wayland 自动识别逻辑复查
- **状态：** complete，未改代码
- 用户反馈：当前自动粘贴仍不够稳定，要求先调研现有自动识别逻辑及改法。
- 执行的操作：
  - 阅读 `pc/platform_keyboard.py` 中 `PasteMode`、`_resolve_wayland_paste_sequence()`、`_resolve_auto_paste_mode()`、AT-SPI in-process/system-python helper、active fallback 和 terminal cache 逻辑。
  - 阅读 `pc/voice_coding.py` 中托盘粘贴模式切换逻辑，确认菜单仅循环切换 Auto/Normal/Terminal/Compat。
  - 本机采样 raw AT-SPI：Chrome 前台时 `FOCUSED` 连续返回 `gnome-shell/window`，`ACTIVE` 返回 Chrome。
  - 本机采样项目封装后的 `_get_focused_accessible_info()`：Chrome 前台 20/20 返回 Chrome/normal；Ghostty 前台 80/80 返回 ghostty/terminal，单次耗时约 289-575ms。
  - 联网查阅 AT-SPI/GNOME/RemoteDesktop portal 资料，确认 portal 只负责键盘事件，不能提供目标窗口类型；GNOME 私有窗口 introspection 不适合作为普通应用默认方案。
- 调研结论：
  - AT-SPI raw focused 不是稳定真相；当前 active fallback 在本机常用应用中有效，但“一次明确结果立刻决策”仍容易被短暂旧窗口/错误窗口影响。
  - 推荐把 `_resolve_auto_paste_mode()` 改成小时间窗口采样 + terminal/normal/uncertain 分类投票，保留 terminal cache 作为打平/全不确定兜底。

## 会话：2026-06-22 CST — GNOME Wayland Auto 粘贴采样投票实现

### 500ms 窗口采样投票
- **状态：** complete，未提交
- 用户确认采用 500ms 时间窗口，在稳定基础上窗口内能采几次采几次，并要求实现和测试。
- 执行的操作：
  - 修改 `pc/platform_keyboard.py`：
    - 新增 500ms AT-SPI 采样窗口、40ms 采样间隔、最多 8 个样本。
    - `_resolve_auto_paste_mode()` 改为对 `terminal` / `normal` / `uncertain` 分类投票，terminal 多数走 `Ctrl+Shift+V`，normal 多数走 `Ctrl+V`。
    - 票数打平或全不确定时保留 3 秒 terminal cache 作为兜底；明确 normal 多数会清 terminal cache。
    - 系统 Python AT-SPI helper 改为一次子进程内循环采样并输出 JSON list，避免每个样本重复启动 Python 导致 500ms 窗口实际只能采到 1 次。
  - 更新 `pc/tests/test_platform_keyboard.py`，覆盖 terminal 多数、normal 多数、打平使用 terminal cache、系统 helper 多样本解析、采样窗口 max samples 等路径。
  - 更新 `CHANGELOG.md`、`README.md`、`README.zh-CN.md`、`android/README.md`、`android/README.zh-CN.md`。
- 验证结果：
  - `.venv/bin/python -m unittest pc.tests.test_platform_keyboard`：45 tests OK。
  - `.venv/bin/python -m py_compile pc/voice_coding.py pc/platform_utils.py pc/platform_keyboard.py pc/platform_autostart.py pc/platform_instance.py pc/network_recovery.py pc/voicing_protocol.py pc/device_identity.py pc/tests/test_platform_keyboard.py pc/tests/test_voice_coding_server.py`：通过。
  - `.venv/bin/python -m unittest discover -s pc/tests`：105 tests OK。
  - `git diff --check`：通过。
  - 本机 sanity check：系统 Python helper 单次进程内采到 3 个 Ghostty 样本，Auto 判定 terminal；当前安装版 `/opt/voicing/voicing` 正在运行并占用 9527，因此未启动源码版覆盖用户当前会话。

## 会话：2026-06-22 CST — v2.9.9 Release 发布准备

### 版本同步与发布前验证
- **状态：** complete
- 用户要求推送 Actions，并确认 Android 代码是否更新。
- 结论：Android 业务代码未更新；本次只改了 Android README 文档和 `android/voice_coding/pubspec.yaml` 版本元数据，以便 release 产物版本同步到 `2.9.9+10`。
- 执行的操作：
  - `CHANGELOG.md` 新增 `2.9.9` 发布块。
  - `pc/voice_coding.py` `APP_VERSION` 更新为 `2.9.9`。
  - `android/voice_coding/pubspec.yaml` 更新为 `2.9.9+10`。
  - README / README.zh-CN 版本徽章和 tag 示例更新为 `v2.9.9`。
- 发布前验证结果：
  - `.venv/bin/python -m py_compile pc/voice_coding.py pc/platform_utils.py pc/platform_keyboard.py pc/platform_autostart.py pc/platform_instance.py pc/network_recovery.py pc/voicing_protocol.py pc/device_identity.py pc/tests/test_platform_keyboard.py pc/tests/test_voice_coding_server.py`：通过。
  - `.venv/bin/python -m unittest discover -s pc/tests`：105 tests OK。
  - `~/development/flutter-3.27.0/bin/flutter analyze --no-fatal-infos --no-fatal-warnings`：退出码 0，仅既有 4 个 `withOpacity` info。
  - `~/development/flutter-3.27.0/bin/flutter test`：24 tests passed。
  - `git diff --check`：通过。
- 提交与推送：
  - 提交：`d57313b Release v2.9.9 paste stability`
  - 已推送 `main`：远端 `refs/heads/main` 指向 `d57313be0c19082b6bf2cd0e5ae63be44b9d2ea4`。
  - 已推送 tag：`v2.9.9`，远端 `refs/tags/v2.9.9` 指向同一提交。
- Actions 结果：
  - Run ID：`27927791710`
  - URL：`https://github.com/kevinlasnh/Voicing/actions/runs/27927791710`
  - 结论：success。
- 发布页面：
  - `https://github.com/kevinlasnh/Voicing/releases/tag/v2.9.9`
- 已确认 Release assets：
  - `voicing.apk`
  - `voicing-linux-amd64.deb`
  - `voicing-linux-x86_64`
  - `voicing-windows-x64.exe`
  - `voicing-macos-arm64.dmg`
  - `SHA256SUMS.txt`

## 会话：2026-06-22 CST — 本机旧版卸载与 v2.9.9 安装确认

### PC deb 卸载与重装状态记录
- **状态：** complete
- 用户要求先卸载当前 PC 端 Voicing，以便下载新版；随后要求记录进度并 push。
- 卸载前状态：
  - `dpkg-query` 显示本机安装 `voicing 2.9.8 install ok installed`。
  - `command -v voicing` 返回 `/usr/bin/voicing`。
  - 发现两个运行中的 `/opt/voicing/voicing` 进程：`3260`、`3751`。
  - `~/.config/autostart/voicing.desktop` 存在，指向 `/opt/voicing/voicing`。
- 执行的卸载操作：
  - 先向旧的 `/opt/voicing/voicing` 进程发送 `SIGTERM`，复查后旧进程已停止。
  - 执行 `sudo -n apt-get remove -y voicing`，成功移除 `voicing 2.9.8` deb 包。
  - 复查确认当时 `voicing` 包不存在、`voicing` 命令不存在、`/opt/voicing` 不存在。
  - 删除旧的 `~/.config/autostart/voicing.desktop`，未删除用户数据或日志。
- 记录进度前复核到的新状态：
  - 用户已安装新版，`dpkg-query` 显示 `voicing 2.9.9 install ok installed`。
  - `command -v voicing` 返回 `/usr/bin/voicing`。
  - `/opt/voicing` 已恢复存在。
  - 当前运行中的新版进程为 `/opt/voicing/voicing`，PID：`57593`、`57596`。
  - GNOME 用户级自启文件已恢复存在，内容包含 `Exec=/opt/voicing/voicing`、`TryExec=/opt/voicing/voicing`、`OnlyShowIn=GNOME;`、`X-GNOME-Autostart-enabled=true`。
- 结论：
  - 旧版 `2.9.8` 已卸载完成。
  - 本机当前已安装并运行 `voicing 2.9.9`。
  - 自启项已经随新版恢复。

---
*每个阶段完成后或遇到错误时更新此文件*

## 会话：2026-07-28 CST — 阶段 33 续接与发布前收敛

### 上下文恢复与当前基线复核
- **状态：** in_progress
- 已重新完整读取 `planning-with-files-zh` skill，并运行 session catchup；恢复脚本未报告遗漏上下文。
- 已确认当前目录 `/home/kevinlasnh/Projects/Voicing` 未命中 Second Brain Path Guard，当前 goal 仍为 active，分支为 `main`。
- 当前未提交业务改动仍为 `.github/workflows/release.yml`、`pc/platform_keyboard.py`、`pc/tests/test_platform_keyboard.py` 与 PWF 三件套；根 `AGENTS.md` / `CLAUDE.md` 保持本地忽略且全文一致。
- 基线验证结果：
  - `.venv/bin/python -m unittest pc.tests.test_platform_keyboard`：55 tests OK。
  - `.venv/bin/python -m unittest discover -s pc/tests`：115 tests OK。
  - `git diff --check`：通过。
- 已确认两份本地 Agent Markdown 中仍有两处过时说明：system helper 已不再重复维护 terminal 名单，阶段 31 的修复也已经实施；发布前需同步更正。
- 决定补充 GNOME Wayland 启动时只读 AT-SPI 预热：后台采样并记录 readiness，不启动 Portal、不缓存粘贴模式、不发送按键，降低首次真实粘贴才初始化探测链的冷启动成本。

### 启动时只读 AT-SPI 预热
- **状态：** complete
- `pc/platform_keyboard.py` 新增 `start_wayland_focus_prewarm()`：仅 GNOME Wayland 创建 daemon thread，后台运行只读焦点采样；worker 只记录脱敏 readiness/votes/sample 元数据，异常不阻断应用启动。
- `pc/voice_coding.py` 在 runtime 支持检查通过后、网络与 WebSocket 启动前触发预热；该路径不会实例化 RemoteDesktop Portal backend、不会发送按键，也不会缓存后续粘贴模式。
- `pc/tests/test_platform_keyboard.py` 新增非 Wayland 跳过、daemon thread、脱敏日志和非致命失败测试；`pc/tests/test_voice_coding_tray.py` 新增启动顺序测试。
- 真实 Wayland 预热线程验证：6/6 样本均为当前 ACTIVE Chrome，`readiness=ready`，线程正常结束，`portal_backend_created=False`。
- 验证结果：
  - 键盘专项：59 tests OK。
  - 托盘/启动专项：13 tests OK。
  - 完整 PC suite：120 tests OK。
  - `py_compile` 与 `git diff --check`：通过。

### 发布配置、版本点与 Android 工具链复核
- **状态：** in_progress
- 已完整读取仓库根 Agent Markdown 和 Release workflow 的 Linux/发布段，确认验证矩阵、tag 发布顺序和 Release 资产清单。
- 已确认 Linux runner 与 DEB 控制文件均已加入 AT-SPI、system Python GI 和 `wl-clipboard` 依赖。
- 已定位 v2.9.10 需要同步的版本点：PC `APP_VERSION`、Android `pubspec.yaml`、CHANGELOG、根 README 版本徽章/tag 示例，以及四份中英文使用文档中的 Wayland Auto 语义。
- 当前 `flutter` 不在 PATH，历史固定 SDK 路径也不存在；正在继续定位本机 Flutter/JDK 17 工具链。

### v2.9.10 版本、文档与 Linux 产物
- **状态：** in_progress
- 已同步 PC `2.9.10`、Android `2.9.10+11`、CHANGELOG、根 README 徽章/tag 示例，以及根/Android 中英文 Wayland Auto 行为说明。
- 新文档明确：Auto 只依据当前 ACTIVE 窗口的可靠证据发送 Ctrl+V 或 Ctrl+Shift+V；unresolved/冲突时不发快捷键，并通过失败 ACK 保留手机文本。
- 根 `AGENTS.md` / `CLAUDE.md` 已同步修正 helper/terminal 名单和阶段 31 的过时说明；两份 SHA-256 一致，H1 正确，仍保持本地 ignore。
- 使用 `.venv` PyInstaller 6.19.0 完成 Linux onefile 构建，生成 59 MiB x86-64 ELF； standalone 副本摘要与原始 `Voicing` 一致。
- 首次按旧 workflow 方式构建 DEB 时发现包内容为 `kevinlasnh/kevinlasnh` 且 desktop 文件受 umask 成为 0664；已修改 workflow 固定元数据 0644，并使用 `dpkg-deb --root-owner-group`。
- 修复后本地 `voicing-linux-amd64.deb` 为版本 2.9.10、amd64，依赖包含 AT-SPI/Python GI/`wl-clipboard`，内容全部 `root/root`，可执行文件 0755、desktop/icon 0644。
- 发布链路复查发现 `voice_coding.type_text()` 仍显式传入 `restore_delay_sec=0.1`，覆盖了平台层新增的 Wayland 350ms 默认值；已删除该覆盖，使真实 WebSocket 路径按平台选择等待时间。
- 新增平台层 Wayland 默认恢复延迟测试与 server 调用契约测试；键盘专项现为 60 tests OK，server 专项 4 tests OK，`py_compile` / `git diff --check` 通过。由于此修复发生在首次 PyInstaller 构建后，最终发布前必须重建 Linux binary/DEB。

### Android 本地工具链恢复
- **状态：** in_progress
- 已安装 OpenJDK 17.0.19 与 aria2；未执行 `apt autoremove` 或删除其他系统包。
- 从官方地址下载并校验 Flutter 3.27.0 archive（MD5 `eb98aed421434e23be8869e66ea9db70`）与 Android command-line tools 12.0（ZIP integrity 通过）。
- Flutter 安装到 `/home/kevinlasnh/development/flutter-3.27.0`，Android SDK 根为 `/home/kevinlasnh/Android/Sdk`；已关闭 Flutter analytics 并接受 Android SDK licenses。
- 正在安装 API 35 platform/build-tools、platform-tools 与项目锁定的 NDK `27.0.12077973`。
- Android toolchain 最终由 `flutter doctor -v` 确认为 API 35、Build Tools 35.0.0、JDK 17、licenses 全部可用；Android Studio 与 Linux desktop clang/GTK 警告不影响 APK 构建。
- `flutter analyze --no-fatal-infos --no-fatal-warnings`：退出码 0，仅 4 条既有 `withOpacity` info。
- `flutter test`：24 tests passed。
- `flutter build apk --debug`：成功，版本名 2.9.10、versionCode 11，APK 签名验证通过。
- `flutter build apk --release -Pvoicing.allowDebugReleaseSigning=true`：本地测试 release 构建成功，31.7 MB；ZIP 完整性、版本 2.9.10/11 与 v1/v2 签名验证通过。该 APK 使用明确允许的 Android Debug 证书，仅用于本地编译验证；正式 GitHub Release 仍由 CI Secrets 签名。
- Flutter 构建曾自动把已跟踪 `android/gradlew` mode 改为 executable；已恢复原始 0644，未夹带该无关改动。

### 最终自动化与 Linux 产物复核
- **状态：** complete（真实终端/普通输入框粘贴仍待用户配合）
- 最终源码重新验证：
  - `pc.tests.test_platform_keyboard`：60 tests OK。
  - 完整 PC suite：122 tests OK。
  - PC `py_compile`：通过。
  - `git diff --check`：通过。
- 在最终源码上重新运行 PyInstaller；最终 `Voicing` 与 `voicing-linux-x86_64` SHA-256 均为 `b15426135a60593587a8cb01309bfc2a6dfcda0ae5ff2aa2613e63c9d6c3be98`。
- 最终 DEB SHA-256 为 `92882486ad4dde80f22bf1b3f371bbb124c0359b3f348e7d4dbd346a310e927d`；包内二进制与 standalone 逐字节一致，版本/架构/依赖、`root/root` ownership 和 mode 均通过。
- `apt-get -s install` 确认本机可从已安装 2.9.9 升级到本地 2.9.10，所有新增运行依赖已满足；没有实际安装本地包。
- 最终 frozen smoke 在 offscreen/当前 Wayland 会话成功到达启动、网络枚举与 AT-SPI prewarm；prewarm 返回 ACTIVE Chrome，未创建 Portal。端口 9527 与系统托盘错误来自已运行的 2.9.9 和 offscreen 环境，是本次受控 smoke 的预期限制；timeout 后无最终 binary 残留进程。
- 普通窗口最终 20 轮压力采样：20/20 decision=normal，每轮 5—6 个可靠样本，全部为 Google Chrome `source=active_window`，0 terminal、0 uncertain。
- Release workflow YAML 解析通过，v2.9.10 changelog 提取模拟通过；版本点、UTF-8/LF、Agent Markdown 同步/ignore 与无旧公开语义扫描均通过。

## 会话：2026-07-28 CST — 全仓逐文件审查与 Agent Markdown 初始化

### 阶段 32：启动与上下文恢复
- **状态：** in_progress
- 已归一化当前工作目录为 `/home/kevinlasnh/Projects/Voicing`，未命中 Second Brain Path Guard。
- 已完整读取 `planning-with-files-zh` skill，并运行 session catchup；恢复脚本未报告未同步上下文。
- 已确认仓库根目录、PWF 三件套均存在，当前分支为 `main`，与 `origin/main` 同步，工作区启动时干净。
- 已确认当前根目录缺少 `AGENTS.md` 与 `CLAUDE.md`，尽管历史 PWF 曾记录过两份本地忽略文件；本次将依据当前仓库重新初始化。
- 下一步：排除 `.git/` 内部数据库后建立完整文件清单，逐文件检查并记录结论。

### 阶段 32：顶层文件与发布配置检查
- **状态：** in_progress
- 已建立完整清单：工作树 86 个文件、约 2.21 MB，启动时全部已跟踪。
- 已完整阅读 `.claude/` 的本机权限与热重启 Skill、`.github/workflows/release.yml`、根 `.gitignore`、中英文根 README、Android README、CONTRIBUTING 和 LICENSE。
- 已记录版本、架构、测试/发布命令、文档同步规则、仓库 Skill 历史例外与 `.gitignore` 约束。
- 下一步：检查 CHANGELOG、Android 工程全部配置/源码/测试、PC 全部源码/测试、协议和二进制资源元数据。

- 已逐行检查 CHANGELOG 1—660 行，确认 2.5.0—2.9.9 的架构、协议、平台、Release 与 Linux Wayland 演进；剩余历史版本继续核对。
- 已完成 CHANGELOG 余下历史版本检查，并完整阅读 Android 工程的 Flutter/Gradle/Manifest/XML/依赖锁/启动脚本等配置文件。
- 已完整阅读 Android 日志/主题/恢复策略/保存设备/协议/WebSocket 抽象，以及 `main.dart` 前 900 行 UI、菜单、输入框与扫码锁定逻辑。
- 已读完 `main.dart` 余下扫码校验、角点映射、动画 painter；已阅读 controller 前 400 行扫码 probe、替换确认和候选 IP 保存流程。
- 已读完 `voicing_connection_controller.dart`：保存地址候选轮询、generation 隔离、前台恢复、心跳、shadow/commit、ACK 清空、Auto Enter 与清理逻辑均已核对。
- 已完整阅读 Kotlin `MainActivity.kt` 和全部 Android 测试，核对 native WiFi 选路、OkHttp/EventChannel 生命周期、IME inset 以及当前测试覆盖/缺口。
- 已完整阅读 PC spec、依赖、设备身份、网络兼容、自启、单实例、平台工具、协议，以及 `platform_keyboard.py` 前 360 行输入/剪贴板/portal 初始化入口。
- 已读完 `platform_keyboard.py`：portal request/session、D-Bus uint、键序列、Auto 投票、AT-SPI in-process/system helper 和 Windows SendInput 均已核对。
- 已阅读 `voice_coding.py` 前 860 行，完成全局状态、日志、跨平台网络枚举/过滤/排序、QR 实际绑定 IP 优先与 WebSocket text/commit ACK 入口核对。
- 已继续阅读 `voice_coding.py` 861—1720 行，核对 ping/sync 广播、listener 动态重绑、自定义托盘菜单定位、粘贴模式切换与 QR dialog payload/动画前半。
- 已读完 `voice_coding.py` 和共享协议契约，完成 Linux 原生菜单、图标缓存、QR 成功态、主入口/单实例以及协议字段同步规则核对。
- 已阅读 PC 测试第一组：身份、自启、网络恢复、server ACK、三平台接口解析和 platform utils/portal/frozen 环境覆盖。
- 已完整阅读 576 行 `test_platform_keyboard.py`，确认 clipboard/PRIMARY、portal uint、键序列、AT-SPI 投票/cache/fallback 与 Windows Enter 的回归覆盖。
- 已读完 PC protocol/tray 测试，并完成全部 14 个二进制资源的类型、尺寸、摘要及 Gradle wrapper archive/manifest 检查。
- 已补读 `progress.md` 历史第 261—650 行，核对 Wayland、托盘、QR、Android 发送、Release 修复的实际演进与当前实现一致。
- 已补读 `progress.md` 余下历史与 `findings.md` 全文；PWF 历史上下文恢复完成。
- 已检查全部文本编码/换行、Git mode、软链接、敏感凭据标记与 ignore 规则：72 个文本均为有效 UTF-8/LF，14 个二进制已核验；未发现私钥或签名文件。

### 阶段 32：仓库级 Agent Markdown 初始化与验证
- **状态：** complete
- 已在仓库根创建本地 `AGENTS.md` 与 `CLAUDE.md`，两份文件均为 123 行、10885 字节，H1 均为 `# Repository Agent Markdown`。
- 两份配置基于本次逐文件审查整理了项目定位、目录职责、QR/WebSocket/ACK 数据流、Android 与 PC 分层、GNOME Wayland/托盘边界、按改动范围验证矩阵、Release、PWF/Git/凭据规则及已知风险。
- 已显式记录 `.claude/settings.local.json` 与 `.claude/skills/pc-hot-restart/` 为历史跟踪例外；未来仓库 Skill 需要 `.agents/skills/` 与 `.claude/skills/` 两份实体副本同步，且禁止写入凭据。
- `.gitignore` 已正确忽略根 `CLAUDE.md` / `AGENTS.md`、`.brv/`、`.workflows/` 和 `.tmp/`，PWF 三件套仍保持跟踪，因此本次无需修改 `.gitignore`，也不会 force-add 两份本地 Agent 文档。
- 配置验证结果：
  - `cmp -s AGENTS.md CLAUDE.md`：通过，两份 SHA-256 均为 `bca0747cd9d42114573e179f80e89ffd09cdfd9e2b24c09c571e8dd39e0ac8f6`。
  - H1 检查：两份均为 `# Repository Agent Markdown`。
  - `git check-ignore -v AGENTS.md CLAUDE.md`：通过，分别命中根 `.gitignore` 第 108、107 行。
  - `file -bi`、CR 扫描和末尾字节检查：两份均为 UTF-8、无 CR、以 LF 结尾。
  - `git diff --check`：通过。
- 本次没有修改 PC、Android、协议或 Release 业务文件，按仓库验证矩阵不运行无关的 PC/Flutter 全套测试；提交范围仅为 PWF 三件套，两份 Agent Markdown 保持本地忽略。
- 已准备提交阶段 32 的 PWF 记录并推送 `main`；推送后将核验本地 HEAD、远端 `origin/main` 与最终工作区状态。

## 会话：2026-07-21 CST — GNOME Wayland 冷启动 terminal 粘贴误判重型调研

### Heavy Research 启动
- **状态：** in_progress
- 用户报告：开机后若未先在 terminal 手动触发一次 Ctrl+Shift+V，手机首次发送文本会走 Ctrl+V，且后续发送持续走 Ctrl+V。
- 已按 heavy-research 流程完成阶段 A 范围确认，限定为当前仓库的 GNOME Wayland PC 输入链路；本轮先调研并形成 deployment plan，不直接修改业务代码。
- 已创建会话目录 `.workflows/2026-07-21-175636/`，准备并行调查联网、源码和长期记忆三个维度。

### Heavy Research 三维取证与校验
- **状态：** complete，等待阶段 C 用户确认
- 并行完成 `web.md`、`source.md`、`memory.md`；三份报告的 `run_id` 均为 `2026-07-21-175636`。
- 联网报告首轮因一处代码参数使用省略号而触发格式校验失败，按流程自动重跑一次后通过。
- 三份报告均覆盖 12/12 叶节点，子问题优先级、三个必需小节、置信度、元数据和占位符检查全部通过。
- 已综合出首选方向：先补无文本内容的结构化诊断，随后采用 tri-state readiness gate、有界重采样和 portal 建会话前后成对采样；保留显式粘贴模式作为降级，不双发快捷键。
- 当前关键缺口：尚无现场日志证明失败时程序实际选择的是 Ctrl+V，还是选择 Ctrl+Shift+V 后 Shift 在 portal/terminal 侧未生效；必须在 deployment plan 中作为先诊断再修复的门槛。

### Deployment plan 生成与阶段收尾
- **状态：** complete
- 用户已明确接受 P0/P1 关键缺口，并授权生成 deployment plan、记录进度和 push。
- 已按 Heavy Research 阶段 D 模板生成 `.workflows/2026-07-21-175636/deployment-plan.md`。
- 计划采用诊断优先的分支部署：先记录 raw AT-SPI samples、helper 状态、最终 sequence 和 portal press/release；再根据证据只进入 classifier、portal chord 或 clipboard 中的一个修复分支。
- 计划明确禁止 unknown 全局默认为 terminal、禁止 Ctrl+V 与 Ctrl+Shift+V 双发；unresolved 超时改为保留 Android 文本并使用显式粘贴模式降级。
- 计划包含 13 个执行分支、逐步回滚、权限/数据/依赖风险，以及 10 次干净 GNOME 登录的实机验收门槛。
- 模板校验通过：无尖括号或省略号占位；所有可逆性和风险等级字段合法；`git diff --check` 待提交前统一执行。

## 会话：2026-07-28 CST — Ubuntu 22.04 GNOME Wayland 终端识别稳定性修复与 v2.9.10 发布

### 阶段 33：启动与证据恢复
- **状态：** in_progress
- 用户要求全面修复终端/非终端自动识别不稳定、terminal 中误发 Ctrl+V 并粘贴图片的问题；必须反复修复和测试，最终记录进度、推送并触发新的 GitHub Actions Release，全部资产成功后才能完成目标。
- 已归一化仓库路径为 `/home/kevinlasnh/Projects/Voicing`，未命中 Second Brain Path Guard；已完整读取仓库 Agent Markdown 与 `planning-with-files-zh` skill，并运行 session catchup，未报告未同步上下文。
- 启动时 `main` 与 `origin/main` 同步，已跟踪工作区干净；仅根 `AGENTS.md` / `CLAUDE.md` 作为忽略的本地配置存在。
- 已恢复阶段 31 的诊断优先结论：不能把 unknown 粗暴映射成 terminal、不能双发快捷键；应先区分 classifier、portal modifier 与 clipboard 根因，并在 unresolved 时保留 Android 文本。
- 已建立六步执行计划：实证基线 → 全链路审查 → 修复与测试 → Ubuntu Wayland 重复验证 → 版本/文档/推送/tag → Actions/Release 资产核验。
- 已确认当前实机环境为 Ubuntu 22.04 + GNOME Shell 42.9 + Wayland，系统 AT-SPI 依赖可导入；已安装应用仍为 v2.9.9。
- 已检查当日 Voicing 日志：当前版本完全缺少焦点样本、helper 状态、AUTO 决策和 portal 键事件诊断，无法从历史日志裁决现场故障分支。
- 已确认本机未安装 `wl-clipboard`、`xclip` 或 `xsel`；后续将把 clipboard backend 与文本写入成功纳入验证，避免旧图片剪贴板干扰判断。
- 已完整阅读 `platform_keyboard.py` 的剪贴板、portal、AUTO 投票、AT-SPI 主进程/system helper 与键序列实现，确认至少五个需要修复的边界：无 unresolved 状态、全 None 不 fallback、DFS stale focused 风险、首次 portal 前后证据丢失、键序列异常不补偿释放。
- 已完整阅读 576 行 `test_platform_keyboard.py` 与 Linux release/deb 配置，确认现有测试固化了 unresolved→Ctrl+V 和普通 focused 不查 ACTIVE 的旧行为，且 deb 未声明 AT-SPI 与 `wl-clipboard` 运行依赖。
- 已在当前真实 AT-SPI desktop tree 中复现跨应用 stale FOCUSED：钉钉仍标记 focused，而另一个窗口才标记 active；现有扫描器选择了钉钉并判 NORMAL。根因已从“可能”提升为实机确认。

### 阶段 33：第一轮实现
- **状态：** in_progress
- 已在 `pc/platform_keyboard.py` 实现 ACTIVE-window-first 扫描骨架：过滤 GNOME Shell/portal，按非 shell ACTIVE 应用选定目标，只在该 ACTIVE 子树内使用 focused 控件；跨应用多 ACTIVE 或无可靠 ACTIVE 时返回带原因的 unresolved。
- 已引入内部 terminal/normal/unresolved 三态与最小可靠票数/票差门槛，取消全 uncertain 自动退化为 Ctrl+V；超时 unresolved 会抛出输入失败，沿现有 ACK 语义保留手机文本。
- 已为首次 portal session 增加授权前/授权后两阶段识别与冲突 reconciliation；可靠 pre + post unresolved 可保留 pre，可靠结果冲突则安全取消。
- 已增加不含用户正文的 attempt 级日志：clipboard backend/文本长度、焦点样本 app/role/source/reason、投票、最终模式和 portal sequence。
- 已为 portal 部分键序列失败增加已按下按键的 best-effort 释放，并在失败时清 session。
- 已将 Wayland clipboard 改为要求 `wl-clipboard`，复制后回读校验；旧 clipboard 文本读取失败时不再错误恢复为空字符串，默认恢复等待提升到 350ms。
- `python3 -m py_compile pc/platform_keyboard.py` 已通过。
- 第一轮实机只读采样验证：修复后连续 5 个样本全部稳定选择真实 ACTIVE 的 Google Chrome frame，未再混入此前 stale 的钉钉 focused；投票为 normal 5、terminal 0、uncertain 0。
- 第一轮运行 `python3 -m unittest pc/tests/test_platform_keyboard.py` 时，45 项均因旧测试 `setUp()` 调用已移除的 terminal cache API 而失败；这是测试契约尚未迁移，不是运行代码导入失败。已记录并进入测试重写阶段，不重复运行同一旧测试。
- 已把 `test_platform_keyboard.py` 扩展到 52 项，覆盖 ACTIVE-first/stale-focused、三态置信门槛、稀疏/冲突/unresolved、重采样、portal 前后 reconciliation、unresolved 禁止发键、modifier 补偿释放、system helper fallback、clipboard 回读与缺少 wl-clipboard 的安全失败。
- 测试迁移后的首轮仅剩 1 项失败：只有 `role=terminal` 而 app 为空的有效样本被过早归为 uncertain；已把分类顺序改为“显式 unresolved reason → terminal role/app → shell/空 app uncertain”。
- 第二轮 `python3 -m unittest pc/tests/test_platform_keyboard.py`：52 tests OK。错误日志中的 portal failure traceback 来自刻意注入的补偿释放测试，测试本身通过。
- 首轮扩大到完整 PC suite 时共运行 88 项，键盘等已执行测试通过，但 4 个 test module 因系统 Python 缺少 `qrcode` 导入失败；这是依赖环境不足，已记录，下一步创建本地 `.venv` 安装锁定依赖后重跑。
- 首次 `python3 -m venv .venv` 因 Ubuntu 未安装 `python3.10-venv` / ensurepip 失败；命令留下的仅是忽略目录内局部 venv 骨架，计划安装系统包后用 `python3 -m venv --clear .venv` 安全重建。
- 已通过 `sudo -n apt-get` 安装 `python3.10-venv` 与 `wl-clipboard`，随后用 `python3 -m venv --clear .venv` 重建隔离环境并成功安装 `pc/requirements.txt` 全部锁定依赖。
- 使用 `.venv` 重跑完整 PC suite：112 tests OK；覆盖 ACK、网络、协议、托盘、平台层及新增 52 项键盘测试。输出中的 portal traceback 与 offscreen Qt warning 均来自预期测试分支，无失败。
- 已在与 PyInstaller 相同的“venv 无 gi → `/usr/bin/python3` helper”路径实机验证：in-process 样本为空，system helper 连续返回 5 个真实 ACTIVE 的 Google Chrome frame，最终稳定判 NORMAL。
- `wl-paste --list-types` 确认当前真实 Wayland clipboard 提供 UTF-8/text MIME，可在不暴露正文的前提下进行写入、回读和恢复验证。
- 已在进程内保存原文本剪贴板，使用随机 token 执行真实 `wl-copy` → `wl-paste` 相等校验，再恢复原文本并复核相等；`wl_clipboard_roundtrip=ok`。
- 对普通窗口 helper 路径执行 20 轮连续实机压力采样：20/20 决策为 normal，共 116 个样本全部来自真实 `active_window` 的 Google Chrome，0 个 unresolved reason，未再出现 stale 钉钉或 GNOME Shell 混入。
- 首次尝试通过 `gnome-terminal` 启动 45 秒临时窗口进行 terminal 压力采样，但 GNOME 的 focus-stealing prevention 没有把前台焦点从 Chrome 转给新窗口，因此 20/20 仍正确判为 Chrome normal；该轮不能作为 terminal 验收证据，已停止复用同一方法。
- 已确认临时 GNOME Terminal 的 AT-SPI frame 可见且 app 名为 `gnome-terminal-server`，但其 ACTIVE 状态会随桌面焦点时序变化；下一步改用 AT-SPI component focus 或用户真实点击建立可证明的终端前台状态。
- 继续尝试 AT-SPI frame `grab_focus()` 返回 false；查询 frame action 接口出现 AT-SPI Get 错误，深层遍历 terminal child 的 focus 尝试又超时。已按三次失败协议停止重复自动抢焦点方案，保留后续由用户真实点击终端后执行采样/粘贴验收的门槛。
- 第二轮代码审查进一步收紧多 ACTIVE 处理：优先 dialog/alert，其次 frame、window；同优先级出现多个真实窗口时返回 unresolved，不按同 app 名盲选。system helper 同步相同逻辑。
- system helper 不再复制 terminal 名单，helper 只返回 ACTIVE-first 证据，由主进程统一分类，减少双份名单漂移风险。
- 新增日志隐私测试，确认 app/role/source 可诊断但窗口标题不进入日志；新增 active window 内 terminal 控件识别测试。
- 第二轮完整 PC suite：115 tests OK。

### 阶段 33：终端实机验收续接检查点
- **状态：** in_progress
- 续接后再次执行当前前台只读探测，6/6 个可靠样本均来自 `Google Chrome/frame/active_window`，决策为 normal。
- 为避免误发，使用“20 轮全部判 terminal 才允许粘贴”的硬门槛进行定时验收；实际 20/20 轮仍为 Chrome normal，因此脚本按设计以 `FAILED_NO_KEYS_SENT` 退出，未改写剪贴板、未创建 Portal 会话、未发送任何按键。
- 随后启动基于 `/tmp/voicing-terminal-ready-v2910-7f3c` 的用户终端握手，等待约 90 秒未收到标记；已主动中断后台等待进程，没有遗留输入动作。
- 当前唯一未完成门槛仍是真实 terminal 前台采样与实际 Ctrl+Shift+V 粘贴验收；下一步由用户在空白终端执行就绪 `touch` 命令后再继续，不重复自动抢焦点路线。
- 在新的 15 分钟后台双场景验收器等待期间，基于当前工作树重跑完整 PC suite：122 tests OK；随后 `py_compile` 与 `git diff --check` 同样通过。
- 已再次逐段审阅 `pc/platform_keyboard.py` 的完整 diff，确认 pre/post Portal reconciliation、unresolved 零按键、ACTIVE-first/system helper 同步、clipboard 回读与恢复、modifier 逆序补偿和隐私日志之间没有发现新的发布阻断。
- 发布物一致性审计发现根中英文 README 仍写旧的约 21 MB APK 体积，而本地 v2.9.10 release APK 为 31.7 MB；已同步修正为约 32 MB，并全仓搜索确认其余 `2.9.9` 命中均为 PWF/CHANGELOG 历史记录。
- 后台双场景验收器连续跨三个目标回合都未收到用户在真实终端创建的 sentinel；为避免其稍后意外触发输入，已主动发送中断并确认进程以 130 退出，期间未创建 Portal 会话、未改写剪贴板、未发送按键。
- 当前所有可自动完成的代码审查、122 项 PC 测试、Android 测试/构建、Linux 构建、版本/文档/工作流与发布物审计均已完成；唯一剩余前置条件是用户参与的真实 Wayland terminal/normal 双场景验收。按目标三次阻塞协议，本轮在此标记 blocked，不提交、不 push、不打 tag。

### 阶段 33：Ghostty `Unnamed/frame` 实机根因与第三轮修复
- **状态：** in_progress
- 用户恢复目标并在真实终端触发新握手后，20/20 轮样本都稳定为 `Unnamed/frame/active_window`，决策均为 normal；全通过门槛正确输出 `FAILED_NO_KEYS_SENT`，没有创建 Portal 会话、写剪贴板或发送按键。
- 在用户停止操作后对同一 ACTIVE frame 进行只读身份诊断：AT-SPI PID 对应的 `/proc` `exe`、`comm`、`cmd0` basename 均为 `ghostty`，toolkit 为 GTK 4.14.5；子树仅 13 个节点（1 个 frame、12 个 panel），没有 FOCUSED、EDITABLE 或 terminal 角色。
- 根因由“焦点不稳定”进一步收敛为 Ghostty 的可访问性身份缺失：其 AT-SPI app name 为 `Unnamed` 且没有可用于分类的 terminal role。下一步新增只读取可执行文件 basename 的 `process_name` 身份信号，并同步主进程与 system-Python helper、补测试后重跑实机压力验收。
- 已实现 `process_name` 第三身份：主进程和 system helper 都从 AT-SPI PID 仅解析 `/proc` 可执行 basename；统一分类器同时检查 app/process，`Unnamed` 且无 process 时改为 uncertain，避免再次默认 Ctrl+V；日志只新增安全 basename，不记录 PID、参数、标题或正文。
- 新增 7 条回归，覆盖 helper 字段归一化、PID 到 basename、application PID fallback、`Unnamed+ghostty` terminal、无进程身份 unresolved、明确普通进程 normal 与日志隐私；键盘专项现为 67 tests OK。
- 当前真实 Ghostty ACTIVE 现场中，in-process 与 venv→system helper 两条路径均返回 `Unnamed/process=ghostty/frame/active_window`；最终连续 20/20 轮全部判 terminal，每轮 5–6 个 terminal 票、0 normal、0 uncertain。
- 完整 PC suite 已提升为 129 tests OK；`py_compile` 与 `git diff --check` 同时通过。
- 使用持久 `QCoreApplication` 模拟真实产品生命周期后，普通 Chrome 空文本 Portal 验收成功：pre/post 均 5 个 normal 票，最终 `portal_sequence=ctrl_v`，Ctrl/V 4 个事件全部成对完成，剪贴板恢复 MATCH。
- 通过 Ghostty 标准 D-Bus application `Activate` 聚焦现有窗口后，终端空文本 Portal 验收成功：pre 4 个、post 5 个 terminal 票，最终 `portal_sequence=ctrl_shift_v`，Ctrl/Shift/V 6 个事件完整按下/释放，剪贴板恢复 MATCH。
- 已启动专用 Ghostty proof 窗口并确认 ACTIVE 判 terminal；第二个独立非空 Portal 会话在 `Start` 授权处超时，未发送任何键，proof 未生成。该失败是重复新建授权会话的验收编排问题，不推翻前一会话已取得的真实 terminal 键序列证据。
- 为无人值守授权临时安装 Ubuntu 官方 ydotool，并在每次发送前确认 Portal modal 期间没有非 Shell ACTIVE 窗口；500ms Enter、2s Enter、`Space→Tab→Enter` 三种方式均未使 GNOME 42 chooser 返回，已按三次失败协议停止。ydotool 已卸载，专用 Ghostty 窗口和精确 `/tmp` 标记已清理，未执行 autoremove，未留下 core/proof。
- 已停止本机运行中的 Voicing 2.9.9 scope 并重启用户级 portal 服务，清除其唯一陈旧 session，同时释放 9527；该旧版后续不自动重启，避免干扰最终 frozen smoke。
- process identity 修复后的 PyInstaller binary 已重建；首轮新 DEB 检查发现当前 umask 令目录 mode 为 0775。workflow 现新增对 package root 全部目录显式 `chmod 0755`，不再依赖 runner umask，进入重新打包。

### 阶段 33：最终本地发布验收
- **状态：** complete（等待提交、tag 与 GitHub Actions）
- 已确认验收现场无 Voicing/frozen harness 残留进程、无 9527 监听、无可见 Portal session；旧版 2.9.9 未重新启动。
- 已将根中英文 README 与 `CHANGELOG.md` 补充为最终行为：Ghostty 的通用 `Unnamed` AT-SPI frame 使用当前 accessible 进程的可执行文件 basename 识别，分类与日志不读取窗口标题或剪贴板正文；DEB 权限明确为目录/可执行文件 0755、元数据/图标 0644。
- 已同步本地忽略的 `AGENTS.md` / `CLAUDE.md`，锁定 `process_name` 隐私边界、主进程/helper 同步规则与 DEB mode 约束；两份 SHA-256 均为 `354f279cfebcf9a5dea47090a8b4688b6403a7da19372d3413354cff14166c7d`，内容完全一致。
- 最终 Linux standalone `pc/dist/Voicing` 与 `pc/dist/voicing-linux-x86_64` 完全一致，SHA-256 均为 `e687dc9d8bc27b964c88132d13395706a3773bbf27fae8635e032422644c1382`。
- 最终 `pc/dist/voicing-linux-amd64.deb` SHA-256 为 `0a9169e479f3f1c63f4b6ae4a6756b144441cbc15b590845a50da5dada1f7573`；版本 2.9.10、amd64，Depends 包含 AT-SPI/Python GI/`wl-clipboard`，包内 owner 全为 root/root，目录与二进制 0755、desktop/icon 0644。
- 最终发布前验证重新执行：完整 PC suite 129 tests OK；PC `py_compile` 通过；Flutter analyze 0 问题；Flutter test 24 tests passed；Release workflow YAML 成功解析出 6 个 jobs；`git diff --check` 通过。
- 本轮实机门槛已判定完成：普通 Chrome 20/20 为 normal，真实 Ghostty 修复后 20/20 为 terminal；两侧真实 Portal 分别发送完整 `ctrl_v` 4 事件与 `ctrl_shift_v` 6 事件，所有 modifier 释放且 clipboard restore 均 MATCH。无人值守非空 proof 因 GNOME 42 授权 chooser 无法安全自动确认而停止，不再重复该失败路线。
