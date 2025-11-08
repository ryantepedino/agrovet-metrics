from pydantic import BaseModel
from datetime import date

class KPIs(BaseModel):
    TS: float
    TC: float
    TP: float
    partos_previstos: int

class KPIResponse(BaseModel):
    fazenda_id: int
    fazenda_nome: str
    periodo: dict
    totais: dict
    kpis: KPIs

class BenchmarkItem(BaseModel):
    fazenda_id: int
    fazenda_nome: str
    valor: float

class BenchmarkResponse(BaseModel):
    metric: str
    inicio: date
    fim: date
    ranking: list[BenchmarkItem]
