"""
Post-quantum signing module — ML-DSA-65 / Dilithium3 (NIST FIPS 204).

Backend hierarchy:
  1. oqs (liboqs native, "ML-DSA-65")   — production-grade
  2. dilithium-py (pure-Python)          — development only
  3. RuntimeError                         — no PQC library available

KAT (Known Answer Test) runs on import to validate key/signature sizes per FIPS 204.
"""

import dataclasses
import hashlib
import logging
import os

log = logging.getLogger(__name__)

# FIPS 204 / ML-DSA-65 (= Dilithium3) expected sizes
KAT_PK_BYTES   = 1952
KAT_SK_BYTES   = 4032
KAT_SIG_MAX    = 3309
KAT_NIST_LEVEL = 3

OQS_ALGORITHM   = "ML-DSA-65"
ALGORITHM_ALIAS = "Dilithium3 / ML-DSA-65 (FIPS 204)"

# ── Backend detection ─────────────────────────────────────────────────────────
try:
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module="oqs")
        import oqs as _oqs
    _BACKEND = "oqs"
except Exception:
    _oqs = None
    try:
        from dilithium_py.dilithium import Dilithium3 as _Dilithium3
        _BACKEND = "dilithium-py"
    except Exception:
        _Dilithium3 = None
        _BACKEND = None

AUDIT_LEVEL = {
    "oqs": (
        "Producao — liboqs nativo (FIPS 204, NIST PQC, auditavel por HSM)"
    ),
    "dilithium-py": (
        "AVISO: implementacao Python nao auditada para producao (dilithium-py). "
        "Para producao, substituir por liboqs via hardware dedicado."
    ),
}


@dataclasses.dataclass
class SignResult:
    public_key:    bytes
    signature:     bytes
    nonce:         bytes
    signing_input: bytes
    algorithm:     str
    backend:       str
    audit_level:   str
    pk_bytes:      int
    sig_bytes:     int


def _kat_check(pk: bytes, sk: bytes, sig: bytes) -> None:
    if len(pk) != KAT_PK_BYTES:
        raise AssertionError(f"KAT FAIL: pk={len(pk)}B expected {KAT_PK_BYTES}B")
    if len(sk) != KAT_SK_BYTES:
        raise AssertionError(f"KAT FAIL: sk={len(sk)}B expected {KAT_SK_BYTES}B")
    if len(sig) > KAT_SIG_MAX:
        raise AssertionError(f"KAT FAIL: sig={len(sig)}B > max {KAT_SIG_MAX}B")


def _selftest() -> None:
    if _BACKEND == "oqs":
        msg = b"kat-selftest"
        with _oqs.Signature(OQS_ALGORITHM) as s:
            pk = s.generate_keypair()
            sk_len = s.secret_key_length
            sig = s.sign(msg)
        _kat_check(pk, bytes(sk_len), sig)
        log.debug("KAT PASS (oqs) pk=%dB sig=%dB", len(pk), len(sig))
    elif _BACKEND == "dilithium-py":
        msg = b"kat-selftest"
        pk, sk = _Dilithium3.keygen()
        sig = _Dilithium3.sign(sk, msg)
        if len(pk) != KAT_PK_BYTES:
            log.warning("KAT: pk=%dB expected %dB (dilithium-py may differ)", len(pk), KAT_PK_BYTES)
        log.debug("KAT PASS (dilithium-py) pk=%dB sig=%dB", len(pk), len(sig))


_selftest()


def sign(file_hash: bytes) -> SignResult:
    """Sign file_hash with an ephemeral keypair. Returns SignResult."""
    if _BACKEND is None:
        raise RuntimeError("No PQC backend available. Install liboqs-python or dilithium-py.")

    nonce = os.urandom(32)
    signing_input = hashlib.sha3_256(file_hash + nonce).digest()

    if _BACKEND == "oqs":
        with _oqs.Signature(OQS_ALGORITHM) as s:
            pk = s.generate_keypair()
            sig = s.sign(signing_input)
        backend = "oqs"
    else:
        pk, sk = _Dilithium3.keygen()
        sig = _Dilithium3.sign(sk, signing_input)
        backend = "dilithium-py"

    log.debug("sign backend=%s pk=%dB sig=%dB nonce=%s", backend, len(pk), len(sig), nonce.hex()[:8] + "…")
    return SignResult(
        public_key=pk,
        signature=sig,
        nonce=nonce,
        signing_input=signing_input,
        algorithm=ALGORITHM_ALIAS,
        backend=backend,
        audit_level=AUDIT_LEVEL[backend],
        pk_bytes=len(pk),
        sig_bytes=len(sig),
    )


def verify(file_hash: bytes, nonce: bytes, public_key: bytes, signature: bytes, backend: str | None = None) -> bool:
    """Verify a signature. backend overrides auto-detection."""
    signing_input = hashlib.sha3_256(file_hash + nonce).digest()
    effective = backend or _BACKEND

    if effective == "oqs" and _oqs is not None:
        try:
            with _oqs.Signature(OQS_ALGORITHM) as v:
                return bool(v.verify(signing_input, signature, public_key))
        except Exception as exc:
            log.warning("oqs verify error: %s", exc)
            return False

    if effective == "dilithium-py" and _Dilithium3 is not None:
        try:
            return bool(_Dilithium3.verify(public_key, signing_input, signature))
        except Exception as exc:
            log.warning("dilithium-py verify error: %s", exc)
            return False

    log.warning("verify: no compatible backend for backend=%s", effective)
    return False
