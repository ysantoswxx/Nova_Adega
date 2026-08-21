from .categoria import Categoria
from .produto import Produto
from .usuarios import Usuario
from .movimentacoes import Movimentacao
from .cliente import Cliente


#Gerar a migration

#python -m alembic revision --autogenerate -m "Criar tabela categorias e produtos."

# aplicar a migration a