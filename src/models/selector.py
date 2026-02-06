"""Model selection logic for video generation."""

from src.models.catalog import ModelCatalog
from src.errors import ModelNotFoundError


class ModelSelector:
    """Auto-selects appropriate model based on inputs."""

    def __init__(self, catalog: ModelCatalog):
        """Initialize selector with model catalog.

        Args:
            catalog: ModelCatalog instance for validation
        """
        self.catalog = catalog

    def select_model(
        self,
        mode: str,
        image_count: int = 0,
        manual_model: str | None = None,
        orientation: str = "landscape"
    ) -> str:
        """Select model based on mode and inputs.

        Args:
            mode: "t2v" (text-to-video) or "i2v" (image-to-video)
            image_count: Number of images (0 for t2v, 1-2 for i2v)
            manual_model: User-specified model ID (overrides auto-selection)
            orientation: "landscape" or "portrait"

        Returns:
            model_id: Validated model ID from catalog

        Raises:
            ModelNotFoundError: If manual_model is invalid
            ValueError: If mode or image_count is invalid
        """
        # If manual model specified, validate and return
        if manual_model:
            # Validate exists in catalog (raises ModelNotFoundError if not found)
            self.catalog.get_model(manual_model)
            return manual_model

        # Auto-selection logic
        if mode == "t2v":
            # Text-to-video: default landscape model
            if orientation == "portrait":
                return "veo_3_1_t2v_fast_portrait"
            else:
                return "veo_3_1_t2v_fast_landscape"

        elif mode == "i2v":
            if image_count == 1:
                # Single image: standard i2v
                if orientation == "portrait":
                    return "veo_3_1_i2v_s_portrait"
                else:
                    return "veo_3_1_i2v_s_landscape"

            elif image_count == 2:
                # Dual image: first-last frame model
                if orientation == "portrait":
                    return "veo_3_1_i2v_s_fast_portrait_fl"
                else:
                    return "veo_3_1_i2v_s_fast_fl"

            else:
                raise ValueError(
                    f"Invalid image_count for i2v: {image_count}. Expected 1 or 2."
                )

        else:
            raise ValueError(
                f"Invalid mode: {mode}. Expected 't2v' or 'i2v'."
            )
