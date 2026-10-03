"""SHA3-256 streaming file hasher."""

import hashlib
import logging
from pathlib import Path

log = logging.getLogger(__name__)

CHUNK_SIZE = 65_536


def sha3_256_file(path: Path) -> bytes:
    """Stream-hash a file with SHA3-256; returns raw 32-byte digest."""
    h = hashlib.sha3_256()
    size = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
            size += len(chunk)
    log.debug("sha3_256_file path=%s size=%d digest=%s", path.name, size, h.hexdigest()[:16] + "…")
    return h.digest()
