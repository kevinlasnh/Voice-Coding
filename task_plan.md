# 任务计划：全面梳理当前仓库用途

## 目标
系统检查当前仓库的结构、入口、依赖、运行方式和主要功能，向用户说明这个项目是在做什么。

## 当前阶段
阶段 33（complete）

## 各阶段

### 阶段 1：仓库元信息与长期记忆
- [x] 确认仓库根目录和 PWF 状态
- [x] 查询 ByteRover 长期记忆中的相关背景
- [x] 记录初始发现
- **状态：** complete

### 阶段 2：目录结构与依赖梳理
- [x] 梳理顶层目录、README、依赖文件和协议文件
- [x] 识别主要语言、平台和运行入口
- [x] 记录结构性发现
- **状态：** complete

### 阶段 3：核心代码阅读
- [x] 阅读 PC 端主入口与关键模块
- [x] 阅读 Android 端主要代码与配置
- [x] 阅读协议契约和测试
- **状态：** complete

### 阶段 4：验证与风险检查
- [x] 检查测试、构建脚本和可运行性
- [x] 查看 git 状态，区分本次新增 PWF 文件和已有改动
- [x] 汇总潜在风险和后续建议
- **状态：** complete

### 阶段 5：交付总结
- [x] 用中文概括仓库用途、架构、运行方式和当前状态
- [x] 同步 progress.md 与 findings.md
- **状态：** complete

### 阶段 6：初始化仓库级 Agent 配置
- [x] 新增 `CLAUDE.md`
- [x] 新增 `AGENTS.md`
- [x] 校验两份文件除 H1 外正文一致
- [x] 记录 `.gitignore` 当前忽略状态
- **状态：** complete

### 阶段 7：Ubuntu/Linux 可用性 Review
- [x] 阅读 Linux 相关代码、README 和 CI 构建脚本
- [x] 检查当前 Ubuntu 会话、系统依赖和 Python 依赖
- [x] 运行可在当前环境执行的 Linux 相关测试
- [x] 汇总当前系统能否使用 Voicing 的结论和阻断项
- **状态：** complete

### 阶段 8：下次继续 Ubuntu 实机可用性修复
- [ ] 切换到 `Ubuntu on Xorg` 会话后重新检查 `XDG_SESSION_TYPE`
- [x] 补齐系统依赖：至少 `libxcb-cursor0`，建议同时安装 `xclip` 或 `xsel`
- [x] 建立可用 Python 运行环境并安装 `pc/requirements.txt`
- [x] 在当前 GNOME Wayland 会话下启动 `.venv/bin/python pc/voice_coding.py --dev`
- [ ] 用 Android 端扫码配对并验证文本能进入当前光标
- **状态：** in_progress

### 阶段 9：GNOME Wayland 同等 Windows 体验改造方案
- [x] 确认当前 Ubuntu/GNOME/Wayland 代码阻断点
- [x] 检索并验证 RemoteDesktop portal、libei、ydotool、wtype 等输入方案
- [x] 对比候选方案能否达到 Windows 同等自动输入/自动回车效果
- [x] 形成推荐代码改造范围和验证计划
- [x] 用户确认采用稳定推荐路径后实现 RemoteDesktop portal 后端
- [x] 更新 PC 端测试、README 和 CHANGELOG
- [x] 完成本机 PC/Android 前置验证
- **状态：** complete

### 阶段 10：Android 实机扫码与端到端输入验证
- [x] 启动 PC 端并保持 WebSocket 服务运行
- [x] Android 端扫码或用已保存设备连接当前 PC
- [x] 验证普通文本进入当前光标（portal uint 修复后通）
- [ ] 验证中文文本、Auto Enter 和空 commit 回车（Auto Enter 路径已触发 `press_enter`；portal 修复后未逐项复核）
- [ ] 验证剪贴板恢复（未单独复核）
- **状态：** in_progress（核心端到端已通，细粒度项待复核）

### 阶段 11：Linux 托盘前端交互修复 + portal D-Bus 修复 + 永久授权调研
- [x] 细颗粒度审查 `pc/voice_coding.py` 托盘链路，定位 Linux 双菜单/抖动/黑闪等问题
- [x] Linux 改用系统原生 `QMenu`（右键交给 `setContextMenu`/宿主，左键/双击 popup），杜绝双菜单
- [x] `update_icon` 去重，消除 Linux 每 200ms 图标抖动
- [x] Wayland 启动预热改为不 `show()`，消除黑闪
- [x] 修复 portal `SelectDevices.types` 与 `NotifyKeyboardKeysym.state` 的 D-Bus uint32 序列化（`'u'` vs `'i'`）
- [x] 调研 GNOME portal 永久授权 → 不可行（GNOME #175），决策保持 portal、接受每次启动一次点击
- **状态：** complete

### 阶段 12：自定义菜单美化 + 原生菜单分隔条 + QR 闪烁迭代
- [x] 自定义 Fluent 菜单（Win/macOS）宽度收紧到 sizeHint（随最长文字自适应）+ 去分隔条（本机 Linux 走原生菜单，无法肉眼确认，待 Windows 实机复核）
- [x] Linux 原生菜单去分隔条（`_setup_native_context_menu` 删 4 个 `addSeparator()`）—— 用户确认无横条 ✅
- [x] QR「下方第二个 QR」闪烁修复（收尾先 hide 解除 surface 映射再 resize/show）—— 用户确认下方闪动消失 ✅
- [ ] Linux 原生菜单宽度仍不自适应（用户反馈，待复核具体表现）
- [x] QR 到达中心时自身闪动一次：用户选择砍掉飞入，已改为中心直接出现/直接关闭，待用户手动启动肉眼确认
- **状态：** in_progress

### 阶段 13：整体前端逻辑 Review
- [x] 审查 PC PyQt 托盘、菜单、QR 和 WebSocket 前端信号链路
- [x] 审查 Android Flutter UI、QR 扫码、连接 controller、native WebSocket 包装和 shadow/commit 发送路径
- [x] 运行 PC 单元测试、Flutter test 和 Flutter analyze
- [x] 汇总可复现/高概率逻辑风险
- **状态：** complete

### 阶段 14：整体前端 Review 问题修复
- [x] 修复 Android native WebSocket 发送失败不可被 controller 捕获的问题
- [x] 修复 PC 同步开关即时广播跨 asyncio event loop 的风险
- [x] 修复 Android QR 替换设备确认先成功后确认的时序问题
- [x] 保持用户要求：不执行 APK 或 deb 编译
- [x] 运行 PC/Android 非打包验证
- [x] 提交并推送到远端
- **状态：** complete

### 阶段 15：Linux Terminal 输入失效调查
- [x] 检查 PC Linux 输入后端的剪贴板与快捷键路径
- [x] 联网检索 GNOME Terminal 粘贴快捷键、RemoteDesktop portal 和 GNOME Shell introspection 限制
- [x] 在本机探测 GNOME Terminal gsettings、GNOME Shell Introspect、AT-SPI 和 wl-clipboard primary selection
- [x] 形成修复方案
- **状态：** complete

### 阶段 16：GNOME Wayland Terminal 粘贴模式实现
- [x] 在 PC 平台输入层新增 Auto/普通/终端/兼容粘贴模式
- [x] Auto 模式通过 AT-SPI 检测 terminal 焦点，命中后发送 Ctrl+Shift+V，否则发送 Ctrl+V
- [x] 托盘菜单新增粘贴模式切换项，作为 Auto 检测失败时的手动兜底
- [x] Wayland 下同时写入 CLIPBOARD 和 PRIMARY，并尽量恢复 PRIMARY
- [x] 更新 README / README.zh-CN / CHANGELOG
- [x] 补充 PC 单元测试并完成验证
- [x] 用户手动启动实测：普通输入框和 terminal 均可自动输入
- **状态：** complete（已实测通过）

### 阶段 17：最新 PC / Android 代码全面逻辑复查
- [x] 复查 PC 端 WebSocket、托盘/QR、同步状态和平台输入逻辑
- [x] 复查 Android 端连接状态机、扫码、WebSocket 发送和文本提交逻辑
- [x] 运行当前环境可用的 PC/Android 验证命令
- [x] 汇总确定 bug、残余风险和测试缺口
- **状态：** complete

### 阶段 18：v2.9.5 GitHub Actions 发布构建修复与重触发
- [x] 推送 `v2.9.5` tag 触发 release workflow
- [x] 检查 Actions 结果并定位 Linux job 失败根因
- [x] 修复 headless Linux runner 中 Qt 单元测试无法初始化的问题
- [x] 运行本地非打包验证
- [x] 提交、推送并重新触发 `v2.9.5` release workflow
- [x] 等待 Actions 完成并确认 APK / DEB / 其他产物发布结果
- **状态：** complete

### 阶段 19：v2.9.6 Linux deb Wayland 启动修复
- [x] 复现已发布 `v2.9.5` deb 在 GNOME Wayland 上误报 RemoteDesktop portal 键盘能力不可用
- [x] 卸载本机已安装的错误 `voicing 2.9.5` deb 包
- [x] 修复 PyInstaller 打包态调用系统命令时的 `LD_LIBRARY_PATH` 污染
- [x] 覆盖 `gdbus`、`wl-copy` / `wl-paste`、系统 Python AT-SPI helper 的系统命令环境
- [x] 更新版本号、README 和 CHANGELOG 到 `2.9.6`
- [x] 完成本地单元测试、Android analyze/test 和 frozen smoke test
- [x] 提交、推送并触发 `v2.9.6` release workflow
- [x] 确认新 Release 资产，尤其是 `voicing-linux-amd64.deb`
- **状态：** complete

### 阶段 20：公开文档同步 Linux 自动粘贴与自启边界
- [x] 审查 `README.md`、`README.zh-CN.md`、Android README 和 `CHANGELOG.md`
- [x] 补充 GNOME Wayland 默认自动粘贴、终端 Ctrl+Shift+V、手动粘贴模式说明
- [x] 补充 Linux GNOME autostart `.desktop` 与 Wayland RemoteDesktop 授权边界
- [x] 同步 Android 端使用文档中用户需要知道的 Linux 桌面端行为
- [x] 运行文档 diff 和 `git diff --check`
- **状态：** complete

### 阶段 21：GNOME Wayland Auto 粘贴稳定性修复
- [x] 复查 PC 端 Linux Auto 粘贴与 AT-SPI terminal 检测路径
- [x] 本机复现 AT-SPI 查询偶发 `None` 导致 Auto 退回普通 `Ctrl+V`
- [x] 将 Auto 模式改为稳定优先：重试焦点检测、缓存近期 terminal、无法可靠确认焦点时走终端安全 `Ctrl+Shift+V`
- [x] 扩展 terminal app 名称识别并同步系统 Python AT-SPI helper
- [x] 更新 README / Android README / CHANGELOG 的 Auto 粘贴边界说明
- [x] 补充 PC 单元测试并完成验证
- **状态：** complete

### 阶段 22：v2.9.7 Release 发布
- [x] 更新 PC / Android 版本号到 `2.9.7`
- [x] 将 CHANGELOG Unreleased 内容落到 `2.9.7` 发布块
- [x] 运行 PC 和 Android 发布前验证
- [x] 提交并推送 `main`
- [x] 推送 `v2.9.7` tag 触发 GitHub Actions release workflow
- [x] 确认 Actions 成功并发布 GitHub Release 资产

### 阶段 28：GNOME Wayland Auto 粘贴采样投票稳定性修复
- [x] 调研当前 AT-SPI focused/active fallback 稳定性与 RemoteDesktop portal 能力边界
- [x] 将 Auto 粘贴从单次明确结果决策改为 500ms 窗口采样投票
- [x] 系统 Python AT-SPI helper 改为单进程内批量采样，避免每个样本重复启动 Python
- [x] 补充 PC 单元测试并更新公开文档
- [x] 运行 PC 编译、单元测试和 diff 检查
- **状态：** complete

### 阶段 29：v2.9.9 Release 发布
- [x] 更新 PC / Android 版本号到 `2.9.9`
- [x] 将 CHANGELOG Unreleased 内容落到 `2.9.9` 发布块
- [x] 运行 PC 和 Android 发布前验证
- [x] 提交并推送 `main`
- [x] 推送 `v2.9.9` tag 触发 GitHub Actions release workflow
- [x] 确认 Actions 成功并发布 GitHub Release 资产
- **状态：** complete

### 阶段 30：本机旧版卸载与 v2.9.9 安装确认
- [x] 停止旧的 `/opt/voicing/voicing` 进程
- [x] 卸载本机已安装的 `voicing 2.9.8` deb 包
- [x] 删除旧的 GNOME 用户级自启文件
- [x] 复核本机已安装 `voicing 2.9.9`
- [x] 确认 `/usr/bin/voicing`、`/opt/voicing`、运行进程和 GNOME 自启项恢复
- **状态：** complete

### 阶段 23：Auto Enter 可靠性修复
- [x] 复查 Android shadow/commit Auto Enter 发送路径
- [x] 复查 PC WebSocket commit 分支与 Wayland Enter 发送路径
- [x] 修复 PC commit 成功/失败 ACK 语义，Enter 成功才返回清空输入
- [x] 延长 PC 粘贴后 Auto Enter settle 延迟
- [x] 修复 Android forceEnter commit 后立刻清空输入的问题，改为等待 PC ACK 清空
- [x] 补充 PC 服务端单元测试并完成 PC/Android 验证
- **状态：** complete

### 阶段 24：Android 到 PC 发送核心链路最终审查
- [x] 审查 Android `sendText()`、shadow increment、commit finalize 与 ACK 处理
- [x] 审查 Dart WebSocket 抽象和 Android Kotlin native WebSocket bridge
- [x] 审查 PC WebSocket handler、输入注入、ACK 清空和 sync disabled 语义
- [x] 审查协议常量/contract 中 text、ack、send_mode、auto_enter 字段一致性
- [x] 运行 PC/Android 验证并确认无新增阻断问题
- **状态：** complete

### 阶段 25：GNOME Wayland Auto 粘贴普通窗口误判修复
- [x] 复查 PC Auto 粘贴焦点判定、AT-SPI active fallback 和测试覆盖
- [x] 修复未知焦点无近期 terminal 缓存时误走终端粘贴的问题
- [x] 将 AT-SPI fallback 从只找 active terminal 改为返回 active 窗口信息，普通窗口可明确走 Ctrl+V
- [x] 同步系统 Python AT-SPI helper 与公开文档/CHANGELOG
- [x] 补充 PC 单元测试并完成验证
- **状态：** complete

### 阶段 26：v2.9.8 Release 发布
- [x] 更新 PC / Android 版本号到 `2.9.8`
- [x] 将 CHANGELOG Unreleased 内容落到 `2.9.8` 发布块
- [x] 运行 PC 和 Android 发布前验证
- [x] 提交并推送 `main`
- [x] 推送 `v2.9.8` tag 触发 GitHub Actions release workflow
- [x] 确认 Actions 成功并发布 GitHub Release 资产
- **状态：** complete

### 阶段 27：本机 v2.9.8 deb 安装与 GNOME 自启确认
- [x] 卸载旧的 `voicing 2.9.7` deb 包
- [x] 确认用户安装的最新 GitHub deb 为 `voicing 2.9.8`
- [x] 确认 `/usr/bin/voicing` 指向 `/opt/voicing/voicing`
- [x] 确认 `~/.config/autostart/voicing.desktop` 存在且启用
- [x] 确认当前桌面为 GNOME，会匹配 autostart 的 `OnlyShowIn=GNOME`
- **状态：** complete

### 阶段 31：GNOME Wayland 冷启动 terminal 首次粘贴误判重型调研
- [x] 建立 Heavy Research 会话与统一调研提纲
- [x] 并行完成联网、源码和长期记忆三维调研
- [x] 校验调研报告并综合根因、方案与关键缺口
- [x] 用户确认调研摘要后生成 deployment plan
- **状态：** complete

### 阶段 32：全仓逐文件审查与仓库级 Agent Markdown 初始化
- [x] 建立排除 `.git/` 内部对象后的完整文件清单，并逐文件检查文本、配置、源码、资源及二进制元数据
- [x] 基于实际仓库结构与工作流编写根目录 `AGENTS.md` 和 `CLAUDE.md`，保证内容完全一致且 H1 为 `# Repository Agent Markdown`
- [x] 校正 `.gitignore`：仓库根 Agent Markdown 保持本地忽略，PWF 三件套保持 Git 跟踪
- [x] 运行配置一致性、编码、Git diff 和适当项目验证
- [x] 同步 PWF 三件套，提交本次应推送文件并推送当前分支
- **状态：** complete

### 阶段 33：Ubuntu 22.04 GNOME Wayland 终端识别稳定性修复与 v2.9.10 发布
- [x] 恢复阶段 31 调研结论，复核当前环境、运行日志和终端/非终端粘贴全链路
- [x] 为焦点采样、helper 状态、AUTO 决策和 portal 键序列补充可验证的结构化诊断
- [x] 实现 terminal / normal / unresolved 三态识别、就绪重采样和安全失败语义
- [x] 补齐分类器、冷启动稀疏样本、Portal modifier、剪贴板恢复和 ACK 回归/压力测试
- [x] 在 Ubuntu 22.04 GNOME Wayland 对 terminal 与普通窗口进行重复实机验证，失败则继续修复重测
- [x] 同步 PC/Android 版本、CHANGELOG 与中英文文档，并完成 PC/Android 发布前验证
- [x] 记录 PWF，提交并推送 `main`，创建 `v2.9.10` tag 触发 GitHub Actions
- [x] 确认 Actions 全绿并核验新 deb、apk 及其余 Release 资产
- **状态：** complete

## 关键问题
1. 这个仓库的产品目标和核心使用场景是什么？
2. PC 端、Android 端和 protocol 目录之间如何协作？
3. 当前仓库是否具备清晰的运行、构建、测试路径？

## 已做决策
| 决策 | 理由 |
|------|------|
| 使用 PWF 记录本次检查 | 任务涉及多目录、多文件和多阶段阅读，适合持久化上下文 |
| 同步新增 `CLAUDE.md` 与 `AGENTS.md` | 仓库级 agent 配置新增时两份文件必须全文一致，H1 均为 `# Repository Agent Markdown` |
| Linux 托盘改用系统原生 `QMenu` | 自定义 `Qt.Popup` 菜单在 GNOME/Wayland 下定位/半透明黑块/Esc/几何无效等问题多，原生菜单更稳 |
| 保持 GNOME portal 输入后端，接受每次启动一次授权 | portal 在安全/零部署/可分发/跨发行版/前瞻性上全面优于 ydotool；ydotool 仅"无弹窗"占优但代价是 `/dev/uinput` 权限降级，不可作为已发布应用的默认 |

## 遇到的错误
| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| 更新 PWF 时补丁上下文未匹配 | 1 | 重新读取三件套后使用更精确补丁 |
| PC 单元测试因缺少 PyQt5 导入失败 | 1 | 记录为环境限制；未安装依赖 |
| 当前 Ubuntu 会话为 Wayland，Voicing Linux 桌面端会主动拒绝启动 | 1 | 切换到 `Ubuntu on Xorg` 会话后再运行 |
| 当前源码运行环境缺少 PyQt5 和 pip | 1 | 下次补齐 Python 依赖环境后再启动 PC 端 |
| GNOME Wayland 不支持直接复用现有 pyautogui 全局按键路径 | 1 | 研究 RemoteDesktop portal/libei 与 ydotool 等替代输入后端 |
| Android debug APK 构建缺 Android SDK | 1 | 已补 SDK，但本任务未改 Android native，用户确认无需继续 APK 构建；停止构建，仅保留 analyze/test |
| GitHub Actions Linux release job 在 headless runner 中 Qt `xcb` 初始化失败 | 1 | Linux release job 和托盘测试设置 `QT_QPA_PLATFORM=offscreen`，本地 88 项 PC 测试通过 |
| 已发布 `v2.9.5` deb 在 GNOME Wayland 下误报 RemoteDesktop portal 键盘能力不可用 | 1 | 清理 PyInstaller 打包态调用系统命令时的 `LD_LIBRARY_PATH`，并发布 `v2.9.6` |
| `v2.9.6` 首次 release run 中 macOS `Create DMG` 报 `hdiutil: create failed - Resource busy` | 1 | 使用 GitHub Actions failed-job rerun 后通过，判断为 macOS runner 临时资源占用 |
| Heavy Research 联网报告首轮含省略号占位 | 1 | 按相同维度 prompt 自动重跑，第二轮通过 12/12 结构与占位符校验 |
| 第一轮键盘测试因旧 terminal cache API 已移除而 45 项均在 setUp 失败 | 1 | 删除旧 cache 测试前置，并按三态/ACTIVE-first/clipboard/portal 新语义重写回归测试 |
| 完整 PC suite 使用系统 Python 时 4 个模块因缺少 `qrcode` 无法导入 | 1 | 创建仓库 `.venv` 并安装 `pc/requirements.txt`，之后用隔离环境重跑完整测试 |
| 创建 `.venv` 时 Ubuntu 缺少 ensurepip / `python3.10-venv` | 1 | 使用免密 sudo 安装 `python3.10-venv`，再以 `--clear` 重建已生成的局部 venv |
| Wayland 自动化无法可靠把临时 GNOME Terminal 切到前台 | 3 | 新窗口受 focus-stealing prevention 限制，frame `grab_focus()` 返回 false，深层 terminal 扫描又超时；停止重复该路线，后续采用用户真实点击/已聚焦终端验证 |
| Ghostty 的真实 ACTIVE 窗口被 AT-SPI 暴露为 `Unnamed/frame` 且无 terminal/focused 子节点 | 1 | 从 ACTIVE accessible 的 AT-SPI PID 读取仅包含可执行文件 basename 的 `process_name`，由主分类器与 system helper 统一将 `ghostty` 判为 terminal；禁止依赖窗口标题或正文 |
| 独立 Portal harness 未持有全局 Qt application 时 `CreateSession` 超时 | 2 | 按真实产品生命周期持有全局 `QCoreApplication`；同一实现随后在 normal 与 terminal 两侧均成功建立并发送完整键序列 |
| 非空 Ghostty proof 使用第二个新 Portal 会话时停在 `Start` 授权并超时 | 1 | 不把授权超时当作输入成功；下一步在单个已授权 Portal backend 生命周期内连续完成空文本和非空 proof，避免重复授权窗口 |
| 本地 DEB 临时目录脚本因包含递归清理被安全策略拒绝 | 1 | 未发生删除；改用 PyInstaller 已重建且受 ignore 管理的 `pc/dist/deb-root`，不执行递归清理 |
| 按旧 workflow 本地打出的 DEB 内容保留普通用户所有权与 umask 模式 | 1 | workflow 改用 `chmod 0644` 与 `dpkg-deb --root-owner-group`，重建后全部内容为 `root/root` |
| 最终 DEB 重打包检测到上次 `deb-root` 仍存在并主动退出 | 1 | 未覆盖旧目录；将旧目录移动为 ignore 内备份，再从最终二进制创建全新 package root |
| 首轮 Release 的 `SHA256SUMS.txt` 保留 CI artifact 子目录，扁平下载后无法直接校验 | 1 | workflow 生成时去除平台目录并断言 5 行/无斜杠；本次仅覆盖 checksum 资产后重新下载原生校验通过 |
| 从 `/tmp` 执行 `gh release upload` 无法推断仓库 | 1 | 未上传任何内容；重试时显式传入 `--repo kevinlasnh/Voicing` 后成功 |

## 备注
- PWF 内容仅记录 agent 自己的检查计划和发现；外部内容如需引用只进入 findings.md。
