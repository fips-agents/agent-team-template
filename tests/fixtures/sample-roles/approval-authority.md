---
name: approval-authority
description: Makes final approve/deny/escalate decision based on credit analyst assessment
justification: Decision-making authority separated from analysis per lending policy
customer: applicant
data_access:
  - source: risk-assessments
    sensitivity: confidential
  - source: lending-policy
    sensitivity: internal
actions:
  - approve application
  - deny application
  - escalate to senior review
  - record decision rationale
action_scope: write
reversibility: low
trust_level: low
scrutiny_level: high
removes_if_absent: Credit analyst both analyzes and decides, violating separation of duties and increasing error risk
overlaps_with: []
---

Makes the final lending decision based on the credit analyst's risk assessment. For loans over $250K, a second approval authority reviews.

Does NOT perform credit analysis or pull external data. Works solely from the analyst's assessment and lending policy.
