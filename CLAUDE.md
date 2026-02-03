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
pyinstaller --onefile --windowed --name=VoiceCoding voice_coding.py
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

---

## CI/CD 规则 (GitHub Actions)

### ⚠️ Android Gradle 构建配置

**问题根源**: GitHub Actions runner 网络环境特殊，配置不当会导致 Gradle 下载失败。

**必须遵守的规则**:

1. **gradle.properties 不能包含本地代理配置**
   ```gradle
   # ❌ 错误 - 会导致 CI 构建失败
   systemProp.https.proxyHost=127.0.0.1
   systemProp.https.proxyPort=7890
   ```

2. **gradle-wrapper.properties 使用官方源**
   ```properties
   # ✅ 正确
   distributionUrl=https\://services.gradle.org/distributions/gradle-8.12-all.zip
   ```

3. **Gradle wrapper 文件必须提交到仓库**
   - `android/voice_coding/gradlew`
   - `android/voice_coding/gradlew.bat`
   - `android/voice_coding/gradle/wrapper/gradle-wrapper.jar`
   - `android/voice_coding/gradle/wrapper/gradle-wrapper.properties`

4. **GitHub Actions workflow 配置**
   ```yaml
   - name: Set up Java
     uses: actions/setup-java@v4
     with:
       distribution: 'zulu'
       java-version: '17'

   - name: Set up Flutter
     uses: subosito/flutter-action@v2
     with:
       flutter-version: 3.27.0
       cache: true

   - name: Build APK
     run: flutter build apk --release
   ```

**常见错误**: `java.net.ConnectException: Connection refused`
- 原因: gradle.properties 配置了本地代理
- 解决: 删除代理配置或使用 `gradle.properties` 模板文件

---

## 当前开发状态 (2026-02-03)

### ✅ 已完成功能

#### PC 端托盘菜单 (v1.8.0)
- **Windows 11 Fluent Design 风格** - 完整实现
- **悬停高亮效果** - 使用 `paintEvent` + `WA_TransparentForMouseEvents` 解决
- **日志系统** - 日志文件位于 `%APPDATA%\VoiceCoding\logs\`
- **菜单项**:
  - 📡 同步输入（开关）
  - 🚀 开机自启（开关）
  - 📋 打开日志
  - 🚪 退出应用

#### 关键技术实现

**PyQt5 悬停高亮解决方案** (重要！):
```python
# 问题：PyQt5 自定义 QWidget 的 :hover CSS 伪状态不工作
# 解决方案：

# 1. 使用 paintEvent 手动绘制背景
def paintEvent(self, event):
    painter = QPainter(self)
    if self._hovered:
        painter.setBrush(QColor(255, 255, 255, 15))
    painter.drawRoundedRect(rect, 4, 4)

# 2. 子控件必须设置鼠标事件穿透
self.icon_label.setAttribute(Qt.WA_TransparentForMouseEvents)
self.text_label.setAttribute(Qt.WA_TransparentForMouseEvents)

# 3. 使用 enterEvent/leaveEvent 追踪悬停状态
def enterEvent(self, event):
    self._hovered = True
    self.update()
```

### 📁 关键文件位置

| 文件 | 说明 |
|------|------|
| `pc/voice_coding.py` | PC 端主程序 |
| `pc/voice_coding.py:695-800` | `MenuItemWidget` 类 - 菜单项组件 |
| `pc/voice_coding.py:802-970` | `ModernMenuWidget` 类 - 菜单容器 |
| `pc/voice_coding.py:972-1070` | `ModernTrayIcon` 类 - 托盘图标 |
| `pc/voice_coding.py:138-170` | `setup_logging()` 日志配置 |

### 🔧 开发工具

**PC 热重启命令**:
```powershell
powershell -ExecutionPolicy Bypass -File ".claude/skills/pc-hot-restart/restart_pc_dev.ps1"
```

### ⚠️ 注意事项

1. **不要使用 QSS :hover** - PyQt5 自定义 QWidget 不支持
2. **子控件必须穿透鼠标事件** - 否则 enterEvent/leaveEvent 不会触发
3. **使用 state.tray_icon** - 不要传 None 给 update_tray_icon_pyqt()

