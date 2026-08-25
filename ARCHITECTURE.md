# Architecture

## Deployment boundary

Deploy once per claim and claimant. Reuse the source through a fresh deployment when the claim, evidence rules, or verifier relationship changes.

Constructor data establishes the deployment subject and fixed role boundary. Later writes add only the bounded records permitted by the lifecycle; a completed instance cannot be reopened.

## Participants

The deployer is the verifier and names one different claimant. The claimant submits and may supplement; anyone may lodge the single public challenge; only the verifier finalizes.

Addresses are normalized before authorization comparisons. Role checks and lifecycle gates execute before semantic assessment.

## State machine

`RULE_SETUP → AWAITING_PROOF → READY_FOR_REVIEW → VERIFIER_REVIEW → COMPLETE, with one bounded supplement loop and one public challenge`

The phase-like field is the primary lifecycle lock. Each write advances that path, performs a documented bounded loop, or fails with an `[EXPECTED]` user error.

## Evidence assembly

The stored claim, evidence policy, artifact-lane rule, validation-lane rule, work declaration, lane evidence, optional supplement, and optional challenge. Artifact references are not fetched or authenticated.

Before consensus, the contract normalizes bounded text, copies required storage into plain local values, serializes a sorted JSON packet, and places it between explicit START/END delimiters. Nondeterministic callbacks do not read contract storage.

## Consensus boundary

Label each frozen evidence lane SUPPORTED, UNCLEAR, or ABSENT; the contract derives the combined proof result deterministically.

The leader callback validates exact JSON shape, field types, closed labels, masks or codes, and length bounds. A validator reruns the same semantic operation and rejects disagreement before state is committed.

## Deterministic boundary

Lane setup, claimant authorization, combined-result derivation, supplement limit, challenge record, and verifier disposition are deterministic.

Important invariants:

- Evidence-lane rules freeze before the claimant can submit proof.
- Only the designated claimant can submit or supplement the proof packet.
- Exactly one artifact label and one validation label determine the stored combined result.
- AI cannot accept or reject the claim; only the verifier records disposition.

No method sends value, pays rewards, escrows assets, deletes external data, calls another contract, or invokes a webhook.

## Failure model

- Invalid caller input or lifecycle use raises `[EXPECTED]` and leaves state unchanged.
- Malformed or out-of-policy model output raises `[LLM_ERROR]` and cannot be stored.
- Validator disagreement cannot commit the semantic result.
- StudioNet proof reads explicitly target `LATEST_FINAL`, avoiding stale pre-final state.
