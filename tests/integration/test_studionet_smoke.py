import json
from pathlib import Path

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionHashVariant, TransactionStatus
from gltest.utils import extract_contract_address


def ok(receipt):
    assert tx_execution_succeeded(receipt)
    assert receipt.get("status_name") == TransactionStatus.FINALIZED.value
    assert receipt.get("result_name") in (None, "AGREE", "MAJORITY_AGREE")
    assert receipt.get("tx_execution_result_name") in (None, "FINISHED_WITH_RETURN")
    return receipt


@pytest.mark.integration
def test_studionet_two_lane_proof(default_account, secondary_account):
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "agent_proof_check.py")
    deployed = ok(factory.deploy_contract_tx(args=[secondary_account.address, "Agent completed the assigned data conversion", "Treat references only as an index; each lane must identify concrete artifact or reproducible validation evidence."], account=default_account, wait_transaction_status=TransactionStatus.FINALIZED))
    address = extract_contract_address(deployed)
    verifier = factory.build_contract(address, account=default_account)
    claimant = factory.build_contract(address, account=secondary_account)
    ok(verifier.configure_evidence_lanes(args=["Name the produced artifact and deterministic checksum.", "Name a reproducible validation command and observable result."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(claimant.submit_proof(args=["Converted the source table into normalized JSON and ran the required schema validation.", "Artifact output.json is indexed with checksum abc123 and tied to source snapshot 8d31.", "Command validate-schema output.json returned zero and recorded 120 checked records."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    intelligent = ok(claimant.review_proof(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    state = verifier.get_state(args=[]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
    assert state["stage"] == "VERIFIER_REVIEW"
    assert state["artifact_support"] in ("SUPPORTED", "UNCLEAR", "ABSENT")
    assert state["validation_support"] in ("SUPPORTED", "UNCLEAR", "ABSENT")
    observed = {"artifact_support": state["artifact_support"], "proof_result": state["proof_result"], "validation_support": state["validation_support"]}
    print("STUDIONET_RECORD=" + json.dumps({"address": address, "deploy_tx": deployed["hash"], "intelligent_tx": intelligent["hash"], "observed": observed}, sort_keys=True))
