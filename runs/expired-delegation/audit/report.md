# Recorded trajectory assurance

Decision: **BLOCK**

Policy: Local refund demonstration. Retained events: 7.

Passive audit of collector-declared facts; not runtime prevention or certification.

## Findings

- DELEGATION\_EXPIRED at refund: Every ancestor delegation must remain unexpired at use.. Witnesses: delegation, refund
- PERMISSION\_DENIED at refund: No direct role grant or valid delegated authority permits this completed action.. Witnesses: refund

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

Bundle SHA-256: `6d4126dea8104d7584cb28b021f32d9d50644f89a36140c1a5b75408fed86828`
