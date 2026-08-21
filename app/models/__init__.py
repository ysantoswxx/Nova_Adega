<<<<<<< HEAD
from app.models.produto import Produto
from app.models.categoria import Categoria
from app.models.movimentacao import Movimentacao
from app.models.usuarios import Usuario
from app.models.cliente import Cliente

=======
from app.models import categoria
from app.models import produto
from app.models import usuarios
from app.models import movimentacao
from app.models import cliente
from app.models import vendas
>>>>>>> eb176609d8e0da19e42a7689fecc32d6d64b4971
#Gerar a migration

#python -m alembic revision --autogenerate -m "Criar tabela categorias e produtos."

# aplicar a migration a