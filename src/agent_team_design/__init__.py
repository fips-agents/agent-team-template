"""Organizational design for multi-agent teams."""

__version__ = "0.1.0"

from agent_team_design.bpmn import parse_bpmn
from agent_team_design.outputs import generate_outputs
from agent_team_design.roles import parse_role_spec
from agent_team_design.trust import derive_scrutiny_level, derive_trust_level

__all__ = [
    "parse_bpmn",
    "parse_role_spec",
    "derive_trust_level",
    "derive_scrutiny_level",
    "generate_outputs",
]
