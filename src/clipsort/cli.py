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
@click.option(
    "--mode",
    type=click.Choice(["auto", "qr", "ocr"]),
    default="auto",
    help="Detection mode: auto (QR→OCR→filename), qr, or ocr.",
)
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
    mode: str,
) -> None:
    """Detect scene info via QR codes and/or OCR (with filename fallback).

    Scans video files in INPUT_DIR for scene information using the selected
    detection mode. Falls back to filename parsing. Organizes into OUTPUT_DIR.
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(message)s")

    from clipsort.qr_detect import DetectionChain, QRDetector

    scanner = FileScanner()
    organizer = Organizer()
    reporter = Reporter()
    parser = FilenameParser()

    def filename_fallback(path: Path) -> ClipInfo | None:
        return parser.parse(path.name)

    # Build detection chain based on mode
    detectors = []

    if mode in ("auto", "qr"):
        qr_detector = QRDetector(scan_seconds=scan_seconds, sample_rate=sample_rate)
        detectors.append(qr_detector.detect)

    if mode in ("auto", "ocr"):
        from clipsort.clapper_detect import ClapperDetector
        from clipsort.ocr import TesseractEngine

        ocr_engine = TesseractEngine()
        clapper_detector = ClapperDetector(
            ocr_engine=ocr_engine, scan_seconds=scan_seconds, sample_rate=sample_rate
        )
        detectors.append(clapper_detector.detect)

    detectors.append(filename_fallback)
    chain = DetectionChain(detectors)

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


@main.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_dir", type=click.Path())
@click.option(
    "--mode",
    type=click.Choice(["auto", "qr", "ocr", "audio"]),
    default="auto",
    help="Detection mode (default: auto).",
)
@click.option("--sample-rate", type=float, default=1.0, help="Frames/sec to sample (default: 1.0).")
@click.option("--precise", is_flag=True, help="Re-encode for frame-accurate cuts.")
@click.option("--skip-preamble", is_flag=True, help="Discard content before first detection.")
@click.option(
    "--slate-buffer", type=float, default=0.5,
    help="Seconds to skip after detection (default: 0.5).",
)
@click.option(
    "--clap-threshold", type=float, default=0.6,
    help="Audio clap detection sensitivity (default: 0.6).",
)
@click.option("--dry-run", is_flag=True, help="Show split plan without executing.")
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging.")
def split(
    input_file: str,
    output_dir: str,
    mode: str,
    sample_rate: float,
    precise: bool,
    skip_preamble: bool,
    slate_buffer: float,
    clap_threshold: float,
    dry_run: bool,
    verbose: bool,
) -> None:
    """Split a continuous video at detected scene boundaries.

    Scans INPUT_FILE for QR codes, clapper boards, and/or audio claps
    throughout the full duration, then splits into individual scene clips
    in OUTPUT_DIR.
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(message)s")

    from clipsort.splitter import SplitPoint, SplitScanner, VideoSplitter

    # Check FFmpeg availability
    try:
        VideoSplitter.check_ffmpeg()
    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    video_path = Path(input_file)
    split_points: list[SplitPoint] = []

    if mode == "audio":
        # Audio-only mode — skip frame detectors
        from clipsort.audio_detect import AudioClapDetector

        click.echo(f"Scanning {video_path.name} for audio claps...")
        detector = AudioClapDetector(threshold=clap_threshold)
        timestamps = detector.detect_timestamps(video_path)
        split_points = [SplitPoint(timestamp=t, clip_info=None) for t in timestamps]
    else:
        # Build frame detectors based on mode
        frame_detectors = []

        if mode in ("auto", "qr"):
            from clipsort.qr_detect import QRDetector

            qr_detector = QRDetector()
            frame_detectors.append(qr_detector.detect_frame)

        if mode in ("auto", "ocr"):
            from clipsort.clapper_detect import ClapperDetector
            from clipsort.ocr import TesseractEngine

            ocr_engine = TesseractEngine()
            clapper_detector = ClapperDetector(ocr_engine=ocr_engine)
            frame_detectors.append(clapper_detector.detect_frame)

        if not frame_detectors:
            click.echo("Error: No detection mode selected.", err=True)
            sys.exit(1)

        click.echo(f"Scanning {video_path.name} for scene markers...")

        # Scan video for visual markers
        scanner = SplitScanner(
            frame_detectors=frame_detectors,
            sample_rate=sample_rate,
        )
        split_points = scanner.scan(video_path)

        # In auto mode, run audio as a post-pass and merge new timestamps
        if mode == "auto":
            from clipsort.audio_detect import AudioClapDetector

            click.echo("Scanning for audio claps...")
            audio_detector = AudioClapDetector(threshold=clap_threshold)
            audio_timestamps = audio_detector.detect_timestamps(video_path)
            for t in audio_timestamps:
                candidate = SplitPoint(timestamp=t, clip_info=None)
                if not scanner._is_duplicate(candidate, split_points):
                    split_points.append(candidate)
            split_points.sort(key=lambda sp: sp.timestamp)

    if not split_points:
        click.echo("No scene markers detected.", err=True)
        sys.exit(1)

    click.echo(f"Found {len(split_points)} scene marker(s).")

    # Get duration and compute segments
    splitter = VideoSplitter(precise=precise)
    duration = splitter.get_video_duration(video_path)
    segments = splitter.compute_segments(
        split_points, duration,
        slate_buffer=slate_buffer,
        skip_preamble=skip_preamble,
    )

    if not segments:
        click.echo("No segments to extract.", err=True)
        sys.exit(1)

    # Display plan
    click.echo(f"\nSplit plan ({len(segments)} segment(s)):")
    for seg in segments:
        end_str = f"{seg.end:.1f}s" if seg.end is not None else "end"
        if seg.clip_info is None:
            label = "preamble" if seg.index == 0 else f"segment {seg.index:03d}"
        else:
            label = f"scene {seg.clip_info.scene}"
            if seg.clip_info.take is not None:
                label += f" take {seg.clip_info.take}"
        click.echo(f"  {seg.start:.1f}s - {end_str}: {label}")

    if dry_run:
        click.echo("\n(dry run — no files created)")
        return

    # Split
    click.echo(f"\nSplitting into {Path(output_dir)}...")
    paths = splitter.split(video_path, Path(output_dir), segments)

    click.echo(f"\nCreated {len(paths)} file(s):")
    for p in paths:
        click.echo(f"  {p.name}")
