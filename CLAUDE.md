# CLAUDE.md

Agent team design template for the fips-agents ecosystem. Helps developers design multi-agent teams by deriving roles from domain constraints.

## Project Status

Early planning. No code yet. See `planning/` for design notes and `docs/` for concept documentation.

## Key Documents

- `docs/concept.md` -- Core concept: organizational design for agent teams
- `planning/design-notes.md` -- Collected design decisions and rationale

## Architecture Decisions

- Separate repo from agent-template -- team design is a build-time concern, not runtime
- Dual-track distribution: standalone library (generic role specs) + fips-agents integration (agent.yaml generation)
- Skills-based workflow modeled after the "imagine" skill pattern -- iterative dialog, not one-shot generation
- Input: domain constraints (BPMN process maps, policies, rules, example outputs)
- Intermediate format: markdown/CSV for easy dedup and diffing
- Output: role specs as markdown with YAML frontmatter, then agent.yaml stubs
- kagenti support is optional -- works without it, but output format is compatible

## Development Conventions

- Python, async where needed
- pytest for testing
- Keep files under 512 lines
- Use pydantic for config and schema validation
