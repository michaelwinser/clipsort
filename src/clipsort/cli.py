"""CLI interface for ClipSort."""

from __future__ import annotations

import io
import logging
import sys
from pathlib import Path

import click

from clipsort import __version__
from clipsort.organizer import Organizer
from clipsort.parser import ClipInfo, FilenameParser
from clipsort.reporter import Reporter
from clipsort.scanner import FileScanner


@click.group(name="clipsort")
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


@main.command("qr-generate")
@click.option("--scene", type=int, default=None, help="Scene number (single mode).")
@click.option("--take", type=int, default=None, help="Take number (single mode).")
@click.option("--scenes", type=int, default=None, help="Number of scenes (batch mode).")
@click.option("--takes", type=int, default=None, help="Number of takes per scene (batch mode).")
@click.option("--project", type=str, default=None, help="Project name.")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output file path.")
def qr_generate(
    scene: int | None,
    take: int | None,
    scenes: int | None,
    takes: int | None,
    project: str | None,
    output: str | None,
) -> None:
    """Generate QR codes for clapper boards.

    Single mode: --scene N --take N  (outputs a PNG)
    Batch mode:  --scenes N --takes N (outputs a PDF sheet)
    """
    from clipsort.qr_generate import QRGenerator

    single = scene is not None or take is not None
    batch = scenes is not None or takes is not None

    if single and batch:
        raise click.UsageError("Cannot mix single (--scene/--take) and batch (--scenes/--takes).")
    if not single and not batch:
        raise click.UsageError("Provide --scene/--take (single) or --scenes/--takes (batch).")

    gen = QRGenerator()

    if single:
        if scene is None or take is None:
            raise click.UsageError("Single mode requires both --scene and --take.")
        out = Path(output) if output else Path(f"S{scene}T{take}.png")
        gen.generate_single(scene, take, project, out)
        click.echo(f"QR code saved to {out}")
    else:
        if scenes is None or takes is None:
            raise click.UsageError("Batch mode requires both --scenes and --takes.")
        out = Path(output) if output else Path("qr_sheet.pdf")
        gen.generate_sheet(scenes, takes, project, out)
        click.echo(f"QR sheet saved to {out}")


@main.command()
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False))
@click.argument("output_dir", type=click.Path())
@click.option("--dry-run", is_flag=True, help="Preview without making changes.")
@click.option("--move", is_flag=True, help="Move files instead of copying.")
@click.option("--recursive", "-r", is_flag=True, help="Scan subdirectories.")
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging.")
@click.option("--report-file", type=click.Path(), default=None, help="Save report to file.")
@click.option("--scan-seconds", type=int, default=10, help="Seconds to scan for QR codes.")
@click.option("--sample-rate", type=int, default=2, help="Frames per second to sample.")
def detect(
    input_dir: str,
    output_dir: str,
    dry_run: bool,
    move: bool,
    recursive: bool,
    verbose: bool,
    report_file: str | None,
    scan_seconds: int,
    sample_rate: int,
) -> None:
    """Detect scene info via QR codes (with filename fallback).

    Scans video files in INPUT_DIR for QR codes. Falls back to filename
    parsing for files without QR codes. Organizes into OUTPUT_DIR.
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(message)s")

    from clipsort.qr_detect import DetectionChain, QRDetector

    scanner = FileScanner()
    organizer = Organizer()
    reporter = Reporter()
    parser = FilenameParser()

    # Build detection chain: QR first, then filename fallback
    qr_detector = QRDetector(scan_seconds=scan_seconds, sample_rate=sample_rate)

    def filename_fallback(path: Path) -> ClipInfo | None:
        return parser.parse(path.name)

    chain = DetectionChain([qr_detector.detect, filename_fallback])

    # Scan
    files = scanner.scan(Path(input_dir), recursive=recursive)
    if not files:
        click.echo("No video files found.", err=True)
        sys.exit(1)

    click.echo(f"Found {len(files)} video file(s).")

    # Detect
    detected = [(f, chain.detect(f)) for f in files]

    # Plan
    plan = organizer.plan(detected, Path(output_dir))

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
