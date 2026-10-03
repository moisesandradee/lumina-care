"""
Tests for phantom_seal tamper-detection pipeline.

Covers:
  - Hash matches original file
  - Hash detects tampered bytes
  - Signature valid for original
  - Signature fails for tampered hash
  - Signature fails with wrong public key
  - Dry-run anchor produces deterministic tx_hash
"""

import hashlib
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Make phantom_seal importable from the package root
sys.path.insert(0, str(Path(__file__).parent.parent))

from phantom_seal.core import hasher, signer, anchor


# ── Helpers ───────────────────────────────────────────────────────────────────

def _tmp_file(content: bytes) -> Path:
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    f.write(content)
    f.close()
    return Path(f.name)


SAMPLE = b"Q-Trust phantom-seal test document\n" * 100


# ── hasher ────────────────────────────────────────────────────────────────────

def test_hash_stable():
    p = _tmp_file(SAMPLE)
    try:
        h1 = hasher.sha3_256_file(p)
        h2 = hasher.sha3_256_file(p)
        assert h1 == h2
    finally:
        p.unlink()


def test_hash_matches_stdlib():
    p = _tmp_file(SAMPLE)
    try:
        got      = hasher.sha3_256_file(p)
        expected = hashlib.sha3_256(SAMPLE).digest()
        assert got == expected
    finally:
        p.unlink()


def test_tampered_bytes_change_hash():
    p = _tmp_file(SAMPLE)
    try:
        h_orig = hasher.sha3_256_file(p)
        tampered = SAMPLE[:-1] + bytes([SAMPLE[-1] ^ 0xFF])
        p.write_bytes(tampered)
        h_tampered = hasher.sha3_256_file(p)
        assert h_orig != h_tampered
    finally:
        p.unlink()


def test_single_bit_flip_changes_hash():
    p = _tmp_file(SAMPLE)
    try:
        h_orig = hasher.sha3_256_file(p)
        data   = bytearray(SAMPLE)
        data[0] ^= 0x01
        p.write_bytes(bytes(data))
        assert hasher.sha3_256_file(p) != h_orig
    finally:
        p.unlink()


# ── signer ────────────────────────────────────────────────────────────────────

def test_sign_returns_expected_fields():
    h = hashlib.sha3_256(SAMPLE).digest()
    r = signer.sign(h)
    assert isinstance(r.public_key, bytes) and len(r.public_key) > 0
    assert isinstance(r.signature,  bytes) and len(r.signature)  > 0
    assert isinstance(r.nonce,      bytes) and len(r.nonce) == 32
    assert isinstance(r.signing_input, bytes) and len(r.signing_input) == 32


def test_verify_original_succeeds():
    h = hashlib.sha3_256(SAMPLE).digest()
    r = signer.sign(h)
    assert signer.verify(h, r.nonce, r.public_key, r.signature, r.backend) is True


def test_verify_tampered_hash_fails():
    h       = hashlib.sha3_256(SAMPLE).digest()
    r       = signer.sign(h)
    bad_hash = bytes([b ^ 0xFF for b in h])
    assert signer.verify(bad_hash, r.nonce, r.public_key, r.signature, r.backend) is False


def test_verify_wrong_public_key_fails():
    h  = hashlib.sha3_256(SAMPLE).digest()
    r  = signer.sign(h)
    r2 = signer.sign(h)               # different ephemeral keypair
    # r2's public key should not verify r's signature
    assert signer.verify(h, r.nonce, r2.public_key, r.signature, r.backend) is False


def test_verify_wrong_nonce_fails():
    h     = hashlib.sha3_256(SAMPLE).digest()
    r     = signer.sign(h)
    bad_nonce = os.urandom(32)
    assert signer.verify(h, bad_nonce, r.public_key, r.signature, r.backend) is False


def test_sign_nonce_unique_per_call():
    h  = hashlib.sha3_256(SAMPLE).digest()
    r1 = signer.sign(h)
    r2 = signer.sign(h)
    assert r1.nonce != r2.nonce


# ── anchor (dry-run only, no network) ────────────────────────────────────────

def test_dry_run_returns_expected_keys():
    h   = hashlib.sha3_256(SAMPLE).digest()
    info = anchor.anchor_dry_run(h)
    assert "tx_hash"      in info
    assert "block_number" in info
    assert info["dry_run"] is True
    assert info["tx_hash"].upper().startswith("0XDRYRUN")


def test_dry_run_deterministic():
    h    = hashlib.sha3_256(SAMPLE).digest()
    tx1  = anchor.anchor_dry_run(h)["tx_hash"]
    tx2  = anchor.anchor_dry_run(h)["tx_hash"]
    assert tx1 == tx2


def test_dry_run_different_hashes_different_tx():
    h1  = hashlib.sha3_256(b"doc1").digest()
    h2  = hashlib.sha3_256(b"doc2").digest()
    tx1 = anchor.anchor_dry_run(h1)["tx_hash"]
    tx2 = anchor.anchor_dry_run(h2)["tx_hash"]
    assert tx1 != tx2
