# app/api/routes_fazendas.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.models.fazenda import Fazenda

router = APIRouter(tags=["Fazendas"])


@router.get("/", summary="Lista todas as fazendas")
def listar_fazendas(db: Session = Depends(get_db)):
    """
    Retorna a lista de fazendas cadastradas no banco (id + nome)
    """
    fazendas = db.query(Fazenda).all()
    return [{"id": f.id, "nome": f.nome} for f in fazendas]
