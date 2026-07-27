"""Events Log & Snapshots API routes."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/events", tags=["Events"])

class EventDTO(BaseModel):
    event_id: str
    timestamp: float
    camera_id: str
    event_type: str
    severity: str
    object_id: Optional[int] = None
    object_class: Optional[str] = None
    confidence: float = 1.0
    zone_id: Optional[str] = None
    zone_name: Optional[str] = None
    snapshot_path: Optional[str] = None

@router.get("", response_model=List[EventDTO])
def search_events(
    camera_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 50,
):
    # Dummy / repository binding
    return []

@router.get("/{event_id}/snapshot")
def get_event_snapshot(event_id: str):
    raise HTTPException(status_code=404, detail="Snapshot not found")
