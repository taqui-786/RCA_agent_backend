from datetime import datetime, timezone
import cognee
from app.action.generate_rca import generate_rca
from app.action.recall_similar_incidents import recall_similar_incidents
from app.action.remember_incident import remember_incident
from app.schemas.incident import (
    Incident,
    IncidentCreate,
    IncidentDetailResponse,
    IncidentResolveRequest,
    RecalledFromItem,
)
from cognee.modules.engine.operations.setup import setup

_store: list[dict] = []
_counter = 0


def _score_recalled(text: str, service: str, environment: str) -> int:
    score = 0
    for line in text.split("\n"):
        if line.startswith("Service:") and service in line:
            score += 2
        elif line.startswith("Environment:") and environment in line:
            score += 1
    return score


def _parse_recalled(text: str) -> RecalledFromItem:
    title = symptom = service = fix = ""
    for line in text.split("\n"):
        if line.startswith("Title:"):
            title = line.split(":", 1)[1].strip()
        elif line.startswith("Symptoms:"):
            symptom = line.split(":", 1)[1].strip()
        elif line.startswith("Service:"):
            service = line.split(":", 1)[1].strip()
        elif line.startswith("Fix Applied:"):
            fix = line.split(":", 1)[1].strip()
    return RecalledFromItem(
        incident_title=title,
        symptom=symptom,
        service=service,
        fix=fix or "Not resolved yet",
    )


async def create_incident(data: IncidentCreate) -> IncidentDetailResponse:
    global _counter

    _counter += 1

    incident = Incident(
        id=_counter,
        title=data.title,
        severity=data.severity,
        service=data.service,
        environment=data.environment,
        symptoms=data.symptoms,
        status="open",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    await setup()

    similar_incidents = await recall_similar_incidents(incident)
    similar_incidents.sort(
        key=lambda t: _score_recalled(t, incident.service, incident.environment),
        reverse=True,
    )
    rca = await generate_rca(incident, similar_incidents)

    incident.root_cause = rca.root_cause

    record = {
        **incident.model_dump(),
        "confidence": rca.confidence,
        "recommended_fix": rca.recommended_fix,
        "first_action": rca.first_action,
        "recalled_from": [_parse_recalled(s) for s in similar_incidents],
    }

    _store.append(record)

    await remember_incident(incident)

    return IncidentDetailResponse(**record)


async def resolve_incident(
    incident_id: int, data: IncidentResolveRequest
) -> IncidentDetailResponse | None:
    for record in _store:
        if record["id"] != incident_id:
            continue

        record["status"] = "resolved"
        record["root_cause"] = data.confirmed_root_cause
        record["fix_applied"] = data.fix_applied
        record["updated_at"] = datetime.now(timezone.utc)

        incident = Incident(**record)
        await remember_incident(incident)
        await cognee.improve()

        return IncidentDetailResponse(**record)

    return None


def get_incident(incident_id: int) -> IncidentDetailResponse | None:
    for record in _store:
        if record["id"] == incident_id:
            return IncidentDetailResponse(**record)
    return None


def list_incidents() -> list[IncidentDetailResponse]:
    return [IncidentDetailResponse(**r) for r in _store]
