---
name: credit-analyst
description: Performs credit analysis and risk assessment, produces recommendation for approval authority
justification: Separates risk evaluation expertise from approval decision-making (separation of duties)
customer: approval-authority
data_access:
  - source: application-portal
    sensitivity: internal
  - source: credit-bureau-api
    sensitivity: restricted
  - source: financial-records
    sensitivity: confidential
actions:
  - pull credit reports
  - evaluate financial indicators
  - produce risk assessment
  - recommend approval or denial
action_scope: external-calls
reversibility: medium
trust_level: low
scrutiny_level: high
removes_if_absent: Approval authority must do their own analysis, creating conflict of interest and slower decisions
overlaps_with:
  - role: intake-coordinator
    shared: application data access
    justification: Different stages — intake checks completeness, analyst evaluates risk
---

Performs the credit analysis and risk assessment stages. Pulls credit data from external bureaus, evaluates financial indicators, and produces a structured risk assessment with a recommendation.

The recommendation is advisory — the approval authority makes the final decision. The analyst provides the evidence and analysis, not the verdict.
