from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.fazenda import Fazenda
from app.models.evento import EventoRepro
from app.schemas.ingest import MobileInput
from app.core.logging import logger

GESTATION_DAYS = 283

def _get_or_create_farm(db: Session, nome: str, produtor=None, municipio=None, estado=None) -> Fazenda:
    farm = db.execute(select(Fazenda).where(Fazenda.nome == nome)).scalar_one_or_none()
    if farm:
        return farm
    farm = Fazenda(nome=nome, produtor=produtor, municipio=municipio, estado=estado)
    db.add(farm)
    db.commit()
    db.refresh(farm)
    logger.info(f"Criada fazenda: {nome}")
    return farm

def insert_mobile_input(db: Session, payload: MobileInput):
    farm = _get_or_create_farm(db, payload.fazenda, payload.produtor, payload.municipio, payload.estado)

    # Regras de coerência
    if payload.inseminadas > payload.aptas:
        raise ValueError("inseminadas não pode ser maior que aptas")
    if payload.gestantes > payload.inseminadas:
        raise ValueError("gestantes não pode ser maior que inseminadas")

    # Inserir eventos (uma linha por tipo)
    for tipo, valor in [
        ("aptas", payload.aptas),
        ("inseminadas", payload.inseminadas),
        ("gestantes", payload.gestantes),
        ("partos", payload.partos or 0),
    ]:
        evt = EventoRepro(fazenda_id=farm.id, data=payload.data, tipo=tipo, valor=int(valor))
        db.add(evt)

    db.commit()
    logger.info(f"Nova medição inserida para {farm.nome} em {payload.data}")
    return type("InsertResult", (), {"fazenda_id": farm.id, "data": payload.data})

def _sum_by_type(db: Session, fazenda_id: int, tipo: str, inicio: date, fim: date) -> int:
    stmt = select(func.coalesce(func.sum(EventoRepro.valor), 0)).where(
        EventoRepro.fazenda_id == fazenda_id,
        EventoRepro.tipo == tipo,
        EventoRepro.data >= inicio,
        EventoRepro.data <= fim,
    )
    return int(db.execute(stmt).scalar() or 0)

def _expected_births(db: Session, fazenda_id: int, inicio: date, fim: date) -> int:
    # Partos previstos = gestantes cujo parto estimado (data + 283) cai no período
    from sqlalchemy import and_
    stmt = select(func.sum(EventoRepro.valor)).where(
        and_(
            EventoRepro.fazenda_id == fazenda_id,
            EventoRepro.tipo == "gestantes",
            EventoRepro.data + timedelta(days=GESTATION_DAYS) >= inicio,
            EventoRepro.data + timedelta(days=GESTATION_DAYS) <= fim,
        )
    )
    return int(db.execute(stmt).scalar() or 0)

def compute_kpis_for_farm(db: Session, fazenda_id: int, inicio: date, fim: date):
    farm = db.get(Fazenda, fazenda_id)
    if not farm:
        raise ValueError("Fazenda não encontrada")

    aptas = _sum_by_type(db, fazenda_id, "aptas", inicio, fim)
    inseminadas = _sum_by_type(db, fazenda_id, "inseminadas", inicio, fim)
    gestantes = _sum_by_type(db, fazenda_id, "gestantes", inicio, fim)
    partos_real = _sum_by_type(db, fazenda_id, "partos", inicio, fim)
    partos_prev = _expected_births(db, fazenda_id, inicio, fim)

    def pct(n, d):
        if d <= 0:
            return 0.0
        return round(100.0 * n / d, 2)

    TS = pct(inseminadas, aptas)
    TC = pct(gestantes, inseminadas)
    TP = round((TS / 100.0) * (TC / 100.0) * 100.0, 2)

    return {
        "fazenda_id": farm.id,
        "fazenda_nome": farm.nome,
        "periodo": {"inicio": str(inicio), "fim": str(fim)},
        "totais": {
            "aptas": aptas,
            "inseminadas": inseminadas,
            "gestantes": gestantes,
            "partos_realizados": partos_real,  # ADICIONADO
            "partos_previstos": partos_prev,
        },
        "kpis": {"TS": TS, "TC": TC, "TP": TP, "partos_previstos": partos_prev},
    }

def benchmark_metric(db: Session, metric: str, inicio: date, fim: date):
    farms = db.query(Fazenda).all()
    ranking = []
    for f in farms:
        k = compute_kpis_for_farm(db, f.id, inicio, fim)
        ranking.append({
            "fazenda_id": f.id,
            "fazenda_nome": f.nome,
            "valor": k["kpis"][metric],
        })
    ranking.sort(key=lambda x: x["valor"], reverse=True)
    return {"metric": metric, "inicio": inicio, "fim": fim, "ranking": ranking}
