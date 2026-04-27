"""Compliance checking for env profiles.

Provides rules-based compliance evaluation against named policy sets
(e.g. 'pci', 'hipaa', 'internal').  Each policy is a collection of
requirements expressed as callables that receive the env dict and return
a list of violation strings.  An empty list means the requirement passes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from envoy.profile import profile_path, profile_exists
from envoy.vault import load

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

PolicyRule = Callable[[Dict[str, str]], List[str]]


@dataclass
class ComplianceViolation:
    policy: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"[{self.policy}/{self.rule}] {self.message}"


@dataclass
class ComplianceReport:
    profile: str
    policy: str
    violations: List[ComplianceViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def as_dict(self) -> dict:
        return {
            "profile": self.profile,
            "policy": self.policy,
            "passed": self.passed,
            "violations": [
                {"rule": v.rule, "message": v.message}
                for v in self.violations
            ],
        }


# ---------------------------------------------------------------------------
# Built-in policies
# ---------------------------------------------------------------------------

def _rule_no_plaintext_secrets(env: Dict[str, str]) -> List[str]:
    """Flag keys whose values look like unencrypted secrets."""
    suspicious_keys = {"PASSWORD", "SECRET", "TOKEN", "API_KEY", "PRIVATE_KEY"}
    issues = []
    for key, value in env.items():
        if any(s in key.upper() for s in suspicious_keys):
            if value and not value.startswith("enc:") and len(value) > 0:
                issues.append(
                    f"Key '{key}' appears to contain a plaintext secret."
                )
    return issues


def _rule_all_keys_uppercase(env: Dict[str, str]) -> List[str]:
    """All keys must be uppercase."""
    return [
        f"Key '{k}' is not uppercase."
        for k in env
        if k != k.upper()
    ]


def _rule_no_empty_values(env: Dict[str, str]) -> List[str]:
    """No key should have an empty value."""
    return [
        f"Key '{k}' has an empty value."
        for k, v in env.items()
        if v == ""
    ]


def _rule_no_localhost_urls(env: Dict[str, str]) -> List[str]:
    """Production profiles should not reference localhost."""
    issues = []
    for key, value in env.items():
        if "localhost" in value.lower() or "127.0.0.1" in value:
            issues.append(
                f"Key '{key}' references localhost — not suitable for production."
            )
    return issues


# Policy registry: name -> {rule_name -> rule_fn}
_POLICIES: Dict[str, Dict[str, PolicyRule]] = {
    "basic": {
        "no_empty_values": _rule_no_empty_values,
        "uppercase_keys": _rule_all_keys_uppercase,
    },
    "security": {
        "no_empty_values": _rule_no_empty_values,
        "uppercase_keys": _rule_all_keys_uppercase,
        "no_plaintext_secrets": _rule_no_plaintext_secrets,
    },
    "production": {
        "no_empty_values": _rule_no_empty_values,
        "uppercase_keys": _rule_all_keys_uppercase,
        "no_plaintext_secrets": _rule_no_plaintext_secrets,
        "no_localhost_urls": _rule_no_localhost_urls,
    },
}


def list_policies() -> List[str]:
    """Return the names of all built-in policies."""
    return list(_POLICIES.keys())


# ---------------------------------------------------------------------------
# Core API
# ---------------------------------------------------------------------------

class ComplianceError(Exception):
    """Raised when compliance checking cannot proceed."""


def check_compliance(
    profile: str,
    passphrase: str,
    policy: str,
    base_dir: Optional[Path] = None,
) -> ComplianceReport:
    """Evaluate *profile* against *policy* and return a ComplianceReport.

    Args:
        profile:    Profile name to check.
        passphrase: Passphrase used to decrypt the vault.
        policy:     Name of the policy to apply (see list_policies()).
        base_dir:   Override base directory (used in tests).

    Raises:
        ComplianceError: If the profile does not exist or the policy is unknown.
    """
    if not profile_exists(profile, base_dir=base_dir):
        raise ComplianceError(f"Profile '{profile}' does not exist.")

    if policy not in _POLICIES:
        raise ComplianceError(
            f"Unknown policy '{policy}'. Available: {', '.join(list_policies())}"
        )

    path = profile_path(profile, base_dir=base_dir)
    env = load(path, passphrase)

    rules = _POLICIES[policy]
    violations: List[ComplianceViolation] = []

    for rule_name, rule_fn in rules.items():
        for message in rule_fn(env):
            violations.append(
                ComplianceViolation(policy=policy, rule=rule_name, message=message)
            )

    return ComplianceReport(profile=profile, policy=policy, violations=violations)


def format_report(report: ComplianceReport) -> str:
    """Return a human-readable summary of a ComplianceReport."""
    lines = [
        f"Compliance report — profile: {report.profile!r}  policy: {report.policy!r}",
        f"Result: {'PASS' if report.passed else 'FAIL'}",
    ]
    if report.violations:
        lines.append(f"Violations ({len(report.violations)}):")
        for v in report.violations:
            lines.append(f"  • {v}")
    else:
        lines.append("No violations found.")
    return "\n".join(lines)
