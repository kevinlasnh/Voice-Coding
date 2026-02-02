# Voice-Coding 开发规范

## ⚠️ 强制规则

### 每次代码修改后必须更新 CHANGELOG

**以下情况必须撰写 CHANGELOG：**
- 代码有功能改动（新增、修改、删除功能）
- Bug 修复
- UI/UI 样式变更
- 配置文件变更
- 依赖库版本变更

**使用方式：**
```
调用 changelog-automation Skill 自动生成
```

**流程：**
1. 修改代码
2. **立即更新 CHANGELOG.md** (使用 Skill)
3. Git commit
4. Git push
