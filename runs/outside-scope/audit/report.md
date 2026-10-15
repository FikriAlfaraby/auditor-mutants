# Recorded trajectory assurance

Decision: **BLOCK**

Policy: Local refund demonstration. Retained events: 7.

Passive audit of collector-declared facts; not runtime prevention or certification.

## Findings

- DELEGATION\_BINDING at refund: Delegated authority does not bind this actor, action and resource.. Witnesses: delegation, refund
- PERMISSION\_DENIED at refund: No direct role grant or valid delegated authority permits this completed action.. Witnesses: refund
- APPROVAL\_BINDING at refund: Approval actor/action/resource/arguments binding does not match.. Witnesses: approval, refund

## Coverage

- APPROVAL\_NOT\_EVALUATED: Approval policy is enabled but no applicable completed action was observed.
- graph: EVALUATED
- permission: EVALUATED
- approval: NOT_EVALUATED
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

Bundle SHA-256: `82884bc4b48a004ef1c03f13326afac7fe180a47b5145d67e0e001bff0eb8a88`
