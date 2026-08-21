from app.models.produto import Produto
from app.models.categoria import Categoria
from app.models.movimentacao import Movimentacao
from app.models.usuarios import Usuario
from app.models.cliente import Cliente

#Gerar a migration

#python -m alembic revision --autogenerate -m "Criar tabela categorias e produtos."

# aplicar a migration a