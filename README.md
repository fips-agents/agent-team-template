# Agent Team Design Template

This template helps developers design multi-agent teams by deriving roles from domain constraints (process maps, policies, rules) rather than from LLM capabilities. Scaffolded via `fips-agents create agent-team`. Part of the [fips-agents](https://github.com/fips-agents) ecosystem.

## Getting Started

```bash
fips-agents create agent-team my-team
```

> Coming soon. The template and CLI integration are under active development.

## Concept

- Roles are derived from domain processes, not invented from capabilities
- Each role gets a justification statement and trust/scrutiny profile
- Active overlap and redundancy detection
- Output: role specs (markdown/YAML frontmatter) and agent.yaml stubs
- Works standalone or with kagenti for capability profiles and trust accumulation
