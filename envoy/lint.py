"""Lint .env profiles for common issues."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import re

_VALID_KEY_RE = re.compile(r'^[A-Z_][A-Z0-9_]*$')
_SUSPICIOUS_VALUE_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')


@dataclass
class LintIssue:
    key: str
    message: str
    severity: str  # 'error' | 'warning'


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == 'error' for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == 'warning' for i in self.issues)


def lint_env(variables: dict[str, str]) -> LintResult:
    """Analyse a dict of env variables and return a LintResult."""
    result = LintResult()

    seen_keys: set[str] = set()

    for key, value in variables.items():
        # Duplicate key detection (can arise from manual vault edits)
        if key in seen_keys:
            result.issues.append(LintIssue(key=key, message="Duplicate key", severity='error'))
        seen_keys.add(key)

        # Key naming convention
        if not _VALID_KEY_RE.match(key):
            result.issues.append(
                LintIssue(
                    key=key,
                    message=f"Key '{key}' does not follow UPPER_SNAKE_CASE convention",
                    severity='warning',
                )
            )

        # Empty value
        if value == '':
            result.issues.append(
                LintIssue(key=key, message="Value is empty", severity='warning')
            )

        # Suspicious control characters in value
        if _SUSPICIOUS_VALUE_RE.search(value):
            result.issues.append(
                LintIssue(
                    key=key,
                    message="Value contains non-printable control characters",
                    severity='error',
                )
            )

        # Unquoted whitespace at edges
        if value != value.strip():
            result.issues.append(
                LintIssue(
                    key=key,
                    message="Value has leading or trailing whitespace",
                    severity='warning',
                )
            )

    return result


def format_lint_result(result: LintResult) -> str:
    """Return a human-readable summary of a LintResult."""
    if not result.issues:
        return "No issues found."
    lines = []
    for issue in result.issues:
        tag = '[ERROR]' if issue.severity == 'error' else '[WARN] '
        lines.append(f"  {tag} {issue.key}: {issue.message}")
    return '\n'.join(lines)
