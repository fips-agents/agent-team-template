"""Organizational design for multi-agent teams."""

__version__ = "0.1.0"

from .bpmn import parse_bpmn
from .outputs import generate_outputs
from .roles import parse_role_spec
from .trust import derive_scrutiny_level, derive_trust_level

__all__ = [
    "parse_bpmn",
    "parse_role_spec",
    "derive_trust_level",
    "derive_scrutiny_level",
    "generate_outputs",
]
