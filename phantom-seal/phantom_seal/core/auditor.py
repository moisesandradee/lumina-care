"""
Evidence writer — bundle JSON and laudo Markdown.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .signer import SignResult

log = logging.getLogger(__name__)

_ROOT         = Path(__file__).parent.parent.parent
EVIDENCE_DIR  = _ROOT / "evidence"
TEMPLATE_PATH = EVIDENCE_DIR / "laudo_template.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def write_bundle(
    target: Path,
    file_hash: bytes,
    sign_result: SignResult,
    tx_info: dict,
    timestamp: str,
) -> Path:
    bundle = {
        "filename":        target.name,
        "file_size_bytes": target.stat().st_size,
        "sha3_256":        file_hash.hex(),
        "algorithm":       sign_result.algorithm,
        "pqc_backend":     sign_result.backend,
        "audit_level":     sign_result.audit_level,
        "public_key":      sign_result.public_key.hex(),
        "signature":       sign_result.signature.hex(),
        "nonce":           sign_result.nonce.hex(),
        "signing_input":   sign_result.signing_input.hex(),
        "timestamp_utc":   timestamp,
        "tx_hash":         tx_info["tx_hash"],
        "block_number":    tx_info["block_number"],
        "network":         tx_info["network"],
        "wallet":          tx_info.get("wallet", "N/A"),
        "dry_run":         tx_info["dry_run"],
    }
    EVIDENCE_DIR.mkdir(exist_ok=True)
    safe_ts   = timestamp.replace(":", "-").replace(" ", "_")
    tx_prefix = tx_info["tx_hash"].replace("0x", "")[:12]
    path = EVIDENCE_DIR / f"bundle_{safe_ts}_{tx_prefix}.json"
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("bundle written path=%s", path.name)
    return path


def write_laudo(
    target: Path,
    file_hash: bytes,
    sign_result: SignResult,
    tx_info: dict,
    timestamp: str,
) -> Path:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    laudo = (
        template
        .replace("{{NOME_ARQUIVO}}",    target.name)
        .replace("{{TAMANHO_BYTES}}",   str(target.stat().st_size))
        .replace("{{HASH_ARQUIVO}}",    file_hash.hex())
        .replace("{{ALGORITMO_PQC}}",   sign_result.algorithm)
        .replace("{{BIBLIOTECA_PQC}}",  sign_result.backend)
        .replace("{{NIVEL_AUDITORIA}}", sign_result.audit_level)
        .replace("{{DATA_UTC}}",        timestamp)
        .replace("{{TX_HASH}}",         tx_info["tx_hash"])
        .replace("{{REDE}}",            tx_info["network"])
        .replace("{{NUMERO_BLOCO}}",    str(tx_info["block_number"]))
        .replace("{{WALLET}}",          tx_info.get("wallet", "N/A"))
    )
    safe_ts = timestamp.replace(":", "-").replace(" ", "_")
    path = EVIDENCE_DIR / f"laudo_{safe_ts}.md"
    path.write_text(laudo, encoding="utf-8")
    log.info("laudo written path=%s", path.name)
    return path
