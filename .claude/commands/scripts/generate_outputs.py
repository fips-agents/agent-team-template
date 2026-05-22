#!/usr/bin/env python3
"""
Generate agent team outputs from role specification files.

Reads role specs with YAML frontmatter and produces:
1. Agent stub YAML files
2. Compatibility matrix showing overlaps
3. Team manifest summarizing the full team design
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("Error: PyYAML not found. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


SCRUTINY_CONFIG = {
    "high": {
        "trace_fidelity": "full",
        "question_tool": True,
        "permission_granularity": "granular",
    },
    "medium": {
        "trace_fidelity": "standard",
        "question_tool": False,
        "permission_granularity": "moderate",
    },
    "low": {
        "trace_fidelity": "minimal",
        "question_tool": False,
        "permission_granularity": "broad",
    },
}

SENSITIVITY_TRUST = {
    "restricted": "low",
    "confidential": "low",
    "internal": "medium",
    "public": "high",
}

ACTION_SCOPE_TRUST = {
    "external-calls": "low",
    "delete": "low",
    "write": "medium",
    "read-only": "high",
}

REVERSIBILITY_IMPACT_SCRUTINY = {
    ("low", "high"): "high",
    ("low", "medium"): "medium",
    ("low", "low"): "medium",
    ("medium", "high"): "high",
    ("medium", "medium"): "medium",
    ("medium", "low"): "low",
    ("high", "high"): "medium",
    ("high", "medium"): "low",
    ("high", "low"): "low",
}


def parse_role_spec(file_path: Path) -> dict[str, Any]:
    """
    Parse a role specification file with YAML frontmatter.

    Returns dict with 'frontmatter' and 'content' keys.
    """
    with open(file_path) as f:
        content = f.read()

    # Split on --- delimiters
    parts = content.split("---")
    if len(parts) < 3:
        raise ValueError(f"Invalid role spec format in {file_path}: missing frontmatter delimiters")

    # Parse YAML frontmatter (parts[1] is between first and second ---)
    frontmatter = yaml.safe_load(parts[1])
    if not frontmatter:
        raise ValueError(f"Empty frontmatter in {file_path}")

    # Content is everything after second ---
    body = "---".join(parts[2:]).strip()

    return {
        "frontmatter": frontmatter,
        "content": body,
        "source_file": file_path.name,
    }


def derive_trust_level(fm: dict[str, Any]) -> str:
    """Derive trust level from data sensitivity and action scope when not explicit."""
    if fm.get("trust_level"):
        return fm["trust_level"]
    worst_sensitivity = "public"
    for da in fm.get("data_access", []):
        s = da.get("sensitivity", "public")
        if SENSITIVITY_TRUST.get(s, "high") < SENSITIVITY_TRUST.get(worst_sensitivity, "high"):
            worst_sensitivity = s
    data_trust = SENSITIVITY_TRUST.get(worst_sensitivity, "medium")
    action_trust = ACTION_SCOPE_TRUST.get(fm.get("action_scope", "read-only"), "medium")
    trust_order = ["low", "medium", "high"]
    return min(data_trust, action_trust, key=lambda t: trust_order.index(t))


def derive_scrutiny_level(fm: dict[str, Any]) -> str:
    """Derive scrutiny from reversibility and impact when not explicit."""
    if fm.get("scrutiny_level"):
        return fm["scrutiny_level"]
    reversibility = fm.get("reversibility", "medium")
    impact = fm.get("impact", "medium")
    return REVERSIBILITY_IMPACT_SCRUTINY.get((reversibility, impact), "medium")


def generate_agent_stub(role_spec: dict[str, Any]) -> str:
    """Generate an agent.yaml stub from a role specification."""
    fm = role_spec["frontmatter"]
    scrutiny = derive_scrutiny_level(fm)
    trust = derive_trust_level(fm)
    config = SCRUTINY_CONFIG.get(scrutiny, SCRUTINY_CONFIG["medium"])

    stub = f"""# Generated from role spec: {role_spec['source_file']}
# Run: python3 .claude/commands/scripts/generate_outputs.py <team-dir>

name: {fm['name']}
description: {fm['description']}

model:
  name: claude-sonnet-4-6

permissions:
  data_access:
"""

    # Add data access entries
    for da in fm.get("data_access", []):
        stub += f"    - source: {da['source']}\n"
        stub += f"      sensitivity: {da['sensitivity']}\n"

    budget = fm.get("budget", {})
    budget_section = ""
    if budget:
        budget_section = "\nbudget:\n"
        if "max_cost_per_turn" in budget:
            budget_section += f"  max_cost_per_turn: {budget['max_cost_per_turn']}\n"
        if "max_cost_per_session" in budget:
            budget_section += f"  max_cost_per_session: {budget['max_cost_per_session']}\n"

    stub += f"""  action_scope: {fm.get('action_scope', 'read-only')}
  granularity: {config['permission_granularity']}

trace:
  fidelity: {config['trace_fidelity']}

tools:
  question:
    enabled: {str(config['question_tool']).lower()}

trust_level: {trust}
scrutiny_level: {scrutiny}
reversibility: {fm.get('reversibility', 'medium')}
"""
    if budget_section:
        stub += budget_section

    return stub


def find_shared_data_sources(role_a: dict[str, Any], role_b: dict[str, Any]) -> list[str]:
    """Find data sources that appear in both roles."""
    sources_a = {da["source"] for da in role_a["frontmatter"].get("data_access", [])}
    sources_b = {da["source"] for da in role_b["frontmatter"].get("data_access", [])}
    return sorted(sources_a & sources_b)


def get_declared_overlap(role_a: dict[str, Any], role_b_name: str) -> dict[str, str] | None:
    """Check if role_a declares an overlap with role_b_name."""
    for overlap in role_a["frontmatter"].get("overlaps_with", []):
        if overlap.get("role") == role_b_name:
            return {
                "shared": overlap.get("shared", ""),
                "justification": overlap.get("justification", ""),
            }
    return None


def generate_compatibility_matrix(role_specs: list[dict[str, Any]]) -> str:
    """Generate compatibility matrix comparing all role pairs."""
    lines = [
        "# Compatibility Matrix",
        "",
        "Generated from role specifications.",
        "",
        "| Role A | Role B | Shared Data Sources | Declared Overlap | Justification |",
        "|--------|--------|---------------------|------------------|---------------|",
    ]

    merge_candidates = []

    for i, role_a in enumerate(role_specs):
        for role_b in role_specs[i + 1:]:
            name_a = role_a["frontmatter"]["name"]
            name_b = role_b["frontmatter"]["name"]

            shared_sources = find_shared_data_sources(role_a, role_b)
            shared_str = ", ".join(shared_sources) if shared_sources else "(none)"

            overlap_a = get_declared_overlap(role_a, name_b)
            overlap_b = get_declared_overlap(role_b, name_a)
            overlap = overlap_a or overlap_b

            declared = "yes" if overlap else "no"
            justification = overlap.get("justification", "—") if overlap else "—"

            lines.append(f"| {name_a} | {name_b} | {shared_str} | {declared} | {justification} |")

            if shared_sources and not overlap:
                merge_candidates.append((name_a, name_b, shared_sources))

    if merge_candidates:
        lines.extend(["", "## Merge Candidates", "",
                       "These role pairs share data sources but have no declared overlap justification. "
                       "Consider whether they should be merged or add an explicit `overlaps_with` entry.", ""])
        for name_a, name_b, shared in merge_candidates:
            lines.append(f"- **{name_a}** and **{name_b}**: share {', '.join(shared)}")

    return "\n".join(lines)


def generate_team_manifest(role_specs: list[dict[str, Any]], team_dir: Path) -> str:
    """Generate team manifest summarizing all roles."""
    lines = [
        "# Team Manifest",
        "",
        "Generated from role specifications.",
        "",
        "## Roles",
        "",
        "| Role | Description | Trust | Scrutiny | Customer | Action Scope |",
        "|------|-------------|-------|----------|----------|--------------|",
    ]

    # Role summary table
    for spec in role_specs:
        fm = spec["frontmatter"]
        name = fm["name"]
        desc = fm["description"][:50] + "..." if len(fm["description"]) > 50 else fm["description"]
        trust = fm.get("trust_level", "medium")
        scrutiny = fm.get("scrutiny_level", "medium")
        customer = fm.get("customer", "—")
        action_scope = fm.get("action_scope", "read-only")

        lines.append(f"| {name} | {desc} | {trust} | {scrutiny} | {customer} | {action_scope} |")

    # Role details
    lines.extend(["", "## Role Details", ""])

    for spec in role_specs:
        fm = spec["frontmatter"]
        name = fm["name"]

        lines.append(f"### {name}")
        lines.append(f"- **Justification**: {fm.get('justification', 'Not specified')}")
        lines.append(f"- **Removes if absent**: {fm.get('removes_if_absent', 'Not specified')}")

        # Data sources
        data_sources = []
        for da in fm.get("data_access", []):
            data_sources.append(f"{da['source']} ({da['sensitivity']})")
        lines.append(f"- **Data sources**: {', '.join(data_sources) if data_sources else 'None'}")
        lines.append("")

    # Design stage assessment
    has_trust = all(spec["frontmatter"].get("trust_level") for spec in role_specs)
    has_scrutiny = all(spec["frontmatter"].get("scrutiny_level") for spec in role_specs)
    has_justification = all(spec["frontmatter"].get("justification") for spec in role_specs)

    if has_trust and has_scrutiny and has_justification:
        stage = "ready"
    elif has_justification:
        stage = "stabilizing"
    elif role_specs:
        stage = "drafting"
    else:
        stage = "exploring"

    lines.extend([
        "## Design Status", "",
        f"**Stage**: {stage}", "",
        f"**Roles defined**: {len(role_specs)}", "",
    ])

    # Overlap summary
    lines.extend(["## Overlap Summary", ""])

    has_overlaps = False
    for spec in role_specs:
        overlaps = spec["frontmatter"].get("overlaps_with", [])
        if overlaps:
            has_overlaps = True
            name = spec["frontmatter"]["name"]
            for overlap in overlaps:
                lines.append(f"- **{name}** overlaps with **{overlap['role']}**: {overlap.get('justification', 'No justification provided')}")

    if not has_overlaps:
        lines.append("No declared overlaps between roles.")

    # Check for next-steps.md
    next_steps_file = team_dir / "next-steps.md"
    if next_steps_file.exists():
        lines.extend(["", "## Open Questions", ""])
        with open(next_steps_file) as f:
            lines.append(f.read().strip())

    return "\n".join(lines)


def generate_outputs(team_dir: str) -> dict[str, list[str]]:
    """
    Generate all outputs for a team design directory.

    Returns dict with paths of generated files.
    """
    team_path = Path(team_dir)

    if not team_path.exists():
        raise FileNotFoundError(f"Team directory not found: {team_dir}")

    roles_dir = team_path / "roles"
    if not roles_dir.exists():
        raise FileNotFoundError(f"Roles directory not found: {roles_dir}")

    # Find all role spec files
    role_files = sorted(roles_dir.glob("*.md"))
    if not role_files:
        raise ValueError(f"No role specification files found in {roles_dir}")

    # Parse all role specs
    role_specs = []
    for role_file in role_files:
        try:
            spec = parse_role_spec(role_file)
            role_specs.append(spec)
        except Exception as e:
            print(f"Warning: Failed to parse {role_file}: {e}", file=sys.stderr)

    if not role_specs:
        raise ValueError("No valid role specifications found")

    # Create output directories
    stubs_dir = team_path / "stubs"
    stubs_dir.mkdir(exist_ok=True)

    generated_files = {
        "stubs": [],
        "matrices": [],
        "manifests": [],
    }

    # Generate agent stubs
    for spec in role_specs:
        name = spec["frontmatter"]["name"]
        stub_content = generate_agent_stub(spec)
        stub_path = stubs_dir / f"{name}.agent.yaml"

        with open(stub_path, "w") as f:
            f.write(stub_content)

        generated_files["stubs"].append(str(stub_path))

    # Generate compatibility matrix
    matrix_content = generate_compatibility_matrix(role_specs)
    matrix_path = team_path / "compatibility-matrix.md"

    with open(matrix_path, "w") as f:
        f.write(matrix_content)

    generated_files["matrices"].append(str(matrix_path))

    # Generate team manifest
    manifest_content = generate_team_manifest(role_specs, team_path)
    manifest_path = team_path / "team-manifest.md"

    with open(manifest_path, "w") as f:
        f.write(manifest_content)

    generated_files["manifests"].append(str(manifest_path))

    return generated_files


def main():
    """CLI entry point."""
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

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
