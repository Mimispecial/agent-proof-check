# Agent Proof Check

Screens a designated claimant's completion proof across separate artifact and reproducible-validation lanes before a human verifier records the disposition.

## Why it is an Intelligent Contract

Label each frozen evidence lane SUPPORTED, UNCLEAR, or ABSENT; the contract derives the combined proof result deterministically. GenLayer validators independently replay that semantic judgment before it becomes shared state. Lane setup, claimant authorization, combined-result derivation, supplement limit, challenge record, and verifier disposition are deterministic.

## Reusable deployment model

Deploy once per claim and claimant. Reuse the source through a fresh deployment when the claim, evidence rules, or verifier relationship changes.

A completed deployment is an auditable record and is not reset or silently repurposed. Reuse means deploying the same reviewed source with new constructor data.

## Roles and workflow

The deployer is the verifier and names one different claimant. The claimant submits and may supplement; anyone may lodge the single public challenge; only the verifier finalizes.

State path: `RULE_SETUP → AWAITING_PROOF → READY_FOR_REVIEW → VERIFIER_REVIEW → COMPLETE, with one bounded supplement loop and one public challenge`

## Evidence boundary

The stored claim, evidence policy, artifact-lane rule, validation-lane rule, work declaration, lane evidence, optional supplement, and optional challenge. Artifact references are not fetched or authenticated.

## Core invariants

- Evidence-lane rules freeze before the claimant can submit proof.
- Only the designated claimant can submit or supplement the proof packet.
- Exactly one artifact label and one validation label determine the stored combined result.
- AI cannot accept or reject the claim; only the verifier records disposition.

## Public interface

Write methods: `add_supplement, configure_evidence_lanes, file_challenge, finalize_review, review_proof, submit_proof`

View methods: `get_evidence_rules, get_policy, get_state`

`get_policy` exposes the machine-readable operating boundary and confirms that this contract never custodies funds.

## Verification

Pinned GenVM runner: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`

```powershell
python -m pip install -r requirements.txt
genvm-lint check contracts/agent_proof_check.py
genvm-lint typecheck contracts/agent_proof_check.py
pytest tests/direct -q
python tests/run_glsim.py --port 4000 --validators 5 --no-browser
gltest tests/integration/test_glsim_consensus.py --network localnet -q
```

The StudioNet smoke test is opt-in and uses three disposable Mimi-only accounts protected outside the workspace. It asserts finalized successful execution and reads committed state with `LATEST_FINAL`.

## Final StudioNet proof

- Contract: https://explorer-studio.genlayer.com/address/0x910B9aFeD093CcC2EB856f5F7224a7e08e6A0c18
- Studio import: https://studio.genlayer.com/?import-contract=0x910B9aFeD093CcC2EB856f5F7224a7e08e6A0c18
- Deployment transaction: https://explorer-studio.genlayer.com/tx/0xa7670e2c5337f406e961e1992ae58ed88f91a568084ad1a9719cd0fa1d5bb9c7
- Intelligent transaction: https://explorer-studio.genlayer.com/tx/0x3b17c84a2bd97301e3edc8555b5e19c13e34078344753313c34eec7495b91980
- Observed committed state: `{"artifact_support":"SUPPORTED","proof_result":"SUFFICIENT","validation_support":"SUPPORTED"}`
- Audited source SHA-256: `b5ed66adf8bb8a3332f2ff1314b9ad5de93a7758c17435f580871f2e1231f291`

## Limitations

- The contract does not download, execute, or authenticate referenced artifacts or commands.
- A SUPPORTED label means the declaration contains the required indexed evidence, not that the real-world claim is true.
- Public challenge text is stored on-chain and must not contain secrets or personal data.

## Repository map

- `contracts/agent_proof_check.py` — Intelligent Contract source
- `tests/direct` — hardened leader/validator and lifecycle tests
- `tests/integration/test_glsim_consensus.py` — five-validator simulator flow
- `tests/integration/test_studionet_smoke.py` — live opt-in proof
- `deployments/studionet.json` — source-bound public deployment evidence
- `ARCHITECTURE.md`, `SOURCE_POLICY.md`, `SECURITY.md`, `AUDIT.md` — reviewer material

License: MIT.
