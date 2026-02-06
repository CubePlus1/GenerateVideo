"""Text-to-Video (T2V) CLI subcommand."""

import click
from pathlib import Path
from rich.console import Console

from src.models.catalog import ModelCatalog
from src.models.selector import ModelSelector
from src import api_client, video_saver
from src.errors import ModelNotFoundError, InvalidPromptError

console = Console()


@click.command()
@click.option("-p", "--prompt", required=True, help="Text prompt or path to .txt file")
@click.option("-m", "--model", default=None, help="Model ID (default: auto-select)")
@click.option("-o", "--output", type=click.Path(), default="./output/", help="Output directory")
def t2v(prompt, model, output):
    """Generate video from text prompt"""

    try:
        # 1. Load prompt (from string or file)
        prompt_path = Path(prompt)
        if prompt_path.exists() and prompt_path.suffix == ".txt":
            prompt_text = prompt_path.read_text(encoding="utf-8").strip()
            console.print(f"[cyan]Loaded prompt from: {prompt_path}[/cyan]")
        else:
            prompt_text = prompt

        if not prompt_text:
            raise InvalidPromptError("Prompt cannot be empty")

        # 2. Select model
        catalog = ModelCatalog()
        selector = ModelSelector(catalog)
        model_id = selector.select_model(mode="t2v", manual_model=model)

        console.print(f"[cyan]Using model: {model_id}[/cyan]")
        console.print(f"[cyan]Generating video from text...[/cyan]")

        # 3. Call API (T2V mode - no images)
        video_bytes = api_client.generate_video(
            img1_b64=None,
            img2_b64=None,
            prompt=prompt_text,
            model=model_id
        )

        # 4. Save video
        console.print("[cyan]Saving video...[/cyan]")
        output_dir = Path(output)
        output_path = video_saver.generate_output_path(output_dir)
        video_saver.save_video_stream(video_bytes, output_path)

        console.print(f"[green]✓ Video saved to: {output_path}[/green]")

    except ModelNotFoundError as e:
        console.print(f"[red]Model Error: {e}[/red]")
        raise click.Abort()
    except InvalidPromptError as e:
        console.print(f"[red]Prompt Error: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()
