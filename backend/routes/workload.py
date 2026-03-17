from fastapi import APIRouter

from analytics.data_loader import load_issues
from analytics.workload import workload_distribution
from models.response import make_response

router = APIRouter(prefix="/api/v1", tags=["workload"])


@router.get("/workload")
def get_workload() -> dict:
    issues = load_issues()
    distribution = workload_distribution(issues)
    return make_response(distribution)
