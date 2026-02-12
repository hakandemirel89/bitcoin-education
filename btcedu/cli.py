import click

from btcedu.config import get_settings
from btcedu.db import init_db
from btcedu.models.episode import EpisodeStatus, PipelineStage


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """btcedu - Bitcoin Education Automation Pipeline"""
    ctx.ensure_object(dict)
    ctx.obj["settings"] = get_settings()


@cli.command()
@click.pass_context
def detect(ctx: click.Context) -> None:
    """Check YouTube feed for new episodes."""
    click.echo("Checking feed for new episodes...")
    click.echo("(Not yet implemented)")


@cli.command()
@click.option("--episode-id", type=int, default=None, help="Process specific episode")
@click.option(
    "--stage",
    type=click.Choice([s.value for s in PipelineStage]),
    default=None,
    help="Run only this stage",
)
@click.pass_context
def run(ctx: click.Context, episode_id: int | None, stage: str | None) -> None:
    """Run the content generation pipeline."""
    if episode_id and stage:
        click.echo(f"Running stage '{stage}' for episode {episode_id}...")
    elif episode_id:
        click.echo(f"Running full pipeline for episode {episode_id}...")
    else:
        click.echo("Running full pipeline for all pending episodes...")
    click.echo("(Not yet implemented)")


@cli.command()
@click.option("--episode-id", type=int, default=None, help="Show status for specific episode")
@click.pass_context
def status(ctx: click.Context, episode_id: int | None) -> None:
    """Show pipeline status for episodes."""
    if episode_id:
        click.echo(f"Status for episode {episode_id}:")
    else:
        click.echo("Pipeline status for all episodes:")
    click.echo("(Not yet implemented)")


@cli.command()
@click.option("--episode-id", type=int, required=True, help="Episode to reprocess")
@click.option(
    "--from",
    "from_stage",
    type=click.Choice([s.value for s in PipelineStage]),
    default="detect",
    help="Reprocess from this stage",
)
@click.pass_context
def reprocess(ctx: click.Context, episode_id: int, from_stage: str) -> None:
    """Reprocess an episode from a specific stage."""
    click.echo(f"Reprocessing episode {episode_id} from stage '{from_stage}'...")
    click.echo("(Not yet implemented)")


@cli.command()
@click.option("--episode-id", type=int, default=None, help="Show cost for specific episode")
@click.pass_context
def cost(ctx: click.Context, episode_id: int | None) -> None:
    """Show API usage costs."""
    if episode_id:
        click.echo(f"Cost for episode {episode_id}:")
    else:
        click.echo("Total API costs:")
    click.echo("(Not yet implemented)")


@cli.command(name="init-db")
@click.pass_context
def init_db_cmd(ctx: click.Context) -> None:
    """Initialize the database (create tables)."""
    settings = ctx.obj["settings"]
    init_db(settings.database_url)
    click.echo("Database initialized successfully.")
