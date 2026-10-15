# Recorded trajectory assurance

Decision: **BLOCK**

Policy: Local refund demonstration. Retained events: 7.

Passive audit of collector-declared facts; not runtime prevention or certification.

## Findings

- UNKNOWN\_ACTOR at refund: Completed action actor is absent from the policy.. Witnesses: refund
- DELEGATION\_BINDING at refund: Delegated authority does not bind this actor, action and resource.. Witnesses: delegation, refund
- PERMISSION\_DENIED at refund: No direct role grant or valid delegated authority permits this completed action.. Witnesses: refund
- APPROVAL\_BINDING at refund: Approval actor/action/resource/arguments binding does not match.. Witnesses: approval, refund

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

Bundle SHA-256: `484f0574f32f0e46456b6317816ceae7d75695c204c9ed36415b520e5e2d4f1c`
