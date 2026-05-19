from fastapi import APIRouter

from api.schemas.requests import AnalyzeRequest
from api.schemas.responses import RepositoryAnalysisResponse
from engine.analyzer import analyze_github_repo
from fastapi import HTTPException
router = APIRouter()


@router.post("/analyze", response_model=RepositoryAnalysisResponse)

def analyze(request: AnalyzeRequest):

    try:
        repo_url = request.repo_url

        result = analyze_github_repo(repo_url)

        # Transform the result to match the response schema
        transformed_response = {
            "repo_url": result.get("repo_url"),
            "summary": {
                "total_files_scanned": result.get("total_files_scanned", 0),
                "total_files_analyzed": result.get("total_files_analyzed", 0),
                "average_complexity": 0.0  # Calculate if needed
            },
            "files": result.get("results", [])
        }
        
        return transformed_response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )