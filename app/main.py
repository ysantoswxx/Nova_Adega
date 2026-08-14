# Ponte de entrada do meu sistema
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import get_usuario_opcional
from app.database import get_db
from app.models.categoria import Categoria
from app.models.produto import Produto

from app.controllers import auth_controller
from app.controllers import usuario_controller
from app.controllers import categoria_controller
from app.controllers import produto_controller
from app.controllers import movimentacao_controller


app = FastAPI(title="Sistema de Ponto de venda")


# Configurar a pasta para servir os arquivos estáticos
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)


# Configurar o Jinja2
templates = Jinja2Templates(directory="app/templates")


# Inclui os routers dos controladores
app.include_router(auth_controller.router)
app.include_router(usuario_controller.router)
app.include_router(categoria_controller.router)
app.include_router(produto_controller.router)
app.include_router(movimentacao_controller.router)


@app.get("/")
def tela_inicial(
    request: Request,
    usuario=Depends(get_usuario_opcional),
    db=Depends(get_db)
):

    # Tela não logado
    if usuario is None:
        return templates.TemplateResponse(
            request,
            "index.html",
            {"request": request}
        )

    # Buscar categorias ativas
    categorias = db.query(Categoria).filter(
        Categoria.ativo == True
    ).order_by(
        Categoria.nome
    ).all()

    # Buscar produtos ativos
    produtos = db.query(Produto).filter(
        Produto.ativo == True
    ).order_by(
        Produto.nome
    ).all()

    # Tela do funcionário
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "request": request,
            "usuario": usuario,
            "categorias": categorias,
            "produtos": produtos
        }
    )