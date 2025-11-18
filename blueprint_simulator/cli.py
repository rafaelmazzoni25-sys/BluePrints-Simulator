"""Command line interface for the blueprint simulator."""

from __future__ import annotations

import argparse
import json
from typing import Dict

from .loader import load_blueprint
from .runtime import BlueprintRunner


def parse_variable_overrides(pairs: list[str]) -> Dict[str, str]:
    overrides: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise argparse.ArgumentTypeError("Variables must be provided as name=value")
        name, value = pair.split("=", 1)
        overrides[name] = _coerce_value(value)
    return overrides


def _coerce_value(value: str):
    for caster in (int, float):
        try:
            return caster(value)
        except ValueError:
            continue
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simulate Unreal Engine Blueprints")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Execute a blueprint definition")
    run_parser.add_argument("blueprint", help="Path to the blueprint JSON file")
    run_parser.add_argument(
        "--variable",
        action="append",
        default=[],
        metavar="name=value",
        help="Override an exposed variable",
    )

    describe_parser = subparsers.add_parser("describe", help="Describe a blueprint")
    describe_parser.add_argument("blueprint", help="Path to the blueprint JSON file")

    subparsers.add_parser("nodes", help="List available node types")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "nodes":
        print("Available nodes:")
        for node_type in BlueprintRunner.available_node_types():
            print(f" - {node_type}")
        return 0

    blueprint = load_blueprint(args.blueprint)
    runner = BlueprintRunner(blueprint)

    if args.command == "describe":
        print(runner.describe())
        return 0

    if args.command == "run":
        overrides = parse_variable_overrides(args.variable)
        context = runner.run(overrides)
        payload = {
            "variables": context.variables,
            "logs": context.logs,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    parser.error("Unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
