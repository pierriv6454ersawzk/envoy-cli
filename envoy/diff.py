"""Diff utilities for comparing env profiles or local vs remote state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    left_value: str | None = None
    right_value: str | None = None


def diff_envs(
    left: Dict[str, str],
    right: Dict[str, str],
    *,
    show_unchanged: bool = False,
) -> List[DiffEntry]:
    """Compare two env dicts and return a list of DiffEntry results."""
    entries: List[DiffEntry] = []
    all_keys = sorted(set(left) | set(right))

    for key in all_keys:
        in_left = key in left
        in_right = key in right

        if in_left and not in_right:
            entries.append(DiffEntry(key=key, status="removed", left_value=left[key]))
        elif in_right and not in_left:
            entries.append(DiffEntry(key=key, status="added", right_value=right[key]))
        elif left[key] != right[key]:
            entries.append(
                DiffEntry(
                    key=key,
                    status="changed",
                    left_value=left[key],
                    right_value=right[key],
                )
            )
        elif show_unchanged:
            entries.append(
                DiffEntry(
                    key=key,
                    status="unchanged",
                    left_value=left[key],
                    right_value=right[key],
                )
            )

    return entries


def format_diff(entries: List[DiffEntry], *, mask_values: bool = True) -> str:
    """Render diff entries as a human-readable string."""
    if not entries:
        return "(no differences)"

    lines: List[str] = []
    for e in entries:
        def _val(v: str | None) -> str:
            if v is None:
                return ""
            return "***" if mask_values else v

        if e.status == "added":
            lines.append(f"  + {e.key} = {_val(e.right_value)}")
        elif e.status == "removed":
            lines.append(f"  - {e.key} = {_val(e.left_value)}")
        elif e.status == "changed":
            lines.append(f"  ~ {e.key}: {_val(e.left_value)} -> {_val(e.right_value)}")
        else:
            lines.append(f"    {e.key} = {_val(e.left_value)}")

    return "\n".join(lines)
