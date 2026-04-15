"""Schema validation for .env profiles.

Allows users to define expected keys, types, and constraints
for a profile and validate an env dict against that schema.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

VALID_TYPES = {"string", "integer", "boolean", "float"}


@dataclass
class SchemaViolation:
    key: str
    message: str
    severity: str = "error"  # "error" | "warning"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message}"


def _schema_path(base_dir: str, profile: str) -> str:
    return os.path.join(base_dir, ".envoy", "schemas", f"{profile}.json")


def save_schema(base_dir: str, profile: str, schema: dict[str, Any]) -> None:
    """Persist a schema definition for a profile."""
    path = _schema_path(base_dir, profile)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(schema, fh, indent=2)


def load_schema(base_dir: str, profile: str) -> dict[str, Any]:
    """Load schema for a profile; returns empty dict if not found."""
    path = _schema_path(base_dir, profile)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_env(
    env: dict[str, str], schema: dict[str, Any]
) -> list[SchemaViolation]:
    """Validate an env dict against a schema definition.

    Schema format::

        {
          "KEY_NAME": {
            "required": true,
            "type": "integer",
            "description": "Port number"
          }
        }
    """
    violations: list[SchemaViolation] = []

    for key, rules in schema.items():
        required = rules.get("required", False)
        expected_type = rules.get("type", "string")

        if key not in env:
            if required:
                violations.append(
                    SchemaViolation(key, "required key is missing", "error")
                )
            continue

        value = env[key]
        if expected_type == "integer":
            try:
                int(value)
            except ValueError:
                violations.append(
                    SchemaViolation(key, f"expected integer, got {value!r}", "error")
                )
        elif expected_type == "float":
            try:
                float(value)
            except ValueError:
                violations.append(
                    SchemaViolation(key, f"expected float, got {value!r}", "error")
                )
        elif expected_type == "boolean":
            if value.lower() not in {"true", "false", "1", "0", "yes", "no"}:
                violations.append(
                    SchemaViolation(
                        key, f"expected boolean, got {value!r}", "error"
                    )
                )

    return violations
