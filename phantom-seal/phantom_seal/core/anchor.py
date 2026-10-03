"""
Sepolia blockchain anchoring.

Wallet lifecycle:
  - load_or_create_wallet() reads phantom-seal/.wallet (hex private key)
    or generates a fresh throwaway testnet key and saves it.
  - connect_sepolia() tries a list of public RPCs; returns first live Web3.
  - anchor() sends a self-send EIP-1559 TX with calldata = QTST || sha3_256.

The .wallet file is gitignored and must NEVER be used on mainnet.
"""

import hashlib
import logging
import os
import time
from pathlib import Path

log = logging.getLogger(__name__)

CHAIN_ID    = 11155111       # Sepolia
MARKER      = b"QTST"        # Q-Trust Seal Token (4 bytes prefix)
WALLET_FILE = Path(__file__).parent.parent.parent / ".wallet"

PUBLIC_RPCS = [
    "https://rpc.sepolia.org",
    "https://ethereum-sepolia.publicnode.com",
    "https://sepolia.drpc.org",
]


def load_or_create_wallet() -> tuple[str, str]:
    """Return (private_key_hex, address). Create .wallet if absent."""
    env_key = os.getenv("WALLET_PRIVATE_KEY", "").strip()
    if env_key:
        from eth_account import Account
        acct = Account.from_key(env_key)
        log.debug("wallet loaded from env address=%s", acct.address)
        return env_key, acct.address

    if WALLET_FILE.exists():
        key = WALLET_FILE.read_text().strip()
        from eth_account import Account
        acct = Account.from_key(key)
        log.debug("wallet loaded from file address=%s", acct.address)
        return key, acct.address

    from eth_account import Account
    acct = Account.create()
    WALLET_FILE.write_text(acct.key.hex())
    log.info("new throwaway testnet wallet created address=%s", acct.address)
    log.warning(
        "Fund this testnet wallet before sealing: %s  "
        "Faucets: https://sepoliafaucet.com  https://faucet.quicknode.com/ethereum/sepolia",
        acct.address,
    )
    return acct.key.hex(), acct.address


def connect_sepolia():
    """Return a connected Web3 instance, trying PUBLIC_RPCS in order."""
    from web3 import Web3

    rpc_url = os.getenv("RPC_URL_SEPOLIA", "").strip()
    candidates = ([rpc_url] if rpc_url else []) + PUBLIC_RPCS

    for url in candidates:
        try:
            w3 = Web3(Web3.HTTPProvider(url, request_kwargs={"timeout": 10}))
            if w3.is_connected():
                log.debug("connected to Sepolia via %s", url)
                return w3
        except Exception as exc:
            log.debug("RPC %s failed: %s", url, exc)

    raise ConnectionError("Could not connect to Sepolia — all RPCs failed")


def anchor(file_hash: bytes) -> dict:
    """
    Send QTST||file_hash as EIP-1559 calldata on Sepolia.
    Returns dict with tx_hash, block_number, network, wallet.
    """
    private_key, address = load_or_create_wallet()
    w3 = connect_sepolia()

    balance = w3.eth.get_balance(address)
    min_balance = w3.to_wei(0.001, "ether")
    if balance < min_balance:
        raise ValueError(
            f"Insufficient balance ({w3.from_wei(balance, 'ether')} ETH) at {address}. "
            "Fund via https://sepoliafaucet.com or https://faucet.quicknode.com/ethereum/sepolia"
        )

    payload    = MARKER + file_hash
    nonce_tx   = w3.eth.get_transaction_count(address, "pending")
    base_fee   = w3.eth.gas_price
    max_prio   = w3.to_wei(1, "gwei")

    tx = {
        "from":                 address,
        "to":                   address,
        "value":                0,
        "data":                 payload,
        "nonce":                nonce_tx,
        "chainId":              CHAIN_ID,
        "maxFeePerGas":         base_fee * 2 + max_prio,
        "maxPriorityFeePerGas": max_prio,
    }
    tx["gas"] = w3.eth.estimate_gas(tx) + 5_000

    signed      = w3.eth.account.sign_transaction(tx, private_key)
    raw_tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    log.info("TX sent hash=%s — waiting for confirmation…", raw_tx_hash.hex())

    receipt = w3.eth.wait_for_transaction_receipt(raw_tx_hash, timeout=180)
    log.info("TX confirmed block=%d", receipt.blockNumber)

    return {
        "tx_hash":      receipt.transactionHash.hex(),
        "block_number": receipt.blockNumber,
        "network":      "Sepolia",
        "wallet":       address,
        "dry_run":      False,
    }


def anchor_dry_run(file_hash: bytes) -> dict:
    """Simulate anchoring without sending any TX (no .env / no funds needed)."""
    payload  = MARKER + file_hash
    sim_hash = "0xDRYRUN" + hashlib.sha3_256(b"dry-run:" + payload).hexdigest()[6:]
    from datetime import datetime, timezone
    sim_block = int(datetime.now(timezone.utc).timestamp()) % 10_000_000 + 7_000_000
    log.info("dry-run anchor simulated tx_hash=%s block=%d", sim_hash, sim_block)
    return {
        "tx_hash":      sim_hash,
        "block_number": sim_block,
        "network":      "Sepolia [DRY-RUN]",
        "wallet":       "N/A",
        "dry_run":      True,
    }
