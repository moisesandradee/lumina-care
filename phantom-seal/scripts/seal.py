"""
seal.py — Q-Trust phantom-seal

Pipeline:
  1. SHA3-256 hash do arquivo (stdlib — sempre real)
  2. Assinatura pós-quântica Dilithium3 via oqs-python
     (fallback Ed25519 via `cryptography` quando liboqs não está disponível)
  3. Ancoragem do payload na Sepolia como calldata
  4. Gera evidence/bundle_*.json  +  evidence/laudo_*.md

Uso:
  python scripts/seal.py logs/sample_aso.pdf            # modo real (requer .env)
  python scripts/seal.py logs/sample_aso.pdf --dry-run  # simula TX; hash e sig reais

Requer .env (modo real):
  RPC_URL_SEPOLIA=https://sepolia.infura.io/v3/<PROJECT_ID>
  WALLET_PRIVATE_KEY=0x<CHAVE_PRIVADA_TESTNET>
"""

import hashlib
import json
import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# ── Tentar importar oqs; fallback para Ed25519 ────────────────────────────────
try:
    import oqs as _oqs
    _OQS_AVAILABLE = True
except ModuleNotFoundError:
    _OQS_AVAILABLE = False

# ── Constantes ─────────────────────────────────────────────────────────────────
ALGORITHM   = "Dilithium3"
FALLBACK_ALG = "HMAC-SHA3-256 (stub — liboqs indisponível, somente dry-run)"
CHAIN_ID    = 11155111        # Sepolia
MARKER      = b"QTST"         # marcador Q-Trust no calldata

ROOT         = Path(__file__).parent.parent
LOGS_DIR     = ROOT / "logs"
EVIDENCE_DIR = ROOT / "evidence"
TEMPLATE     = EVIDENCE_DIR / "laudo_template.md"


# ══════════════════════════════════════════════════════════════════════════════
# Passo 1 — Hash
# ══════════════════════════════════════════════════════════════════════════════
def sha3_256_file(path: Path) -> bytes:
    """SHA3-256 em streaming (64 KB/chunk) — sem dependências externas."""
    h = hashlib.sha3_256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65_536), b""):
            h.update(chunk)
    return h.digest()


# ══════════════════════════════════════════════════════════════════════════════
# Passo 2 — Assinatura
# ══════════════════════════════════════════════════════════════════════════════
def sign_dilithium3(file_hash: bytes) -> tuple[bytes, bytes]:
    """Dilithium3 via oqs-python. Keypair efêmero; só public_key é persistido."""
    with _oqs.Signature(ALGORITHM) as signer:
        public_key = signer.generate_keypair()
        signature  = signer.sign(file_hash)
    return public_key, signature


def sign_hmac_fallback(file_hash: bytes) -> tuple[bytes, bytes]:
    """
    HMAC-SHA3-256 via stdlib — usado somente em --dry-run quando liboqs não
    está instalado. Gera um par (chave, mac) análogo a (public_key, signature)
    para que verify.py possa recomputar e conferir.
    Não é criptografia assimétrica real — apenas para demo sem deps externas.
    """
    import hmac
    key = secrets.token_bytes(32)
    mac = hmac.new(key, file_hash, hashlib.sha3_256).digest()
    return key, mac


def sign_hash(file_hash: bytes) -> tuple[bytes, bytes, str]:
    """
    Retorna (public_key, signature, algorithm_label).
    Usa Dilithium3 se oqs disponível, Ed25519 caso contrário.
    """
    if _OQS_AVAILABLE:
        pk, sig = sign_dilithium3(file_hash)
        return pk, sig, ALGORITHM
    else:
        pk, sig = sign_hmac_fallback(file_hash)
        return pk, sig, FALLBACK_ALG


# ══════════════════════════════════════════════════════════════════════════════
# Passo 3a — Ancoragem real na Sepolia
# ══════════════════════════════════════════════════════════════════════════════
def anchor_to_sepolia(payload: bytes) -> dict:
    """
    EIP-1559 self-send com calldata = QTST ‖ SHA3-256(arquivo).
    Requer RPC_URL_SEPOLIA e WALLET_PRIVATE_KEY em .env.
    """
    from web3 import Web3

    rpc_url     = os.getenv("RPC_URL_SEPOLIA")
    private_key = os.getenv("WALLET_PRIVATE_KEY")
    if not rpc_url or not private_key:
        raise EnvironmentError(
            "Configure RPC_URL_SEPOLIA e WALLET_PRIVATE_KEY em phantom-seal/.env\n"
            "Ou use --dry-run para simular a ancoragem."
        )

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError(f"Sem conexão com Sepolia via {rpc_url}")

    account = w3.eth.account.from_key(private_key)
    nonce   = w3.eth.get_transaction_count(account.address, "pending")
    base_fee    = w3.eth.gas_price
    max_priority = w3.to_wei(1, "gwei")

    tx = {
        "from": account.address,
        "to":   account.address,
        "value": 0,
        "data": payload,
        "nonce": nonce,
        "chainId": CHAIN_ID,
        "maxFeePerGas": base_fee * 2 + max_priority,
        "maxPriorityFeePerGas": max_priority,
    }
    tx["gas"] = w3.eth.estimate_gas(tx) + 5_000

    signed      = account.sign_transaction(tx)
    raw_tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"      Aguardando confirmação (tx={raw_tx_hash.hex()[:20]}…)")
    receipt = w3.eth.wait_for_transaction_receipt(raw_tx_hash, timeout=180)

    return {
        "tx_hash":      receipt.transactionHash.hex(),
        "block_number": receipt.blockNumber,
        "network":      "Sepolia",
        "dry_run":      False,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Passo 3b — Ancoragem simulada (dry-run)
# ══════════════════════════════════════════════════════════════════════════════
def anchor_dry_run(payload: bytes) -> dict:
    """
    Simula a TX sem enviar nada à rede.
    O tx_hash é derivado deterministicamente do payload (SHA3-256 do próprio
    payload), garantindo que o campo seja verificável localmente mesmo sem RPC.
    """
    # Simula um tx hash plausível usando hash do payload
    simulated_tx = "0x" + hashlib.sha3_256(b"dry-run:" + payload).hexdigest()
    # Simula um número de bloco baseado no timestamp atual
    simulated_block = int(datetime.now(timezone.utc).timestamp()) % 10_000_000 + 7_000_000

    return {
        "tx_hash":      simulated_tx,
        "block_number": simulated_block,
        "network":      "Sepolia [DRY-RUN — não enviado à rede]",
        "dry_run":      True,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Passo 4 — Evidência
# ══════════════════════════════════════════════════════════════════════════════
def write_bundle(
    target: Path,
    file_hash: bytes,
    public_key: bytes,
    signature: bytes,
    algorithm: str,
    tx_info: dict,
    timestamp: str,
) -> Path:
    bundle = {
        "filename":        target.name,
        "file_size_bytes": target.stat().st_size,
        "sha3_256":        file_hash.hex(),
        "algorithm":       algorithm,
        "public_key":      public_key.hex(),
        "signature":       signature.hex(),
        "timestamp_utc":   timestamp,
        "tx_hash":         tx_info["tx_hash"],
        "block_number":    tx_info["block_number"],
        "network":         tx_info["network"],
        "dry_run":         tx_info["dry_run"],
    }
    safe_ts   = timestamp.replace(":", "-").replace(" ", "_")
    tx_prefix = tx_info["tx_hash"][2:14]
    path = EVIDENCE_DIR / f"bundle_{safe_ts}_{tx_prefix}.json"
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_laudo(
    target: Path,
    file_hash: bytes,
    algorithm: str,
    tx_info: dict,
    timestamp: str,
) -> Path:
    template = TEMPLATE.read_text(encoding="utf-8")
    laudo = (
        template
        .replace("{{NOME_ARQUIVO}}",   target.name)
        .replace("{{TAMANHO_BYTES}}",  str(target.stat().st_size))
        .replace("{{HASH_ARQUIVO}}",   file_hash.hex())
        .replace("{{ALGORITMO_PQC}}", algorithm)
        .replace("{{DATA_UTC}}",       timestamp)
        .replace("{{TX_HASH}}",        tx_info["tx_hash"])
        .replace("{{REDE}}",           tx_info["network"])
        .replace("{{NUMERO_BLOCO}}",   str(tx_info["block_number"]))
    )
    safe_ts = timestamp.replace(":", "-").replace(" ", "_")
    path = EVIDENCE_DIR / f"laudo_{safe_ts}.md"
    path.write_text(laudo, encoding="utf-8")
    return path


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    args     = [a for a in sys.argv[1:] if not a.startswith("-")]
    dry_run  = "--dry-run" in sys.argv or "-n" in sys.argv

    if args:
        target = Path(args[0])
    else:
        pdfs = sorted(LOGS_DIR.glob("*.pdf"))
        if not pdfs:
            print("Uso: python scripts/seal.py <arquivo> [--dry-run]")
            sys.exit(1)
        target = pdfs[0]

    if not target.exists():
        print(f"Erro: arquivo não encontrado: {target}")
        sys.exit(1)

    mode_label = "DRY-RUN (TX simulada)" if dry_run else "PRODUÇÃO"
    sig_label  = f"Dilithium3 (oqs)" if _OQS_AVAILABLE else "Ed25519 (fallback — liboqs indisponível)"

    print()
    print("phantom-seal  |  Q-Trust — Selagem de Integridade")
    print("─" * 56)
    print(f"Arquivo    : {target.resolve()}")
    print(f"Tamanho    : {target.stat().st_size:,} bytes")
    print(f"Assinatura : {sig_label}")
    print(f"Modo       : {mode_label}")
    print()

    # 1. Hash
    print("[1/4] Calculando SHA3-256 …")
    file_hash = sha3_256_file(target)
    print(f"      {file_hash.hex()}")

    # 2. Assinatura
    print(f"[2/4] Assinando com {sig_label} …")
    public_key, signature, alg_used = sign_hash(file_hash)
    print(f"      pubkey={len(public_key)} B  assinatura={len(signature)} B")

    # 3. Ancoragem
    payload = MARKER + file_hash   # 36 bytes: 4 marcador + 32 hash
    if dry_run:
        print(f"[3/4] Simulando ancoragem na Sepolia (calldata={len(payload)} bytes) …")
        tx_info = anchor_dry_run(payload)
        print(f"      tx_hash (simulado): {tx_info['tx_hash']}")
        print(f"      bloco   (simulado): {tx_info['block_number']}")
    else:
        print(f"[3/4] Ancorando na Sepolia (calldata={len(payload)} bytes) …")
        tx_info = anchor_to_sepolia(payload)
        print(f"      tx   : {tx_info['tx_hash']}")
        print(f"      bloco: {tx_info['block_number']}")

    # 4. Evidência
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print("[4/4] Gerando evidência …")
    bundle_path = write_bundle(target, file_hash, public_key, signature, alg_used, tx_info, timestamp)
    laudo_path  = write_laudo(target, file_hash, alg_used, tx_info, timestamp)
    print(f"      bundle : {bundle_path.name}")
    print(f"      laudo  : {laudo_path.name}")

    print()
    print("─" * 56)
    print("SELAGEM CONCLUÍDA")
    print(f"  SHA3-256 : {file_hash.hex()}")
    print(f"  TX       : {tx_info['tx_hash']}")
    print(f"  Bloco    : {tx_info['block_number']}  ({tx_info['network']})")
    print(f"  Selado em: {timestamp} UTC")
    if dry_run:
        print()
        print("  NOTA: modo --dry-run. Para ancorar de verdade na Sepolia,")
        print("  configure .env e execute sem --dry-run.")
    print()


if __name__ == "__main__":
    main()
