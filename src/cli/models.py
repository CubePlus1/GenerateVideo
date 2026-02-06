import click
import json
from rich.console import Console
from rich.table import Table
from src.models.catalog import ModelCatalog

console = Console()

@click.command(name="models")
@click.option("--filter", type=click.Choice(["t2v", "i2v", "r2v"]), help="Filter by category")
@click.option("--format", type=click.Choice(["table", "json"]), default="table", help="Output format")
def list_models(filter, format):
    """List available video generation models"""

    try:
        catalog = ModelCatalog()
        models = catalog.list_models(filter_category=filter)

        if format == "json":
            # JSON output
            output = [
                {"id": m.id, "name": m.name, "category": m.category,
                 "recommended": m.recommended}
                for m in models
            ]
            console.print_json(data=output)
        else:
            # Table output
            table = Table(title=f"Available Models ({len(models)} total)")
            table.add_column("Model ID", style="cyan")
            table.add_column("Name", style="white")
            table.add_column("Category", style="yellow")
            table.add_column("Recommended", style="green")

            for model in models:
                table.add_row(
                    model.id,
                    model.name,
                    model.category,
                    "✓" if model.recommended else ""
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()
