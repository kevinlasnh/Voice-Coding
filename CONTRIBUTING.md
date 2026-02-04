# Contributing to Voicing / 贡献指南

感谢您有兴趣为 Voicing 做出贡献！

## 如何贡献

### 报告 Bug

1. 在 [Issues](https://github.com/kevinlasnh/Voice-Coding/issues) 中搜索是否已有相同问题
2. 如果没有，创建新 Issue，包含：
   - 问题描述
   - 复现步骤
   - 期望行为
   - 实际行为
   - 环境信息（Windows 版本、Python 版本等）

### 提交功能建议

1. 创建新 Issue，标记为 `enhancement`
2. 描述功能需求和使用场景

### 提交代码

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request

## 代码规范

- Python 代码遵循 PEP 8
- 使用有意义的变量名和函数名
- 添加必要的注释（中英双语优先）
- 保持代码简洁

## 开发环境

```bash
# 克隆仓库
git clone https://github.com/kevinlasnh/Voice-Coding.git
cd Voice-Coding/pc

# 安装依赖
pip install -r requirements.txt

# 运行
python voice_coding.py
```

## 测试

在提交 PR 前，请确保：
1. 程序能正常启动
2. 手机端能正常连接
3. 文本能正常发送到电脑

---

再次感谢您的贡献！
