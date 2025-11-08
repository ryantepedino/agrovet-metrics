from sqlalchemy import Column, Integer, Date, ForeignKey
from app.models.base import Base

class Ciclo(Base):
    __tablename__ = "ciclos"
    id = Column(Integer, primary_key=True, index=True)
    fazenda_id = Column(Integer, ForeignKey("fazendas.id"), nullable=False, index=True)
    inicio = Column(Date, nullable=False)
    fim = Column(Date, nullable=False)
