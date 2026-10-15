# Recorded trajectory assurance

Decision: **BLOCK**

Policy: Local refund demonstration. Retained events: 8.

Passive audit of collector-declared facts; not runtime prevention or certification.

## Findings

- APPROVAL\_REUSE at refund-2: Completed uses exceed the recorded approval's bounded use allowance.. Witnesses: approval, refund, refund-2
- BUDGET\_EXCEEDED at refund-2: Configured trace budget rule 0 exceeded its integer limit.. Witnesses: refund, refund-2

## Coverage

- graph: EVALUATED
- permission: EVALUATED
- approval: EVALUATED
- delegation: EVALUATED
- budget: EVALUATED
- citation: EVALUATED

## Limitations

- Capture completeness, collector identity, actor identity, human approval and costs are caller declarations, not authenticated facts.
- This passive audit inspects already-recorded actions and does not prevent execution or reverse effects.
- Recorded dependency edges establish declared lineage, not physical causality or completeness of unobserved activity.
- Citations verify recorded source identity and content digests, not semantic entailment, factual truth or licensing.
- Integer costs use caller-defined units; this is not billing proof or currency conversion.
- Checksums provide integrity, not authenticity, production certification or deployment authorization.

Bundle SHA-256: `2631bc90d78c9fb662f0139e5ccf8dd623b994271f36993c6c66fc98bd68a5be`
