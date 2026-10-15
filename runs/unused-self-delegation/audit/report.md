# Recorded trajectory assurance

Decision: **BLOCK**

Policy: Local refund demonstration. Retained events: 8.

Passive audit of collector-declared facts; not runtime prevention or certification.

## Findings

- DELEGATION\_ISSUER\_PERMISSION at rogue-delegation: Root issuer lacks direct permission for the delegated scope.. Witnesses: rogue-delegation

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

Bundle SHA-256: `8c7856aad8c99d318fb4716f31eacde58174f41d2a7a07fd2459d6d47545e5c9`
