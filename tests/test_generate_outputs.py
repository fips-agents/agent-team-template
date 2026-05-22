"""
Tests for generate_outputs.py script.
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent.parent / ".claude" / "commands" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from generate_outputs import (
    SCRUTINY_CONFIG,
    derive_scrutiny_level,
    derive_trust_level,
    find_shared_data_sources,
    generate_agent_stub,
    generate_compatibility_matrix,
    generate_outputs,
    generate_team_manifest,
    get_declared_overlap,
    parse_role_spec,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "sample-roles"


def test_parse_role_spec():
    """Parse a role spec file and verify frontmatter extraction."""
    intake_file = FIXTURES_DIR / "intake-coordinator.md"
    spec = parse_role_spec(intake_file)

    assert "frontmatter" in spec
    assert "content" in spec
    assert "source_file" in spec

    fm = spec["frontmatter"]
    assert fm["name"] == "intake-coordinator"
    assert fm["description"] == "Verifies application completeness and routes to appropriate analysis path"
    assert fm["trust_level"] == "medium"
    assert fm["scrutiny_level"] == "low"
    assert fm["action_scope"] == "read-only"
    assert fm["customer"] == "credit-analyst"

    # Check data access
    assert len(fm["data_access"]) == 2
    sources = {da["source"] for da in fm["data_access"]}
    assert "application-portal" in sources
    assert "customer-database" in sources

    # Check actions
    assert "verify document completeness" in fm["actions"]
    assert "route applications" in fm["actions"]

    # Check overlaps
    assert len(fm["overlaps_with"]) == 1
    assert fm["overlaps_with"][0]["role"] == "credit-analyst"

    # Check content
    assert "Handles application receipt" in spec["content"]


def test_generate_agent_stub_high_scrutiny():
    """Generate agent stub for high scrutiny role (credit-analyst)."""
    analyst_file = FIXTURES_DIR / "credit-analyst.md"
    spec = parse_role_spec(analyst_file)

    stub = generate_agent_stub(spec)

    # Check that high scrutiny config is applied
    assert "fidelity: full" in stub
    assert "enabled: true" in stub  # question tool
    assert "granularity: granular" in stub

    # Check basic fields
    assert "name: credit-analyst" in stub
    assert "Performs credit analysis" in stub
    assert "scrutiny_level: high" in stub
    assert "trust_level: low" in stub

    # Check data access
    assert "application-portal" in stub
    assert "credit-bureau-api" in stub
    assert "financial-records" in stub


def test_generate_agent_stub_low_scrutiny():
    """Generate agent stub for low scrutiny role (intake-coordinator)."""
    intake_file = FIXTURES_DIR / "intake-coordinator.md"
    spec = parse_role_spec(intake_file)

    stub = generate_agent_stub(spec)

    # Check that low scrutiny config is applied
    assert "fidelity: minimal" in stub
    assert "enabled: false" in stub  # question tool
    assert "granularity: broad" in stub

    # Check basic fields
    assert "name: intake-coordinator" in stub
    assert "scrutiny_level: low" in stub
    assert "trust_level: medium" in stub
    assert "action_scope: read-only" in stub


def test_find_shared_data_sources():
    """Test finding shared data sources between roles."""
    intake_file = FIXTURES_DIR / "intake-coordinator.md"
    analyst_file = FIXTURES_DIR / "credit-analyst.md"

    intake_spec = parse_role_spec(intake_file)
    analyst_spec = parse_role_spec(analyst_file)

    shared = find_shared_data_sources(intake_spec, analyst_spec)

    # Both access application-portal
    assert "application-portal" in shared
    assert len(shared) == 1


def test_get_declared_overlap():
    """Test extracting declared overlaps from role spec."""
    intake_file = FIXTURES_DIR / "intake-coordinator.md"
    spec = parse_role_spec(intake_file)

    # Intake coordinator declares overlap with credit-analyst
    overlap = get_declared_overlap(spec, "credit-analyst")
    assert overlap is not None
    assert "Different stages" in overlap["justification"]

    # No overlap declared with approval-authority
    overlap = get_declared_overlap(spec, "approval-authority")
    assert overlap is None


def test_compatibility_matrix():
    """Generate compatibility matrix from sample roles."""
    intake_file = FIXTURES_DIR / "intake-coordinator.md"
    analyst_file = FIXTURES_DIR / "credit-analyst.md"
    approval_file = FIXTURES_DIR / "approval-authority.md"

    specs = [
        parse_role_spec(intake_file),
        parse_role_spec(analyst_file),
        parse_role_spec(approval_file),
    ]

    matrix = generate_compatibility_matrix(specs)

    # Check structure
    assert "# Compatibility Matrix" in matrix
    assert "| Role A | Role B | Shared Data Sources | Declared Overlap | Justification |" in matrix

    # Check specific entries
    assert "intake-coordinator" in matrix
    assert "credit-analyst" in matrix
    assert "approval-authority" in matrix

    # Verify shared data source detection
    assert "application-portal" in matrix

    # Verify declared overlap capture
    assert "Different stages" in matrix


def test_team_manifest():
    """Generate team manifest from sample roles."""
    intake_file = FIXTURES_DIR / "intake-coordinator.md"
    analyst_file = FIXTURES_DIR / "credit-analyst.md"
    approval_file = FIXTURES_DIR / "approval-authority.md"

    specs = [
        parse_role_spec(intake_file),
        parse_role_spec(analyst_file),
        parse_role_spec(approval_file),
    ]

    manifest = generate_team_manifest(specs, FIXTURES_DIR.parent)

    # Check structure
    assert "# Team Manifest" in manifest
    assert "## Roles" in manifest
    assert "## Role Details" in manifest
    assert "## Overlap Summary" in manifest

    # Check all roles appear in table
    assert "intake-coordinator" in manifest
    assert "credit-analyst" in manifest
    assert "approval-authority" in manifest

    # Check role details
    assert "Prevents underwriters from wasting time" in manifest
    assert "Separates risk evaluation expertise" in manifest

    # Check overlap summary
    assert "Different stages" in manifest


def test_derive_scrutiny_from_reversibility():
    """Scrutiny derived from reversibility + impact when not explicit."""
    fm_high = {"reversibility": "low", "impact": "high"}
    assert derive_scrutiny_level(fm_high) == "high"

    fm_low = {"reversibility": "high", "impact": "low"}
    assert derive_scrutiny_level(fm_low) == "low"

    fm_medium = {"reversibility": "medium", "impact": "medium"}
    assert derive_scrutiny_level(fm_medium) == "medium"


def test_derive_scrutiny_explicit_overrides():
    """Explicit scrutiny_level is used when present."""
    fm = {"scrutiny_level": "low", "reversibility": "low", "impact": "high"}
    assert derive_scrutiny_level(fm) == "low"


def test_derive_trust_from_data_and_actions():
    """Trust derived from data sensitivity and action scope."""
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
    """Explicit trust_level is used when present."""
    fm = {
        "trust_level": "high",
        "data_access": [{"source": "api", "sensitivity": "restricted"}],
        "action_scope": "external-calls",
    }
    assert derive_trust_level(fm) == "high"


def test_budget_in_stub():
    """Budget fields appear in generated stub when present."""
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
    """Team manifest includes design stage assessment."""
    intake_file = FIXTURES_DIR / "intake-coordinator.md"
    analyst_file = FIXTURES_DIR / "credit-analyst.md"
    approval_file = FIXTURES_DIR / "approval-authority.md"

    specs = [
        parse_role_spec(intake_file),
        parse_role_spec(analyst_file),
        parse_role_spec(approval_file),
    ]

    manifest = generate_team_manifest(specs, FIXTURES_DIR.parent)
    assert "## Design Status" in manifest
    assert "**Stage**: ready" in manifest


def test_compatibility_matrix_merge_candidates(tmp_path):
    """Roles sharing data without declared overlap are flagged as merge candidates."""
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
    assert "role-a" in matrix
    assert "role-b" in matrix


def test_missing_optional_fields(tmp_path):
    """Test handling role spec with minimal frontmatter."""
    minimal_spec = """---
name: minimal-role
description: A minimal role spec for testing
---

This is a minimal role specification with only required fields.
"""

    spec_file = tmp_path / "minimal.md"
    spec_file.write_text(minimal_spec)

    spec = parse_role_spec(spec_file)

    # Should parse successfully
    assert spec["frontmatter"]["name"] == "minimal-role"

    # Generate stub with defaults
    stub = generate_agent_stub(spec)

    # Should have defaults applied
    assert "action_scope: read-only" in stub
    assert "fidelity: standard" in stub  # medium scrutiny default


def test_empty_roles_directory(tmp_path):
    """Test error when roles directory is empty."""
    team_dir = tmp_path / "empty-team"
    roles_dir = team_dir / "roles"
    roles_dir.mkdir(parents=True)

    with pytest.raises(ValueError, match="No role specification files found"):
        generate_outputs(str(team_dir))


def test_nonexistent_directory():
    """Test error when team directory doesn't exist."""
    with pytest.raises(FileNotFoundError, match="Team directory not found"):
        generate_outputs("/nonexistent/path")


def test_full_pipeline(tmp_path):
    """Run full pipeline against sample roles."""
    # Create team directory structure
    team_dir = tmp_path / "test-team"
    roles_dir = team_dir / "roles"
    roles_dir.mkdir(parents=True)

    # Copy sample role files
    for role_file in FIXTURES_DIR.glob("*.md"):
        (roles_dir / role_file.name).write_text(role_file.read_text())

    # Run generator
    generated = generate_outputs(str(team_dir))

    # Verify all outputs created
    assert len(generated["stubs"]) == 3
    assert len(generated["matrices"]) == 1
    assert len(generated["manifests"]) == 1

    # Verify stub files exist and contain expected content
    stubs_dir = team_dir / "stubs"
    assert (stubs_dir / "intake-coordinator.agent.yaml").exists()
    assert (stubs_dir / "credit-analyst.agent.yaml").exists()
    assert (stubs_dir / "approval-authority.agent.yaml").exists()

    # Check stub content
    analyst_stub = (stubs_dir / "credit-analyst.agent.yaml").read_text()
    assert "name: credit-analyst" in analyst_stub
    assert "fidelity: full" in analyst_stub

    # Verify matrix file
    matrix_file = team_dir / "compatibility-matrix.md"
    assert matrix_file.exists()
    matrix_content = matrix_file.read_text()
    assert "application-portal" in matrix_content

    # Verify manifest file
    manifest_file = team_dir / "team-manifest.md"
    assert manifest_file.exists()
    manifest_content = manifest_file.read_text()
    assert "intake-coordinator" in manifest_content
    assert "credit-analyst" in manifest_content
    assert "approval-authority" in manifest_content
