from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    # ← ADICIONE ESTA LINHA
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    ativa = Column(Boolean, default=True)

    produtos = relationship("Produto", back_populates="categoria")
