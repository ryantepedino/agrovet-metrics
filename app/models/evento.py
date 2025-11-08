from sqlalchemy import Column, Integer, Date, String, ForeignKey, CheckConstraint, Index
from app.models.base import Base

class EventoRepro(Base):
    __tablename__ = "eventos_repro"
    id = Column(Integer, primary_key=True, index=True)
    fazenda_id = Column(Integer, ForeignKey("fazendas.id"), nullable=False, index=True)
    data = Column(Date, index=True, nullable=False)
    tipo = Column(String, nullable=False)  # aptas|inseminadas|gestantes|partos
    valor = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("valor >= 0", name="ck_valor_nao_negativo"),
        Index("ix_evento_fazenda_data", "fazenda_id", "data"),
    )
