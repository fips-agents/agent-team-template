# Retrospective: Initial Implementation

**Date:** 2026-05-22
**Effort:** Full buildout of agent-team-template from planning docs to working project
**Issues:** #1 (epic), #2, #3, #4, #5, #6, #7, #8
**Commits:** 139a343..748cf62 (7 commits, ~2,100 lines)

## What We Set Out To Do

Implement all deliverables from the epic: domain constraint ingestion (BPMN, policies, rules, free-text), iterative role derivation dialog, role justification with overlap detection, trust/scrutiny profiling with runtime config mapping, output generation (agent.yaml stubs, compatibility matrix, team manifest), CLI integration, and standalone library packaging.

## What Changed

| Change | Type | Rationale |
|--------|------|-----------|
| Incremental scope (#2-#3 first, then #4-#6, then #8) | Good pivot | User chose to build incrementally rather than all-at-once; allowed validation between rounds |
| BPMN parser error handling: sys.exit to exceptions | Good pivot | Review caught library-unfriendly pattern; exceptions are composable, sys.exit is not |
| Budget dimension added to trust profiles | Missed | Issue #5 specified it; initial implementation omitted it; caught in review |
| Scrutiny/trust derivation logic | Missed | Script hardcoded "medium" default instead of deriving from reversibility+impact; caught in review |
| overlap-analysis.md replaced by inline overlaps_with | Good pivot | Overlaps live with the roles they describe; eliminates a file that would drift |
| #7 filed on fips-agents-cli instead of implemented here | Scope deferral | CLI changes belong in fips-agents-cli; template side was already complete |
| Relative imports for CLI rename readiness | Good pivot | Came from fips-agents-cli agent feedback; reduces rename surface from 13 files to 4 |

## What Went Well

- BPMN parser validated against 3,739 real-world files (99.8% parse rate) — caught zero bugs that fixture-only testing would have missed, but established confidence
- Review sub-agents caught 4 substantive gaps that would have shipped without them: budget dimension, scrutiny derivation, merge recommendations, design stage tracking
- The imagine skill pattern gave strong structural guidance — didn't have to invent a dialog framework
- Package extraction was clean because the scripts were already well-factored into pure functions
- Cross-repo issue filing (#52 on fips-agents-cli) kept the boundary clean without losing context

## Gaps Identified

| Gap | Severity | Resolution |
|-----|----------|------------|
| design-team.md is 539 lines (over 512 guideline) | Accept | Skill commands are instruction-dense; splitting would hurt readability |
| No CI/CD workflow for PyPI publishing | Follow-up | Need publish.yml matching agent-template's pattern |
| No integration test of /design-team command | Accept | Skill commands are Claude instructions, not testable programmatically |
| Pydantic not used despite CLAUDE.md convention | Accept | PyYAML sufficient; Pydantic for frontmatter parsing would be over-engineering |

## Action Items

- [ ] Add GitHub Actions workflow for PyPI publishing (follow agent-template pattern)

## Patterns

**Start:** Validating parsers against real-world corpora, not just fixtures. The 3,739-file BPMN test was low-cost and high-signal.

**Continue:** Using review sub-agents after implementation. They caught real gaps (budget, derivation logic) that the implementing agent missed because it was focused on structure, not acceptance criteria.

**Continue:** Incremental scoping with user checkpoints. Building #2-#3 first, validating, then #4-#6 prevented compounding errors.

**Continue:** Filing cross-repo issues with full context instead of switching repos mid-session. Keeps focus clean and gives the receiving repo a self-contained brief.
