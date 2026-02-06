"""Custom exceptions for video generation."""

class VideoGenerationError(Exception):
    """Base exception for video generation errors."""
    pass

class InvalidImageError(VideoGenerationError):
    """Raised when image file is invalid, missing, or oversized."""
    pass

class APIError(VideoGenerationError):
    """Raised when API communication fails (4xx/5xx responses)."""
    pass

class StreamingError(VideoGenerationError):
    """Raised when streaming response parsing fails."""
    pass

class SaveError(VideoGenerationError):
    """Raised when video file cannot be written to disk."""
    pass

class ModelNotFoundError(VideoGenerationError):
    """Raised when requested model doesn't exist in catalog."""
    pass

class InvalidPromptError(VideoGenerationError):
    """Raised when prompt is missing or invalid."""
    pass
