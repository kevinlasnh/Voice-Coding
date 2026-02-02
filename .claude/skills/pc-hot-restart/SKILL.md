---
name: pc_hot_restart
description: Restart Voice Coding PC dev process by killing the old instance and starting a new one.
---

# Skill: PC 端热重启 (Hot Restart)

用于快速迭代 PC 端程序：修改代码后自动杀掉旧进程并重启开发版本。

## 🎯 目标
- 结束当前运行的 `voice_coding.py` 进程
- 可选结束 `VoiceCoding.exe`（如果仍在运行）
- 以 `--dev` 模式重新启动脚本

## 🚀 执行步骤 (Procedure)

1. **运行脚本**（PowerShell）：

   ```powershell
   # 在任意目录执行，脚本会自动定位仓库根目录
   powershell -ExecutionPolicy Bypass -File "C:\Zero\Doc\Cloud\GitHub\Voice-Coding\.claude\skills\pc-hot-restart\restart_pc_dev.ps1"
   ```

2. **预期结果**
   - 旧进程被停止
   - 新进程启动成功（带 `--dev` 参数）
   - 终端显示 `Restarted dev app: ...`

## ✅ 验证
- 任务栏托盘出现 Voice Coding 图标
- 手机端/Android 端重新连接正常
- 控制台无报错
