import logging

import click

from btcedu.config import get_settings
from btcedu.db import get_session_factory, init_db
from btcedu.models.episode import Episode, EpisodeStatus, PipelineStage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """btcedu - Bitcoin Education Automation Pipeline"""
    ctx.ensure_object(dict)
    settings = get_settings()
    ctx.obj["settings"] = settings
    init_db(settings.database_url)
    ctx.obj["session_factory"] = get_session_factory(settings.database_url)


@cli.command()
@click.pass_context
def detect(ctx: click.Context) -> None:
    """Check feed for new episodes and insert into DB."""
    from btcedu.core.detector import detect_episodes

    settings = ctx.obj["settings"]
    session = ctx.obj["session_factory"]()
    try:
        result = detect_episodes(session, settings)
        click.echo(f"Found: {result.found}  New: {result.new}  Total in DB: {result.total}")
    finally:
        session.close()


@cli.command()
@click.option(
    "--episode-id", "episode_ids", multiple=True, required=True,
    help="Episode ID(s) to download (repeatable).",
)
@click.option("--force", is_flag=True, default=False, help="Re-download even if file exists.")
@click.pass_context
def download(ctx: click.Context, episode_ids: tuple[str, ...], force: bool) -> None:
    """Download audio for specified episodes."""
    from btcedu.core.detector import download_episode

    settings = ctx.obj["settings"]
    session = ctx.obj["session_factory"]()
    try:
        for eid in episode_ids:
            try:
                path = download_episode(session, eid, settings, force=force)
                click.echo(f"[OK] {eid} -> {path}")
            except Exception as e:
                click.echo(f"[FAIL] {eid}: {e}", err=True)
    finally:
        session.close()


@cli.command()
@click.option(
    "--episode-id", "episode_ids", multiple=True,
    help="Episode ID(s) to process (repeatable). If omitted, processes all NEW episodes.",
)
@click.option(
    "--stage",
    type=click.Choice([s.value for s in PipelineStage]),
    default=None,
    help="Run only this stage.",
)
@click.pass_context
def run(ctx: click.Context, episode_ids: tuple[str, ...], stage: str | None) -> None:
    """Run the content generation pipeline."""
    from btcedu.core.detector import download_episode

    settings = ctx.obj["settings"]
    session = ctx.obj["session_factory"]()
    try:
        # Resolve which episodes to process
        if episode_ids:
            episodes = (
                session.query(Episode)
                .filter(Episode.episode_id.in_(episode_ids))
                .all()
            )
        else:
            episodes = (
                session.query(Episode)
                .filter(Episode.status == EpisodeStatus.NEW)
                .all()
            )

        if not episodes:
            click.echo("No episodes to process.")
            return

        for ep in episodes:
            click.echo(f"Processing: {ep.episode_id} ({ep.title})")

            # Download if needed
            if ep.status == EpisodeStatus.NEW and (stage is None or stage == "download"):
                try:
                    path = download_episode(session, ep.episode_id, settings)
                    click.echo(f"  Downloaded -> {path}")
                except Exception as e:
                    click.echo(f"  Download failed: {e}", err=True)
                    continue

            # Future stages (transcribe, chunk, generate) will be added here
            if stage and stage != "download":
                click.echo(f"  Stage '{stage}' not yet implemented.")
    finally:
        session.close()


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show pipeline status: counts by status + last 10 episodes."""
    session = ctx.obj["session_factory"]()
    try:
        from sqlalchemy import func

        rows = (
            session.query(Episode.status, func.count())
            .group_by(Episode.status)
            .all()
        )
        total = sum(c for _, c in rows)
        click.echo(f"=== Episodes: {total} ===")
        for s, c in rows:
            click.echo(f"  {s.value:<14} {c}")

        # Last 10 episodes
        click.echo("")
        click.echo("--- Last 10 episodes ---")
        recent = (
            session.query(Episode)
            .order_by(Episode.detected_at.desc())
            .limit(10)
            .all()
        )
        if not recent:
            click.echo("  (none)")
        for ep in recent:
            pub = ep.published_at.strftime("%Y-%m-%d") if ep.published_at else "???"
            click.echo(f"  [{ep.status.value:<12}] {ep.episode_id}  {pub}  {ep.title[:60]}")
    finally:
        session.close()


@cli.command()
@click.option("--episode-id", type=int, default=None, help="Show cost for specific episode")
@click.pass_context
def cost(ctx: click.Context, episode_id: int | None) -> None:
    """Show API usage costs."""
    click.echo("(Not yet implemented — available after Phase 4)")


@cli.command()
@click.option("--episode-id", type=str, required=True, help="Episode to reprocess")
@click.option(
    "--from",
    "from_stage",
    type=click.Choice([s.value for s in PipelineStage]),
    default="detect",
    help="Reprocess from this stage",
)
@click.pass_context
def reprocess(ctx: click.Context, episode_id: str, from_stage: str) -> None:
    """Reprocess an episode from a specific stage."""
    click.echo(f"Reprocessing episode {episode_id} from stage '{from_stage}'...")
    click.echo("(Not yet implemented)")


@cli.command(name="init-db")
@click.pass_context
def init_db_cmd(ctx: click.Context) -> None:
    """Initialize the database (create tables)."""
    click.echo("Database initialized successfully.")
