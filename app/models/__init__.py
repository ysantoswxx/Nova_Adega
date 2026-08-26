from app.models import categoria
from app.models import produto
from app.models import usuarios
from app.models import movimentacao
from app.models import cliente
from app.models import vendas

#Gerar a migration

#python -m alembic revision --autogenerate -m "Criar tabela categorias e produtos."

# aplicar a migration a
# python -m alembic upgrade head