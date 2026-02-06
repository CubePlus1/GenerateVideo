import click

from src.cli.i2v import i2v
from src.cli.models import list_models
from src.cli.t2v import t2v


@click.group()
@click.version_option(version="0.2.0")
def cli():
    """Unified video generation CLI - T2V and I2V

    Generate videos from text prompts or images using AI models.
    """
    pass


# Register subcommands
cli.add_command(i2v)
cli.add_command(list_models)
cli.add_command(t2v)


if __name__ == "__main__":
    cli()
