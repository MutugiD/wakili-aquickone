from typing import List, Optional
from backend.api.models.research import ResearchQueryRequest, ResearchResponse

class ResearchService:
    _history: List[ResearchResponse] = []

    @classmethod
    def query(cls, request: ResearchQueryRequest) -> ResearchResponse:
        # TODO: Connect to research agent
        answer = f"[Stub] Research answer for: {request.question}"
        response = ResearchResponse(answer=answer, sources=["[Stub source]"])
        cls._history.append(response)
        return response

    @classmethod
    def history(cls) -> List[ResearchResponse]:
        return cls._history