"""CLI interface for ClipSort."""

from __future__ import annotations

import io
import logging
import sys
from pathlib import Path

import click

from clipsort import __version__
from clipsort.organizer import Organizer
from clipsort.parser import FilenameParser
from clipsort.reporter import Reporter
from clipsort.scanner import FileScanner


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """ClipSort — organize video clips into scene folders."""


@main.command()
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False))
@click.argument("output_dir", type=click.Path())
@click.option("--dry-run", is_flag=True, help="Preview without making changes.")
@click.option("--move", is_flag=True, help="Move files instead of copying.")
@click.option("--recursive", "-r", is_flag=True, help="Scan subdirectories.")
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging.")
@click.option("--report-file", type=click.Path(), default=None, help="Save report to file.")
def organize(
    input_dir: str,
    output_dir: str,
    dry_run: bool,
    move: bool,
    recursive: bool,
    verbose: bool,
    report_file: str | None,
) -> None:
    """Organize video clips from INPUT_DIR into scene folders in OUTPUT_DIR."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(message)s")

    scanner = FileScanner()
    parser = FilenameParser()
    organizer = Organizer()
    reporter = Reporter()

    # Scan
    files = scanner.scan(Path(input_dir), recursive=recursive)
    if not files:
        click.echo("No video files found.", err=True)
        sys.exit(1)

    click.echo(f"Found {len(files)} video file(s).")

    # Parse
    parsed = [(f, parser.parse(f.name)) for f in files]

    # Plan
    plan = organizer.plan(parsed, Path(output_dir))

    # Report
    if dry_run:
        click.echo("\n--- Dry Run ---")
        for source, dest in plan.mappings:
            click.echo(f"  {source.name} -> {dest.relative_to(Path(output_dir))}")
        if plan.unsorted:
            click.echo("  Unsorted:")
            for f in plan.unsorted:
                click.echo(f"    {f.name}")
        click.echo("--- End Dry Run ---\n")
    else:
        count = organizer.execute(plan, move=move)
        click.echo(f"\n{'Moved' if move else 'Copied'} {count} file(s).")

    click.echo("")
    buf = io.StringIO()
    reporter.report(plan, stream=buf)
    click.echo(buf.getvalue(), nl=False)

    if report_file:
        reporter.save(plan, Path(report_file))
        click.echo(f"\nReport saved to {report_file}")
