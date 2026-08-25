from pathlib import Path
import json

CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "agent_proof_check.py"
SDK = "v0.2.16"
PROMPT = "Review two declared evidence lanes"
STANDARD = "Treat references only as an index. Each lane must identify a concrete artifact or reproducible validation record, and no reference is assumed authentic or externally verified."


def address(account):
    return "0x" + account.hex()


def proof(vm, direct_deploy, verifier, claimant):
    vm.sender = verifier
    contract = direct_deploy(str(CONTRACT), address(claimant), "Agent completed the assigned data conversion", STANDARD, sdk_version=SDK)
    contract.configure_evidence_lanes(
        "Name the produced artifact and a deterministic checksum tied to the declared conversion.",
        "Name a reproducible validation command and its observable result for the produced artifact.",
    )
    vm.sender = claimant
    contract.submit_proof(
        "Converted the source table into the requested normalized JSON artifact and ran the required schema validation.",
        "Artifact output.json is indexed with checksum abc123 and tied to source snapshot 8d31.",
        "Command validate-schema output.json returned exit code zero and recorded 120 checked records.",
    )
    return contract


def test_supported_lanes_and_verifier_acceptance(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = proof(direct_vm, direct_deploy, direct_alice, direct_bob)
    direct_vm.mock_llm(PROMPT, json.dumps({"artifact_support": "SUPPORTED", "validation_support": "SUPPORTED"}))
    contract.review_proof()
    leader = direct_vm._captured_validators[-1][0]
    assert direct_vm.run_validator(leader_result=leader) is True
    direct_vm.sender = direct_alice
    contract.finalize_review("ACCEPT", "Both frozen evidence lanes contain concrete indexed support for the declared work.")
    assert contract.get_state()["proof_result"] == "SUFFICIENT"
    assert contract.get_state()["disposition"] == "ACCEPT"


def test_partial_proof_supplement_and_independent_challenge(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = proof(direct_vm, direct_deploy, direct_alice, direct_bob)
    direct_vm.mock_llm(PROMPT, json.dumps({"artifact_support": "SUPPORTED", "validation_support": "UNCLEAR"}))
    contract.review_proof()
    direct_vm.sender = direct_bob
    contract.add_supplement("The validation supplement names the full command, zero exit code, schema version, and all 120 checked record identifiers.")
    direct_vm.clear_mocks()
    direct_vm.mock_llm(PROMPT, json.dumps({"artifact_support": "SUPPORTED", "validation_support": "SUPPORTED"}))
    contract.review_proof()
    direct_vm.sender = direct_charlie
    contract.file_challenge("The artifact checksum reference names a different output filename and should be examined by the verifier.")
    direct_vm.sender = direct_alice
    contract.finalize_review("REJECT", "Rejected after the verifier considered the independent filename mismatch challenge.")
    assert contract.get_state()["supplement_used"] is True
    assert contract.get_state()["challenger"] == address(direct_charlie).lower()


def test_claimant_role_and_bad_support_label_fail_closed(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    direct_vm.sender = direct_alice
    contract = direct_deploy(str(CONTRACT), address(direct_bob), "Agent completed the assigned data conversion", STANDARD, sdk_version=SDK)
    contract.configure_evidence_lanes("Name the produced artifact and deterministic checksum.", "Name a reproducible validation command and result.")
    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("only_claimant"):
        contract.submit_proof("An unauthorized work summary must not enter this designated proof case.", "Unauthorized artifact reference with checksum data.", "Unauthorized validation command and result data.")
    direct_vm.sender = direct_bob
    contract.submit_proof("Converted the table and recorded the produced artifact plus a validation result.", "Artifact output.json has checksum abc123.", "Validation command returned exit code zero for 120 records.")
    direct_vm.mock_llm(PROMPT, json.dumps({"artifact_support": "CERTAIN", "validation_support": "SUPPORTED"}))
    with direct_vm.expect_revert("invalid_support_label"):
        contract.review_proof()
    assert contract.get_state()["stage"] == "READY_FOR_REVIEW"
