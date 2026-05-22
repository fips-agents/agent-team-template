"""BPMN parser wrapper — delegates to the agent_team_design package."""

import argparse
import json
import sys

try:
    from agent_team_design.bpmn import parse_bpmn
except ImportError:
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[3] / "src"))
    from agent_team_design.bpmn import parse_bpmn


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse BPMN 2.0 XML files to JSON")
    parser.add_argument("file", help="Path to BPMN XML file")
    args = parser.parse_args()

    try:
        result = parse_bpmn(args.file)
        print(json.dumps(result, indent=2))
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
