import logging
from pathlib import Path

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
    "--episode-id", "episode_ids", multiple=True, required=True,
    help="Episode ID(s) to transcribe (repeatable).",
)
@click.option("--force", is_flag=True, default=False, help="Re-transcribe even if file exists.")
@click.pass_context
def transcribe(ctx: click.Context, episode_ids: tuple[str, ...], force: bool) -> None:
    """Transcribe audio for specified episodes via Whisper API."""
    from btcedu.core.transcriber import transcribe_episode

    settings = ctx.obj["settings"]
    session = ctx.obj["session_factory"]()
    try:
        for eid in episode_ids:
            try:
                path = transcribe_episode(session, eid, settings, force=force)
                click.echo(f"[OK] {eid} -> {path}")
            except Exception as e:
                click.echo(f"[FAIL] {eid}: {e}", err=True)
    finally:
        session.close()


@cli.command()
@click.option(
    "--episode-id", "episode_ids", multiple=True, required=True,
    help="Episode ID(s) to chunk (repeatable).",
)
@click.option("--force", is_flag=True, default=False, help="Re-chunk even if file exists.")
@click.pass_context
def chunk(ctx: click.Context, episode_ids: tuple[str, ...], force: bool) -> None:
    """Chunk transcripts for specified episodes."""
    from btcedu.core.transcriber import chunk_episode

    settings = ctx.obj["settings"]
    session = ctx.obj["session_factory"]()
    try:
        for eid in episode_ids:
            try:
                count = chunk_episode(session, eid, settings, force=force)
                click.echo(f"[OK] {eid} -> {count} chunks")
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
    from btcedu.core.transcriber import chunk_episode, transcribe_episode

    settings = ctx.obj["settings"]
    session = ctx.obj["session_factory"]()
    try:
        if episode_ids:
            episodes = (
                session.query(Episode)
                .filter(Episode.episode_id.in_(episode_ids))
                .all()
            )
        else:
            episodes = (
                session.query(Episode)
                .filter(
                    Episode.status.in_([
                        EpisodeStatus.NEW,
                        EpisodeStatus.DOWNLOADED,
                        EpisodeStatus.TRANSCRIBED,
                        EpisodeStatus.CHUNKED,
                    ])
                )
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

            # Transcribe if needed
            if ep.status == EpisodeStatus.DOWNLOADED and (
                stage is None or stage == "transcribe"
            ):
                try:
                    path = transcribe_episode(session, ep.episode_id, settings)
                    click.echo(f"  Transcribed -> {path}")
                except Exception as e:
                    click.echo(f"  Transcribe failed: {e}", err=True)
                    continue

            # Chunk if needed
            if ep.status == EpisodeStatus.TRANSCRIBED and (
                stage is None or stage == "chunk"
            ):
                try:
                    count = chunk_episode(session, ep.episode_id, settings)
                    click.echo(f"  Chunked -> {count} chunks")
                except Exception as e:
                    click.echo(f"  Chunk failed: {e}", err=True)
                    continue

            # Generate if needed
            if ep.status == EpisodeStatus.CHUNKED and (
                stage is None or stage == "generate"
            ):
                try:
                    from btcedu.core.generator import generate_content

                    gen = generate_content(session, ep.episode_id, settings)
                    click.echo(
                        f"  Generated -> {len(gen.artifacts)} artifacts (${gen.total_cost_usd:.4f})"
                    )
                except Exception as e:
                    click.echo(f"  Generate failed: {e}", err=True)
                    continue
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
            click.echo(
                f"  [{ep.status.value:<12}] {ep.episode_id}  {pub}  {ep.title[:60]}"
            )
    finally:
        session.close()


@cli.command()
@click.option(
    "--episode-id", "episode_ids", multiple=True, required=True,
    help="Episode ID(s) to generate content for (repeatable).",
)
@click.option("--force", is_flag=True, default=False, help="Regenerate even if outputs exist.")
@click.option("--top-k", type=int, default=16, help="Number of chunks to retrieve for context.")
@click.pass_context
def generate(ctx: click.Context, episode_ids: tuple[str, ...], force: bool, top_k: int) -> None:
    """Generate Turkish content package for CHUNKED episodes."""
    from btcedu.core.generator import generate_content

    settings = ctx.obj["settings"]
    session = ctx.obj["session_factory"]()
    try:
        for eid in episode_ids:
            try:
                result = generate_content(session, eid, settings, force=force, top_k=top_k)
                click.echo(
                    f"[OK] {eid} -> {len(result.artifacts)} artifacts "
                    f"(${result.total_cost_usd:.4f})"
                )
            except Exception as e:
                click.echo(f"[FAIL] {eid}: {e}", err=True)
    finally:
        session.close()


@cli.command()
@click.option("--episode-id", "episode_id", type=str, default=None, help="Filter by episode ID")
@click.pass_context
def cost(ctx: click.Context, episode_id: str | None) -> None:
    """Show API usage costs from PipelineRun records."""
    from sqlalchemy import func

    from btcedu.models.episode import PipelineRun

    session = ctx.obj["session_factory"]()
    try:
        query = session.query(
            PipelineRun.stage,
            func.count().label("runs"),
            func.sum(PipelineRun.input_tokens).label("input_tokens"),
            func.sum(PipelineRun.output_tokens).label("output_tokens"),
            func.sum(PipelineRun.estimated_cost_usd).label("total_cost"),
        )

        if episode_id:
            ep = session.query(Episode).filter(Episode.episode_id == episode_id).first()
            if not ep:
                click.echo(f"Episode not found: {episode_id}")
                return
            query = query.filter(PipelineRun.episode_id == ep.id)

        rows = query.group_by(PipelineRun.stage).all()

        if not rows:
            click.echo("No pipeline runs recorded yet.")
            return

        click.echo("=== API Usage Costs ===")
        grand_total = 0.0
        for row in rows:
            cost_val = row.total_cost or 0.0
            grand_total += cost_val
            click.echo(
                f"  {row.stage.value:<12} "
                f"runs={row.runs}  "
                f"in={row.input_tokens or 0:>8}  "
                f"out={row.output_tokens or 0:>8}  "
                f"${cost_val:.4f}"
            )
        click.echo(f"  {'TOTAL':<12} ${grand_total:.4f}")
    finally:
        session.close()


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
