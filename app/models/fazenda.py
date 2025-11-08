from sqlalchemy import Column, Integer, String
from app.models.base import Base

class Fazenda(Base):
    __tablename__ = "fazendas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, nullable=False, index=True)
    produtor = Column(String, nullable=True)
    municipio = Column(String, nullable=True)
    estado = Column(String, nullable=True)
