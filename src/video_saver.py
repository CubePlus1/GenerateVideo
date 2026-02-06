"""Video saving functionality with timestamp-based naming."""

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from src.errors import SaveError


def generate_output_path(output_dir: Path) -> Path:
    """Generate a timestamped output path for the video file.

    Creates the output directory if it doesn't exist and generates a unique
    filename with format: video_YYYYMMDD_HHMMSS_{uuid}.mp4

    Args:
        output_dir: Directory where the video file should be saved.

    Returns:
        Full path to the output video file.

    Example:
        >>> output_dir = Path("outputs")
        >>> path = generate_output_path(output_dir)
        >>> print(path.name)
        video_20260207_143052_a3f2b1c4.mp4
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid4().hex[:8]
    filename = f"video_{timestamp}_{unique_id}.mp4"

    return output_dir / filename


def save_video_stream(stream_content: bytes, output_path: Path) -> None:
    """Save binary video content to disk.

    Writes the video stream to the specified path. If an error occurs during
    writing, the partial file is cleaned up automatically.

    Args:
        stream_content: Binary content of the video file.
        output_path: Path where the video should be saved.

    Raises:
        SaveError: If writing to disk fails.

    Example:
        >>> content = b"video_binary_data"
        >>> path = Path("output/video.mp4")
        >>> save_video_stream(content, path)
    """
    try:
        output_path.write_bytes(stream_content)
    except (OSError, IOError) as e:
        # Clean up partial file on failure (Windows-safe)
        output_path.unlink(missing_ok=True)
        raise SaveError(f"Failed to save video to {output_path}: {e}") from e
