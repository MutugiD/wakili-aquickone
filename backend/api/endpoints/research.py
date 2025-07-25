from fastapi import APIRouter
from backend.api.models.research import ResearchQueryRequest, ResearchResponse
from backend.api.services.research_service import ResearchService
from typing import List

router = APIRouter(prefix="/research", tags=["research"])

@router.post("/query", response_model=ResearchResponse)
def research_query(request: ResearchQueryRequest):
    return ResearchService.query(request)

@router.get("/history", response_model=List[ResearchResponse])
def research_history():
    return ResearchService.history()