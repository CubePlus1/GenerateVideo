# Issue: ModuleNotFoundError when running `genvideo` command

## 问题描述

安装包后运行 `genvideo --help` 时出现以下错误：

```
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "D:\0code\0toys\GenerateVideo\.venv\Scripts\genvideo.exe\__main__.py", line 4, in <module>
ModuleNotFoundError: No module named 'src'
```

但是使用 `python -m src.cli.main --help` 可以正常运行。

## 根本原因

### 原因 1: `pyproject.toml` 缺少包根路径配置

**问题**：setuptools 无法正确识别 `src` 目录的位置。

**解决方案**：在 `pyproject.toml` 中添加包目录配置：

```toml
[tool.setuptools]
packages = ["src", "src.cli", "src.models"]

[tool.setuptools.package-dir]
"" = "."
```

**说明**：
- `packages` 显式列出所有需要安装的包
- `package-dir` 告诉 setuptools 包的根路径在项目根目录 `"."`

### 原因 2: 虚拟环境和 pip 不匹配

**问题**：虚拟环境由 `uv` 创建（`.venv` 目录），但使用全局 `pip` 安装包。

**现象**：
- `pip install -e .` 将包安装到全局 Python 环境
- `.venv` 虚拟环境中没有安装包
- `genvideo` 命令在虚拟环境中找不到 `src` 模块

**解决方案**：使用 `uv pip` 安装到虚拟环境：

```bash
# 激活虚拟环境
.venv\Scripts\activate

# 使用 uv pip 安装（推荐）
uv pip install -e .

# 或使用标准 pip（确保在虚拟环境中）
pip install -e .
```

## 完整解决步骤

### 1. 修复 `pyproject.toml`

确保包含以下配置：

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "generatevideo"
version = "0.1.0"
description = "Unified video generation CLI - T2V and I2V"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "moviepy>=2.2.1",
    "httpx",
    "rich",
    "click>=8.1.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
]

[project.scripts]
genvideo = "src.cli.main:cli"

[tool.setuptools]
packages = ["src", "src.cli", "src.models"]

[tool.setuptools.package-dir]
"" = "."
```

### 2. 重新安装包

```bash
# 卸载旧版本
uv pip uninstall generatevideo -y

# 重新安装（可编辑模式）
uv pip install -e .
```

### 3. 验证安装

```bash
# 测试命令
genvideo --help

# 应该输出：
# Usage: genvideo [OPTIONS] COMMAND [ARGS]...
#
#   Unified video generation CLI - T2V and I2V
#
#   Generate videos from text prompts or images using AI models.
#
# Options:
#   --version  Show the version and exit.
#   --help     Show this message and exit.
#
# Commands:
#   i2v     Generate video from 1-2 images
#   models  List available video generation models
#   t2v     Generate video from text prompt
```

## 诊断检查清单

如果遇到类似问题，按以下顺序检查：

### ✅ 1. 检查虚拟环境是否激活
```bash
# Windows PowerShell
# 应该显示 (generatevideo) 或 (.venv) 前缀
```

### ✅ 2. 检查使用的 pip 版本
```bash
# 应该指向虚拟环境中的 pip
where pip

# 推荐使用 uv pip
uv pip --version
```

### ✅ 3. 检查包是否安装
```bash
pip list | findstr generatevideo
# 或
uv pip list | findstr generatevideo

# 应该显示：generatevideo 0.1.0
```

### ✅ 4. 测试 Python 模块导入
```bash
python -m src.cli.main --help
```

如果此命令能工作但 `genvideo` 不行，说明是包安装配置问题。

### ✅ 5. 检查 pyproject.toml 配置
确保包含：
- `[build-system]` - 构建系统配置
- `[tool.setuptools]` - 包列表和根路径
- `[tool.setuptools.package-dir]` - 包目录映射

## 最佳实践

### 1. 使用虚拟环境

**推荐使用 uv**（更快）：
```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境（Windows）
.venv\Scripts\activate

# 安装包
uv pip install -e .
```

**或使用标准 venv**：
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境（Windows）
.venv\Scripts\activate

# 安装包
pip install -e .
```

### 2. 项目结构

```
GenerateVideo/
├── .venv/                  # 虚拟环境（不提交到 git）
├── src/                    # 源代码包
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── t2v.py
│   │   ├── i2v.py
│   │   └── models.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── catalog.py
│   │   └── selector.py
│   ├── config.py
│   ├── api_client.py
│   └── ...
├── pyproject.toml          # 包配置（关键文件）
├── README.md
└── .env                    # 配置文件（不提交到 git）
```

### 3. 配置文件完整性

确保 `pyproject.toml` 包含所有必要部分：

| 配置段 | 作用 | 必需 |
|--------|------|------|
| `[build-system]` | 指定构建工具 | ✅ 是 |
| `[project]` | 包元数据和依赖 | ✅ 是 |
| `[project.scripts]` | CLI 入口点 | ✅ 是 |
| `[tool.setuptools]` | 包列表 | ✅ 是 |
| `[tool.setuptools.package-dir]` | 包根路径 | ✅ 是 |

## 相关文档

- [Python Packaging User Guide](https://packaging.python.org/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Click Documentation](https://click.palletsprojects.com/)

## 日期

- **发现日期**: 2026-02-07
- **修复日期**: 2026-02-07
- **影响版本**: v0.1.0
- **状态**: ✅ 已解决
