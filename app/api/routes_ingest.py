from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.services.kpi import insert_mobile_input
from app.etl.cleaning import normalize_excel
from app.schemas.ingest import MobileInput, IngestReport

router = APIRouter()

@router.post("/mobile", response_model=IngestReport)
def ingest_mobile(payloads: list[MobileInput], db: Session = Depends(get_db)):
    warnings = []
    for p in payloads:
        try:
            insert_mobile_input(db, p)
        except Exception as e:
            warnings.append(str(e))
    return {"rows": len(payloads), "warnings": warnings}

@router.post("/upload", response_model=IngestReport)
def ingest_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(file.file.read())
        rows, warnings = normalize_excel(temp_path)
        for r in rows:
            insert_mobile_input(db, r)
        return {"rows": len(rows), "warnings": warnings}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
