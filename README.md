# Agent Team Design Template

Design multi-agent teams by deriving roles from domain constraints (process maps, policies, rules) rather than from LLM capabilities. Part of the [fips-agents](https://github.com/fips-agents) ecosystem.

## How It Works

A developer runs `/design-team` in Claude Code and enters an iterative dialog that walks through:

1. **Domain constraint ingestion** — BPMN process maps, policy documents, compliance rules, or a plain-language walkthrough of the process
2. **Process mapping** — stages, decision points, handoffs, data flows, exception paths
3. **Role derivation** — candidate roles derived from process gaps, not from LLM capabilities
4. **Trust and scrutiny profiling** — reversibility, impact, data sensitivity mapped to runtime config
5. **Output generation** — role specs, agent.yaml stubs, compatibility matrix, team manifest

Each role must pass the "removal test": if removing it doesn't degrade anything, the role doesn't carry its weight.

## Getting Started

```bash
fips-agents create agent-team my-team
cd my-team
pip install -e .
```

Then run `/design-team` in Claude Code to start the interactive design session.

### Standalone library

The core logic is also available as a standalone Python package:

```bash
pip install agent-team-design
```

CLI commands:

```bash
agent-team-design parse-bpmn process.bpmn      # Parse BPMN to JSON
agent-team-design generate team-design/my-team  # Generate stubs, matrix, manifest
```

## Documentation

- [docs/concept.md](docs/concept.md) — Core concept: organizational design for agent teams
- [planning/design-notes.md](planning/design-notes.md) — Design decisions and rationale

## Related Projects

- [fips-agents/agent-template](https://github.com/fips-agents/agent-template) — Agent templates (agent loop + agentic workflow)
- [fips-agents/mcp-server-template](https://github.com/fips-agents/mcp-server-template) — MCP server template
- [fips-agents/fips-agents-cli](https://github.com/fips-agents/fips-agents-cli) — CLI tool for scaffolding fips-agents projects

## License

Apache License 2.0. See [LICENSE](LICENSE).
