# Unified Video Generation CLI - Product Specification

**Project**: Python CLI tool for T2V and I2V video generation
**Date**: 2026-02-07
**Status**: PLANNING

---

## Executive Summary

Create a unified CLI tool `genvideo` that supports:
1. **Text-to-Video (T2V)** - Generate videos from text prompts
2. **Image-to-Video (I2V)** - Generate videos from 1-2 images
3. **Model Selection** - Auto-select or manually choose models from catalog

---

## Functional Requirements

### 1. Text-to-Video (T2V)
- Command: `genvideo t2v --prompt "text" --model veo_3_1_t2v_fast_landscape`
- Input: Text prompt (string or file path)
- Output: MP4 video file
- Default model: `veo_3_1_t2v_fast_landscape`

### 2. Image-to-Video (I2V)
- Command: `genvideo i2v -i img1.jpg [-i img2.jpg] --prompt "text"`
- Input: 1-2 images + text prompt
- Auto-selection:
  - 1 image → `veo_3_1_i2v_s_landscape`
  - 2 images → `veo_3_1_i2v_s_fast_fl` (first-last frame)
- Manual override: `--model <model_id>`

### 3. Model Catalog
- Command: `genvideo models [--filter t2v|i2v]`
- Source: `D:\0code\0toys\GenerateVideo\output\model.json`
- Display: Model IDs, names, descriptions

---

## Technical Architecture

### Technology Stack
- **CLI Framework**: Click (subcommands)
- **Config**: Pydantic Settings
- **HTTP**: httpx (existing)
- **UI**: rich (existing)

### Code Reuse (70%)
- ✅ `src/encoder.py` - Image encoding
- ✅ `src/api_client.py` - API communication
- ✅ `src/video_saver.py` - Video saving
- ✅ `src/errors.py` - Exception handling

### New Components (30%)
- `src/cli/` - Click-based CLI
  - `main.py` - Entry point
  - `t2v.py` - T2V subcommand
  - `i2v.py` - I2V subcommand
  - `models.py` - Model listing
- `src/models/` - Model management
  - `catalog.py` - Read model.json
  - `selector.py` - Auto-selection logic

---

## File Structure

```
GenerateVideo/
├── pyproject.toml           [MODIFY] Add click, pydantic
├── src/
│   ├── config.py            [REPLACE] Pydantic Settings
│   ├── errors.py            [EXTEND] Add ModelNotFoundError
│   ├── api_client.py        [ADAPT] Dynamic model parameter
│   ├── encoder.py           [REUSE]
│   ├── video_saver.py       [REUSE]
│   ├── cli/                 [NEW]
│   │   ├── main.py
│   │   ├── t2v.py
│   │   ├── i2v.py
│   │   └── models.py
│   └── models/              [NEW]
│       ├── catalog.py
│       └── selector.py
└── generate_video.py        [KEEP] Legacy wrapper
```

---

## Implementation Phases

### Phase 1: Foundation
1. Update pyproject.toml dependencies
2. Replace config.py with Pydantic Settings
3. Extend errors.py with ModelNotFoundError

### Phase 2: Model Management
1. Create ModelCatalog (read model.json)
2. Create ModelSelector (auto-selection)
3. Unit tests

### Phase 3: CLI Implementation
1. Create Click command structure
2. Implement t2v subcommand
3. Implement i2v subcommand
4. Implement models subcommand

### Phase 4: Integration
1. Adapt api_client.py for dynamic models
2. Wire CLI → Model Selection → API → Saver
3. Integration tests

### Phase 5: Polish
1. Rich progress bars
2. Error messages
3. Documentation

---

## Acceptance Criteria

### T2V Success
- ✅ `genvideo t2v -p "cat" -m veo_3_1_t2v_fast_landscape`
- ✅ Generates MP4 video
- ✅ Clear error messages on failure

### I2V Single Image
- ✅ `genvideo i2v -i img.jpg -p "text"`
- ✅ Auto-selects `veo_3_1_i2v_s_landscape`
- ✅ Generates video

### I2V Dual Image
- ✅ `genvideo i2v -i img1.jpg -i img2.jpg -p "text"`
- ✅ Auto-selects `veo_3_1_i2v_s_fast_fl`
- ✅ Generates transition video

### Model Listing
- ✅ `genvideo models --filter i2v`
- ✅ Shows filtered model list
- ✅ Marks recommended models

---

## Windows Compliance (CLAUDE.md)

- ✅ Virtual environment installation
- ✅ pathlib for all paths
- ✅ No `> nul` file operations
- ✅ Proper path quoting

---

**SPECIFICATION COMPLETE - READY FOR PLANNING**
