"""Reporter — generates human-readable summaries of operations."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

from clipsort.organizer import OrganizePlan


class Reporter:
    """Generate summaries of organization plans."""

    def report(self, plan: OrganizePlan, stream=sys.stdout) -> None:
        """Print an organization summary to the given stream."""
        scenes: dict[str, list[str]] = defaultdict(list)

        for source, dest in plan.mappings:
            folder = dest.parent.name
            scenes[folder].append(source.name)

        stream.write(f"Files processed: {len(plan.mappings) + len(plan.unsorted)}\n")
        stream.write(f"Scenes detected: {len(scenes)}\n")

        for folder in sorted(scenes):
            stream.write(f"  {folder}: {len(scenes[folder])} clip(s)\n")

        if plan.unsorted:
            stream.write(f"Unsorted: {len(plan.unsorted)} file(s)\n")
            for f in plan.unsorted:
                stream.write(f"  {f.name}\n")

        if plan.conflicts:
            stream.write(f"Conflicts resolved: {len(plan.conflicts)}\n")
            for source, attempted, actual in plan.conflicts:
                stream.write(f"  {source.name}: {attempted.name} -> {actual.name}\n")

        if plan.methods:
            stream.write("Detection methods:\n")
            for name in sorted(plan.methods):
                stream.write(f"  {name}: {plan.methods[name]}\n")

    def save(self, plan: OrganizePlan, path: Path) -> None:
        """Save the report to a file."""
        with open(path, "w") as f:
            self.report(plan, stream=f)
