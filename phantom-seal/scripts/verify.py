"""
verify.py — Q-Trust phantom-seal

Three-layer verification:
  1. SHA3-256 of the current file == hash stored in the evidence bundle
  2. Hash anchored on-chain (Sepolia calldata) == stored hash
  3. Dilithium3 signature over the hash is valid with the stored public key

Usage:
  python scripts/verify.py logs/sample_aso.pdf evidence/bundle_<...>.json

Requires .env with:
  RPC_URL_SEPOLIA=https://sepolia.infura.io/v3/<PROJECT_ID>
"""

import hashlib
import json
import os
import sys
from pathlib import Path

import oqs
from dotenv import load_dotenv
from web3 import Web3

load_dotenv(Path(__file__).parent.parent / ".env")

# ── Constants ──────────────────────────────────────────────────────────────────
MARKER = b"QTST"
ROOT = Path(__file__).parent.parent
EVIDENCE_DIR = ROOT / "evidence"

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"


# ── Helpers ────────────────────────────────────────────────────────────────────
def sha3_256_file(path: Path) -> bytes:
    h = hashlib.sha3_256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65_536), b""):
            h.update(chunk)
    return h.digest()


def fetch_calldata(tx_hash: str) -> bytes | None:
    """Fetch raw calldata bytes from a Sepolia transaction."""
    rpc_url = os.getenv("RPC_URL_SEPOLIA")
    if not rpc_url:
        print("      WARNING: RPC_URL_SEPOLIA not set — skipping on-chain check.")
        return None

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"      WARNING: Cannot connect to Sepolia via {rpc_url} — skipping.")
        return None

    tx = w3.eth.get_transaction(tx_hash)
    return bytes(tx.input)


def verify_pqc_signature(
    file_hash: bytes,
    public_key: bytes,
    signature: bytes,
    algorithm: str,
) -> bool:
    with oqs.Signature(algorithm) as verifier:
        return verifier.verify(file_hash, signature, public_key)


# ── Check functions ────────────────────────────────────────────────────────────
def check_file_hash(target: Path, stored_hex: str) -> tuple[str, str]:
    """Returns (status, current_hex)."""
    current = sha3_256_file(target)
    stored = bytes.fromhex(stored_hex)
    match = current == stored
    return (PASS if match else FAIL), current.hex()


def check_onchain(tx_hash: str, stored_hex: str) -> tuple[str, str]:
    """Returns (status, anchored_hex_or_note)."""
    try:
        calldata = fetch_calldata(tx_hash)
        if calldata is None:
            return SKIP, "RPC unavailable"
        if calldata[:4] != MARKER:
            return FAIL, f"unexpected marker: {calldata[:4].hex()}"
        anchored = calldata[4:36]   # 32 bytes of SHA3-256
        stored = bytes.fromhex(stored_hex)
        if anchored == stored:
            return PASS, anchored.hex()
        return FAIL, f"mismatch: {anchored.hex()}"
    except Exception as exc:
        return SKIP, str(exc)


def check_signature(
    stored_hex: str,
    pubkey_hex: str,
    sig_hex: str,
    algorithm: str,
) -> tuple[str, str]:
    """Returns (status, detail)."""
    try:
        file_hash = bytes.fromhex(stored_hex)
        public_key = bytes.fromhex(pubkey_hex)
        signature = bytes.fromhex(sig_hex)
        valid = verify_pqc_signature(file_hash, public_key, signature, algorithm)
        return (PASS if valid else FAIL), ("cryptographically valid" if valid else "invalid signature")
    except Exception as exc:
        return FAIL, str(exc)


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    if len(sys.argv) < 3:
        # If only one arg, try to find the most recent bundle automatically
        if len(sys.argv) == 2:
            target = Path(sys.argv[1])
            bundles = sorted(EVIDENCE_DIR.glob("bundle_*.json"), reverse=True)
            if not bundles:
                print("No bundle found in evidence/. Run seal.py first.")
                sys.exit(1)
            bundle_path = bundles[0]
            print(f"Auto-selected bundle: {bundle_path.name}")
        else:
            print("Usage: python scripts/verify.py <arquivo> [bundle.json]")
            print("       If bundle.json is omitted the most recent one is used.")
            sys.exit(1)
    else:
        target = Path(sys.argv[1])
        bundle_path = Path(sys.argv[2])

    if not target.exists():
        print(f"Error: file not found: {target}")
        sys.exit(1)
    if not bundle_path.exists():
        print(f"Error: bundle not found: {bundle_path}")
        sys.exit(1)

    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    algorithm = bundle.get("algorithm", "Dilithium3")

    print(f"\nphantom-seal  |  Q-Trust integrity verification")
    print(f"{'─' * 60}")
    print(f"File       : {target.resolve()}")
    print(f"Bundle     : {bundle_path.name}")
    print(f"Sealed at  : {bundle.get('timestamp_utc', 'unknown')} UTC")
    print(f"TX         : {bundle.get('tx_hash', 'unknown')}")
    print(f"Block      : {bundle.get('block_number', 'unknown')} ({bundle.get('network', '?')})\n")

    # 1. File hash
    print("[1/3] Verifying SHA3-256 hash …")
    hash_status, current_hex = check_file_hash(target, bundle["sha3_256"])
    print(f"      stored : {bundle['sha3_256']}")
    print(f"      current: {current_hex}")
    print(f"      result : {hash_status}")

    # 2. On-chain anchor
    print(f"\n[2/3] Verifying on-chain anchor ({bundle.get('network', 'Sepolia')}) …")
    chain_status, chain_detail = check_onchain(bundle["tx_hash"], bundle["sha3_256"])
    print(f"      anchored hash : {chain_detail}")
    print(f"      result        : {chain_status}")

    # 3. PQC signature
    print(f"\n[3/3] Verifying {algorithm} signature …")
    sig_status, sig_detail = check_signature(
        bundle["sha3_256"],
        bundle["public_key"],
        bundle["signature"],
        algorithm,
    )
    print(f"      detail : {sig_detail}")
    print(f"      result : {sig_status}")

    # ── Summary ────────────────────────────────────────────────────────────────
    print(f"\n{'─' * 60}")
    print("VERIFICATION SUMMARY")
    print(f"  [{'✓' if hash_status  == PASS else '✗' if hash_status  == FAIL else '~'}] File hash (SHA3-256)      : {hash_status}")
    print(f"  [{'✓' if chain_status == PASS else '✗' if chain_status == FAIL else '~'}] On-chain anchor (Sepolia) : {chain_status}")
    print(f"  [{'✓' if sig_status   == PASS else '✗' if sig_status   == FAIL else '~'}] PQC signature ({algorithm}): {sig_status}")

    hard_fail = hash_status == FAIL or sig_status == FAIL or chain_status == FAIL
    inconclusive = SKIP in (chain_status,) and not hard_fail

    print()
    if hard_fail:
        print("  RESULT: INTEGRITY FAILURE — the file may have been tampered with.")
        sys.exit(1)
    elif inconclusive:
        print("  RESULT: PARTIAL PASS — file hash and PQC signature are valid.")
        print("          On-chain check was skipped (set RPC_URL_SEPOLIA to enable).")
        sys.exit(0)
    else:
        print("  RESULT: INTEGRITY CONFIRMED — file is identical to the sealed original.")
        sys.exit(0)


if __name__ == "__main__":
    main()
