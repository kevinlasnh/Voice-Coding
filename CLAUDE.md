# Voice-Coding 开发规范

## ⚠️ 强制规则

### 每次代码修改后必须更新 CHANGELOG

**以下情况必须撰写 CHANGELOG：**
- 代码有功能改动（新增、修改、删除功能）
- Bug 修复
- UI/UI 样式变更
- 配置文件变更
- 依赖库版本变更

**流程：**
1. 修改代码
2. **立即更新 CHANGELOG.md**
3. Git commit
4. Git push

---

## 项目架构

### PC 端 (Python)
- **主程序**: `pc/voice_coding.py`
- **Web 前端**: `pc/web/index.html`
- **依赖**: `pc/requirements.txt`

### Android 端 (Flutter)
- **主程序**: `android/voice_coding/lib/main.dart`
- **依赖**: `android/voice_coding/pubspec.yaml`

---

## 开发命令

### PC 端热重启
```powershell
powershell -ExecutionPolicy Bypass -File ".claude/skills/pc-hot-restart/restart_pc_dev.ps1"
```

### PC 端打包
```bash
cd pc
pyinstaller --onefile --windowed --name=VoiceCoding --add-data="web;web" voice_coding.py
```

### Android 端运行
```bash
cd android/voice_coding
flutter run
```

---

## 设计规范

### 颜色
- 背景深色: `#3D3B37`
- 文字白色: `#ECECEC`
- 成功绿色: `#5CB87A`
- 警告橙色: `#E5A84B`
- 错误红色: `#E85C4A`
- 灰色占位: `#6B6B6B`

### 间距
- 边缘 padding: 16px
- 组件内 padding: 14px
- 组件间距: 12px
- 圆角: 12px

### 字体
- 正文: 16px
- 状态文字: 15px, fontWeight 600
- 提示文字: 13px
