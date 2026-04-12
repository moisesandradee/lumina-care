"""
seal.py — Q-Trust phantom-seal

Pipeline completo:
  1. SHA3-256 do arquivo (stdlib — sempre real)
  2. Assinatura Dilithium3 pós-quântica:
       - Backend preferencial : oqs-python  (liboqs nativo)
       - Backend fallback real: dilithium-py (Dilithium3 puro-Python, NIST PQC)
       - Stub de último recurso: HMAC-SHA3-256 (somente se ambos ausentes)
  3. Ancoragem na Sepolia:
       - MODO REAL    : RPC_URL_SEPOLIA + WALLET_PRIVATE_KEY definidos em .env
       - MODO DRY-RUN : .env vazio/ausente → TX simulada, laudo gerado da mesma forma
  4. Gera evidence/bundle_*.json + evidence/laudo_*.md

Uso:
  python scripts/seal.py logs/sample_aso.pdf          # auto-detecta modo pelo .env
  python scripts/seal.py logs/sample_aso.pdf --dry-run  # força dry-run

Para modo real, preencha phantom-seal/.env:
  RPC_URL_SEPOLIA=https://sepolia.infura.io/v3/<PROJECT_ID>
  WALLET_PRIVATE_KEY=0x<CHAVE_PRIVADA_TESTNET>

  Obter RPC gratuito : https://app.infura.io  ou  https://www.alchemy.com
  Faucet Sepolia ETH : https://sepoliafaucet.com
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

# ── Detectar backend PQC disponível ───────────────────────────────────────────
try:
    import oqs as _oqs
    _PQC_BACKEND = "oqs"
except ModuleNotFoundError:
    _oqs = None
    try:
        from dilithium_py.dilithium import Dilithium3 as _Dilithium3
        _PQC_BACKEND = "dilithium-py"
    except ModuleNotFoundError:
        _Dilithium3 = None
        _PQC_BACKEND = "hmac-stub"

# ── Constantes ─────────────────────────────────────────────────────────────────
ALGORITHM  = "Dilithium3"
CHAIN_ID   = 11155111       # Sepolia
MARKER     = b"QTST"        # 4 bytes: Q-Trust Seal Token (prefixo do calldata)

ROOT         = Path(__file__).parent.parent
LOGS_DIR     = ROOT / "logs"
EVIDENCE_DIR = ROOT / "evidence"
TEMPLATE     = EVIDENCE_DIR / "laudo_template.md"

_BACKEND_LABEL = {
    "oqs":         "Dilithium3 (oqs-python / liboqs nativo)",
    "dilithium-py": "Dilithium3 (dilithium-py — puro-Python, NIST PQC Round 3)",
    "hmac-stub":   "HMAC-SHA3-256 (stub — instale oqs-python ou dilithium-py para PQC real)",
}


# ══════════════════════════════════════════════════════════════════════════════
# Passo 1 — Hash SHA3-256
# ══════════════════════════════════════════════════════════════════════════════
def sha3_256_file(path: Path) -> bytes:
    """Leitura em streaming (64 KB/chunk) — sem dependências externas."""
    h = hashlib.sha3_256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65_536), b""):
            h.update(chunk)
    return h.digest()


# ══════════════════════════════════════════════════════════════════════════════
# Passo 2 — Assinatura Dilithium3
# ══════════════════════════════════════════════════════════════════════════════
def _sign_oqs(file_hash: bytes) -> tuple[bytes, bytes]:
    """Dilithium3 via oqs-python (liboqs nativo). Keypair efêmero."""
    with _oqs.Signature(ALGORITHM) as signer:
        pk = signer.generate_keypair()
        sig = signer.sign(file_hash)
    return pk, sig


def _sign_dilithium_py(file_hash: bytes) -> tuple[bytes, bytes]:
    """
    Dilithium3 puro-Python (dilithium-py).
    Mesmos parâmetros NIST que oqs, sem dependência de biblioteca C.
    pk=1952 B, sk=4000 B, sig=3293 B.
    """
    pk, sk = _Dilithium3.keygen()
    sig = _Dilithium3.sign(sk, file_hash)
    return pk, sig


def _sign_hmac_stub(file_hash: bytes) -> tuple[bytes, bytes]:
    """
    HMAC-SHA3-256 stdlib — último recurso quando nenhuma lib PQC está disponível.
    NÃO é assinatura assimétrica. Apenas para demonstração local.
    """
    import hmac
    key = secrets.token_bytes(32)
    mac = hmac.new(key, file_hash, hashlib.sha3_256).digest()
    return key, mac


def sign_hash(file_hash: bytes) -> tuple[bytes, bytes]:
    """Despacha para o melhor backend PQC disponível."""
    if _PQC_BACKEND == "oqs":
        return _sign_oqs(file_hash)
    elif _PQC_BACKEND == "dilithium-py":
        return _sign_dilithium_py(file_hash)
    else:
        return _sign_hmac_stub(file_hash)


# ══════════════════════════════════════════════════════════════════════════════
# Passo 3a — Ancoragem real na Sepolia (EIP-1559)
# ══════════════════════════════════════════════════════════════════════════════
def anchor_to_sepolia(payload: bytes) -> dict:
    """
    Self-send EIP-1559 com calldata = QTST ‖ SHA3-256(arquivo).
    Lê credenciais do .env. Aguarda confirmação (~15 s na Sepolia).
    """
    from web3 import Web3

    rpc_url     = os.getenv("RPC_URL_SEPOLIA", "").strip()
    private_key = os.getenv("WALLET_PRIVATE_KEY", "").strip()

    if not rpc_url or not private_key:
        raise EnvironmentError("RPC_URL_SEPOLIA ou WALLET_PRIVATE_KEY ausentes no .env")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError(f"Sem conexao com Sepolia via {rpc_url}")

    account      = w3.eth.account.from_key(private_key)
    nonce        = w3.eth.get_transaction_count(account.address, "pending")
    base_fee     = w3.eth.gas_price
    max_priority = w3.to_wei(1, "gwei")

    tx = {
        "from":                 account.address,
        "to":                   account.address,
        "value":                0,
        "data":                 payload,
        "nonce":                nonce,
        "chainId":              CHAIN_ID,
        "maxFeePerGas":         base_fee * 2 + max_priority,
        "maxPriorityFeePerGas": max_priority,
    }
    tx["gas"] = w3.eth.estimate_gas(tx) + 5_000

    signed      = account.sign_transaction(tx)
    raw_tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"      TX enviada: {raw_tx_hash.hex()} — aguardando confirmacao...")
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
    Nenhuma TX é enviada. O tx_hash simulado é SHA3-256(b'dry-run:' + payload),
    tornando o laudo reproduzivel (mesmo payload → mesmo tx_hash simulado).
    """
    sim_tx    = "0xDRYRUN" + hashlib.sha3_256(b"dry-run:" + payload).hexdigest()[6:]
    sim_block = int(datetime.now(timezone.utc).timestamp()) % 10_000_000 + 7_000_000
    return {
        "tx_hash":      sim_tx,
        "block_number": sim_block,
        "network":      "Sepolia [DRY-RUN - nao enviado a rede]",
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
    pqc_backend: str,
    tx_info: dict,
    timestamp: str,
) -> Path:
    bundle = {
        "filename":        target.name,
        "file_size_bytes": target.stat().st_size,
        "sha3_256":        file_hash.hex(),
        "algorithm":       ALGORITHM,
        "pqc_backend":     pqc_backend,
        "alg_label":       _BACKEND_LABEL[pqc_backend],
        "public_key":      public_key.hex(),
        "signature":       signature.hex(),
        "timestamp_utc":   timestamp,
        "tx_hash":         tx_info["tx_hash"],
        "block_number":    tx_info["block_number"],
        "network":         tx_info["network"],
        "dry_run":         tx_info["dry_run"],
    }
    safe_ts   = timestamp.replace(":", "-").replace(" ", "_")
    tx_prefix = tx_info["tx_hash"].replace("0x", "")[:12]
    path = EVIDENCE_DIR / f"bundle_{safe_ts}_{tx_prefix}.json"
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_laudo(
    target: Path,
    file_hash: bytes,
    pqc_backend: str,
    tx_info: dict,
    timestamp: str,
) -> Path:
    alg_label = _BACKEND_LABEL[pqc_backend]
    template  = TEMPLATE.read_text(encoding="utf-8")
    laudo = (
        template
        .replace("{{NOME_ARQUIVO}}",  target.name)
        .replace("{{TAMANHO_BYTES}}", str(target.stat().st_size))
        .replace("{{HASH_ARQUIVO}}",  file_hash.hex())
        .replace("{{ALGORITMO_PQC}}", alg_label)
        .replace("{{DATA_UTC}}",      timestamp)
        .replace("{{TX_HASH}}",       tx_info["tx_hash"])
        .replace("{{REDE}}",          tx_info["network"])
        .replace("{{NUMERO_BLOCO}}",  str(tx_info["block_number"]))
    )
    safe_ts = timestamp.replace(":", "-").replace(" ", "_")
    path = EVIDENCE_DIR / f"laudo_{safe_ts}.md"
    path.write_text(laudo, encoding="utf-8")
    return path


# ══════════════════════════════════════════════════════════════════════════════
# Checklist de producao (impresso quando em dry-run)
# ══════════════════════════════════════════════════════════════════════════════
def print_production_checklist() -> None:
    rpc = os.getenv("RPC_URL_SEPOLIA", "").strip()
    key = os.getenv("WALLET_PRIVATE_KEY", "").strip()

    print()
    print("  O QUE FALTA PARA MODO REAL (PRODUCAO):")
    print()
    if not rpc:
        print("  [ ] RPC_URL_SEPOLIA — adicione em phantom-seal/.env")
        print("      Gratis: https://app.infura.io  ou  https://www.alchemy.com")
        print("      Ex: RPC_URL_SEPOLIA=https://sepolia.infura.io/v3/SEU_ID")
    else:
        print("  [x] RPC_URL_SEPOLIA — configurado")

    if not key:
        print("  [ ] WALLET_PRIVATE_KEY — adicione em phantom-seal/.env")
        print("      Use carteira EXCLUSIVA de testnet (nunca use chave de mainnet)")
        print("      Faucet Sepolia ETH: https://sepoliafaucet.com")
    else:
        print("  [x] WALLET_PRIVATE_KEY — configurado")

    if _PQC_BACKEND == "hmac-stub":
        print("  [ ] Biblioteca PQC real:")
        print("      pip install dilithium-py   (puro-Python, sem deps C)")
        print("      pip install oqs-python      (requer liboqs compilado)")
    else:
        print(f"  [x] PQC backend — {_BACKEND_LABEL[_PQC_BACKEND]}")

    print()
    print("  Quando .env estiver preenchido, rode sem --dry-run:")
    print("  python scripts/seal.py logs/sample_aso.pdf")
    print()


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    # Argumentos
    args     = [a for a in sys.argv[1:] if not a.startswith("-")]
    force_dry = "--dry-run" in sys.argv or "-n" in sys.argv

    # Resolver arquivo alvo
    if args:
        target = Path(args[0])
    else:
        pdfs = sorted(LOGS_DIR.glob("*.pdf"))
        if not pdfs:
            print("Uso: python scripts/seal.py <arquivo> [--dry-run]")
            sys.exit(1)
        target = pdfs[0]

    if not target.exists():
        print(f"Erro: arquivo nao encontrado: {target}")
        sys.exit(1)

    # Auto-detectar modo pelo .env
    rpc = os.getenv("RPC_URL_SEPOLIA", "").strip()
    key = os.getenv("WALLET_PRIVATE_KEY", "").strip()
    dry_run = force_dry or not (rpc and key)

    mode_label = "DRY-RUN (TX simulada)" if dry_run else "REAL (Sepolia testnet)"

    print()
    print("phantom-seal  |  Q-Trust  Selagem de Integridade")
    print("=" * 56)
    print(f"Arquivo   : {target.resolve()}")
    print(f"Tamanho   : {target.stat().st_size:,} bytes")
    print(f"PQC       : {_BACKEND_LABEL[_PQC_BACKEND]}")
    print(f"Modo      : {mode_label}")
    print()

    # ── 1. Hash ────────────────────────────────────────────────────────────────
    print("[1/4] Calculando SHA3-256 ...")
    file_hash = sha3_256_file(target)
    print(f"      {file_hash.hex()}")

    # ── 2. Assinatura PQC ──────────────────────────────────────────────────────
    print(f"[2/4] Assinando com {ALGORITHM} ({_PQC_BACKEND}) ...")
    public_key, signature = sign_hash(file_hash)
    print(f"      public_key={len(public_key)} B  assinatura={len(signature)} B")

    # ── 3. Ancoragem ───────────────────────────────────────────────────────────
    payload = MARKER + file_hash    # 36 bytes: 4 marcador + 32 hash
    if dry_run:
        print(f"[3/4] Simulando ancoragem na Sepolia (calldata={len(payload)} B) ...")
        tx_info = anchor_dry_run(payload)
        print(f"      tx_hash (simulado) : {tx_info['tx_hash']}")
        print(f"      bloco   (simulado) : {tx_info['block_number']}")
    else:
        print(f"[3/4] Ancorando na Sepolia (calldata={len(payload)} B) ...")
        tx_info = anchor_to_sepolia(payload)
        print(f"      tx_hash : {tx_info['tx_hash']}")
        print(f"      bloco   : {tx_info['block_number']}")

    # ── 4. Evidência ───────────────────────────────────────────────────────────
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print("[4/4] Gerando evidencia ...")
    bundle_path = write_bundle(
        target, file_hash, public_key, signature, _PQC_BACKEND, tx_info, timestamp
    )
    laudo_path = write_laudo(target, file_hash, _PQC_BACKEND, tx_info, timestamp)
    print(f"      bundle : {bundle_path.name}")
    print(f"      laudo  : {laudo_path.name}")

    # ── Resumo ─────────────────────────────────────────────────────────────────
    print()
    print("=" * 56)
    print("SELAGEM CONCLUIDA")
    print(f"  SHA3-256 : {file_hash.hex()}")
    print(f"  TX       : {tx_info['tx_hash']}")
    print(f"  Bloco    : {tx_info['block_number']}  ({tx_info['network']})")
    print(f"  Selado em: {timestamp} UTC")

    if dry_run:
        print_production_checklist()


if __name__ == "__main__":
    main()
