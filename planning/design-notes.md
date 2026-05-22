# Design Notes

Collected from initial design discussions, May 2026.

## Key decisions

1. **Separate repo from agent-template** — Team design artifacts are build-time concerns. Deployed agents don't carry organizational design tooling. Allows independent release cadence.

2. **CLI integration via `fips-agents create agent-team`** — Follows existing pattern for `fips-agents create mcp-server`. Developer gets a workspace with skills, uses skills to design, then scaffolds actual agents from the output.

3. **Dual-track distribution** — Standalone version works with generic role specs. fips-agents integration adds a thin layer mapping to agent.yaml, permissions, trace fidelity. Standalone version is the upstream contribution candidate for kagenti/OGX.

4. **Imagine-style iterative dialog** — Not one-shot generation. The skill walks the developer through role derivation, justification, trust profiling, and overlap detection.

5. **Domain-constraint-driven** — Accepts BPMN process maps, policies, rules, example outputs. Roles derived from domain, not from LLM capability catalog.

6. **Trust to runtime config mapping** — Trust profiles map to concrete fipsagents config (permissions, trace fidelity, compaction, question tool). This bridges organizational design with runtime governance.

7. **kagenti optional** — Output format is kagenti-compatible (capability profiles, trust accumulation) but the tool works without kagenti infrastructure.
