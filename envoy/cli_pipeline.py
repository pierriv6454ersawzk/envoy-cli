"""CLI commands for managing envoy pipelines."""

from __future__ import annotations

import json
import sys

from envoy.pipeline import (
    PipelineError,
    delete_pipeline,
    list_pipelines,
    load_pipeline,
    save_pipeline,
)


def cmd_pipeline_save(args) -> None:
    """Save a pipeline from a JSON steps definition."""
    try:
        steps = json.loads(args.steps)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON for steps — {exc}", file=sys.stderr)
        sys.exit(1)
    try:
        save_pipeline(args.name, args.profile, steps, base_dir=args.base_dir)
        print(f"Pipeline '{args.name}' saved for profile '{args.profile}' ({len(steps)} step(s)).")
    except PipelineError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_pipeline_show(args) -> None:
    """Display a pipeline definition."""
    try:
        pipeline = load_pipeline(args.name, base_dir=args.base_dir)
    except PipelineError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Pipeline : {args.name}")
    print(f"Profile  : {pipeline['profile']}")
    print(f"Steps    : {len(pipeline['steps'])}")
    for i, step in enumerate(pipeline["steps"], 1):
        params = {k: v for k, v in step.items() if k != "action"}
        param_str = ", ".join(f"{k}={v}" for k, v in params.items())
        print(f"  {i}. {step.get('action', '?')}" + (f"  ({param_str})" if param_str else ""))


def cmd_pipeline_list(args) -> None:
    """List all saved pipelines."""
    names = list_pipelines(base_dir=args.base_dir)
    if not names:
        print("No pipelines defined.")
    else:
        for name in names:
            print(name)


def cmd_pipeline_delete(args) -> None:
    """Delete a pipeline by name."""
    try:
        delete_pipeline(args.name, base_dir=args.base_dir)
        print(f"Pipeline '{args.name}' deleted.")
    except PipelineError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_pipeline_commands(subparsers, common_args) -> None:
    p_save = subparsers.add_parser("pipeline-save", help="Save a pipeline definition")
    common_args(p_save)
    p_save.add_argument("name", help="Pipeline name")
    p_save.add_argument("profile", help="Target profile")
    p_save.add_argument("steps", help="JSON array of step objects")
    p_save.set_defaults(func=cmd_pipeline_save)

    p_show = subparsers.add_parser("pipeline-show", help="Show a pipeline")
    common_args(p_show)
    p_show.add_argument("name", help="Pipeline name")
    p_show.set_defaults(func=cmd_pipeline_show)

    p_list = subparsers.add_parser("pipeline-list", help="List all pipelines")
    common_args(p_list)
    p_list.set_defaults(func=cmd_pipeline_list)

    p_del = subparsers.add_parser("pipeline-delete", help="Delete a pipeline")
    common_args(p_del)
    p_del.add_argument("name", help="Pipeline name")
    p_del.set_defaults(func=cmd_pipeline_delete)
