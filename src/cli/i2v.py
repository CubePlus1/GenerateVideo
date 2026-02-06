"""Image-to-Video (I2V) CLI subcommand."""

import click
from pathlib import Path
from rich.console import Console

from src.models.catalog import ModelCatalog
from src.models.selector import ModelSelector
from src import encoder, api_client, video_saver
from src.errors import ModelNotFoundError, InvalidPromptError, InvalidImageError

console = Console()


@click.command()
@click.option(
    "-i", "--image", "images",
    multiple=True,
    type=click.Path(exists=True),
    help="Input image(s). Use twice for 2 images: -i img1.jpg -i img2.jpg"
)
@click.option(
    "-p", "--prompt",
    required=True,
    help="Text prompt or path to .txt file"
)
@click.option(
    "-m", "--model",
    default=None,
    help="Model ID (overrides auto-selection)"
)
@click.option(
    "-o", "--output",
    type=click.Path(),
    default="./output/",
    help="Output directory"
)
def i2v(images, prompt, model, output):
    """Generate video from 1-2 images"""

    try:
        # 1. Validate image count
        if len(images) < 1 or len(images) > 2:
            raise InvalidImageError(f"Expected 1-2 images, got {len(images)}")

        # 2. Load prompt
        prompt_path = Path(prompt)
        if prompt_path.exists() and prompt_path.suffix == ".txt":
            prompt_text = prompt_path.read_text(encoding="utf-8").strip()
        else:
            prompt_text = prompt

        if not prompt_text:
            raise InvalidPromptError("Prompt cannot be empty")

        # 3. Select model (auto or manual)
        catalog = ModelCatalog()
        selector = ModelSelector(catalog)
        model_id = selector.select_model(
            mode="i2v",
            image_count=len(images),
            manual_model=model
        )

        console.print(f"[cyan]Using model: {model_id}[/cyan]")
        console.print(f"[cyan]Encoding {len(images)} image(s)...[/cyan]")

        # 4. Encode images
        img1_b64 = encoder.encode_image_to_base64(Path(images[0]))
        img2_b64 = encoder.encode_image_to_base64(Path(images[1])) if len(images) == 2 else None

        console.print("[cyan]Generating video...[/cyan]")

        # 5. Call API
        video_bytes = api_client.generate_video(
            prompt=prompt_text,
            model=model_id,
            img1_b64=img1_b64,
            img2_b64=img2_b64
        )

        # 6. Save video
        console.print("[cyan]Saving video...[/cyan]")
        output_dir = Path(output)
        output_path = video_saver.generate_output_path(output_dir)
        video_saver.save_video_stream(video_bytes, output_path)

        console.print(f"[green]✓ Video saved to: {output_path}[/green]")

    except (ModelNotFoundError, InvalidPromptError, InvalidImageError) as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Unexpected Error: {e}[/red]")
        raise click.Abort()
