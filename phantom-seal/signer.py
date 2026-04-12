import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3

load_dotenv()

SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL", "")
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY", "")
CHAIN_ID = int(os.getenv("CHAIN_ID", "11155111"))
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
QTST_PREFIX = bytes.fromhex("51545354")


def hash_document(file_path: str) -> dict:
    p = Path(file_path)
    if not p.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    data = p.read_bytes()
    h = hashlib.sha3_256(data).hexdigest()
    return {
        "file_path": str(p),
        "file_name": p.name,
        "size_bytes": len(data),
        "sha3_256": h,
    }


def sign_hash(sha3_hex: str) -> dict:
    message = f"PHANTOM-SEAL::{sha3_hex}"
    msg = encode_defunct(text=message)
    account = Account.from_key(WALLET_PRIVATE_KEY)
    signed = account.sign_message(msg)
    return {
        "message": message,
        "message_hash": signed.messageHash.hex(),
        "signature": signed.signature.hex(),
        "address": account.address,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


def anchor_to_chain(sha3_hex: str) -> dict:
    payload = QTST_PREFIX + bytes.fromhex(sha3_hex)
    if DRY_RUN:
        return {
            "tx_hash": None,
            "network": "dry-run",
            "data_hex": payload.hex(),
        }
    w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
    account = Account.from_key(WALLET_PRIVATE_KEY)
    tx = {
        "from": account.address,
        "to": account.address,
        "value": 0,
        "data": payload,
        "chainId": CHAIN_ID,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gasPrice": w3.eth.gas_price,
    }
    tx["gas"] = w3.eth.estimate_gas(tx)
    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()
    return {
        "tx_hash": tx_hash,
        "network": "sepolia",
        "data_hex": payload.hex(),
        "from": account.address,
        "to": account.address,
        "chain_id": CHAIN_ID,
    }


def save_result(data: dict) -> str:
    evidence_dir = Path("evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = evidence_dir / f"seal_{ts}.json"
    filename.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(filename)


def seal(file_path: str) -> dict:
    doc = hash_document(file_path)
    sig = sign_hash(doc["sha3_256"])
    anchor = anchor_to_chain(doc["sha3_256"])
    result = {
        "document": doc,
        "signature": sig,
        "anchor": anchor,
        "settings": {
            "dry_run": DRY_RUN,
            "chain_id": CHAIN_ID,
            "qtst_prefix_hex": QTST_PREFIX.hex(),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        },
    }
    result["evidence_file"] = save_result(result)
    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python signer.py <caminho_do_arquivo>")
        sys.exit(1)

    evidence = seal(sys.argv[1])
    print(json.dumps(evidence, indent=2, ensure_ascii=False))
