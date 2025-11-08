from pydantic import BaseModel, field_validator
from datetime import date

class MobileInput(BaseModel):
    fazenda: str
    data: date
    aptas: int
    inseminadas: int
    gestantes: int
    partos: int | None = 0
    produtor: str | None = None
    municipio: str | None = None
    estado: str | None = None

    @field_validator("aptas", "inseminadas", "gestantes", "partos")
    @classmethod
    def non_negative(cls, v):
        if v is None:
            return 0
        if v < 0:
            raise ValueError("valores não podem ser negativos")
        return v

class IngestReport(BaseModel):
    rows: int
    warnings: list[str]
