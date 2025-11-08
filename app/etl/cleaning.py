import pandas as pd
from datetime import datetime
from app.schemas.ingest import MobileInput

EXPECTED_COLS = ["fazenda", "data", "aptas", "inseminadas", "gestantes", "partos"]

def normalize_excel(file_path: str):
    """
    Lê um arquivo Excel/CSV e converte em MobileInput.
    Corrige nomes de colunas e valida conteúdo.
    """
    ext = file_path.split(".")[-1].lower()
    if ext == "csv":
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    df.columns = [c.strip().lower() for c in df.columns]

    # Tenta mapear colunas equivalentes
    col_map = {}
    for c in df.columns:
        if "faz" in c:
            col_map[c] = "fazenda"
        elif "data" in c:
            col_map[c] = "data"
        elif "apta" in c:
            col_map[c] = "aptas"
        elif "inse" in c:
            col_map[c] = "inseminadas"
        elif "ges" in c:
            col_map[c] = "gestantes"
        elif "part" in c:
            col_map[c] = "partos"

    df = df.rename(columns=col_map)

    warnings = []
    missing = [c for c in EXPECTED_COLS if c not in df.columns]
    if missing:
        warnings.append(f"Colunas ausentes: {', '.join(missing)}")

    clean_rows = []
    for _, row in df.iterrows():
        try:
            item = MobileInput(
                fazenda=str(row.get("fazenda", "")).strip(),
                data=pd.to_datetime(row.get("data")).date() if not pd.isna(row.get("data")) else datetime.today().date(),
                aptas=int(row.get("aptas", 0)),
                inseminadas=int(row.get("inseminadas", 0)),
                gestantes=int(row.get("gestantes", 0)),
                partos=int(row.get("partos", 0)),
            )
            clean_rows.append(item)
        except Exception as e:
            warnings.append(f"Linha ignorada: {e}")

    return clean_rows, warnings
