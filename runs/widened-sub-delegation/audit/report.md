# Recorded trajectory assurance

Decision: **BLOCK**

Policy: Local refund demonstration. Retained events: 8.

Passive audit of collector-declared facts; not runtime prevention or certification.

## Findings

- DELEGATION\_ATTENUATION at sub-delegation: Child delegation must be owned by its issuer and preserve or narrow parent action/scope.. Witnesses: delegation, sub-delegation
- DELEGATION\_ATTENUATION at sub-delegation: Child delegation must be owned by its issuer and preserve or narrow parent action/scope.. Witnesses: delegation, sub-delegation
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

Bundle SHA-256: `0dbec00f24783dcc19957f894e423b2a99b08351c457176a316e2270eb28252c`
