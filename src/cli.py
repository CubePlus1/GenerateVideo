"""Command-line argument parsing for video generation."""
import argparse
import sys
from pathlib import Path

from src.config import DEFAULT_OUTPUT_DIR


def parse_args() -> argparse.Namespace:
    """Parse and validate command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments with:
            - image1 (Path): Path to first image
            - image2 (Path): Path to second image
            - prompt_text (str): Content of prompt file
            - output_dir (Path): Output directory path

    Exits:
        SystemExit(1): If required files don't exist
    """
    parser = argparse.ArgumentParser(
        description="Generate video from two images using AI"
    )

    parser.add_argument(
        "-img1", "--image1",
        required=True,
        help="Path to the first image file"
    )

    parser.add_argument(
        "-img2", "--image2",
        required=True,
        help="Path to the second image file"
    )

    parser.add_argument(
        "-p", "--prompt",
        required=True,
        help="Path to the text file containing the prompt"
    )

    parser.add_argument(
        "-o", "--output",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for generated video (default: {DEFAULT_OUTPUT_DIR})"
    )

    args = parser.parse_args()

    # Convert paths to Path objects
    image1_path = Path(args.image1)
    image2_path = Path(args.image2)
    prompt_path = Path(args.prompt)
    output_path = Path(args.output)

    # Validate image files exist
    if not image1_path.exists():
        print(f"Error: First image file not found: {image1_path}", file=sys.stderr)
        sys.exit(1)

    if not image2_path.exists():
        print(f"Error: Second image file not found: {image2_path}", file=sys.stderr)
        sys.exit(1)

    # Validate prompt file exists
    if not prompt_path.exists():
        print(f"Error: Prompt file not found: {prompt_path}", file=sys.stderr)
        sys.exit(1)

    # Read prompt file content
    try:
        prompt_text = prompt_path.read_text(encoding='utf-8').strip()
        if not prompt_text:
            print(f"Error: Prompt file is empty: {prompt_path}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to read prompt file: {e}", file=sys.stderr)
        sys.exit(1)

    # Create new namespace with validated data
    validated_args = argparse.Namespace(
        image1=image1_path,
        image2=image2_path,
        prompt_text=prompt_text,
        output_dir=output_path
    )

    return validated_args
