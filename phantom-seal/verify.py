import json
import hashlib
from pathlib import Path
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3

QTST_PREFIX = bytes.fromhex("51545354")


def load_evidence(evidence_path: str) -> dict:
    return json.loads(Path(evidence_path).read_text(encoding="utf-8"))


def verify_hash(doc_path: str, evidence: dict) -> dict:
    p = Path(doc_path)
    if not p.is_file():
        return {"ok": False, "reason": "Documento não encontrado"}
    computed = hashlib.sha3_256(p.read_bytes()).hexdigest()
    expected = evidence["document"]["sha3_256"]
    ok = computed == expected
    return {
        "ok": ok,
        "computed": computed,
        "expected": expected,
        "reason": None if ok else "Hash divergente — documento modificado ou incorreto",
    }


def verify_signature(evidence: dict) -> dict:
    sig_data = evidence["signature"]
    message = sig_data["message"]
    msg = encode_defunct(text=message)
    recovered = Account.recover_message(msg, signature=bytes.fromhex(sig_data["signature"].lstrip("0x")))
    expected = sig_data["address"]
    ok = recovered.lower() == expected.lower()
    return {
        "ok": ok,
        "recovered_address": recovered,
        "expected_address": expected,
        "reason": None if ok else "Assinatura inválida — endereço recuperado diverge",
    }


def verify_transaction(evidence: dict, rpc_url: str = "") -> dict:
    tx_hash = evidence["anchor"].get("tx_hash")
    if not tx_hash:
        return {"ok": True, "skipped": True, "reason": "dry-run ou tx_hash ausente"}
    if not rpc_url:
        return {"ok": False, "reason": "RPC URL necessário para verificar transação"}
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    tx = w3.eth.get_transaction(tx_hash)
    if not tx:
        return {"ok": False, "reason": "Transação não encontrada na rede"}
    expected_payload = "0x" + QTST_PREFIX.hex() + evidence["document"]["sha3_256"]
    expected_address = evidence["signature"]["address"]
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    tx_input = tx["input"] if isinstance(tx["input"], str) else tx["input"].hex()
    checks = {
        "payload_match": tx_input.lower() == expected_payload.lower(),
        "sender_match": tx["from"].lower() == expected_address.lower(),
        "receipt_status": receipt.status == 1,
    }
    ok = all(checks.values())
    return {"ok": ok, "checks": checks, "reason": None if ok else "Falha na verificação on-chain"}


def verify(doc_path: str, evidence_path: str, rpc_url: str = "") -> dict:
    evidence = load_evidence(evidence_path)
    hash_res = verify_hash(doc_path, evidence)
    sig_res = verify_signature(evidence)
    tx_res = verify_transaction(evidence, rpc_url)
    ok = hash_res["ok"] and sig_res["ok"] and tx_res["ok"]
    return {"ok": ok, "hash": hash_res, "signature": sig_res, "transaction": tx_res}


if __name__ == "__main__":
    import sys, os

    if len(sys.argv) < 3:
        print("Uso: python verify.py <doc> <evidence.json> [rpc_url]")
        sys.exit(1)
    doc = sys.argv[1]
    evidence_path = sys.argv[2]
    rpc = sys.argv[3] if len(sys.argv) > 3 else os.getenv("SEPOLIA_RPC_URL", "")
    result = verify(doc, evidence_path, rpc)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["ok"] else 1)
