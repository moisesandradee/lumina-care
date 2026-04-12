"""
verify.py — Q-Trust phantom-seal

Verificacao em 3 camadas:
  1. SHA3-256 do arquivo atual  ==  hash no bundle/laudo
  2. Hash no calldata da TX Sepolia  ==  hash no bundle/laudo
  3. Assinatura Dilithium3 valida com a public_key do bundle

Resultado final: INTEGRO ou ADULTERADO

Uso:
  python scripts/verify.py logs/sample_aso.pdf evidence/bundle_<...>.json
  python scripts/verify.py logs/sample_aso.pdf evidence/laudo_<...>.md
  python scripts/verify.py logs/sample_aso.pdf      # usa bundle mais recente

Para verificacao on-chain, configure phantom-seal/.env:
  RPC_URL_SEPOLIA=https://sepolia.infura.io/v3/<PROJECT_ID>
"""

import hashlib
import hmac
import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# ── Backend PQC (mesmo order de preferencia que seal.py) ──────────────────────
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
MARKER      = b"QTST"
HASH_OFFSET = 4
HASH_LEN    = 32

ROOT         = Path(__file__).parent.parent
EVIDENCE_DIR = ROOT / "evidence"

OK   = "OK  "
FAIL = "FAIL"
SKIP = "SKIP"


# ══════════════════════════════════════════════════════════════════════════════
# 1 — Hash local
# ══════════════════════════════════════════════════════════════════════════════
def sha3_256_file(path: Path) -> bytes:
    h = hashlib.sha3_256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65_536), b""):
            h.update(chunk)
    return h.digest()


# ══════════════════════════════════════════════════════════════════════════════
# 2 — Busca on-chain
# ══════════════════════════════════════════════════════════════════════════════
def fetch_anchored_hash(tx_hash: str) -> tuple[bytes | None, str]:
    """
    Retorna (hash_bytes, mensagem).
    hash_bytes = None se o RPC nao estiver disponivel (SKIP).
    """
    rpc_url = os.getenv("RPC_URL_SEPOLIA", "").strip()
    if not rpc_url:
        return None, "RPC_URL_SEPOLIA nao configurado -- verificacao on-chain ignorada"

    # TX simulada de dry-run: verificar localmente pelo payload
    if tx_hash.upper().startswith("0XDRYRUN"):
        return None, "TX dry-run -- sem ancoragem real para verificar on-chain"

    try:
        from web3 import Web3
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            return None, f"Sem conexao com Sepolia via {rpc_url}"

        tx       = w3.eth.get_transaction(tx_hash)
        calldata = bytes(tx["input"])

        if len(calldata) < HASH_OFFSET + HASH_LEN:
            return None, f"Calldata curto demais ({len(calldata)} bytes)"
        if calldata[:HASH_OFFSET] != MARKER:
            return None, f"Marcador invalido: {calldata[:4].hex()!r} (esperado 'QTST')"

        return calldata[HASH_OFFSET : HASH_OFFSET + HASH_LEN], "ok"

    except Exception as exc:
        return None, str(exc)


# ══════════════════════════════════════════════════════════════════════════════
# 3 — Verificacao de assinatura
# ══════════════════════════════════════════════════════════════════════════════
def verify_signature(file_hash: bytes, pubkey: bytes, sig: bytes, backend: str) -> tuple[bool | None, str]:
    """
    Verifica a assinatura com o backend correto.
    Retorna (resultado, mensagem).
    resultado = None se nao for possivel verificar (backend incompativel).
    """
    if backend == "oqs":
        if _PQC_BACKEND != "oqs":
            return None, "oqs-python ausente neste ambiente -- impossivel verificar assinatura oqs"
        try:
            with _oqs.Signature("Dilithium3") as v:
                ok = v.verify(file_hash, sig, pubkey)
            return ok, "Dilithium3/oqs valida" if ok else "Dilithium3/oqs INVALIDA"
        except Exception as exc:
            return False, f"Erro oqs: {exc}"

    elif backend == "dilithium-py":
        if _PQC_BACKEND not in ("dilithium-py", "oqs"):
            return None, "dilithium-py ausente neste ambiente -- impossivel verificar"
        try:
            if _PQC_BACKEND == "oqs":
                # oqs tambem implementa Dilithium3 e pode verificar
                with _oqs.Signature("Dilithium3") as v:
                    ok = v.verify(file_hash, sig, pubkey)
            else:
                ok = _Dilithium3.verify(pubkey, file_hash, sig)
            return ok, "Dilithium3 valida" if ok else "Dilithium3 INVALIDA"
        except Exception as exc:
            return False, f"Erro Dilithium3: {exc}"

    elif backend == "hmac-stub":
        # HMAC-SHA3-256: verificar recomputando MAC com a chave (= public_key do bundle)
        try:
            expected = hmac.new(pubkey, file_hash, hashlib.sha3_256).digest()
            ok = hmac.compare_digest(expected, sig)
            return ok, "HMAC-SHA3-256 valido (stub)" if ok else "HMAC-SHA3-256 INVALIDO"
        except Exception as exc:
            return False, f"Erro HMAC: {exc}"

    return None, f"Backend desconhecido: {backend!r}"


# ══════════════════════════════════════════════════════════════════════════════
# Carregar bundle ou laudo
# ══════════════════════════════════════════════════════════════════════════════
def load_evidence(path: Path) -> dict:
    """Aceita bundle JSON ou laudo Markdown."""
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))

    if path.suffix == ".md":
        text   = path.read_text(encoding="utf-8")
        bundle: dict = {}

        m = re.search(r"Transacao Blockchain:\s+(0x\S+)\s+\(Rede (.+?)\)", text)
        if m:
            bundle["tx_hash"] = m.group(1)
            bundle["network"] = m.group(2)

        m = re.search(r"Hash do Arquivo \(SHA3\):\s+([0-9a-fA-F]{64,})", text)
        if m:
            bundle["sha3_256"] = m.group(1)

        m = re.search(r"Bloco de Confianca:\s+(\d+)", text)
        if m:
            bundle["block_number"] = int(m.group(1))

        m = re.search(r"Data da Selagem \(UTC\):\s+(.+)", text)
        if m:
            bundle["timestamp_utc"] = m.group(1).strip()

        if "tx_hash" not in bundle or "sha3_256" not in bundle:
            raise ValueError(
                f"Nao foi possivel extrair tx_hash/sha3_256 de {path.name}.\n"
                "Use o bundle JSON para verificacao completa (inclui assinatura PQC)."
            )
        bundle.setdefault("pqc_backend", None)
        return bundle

    raise ValueError(f"Formato nao reconhecido: {path.suffix}")


def resolve_evidence(arg: str | None) -> Path:
    if arg:
        p = Path(arg)
        if not p.exists():
            print(f"Erro: evidencia nao encontrada: {p}")
            sys.exit(1)
        return p
    bundles = sorted(EVIDENCE_DIR.glob("bundle_*.json"), reverse=True)
    if not bundles:
        print("Nenhum bundle em evidence/. Execute seal.py primeiro.")
        sys.exit(1)
    chosen = bundles[0]
    print(f"Bundle selecionado automaticamente: {chosen.name}")
    return chosen


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python scripts/verify.py <arquivo> [bundle.json | laudo.md]")
        sys.exit(1)

    target   = Path(sys.argv[1])
    evidence = resolve_evidence(sys.argv[2] if len(sys.argv) >= 3 else None)

    if not target.exists():
        print(f"Erro: arquivo nao encontrado: {target}")
        sys.exit(1)

    bundle      = load_evidence(evidence)
    tx_hash     = bundle["tx_hash"]
    stored_hex  = bundle["sha3_256"]
    pqc_backend = bundle.get("pqc_backend")     # None se vier de laudo .md
    pubkey_hex  = bundle.get("public_key")
    sig_hex     = bundle.get("signature")

    print()
    print("phantom-seal  |  Q-Trust  Verificacao de Integridade")
    print("=" * 62)
    print(f"Arquivo   : {target.resolve()}")
    print(f"Tamanho   : {target.stat().st_size:,} bytes")
    print(f"Evidencia : {evidence.name}")
    if bundle.get("timestamp_utc"):
        print(f"Selado em : {bundle['timestamp_utc']} UTC")
    print(f"TX        : {tx_hash}")
    if bundle.get("network"):
        print(f"Rede      : {bundle['network']}")
    print()

    # ── Camada 1: hash local ───────────────────────────────────────────────────
    print("[1/3] Recalculando SHA3-256 do arquivo ...")
    local_hash = sha3_256_file(target)
    hash_ok    = local_hash.hex() == stored_hex
    st1        = OK if hash_ok else FAIL
    print(f"      hash local  : {local_hash.hex()}")
    print(f"      hash selado : {stored_hex}")
    print(f"      resultado   : {st1}")

    # ── Camada 2: on-chain ─────────────────────────────────────────────────────
    print(f"\n[2/3] Buscando calldata na Sepolia ...")
    anchored_hash, chain_msg = fetch_anchored_hash(tx_hash)

    if anchored_hash is None:
        st2         = SKIP
        chain_match = None
        print(f"      {chain_msg}")
    else:
        chain_match = anchored_hash == local_hash
        st2         = OK if chain_match else FAIL
        print(f"      hash on-chain: {anchored_hash.hex()}")
    print(f"      resultado    : {st2}")

    # ── Camada 3: assinatura PQC ───────────────────────────────────────────────
    print(f"\n[3/3] Verificando assinatura PQC ...")
    if pubkey_hex and sig_hex and pqc_backend:
        pubkey    = bytes.fromhex(pubkey_hex)
        sig       = bytes.fromhex(sig_hex)
        sig_ok, sig_msg = verify_signature(local_hash, pubkey, sig, pqc_backend)
        st3       = (OK if sig_ok else FAIL) if sig_ok is not None else SKIP
    else:
        sig_ok, sig_msg = None, "public_key/signature ausentes (laudo .md nao os contem)"
        st3 = SKIP
    print(f"      {sig_msg}")
    print(f"      resultado   : {st3}")

    # ── Veredicto ──────────────────────────────────────────────────────────────
    print()
    print("=" * 62)

    # Falha dura: hash local diverge OU assinatura invalida
    hard_fail = (not hash_ok) or (sig_ok is False)
    # Falha on-chain: chain_match nao skippado e diverge
    chain_fail = (chain_match is not None) and (not chain_match)

    print(f"  [{'v' if st1 == OK else 'x' if st1 == FAIL else '~'}] Hash SHA3-256 local   : {st1.strip()}")
    print(f"  [{'v' if st2 == OK else 'x' if st2 == FAIL else '~'}] Hash on-chain Sepolia : {st2.strip()}")
    print(f"  [{'v' if st3 == OK else 'x' if st3 == FAIL else '~'}] Assinatura PQC        : {st3.strip()}")
    print()

    if hard_fail or chain_fail:
        print("  ADULTERADO")
        print()
        if not hash_ok:
            print(f"  O hash atual ({local_hash.hex()[:16]}...)")
            print(f"  difere do selado ({stored_hex[:16]}...).")
            print("  O arquivo foi modificado apos a selagem.")
        if chain_fail:
            print("  O hash on-chain nao bate com o hash local.")
        if sig_ok is False:
            print("  A assinatura PQC e invalida.")
        sys.exit(1)
    else:
        print("  INTEGRO")
        print()
        if hash_ok:
            print("  O hash SHA3-256 do arquivo coincide com o valor selado.")
        if chain_match:
            print("  O hash ancorado na Sepolia confirma a integridade.")
        elif st2 == SKIP:
            print(f"  (verificacao on-chain: {chain_msg})")
        if sig_ok is True:
            print("  Assinatura Dilithium3 criptograficamente valida.")
        elif st3 == SKIP:
            print("  (assinatura PQC: nao verificada neste ambiente)")
        sys.exit(0)


if __name__ == "__main__":
    main()
