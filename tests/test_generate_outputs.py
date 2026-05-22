"""Tests for output generation."""

from pathlib import Path

import pytest

from agent_team_design.outputs import (
    find_shared_data_sources,
    generate_agent_stub,
    generate_compatibility_matrix,
    generate_outputs,
    generate_team_manifest,
    get_declared_overlap,
)
from agent_team_design.roles import parse_role_spec
from agent_team_design.trust import derive_scrutiny_level, derive_trust_level


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "sample-roles"


def test_parse_role_spec():
    spec = parse_role_spec(FIXTURES_DIR / "intake-coordinator.md")

    assert spec["frontmatter"]["name"] == "intake-coordinator"
    assert spec["frontmatter"]["customer"] == "credit-analyst"
    assert len(spec["frontmatter"]["data_access"]) == 2
    assert spec["source_file"] == "intake-coordinator.md"
    assert "document verification" in spec["content"].lower()


def test_generate_agent_stub_high_scrutiny():
    spec = parse_role_spec(FIXTURES_DIR / "credit-analyst.md")
    stub = generate_agent_stub(spec)

    assert "name: credit-analyst" in stub
    assert "fidelity: full" in stub
    assert "enabled: true" in stub
    assert "granularity: granular" in stub
    assert "trust_level: low" in stub
    assert "scrutiny_level: high" in stub


def test_generate_agent_stub_low_scrutiny():
    spec = parse_role_spec(FIXTURES_DIR / "intake-coordinator.md")
    stub = generate_agent_stub(spec)

    assert "name: intake-coordinator" in stub
    assert "fidelity: minimal" in stub
    assert "enabled: false" in stub
    assert "granularity: broad" in stub


def test_find_shared_data_sources():
    intake = parse_role_spec(FIXTURES_DIR / "intake-coordinator.md")
    analyst = parse_role_spec(FIXTURES_DIR / "credit-analyst.md")
    approval = parse_role_spec(FIXTURES_DIR / "approval-authority.md")

    shared_ia = find_shared_data_sources(intake, analyst)
    assert "application-portal" in shared_ia

    shared_aa = find_shared_data_sources(analyst, approval)
    assert shared_aa == []


def test_get_declared_overlap():
    intake = parse_role_spec(FIXTURES_DIR / "intake-coordinator.md")

    overlap = get_declared_overlap(intake, "credit-analyst")
    assert overlap is not None
    assert "justification" in overlap

    no_overlap = get_declared_overlap(intake, "approval-authority")
    assert no_overlap is None


def test_compatibility_matrix():
    specs = [
        parse_role_spec(FIXTURES_DIR / f)
        for f in sorted(FIXTURES_DIR.glob("*.md"))
    ]

    matrix = generate_compatibility_matrix(specs)

    assert "# Compatibility Matrix" in matrix
    assert "application-portal" in matrix
    assert "Different stages" in matrix


def test_team_manifest():
    specs = [
        parse_role_spec(FIXTURES_DIR / f)
        for f in sorted(FIXTURES_DIR.glob("*.md"))
    ]

    manifest = generate_team_manifest(specs, FIXTURES_DIR.parent)

    assert "# Team Manifest" in manifest
    assert "## Roles" in manifest
    assert "## Role Details" in manifest
    assert "## Design Status" in manifest
    assert "## Overlap Summary" in manifest
    assert "intake-coordinator" in manifest
    assert "credit-analyst" in manifest
    assert "approval-authority" in manifest
    assert "Prevents underwriters from wasting time" in manifest
    assert "Different stages" in manifest


def test_derive_scrutiny_from_reversibility():
    assert derive_scrutiny_level({"reversibility": "low", "impact": "high"}) == "high"
    assert derive_scrutiny_level({"reversibility": "high", "impact": "low"}) == "low"
    assert derive_scrutiny_level({"reversibility": "medium", "impact": "medium"}) == "medium"


def test_derive_scrutiny_explicit_overrides():
    fm = {"scrutiny_level": "low", "reversibility": "low", "impact": "high"}
    assert derive_scrutiny_level(fm) == "low"


def test_derive_trust_from_data_and_actions():
    fm_low = {
        "data_access": [{"source": "api", "sensitivity": "restricted"}],
        "action_scope": "external-calls",
    }
    assert derive_trust_level(fm_low) == "low"

    fm_high = {
        "data_access": [{"source": "docs", "sensitivity": "public"}],
        "action_scope": "read-only",
    }
    assert derive_trust_level(fm_high) == "high"


def test_derive_trust_explicit_overrides():
    fm = {
        "trust_level": "high",
        "data_access": [{"source": "api", "sensitivity": "restricted"}],
        "action_scope": "external-calls",
    }
    assert derive_trust_level(fm) == "high"


def test_budget_in_stub():
    spec = {
        "frontmatter": {
            "name": "costly-role",
            "description": "A role with budget",
            "scrutiny_level": "high",
            "trust_level": "low",
            "budget": {"max_cost_per_turn": 0.50, "max_cost_per_session": 10.00},
        },
        "source_file": "costly-role.md",
    }
    stub = generate_agent_stub(spec)
    assert "max_cost_per_turn: 0.5" in stub
    assert "max_cost_per_session: 10.0" in stub


def test_manifest_includes_design_status():
    specs = [
        parse_role_spec(FIXTURES_DIR / f)
        for f in sorted(FIXTURES_DIR.glob("*.md"))
    ]
    manifest = generate_team_manifest(specs, FIXTURES_DIR.parent)
    assert "**Stage**: ready" in manifest


def test_compatibility_matrix_merge_candidates(tmp_path):
    roles_dir = tmp_path / "roles"
    roles_dir.mkdir()

    (roles_dir / "role-a.md").write_text("""---
name: role-a
description: First role
data_access:
  - source: shared-db
    sensitivity: internal
overlaps_with: []
---
Content.
""")
    (roles_dir / "role-b.md").write_text("""---
name: role-b
description: Second role
data_access:
  - source: shared-db
    sensitivity: internal
overlaps_with: []
---
Content.
""")

    specs = [parse_role_spec(roles_dir / "role-a.md"), parse_role_spec(roles_dir / "role-b.md")]
    matrix = generate_compatibility_matrix(specs)
    assert "## Merge Candidates" in matrix


def test_missing_optional_fields(tmp_path):
    minimal_spec = """---
name: minimal-role
description: A minimal role spec for testing
---

This is a minimal role specification with only required fields.
"""
    spec_file = tmp_path / "minimal.md"
    spec_file.write_text(minimal_spec)

    spec = parse_role_spec(spec_file)
    assert spec["frontmatter"]["name"] == "minimal-role"

    stub = generate_agent_stub(spec)
    assert "action_scope: read-only" in stub
    assert "fidelity: standard" in stub


def test_empty_roles_directory(tmp_path):
    team_dir = tmp_path / "empty-team"
    (team_dir / "roles").mkdir(parents=True)

    with pytest.raises(ValueError, match="No role specification files found"):
        generate_outputs(str(team_dir))


def test_nonexistent_directory():
    with pytest.raises(FileNotFoundError, match="Team directory not found"):
        generate_outputs("/nonexistent/path")


def test_full_pipeline(tmp_path):
    team_dir = tmp_path / "test-team"
    roles_dir = team_dir / "roles"
    roles_dir.mkdir(parents=True)

    for role_file in FIXTURES_DIR.glob("*.md"):
        (roles_dir / role_file.name).write_text(role_file.read_text())

    generated = generate_outputs(str(team_dir))

    assert len(generated["stubs"]) == 3
    assert len(generated["matrices"]) == 1
    assert len(generated["manifests"]) == 1

    stubs_dir = team_dir / "stubs"
    assert (stubs_dir / "intake-coordinator.agent.yaml").exists()
    assert (stubs_dir / "credit-analyst.agent.yaml").exists()
    assert (stubs_dir / "approval-authority.agent.yaml").exists()

    analyst_stub = (stubs_dir / "credit-analyst.agent.yaml").read_text()
    assert "name: credit-analyst" in analyst_stub
    assert "fidelity: full" in analyst_stub

    matrix_content = (team_dir / "compatibility-matrix.md").read_text()
    assert "application-portal" in matrix_content

    manifest_content = (team_dir / "team-manifest.md").read_text()
    assert "intake-coordinator" in manifest_content
