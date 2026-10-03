"""
phantom-seal CLI — seal a file.

Usage:
  python -m phantom_seal.cli.seal logs/sample_aso.pdf
  python -m phantom_seal.cli.seal logs/sample_aso.pdf --dry-run
"""

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
log = logging.getLogger("phantom_seal.seal")

_LOGS_DIR = Path(__file__).parent.parent.parent / "logs"


def main() -> None:
    args      = [a for a in sys.argv[1:] if not a.startswith("-")]
    force_dry = "--dry-run" in sys.argv or "-n" in sys.argv

    if args:
        target = Path(args[0])
    else:
        pdfs = sorted(_LOGS_DIR.glob("*.pdf"))
        if not pdfs:
            log.error("No target file. Usage: python -m phantom_seal.cli.seal <file> [--dry-run]")
            sys.exit(1)
        target = pdfs[0]

    if not target.exists():
        log.error("File not found: %s", target)
        sys.exit(1)

    rpc = os.getenv("RPC_URL_SEPOLIA", "").strip()
    key = os.getenv("WALLET_PRIVATE_KEY", "").strip()
    dry_run = force_dry or not (rpc and key)

    from phantom_seal.core import hasher, signer, anchor, auditor

    log.info("=== phantom-seal | Q-Trust sealing ===")
    log.info("file=%s size=%d bytes", target.resolve(), target.stat().st_size)
    log.info("mode=%s", "DRY-RUN" if dry_run else "REAL (Sepolia)")

    log.info("[1/4] SHA3-256 …")
    file_hash = hasher.sha3_256_file(target)
    log.info("      %s", file_hash.hex())

    log.info("[2/4] Signing with ML-DSA-65 / Dilithium3 …")
    result = signer.sign(file_hash)
    log.info("      backend=%s pk=%dB sig=%dB", result.backend, result.pk_bytes, result.sig_bytes)

    log.info("[3/4] Anchoring …")
    if dry_run:
        tx_info = anchor.anchor_dry_run(file_hash)
    else:
        tx_info = anchor.anchor(file_hash)
    log.info("      tx=%s block=%s", tx_info["tx_hash"], tx_info["block_number"])

    log.info("[4/4] Writing evidence …")
    ts           = auditor.utc_now()
    bundle_path  = auditor.write_bundle(target, file_hash, result, tx_info, ts)
    laudo_path   = auditor.write_laudo(target, file_hash, result, tx_info, ts)
    log.info("      bundle=%s", bundle_path.name)
    log.info("      laudo=%s",  laudo_path.name)

    log.info("=== SEALING COMPLETE ===")
    log.info("sha3_256=%s", file_hash.hex())
    log.info("tx=%s  network=%s", tx_info["tx_hash"], tx_info["network"])

    if dry_run:
        log.warning(
            "DRY-RUN: no TX sent. Set RPC_URL_SEPOLIA + WALLET_PRIVATE_KEY in .env "
            "and fund the wallet at https://sepoliafaucet.com for real anchoring."
        )


if __name__ == "__main__":
    main()
