"""Compare two profiles side-by-side, showing keys present in one but not the other."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envoy.vault import load


@dataclass
class CompareResult:
    only_in_a: Dict[str, str] = field(default_factory=dict)
    only_in_b: Dict[str, str] = field(default_factory=dict)
    in_both_same: Dict[str, str] = field(default_factory=dict)
    in_both_different: Dict[str, tuple] = field(default_factory=dict)  # key -> (val_a, val_b)

    @property
    def is_identical(self) -> bool:
        return not (self.only_in_a or self.only_in_b or self.in_both_different)


def compare_profiles(
    path_a: str,
    passphrase_a: str,
    path_b: str,
    passphrase_b: str,
) -> CompareResult:
    """Load two vault files and compare their contents."""
    env_a: Dict[str, str] = load(path_a, passphrase_a)
    env_b: Dict[str, str] = load(path_b, passphrase_b)

    keys_a = set(env_a)
    keys_b = set(env_b)

    result = CompareResult()
    result.only_in_a = {k: env_a[k] for k in keys_a - keys_b}
    result.only_in_b = {k: env_b[k] for k in keys_b - keys_a}

    for k in keys_a & keys_b:
        if env_a[k] == env_b[k]:
            result.in_both_same[k] = env_a[k]
        else:
            result.in_both_different[k] = (env_a[k], env_b[k])

    return result


def format_compare(result: CompareResult, show_same: bool = False, mask: bool = True) -> str:
    """Return a human-readable string of the comparison result."""
    lines: List[str] = []
    _mask = lambda v: "***" if mask else v

    for k, v in sorted(result.only_in_a.items()):
        lines.append(f"  < {k}={_mask(v)}")
    for k, v in sorted(result.only_in_b.items()):
        lines.append(f"  > {k}={_mask(v)}")
    for k, (va, vb) in sorted(result.in_both_different.items()):
        lines.append(f"  ~ {k}: {_mask(va)} -> {_mask(vb)}")
    if show_same:
        for k, v in sorted(result.in_both_same.items()):
            lines.append(f"    {k}={_mask(v)}")

    if not lines:
        return "Profiles are identical."
    return "\n".join(lines)
