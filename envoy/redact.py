"""Redaction support: mask sensitive values when displaying env vars."""

import re
from typing import Dict, List

DEFAULT_PATTERNS: List[str] = [
    r"(?i)password",
    r"(?i)secret",
    r"(?i)token",
    r"(?i)api[_]?key",
    r"(?i)private[_]?key",
    r"(?i)auth",
    r"(?i)credential",
]

MASK = "********"


def _compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p) for p in patterns]


def is_sensitive(key: str, patterns: List[str] = None) -> bool:
    """Return True if the key matches any sensitive pattern."""
    pats = _compile_patterns(patterns or DEFAULT_PATTERNS)
    return any(p.search(key) for p in pats)


def redact_env(
    env: Dict[str, str],
    patterns: List[str] = None,
    reveal: bool = False,
) -> Dict[str, str]:
    """Return a copy of env with sensitive values masked.

    Args:
        env: The environment dictionary to redact.
        patterns: Optional list of regex patterns to match sensitive keys.
        reveal: If True, return values unmasked (no-op redaction).
    """
    if reveal:
        return dict(env)
    result = {}
    for key, value in env.items():
        result[key] = MASK if is_sensitive(key, patterns) else value
    return result


def redact_value(key: str, value: str, patterns: List[str] = None, reveal: bool = False) -> str:
    """Redact a single value based on its key name."""
    if reveal:
        return value
    return MASK if is_sensitive(key, patterns) else value
