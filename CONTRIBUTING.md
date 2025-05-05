# 贡献指南

感谢您对儿童智能台灯监控系统项目的关注！我们欢迎所有形式的贡献，包括但不限于：
- 代码贡献
- 文档改进
- Bug报告
- 功能建议

## 开发环境设置

1. 克隆项目仓库
```bash
git clone [repository-url]
cd Py-server
```

2. 配置Python环境
```bash
# 使用conda
conda env create -f environment.yml
conda activate py-server

# 或使用pip
pip install -r requirements.txt
```

## 代码规范

- 遵循PEP 8 Python代码风格指南
- 使用有意义的变量和函数名称
- 添加必要的注释和文档字符串
- 保持代码整洁和模块化

## 提交规范

1. 创建新的分支进行开发
```bash
git checkout -b feature/your-feature-name
```

2. 提交信息格式
```
类型: 简短的描述

详细描述（如果需要）
```
类型包括：
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码风格修改
- refactor: 代码重构
- test: 测试相关
- chore: 构建过程或辅助工具的变动

3. 发起Pull Request
- 确保代码通过所有测试
- 提供清晰的PR描述
- 关联相关的Issue

## 子模块开发

如果您在开发语音交互等子模块：
1. 查阅README中的API文档
2. 遵循项目的串口通信协议
3. 确保与主系统的兼容性

## 问题报告

报告问题时请包含：
- 问题的详细描述
- 复现步骤
- 期望的行为
- 实际的行为
- 系统环境信息

## 联系方式

如有任何问题，请通过以下方式联系我们：
- 提交Issue
- 发送邮件至[项目维护者邮箱](2256096153@qq.com)