"""Output generator wrapper — delegates to the agent_team_design package."""

import argparse
import sys

try:
    from agent_team_design.outputs import generate_outputs
except ImportError:
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[3] / "src"))
    from agent_team_design.outputs import generate_outputs


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate agent team outputs from role specifications"
    )
    parser.add_argument(
        "team_dir",
        help="Path to team design directory containing roles/ subdirectory",
    )
    args = parser.parse_args()

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


if __name__ == "__main__":
    main()
