from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)

    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    tipo = Column(String(20), nullable=False)   # Entrada ou Saída

    quantidade = Column(Integer, nullable=False)

    data_hora = Column(DateTime, default=datetime.now)

    observacao = Column(String(255), nullable=True)

    # Relacionamentos
    produto = relationship("Produto", back_populates="movimentacoes")

    usuario = relationship("Usuario", back_populates="movimentacoes")