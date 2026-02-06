# 视频生成 CLI 工具

一个基于 AI 的 Python 命令行工具，可从两张图片生成平滑的过渡视频。

## 概述

GenerateVideo 是一个命令行实用工具，使用 AI 技术将两张静态图片转换为流畅的视频过渡效果。该工具具有强大的错误处理、实时进度跟踪和自动重试机制，可确保视频生成的可靠性。

### 核心特性

- **Base64 图片编码**：自动图片预处理和编码
- **流式 API 调用**：视频生成过程中的实时进度更新
- **丰富的进度条**：带详细状态信息的可视化反馈
- **完善的错误处理**：清晰的错误消息和恢复指导
- **灵活的配置**：可自定义输出路径和 API 设置

## 系统要求

- **Python**：3.10 或更高版本
- **依赖包**：
  - `httpx`：用于 API 通信的异步 HTTP 客户端
  - `rich`：终端格式化和进度条
  - `pytest`：测试框架
  - `black`：代码格式化

## 安装步骤

### 第 1 步：进入项目目录

```bash
cd D:\0code\0toys\GenerateVideo
```

### 第 2 步：创建虚拟环境

```bash
# Windows
python -m venv venv

# Linux/macOS
python3 -m venv venv
```

### 第 3 步：激活虚拟环境

```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 第 4 步：安装依赖

```bash
# 推荐：使用 uv 以获得更快的安装速度
uv pip install -r requirements.txt

# 或者：使用标准 pip
pip install -r requirements.txt
```

## 使用方法

### 基础命令

```bash
python generate_video.py --image1 第一张图.jpg --image2 第二张图.jpg --prompt 提示词.txt
```

### 简写参数形式

```bash
python generate_video.py -img1 图1.jpg -img2 图2.jpg -p 提示词.txt
```

### 自定义输出目录

```bash
python generate_video.py -img1 图1.jpg -img2 图2.jpg -p 提示词.txt -o ./我的视频/
```

## 命令行参数说明

| 参数 | 简写 | 必需 | 说明 |
|------|------|------|------|
| `--image1` | `-img1` | ✅ | 第一张图片的路径（JPEG/PNG，最大 10MB）|
| `--image2` | `-img2` | ✅ | 第二张图片的路径（JPEG/PNG，最大 10MB）|
| `--prompt` | `-p` | ✅ | 包含生成提示词的文本文件路径 |
| `--output` | `-o` | ❌ | 输出目录（默认：`./output/`）|

### 图片要求

- **支持的格式**：JPEG、PNG
- **最大文件大小**：每张图片 10MB
- **推荐分辨率**：512x512 到 1024x1024 像素

## 输出文件

### 文件命名规则

生成的视频遵循以下命名模式：

```
video_年月日_时分秒_<uuid>.mp4
```

**示例**：`video_20260207_143052_a3f2b1c4.mp4`

### 默认保存位置

视频保存到 `./output/` 目录，除非使用 `-o` 参数指定其他位置。

## 退出代码

| 代码 | 含义 | 说明 |
|------|---------|-------------|
| `0` | 成功 | 视频生成成功 |
| `1` | 输入无效 | 文件缺失、格式错误或文件过大 |
| `2` | API 错误 | 服务器返回 4xx/5xx 错误响应 |
| `3` | 网络错误 | 连接超时或服务器无法访问 |
| `4` | 保存错误 | 磁盘已满、权限被拒绝或 I/O 错误 |

## 使用示例

### 使用示例文件

```bash
python generate_video.py ^
  -img1 examples/sample_images/test1.jpg ^
  -img2 examples/sample_images/test2.jpg ^
  -p examples/sample_prompt.txt
```

### 指定自定义输出目录

```bash
python generate_video.py ^
  -img1 photos/sunrise.jpg ^
  -img2 photos/sunset.jpg ^
  -p prompts/day_transition.txt ^
  -o ./generated_videos/
```

### 批量处理（Windows）

```batch
@echo off
for %%i in (image_pairs\*.jpg) do (
  python generate_video.py -img1 %%i -img2 image_pairs\next_%%i -p prompt.txt
)
```

## 故障排除

### 常见错误及解决方案

#### 错误："Image file too large"（图片文件过大）

**问题**：一张或两张图片超过了 10MB 的限制。

**解决方案**：在处理前调整或压缩图片大小。

```bash
# 使用 ImageMagick 示例
magick convert large_image.jpg -resize 1024x1024 -quality 85 optimized_image.jpg
```

#### 错误："Network Error"（网络错误）

**问题**：无法连接到 API 服务器。

**解决方案**：
1. 验证 API 服务器正在 `http://localhost:8000` 上运行
2. 检查网络连接
3. 查看防火墙设置

```bash
# 测试 API 连接性
curl http://localhost:8000/health
```

#### 错误："API Error: 401 Unauthorized"（API 错误：401 未授权）

**问题**：API 认证令牌无效或缺失。

**解决方案**：在 `src/config.py` 中更新您的 API 令牌：

```python
# src/config.py
API_TOKEN = "your-valid-token-here"
```

#### 错误："Permission denied"（权限被拒绝）（保存错误）

**问题**：输出目录没有写入权限。

**解决方案**：
- 检查目录权限
- 以适当的权限运行
- 确保输出目录存在且可写

```bash
# Windows：检查权限
icacls output

# 创建输出目录
mkdir output
```

#### 错误："Invalid image format"（图片格式无效）

**问题**：图片文件不是 JPEG 或 PNG 格式。

**解决方案**：将图片转换为支持的格式：

```bash
# 使用 ImageMagick
magick convert image.bmp image.jpg
```

## 配置说明

### API 设置

编辑 `src/config.py` 以自定义配置：

```python
# API 配置
API_ENDPOINT = "http://localhost:8000/v1/chat/completions"
API_TOKEN = "your-api-token"
MODEL_NAME = "veo_3_1_i2v_s_fast_fl_landscape"
REQUEST_TIMEOUT = 300  # 秒（5 分钟）

# 文件约束
MAX_IMAGE_SIZE = 10485760  # 10MB（字节）
VALID_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png']

# 输出设置
DEFAULT_OUTPUT_DIR = "./output/"
```

### 超时配置

对于较长的视频生成任务，可以增加超时时间：

```python
# src/config.py
REQUEST_TIMEOUT = 600  # 10 分钟
```

## 开发相关

### 运行测试

```bash
# 首先激活虚拟环境
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# 运行所有测试
pytest tests/

# 详细输出模式
pytest -v tests/

# 运行特定测试文件
pytest tests/test_encoder.py
```

### 代码格式化

本项目使用 Black 进行代码格式化：

```bash
# 格式化所有 Python 文件
black .

# 检查格式但不应用更改
black --check .
```

## 项目结构

```
GenerateVideo/
├── generate_video.py          # 主入口文件
├── requirements.txt           # Python 依赖
├── README.md                  # 英文文档
├── README_CN.md               # 中文文档（本文件）
├── venv/                      # 虚拟环境
├── src/
│   ├── __init__.py
│   ├── config.py             # 配置设置
│   ├── errors.py             # 自定义异常定义
│   ├── encoder.py            # 图片编码工具
│   ├── api_client.py         # API 通信逻辑
│   ├── video_saver.py        # 视频保存功能
│   └── cli.py                # 命令行参数解析
├── tests/                     # 测试文件
│   ├── test_encoder.py
│   ├── test_api_client.py
│   └── test_cli.py
├── examples/                  # 示例文件
│   ├── sample_images/
│   │   ├── test1.jpg
│   │   └── test2.jpg
│   └── sample_prompt.txt
└── output/                    # 生成的视频（自动创建）
```

## 技术特性

- **自适应流式解析**：自动检测 API 响应格式（二进制/SSE/JSON）
- **进度可视化**：实时显示下载速度和剩余时间
- **文件验证**：自动检查图片存在性、格式和大小
- **跨平台兼容**：使用 pathlib 确保 Windows/Linux/macOS 路径处理
- **错误恢复**：失败时自动清理临时文件
- **唯一文件名**：时间戳 + UUID 防止文件覆盖
- **UTF-8 编码支持**：正确处理中文提示词和文件路径

## 许可证

MIT License

## 支持

遇到问题？请查阅：
- [英文文档](README.md)
- [故障排除](#故障排除)
- [配置说明](#配置说明)

---

**项目状态**：生产就绪 ✅
