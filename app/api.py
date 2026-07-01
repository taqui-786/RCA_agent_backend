from fastapi import APIRouter, HTTPException, status
from app.schemas.incident import IncidentCreate, IncidentDetailResponse, IncidentResolveRequest
from app.services.incident_service import create_incident, get_incident, list_incidents, resolve_incident

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("", response_model=IncidentDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_incident_endpoint(incident: IncidentCreate):
    return await create_incident(incident)


@router.post("/{incident_id}/resolve", response_model=IncidentDetailResponse)
async def resolve_incident_endpoint(incident_id: int, data: IncidentResolveRequest):
    result = await resolve_incident(incident_id, data)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return result


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
async def get_incident_endpoint(incident_id: int):
    result = await get_incident(incident_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return result


@router.get("", response_model=list[IncidentDetailResponse])
async def list_incidents_endpoint():
    return await list_incidents()
