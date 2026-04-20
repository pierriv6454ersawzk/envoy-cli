"""Profile scoring: compute a quality/completeness score for a profile."""

from __future__ import annotations

import dataclasses
from typing import Dict, List

from envoy.vault import load
from envoy.profile import profile_exists
from envoy.schema import load_schema
from envoy.lint import lint_env, has_errors, has_warnings


@dataclasses.dataclass
class ScoreReport:
    profile: str
    total_keys: int
    schema_coverage: float   # 0.0 – 1.0
    lint_errors: int
    lint_warnings: int
    score: int               # 0 – 100
    grade: str

    def as_dict(self) -> Dict:
        return dataclasses.asdict(self)


_GRADE_THRESHOLDS = [
    (90, "A"),
    (75, "B"),
    (60, "C"),
    (40, "D"),
    (0,  "F"),
]


def _grade(score: int) -> str:
    for threshold, letter in _GRADE_THRESHOLDS:
        if score >= threshold:
            return letter
    return "F"


def score_profile(profile: str, passphrase: str, base_dir: str | None = None) -> ScoreReport:
    """Compute a quality score for *profile*.

    Scoring breakdown (100 pts total):
      - 50 pts: schema coverage (fraction of required keys present)
      - 30 pts: no lint errors   (-10 per error, floor 0)
      - 20 pts: no lint warnings (-5 per warning, floor 0)
    """
    if not profile_exists(profile, base_dir=base_dir):
        raise ValueError(f"Profile '{profile}' does not exist.")

    env: Dict[str, str] = load(profile, passphrase, base_dir=base_dir)
    schema: Dict = load_schema(profile, base_dir=base_dir)
    required_keys: List[str] = [
        k for k, v in schema.items() if v.get("required", False)
    ]

    if required_keys:
        present = sum(1 for k in required_keys if k in env)
        coverage = present / len(required_keys)
    else:
        coverage = 1.0

    lint_result = lint_env(env)
    errors = len([i for i in lint_result.issues if i.severity == "error"])
    warnings = len([i for i in lint_result.issues if i.severity == "warning"])

    schema_pts  = round(coverage * 50)
    error_pts   = max(0, 30 - errors   * 10)
    warning_pts = max(0, 20 - warnings *  5)
    total_score = schema_pts + error_pts + warning_pts

    return ScoreReport(
        profile=profile,
        total_keys=len(env),
        schema_coverage=round(coverage, 4),
        lint_errors=errors,
        lint_warnings=warnings,
        score=total_score,
        grade=_grade(total_score),
    )
