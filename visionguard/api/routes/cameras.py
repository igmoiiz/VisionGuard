"""Cameras Management API routes."""
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/cameras", tags=["Cameras"])

class CameraDTO(BaseModel):
    id: str
    name: str
    source: str
    enabled: bool = True
    resolution: List[int] = [1280, 720]
    fps_target: float = 25.0

@router.get("", response_model=List[CameraDTO])
def list_cameras():
    return [
        CameraDTO(
            id="cam_01",
            name="Main Entrance Camera",
            source="0",
            enabled=True,
            resolution=[1280, 720],
            fps_target=25.0,
        )
    ]
