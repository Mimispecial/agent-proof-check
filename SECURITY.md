# Security

## Scope

This repository contains one bounded Intelligent Contract, direct tests, a five-validator GLSim test, and an opt-in StudioNet smoke test. It has no frontend, backend, database, token, payout, proxy upgrade, or repository secret.

## Trust model

Untrusted evidence is delimited as data, model outputs use closed schemas, and validator replay must agree before semantic state is stored.

The deployer is the verifier and names one different claimant. The claimant submits and may supplement; anyone may lodge the single public challenge; only the verifier finalizes.

## Implemented controls

- Concrete immutable GenVM runner hash; no floating runner dependency.
- Address normalization, explicit role separation, collection caps, one-time actions, and lifecycle locks.
- Bounded text plus strict `[EXPECTED]` and `[LLM_ERROR]` failure classes.
- Sorted, delimited evidence packets and independent validator replay.
- Storage is copied before nondeterministic callbacks; static audit requires zero callback reads from `self`.
- No cross-contract calls, fund custody, transfer, automated purchase, external deletion, or webhook.
- `.env`, caches, artifacts, wallet files, and local secrets are ignored. Live wallets are encrypted outside the workspace.

## Contract-specific safety properties

- Evidence-lane rules freeze before the claimant can submit proof.
- Only the designated claimant can submit or supplement the proof packet.
- Exactly one artifact label and one validation label determine the stored combined result.
- AI cannot accept or reject the claim; only the verifier records disposition.

## Residual risks

- The contract does not download, execute, or authenticate referenced artifacts or commands.
- A SUPPORTED label means the declaration contains the required indexed evidence, not that the real-world claim is true.
- Public challenge text is stored on-chain and must not contain secrets or personal data.

Do not use this contract to make legal, medical, financial, employment, admission, credit, or physical-safety decisions beyond the explicit low-risk policy in its source. A new use case requires a fresh deployment and independent domain review.

## Reporting

Report vulnerabilities privately to the repository owner with the contract name, affected method, reproduction, expected invariant, and impact. Never include private keys, wallet passwords, or personal data.
