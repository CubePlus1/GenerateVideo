"""Integration tests for the genvideo CLI using Click's testing utilities."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import Mock, patch
from src.cli.main import cli


@pytest.fixture
def runner():
    """Create CLI test runner"""
    return CliRunner()


@pytest.fixture
def mock_api_response():
    """Mock API response with fake video data"""
    return b"fake_video_data"


def test_t2v_default_model(runner, mock_api_response):
    """Test T2V with default model selection"""
    with patch('src.api_client.generate_video', return_value=mock_api_response):
        result = runner.invoke(cli, ['t2v', '-p', 'test prompt'])
        assert result.exit_code == 0
        assert 'Video saved' in result.output


def test_t2v_manual_model(runner, mock_api_response):
    """Test T2V with manual model override"""
    with patch('src.api_client.generate_video', return_value=mock_api_response):
        result = runner.invoke(cli, ['t2v', '-p', 'test', '-m', 'veo_3_1_t2v_fast_portrait'])
        assert result.exit_code == 0


def test_i2v_single_image(runner, tmp_path, mock_api_response):
    """Test I2V with single image (auto-select)"""
    # Create temp image file
    img = tmp_path / "test.jpg"
    img.write_bytes(b"fake_image")

    with patch('src.encoder.encode_image_to_base64', return_value='base64data'):
        with patch('src.api_client.generate_video', return_value=mock_api_response):
            result = runner.invoke(cli, ['i2v', '-i', str(img), '-p', 'test'])
            assert result.exit_code == 0
            assert 'veo_3_1_i2v_s_landscape' in result.output or 'Video saved' in result.output


def test_i2v_dual_image(runner, tmp_path, mock_api_response):
    """Test I2V with dual images (first-last frame)"""
    img1 = tmp_path / "img1.jpg"
    img2 = tmp_path / "img2.jpg"
    img1.write_bytes(b"fake1")
    img2.write_bytes(b"fake2")

    with patch('src.encoder.encode_image_to_base64', return_value='base64data'):
        with patch('src.api_client.generate_video', return_value=mock_api_response):
            result = runner.invoke(cli, ['i2v', '-i', str(img1), '-i', str(img2), '-p', 'test'])
            assert result.exit_code == 0
            assert 'veo_3_1_i2v_s_fast_fl' in result.output or 'Video saved' in result.output


def test_models_list(runner):
    """Test models listing command"""
    result = runner.invoke(cli, ['models'])
    assert result.exit_code == 0
    assert 'veo' in result.output.lower()


def test_models_filter(runner):
    """Test models listing with category filter"""
    result = runner.invoke(cli, ['models', '--filter', 'i2v'])
    assert result.exit_code == 0


def test_invalid_model_error(runner):
    """Test error handling for invalid model"""
    result = runner.invoke(cli, ['t2v', '-p', 'test', '-m', 'nonexistent_model'])
    assert result.exit_code != 0
    assert 'Error' in result.output or 'not found' in result.output.lower()


def test_missing_prompt_error(runner):
    """Test error handling for missing prompt"""
    result = runner.invoke(cli, ['t2v'])
    assert result.exit_code != 0


def test_invalid_image_count(runner, tmp_path):
    """Test I2V rejects more than 2 images"""
    imgs = [tmp_path / f"img{i}.jpg" for i in range(3)]
    for img in imgs:
        img.write_bytes(b"fake")

    result = runner.invoke(cli, ['i2v', '-i', str(imgs[0]), '-i', str(imgs[1]), '-i', str(imgs[2]), '-p', 'test'])
    assert result.exit_code != 0
    assert 'Expected 1-2 images' in result.output or 'Error' in result.output
