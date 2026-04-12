"""
seal.py — Q-Trust phantom-seal

Pipeline:
  1. SHA3-256 hash of the target file
  2. Dilithium3 (PQC) signature of the hash
  3. Anchor payload to Sepolia as calldata
  4. Persist evidence bundle (JSON) + human-readable laudo (Markdown)

Usage:
  python scripts/seal.py logs/sample_aso.pdf

Requires .env with:
  RPC_URL_SEPOLIA=https://sepolia.infura.io/v3/<PROJECT_ID>
  WALLET_PRIVATE_KEY=0x<PRIVATE_KEY>
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import oqs
from dotenv import load_dotenv
from web3 import Web3

load_dotenv(Path(__file__).parent.parent / ".env")

import os

# ── Constants ─────────────────────────────────────────────────────────────────
ALGORITHM = "Dilithium3"
CHAIN_ID = 11155111          # Sepolia
MARKER = b"QTST"             # 4-byte prefix in calldata: Q-Trust Seal Token

ROOT = Path(__file__).parent.parent
LOGS_DIR = ROOT / "logs"
EVIDENCE_DIR = ROOT / "evidence"
TEMPLATE_PATH = EVIDENCE_DIR / "laudo_template.md"


# ── Step 1: Hash ───────────────────────────────────────────────────────────────
def sha3_256_file(path: Path) -> bytes:
    """Stream-hash the file to avoid loading large files into memory."""
    h = hashlib.sha3_256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65_536), b""):
            h.update(chunk)
    return h.digest()


# ── Step 2: PQC Signature ──────────────────────────────────────────────────────
def sign_hash(file_hash: bytes) -> tuple[bytes, bytes]:
    """
    Returns (public_key, signature) using Dilithium3.
    The keypair is ephemeral; public_key is saved to the evidence bundle
    so verify.py can re-check the signature without any secret material.
    """
    with oqs.Signature(ALGORITHM) as signer:
        public_key = signer.generate_keypair()
        signature = signer.sign(file_hash)
    return public_key, signature


# ── Step 3: Anchor to Sepolia ──────────────────────────────────────────────────
def anchor_to_sepolia(payload: bytes) -> dict:
    """
    Sends a self-directed transaction to Sepolia with `payload` as calldata.
    The transaction costs ~21 000 + 68 * len(payload) gas (all zero-bytes cheaper).
    Returns tx_hash, block_number, sender address.
    """
    rpc_url = os.getenv("RPC_URL_SEPOLIA")
    private_key = os.getenv("WALLET_PRIVATE_KEY")

    if not rpc_url or not private_key:
        raise EnvironmentError(
            "Set RPC_URL_SEPOLIA and WALLET_PRIVATE_KEY in phantom-seal/.env"
        )

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to Sepolia via {rpc_url}")

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address, "pending")

    base_fee = w3.eth.gas_price
    max_priority = w3.to_wei(1, "gwei")

    tx = {
        "from": account.address,
        "to": account.address,       # self-send; no ETH transfer needed
        "value": 0,
        "data": payload,
        "nonce": nonce,
        "chainId": CHAIN_ID,
        "maxFeePerGas": base_fee * 2 + max_priority,
        "maxPriorityFeePerGas": max_priority,
    }
    tx["gas"] = w3.eth.estimate_gas(tx) + 5_000   # small safety margin

    signed = account.sign_transaction(tx)
    raw_tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

    print(f"      Waiting for confirmation (tx={raw_tx_hash.hex()[:20]}…)")
    receipt = w3.eth.wait_for_transaction_receipt(raw_tx_hash, timeout=180)

    return {
        "tx_hash": receipt.transactionHash.hex(),
        "block_number": receipt.blockNumber,
        "sender": account.address,
        "network": "Sepolia",
    }


# ── Step 4: Evidence ───────────────────────────────────────────────────────────
def write_bundle(
    target: Path,
    file_hash: bytes,
    public_key: bytes,
    signature: bytes,
    tx_info: dict,
    timestamp: str,
) -> Path:
    bundle = {
        "filename": target.name,
        "file_size_bytes": target.stat().st_size,
        "sha3_256": file_hash.hex(),
        "algorithm": ALGORITHM,
        "public_key": public_key.hex(),
        "signature": signature.hex(),
        "timestamp_utc": timestamp,
        "tx_hash": tx_info["tx_hash"],
        "block_number": tx_info["block_number"],
        "network": tx_info["network"],
    }
    safe_ts = timestamp.replace(":", "-").replace(" ", "_")
    path = EVIDENCE_DIR / f"bundle_{safe_ts}_{tx_info['tx_hash'][:12]}.json"
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_laudo(
    target: Path,
    file_hash: bytes,
    tx_info: dict,
    timestamp: str,
) -> Path:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    laudo = (
        template
        .replace("{{NOME_ARQUIVO}}", target.name)
        .replace("{{TAMANHO_BYTES}}", str(target.stat().st_size))
        .replace("{{HASH_ARQUIVO}}", file_hash.hex())
        .replace("{{ALGORITMO_PQC}}", ALGORITHM)
        .replace("{{DATA_UTC}}", timestamp)
        .replace("{{TX_HASH}}", tx_info["tx_hash"])
        .replace("{{REDE}}", tx_info["network"])
        .replace("{{NUMERO_BLOCO}}", str(tx_info["block_number"]))
    )
    safe_ts = timestamp.replace(":", "-").replace(" ", "_")
    path = EVIDENCE_DIR / f"laudo_{safe_ts}.md"
    path.write_text(laudo, encoding="utf-8")
    return path


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    if len(sys.argv) >= 2:
        target = Path(sys.argv[1])
    else:
        pdfs = sorted(LOGS_DIR.glob("*.pdf"))
        if not pdfs:
            print("Usage: python scripts/seal.py <arquivo>")
            sys.exit(1)
        target = pdfs[0]

    if not target.exists():
        print(f"Error: file not found: {target}")
        sys.exit(1)

    print(f"\nphantom-seal  |  Q-Trust integrity sealing")
    print(f"{'─' * 50}")
    print(f"File     : {target.resolve()}")
    print(f"Size     : {target.stat().st_size:,} bytes")
    print(f"Algorithm: {ALGORITHM}\n")

    # 1. Hash
    print("[1/4] Computing SHA3-256 …")
    file_hash = sha3_256_file(target)
    print(f"      {file_hash.hex()}")

    # 2. Sign
    print(f"[2/4] Signing with {ALGORITHM} (post-quantum) …")
    public_key, signature = sign_hash(file_hash)
    print(f"      pubkey={len(public_key)} B  sig={len(signature)} B")

    # 3. Anchor — payload: 4-byte marker ‖ 32-byte SHA3 hash
    payload = MARKER + file_hash
    print(f"[3/4] Anchoring to Sepolia (calldata={len(payload)} bytes) …")
    tx_info = anchor_to_sepolia(payload)
    print(f"      tx   : {tx_info['tx_hash']}")
    print(f"      block: {tx_info['block_number']}")

    # 4. Evidence
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print("[4/4] Writing evidence …")
    bundle_path = write_bundle(target, file_hash, public_key, signature, tx_info, timestamp)
    laudo_path = write_laudo(target, file_hash, tx_info, timestamp)
    print(f"      bundle : {bundle_path.name}")
    print(f"      laudo  : {laudo_path.name}")

    print(f"\n{'─' * 50}")
    print("SEALING COMPLETE")
    print(f"  SHA3-256 : {file_hash.hex()}")
    print(f"  TX       : {tx_info['tx_hash']}")
    print(f"  Block    : {tx_info['block_number']} ({tx_info['network']})")
    print(f"  Sealed at: {timestamp} UTC\n")


if __name__ == "__main__":
    main()
