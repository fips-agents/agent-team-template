"""Output generation: agent stubs, compatibility matrix, team manifest."""

import sys
from pathlib import Path
from typing import Any

from .roles import parse_role_spec
from .trust import SCRUTINY_CONFIG, derive_scrutiny_level, derive_trust_level


def generate_agent_stub(role_spec: dict[str, Any]) -> str:
    """Generate an agent.yaml stub from a role specification."""
    fm = role_spec["frontmatter"]
    scrutiny = derive_scrutiny_level(fm)
    trust = derive_trust_level(fm)
    config = SCRUTINY_CONFIG.get(scrutiny, SCRUTINY_CONFIG["medium"])

    stub = f"""# Generated from role spec: {role_spec['source_file']}
# Run: agent-team-design generate <team-dir>

name: {fm['name']}
description: {fm['description']}

model:
  name: claude-sonnet-4-6

permissions:
  data_access:
"""

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


def find_shared_data_sources(
    role_a: dict[str, Any], role_b: dict[str, Any],
) -> list[str]:
    """Find data sources that appear in both roles."""
    sources_a = {da["source"] for da in role_a["frontmatter"].get("data_access", [])}
    sources_b = {da["source"] for da in role_b["frontmatter"].get("data_access", [])}
    return sorted(sources_a & sources_b)


def get_declared_overlap(
    role_a: dict[str, Any], role_b_name: str,
) -> dict[str, str] | None:
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

            lines.append(
                f"| {name_a} | {name_b} | {shared_str} | {declared} | {justification} |"
            )

            if shared_sources and not overlap:
                merge_candidates.append((name_a, name_b, shared_sources))

    if merge_candidates:
        lines.extend([
            "", "## Merge Candidates", "",
            "These role pairs share data sources but have no declared overlap justification. "
            "Consider whether they should be merged or add an explicit `overlaps_with` entry.",
            "",
        ])
        for name_a, name_b, shared in merge_candidates:
            lines.append(f"- **{name_a}** and **{name_b}**: share {', '.join(shared)}")

    return "\n".join(lines)


def generate_team_manifest(
    role_specs: list[dict[str, Any]], team_dir: Path,
) -> str:
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

    for spec in role_specs:
        fm = spec["frontmatter"]
        name = fm["name"]
        desc = fm["description"][:50] + "..." if len(fm["description"]) > 50 else fm["description"]
        trust = fm.get("trust_level", "medium")
        scrutiny = fm.get("scrutiny_level", "medium")
        customer = fm.get("customer", "—")
        action_scope = fm.get("action_scope", "read-only")
        lines.append(
            f"| {name} | {desc} | {trust} | {scrutiny} | {customer} | {action_scope} |"
        )

    lines.extend(["", "## Role Details", ""])

    for spec in role_specs:
        fm = spec["frontmatter"]
        lines.append(f"### {fm['name']}")
        lines.append(f"- **Justification**: {fm.get('justification', 'Not specified')}")
        lines.append(
            f"- **Removes if absent**: {fm.get('removes_if_absent', 'Not specified')}"
        )
        data_sources = [
            f"{da['source']} ({da['sensitivity']})"
            for da in fm.get("data_access", [])
        ]
        lines.append(
            f"- **Data sources**: {', '.join(data_sources) if data_sources else 'None'}"
        )
        lines.append("")

    # Design stage
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
                lines.append(
                    f"- **{name}** overlaps with **{overlap['role']}**: "
                    f"{overlap.get('justification', 'No justification provided')}"
                )
    if not has_overlaps:
        lines.append("No declared overlaps between roles.")

    next_steps_file = team_dir / "next-steps.md"
    if next_steps_file.exists():
        lines.extend(["", "## Open Questions", ""])
        with open(next_steps_file) as f:
            lines.append(f.read().strip())

    return "\n".join(lines)


def generate_outputs(team_dir: str) -> dict[str, list[str]]:
    """Generate all outputs for a team design directory.

    Returns dict with paths of generated files keyed by type.

    Raises:
        FileNotFoundError: If team or roles directory doesn't exist.
        ValueError: If no valid role specifications found.
    """
    team_path = Path(team_dir)

    if not team_path.exists():
        raise FileNotFoundError(f"Team directory not found: {team_dir}")

    roles_dir = team_path / "roles"
    if not roles_dir.exists():
        raise FileNotFoundError(f"Roles directory not found: {roles_dir}")

    role_files = sorted(roles_dir.glob("*.md"))
    if not role_files:
        raise ValueError(f"No role specification files found in {roles_dir}")

    role_specs = []
    for role_file in role_files:
        try:
            spec = parse_role_spec(role_file)
            role_specs.append(spec)
        except Exception as e:
            print(f"Warning: Failed to parse {role_file}: {e}", file=sys.stderr)

    if not role_specs:
        raise ValueError("No valid role specifications found")

    stubs_dir = team_path / "stubs"
    stubs_dir.mkdir(exist_ok=True)

    generated_files: dict[str, list[str]] = {
        "stubs": [],
        "matrices": [],
        "manifests": [],
    }

    for spec in role_specs:
        name = spec["frontmatter"]["name"]
        stub_content = generate_agent_stub(spec)
        stub_path = stubs_dir / f"{name}.agent.yaml"
        with open(stub_path, "w") as f:
            f.write(stub_content)
        generated_files["stubs"].append(str(stub_path))

    matrix_content = generate_compatibility_matrix(role_specs)
    matrix_path = team_path / "compatibility-matrix.md"
    with open(matrix_path, "w") as f:
        f.write(matrix_content)
    generated_files["matrices"].append(str(matrix_path))

    manifest_content = generate_team_manifest(role_specs, team_path)
    manifest_path = team_path / "team-manifest.md"
    with open(manifest_path, "w") as f:
        f.write(manifest_content)
    generated_files["manifests"].append(str(manifest_path))

    return generated_files
