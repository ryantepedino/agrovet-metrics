from datetime import date
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.services.reports import build_pdf_report, build_xlsx_export

router = APIRouter()

@router.get("/fazenda/{fazenda_id}.pdf")
def get_pdf_report(
    fazenda_id: int,
    inicio: date,
    fim: date,
    db: Session = Depends(get_db)
):
    try:
        path = build_pdf_report(db, fazenda_id, inicio, fim)
        with open(path, "rb") as f:
            pdf_bytes = f.read()
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="Relatorio_Fazenda_{fazenda_id}.pdf"'
            },
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/fazenda/{fazenda_id}.xlsx")
def get_xlsx_export(
    fazenda_id: int,
    inicio: date,
    fim: date,
    db: Session = Depends(get_db)
):
    try:
        path = build_xlsx_export(db, fazenda_id, inicio, fim)
        with open(path, "rb") as f:
            xlsx_bytes = f.read()
        return Response(
            content=xlsx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="Export_Fazenda_{fazenda_id}.xlsx"'
            },
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
