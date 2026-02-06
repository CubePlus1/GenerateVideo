"""Unit tests for model catalog and selector."""

import pytest
from pathlib import Path
from src.models.catalog import ModelCatalog, ModelInfo
from src.models.selector import ModelSelector
from src.errors import ModelNotFoundError


def test_catalog_loads():
    """Test catalog loads model.json successfully"""
    catalog = ModelCatalog()
    assert len(catalog.models) > 0


def test_get_model_by_id():
    """Test retrieving model by ID"""
    catalog = ModelCatalog()
    model = catalog.get_model("veo_3_1_i2v_s_fast_fl")
    assert model.id == "veo_3_1_i2v_s_fast_fl"
    assert model.category == "i2v"


def test_model_not_found():
    """Test ModelNotFoundError raised for invalid ID"""
    catalog = ModelCatalog()
    with pytest.raises(ModelNotFoundError):
        catalog.get_model("invalid_model_id")


def test_filter_by_category():
    """Test filtering models by category"""
    catalog = ModelCatalog()
    i2v_models = catalog.list_models(filter_category="i2v")
    assert all(m.category == "i2v" for m in i2v_models)
    assert len(i2v_models) > 0


def test_selector_t2v_default():
    """Test auto-selection for T2V"""
    catalog = ModelCatalog()
    selector = ModelSelector(catalog)
    model_id = selector.select_model(mode="t2v")
    assert model_id == "veo_3_1_t2v_fast_landscape"


def test_selector_i2v_single_image():
    """Test auto-selection for I2V with 1 image"""
    catalog = ModelCatalog()
    selector = ModelSelector(catalog)
    model_id = selector.select_model(mode="i2v", image_count=1)
    assert model_id == "veo_3_1_i2v_s_landscape"


def test_selector_i2v_dual_image():
    """Test auto-selection for I2V with 2 images"""
    catalog = ModelCatalog()
    selector = ModelSelector(catalog)
    model_id = selector.select_model(mode="i2v", image_count=2)
    assert model_id == "veo_3_1_i2v_s_fast_fl"


def test_selector_manual_override():
    """Test manual model override with validation"""
    catalog = ModelCatalog()
    selector = ModelSelector(catalog)
    model_id = selector.select_model(mode="t2v", manual_model="veo_3_1_t2v_fast_portrait")
    assert model_id == "veo_3_1_t2v_fast_portrait"


def test_selector_invalid_manual():
    """Test invalid manual model raises error"""
    catalog = ModelCatalog()
    selector = ModelSelector(catalog)
    with pytest.raises(ModelNotFoundError):
        selector.select_model(mode="t2v", manual_model="nonexistent_model")
