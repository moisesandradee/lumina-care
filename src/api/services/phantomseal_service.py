from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class PhantomSealService:
    """Thin backend adapter for PhantomSeal operations.

    This service intentionally starts as an application-layer wrapper so Lumina
    can expose stable HTTP endpoints before deeper infrastructure hardening.
    The implementation below is local-file oriented and should evolve toward
    dedicated storage, secret management, and evidence indexing.
    """

    def __init__(self, evidence_dir: str = "evidence") -> None:
        self.evidence_dir = Path(evidence_dir)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def health(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": "phantomseal",
            "evidence_dir": str(self.evidence_dir),
        }

    def list_evidence(self) -> Dict[str, Any]:
        files = sorted(self.evidence_dir.glob("seal_*.json"), reverse=True)
        items = []
        for file in files:
            items.append(
                {
                    "file_name": file.name,
                    "path": str(file),
                }
            )
        return {"ok": True, "count": len(items), "items": items}

    def get_evidence(self, file_name: str) -> Dict[str, Any]:
        target = self.evidence_dir / file_name
        if not target.exists() or not target.is_file():
            return {"ok": False, "reason": "Evidence file not found", "file_name": file_name}

        return {
            "ok": True,
            "file_name": file_name,
            "data": json.loads(target.read_text(encoding="utf-8")),
        }
