from fastapi import APIRouter, HTTPException
from typing import Optional

from src.api.services.phantomseal_service import PhantomSealService

router = APIRouter(prefix="/api/v1/phantomseal", tags=["phantomseal"])

service = PhantomSealService()


@router.get("/health")
def health():
    return service.health()


@router.get("/evidence")
def list_evidence():
    return service.list_evidence()


@router.get("/evidence/{file_name}")
def get_evidence(file_name: str):
    result = service.get_evidence(file_name)
    if not result.get("ok"):
        raise HTTPException(status_code=404, detail=result.get("reason"))
    return result
