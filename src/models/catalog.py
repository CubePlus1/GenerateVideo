"""Model catalog for video generation models."""

from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Optional

from ..errors import ModelNotFoundError


@dataclass
class ModelInfo:
    """Information about a video generation model."""
    id: str
    name: str
    category: str  # "t2v" | "i2v" | "r2v"
    description: str
    features: list[str] = field(default_factory=list)
    recommended: bool = False


class ModelCatalog:
    """Reads and queries model.json catalog."""

    def __init__(self, catalog_path: Path = Path("output/model.json")):
        """Initialize catalog from model.json file.

        Args:
            catalog_path: Path to model.json file
        """
        self.models: dict[str, ModelInfo] = {}
        self._load_catalog(catalog_path)

    def _load_catalog(self, path: Path):
        """Load and parse model.json.

        Args:
            path: Path to model.json file

        Raises:
            FileNotFoundError: If model.json doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Parse T2V models (text-to-video)
        t2v_section = data.get("video_generation_text_to_video", {})
        self._parse_t2v_models(t2v_section)

        # Parse I2V models (image-to-video)
        i2v_section = data.get("video_generation_image_to_video", {})
        self._parse_i2v_models(i2v_section)

        # Parse R2V models (reference-to-video)
        r2v_section = data.get("video_generation_reference_to_video", {})
        self._parse_r2v_models(r2v_section)

    def _parse_t2v_models(self, section: dict):
        """Parse text-to-video models from JSON section."""
        description = section.get("description", "")
        veo_versions = section.get("veo_versions", {})

        for version_key, version_data in veo_versions.items():
            models = version_data.get("models", [])
            for model in models:
                model_id = model.get("id")
                if not model_id:
                    continue

                features = []
                if model.get("resolution"):
                    features.append(f"Resolution: {model['resolution']}")
                if model.get("speed"):
                    features.append(f"Speed: {model['speed']}")
                if model.get("orientation"):
                    features.append(f"Orientation: {model['orientation']}")

                self.models[model_id] = ModelInfo(
                    id=model_id,
                    name=model.get("name", model_id),
                    category="t2v",
                    description=description,
                    features=features,
                    recommended=model.get("recommended", False)
                )

    def _parse_i2v_models(self, section: dict):
        """Parse image-to-video models from JSON section."""
        description = section.get("description", "")
        veo_versions = section.get("veo_versions", {})

        for version_key, version_data in veo_versions.items():
            models = version_data.get("models", [])
            for model in models:
                model_id = model.get("id")
                if not model_id:
                    continue

                features = []
                if model.get("features"):
                    features.extend(model["features"])
                if model.get("resolution"):
                    features.append(f"Resolution: {model['resolution']}")
                if model.get("speed"):
                    features.append(f"Speed: {model['speed']}")
                if model.get("orientation"):
                    features.append(f"Orientation: {model['orientation']}")

                self.models[model_id] = ModelInfo(
                    id=model_id,
                    name=model.get("name", model_id),
                    category="i2v",
                    description=description,
                    features=features,
                    recommended=model.get("recommended", False)
                )

    def _parse_r2v_models(self, section: dict):
        """Parse reference-to-video models from JSON section."""
        description = section.get("description", "")
        models = section.get("models", [])

        for model in models:
            model_id = model.get("id")
            if not model_id:
                continue

            features = []
            if model.get("resolution"):
                features.append(f"Resolution: {model['resolution']}")
            if model.get("speed"):
                features.append(f"Speed: {model['speed']}")

            self.models[model_id] = ModelInfo(
                id=model_id,
                name=model.get("name", model_id),
                category="r2v",
                description=description,
                features=features,
                recommended=False
            )

    def get_model(self, model_id: str) -> ModelInfo:
        """Get model by ID.

        Args:
            model_id: Model identifier

        Returns:
            ModelInfo object

        Raises:
            ModelNotFoundError: If model doesn't exist in catalog
        """
        if model_id not in self.models:
            raise ModelNotFoundError(
                f"Model '{model_id}' not found in catalog. "
                f"Available models: {', '.join(sorted(self.models.keys()))}"
            )
        return self.models[model_id]

    def list_models(self, filter_category: Optional[str] = None) -> list[ModelInfo]:
        """List all models, optionally filtered by category.

        Args:
            filter_category: Optional category filter ("t2v", "i2v", "r2v")

        Returns:
            List of ModelInfo objects
        """
        if filter_category:
            return [
                model for model in self.models.values()
                if model.category == filter_category
            ]
        return list(self.models.values())

    def get_recommended(self, category: str) -> ModelInfo:
        """Get recommended model for category.

        Args:
            category: Model category ("t2v", "i2v", "r2v")

        Returns:
            Recommended ModelInfo object

        Raises:
            ModelNotFoundError: If no recommended model found for category
        """
        recommended = [
            model for model in self.models.values()
            if model.category == category and model.recommended
        ]

        if not recommended:
            raise ModelNotFoundError(
                f"No recommended model found for category '{category}'"
            )

        return recommended[0]
