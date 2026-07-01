from cognee import cognee
from fastapi import HTTPException
from app.schemas.incident import Incident


def incident_to_memory(incident: Incident) -> str:
    memory = f"""
Title: {incident.title}
Service: {incident.service}
Environment: {incident.environment}
Severity: {incident.severity.value}
Symptoms: {incident.symptoms}
""".strip()

    if incident.root_cause:
        memory += f"\nRoot Cause: {incident.root_cause}"

    if incident.fix_applied:
        memory += f"\nFix Applied: {incident.fix_applied}"

    return memory


async def remember_incident(incident: Incident) -> None:
    memory_text = incident_to_memory(incident)
    try:
        await cognee.remember(memory_text)
        return True
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store incident in memory: {str(e)}",
        )
