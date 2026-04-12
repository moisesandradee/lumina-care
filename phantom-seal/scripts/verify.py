"""
verify.py — Q-Trust phantom-seal

Fluxo de verificação:
  1. Lê o arquivo original e recalcula SHA3-256
  2. Carrega tx_hash do bundle JSON ou laudo Markdown
  3. Busca a transação na Sepolia e decodifica o calldata
  4. Compara hash local com hash ancorado on-chain
  5. Verifica assinatura Dilithium3 (camada adicional)
  6. Imprime 'ÍNTEGRO ✅' ou 'ADULTERADO ❌'

Uso:
  python scripts/verify.py logs/sample_aso.pdf evidence/bundle_<...>.json
  python scripts/verify.py logs/sample_aso.pdf evidence/laudo_<...>.md
  python scripts/verify.py logs/sample_aso.pdf          # usa bundle mais recente

Requer .env com:
  RPC_URL_SEPOLIA=https://sepolia.infura.io/v3/<PROJECT_ID>
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

import oqs
from dotenv import load_dotenv
from web3 import Web3

load_dotenv(Path(__file__).parent.parent / ".env")

# ── Constantes ─────────────────────────────────────────────────────────────────
MARKER = b"QTST"          # 4 bytes: Q-Trust Seal Token (prefixo do calldata)
HASH_OFFSET = 4           # bytes[4:36] = SHA3-256 (32 bytes)
HASH_LEN = 32

ROOT = Path(__file__).parent.parent
EVIDENCE_DIR = ROOT / "evidence"


# ══════════════════════════════════════════════════════════════════════════════
# Passo 1 — Recalcular hash local
# ══════════════════════════════════════════════════════════════════════════════
def sha3_256_file(path: Path) -> bytes:
    """Leitura em streaming (chunks de 64 KB) para arquivos grandes."""
    h = hashlib.sha3_256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65_536), b""):
            h.update(chunk)
    return h.digest()


# ══════════════════════════════════════════════════════════════════════════════
# Passo 2 — Carregar metadados do bundle ou laudo
# ══════════════════════════════════════════════════════════════════════════════
def load_bundle(path: Path) -> dict:
    """
    Aceita dois formatos:
      - bundle_*.json  → dicionário direto
      - laudo_*.md     → extrai tx_hash e sha3_256 via regex
    Retorna dict com pelo menos 'tx_hash' e 'sha3_256'.
    """
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))

    if path.suffix == ".md":
        text = path.read_text(encoding="utf-8")
        bundle: dict = {}

        # Extrai TX hash  (linha: " Transação Blockchain:   0x<hash> (Rede …)")
        m = re.search(r"Transação Blockchain:\s+(0x[0-9a-fA-F]+)", text)
        if m:
            bundle["tx_hash"] = m.group(1)

        # Extrai SHA3 hash (linha: " Hash do Arquivo (SHA3): <hex>")
        m = re.search(r"Hash do Arquivo \(SHA3\):\s+([0-9a-fA-F]{64})", text)
        if m:
            bundle["sha3_256"] = m.group(1)

        # Campos opcionais
        m = re.search(r"Bloco de Confiança:\s+(\d+)", text)
        if m:
            bundle["block_number"] = int(m.group(1))

        m = re.search(r"Data da Selagem \(UTC\):\s+(.+)", text)
        if m:
            bundle["timestamp_utc"] = m.group(1).strip()

        if "tx_hash" not in bundle or "sha3_256" not in bundle:
            raise ValueError(f"Não foi possível extrair tx_hash / sha3_256 de {path.name}")
        return bundle

    raise ValueError(f"Formato não reconhecido: {path.suffix} (use .json ou .md)")


def resolve_evidence(argv_path: str | None) -> Path:
    """Retorna o path do bundle/laudo; se não fornecido, usa o JSON mais recente."""
    if argv_path:
        p = Path(argv_path)
        if not p.exists():
            print(f"Erro: arquivo de evidência não encontrado: {p}")
            sys.exit(1)
        return p

    bundles = sorted(EVIDENCE_DIR.glob("bundle_*.json"), reverse=True)
    if not bundles:
        print("Nenhum bundle encontrado em evidence/. Execute seal.py primeiro.")
        sys.exit(1)
    chosen = bundles[0]
    print(f"Bundle selecionado automaticamente: {chosen.name}")
    return chosen


# ══════════════════════════════════════════════════════════════════════════════
# Passo 3 — Buscar transação na Sepolia e decodificar calldata
# ══════════════════════════════════════════════════════════════════════════════
def fetch_anchored_hash(tx_hash: str) -> bytes:
    """
    Conecta na Sepolia, busca a transação pelo tx_hash e extrai o hash SHA3-256
    do calldata.

    Formato esperado do calldata:
      bytes[0:4]  = b'QTST'         (marcador Q-Trust)
      bytes[4:36] = SHA3-256(arquivo) (32 bytes)

    Raises:
      EnvironmentError  — RPC_URL_SEPOLIA não configurado
      ConnectionError   — falha de conexão com o nó RPC
      ValueError        — calldata inválido ou marcador ausente
    """
    rpc_url = os.getenv("RPC_URL_SEPOLIA")
    if not rpc_url:
        raise EnvironmentError(
            "RPC_URL_SEPOLIA não está definido em .env\n"
            "Configure: RPC_URL_SEPOLIA=https://sepolia.infura.io/v3/<PROJECT_ID>"
        )

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError(
            f"Não foi possível conectar à Sepolia via {rpc_url}\n"
            "Verifique sua conexão e o PROJECT_ID do Infura/Alchemy."
        )

    print(f"      Conectado à Sepolia  (bloco atual: {w3.eth.block_number:,})")

    tx = w3.eth.get_transaction(tx_hash)
    calldata: bytes = bytes(tx["input"])

    print(f"      Calldata bruto ({len(calldata)} bytes): {calldata.hex()}")

    if len(calldata) < HASH_OFFSET + HASH_LEN:
        raise ValueError(
            f"Calldata curto demais ({len(calldata)} bytes); esperado ≥ {HASH_OFFSET + HASH_LEN}"
        )
    if calldata[:HASH_OFFSET] != MARKER:
        raise ValueError(
            f"Marcador inválido: {calldata[:4].hex()!r} (esperado 'QTST' = 51545354)"
        )

    return calldata[HASH_OFFSET : HASH_OFFSET + HASH_LEN]


# ══════════════════════════════════════════════════════════════════════════════
# Passo 5 — Verificação de assinatura PQC (camada complementar)
# ══════════════════════════════════════════════════════════════════════════════
def verify_pqc_signature(bundle: dict, file_hash: bytes) -> tuple[bool | None, str]:
    """
    Retorna (resultado, mensagem).
    resultado = True/False/None (None = dados ausentes no bundle, pulado).
    """
    algorithm = bundle.get("algorithm", "Dilithium3")
    pubkey_hex = bundle.get("public_key")
    sig_hex = bundle.get("signature")

    if not pubkey_hex or not sig_hex:
        return None, "public_key / signature ausentes no bundle (laudo .md não os contém)"

    try:
        public_key = bytes.fromhex(pubkey_hex)
        signature = bytes.fromhex(sig_hex)
        with oqs.Signature(algorithm) as verifier:
            valid = verifier.verify(file_hash, signature, public_key)
        return valid, f"{algorithm}: {'válida' if valid else 'INVÁLIDA'}"
    except Exception as exc:
        return False, f"Erro ao verificar assinatura: {exc}"


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python scripts/verify.py <arquivo> [bundle.json | laudo.md]")
        sys.exit(1)

    target = Path(sys.argv[1])
    evidence_arg = sys.argv[2] if len(sys.argv) >= 3 else None

    if not target.exists():
        print(f"Erro: arquivo não encontrado: {target}")
        sys.exit(1)

    evidence_path = resolve_evidence(evidence_arg)
    bundle = load_bundle(evidence_path)

    tx_hash: str = bundle["tx_hash"]
    stored_hex: str = bundle["sha3_256"]

    print()
    print("phantom-seal  |  Verificação de Integridade Q-Trust")
    print("─" * 62)
    print(f"Arquivo     : {target.resolve()}")
    print(f"Tamanho     : {target.stat().st_size:,} bytes")
    print(f"Evidência   : {evidence_path.name}")
    if bundle.get("timestamp_utc"):
        print(f"Selado em   : {bundle['timestamp_utc']} UTC")
    print(f"TX Sepolia  : {tx_hash}")
    print()

    # ── Passo 1: hash local ────────────────────────────────────────────────────
    print("[1/3] Recalculando SHA3-256 do arquivo …")
    local_hash = sha3_256_file(target)
    print(f"      hash local  : {local_hash.hex()}")
    print(f"      hash selado : {stored_hex}")

    hash_matches_bundle = local_hash.hex() == stored_hex
    status_bundle = "OK" if hash_matches_bundle else "DIVERGE"
    print(f"      vs. bundle  : {status_bundle}")

    # ── Passo 2: hash on-chain ─────────────────────────────────────────────────
    print(f"\n[2/3] Buscando transação na Sepolia …")
    try:
        anchored_hash = fetch_anchored_hash(tx_hash)
        print(f"      hash on-chain: {anchored_hash.hex()}")

        hash_matches_chain = local_hash == anchored_hash
        chain_available = True
    except Exception as exc:
        print(f"      ERRO ao buscar TX: {exc}")
        anchored_hash = None
        hash_matches_chain = False
        chain_available = False

    # ── Passo 3: assinatura PQC ────────────────────────────────────────────────
    print(f"\n[3/3] Verificando assinatura pós-quântica …")
    sig_result, sig_msg = verify_pqc_signature(bundle, local_hash)
    print(f"      {sig_msg}")

    # ── Veredicto ──────────────────────────────────────────────────────────────
    print()
    print("─" * 62)

    if chain_available:
        # Comparação primária: hash local == hash ancorado on-chain
        integro = hash_matches_chain
    else:
        # Fallback: sem RPC, compara apenas com o bundle
        integro = hash_matches_bundle

    # A assinatura PQC inválida (quando presente) invalida o resultado
    if sig_result is False:
        integro = False

    print()
    if integro:
        print("  ÍNTEGRO ✅")
        print()
        if chain_available:
            print("  O hash SHA3-256 do arquivo coincide com o valor")
            print("  ancorado imutavelmente na Sepolia.")
        else:
            print("  O hash SHA3-256 local coincide com o bundle.")
            print("  (verificação on-chain indisponível — configure RPC_URL_SEPOLIA)")
        if sig_result is True:
            print("  Assinatura Dilithium3 verificada com sucesso.")
        print()
        sys.exit(0)
    else:
        print("  ADULTERADO ❌")
        print()
        if chain_available and not hash_matches_chain:
            print(f"  Hash local   : {local_hash.hex()}")
            print(f"  Hash on-chain: {anchored_hash.hex() if anchored_hash else 'N/A'}")
            print("  Os hashes divergem: o arquivo foi modificado após a selagem.")
        elif not hash_matches_bundle:
            print(f"  Hash local : {local_hash.hex()}")
            print(f"  Hash bundle: {stored_hex}")
            print("  O arquivo difere do registrado no bundle.")
        if sig_result is False and "Erro" not in sig_msg:
            print("  Assinatura Dilithium3 inválida.")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
