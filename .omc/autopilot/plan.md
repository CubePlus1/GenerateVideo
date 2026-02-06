# Implementation Plan: Python Video Generation CLI Tool

## Analysis Summary

The project directory (`D:\0code\0toys\GenerateVideo`) currently contains only the specification file. This is a greenfield implementation requiring complete project setup from scratch.

**Specification Reference**: `D:\0code\0toys\GenerateVideo\.omc\autopilot\spec.md`

---

## Implementation Plan

### Phase 0: Project Foundation
**Goal**: Establish virtual environment and directory structure

#### Task 0.1: Virtual Environment Setup
- **Complexity**: Simple
- **Files**: `venv\` (directory)
- **Commands**:
  ```bash
  # From D:\0code\0toys\GenerateVideo
  python -m venv venv
  venv\Scripts\activate
  ```
- **Success Criteria**:
  - `venv\` directory exists
  - Prompt shows `(venv)` when activated
- **Dependencies**: None

#### Task 0.2: Directory Structure
- **Complexity**: Simple
- **Files to Create**:
  ```
  D:\0code\0toys\GenerateVideo\src\__init__.py
  D:\0code\0toys\GenerateVideo\tests\__init__.py
  D:\0code\0toys\GenerateVideo\examples\sample_prompt.txt
  D:\0code\0toys\GenerateVideo\examples\sample_images\.gitkeep
  D:\0code\0toys\GenerateVideo\output\.gitkeep
  ```
- **Success Criteria**: All directories exist
- **Dependencies**: Task 0.1

#### Task 0.3: Requirements File
- **Complexity**: Simple
- **File**: `D:\0code\0toys\GenerateVideo\requirements.txt`
- **Content**:
  ```
  httpx==0.27.0
  rich==13.7.1
  pytest==8.0.0
  black==24.1.0
  ```
- **Success Criteria**: File created with exact dependencies
- **Dependencies**: Task 0.2

#### Task 0.4: Dependency Installation
- **Complexity**: Simple
- **Command**:
  ```bash
  # Ensure venv is activated
  uv pip install -r requirements.txt
  # Fallback: pip install -r requirements.txt
  ```
- **Success Criteria**:
  - All packages installed successfully
  - `pip list` shows httpx, rich, pytest, black
- **Dependencies**: Task 0.3

---

### Phase 1: Core Modules (Bottom-Up)

#### Task 1.1: Configuration Constants
- **Complexity**: Simple
- **File**: `D:\0code\0toys\GenerateVideo\src\config.py`
- **Implementation**:
  - API endpoint: `http://localhost:8000/v1/chat/completions`
  - Auth token: `han1234`
  - Model name: `veo_3_1_i2v_s_fast_fl_landscape`
  - Timeout: 300 seconds
  - Max image size: 10MB (10485760 bytes)
  - Default output directory: `./output/`
  - Valid image formats: `['.jpg', '.jpeg', '.png']`
- **Success Criteria**:
  - All constants defined as module-level variables
  - Type hints present
- **Dependencies**: Task 0.4

#### Task 1.2: Exception Hierarchy
- **Complexity**: Simple
- **File**: `D:\0code\0toys\GenerateVideo\src\errors.py`
- **Implementation**:
  ```python
  class VideoGenerationError(Exception): pass
  class InvalidImageError(VideoGenerationError): pass
  class APIError(VideoGenerationError): pass
  class StreamingError(VideoGenerationError): pass
  class SaveError(VideoGenerationError): pass
  ```
- **Success Criteria**:
  - 5 exception classes defined
  - Proper inheritance chain
  - Docstrings for each class
- **Dependencies**: Task 1.1

#### Task 1.3: Image Encoder
- **Complexity**: Medium
- **File**: `D:\0code\0toys\GenerateVideo\src\encoder.py`
- **Implementation**:
  - Function: `encode_image_to_base64(image_path: Path) -> str`
  - Validate file existence (`InvalidImageError` if missing)
  - Validate file extension (`.jpg`, `.jpeg`, `.png`)
  - Validate file size (< 10MB from `config.MAX_IMAGE_SIZE`)
  - Read binary content
  - Base64 encode using `base64.b64encode()`
  - Return as UTF-8 string
- **Success Criteria**:
  - Raises `InvalidImageError` for missing/invalid/oversized files
  - Returns valid base64 string for valid images
  - Uses `pathlib.Path` for paths
- **Dependencies**: Task 1.2

#### Task 1.4: Video Saver
- **Complexity**: Medium
- **File**: `D:\0code\0toys\GenerateVideo\src\video_saver.py`
- **Implementation**:
  - Function: `generate_output_path(output_dir: Path) -> Path`
    - Format: `video_YYYYMMDD_HHMMSS_<uuid>.mp4`
    - Create directory if missing
  - Function: `save_video_stream(stream_content: bytes, output_path: Path) -> None`
    - Write binary content to file
    - Raise `SaveError` on I/O errors
    - Delete partial file on failure
- **Success Criteria**:
  - Unique filenames via timestamp + UUID
  - Auto-creates output directory
  - Handles write failures gracefully
- **Dependencies**: Task 1.2

#### Task 1.5: API Client
- **Complexity**: Complex
- **File**: `D:\0code\0toys\GenerateVideo\src\api_client.py`
- **Implementation**:
  - Function: `generate_video(img1_b64: str, img2_b64: str, prompt: str) -> bytes`
  - Build payload per spec
  - POST with `httpx.Client()` (timeout=300)
  - Headers: `Authorization: Bearer han1234`, `Content-Type: application/json`
  - Stream response parsing (detect format: SSE/chunked JSON/binary)
  - Progress indication with `rich.progress`
  - Raise `APIError` for 4xx/5xx
  - Raise `StreamingError` for malformed responses
  - Return complete video bytes
- **Success Criteria**:
  - Sends correct payload
  - Handles streaming response
  - Shows progress bar
  - Returns binary video content
- **Dependencies**: Task 1.3, Task 1.4

---

### Phase 2: CLI and Orchestration

#### Task 2.1: Argument Parser
- **Complexity**: Medium
- **File**: `D:\0code\0toys\GenerateVideo\src\cli.py`
- **Implementation**:
  - Use `argparse.ArgumentParser`
  - Arguments:
    - `-img1` (required): Path to first image
    - `-img2` (required): Path to second image
    - `-p` (required): Path to prompt file
    - `-o` (optional): Output directory (default: `./output/`)
  - Validation:
    - Convert to `pathlib.Path` objects
    - Check file existence for images and prompt
    - Read prompt file content
  - Function: `parse_args() -> Namespace`
- **Success Criteria**:
  - All required args enforced
  - Help text displayed for `-h`
  - Paths converted to `Path` objects
- **Dependencies**: Task 1.1

#### Task 2.2: Main Entry Point
- **Complexity**: Complex
- **File**: `D:\0code\0toys\GenerateVideo\generate_video.py`
- **Implementation**:
  - Import all modules from `src/`
  - Main flow:
    1. Parse CLI arguments
    2. Encode images
    3. Read prompt content
    4. Call API
    5. Generate output path
    6. Save video
    7. Print success message
  - Error handling:
    - Catch `InvalidImageError` → Exit 1
    - Catch `APIError` → Exit 2
    - Catch network errors → Exit 3
    - Catch `SaveError` → Exit 4
    - Use `rich.console` for colored output
  - Logging with `logging` module
- **Success Criteria**:
  - Successful run exits with code 0
  - Errors exit with correct codes (1-4)
  - User sees clear messages
  - Video saved to output directory
- **Dependencies**: All Phase 1 tasks, Task 2.1

---

### Phase 3: Testing and Documentation

#### Task 3.1: Unit Tests
- **Complexity**: Medium
- **Files**:
  - `D:\0code\0toys\GenerateVideo\tests\test_encoder.py`
  - `D:\0code\0toys\GenerateVideo\tests\test_video_saver.py`
  - `D:\0code\0toys\GenerateVideo\tests\test_cli.py`
- **Implementation**:
  - Test image encoding (valid/invalid formats, sizes)
  - Test filename generation (uniqueness, format)
  - Test argument parsing (missing required args)
  - Use `pytest` fixtures for temp files
  - Mock API calls with `unittest.mock`
- **Success Criteria**:
  - `pytest` runs successfully
  - Coverage > 70% for core modules
- **Dependencies**: Task 2.2

#### Task 3.2: Integration Test
- **Complexity**: Complex
- **File**: `D:\0code\0toys\GenerateVideo\tests\test_integration.py`
- **Implementation**:
  - Mock `httpx` client to simulate API response
  - Test full workflow: CLI → Encode → API → Save
  - Verify output file creation
  - Test error paths (missing files, API errors)
- **Success Criteria**:
  - End-to-end test passes
  - Mock API returns test video data
  - Output file verified
- **Dependencies**: Task 3.1

#### Task 3.3: Example Files
- **Complexity**: Simple
- **Files**:
  - `D:\0code\0toys\GenerateVideo\examples\sample_prompt.txt`
  - `D:\0code\0toys\GenerateVideo\examples\sample_images\test1.jpg` (placeholder)
  - `D:\0code\0toys\GenerateVideo\examples\sample_images\test2.jpg` (placeholder)
- **Content**:
  - `sample_prompt.txt`: "A smooth transition from a calm ocean to a bustling cityscape."
- **Success Criteria**: Example files exist
- **Dependencies**: None

#### Task 3.4: README Documentation
- **Complexity**: Medium
- **File**: `D:\0code\0toys\GenerateVideo\README.md`
- **Sections**:
  1. Overview
  2. Requirements
  3. Installation
  4. Usage
  5. Options
  6. Output
  7. Error Codes
  8. Examples
  9. Troubleshooting
- **Success Criteria**:
  - All sections present
  - Code examples work
  - Clear for new users
- **Dependencies**: Task 2.2, Task 3.3

---

## Dependency Graph

```
Phase 0: Foundation
  0.1 (venv) → 0.2 (dirs) → 0.3 (requirements.txt) → 0.4 (install)

Phase 1: Core Modules
  1.1 (config.py)
    ↓
  1.2 (errors.py)
    ↓
  1.3 (encoder.py) ─┐
  1.4 (video_saver.py) ─┤
    ↓                   │
  1.5 (api_client.py) ←┘

Phase 2: CLI
  2.1 (cli.py) ─┐
                ├→ 2.2 (generate_video.py)
  Phase 1 ──────┘

Phase 3: Testing & Docs
  2.2 → 3.1 (unit tests) → 3.2 (integration tests)
  None → 3.3 (examples)
  2.2 + 3.3 → 3.4 (README.md)
```

---

## Execution Strategy

**Parallelization Opportunities**:
- Phase 1: Tasks 1.3 and 1.4 can run in parallel (both depend only on 1.2)
- Phase 3: Tasks 3.1 and 3.3 can run in parallel

**Critical Path**: 0.1 → 0.2 → 0.3 → 0.4 → 1.1 → 1.2 → 1.3 → 1.5 → 2.1 → 2.2

---

**PLAN STATUS**: READY FOR EXECUTION
