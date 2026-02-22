<div align="center">

<img src="assets/banner.png" alt="Personal Website Manager Banner" width="100%">

# Personal Website Manager

<a href="README.md">English</a> | <a href="README_CN.md">简体中文</a>

**一款现代化、优雅的 Markdown 编辑器，支持实时预览、Git 集成和 AI 写作助手。**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/6chHenry/personal-website-manager)

<img src="assets/screenshots/main_interface.png" alt="主界面" width="80%">

</div>

---

## ✨ 功能特性

- 📝 **Markdown 编辑器** - 功能完整的 Markdown 编辑，支持语法高亮，字体与预览保持一致
- 👁 **实时预览** - 实时渲染预览，精美的深色主题
- 🌳 **文件树** - 直观的文件导航，支持右键菜单操作，智能三级展开
- 🧠 **思维导图** - 可视化目录结构，交互式思维导图，支持展开折叠，视图中心保持稳定
- 🔀 **Git 集成** - 内置 Git 版本控制支持
- 🤖 **AI 助手** - AI 驱动的写作助手，支持多模型切换（硅基流动 + Moonshot）
- 🔍 **内容搜索** - 跨所有 Markdown 文件搜索
- 📐 **数学公式** - LaTeX/KaTeX 数学公式渲染
- 🖼 **图片预览** - 内置图片查看器
- 🎨 **现代界面** - 精美的深色主题，流畅动画效果，简洁双栏布局

---

## 🚀 新增功能

### 思维导图视图
将文档结构可视化为交互式思维导图。双击文件夹展开/折叠，智能视图保持让焦点稳定不偏移。

### 多模型 AI 助手
在硅基流动模型（DeepSeek、Qwen、GLM）和 Moonshot（Kimi K2.5）之间无缝切换。根据所选模型自动切换 API 配置。

### 统一字体
编辑器现在使用与预览相同的精美「霞鹜文楷」字体，实现真正的所见即所得编辑体验。

### 精简布局
专注的双栏布局（编辑器 + 预览），最大化生产力。不再有多余的布局切换。

---

## 📸 软件截图

<div align="center">
  <img src="assets/screenshots/editor.png" alt="编辑器" width="45%">
  <img src="assets/screenshots/preview.png" alt="预览" width="45%">
</div>

<div align="center">
  <img src="assets/screenshots/ai_chat.png" alt="AI 对话" width="45%">
  <img src="assets/screenshots/git_commit.png" alt="Git 提交" width="45%">
</div>

---

## 🚀 快速开始

### 环境要求

- Python 3.10 或更高版本
- Git（用于版本控制功能）

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/6chHenry/personal-website-manager.git
   cd personal-website-manager
   ```

2. **创建虚拟环境**（推荐）
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行程序**
   ```bash
   python main.py
   ```

---

## ⚙️ 配置说明

### AI 助手配置

要使用 AI 助手功能，需要配置您的 API 密钥：

1. 在程序目录创建 `config.json` 文件
2. 添加您的 API 配置：
   ```json
   {
     "api_key": "your-api-key-here",
     "api_base": "https://api.siliconflow.cn/v1"
   }
   ```

### 支持的 AI 模型

**硅基流动模型：**
- DeepSeek V3（推荐）
- DeepSeek R1
- Qwen3-8B
- Qwen2.5 系列（7B/14B/32B）
- Qwen2.5-Coder-7B
- GLM-4-9B
- GLM-Z1-9B

**Moonshot 模型：**
- Kimi K2.5

---

## 📖 文档

详细文档请访问我们的 [Wiki](https://github.com/6chHenry/personal-website-manager/wiki)。

- [快速入门](https://github.com/6chHenry/personal-website-manager/wiki/Getting-Started)
- [功能指南](https://github.com/6chHenry/personal-website-manager/wiki/Features)
- [配置说明](https://github.com/6chHenry/personal-website-manager/wiki/Configuration)
- [快捷键](https://github.com/6chHenry/personal-website-manager/wiki/Keyboard-Shortcuts)

---

## 🛠️ 技术栈

- **GUI 框架**: PyQt6
- **Markdown 渲染**: markdown2
- **语法高亮**: Pygments
- **数学渲染**: KaTeX / MathJax
- **版本控制**: GitPython
- **AI 集成**: OpenAI 兼容 API

---

## 🤝 参与贡献

欢迎参与贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

请阅读我们的 [贡献指南](CONTRIBUTING.md) 了解更多详情。

---

## 📝 开源协议

本项目基于 MIT 协议开源 - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI 框架
- [markdown2](https://github.com/trentm/python-markdown2) - Markdown 解析器
- [KaTeX](https://katex.org/) - 数学公式渲染
- [SiliconFlow](https://siliconflow.cn/) - AI API 提供商
- [Moonshot AI](https://www.moonshot.cn/) - Kimi API 提供商

---

## 📧 联系方式

<!-- Your Name - [@twitter_handle](https://twitter.com/yourhandle) - email@example.com -->

项目地址: [https://github.com/6chHenry/personal-website-manager](https://github.com/6chHenry/personal-website-manager)

---

<div align="center">

**如果这个项目对您有帮助，请考虑给它一个 ⭐️！**

[⬆ 返回顶部](#personal-website-manager)

</div>
