"""
phantom-seal CLI — verify a sealed file.

Usage:
  python -m phantom_seal.cli.verify logs/sample_aso.pdf evidence/bundle_*.json
  python -m phantom_seal.cli.verify logs/sample_aso.pdf   # uses latest bundle
"""

import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("phantom_seal.verify")

_EVIDENCE_DIR = Path(__file__).parent.parent.parent / "evidence"
_MARKER       = b"QTST"
_HASH_OFFSET  = 4
_HASH_LEN     = 32


def _resolve_bundle(arg: str | None) -> Path:
    if arg:
        p = Path(arg)
        if not p.exists():
            log.error("Bundle not found: %s", p)
            sys.exit(1)
        return p
    bundles = sorted(_EVIDENCE_DIR.glob("bundle_*.json"), reverse=True)
    if not bundles:
        log.error("No bundle in evidence/. Run seal first.")
        sys.exit(1)
    log.info("Auto-selected bundle: %s", bundles[0].name)
    return bundles[0]


def _fetch_on_chain(tx_hash: str) -> tuple[bytes | None, str]:
    if tx_hash.upper().startswith("0XDRYRUN"):
        return None, "dry-run TX — no on-chain anchor"
    rpc_url = os.getenv("RPC_URL_SEPOLIA", "").strip()
    if not rpc_url:
        return None, "RPC_URL_SEPOLIA not set — skipping on-chain check"
    try:
        from web3 import Web3
        w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 10}))
        if not w3.is_connected():
            return None, f"Cannot connect to Sepolia via {rpc_url}"
        tx       = w3.eth.get_transaction(tx_hash)
        calldata = bytes(tx["input"])
        if len(calldata) < _HASH_OFFSET + _HASH_LEN:
            return None, f"calldata too short ({len(calldata)} B)"
        if calldata[:_HASH_OFFSET] != _MARKER:
            return None, f"invalid marker {calldata[:4].hex()!r}"
        return calldata[_HASH_OFFSET:_HASH_OFFSET + _HASH_LEN], "ok"
    except Exception as exc:
        return None, str(exc)


def main() -> None:
    if len(sys.argv) < 2:
        log.error("Usage: python -m phantom_seal.cli.verify <file> [bundle.json]")
        sys.exit(1)

    target  = Path(sys.argv[1])
    bundle_path = _resolve_bundle(sys.argv[2] if len(sys.argv) >= 3 else None)

    if not target.exists():
        log.error("File not found: %s", target)
        sys.exit(1)

    bundle     = json.loads(bundle_path.read_text(encoding="utf-8"))
    tx_hash    = bundle["tx_hash"]
    stored_hex = bundle["sha3_256"]
    pqc_back   = bundle.get("pqc_backend")
    pubkey_hex = bundle.get("public_key")
    sig_hex    = bundle.get("signature")
    nonce_hex  = bundle.get("nonce")

    log.info("=== phantom-seal | Q-Trust verification ===")
    log.info("file=%s  size=%d B", target.resolve(), target.stat().st_size)
    log.info("bundle=%s", bundle_path.name)

    from phantom_seal.core import hasher, signer as _signer

    # Layer 1: local hash
    log.info("[1/3] SHA3-256 …")
    local_hash = hasher.sha3_256_file(target)
    hash_ok    = local_hash.hex() == stored_hex
    log.info("      local  : %s", local_hash.hex())
    log.info("      sealed : %s", stored_hex)
    log.info("      result : %s", "OK" if hash_ok else "FAIL")

    # Layer 2: on-chain
    log.info("[2/3] On-chain anchor …")
    anchored, chain_msg = _fetch_on_chain(tx_hash)
    if anchored is None:
        chain_match = None
        log.info("      SKIP — %s", chain_msg)
    else:
        chain_match = (anchored == local_hash)
        log.info("      on-chain: %s", anchored.hex())
        log.info("      result  : %s", "OK" if chain_match else "FAIL")

    # Layer 3: PQC signature
    log.info("[3/3] PQC signature …")
    if pubkey_hex and sig_hex and nonce_hex and pqc_back:
        pk    = bytes.fromhex(pubkey_hex)
        sig   = bytes.fromhex(sig_hex)
        nonce = bytes.fromhex(nonce_hex)
        sig_ok = _signer.verify(local_hash, nonce, pk, sig, pqc_back)
        log.info("      result : %s", "OK" if sig_ok else "FAIL")
    else:
        sig_ok = None
        log.info("      SKIP — public_key/signature/nonce absent in bundle")

    # Verdict
    log.info("=" * 50)
    hard_fail  = (not hash_ok) or (sig_ok is False)
    chain_fail = (chain_match is not None) and (not chain_match)

    checks = [
        ("Hash SHA3-256", "OK" if hash_ok else "FAIL"),
        ("On-chain Sepolia", "OK" if chain_match else ("SKIP" if chain_match is None else "FAIL")),
        ("PQC signature", "OK" if sig_ok else ("SKIP" if sig_ok is None else "FAIL")),
    ]
    for label, status in checks:
        mark = "v" if status == "OK" else ("~" if status == "SKIP" else "x")
        log.info("  [%s] %-22s: %s", mark, label, status)

    if hard_fail or chain_fail:
        log.error("ADULTERADO — file integrity compromised")
        sys.exit(1)
    else:
        log.info("INTEGRO — file matches sealed original")
        sys.exit(0)


if __name__ == "__main__":
    main()
