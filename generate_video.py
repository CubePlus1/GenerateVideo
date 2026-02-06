"""
Main entry point for video generation tool.

Wires together all modules: CLI parsing, image encoding, API communication,
and video saving with comprehensive error handling.
"""

import sys
import logging
from rich.console import Console

from src import cli, encoder, api_client, video_saver, errors


def main():
    """Main execution flow with error handling."""
    # Setup logging and rich console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console = Console()

    try:
        # Parse CLI arguments
        args = cli.parse_args()

        # Encode images to base64
        console.print("[cyan]Encoding images...[/cyan]")
        img1_b64 = encoder.encode_image_to_base64(args.image1)
        img2_b64 = encoder.encode_image_to_base64(args.image2)

        # Call API to generate video
        console.print("[cyan]Generating video...[/cyan]")
        video_bytes = api_client.generate_video(img1_b64, img2_b64, args.prompt_text)

        # Save video to output directory
        console.print("[cyan]Saving video...[/cyan]")
        output_path = video_saver.generate_output_path(args.output_dir)
        video_saver.save_video_stream(video_bytes, output_path)

        # Success message
        console.print(f"[green]✓ Video saved to: {output_path}[/green]")
        sys.exit(0)

    except errors.InvalidImageError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except errors.APIError as e:
        console.print(f"[red]API Error: {e}[/red]")
        sys.exit(2)
    except (ConnectionError, TimeoutError) as e:
        console.print(f"[red]Network Error: {e}[/red]")
        sys.exit(3)
    except errors.SaveError as e:
        console.print(f"[red]Save Error: {e}[/red]")
        sys.exit(4)
    except Exception as e:
        console.print(f"[red]Unexpected Error: {e}[/red]")
        logging.exception("Unexpected error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()
