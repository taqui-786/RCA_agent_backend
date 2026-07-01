from cognee import cognee, SearchType
from cognee.modules.retrieval.exceptions.exceptions import NoDataError
from fastapi import HTTPException

from app.schemas.incident import Incident

async def recall_similar_incidents(incident: Incident) -> list[str]:
    query = f"cloud incident on service {incident.service} in {incident.environment}. symptoms: {incident.symptoms}"
    try:
        results = await cognee.recall(
            query_text=query,
            query_type=SearchType.CHUNKS,
            only_context=True,
            top_k=5,
        )
        return [item.text for item in results]
    except NoDataError:
        return []
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to recall similar incidents: {str(e)}",
        )