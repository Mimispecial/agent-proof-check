from pathlib import Path
import json

from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address

PROMPT = "Review two declared evidence lanes"


def context():
    validators = get_validator_factory().batch_create_mock_validators(5, mock_llm_response={"nondet_exec_prompt": {PROMPT: json.dumps({"artifact_support": "SUPPORTED", "validation_support": "SUPPORTED"})}})
    return {"validators": [validator.to_dict() for validator in validators]}


def ok(receipt):
    assert tx_execution_succeeded(receipt)


def test_five_validator_two_lane_proof():
    verifier_account, claimant_account = create_accounts(2)
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "agent_proof_check.py")
    deployed = factory.deploy_contract_tx(args=[claimant_account.address, "Agent completed the assigned data conversion", "Treat references only as an index; each lane must identify concrete artifact or reproducible validation evidence."], account=verifier_account, wait_transaction_status=TransactionStatus.FINALIZED)
    ok(deployed)
    address = extract_contract_address(deployed)
    verifier = factory.build_contract(address, account=verifier_account)
    claimant = factory.build_contract(address, account=claimant_account)
    ok(verifier.configure_evidence_lanes(args=["Name the produced artifact and deterministic checksum.", "Name a reproducible validation command and observable result."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(claimant.submit_proof(args=["Converted the source table into normalized JSON and ran the required schema validation.", "Artifact output.json is indexed with checksum abc123 and tied to source snapshot 8d31.", "Command validate-schema output.json returned zero and recorded 120 checked records."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(claimant.review_proof(args=[]).transact(transaction_context=context(), wait_transaction_status=TransactionStatus.FINALIZED))
    ok(verifier.finalize_review(args=["ACCEPT", "Both frozen evidence lanes contain concrete indexed support for the declared work."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    assert verifier.get_state(args=[]).call()["disposition"] == "ACCEPT"
