# app/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.models.base import Base, engine

# Importações das rotas
from app.api.routes_ingest import router as ingest_router
from app.api.routes_kpi import router as kpi_router
from app.api.routes_reports import router as reports_router
from app.api.routes_fazendas import router as fazendas_router  # ✅ NOVO

# Cria as tabelas no banco (se ainda não existirem)
Base.metadata.create_all(bind=engine)

# Instância principal do FastAPI
app = FastAPI(
    title="AgroVet Metrics API",
    version="1.0.0",
    description=(
        "MVP para manejo reprodutivo bovino: ingestão de dados, cálculo de KPIs, "
        "comparativos e relatórios PDF/XLSX."
    ),
)

# Configuração de CORS (libera acesso do Streamlit e outros frontends)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas principais
app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
app.include_router(kpi_router, prefix="/kpi", tags=["kpi"])
app.include_router(reports_router, prefix="/relatorio", tags=["relatorios"])
app.include_router(fazendas_router, prefix="/fazendas", tags=["fazendas"])  # ✅ Correção segura

# Endpoint simples de verificação (healthcheck)
@app.get("/", tags=["health"])
def healthcheck():
    return {"status": "ok", "service": "AgroVet Metrics API"}
