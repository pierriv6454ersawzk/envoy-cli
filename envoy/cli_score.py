"""CLI commands for profile scoring."""

from __future__ import annotations

import sys

from envoy.score import score_profile


def cmd_score(args) -> None:
    """Show quality score for a profile."""
    try:
        report = score_profile(
            profile=args.profile,
            passphrase=args.passphrase,
            base_dir=getattr(args, "base_dir", None),
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Profile : {report.profile}")
    print(f"Keys    : {report.total_keys}")
    print(f"Schema  : {report.schema_coverage * 100:.1f}% required keys present")
    print(f"Errors  : {report.lint_errors}")
    print(f"Warnings: {report.lint_warnings}")
    print(f"Score   : {report.score}/100  [{report.grade}]")


def register_score_commands(subparsers) -> None:
    p = subparsers.add_parser("score", help="Show quality score for a profile")
    p.add_argument("profile", help="Profile name")
    p.add_argument("--passphrase", required=True, help="Vault passphrase")
    p.set_defaults(func=cmd_score)
