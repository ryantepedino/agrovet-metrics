from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.services.kpi import compute_kpis_for_farm, benchmark_metric
from app.schemas.kpi import KPIResponse, BenchmarkResponse

router = APIRouter()

@router.get("/{fazenda_id}", response_model=KPIResponse)
def get_kpis(
    fazenda_id: int,
    inicio: date,
    fim: date,
    db: Session = Depends(get_db)
):
    try:
        return compute_kpis_for_farm(db, fazenda_id, inicio, fim)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/benchmark/{metric}", response_model=BenchmarkResponse)
def get_benchmark(
    metric: str,
    inicio: date,
    fim: date,
    db: Session = Depends(get_db)
):
    try:
        return benchmark_metric(db, metric, inicio, fim)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
