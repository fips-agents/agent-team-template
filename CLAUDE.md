# CLAUDE.md

Agent team design template for the fips-agents ecosystem. Helps developers design multi-agent teams by deriving roles from domain constraints.

## Project Status

Implemented. All core issues (#2-#8) closed. CLI integration tracked in fips-agents/fips-agents-cli#52.

## Key Files

- `.claude/commands/design-team.md` -- Interactive skill command (invoke with `/design-team`)
- `.claude/commands/scripts/bpmn_parser.py` -- BPMN parser wrapper
- `.claude/commands/scripts/generate_outputs.py` -- Output generator wrapper
- `src/agent_team_design/` -- Standalone Python package
- `docs/concept.md` -- Core concept: organizational design for agent teams
- `planning/design-notes.md` -- Collected design decisions and rationale

## Architecture Decisions

- Separate repo from agent-template -- team design is a build-time concern, not runtime
- Dual-track distribution: standalone library (`pip install agent-team-design`) + fips-agents integration (agent.yaml generation)
- Skills-based workflow modeled after the "imagine" skill pattern -- iterative dialog, not one-shot generation
- Input: domain constraints (BPMN process maps, policies, rules, example outputs)
- Intermediate format: markdown/CSV for easy dedup and diffing
- Output: role specs as markdown with YAML frontmatter, then agent.yaml stubs
- Internal package imports are relative -- simplifies CLI rename when scaffolding new projects
- kagenti support is optional -- works without it, but output format is compatible

## Development Conventions

- Python 3.10+, async where needed
- pytest for testing (`pytest tests/`)
- Keep files under 512 lines
- PyYAML is the only runtime dependency
- Wrapper scripts in `.claude/commands/scripts/` delegate to the package via `try/except ImportError` fallback
