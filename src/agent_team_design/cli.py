"""CLI entry point for agent-team-design."""

import argparse
import json
import sys

from agent_team_design.bpmn import parse_bpmn
from agent_team_design.outputs import generate_outputs


def cmd_parse_bpmn(args: argparse.Namespace) -> None:
    try:
        result = parse_bpmn(args.file)
        print(json.dumps(result, indent=2))
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_generate(args: argparse.Namespace) -> None:
    try:
        generated = generate_outputs(args.team_dir)

        print("Generated outputs:")
        print(f"\nAgent stubs ({len(generated['stubs'])}):")
        for stub in generated["stubs"]:
            print(f"  - {stub}")
        print(f"\nCompatibility matrices ({len(generated['matrices'])}):")
        for matrix in generated["matrices"]:
            print(f"  - {matrix}")
        print(f"\nTeam manifests ({len(generated['manifests'])}):")
        for manifest in generated["manifests"]:
            print(f"  - {manifest}")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="agent-team-design",
        description="Organizational design tools for multi-agent teams",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    bpmn_parser = subparsers.add_parser(
        "parse-bpmn", help="Parse a BPMN 2.0 XML file to JSON",
    )
    bpmn_parser.add_argument("file", help="Path to BPMN XML file")
    bpmn_parser.set_defaults(func=cmd_parse_bpmn)

    gen_parser = subparsers.add_parser(
        "generate", help="Generate outputs from role specifications",
    )
    gen_parser.add_argument(
        "team_dir", help="Path to team design directory containing roles/",
    )
    gen_parser.set_defaults(func=cmd_generate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
