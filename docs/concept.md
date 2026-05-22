# Agent Team Design — Concept

## Problem

Developers designing multi-agent teams tend to create roles based on what LLMs are good at (summarizing, classifying, generating) rather than what the domain process requires. This leads to redundant roles, wrong trust boundaries, and wasted resources. Before evaluating whether an agent performs well, we need to validate that the role itself is load-bearing for the use case.

## Approach

Organizational design principles applied to agent teams. The analogy: a CFO and CIO endure as roles because they fill governance gaps that emerge naturally from how organizations scale. A role is justified when removing it creates a gap that some other part of the system would have to fill ad-hoc and worse. This tool applies the same test to agent roles.

## Design Principles

- Start from the mission and domain constraints, not from desired agent capabilities
- Roles are derived from process maps, policies, and rules — not invented
- Each role gets a justification statement: why it exists, what degrades if removed
- Trust profiles: what data, actions, and budget each role can access
- Scrutiny proportional to reversibility of actions, not just authority level
- Active overlap/redundancy detection with justification required for intentional duplication (e.g., separation of duties)

## Developer Workflow

1. `fips-agents create agent-team` downloads the template with skills
2. Developer supplies domain constraints: process maps (BPMN, etc.), policies, rules, example outputs
3. Iterative dialog (imagine-style) to derive and challenge roles
4. Intermediate artifacts: markdown/CSV for dedup and diffing
5. Final output: role specs as markdown with YAML frontmatter
6. Generate agent.yaml stubs from the specs

## Trust and Scrutiny Profiles

Each role gets a trust profile mapping to runtime config:

- Trust profiles map to permissions config in agent.yaml
- Scrutiny levels map to trace fidelity, compaction policy, question tool presence
- High-trust/high-scrutiny (CFO equivalent): fidelity: full, granular permission rules
- Low-trust/low-scrutiny (receptionist equivalent): fidelity: minimal, broad allow rules

The key insight is that scrutiny is proportional to the *reversibility* of actions, not the *authority level* of the role. A role that can delete production data needs high scrutiny regardless of its rank in the team hierarchy. A role that only reads public data and produces summaries needs low scrutiny even if its output is consumed by senior decision-makers.

## Distribution Strategy

Dual-track: standalone library with generic role spec output (markdown/YAML), plus a fips-agents integration layer that maps specs into agent.yaml, permissions, and trace fidelity config. The standalone version is the upstream contribution candidate for kagenti or OGX. Keeps fips-agents unblocked on upstream acceptance while enabling contribution when the concept matures.

## Lifecycle

Initial team design is step one. Re-evaluation of team structure using runtime telemetry from deployed agents is a future capability. Could be offered as part of agent ops tooling — feeding real performance data back into the organizational design to validate that the roles as designed actually carry their weight in production.
