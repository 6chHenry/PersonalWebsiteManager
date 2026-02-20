# Contributing to Personal Website Manager

First off, thank you for considering contributing to Personal Website Manager! It's people like you that make this project better.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if possible**
- **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and explain the expected behavior**
- **Explain why this enhancement would be useful**

### Pull Requests

- Fill in the required template
- Do not include issue numbers in the PR title
- Include screenshots and animated GIFs in your pull request whenever possible
- Follow the coding standards
- Include appropriate tests

---

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- A code editor (VS Code recommended)

### Setup Steps

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/6chHenry/personal-website-manager.git
   cd personal-website-manager
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Create a branch for your changes**
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use 4 spaces for indentation
- Maximum line length is 100 characters
- Use meaningful variable and function names
- Add docstrings to all public functions and classes

### Code Formatting

We use the following tools for code quality:

- `black` for code formatting
- `flake8` for linting
- `isort` for import sorting

Run these before committing:
```bash
black .
flake8 .
isort .
```

### File Structure

```
PersonalWebsiteApp/
├── assets/           # Images, icons, and other assets
├── core/             # Core business logic
│   ├── git_manager.py
│   ├── file_manager.py
│   └── markdown_renderer.py
├── ui/               # User interface components
│   ├── main_window.py
│   ├── editor.py
│   ├── preview.py
│   └── ...
├── config.py         # Configuration settings
├── main.py           # Application entry point
└── requirements.txt  # Dependencies
```

---

## Commit Guidelines

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests
- `chore`: Changes to the build process or auxiliary tools

#### Examples

```
feat(editor): add auto-save functionality

Add automatic saving of documents every 30 seconds with visual indicator.
Users can configure the interval in settings.

Closes #123
```

```
fix(preview): resolve image loading issue

Images with relative paths now load correctly in the preview panel.
The baseUrl parameter is properly set for QWebEngineView.

Fixes #456
```

---

## Pull Request Process

1. **Update the README.md** with details of changes to the interface
2. **Update the documentation** if you're changing functionality
3. **Add tests** for new features
4. **Ensure all tests pass** before submitting
5. **Request review** from maintainers

### PR Checklist

- [ ] Code follows the project's coding standards
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages follow the guidelines
- [ ] PR title is clear and descriptive

---

## Questions?

Feel free to open an issue with the "question" label, or reach out to the maintainers directly.

Thank you for your contributions! 🎉
