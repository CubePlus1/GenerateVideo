# GenerateVideo

A Python CLI tool for generating videos from two images using AI-powered video generation.

## Overview

GenerateVideo is a command-line utility that transforms two static images into a smooth video transition using AI. The tool features robust error handling, real-time progress tracking, and automatic retry mechanisms for reliable video generation.

### Key Features

- **Base64 Image Encoding**: Automatic image preprocessing and encoding
- **Streaming API**: Real-time progress updates during video generation
- **Rich Progress Bars**: Visual feedback with detailed status information
- **Comprehensive Error Handling**: Clear error messages and recovery guidance
- **Flexible Configuration**: Customizable output paths and API settings

## Requirements

- **Python**: 3.10 or higher
- **Dependencies**:
  - `httpx`: Async HTTP client for API communication
  - `rich`: Terminal formatting and progress bars
  - `pytest`: Testing framework
  - `black`: Code formatting

## Installation

### Step 1: Navigate to Project

```bash
cd D:\0code\0toys\GenerateVideo
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv

# Linux/macOS
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
# Recommended: Use uv for faster installation
uv pip install -r requirements.txt

# Alternative: Standard pip
pip install -r requirements.txt
```

## Usage

### Basic Command

```bash
python generate_video.py --image1 path/to/first.jpg --image2 path/to/second.jpg --prompt prompt.txt
```

### Short Form Arguments

```bash
python generate_video.py -img1 first.jpg -img2 second.jpg -p prompt.txt
```

### Custom Output Directory

```bash
python generate_video.py -img1 first.jpg -img2 second.jpg -p prompt.txt -o ./my_videos/
```

## Command-Line Arguments

| Argument | Short Form | Required | Description |
|----------|------------|----------|-------------|
| `--image1` | `-img1` | ✅ | Path to first image (JPEG/PNG, max 10MB) |
| `--image2` | `-img2` | ✅ | Path to second image (JPEG/PNG, max 10MB) |
| `--prompt` | `-p` | ✅ | Path to text file containing generation prompt |
| `--output` | `-o` | ❌ | Output directory (default: `./output/`) |

### Image Requirements

- **Supported Formats**: JPEG, PNG
- **Maximum Size**: 10MB per image
- **Recommended Resolution**: 512x512 to 1024x1024 pixels

## Output

### File Naming Convention

Generated videos follow this naming pattern:

```
video_YYYYMMDD_HHMMSS_<uuid>.mp4
```

**Example**: `video_20260207_143052_a3f2b1c4.mp4`

### Default Location

Videos are saved to `./output/` unless specified otherwise with the `-o` flag.

## Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `0` | Success | Video generated successfully |
| `1` | Invalid Input | Missing files, wrong format, or file too large |
| `2` | API Error | Server returned 4xx/5xx error response |
| `3` | Network Error | Connection timeout or server unreachable |
| `4` | Save Error | Disk full, permission denied, or I/O error |

## Examples

### Using Example Files

```bash
python generate_video.py \
  -img1 examples/sample_images/test1.jpg \
  -img2 examples/sample_images/test2.jpg \
  -p examples/sample_prompt.txt
```

### Specifying Custom Output

```bash
python generate_video.py \
  -img1 photos/sunrise.jpg \
  -img2 photos/sunset.jpg \
  -p prompts/day_transition.txt \
  -o ./generated_videos/
```

### Batch Processing (Windows)

```batch
@echo off
for %%i in (image_pairs\*.jpg) do (
  python generate_video.py -img1 %%i -img2 image_pairs\next_%%i -p prompt.txt
)
```

## Troubleshooting

### Common Errors and Solutions

#### "Image file too large"

**Problem**: One or both images exceed the 10MB limit.

**Solution**: Resize or compress images before processing.

```bash
# Example using ImageMagick
magick convert large_image.jpg -resize 1024x1024 -quality 85 optimized_image.jpg
```

#### "Network Error"

**Problem**: Cannot connect to API server.

**Solution**:
1. Verify API server is running at `http://localhost:8000`
2. Check network connectivity
3. Review firewall settings

```bash
# Test API connectivity
curl http://localhost:8000/health
```

#### "API Error: 401 Unauthorized"

**Problem**: Invalid or missing API authentication token.

**Solution**: Update your API token in `src/config.py`:

```python
# src/config.py
API_TOKEN = "your-valid-token-here"
```

#### "Permission denied" (Save Error)

**Problem**: No write permissions for output directory.

**Solution**:
- Check directory permissions
- Run with appropriate privileges
- Ensure output directory exists and is writable

```bash
# Windows: Check permissions
icacls output

# Create output directory
mkdir output
```

#### "Invalid image format"

**Problem**: Image file is not JPEG or PNG.

**Solution**: Convert images to supported format:

```bash
# Using ImageMagick
magick convert image.bmp image.jpg
```

## Configuration

### API Settings

Edit `src/config.py` to customize:

```python
# API Configuration
API_ENDPOINT = "http://localhost:8000/generate"
API_TOKEN = "your-api-token"
REQUEST_TIMEOUT = 300  # seconds (5 minutes)

# Output Settings
DEFAULT_OUTPUT_DIR = "./output/"
VIDEO_FILENAME_PATTERN = "video_{timestamp}_{uuid}.mp4"
```

### Timeout Configuration

For longer video generation tasks, increase the timeout:

```python
# src/config.py
REQUEST_TIMEOUT = 600  # 10 minutes
```

## Development

### Running Tests

```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Run all tests
pytest tests/

# Run with verbose output
pytest -v tests/

# Run specific test file
pytest tests/test_image_processing.py
```

### Code Formatting

This project uses Black for consistent code formatting:

```bash
# Format all Python files
black .

# Check formatting without applying
black --check .
```

## Project Structure

```
GenerateVideo/
├── generate_video.py          # Main CLI entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── src/
│   ├── api_client.py         # API communication logic
│   ├── image_processing.py   # Image encoding utilities
│   ├── config.py             # Configuration settings
│   └── validators.py         # Input validation
├── tests/
│   ├── test_api_client.py
│   ├── test_image_processing.py
│   └── test_validators.py
├── examples/
│   ├── sample_images/
│   │   ├── test1.jpg
│   │   └── test2.jpg
│   └── sample_prompt.txt
└── output/                    # Generated videos (created automatically)
```

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact: [your-email@example.com]
- Documentation: [project-docs-url]

## Changelog

### Version 1.0.0 (2026-02-07)
- Initial release
- Two-image video generation
- Progress tracking with Rich library
- Comprehensive error handling
- Base64 image encoding
- Streaming API support
