from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(200), nullable=False)
    telefone = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)
    cpf = Column(String(14), nullable=True)
    ativo = Column(Boolean, default=True)
