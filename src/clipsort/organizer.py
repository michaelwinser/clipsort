"""Organizer — builds and executes a file organization plan."""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from clipsort.parser import ClipInfo

logger = logging.getLogger(__name__)


@dataclass
class OrganizePlan:
    """A plan describing where each file should go."""

    mappings: list[tuple[Path, Path]] = field(default_factory=list)
    unsorted: list[Path] = field(default_factory=list)
    conflicts: list[tuple[Path, Path, Path]] = field(default_factory=list)
    methods: dict[str, str] = field(default_factory=dict)


class Organizer:
    """Build and execute file organization plans."""

    def plan(
        self,
        files: list[tuple[Path, ClipInfo | None]],
        output_dir: Path,
        folder_format: str = "scene_{scene:02d}",
    ) -> OrganizePlan:
        """Build the organization plan.

        Args:
            files: List of (path, clip_info_or_None) pairs.
            output_dir: Root directory for organized output.
            folder_format: Format string for scene folders. Must contain {scene}.

        Returns:
            An OrganizePlan with mappings, unsorted files, and conflicts.
        """
        result = OrganizePlan()
        used_destinations: dict[Path, Path] = {}

        for source, info in files:
            if info is None:
                result.unsorted.append(source)
                continue

            folder_name = folder_format.format(scene=info.scene)
            dest = output_dir / folder_name / source.name

            if dest in used_destinations:
                original_dest = dest
                dest = self._resolve_conflict(dest, used_destinations)
                result.conflicts.append((source, original_dest, dest))
                logger.warning(
                    "Conflict: %s -> %s (renamed to %s)", source.name, original_dest, dest
                )

            used_destinations[dest] = source
            result.mappings.append((source, dest))
            result.methods[source.name] = info.method

        return result

    def execute(self, plan: OrganizePlan, move: bool = False) -> int:
        """Execute the plan: copy or move files.

        Args:
            plan: The organization plan to execute.
            move: If True, move files instead of copying.

        Returns:
            Number of files processed.
        """
        count = 0
        for source, dest in plan.mappings:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if move:
                shutil.move(str(source), dest)
            else:
                shutil.copy2(source, dest)
            count += 1
            logger.debug("%s %s -> %s", "Moved" if move else "Copied", source, dest)

        if plan.unsorted:
            unsorted_dir = dest.parent.parent / "unsorted" if plan.mappings else Path("unsorted")
            if plan.mappings:
                unsorted_dir = plan.mappings[0][1].parent.parent / "unsorted"
            for source in plan.unsorted:
                unsorted_dest = unsorted_dir / source.name
                unsorted_dest.parent.mkdir(parents=True, exist_ok=True)
                if move:
                    shutil.move(str(source), unsorted_dest)
                else:
                    shutil.copy2(source, unsorted_dest)
                count += 1

        return count

    @staticmethod
    def _resolve_conflict(dest: Path, used: dict[Path, Path]) -> Path:
        """Append _2, _3, etc. to avoid destination collisions."""
        stem = dest.stem
        suffix = dest.suffix
        parent = dest.parent
        counter = 2
        while dest in used:
            dest = parent / f"{stem}_{counter}{suffix}"
            counter += 1
        return dest
