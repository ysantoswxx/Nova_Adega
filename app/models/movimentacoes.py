from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


class TipoMovimentacao(str, enum.Enum):
    entrada = "entrada"
    saida = "saida"


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    tipo = Column(Enum(TipoMovimentacao), nullable=False)
    quantidade = Column(Integer, nullable=False, default=0)
    preco_unitario = Column(Float, nullable=False, default=0.0)
    valor_total = Column(Float, nullable=False, default=0.0)
    observacao = Column(String(255), nullable=True)
    criado_em = Column(DateTime, default=datetime.now)

    # Chave estrangeira para produto
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    produto = relationship("Produto", backref="movimentacoes")

    # Chave estrangeira para usuário
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    usuario = relationship("Usuario", backref="movimentacoes")
